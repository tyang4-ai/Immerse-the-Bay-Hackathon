from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import time

from model_loader import ECGModelLoader
from ecg_heartrate_analyzer import ECGHeartRateAnalyzer

from heart_region_mapper import HeartRegionMapper
from clinical_decision_support_llm import ClinicalDecisionSupportLLM

app = Flask(__name__)
CORS(app)

ecg_model = ECGModelLoader()
hr_analyzer = ECGHeartRateAnalyzer(sampling_rate=400)

region_mapper = HeartRegionMapper()
clinical_llm = ClinicalDecisionSupportLLM()

def initialize():
    print("Initializing backend...")
    if not ecg_model.load_model():
        print("WARNING: Running in simulation mode (model not loaded)")
    print("Backend ready!")

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'model_loaded': ecg_model.model is not None
    })

@app.route('/api/ecg/analyze', methods=['POST'])
def analyze_ecg():
    start_time = time.time()

    try:
        data = request.get_json()

        if 'ecg_signal' not in data:
            return jsonify({'error': 'Missing ecg_signal field'}), 400

        ecg_signal = np.array(data['ecg_signal'], dtype=np.float32)

        if ecg_signal.shape != (4096, 12):
            return jsonify({
                'error': f'Invalid shape {ecg_signal.shape}, expected (4096, 12)'
            }), 400

        predictions_dict = ecg_model.predict(ecg_signal)
        top_condition, confidence = ecg_model.get_top_condition(predictions_dict)

        heart_rate_data = hr_analyzer.analyze(ecg_signal)

        region_health = region_mapper.get_region_health_status(predictions_dict)
        activation_sequence = region_mapper.get_activation_sequence(region_health)

        # 4. Clinical Decision Support (Doctor-focused)
        llm_interpretation = clinical_llm.analyze(
            predictions_dict,
            heart_rate_data,
            region_health,
            top_condition,
            confidence,
            output_mode='clinical_expert'  # Use clinical expert mode for doctors
        )

        # === RESPONSE ===
        processing_time_ms = (time.time() - start_time) * 1000

        return jsonify({
            'predictions': predictions_dict,
            'heart_rate': heart_rate_data,
            'region_health': region_health if region_health else None,
            'activation_sequence': activation_sequence if activation_sequence else None,
            'llm_interpretation': llm_interpretation if llm_interpretation else None,
            'top_condition': top_condition,
            'confidence': round(confidence, 3),
            'processing_time_ms': round(processing_time_ms, 2),
            'model_version': '1.0.0',
            'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    initialize()
    app.run(host='0.0.0.0', port=5000, debug=True)