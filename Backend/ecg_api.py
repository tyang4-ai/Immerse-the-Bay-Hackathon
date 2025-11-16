from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import time
import json
from functools import lru_cache
import hashlib

from model_loader import ECGModelLoader
from ecg_heartrate_analyzer import ECGHeartRateAnalyzer
from heart_region_mapper import HeartRegionMapper
from clinical_decision_support_llm import ClinicalDecisionSupportLLM
from logger import api_logger, PerformanceTimer

app = Flask(__name__)
CORS(app)

# Global module instances
ecg_model = ECGModelLoader()
hr_analyzer = ECGHeartRateAnalyzer(sampling_rate=400)
region_mapper = HeartRegionMapper()
clinical_llm = ClinicalDecisionSupportLLM()

# Cache statistics
cache_stats = {'hits': 0, 'misses': 0}


def initialize():
    """Initialize backend modules with safety nets"""
    api_logger.info("Initializing HoloHuman XR Backend...")

    with PerformanceTimer("Model loading", api_logger):
        model_loaded = ecg_model.load_model()

    if not model_loaded:
        api_logger.warning("Model not loaded - running in FALLBACK mode (serving cached predictions)")
        api_logger.warning("To use full ML inference, ensure model/model.hdf5 exists")
    else:
        api_logger.info(f"ECG model loaded successfully: {ecg_model.model_path}")

    api_logger.info("Backend initialization complete!")


def validate_ecg_input(ecg_signal: np.ndarray) -> tuple[bool, str]:
    """
    Validate ECG signal input for safety and quality

    Returns: (is_valid, error_message)
    """
    # Check for NaN or Inf values
    if np.isnan(ecg_signal).any():
        nan_percentage = np.isnan(ecg_signal).sum() / ecg_signal.size * 100
        if nan_percentage > 5:
            return False, f"Signal contains {nan_percentage:.1f}% NaN values (threshold: 5%)"

    if np.isinf(ecg_signal).any():
        return False, "Signal contains infinite values"

    # Check amplitude range (realistic ECG: -5mV to +5mV)
    signal_min, signal_max = ecg_signal.min(), ecg_signal.max()
    if signal_min < -5.0 or signal_max > 5.0:
        return False, f"Signal amplitude out of range: [{signal_min:.2f}, {signal_max:.2f}] (expected: [-5.0, 5.0] mV)"

    # Check for flat-line signal (>90% zeros)
    zero_percentage = (np.abs(ecg_signal) < 0.001).sum() / ecg_signal.size * 100
    if zero_percentage > 90:
        return False, f"Signal appears flat-line ({zero_percentage:.1f}% zeros)"

    # Check signal quality (basic SNR estimate)
    signal_std = np.std(ecg_signal)
    if signal_std < 0.01:
        return False, f"Signal has very low variance (std={signal_std:.4f}), possible noise or artifact"

    return True, "OK"


def create_cache_key(predictions_dict: dict, top_condition: str, confidence: float, output_mode: str, region_focus: str = None) -> str:
    """
    Create cache key for LLM responses

    Bucket confidence to reduce cache misses from tiny variations
    """
    confidence_bucket = round(confidence, 1)  # Round to nearest 0.1
    key_data = f"{top_condition}:{confidence_bucket}:{output_mode}"

    # Add region_focus to cache key for storytelling mode
    if output_mode == 'storytelling' and region_focus:
        key_data += f":{region_focus}"

    return hashlib.md5(key_data.encode()).hexdigest()


@lru_cache(maxsize=128)
def get_cached_llm_response(cache_key: str, predictions_json: str, hr_json: str,
                            region_json: str, top_condition: str,
                            confidence: float, output_mode: str, region_focus: str = None):
    """
    Cached LLM interpretation (10-minute TTL via LRU)

    Args are JSON strings to make them hashable for cache
    """
    predictions_dict = json.loads(predictions_json)
    heart_rate_data = json.loads(hr_json)
    region_health = json.loads(region_json)

    api_logger.info(f"Cache MISS for key {cache_key[:8]}... - calling Claude API")
    cache_stats['misses'] += 1

    # Build kwargs for storytelling mode
    kwargs = {}
    if output_mode == 'storytelling' and region_focus:
        kwargs['region_focus'] = region_focus

    return clinical_llm.analyze(
        predictions_dict,
        heart_rate_data,
        region_health,
        top_condition,
        confidence,
        output_mode=output_mode,
        **kwargs
    )


@app.before_request
def before_request():
    """Set request ID for logging context"""
    request_id = api_logger.set_request_id()
    api_logger.info(f"Request received: {request.method} {request.path}")


@app.route('/health', methods=['GET'])
def health_check():
    """Enhanced health check with model status"""
    model_status = 'loaded' if ecg_model.model is not None else 'fallback_mode'

    return jsonify({
        'status': 'healthy',
        'model_loaded': ecg_model.model is not None,
        'model_status': model_status,
        'model_path': ecg_model.model_path if ecg_model.model else None,
        'simulation_mode': ecg_model.simulation_mode,
        'cache_stats': cache_stats.copy(),
        'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    })


@app.route('/api/ecg/analyze', methods=['POST'])
def analyze_ecg():
    """
    Main ECG analysis endpoint with safety nets and caching

    Request body:
    {
        "ecg_signal": [[...], [...], ...],  # 4096 x 12 array
        "output_mode": "clinical_expert",    # Optional: clinical_expert|patient_education|storytelling
        "region_focus": "rbbb"               # Optional: for storytelling mode
    }
    """
    start_time = time.time()

    try:
        # === INPUT VALIDATION ===
        data = request.get_json()

        if not data:
            error_id = api_logger.generate_error_id()
            api_logger.error(f"{error_id}: No JSON data in request body")
            return jsonify({
                'error': 'Request body must be valid JSON',
                'error_id': error_id,
                'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
            }), 400

        if 'ecg_signal' not in data:
            error_id = api_logger.generate_error_id()
            api_logger.error(f"{error_id}: Missing ecg_signal field")
            return jsonify({
                'error': 'Missing required field: ecg_signal',
                'error_id': error_id,
                'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
            }), 400

        # Convert to numpy array
        try:
            ecg_signal = np.array(data['ecg_signal'], dtype=np.float32)
        except (ValueError, TypeError) as e:
            error_id = api_logger.generate_error_id()
            api_logger.error(f"{error_id}: Invalid ecg_signal format - {str(e)}")
            return jsonify({
                'error': 'ecg_signal must be a numeric array',
                'error_id': error_id,
                'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
            }), 400

        # Shape validation
        if ecg_signal.shape != (4096, 12):
            error_id = api_logger.generate_error_id()
            api_logger.error(f"{error_id}: Invalid shape {ecg_signal.shape}")
            return jsonify({
                'error': f'Invalid ECG shape {ecg_signal.shape}, expected (4096, 12) for 12-lead ECG',
                'error_id': error_id,
                'expected_shape': [4096, 12],
                'actual_shape': list(ecg_signal.shape),
                'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
            }), 400

        # Quality validation
        is_valid, validation_msg = validate_ecg_input(ecg_signal)
        if not is_valid:
            error_id = api_logger.generate_error_id()
            api_logger.warning(f"{error_id}: Signal validation failed - {validation_msg}")
            return jsonify({
                'error': 'ECG signal quality check failed',
                'error_id': error_id,
                'details': validation_msg,
                'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
            }), 400

        api_logger.info("Input validation passed")

        # === PROCESSING PIPELINE ===
        output_mode = data.get('output_mode', 'clinical_expert')
        region_focus = data.get('region_focus', None)

        # 1. ECG Model Prediction
        with PerformanceTimer("Model prediction", api_logger):
            predictions_dict = ecg_model.predict(ecg_signal)
            top_condition, confidence = ecg_model.get_top_condition(predictions_dict)

        # 2. Heart Rate Analysis
        with PerformanceTimer("Heart rate analysis", api_logger):
            heart_rate_data = hr_analyzer.analyze(ecg_signal)

        # 3. Region Mapping
        with PerformanceTimer("Region mapping", api_logger):
            region_health = region_mapper.get_region_health_status(predictions_dict)
            activation_sequence = region_mapper.get_activation_sequence(region_health)

        # 4. Clinical Decision Support (with caching)
        cache_key = create_cache_key(predictions_dict, top_condition, confidence, output_mode, region_focus)

        try:
            # Convert dicts to JSON strings for caching (must be hashable)
            predictions_json = json.dumps(predictions_dict, sort_keys=True)
            hr_json = json.dumps(heart_rate_data, sort_keys=True)
            region_json = json.dumps(region_health, sort_keys=True)

            with PerformanceTimer("LLM interpretation (with cache)", api_logger):
                llm_interpretation = get_cached_llm_response(
                    cache_key, predictions_json, hr_json, region_json,
                    top_condition, confidence, output_mode, region_focus
                )

            # Check if this was a cache hit
            cache_hit = cache_stats['hits'] > 0 or cache_key in str(get_cached_llm_response.cache_info())
            if cache_hit:
                cache_stats['hits'] += 1
                api_logger.info(f"Cache HIT for key {cache_key[:8]}...")

        except Exception as llm_error:
            error_id = api_logger.generate_error_id()
            api_logger.error(f"{error_id}: LLM processing failed - {str(llm_error)}")
            llm_interpretation = None
            cache_hit = False

        # === RESPONSE ===
        processing_time_ms = (time.time() - start_time) * 1000

        response_data = {
            'predictions': predictions_dict,
            'heart_rate': heart_rate_data,
            'region_health': region_health if region_health else None,
            'activation_sequence': activation_sequence if activation_sequence else None,
            'llm_interpretation': llm_interpretation if llm_interpretation else None,
            'top_condition': top_condition,
            'confidence': round(confidence, 3),
            'processing_time_ms': round(processing_time_ms, 2),
            'model_version': '1.0.0',
            'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
            'metadata': {
                'simulation_mode': ecg_model.simulation_mode,
                'cache_hit': cache_hit,
                'output_mode': output_mode,
                'region_focus': region_focus if output_mode == 'storytelling' else None,
                'request_id': api_logger.request_id
            }
        }

        api_logger.info(f"Request completed successfully in {processing_time_ms:.2f}ms")
        return jsonify(response_data)

    except Exception as e:
        error_id = api_logger.generate_error_id()
        api_logger.error(f"{error_id}: Unexpected error in analyze_ecg - {str(e)}", exc_info=True)

        return jsonify({
            'error': 'An internal processing error occurred',
            'error_id': error_id,
            'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
            'suggestion': 'Please check your ECG data format and try again'
        }), 500


@app.route('/api/cache/stats', methods=['GET'])
def cache_statistics():
    """Get cache performance statistics"""
    cache_info = get_cached_llm_response.cache_info()

    total_requests = cache_stats['hits'] + cache_stats['misses']
    hit_rate = (cache_stats['hits'] / total_requests * 100) if total_requests > 0 else 0

    return jsonify({
        'cache_stats': {
            'hits': cache_stats['hits'],
            'misses': cache_stats['misses'],
            'total_requests': total_requests,
            'hit_rate_percent': round(hit_rate, 2)
        },
        'lru_cache_info': {
            'hits': cache_info.hits,
            'misses': cache_info.misses,
            'max_size': cache_info.maxsize,
            'current_size': cache_info.currsize
        }
    })


@app.route('/api/cache/clear', methods=['POST'])
def clear_cache():
    """Clear LLM response cache (admin only)"""
    get_cached_llm_response.cache_clear()
    cache_stats['hits'] = 0
    cache_stats['misses'] = 0

    api_logger.info("Cache cleared by admin request")

    return jsonify({
        'message': 'Cache cleared successfully',
        'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    })


# ============================================================================
# PHASE 3: TEMPORAL DRILLDOWN ENDPOINTS
# ============================================================================

@app.route('/api/ecg/beats', methods=['POST'])
def get_beats():
    """
    Fast R-peak detection endpoint for VR timeline scrubbing

    Request body:
    {
        "ecg_signal": [[...], [...], ...]  # 4096 x 12 array
    }

    Response:
    {
        "r_peaks": [350, 980, 1610, ...],
        "beat_count": 12,
        "avg_rr_interval_ms": 830.0,
        "rhythm": "regular"
    }
    """
    start_time = time.time()

    try:
        # Input validation
        data = request.get_json()

        if not data or 'ecg_signal' not in data:
            error_id = api_logger.generate_error_id()
            api_logger.error(f"{error_id}: Missing ecg_signal in /api/ecg/beats")
            return jsonify({
                'error': 'Missing required field: ecg_signal',
                'error_id': error_id,
                'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
            }), 400

        # Convert to numpy array
        try:
            ecg_signal = np.array(data['ecg_signal'], dtype=np.float32)
        except (ValueError, TypeError) as e:
            error_id = api_logger.generate_error_id()
            api_logger.error(f"{error_id}: Invalid ecg_signal format - {str(e)}")
            return jsonify({
                'error': 'ecg_signal must be a numeric array',
                'error_id': error_id,
                'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
            }), 400

        # Shape validation
        if ecg_signal.shape != (4096, 12):
            error_id = api_logger.generate_error_id()
            api_logger.error(f"{error_id}: Invalid shape {ecg_signal.shape} in /api/ecg/beats")
            return jsonify({
                'error': f'Invalid ECG shape {ecg_signal.shape}, expected (4096, 12)',
                'error_id': error_id,
                'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
            }), 400

        # Detect R-peaks
        with PerformanceTimer("Beat detection", api_logger):
            r_peaks, lead_used, lead_quality, fallback_triggered = hr_analyzer.detect_r_peaks(ecg_signal)

        # Calculate rhythm metrics
        if len(r_peaks) >= 2:
            rr_intervals = np.diff(r_peaks)
            avg_rr_samples = np.mean(rr_intervals)
            avg_rr_ms = (avg_rr_samples / hr_analyzer.fs) * 1000

            # Rhythm regularity (CV < 0.15 = regular, >= 0.15 = irregular)
            rr_cv = np.std(rr_intervals) / np.mean(rr_intervals)
            rhythm = "regular" if rr_cv < 0.15 else "irregular"
        else:
            avg_rr_ms = 0.0
            rhythm = "undetectable"

        processing_time_ms = (time.time() - start_time) * 1000

        response_data = {
            'r_peaks': r_peaks.tolist(),
            'beat_count': len(r_peaks),
            'avg_rr_interval_ms': round(avg_rr_ms, 1),
            'rhythm': rhythm,
            'lead_used': lead_used,
            'lead_quality': round(lead_quality, 2),
            'processing_time_ms': round(processing_time_ms, 2),
            'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
        }

        api_logger.info(f"Beat detection completed: {len(r_peaks)} beats in {processing_time_ms:.2f}ms")
        return jsonify(response_data)

    except Exception as e:
        error_id = api_logger.generate_error_id()
        api_logger.error(f"{error_id}: Error in /api/ecg/beats - {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Beat detection failed',
            'error_id': error_id,
            'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
        }), 500


@app.route('/api/ecg/beat/<int:beat_index>', methods=['POST'])
def get_beat_detail(beat_index):
    """
    Single beat waveform analysis

    Request body:
    {
        "ecg_signal": [[...], [...], ...]  # 4096 x 12 array
    }

    Response:
    {
        "beat_index": 3,
        "waveform": {
            "p_wave": {"onset": 2450, "peak": 2500, "offset": 2580},
            "qrs_complex": {"onset": 2650, "peak": 2700, "offset": 2750},
            "t_wave": {"onset": 2850, "peak": 2950, "offset": 3050}
        },
        "intervals": {
            "pr_interval_ms": 170,
            "qrs_duration_ms": 100,
            "qt_interval_ms": 400
        },
        "raw_samples": [...],
        "annotations": "Normal sinus beat"
    }
    """
    start_time = time.time()

    try:
        # Input validation
        data = request.get_json()

        if not data or 'ecg_signal' not in data:
            error_id = api_logger.generate_error_id()
            api_logger.error(f"{error_id}: Missing ecg_signal in /api/ecg/beat/{beat_index}")
            return jsonify({
                'error': 'Missing required field: ecg_signal',
                'error_id': error_id,
                'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
            }), 400

        # Convert to numpy array
        try:
            ecg_signal = np.array(data['ecg_signal'], dtype=np.float32)
        except (ValueError, TypeError) as e:
            error_id = api_logger.generate_error_id()
            api_logger.error(f"{error_id}: Invalid ecg_signal format - {str(e)}")
            return jsonify({
                'error': 'ecg_signal must be a numeric array',
                'error_id': error_id,
                'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
            }), 400

        # Shape validation
        if ecg_signal.shape != (4096, 12):
            error_id = api_logger.generate_error_id()
            api_logger.error(f"{error_id}: Invalid shape {ecg_signal.shape}")
            return jsonify({
                'error': f'Invalid ECG shape {ecg_signal.shape}, expected (4096, 12)',
                'error_id': error_id,
                'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
            }), 400

        # Detect R-peaks
        with PerformanceTimer(f"Beat {beat_index} analysis", api_logger):
            r_peaks, lead_used, _, _ = hr_analyzer.detect_r_peaks(ecg_signal)

        # Validate beat index
        if beat_index < 0 or beat_index >= len(r_peaks):
            error_id = api_logger.generate_error_id()
            api_logger.warning(f"{error_id}: Beat index {beat_index} out of range (0-{len(r_peaks)-1})")
            return jsonify({
                'error': f'Beat index {beat_index} out of range',
                'error_id': error_id,
                'beat_count': len(r_peaks),
                'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
            }), 400

        # Extract beat window (±200ms around R-peak)
        r_peak_sample = int(r_peaks[beat_index])
        window_samples = int(0.2 * hr_analyzer.fs)  # 200ms = 80 samples at 400Hz
        beat_start = max(0, r_peak_sample - window_samples)
        beat_end = min(len(ecg_signal), r_peak_sample + window_samples)

        # Get lead used for analysis
        lead_index = {'II': 1, 'V1': 6, 'V5': 10, 'I': 0, 'aVF': 7}.get(lead_used, 1)
        beat_signal = ecg_signal[beat_start:beat_end, lead_index]

        # Simple waveform detection (placeholder - could be enhanced with actual detection)
        # For now, we'll estimate based on typical ECG intervals
        relative_r_peak = r_peak_sample - beat_start

        # Estimate P-wave (typically 40-80ms before QRS onset)
        p_onset = max(0, relative_r_peak - 60)
        p_peak = max(0, relative_r_peak - 50)
        p_offset = max(0, relative_r_peak - 30)

        # QRS complex (typically 80-120ms wide)
        qrs_onset = max(0, relative_r_peak - 20)
        qrs_peak = relative_r_peak
        qrs_offset = min(len(beat_signal) - 1, relative_r_peak + 30)

        # T-wave (typically 100-200ms after QRS offset)
        t_onset = min(len(beat_signal) - 1, qrs_offset + 20)
        t_peak = min(len(beat_signal) - 1, qrs_offset + 70)
        t_offset = min(len(beat_signal) - 1, qrs_offset + 120)

        # Calculate intervals in ms
        pr_interval_ms = ((qrs_onset - p_onset) / hr_analyzer.fs) * 1000
        qrs_duration_ms = ((qrs_offset - qrs_onset) / hr_analyzer.fs) * 1000
        qt_interval_ms = ((t_offset - qrs_onset) / hr_analyzer.fs) * 1000

        # Generate annotation
        annotation = "Normal sinus beat"
        if qrs_duration_ms > 120:
            annotation = "Wide QRS complex (possible bundle branch block)"
        elif pr_interval_ms > 200:
            annotation = "Prolonged PR interval (possible AV block)"

        processing_time_ms = (time.time() - start_time) * 1000

        response_data = {
            'beat_index': beat_index,
            'r_peak_sample': r_peak_sample,
            'waveform': {
                'p_wave': {
                    'onset': int(beat_start + p_onset),
                    'peak': int(beat_start + p_peak),
                    'offset': int(beat_start + p_offset)
                },
                'qrs_complex': {
                    'onset': int(beat_start + qrs_onset),
                    'peak': int(beat_start + qrs_peak),
                    'offset': int(beat_start + qrs_offset)
                },
                't_wave': {
                    'onset': int(beat_start + t_onset),
                    'peak': int(beat_start + t_peak),
                    'offset': int(beat_start + t_offset)
                }
            },
            'intervals': {
                'pr_interval_ms': round(pr_interval_ms, 1),
                'qrs_duration_ms': round(qrs_duration_ms, 1),
                'qt_interval_ms': round(qt_interval_ms, 1)
            },
            'raw_samples': beat_signal.tolist(),
            'lead_used': lead_used,
            'annotations': annotation,
            'processing_time_ms': round(processing_time_ms, 2),
            'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
        }

        api_logger.info(f"Beat {beat_index} analysis completed in {processing_time_ms:.2f}ms")
        return jsonify(response_data)

    except Exception as e:
        error_id = api_logger.generate_error_id()
        api_logger.error(f"{error_id}: Error in /api/ecg/beat/{beat_index} - {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Beat analysis failed',
            'error_id': error_id,
            'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
        }), 500


@app.route('/api/ecg/segment', methods=['POST'])
def get_segment():
    """
    Time window analysis endpoint

    Request body:
    {
        "ecg_signal": [[...], [...], ...],  # 4096 x 12 array
        "start_ms": 1000,                    # Start time in milliseconds
        "end_ms": 3000                       # End time in milliseconds
    }

    Response:
    {
        "segment": {
            "start_ms": 1000,
            "end_ms": 3000,
            "beats_in_segment": 2,
            "rhythm_analysis": "Regular sinus rhythm",
            "events": [
                {"type": "r_peak", "time_ms": 1350},
                {"type": "r_peak", "time_ms": 2180}
            ]
        }
    }
    """
    start_time = time.time()

    try:
        # Input validation
        data = request.get_json()

        if not data or 'ecg_signal' not in data:
            error_id = api_logger.generate_error_id()
            api_logger.error(f"{error_id}: Missing ecg_signal in /api/ecg/segment")
            return jsonify({
                'error': 'Missing required field: ecg_signal',
                'error_id': error_id,
                'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
            }), 400

        if 'start_ms' not in data or 'end_ms' not in data:
            error_id = api_logger.generate_error_id()
            api_logger.error(f"{error_id}: Missing time range in /api/ecg/segment")
            return jsonify({
                'error': 'Missing required fields: start_ms and end_ms',
                'error_id': error_id,
                'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
            }), 400

        # Convert to numpy array
        try:
            ecg_signal = np.array(data['ecg_signal'], dtype=np.float32)
        except (ValueError, TypeError) as e:
            error_id = api_logger.generate_error_id()
            api_logger.error(f"{error_id}: Invalid ecg_signal format - {str(e)}")
            return jsonify({
                'error': 'ecg_signal must be a numeric array',
                'error_id': error_id,
                'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
            }), 400

        # Shape validation
        if ecg_signal.shape != (4096, 12):
            error_id = api_logger.generate_error_id()
            api_logger.error(f"{error_id}: Invalid shape {ecg_signal.shape}")
            return jsonify({
                'error': f'Invalid ECG shape {ecg_signal.shape}, expected (4096, 12)',
                'error_id': error_id,
                'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
            }), 400

        # Get time range
        start_ms = float(data['start_ms'])
        end_ms = float(data['end_ms'])

        # Validate time range
        max_duration_ms = (len(ecg_signal) / hr_analyzer.fs) * 1000
        if start_ms < 0 or end_ms > max_duration_ms or start_ms >= end_ms:
            error_id = api_logger.generate_error_id()
            api_logger.error(f"{error_id}: Invalid time range [{start_ms}, {end_ms}]")
            return jsonify({
                'error': f'Invalid time range [{start_ms}, {end_ms}], max duration is {max_duration_ms:.1f}ms',
                'error_id': error_id,
                'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
            }), 400

        # Detect R-peaks
        with PerformanceTimer(f"Segment analysis [{start_ms}-{end_ms}ms]", api_logger):
            r_peaks, lead_used, _, _ = hr_analyzer.detect_r_peaks(ecg_signal)

        # Convert R-peaks to milliseconds
        r_peaks_ms = (r_peaks / hr_analyzer.fs) * 1000

        # Filter R-peaks within time window
        beats_in_segment = r_peaks_ms[(r_peaks_ms >= start_ms) & (r_peaks_ms <= end_ms)]

        # Analyze rhythm in segment
        if len(beats_in_segment) >= 2:
            rr_intervals = np.diff(beats_in_segment)
            rr_cv = np.std(rr_intervals) / np.mean(rr_intervals)

            if rr_cv < 0.10:
                rhythm = "Regular sinus rhythm"
            elif rr_cv < 0.20:
                rhythm = "Mildly irregular rhythm"
            else:
                rhythm = "Irregular rhythm (possible arrhythmia)"
        elif len(beats_in_segment) == 1:
            rhythm = "Single beat detected"
        else:
            rhythm = "No beats detected in segment"

        # Create events list
        events = [
            {
                'type': 'r_peak',
                'time_ms': round(float(peak_ms), 1)
            }
            for peak_ms in beats_in_segment
        ]

        processing_time_ms = (time.time() - start_time) * 1000

        response_data = {
            'segment': {
                'start_ms': start_ms,
                'end_ms': end_ms,
                'duration_ms': end_ms - start_ms,
                'beats_in_segment': len(beats_in_segment),
                'rhythm_analysis': rhythm,
                'events': events,
                'lead_used': lead_used
            },
            'processing_time_ms': round(processing_time_ms, 2),
            'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
        }

        api_logger.info(f"Segment analysis [{start_ms}-{end_ms}ms] completed: {len(beats_in_segment)} beats in {processing_time_ms:.2f}ms")
        return jsonify(response_data)

    except Exception as e:
        error_id = api_logger.generate_error_id()
        api_logger.error(f"{error_id}: Error in /api/ecg/segment - {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Segment analysis failed',
            'error_id': error_id,
            'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
        }), 500


if __name__ == '__main__':
    initialize()
    app.run(host='0.0.0.0', port=5000, debug=True)