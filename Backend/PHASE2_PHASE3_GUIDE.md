# Phase 2 & Phase 3 Implementation Guide

**Purpose:** Complete implementation instructions for remaining enhancements
**Status:** Phase 1 COMPLETE ✅ | Phase 2 & 3 Ready for Implementation

---

## Phase 2: User Experience Enhancements

### Feature 2.1: Adaptive Storytelling Mode

#### Implementation Location
**File:** `Backend/clinical_decision_support_llm.py`

#### Changes Required

**Step 1: Update Mode Validation** (Line 481)
```python
# OLD:
if output_mode not in ['clinical_expert', 'patient_education']:
    raise ValueError(f"Invalid output_mode: {output_mode}...")

# NEW:
if output_mode not in ['clinical_expert', 'patient_education', 'storytelling']:
    raise ValueError(f"Invalid output_mode: {output_mode}. Must be 'clinical_expert', 'patient_education', or 'storytelling'")
```

**Step 2: Add Storytelling Prompt Builder** (After line 262)
```python
def build_storytelling_prompt(self, predictions_dict, heart_rate_data, region_health,
                               top_condition, confidence, region_focus=None):
    """
    Build immersive "Down the Rabbit Hole" narrative prompt.

    Args:
        region_focus (str, optional): Specific region to focus on (e.g., 'rbbb', 'sa_node')

    Returns:
        str: Prompt for Claude to generate storytelling narrative
    """
    focus_region = region_focus or top_condition.lower()

    prompt = f"""You are narrating an immersive VR journey through a patient's heart for remote cardiac diagnostics.
The doctor is exploring the heart in VR to diagnose the patient's condition.

**Theme:** "Down the Rabbit Hole" - The doctor is diving deeper into the heart's electrical system

**Patient's ECG Analysis:**
- Top Finding: {top_condition} (confidence: {confidence:.1%})
- Heart Rate: {heart_rate_data.get('bpm', 'N/A')} BPM
- All Predictions: {json.dumps(predictions_dict, indent=2)}

**Region Currently Focused:** {focus_region}

**Task:** Generate an immersive, medically accurate narrative that:
1. Describes the journey as the doctor "enters" this region of the heart
2. Uses "Down the Rabbit Hole" theme (progressive descent, discovery, revelation)
3. Explains what the doctor is "seeing" (electrical delays, conduction blocks, etc.)
4. Provides medical insights suitable for a cardiologist
5. Suggests where to "travel next" in the heart (waypoints)

**Output Format (JSON):**
{{
  "current_location": "{focus_region}",
  "narrative": "Your immersive narrative here (2-3 sentences, present tense, second person)",
  "medical_insight": "The clinical significance (1 sentence)",
  "waypoints": [
    {{"region": "next_region_name", "teaser": "Why to go there next"}},
    {{"region": "another_region", "teaser": "Alternative path"}}
  ],
  "atmosphere": "Dark/mysterious/revealing (set the VR mood)"
}}

**Example Narrative Style:**
"You descend into the right bundle branch, expecting smooth electrical conduction. Instead, you encounter a complete blockade—the pathway is dark, silent, frozen at 320ms delay. The electrical signal cannot pass through..."

Generate the JSON output now:"""

    return prompt
```

**Step 3: Add Storytelling Fallback** (After line 433)
```python
def _init_storytelling_fallbacks(self):
    """Initialize storytelling mode fallbacks."""
    self.storytelling_fallbacks = {
        'sa_node': {
            'narrative': "You stand at the sinoatrial node, the heart's natural pacemaker, pulsing with a steady rhythm of {} BPM. This is where every heartbeat begins—a small cluster of cells firing in perfect synchrony.",
            'medical_insight': "SA node function appears normal with regular depolarization",
            'atmosphere': "Rhythmic, glowing, pulsating blue light"
        },
        'rbbb': {
            'narrative': "You descend into the right bundle branch, expecting rapid conduction. Instead, you find a blockage—the electrical highway is severed. Signals that should pass in milliseconds are delayed by 320ms, forcing the right ventricle to contract late.",
            'medical_insight': "Complete right bundle branch block with significant conduction delay",
            'atmosphere': "Dark pathway with flickering red warning lights"
        },
        'lbbb': {
            'narrative': "The left bundle branch lies before you, but something is wrong. The pathway is blocked, forcing electrical impulses to take a slow, inefficient detour through muscle tissue instead of the rapid Purkinje fibers.",
            'medical_insight': "Left bundle branch block causing dyssynchronous ventricular contraction",
            'atmosphere': "Obstructed tunnel with dimming yellow lights"
        },
        'av_node': {
            'narrative': "You arrive at the AV node, the gatekeeper between atria and ventricles. Here, signals pause briefly—a necessary delay of {}ms to allow the atria to finish contracting before the ventricles activate.",
            'medical_insight': "AV nodal conduction shows {}ms PR interval",
            'atmosphere': "Pulsing checkpoint with amber glow"
        },
        'ra': {
            'narrative': "You float through the right atrium, watching electrical waves ripple across the chamber wall. The signal has just left the SA node and is spreading like wildfire, preparing this chamber to contract.",
            'medical_insight': "Right atrial activation occurring normally with {}ms delay from SA node",
            'atmosphere': "Expanding blue waves across chamber walls"
        },
        'la': {
            'narrative': "The left atrium surrounds you—a chamber in motion. Electrical signals wash over the walls in coordinated waves, ensuring blood is pushed efficiently into the left ventricle below.",
            'medical_insight': "Left atrial depolarization proceeding normally",
            'atmosphere': "Coordinated wave patterns, soft blue light"
        },
        'rv': {
            'narrative': "You've reached the right ventricle, the powerful pump sending blood to the lungs. {} With each contraction, this chamber squeezes, propelling blood forward.",
            'medical_insight': "Right ventricular activation shows {} severity score",
            'atmosphere': "Powerful rhythmic contractions, red muscular walls"
        },
        'lv': {
            'narrative': "You stand in the left ventricle—the heart's strongest chamber. Thick muscular walls surround you, contracting with tremendous force to push blood throughout the entire body.",
            'medical_insight': "Left ventricular function with {} activation delay",
            'atmosphere': "Intense red glow, massive muscular contractions"
        },
        'purkinje': {
            'narrative': "You're now traveling through the Purkinje fibers—the heart's electrical superhighway. These specialized cells conduct signals at incredible speed, ensuring coordinated ventricular contraction.",
            'medical_insight': "Purkinje fiber conduction at {}ms",
            'atmosphere': "Lightning-fast electrical signals, web of glowing fibers"
        },
        'bundle_his': {
            'narrative': "The Bundle of His—a critical junction where electrical signals split to reach both ventricles. This is where precision matters most.",
            'medical_insight': "Bundle of His conduction shows {}ms delay",
            'atmosphere': "Branching pathways with golden electrical arcs"
        }
    }

def get_storytelling_fallback(self, top_condition, confidence, heart_rate_data,
                               region_health, region_focus=None):
    """Generate storytelling mode fallback response."""
    focus = region_focus or top_condition.lower()
    bpm = heart_rate_data.get('bpm', 72)

    # Get base narrative for focused region
    region_data = self.storytelling_fallbacks.get(focus, {
        'narrative': f"You explore the {focus} region of the heart, searching for clues to the patient's condition.",
        'medical_insight': f"{top_condition} detected with {confidence:.1%} confidence",
        'atmosphere': "Mysterious, dimly lit"
    })

    # Format narrative with dynamic data
    narrative = region_data['narrative']
    if '{}' in narrative:
        # Fill in dynamic values (BPM, delays, severity, etc.)
        if focus in region_health:
            severity = region_health[focus].get('severity', 0)
            delay = region_health[focus].get('activation_delay_ms', 0)
            narrative = narrative.format(severity=severity, delay=delay, bpm=bpm)
        else:
            narrative = narrative.format(bpm)

    # Generate waypoints based on activation sequence
    waypoints = []
    if focus == 'sa_node':
        waypoints = [
            {"region": "ra", "teaser": "Follow the signal to the right atrium"},
            {"region": "la", "teaser": "Or observe left atrial activation"}
        ]
    elif focus == 'av_node':
        waypoints = [
            {"region": "bundle_his", "teaser": "Descend through the Bundle of His"},
            {"region": "lbbb", "teaser": "Explore the left bundle branch"},
            {"region": "rbbb", "teaser": "Or investigate the right bundle branch"}
        ]
    elif focus in ['rbbb', 'lbbb']:
        waypoints = [
            {"region": "purkinje", "teaser": "Follow the Purkinje fiber network"},
            {"region": "rv" if focus == 'rbbb' else "lv", "teaser": "Enter the target ventricle"}
        ]
    else:
        waypoints = [
            {"region": "sa_node", "teaser": "Return to the pacemaker"},
            {"region": "av_node", "teaser": "Visit the AV node gatekeeper"}
        ]

    return {
        "storytelling_journey": {
            "current_location": focus,
            "narrative": narrative,
            "medical_insight": region_data.get('medical_insight', '').format(
                severity=region_health.get(focus, {}).get('severity', 0)
            ) if focus in region_health else region_data.get('medical_insight', ''),
            "waypoints": waypoints,
            "atmosphere": region_data.get('atmosphere', 'Unknown'),
            "theme": "Down the Rabbit Hole: Cardiac Exploration"
        },
        "top_condition": top_condition,
        "confidence": confidence
    }
```

**Step 4: Update analyze() method** (Lines 484-530)
```python
# Inside analyze() method, add storytelling branch:

if output_mode == 'clinical_expert':
    prompt = self.build_clinical_expert_prompt(...)
elif output_mode == 'patient_education':
    prompt = self.build_patient_education_prompt(...)
elif output_mode == 'storytelling':
    region_focus = kwargs.get('region_focus', None)  # Allow passing region_focus
    prompt = self.build_storytelling_prompt(
        predictions_dict, heart_rate_data, region_health,
        top_condition, confidence, region_focus
    )

# ... and later in fallback section:

if output_mode == 'clinical_expert':
    return self.get_clinical_expert_fallback(...)
elif output_mode == 'patient_education':
    return self.get_patient_education_fallback(...)
elif output_mode == 'storytelling':
    region_focus = kwargs.get('region_focus', None)
    return self.get_storytelling_fallback(
        top_condition, confidence, heart_rate_data, region_health, region_focus
    )
```

**Step 5: Update method signature** (Line 465-466)
```python
def analyze(self, predictions_dict, heart_rate_data, region_health,
            top_condition, confidence, output_mode='clinical_expert', **kwargs):
```

**Step 6: Update __init__** (Line 50)
```python
self._init_patient_education_fallbacks()
self._init_clinical_expert_fallbacks()
self._init_storytelling_fallbacks()  # ADD THIS LINE
```

---

### Feature 2.2: Heart Rate Fallback Leads

#### Implementation Location
**File:** `Backend/ecg_heartrate_analyzer.py`

#### Current Problem (Line 23-27)
```python
# Hardcoded to Lead II only
if len(ecg_signal.shape) > 1:
    signal = ecg_signal[:, 1]  # Lead II (index 1)
else:
    signal = ecg_signal
```

#### Solution: Multi-Lead Fallback

**Step 1: Add Lead Priority Constants** (After line 12)
```python
# Lead priority for R-peak detection (index in 12-lead ECG)
LEAD_PRIORITY = [
    (1, "II"),     # Lead II - best for R-peak detection
    (6, "V1"),     # Lead V1 - good QRS visibility
    (10, "V5"),    # Lead V5 - strong ventricular signal
    (0, "I"),      # Lead I - limb lead backup
    (7, "aVF")     # Lead aVF - inferior view backup
]
```

**Step 2: Add Signal Quality Assessment** (New method after line 60)
```python
def assess_signal_quality(self, signal, r_peaks):
    """
    Assess R-peak detection quality for a given lead.

    Args:
        signal: 1D ECG signal
        r_peaks: Detected R-peak indices

    Returns:
        float: Quality score (0.0 to 1.0, higher is better)
    """
    if len(r_peaks) < 2:
        return 0.0  # Too few peaks

    # Calculate SNR estimate
    peak_amplitudes = [abs(signal[idx]) for idx in r_peaks if idx < len(signal)]
    if not peak_amplitudes:
        return 0.0

    avg_peak_amplitude = np.mean(peak_amplitudes)
    signal_noise = np.std(signal)

    if signal_noise == 0:
        return 0.0

    snr = avg_peak_amplitude / signal_noise

    # Check rhythm regularity
    rr_intervals = np.diff(r_peaks)
    if len(rr_intervals) > 0:
        regularity = 1.0 - (np.std(rr_intervals) / np.mean(rr_intervals))
        regularity = max(0.0, min(1.0, regularity))
    else:
        regularity = 0.0

    # Combined quality score
    quality = (snr * 0.6) + (regularity * 0.4)
    quality = min(1.0, quality / 10.0)  # Normalize to 0-1

    return quality
```

**Step 3: Rewrite detect_r_peaks() with Fallback** (Lines 15-46)
```python
def detect_r_peaks(self, ecg_signal):
    """
    Detect R-peaks using Pan-Tompkins algorithm with multi-lead fallback.

    Args:
        ecg_signal: numpy array (4096, 12) or (4096,)

    Returns:
        tuple: (r_peak_indices, lead_used, lead_quality, fallback_triggered)
    """
    # If 1D signal, use it directly
    if len(ecg_signal.shape) == 1:
        signal = ecg_signal
        lead_used = "Unknown"
        return self._detect_peaks_single_lead(signal), lead_used, 1.0, False

    # Try leads in priority order
    best_peaks = None
    best_quality = 0.0
    best_lead_name = None
    best_lead_idx = None
    fallback_triggered = False

    for lead_idx, lead_name in LEAD_PRIORITY:
        if lead_idx >= ecg_signal.shape[1]:
            continue  # Skip if lead not available

        signal = ecg_signal[:, lead_idx]

        try:
            r_peaks = self._detect_peaks_single_lead(signal)
            quality = self.assess_signal_quality(signal, r_peaks)

            print(f"[HR] Lead {lead_name} (index {lead_idx}): {len(r_peaks)} peaks, quality={quality:.3f}")

            # Accept if quality threshold met
            if quality > 0.7:
                print(f"[HR] Using Lead {lead_name} (quality {quality:.3f} > 0.7 threshold)")
                return r_peaks, lead_name, quality, fallback_triggered

            # Track best attempt
            if quality > best_quality:
                best_quality = quality
                best_peaks = r_peaks
                best_lead_name = lead_name
                best_lead_idx = lead_idx

            # Mark fallback if we skip Lead II
            if lead_idx != 1:  # Not Lead II
                fallback_triggered = True

        except Exception as e:
            print(f"[HR] Lead {lead_name} failed: {e}")
            continue

    # Use best attempt if no lead met threshold
    if best_peaks is not None:
        print(f"[HR] No lead met 0.7 threshold - using best: Lead {best_lead_name} (quality {best_quality:.3f})")
        return best_peaks, best_lead_name, best_quality, True

    # Ultimate fallback: Lead II regardless of quality
    print("[HR] All leads failed - forcing Lead II detection")
    signal = ecg_signal[:, 1]
    r_peaks = self._detect_peaks_single_lead(signal)
    return r_peaks, "II (forced)", 0.0, True
```

**Step 4: Extract Single-Lead Detection** (New method)
```python
def _detect_peaks_single_lead(self, signal):
    """
    Detect R-peaks on a single lead using Pan-Tompkins.

    Args:
        signal: 1D ECG signal

    Returns:
        np.ndarray: R-peak indices
    """
    # Pan-Tompkins algorithm
    filtered = self.bandpass_filter(signal)
    differentiated = np.diff(filtered)
    squared = differentiated ** 2

    # Integrate
    window_size = int(0.150 * self.fs)
    integrated = np.convolve(squared, np.ones(window_size)/window_size, mode='same')

    # Find peaks
    min_distance = int(0.2 * self.fs)  # 200ms minimum between beats
    peaks, _ = find_peaks(
        integrated,
        distance=min_distance,
        prominence=np.std(integrated) * 0.5
    )

    return peaks
```

**Step 5: Update analyze() method** (Lines 63-82)
```python
def analyze(self, ecg_signal):
    """
    Analyze ECG to extract heart rate metrics with multi-lead fallback.

    Returns:
        dict: {bpm, rr_intervals_ms, beat_timestamps, r_peak_count,
               lead_used, lead_quality, fallback_triggered}
    """
    r_peaks, lead_used, lead_quality, fallback_triggered = self.detect_r_peaks(ecg_signal)

    # Calculate BPM
    if len(r_peaks) < 2:
        return {
            'bpm': 60.0,
            'rr_intervals_ms': [],
            'beat_timestamps': [],
            'r_peak_count': 0,
            'lead_used': lead_used,
            'lead_quality': 0.0,
            'fallback_triggered': fallback_triggered
        }

    rr_intervals_samples = np.diff(r_peaks)
    rr_intervals_ms = (rr_intervals_samples / self.fs) * 1000

    avg_rr_ms = np.mean(rr_intervals_ms)
    bpm = 60000 / avg_rr_ms

    beat_timestamps = (r_peaks / self.fs).tolist()

    return {
        'bpm': round(bpm, 1),
        'rr_intervals_ms': [round(x, 1) for x in rr_intervals_ms.tolist()],
        'beat_timestamps': [round(x, 2) for x in beat_timestamps],
        'r_peak_count': len(r_peaks),
        'lead_used': lead_used,
        'lead_quality': round(lead_quality, 3),
        'fallback_triggered': fallback_triggered
    }
```

---

## Phase 3: Temporal Drilldown Endpoints

**File:** `Backend/ecg_api.py` (add after line 329)

### Endpoint 1: Beat Detection Only

```python
@app.route('/api/ecg/beats', methods=['POST'])
def detect_beats():
    """
    Fast R-peak detection only (no full analysis).

    Request: {"ecg_signal": [[...], [...]]}
    Response: {"r_peaks": [...], "beat_count": 12, "rhythm": "regular"}
    """
    try:
        data = request.get_json()
        ecg_signal = np.array(data['ecg_signal'], dtype=np.float32)

        # Just heart rate analysis
        hr_data = hr_analyzer.analyze(ecg_signal)

        # Rhythm assessment
        rr_intervals = hr_data.get('rr_intervals_ms', [])
        if len(rr_intervals) > 2:
            rr_std = np.std(rr_intervals)
            rr_mean = np.mean(rr_intervals)
            rhythm = "regular" if (rr_std / rr_mean) < 0.15 else "irregular"
        else:
            rhythm = "insufficient_data"

        return jsonify({
            'r_peaks': hr_data.get('beat_timestamps', []),
            'beat_count': hr_data.get('r_peak_count', 0),
            'avg_rr_interval_ms': round(np.mean(rr_intervals), 1) if rr_intervals else 0,
            'rhythm': rhythm,
            'lead_used': hr_data.get('lead_used', 'II'),
            'processing_time_ms': 0  # TODO: add timing
        })

    except Exception as e:
        error_id = api_logger.generate_error_id()
        api_logger.error(f"{error_id}: Beat detection failed - {str(e)}")
        return jsonify({
            'error': 'Beat detection failed',
            'error_id': error_id
        }), 500
```

### Endpoint 2: Single Beat Analysis

```python
@app.route('/api/ecg/beat/<int:beat_index>', methods=['POST'])
def analyze_beat(beat_index):
    """
    Analyze a single heartbeat in detail.

    Request: {"ecg_signal": [[...], [...]]}
    Response: {"beat_index": 3, "waveform": {...}, "intervals": {...}}
    """
    try:
        data = request.get_json()
        ecg_signal = np.array(data['ecg_signal'], dtype=np.float32)

        # Detect all beats first
        hr_data = hr_analyzer.analyze(ecg_signal)
        r_peaks = hr_data.get('beat_timestamps', [])

        if beat_index >= len(r_peaks):
            return jsonify({
                'error': f'Beat index {beat_index} out of range (0-{len(r_peaks)-1})'
            }), 400

        # Extract beat window (400ms before to 400ms after R-peak)
        sampling_rate = 400  # Hz
        r_peak_sample = int(r_peaks[beat_index] * sampling_rate)
        window_start = max(0, r_peak_sample - int(0.4 * sampling_rate))
        window_end = min(ecg_signal.shape[0], r_peak_sample + int(0.4 * sampling_rate))

        beat_segment = ecg_signal[window_start:window_end, 1]  # Lead II

        # TODO: Implement P-wave, QRS, T-wave detection
        # For now, return basic info
        return jsonify({
            'beat_index': beat_index,
            'time_window': {
                'start_ms': (window_start / sampling_rate) * 1000,
                'end_ms': (window_end / sampling_rate) * 1000,
                'duration_ms': ((window_end - window_start) / sampling_rate) * 1000
            },
            'raw_samples': beat_segment.tolist(),
            'annotations': 'Beat waveform extracted (detailed analysis TBD)'
        })

    except Exception as e:
        error_id = api_logger.generate_error_id()
        api_logger.error(f"{error_id}: Single beat analysis failed - {str(e)}")
        return jsonify({
            'error': 'Beat analysis failed',
            'error_id': error_id
        }), 500
```

### Endpoint 3: Time Segment Analysis

```python
@app.route('/api/ecg/segment', methods=['POST'])
def analyze_segment():
    """
    Analyze arbitrary time segment.

    Request: {"ecg_signal": [[...]], "start_time_ms": 1000, "end_time_ms": 3000}
    """
    try:
        data = request.get_json()
        ecg_signal = np.array(data['ecg_signal'], dtype=np.float32)
        start_ms = data.get('start_time_ms', 0)
        end_ms = data.get('end_time_ms', 2000)

        sampling_rate = 400
        start_sample = int((start_ms / 1000) * sampling_rate)
        end_sample = int((end_ms / 1000) * sampling_rate)

        segment = ecg_signal[start_sample:end_sample, :]

        # Detect beats in segment
        hr_data = hr_analyzer.analyze(segment)

        return jsonify({
            'segment': {
                'start_ms': start_ms,
                'end_ms': end_ms,
                'beats_in_segment': hr_data.get('r_peak_count', 0),
                'rhythm_analysis': 'Regular sinus rhythm',  # TODO: implement
                'raw_data': segment[:, 1].tolist()[:100],  # Limit to 100 samples for response size
                'events': [
                    {'type': 'r_peak', 'time_ms': start_ms + (ts * 1000)}
                    for ts in hr_data.get('beat_timestamps', [])
                ]
            }
        })

    except Exception as e:
        error_id = api_logger.generate_error_id()
        api_logger.error(f"{error_id}: Segment analysis failed - {str(e)}")
        return jsonify({
            'error': 'Segment analysis failed',
            'error_id': error_id
        }), 500
```

---

## Testing Strategy

### Test Storytelling Mode
```python
# Backend/test_storytelling.py
import requests
import json

response = requests.post('http://localhost:5000/api/ecg/analyze', json={
    'ecg_signal': [...],  # Load from synthetic_ecg_normal.json
    'output_mode': 'storytelling',
    'region_focus': 'sa_node'
})

print(json.dumps(response.json()['llm_interpretation']['storytelling_journey'], indent=2))
```

### Test Heart Rate Fallback
```python
# Create corrupted ECG with Lead II noise
corrupted_ecg = normal_ecg.copy()
corrupted_ecg[:, 1] = np.random.randn(4096)  # Destroy Lead II

response = requests.post('http://localhost:5000/api/ecg/analyze', json={
    'ecg_signal': corrupted_ecg.tolist()
})

hr_data = response.json()['heart_rate']
print(f"Lead used: {hr_data['lead_used']}")
print(f"Fallback triggered: {hr_data['fallback_triggered']}")
print(f"Quality: {hr_data['lead_quality']}")
```

### Test Temporal Endpoints
```python
# Test beat detection
response = requests.post('http://localhost:5000/api/ecg/beats', json={
    'ecg_signal': [...]
})
print(f"Detected {response.json()['beat_count']} beats")

# Test single beat
response = requests.post('http://localhost:5000/api/ecg/beat/3', json={
    'ecg_signal': [...]
})
print(f"Beat 3 waveform: {len(response.json()['raw_samples'])} samples")
```

---

## Implementation Checklist

### Phase 2
- [ ] Add storytelling mode validation
- [ ] Create storytelling prompt builder
- [ ] Add storytelling fallbacks for 10 regions
- [ ] Update analyze() method
- [ ] Test storytelling with VR Unity client

- [ ] Add LEAD_PRIORITY constants
- [ ] Implement assess_signal_quality()
- [ ] Rewrite detect_r_peaks() with fallback
- [ ] Extract _detect_peaks_single_lead()
- [ ] Update analyze() response structure
- [ ] Test with corrupted leads

### Phase 3
- [ ] Add GET /api/ecg/beats endpoint
- [ ] Add POST /api/ecg/beat/<index> endpoint
- [ ] Add POST /api/ecg/segment endpoint
- [ ] Implement P-QRS-T wave detection (advanced)
- [ ] Add rhythm classification (advanced)
- [ ] Test all temporal endpoints

### Documentation
- [ ] Update Backend/README.md with new endpoints
- [ ] Update IMPLEMENTATION_CHECKLIST.md
- [ ] Create API examples for Unity team
- [ ] Document storytelling mode usage

### Final
- [ ] Commit Phase 2 changes
- [ ] Commit Phase 3 changes
- [ ] Push to GitHub main branch
- [ ] Update hackathon presentation deck

---

## Estimated Time Remaining

- **Phase 2 Storytelling:** 3-4 hours
- **Phase 2 HR Fallback:** 1-2 hours
- **Phase 3 Temporal Endpoints:** 4-5 hours
- **Testing & Documentation:** 2-3 hours

**Total:** 10-14 hours

---

## Priority Recommendations

**For Hackathon Demo (Minimum Viable):**
1. ✅ Phase 1 (DONE) - Production-ready backend
2. **Storytelling mode** - High demo impact, aligns with "Down the Rabbit Hole" theme
3. **HR fallback** - Robustness for live demo

**Nice to Have:**
4. Temporal endpoints - Advanced feature, not critical for basic VR demo

**Unity can integrate NOW with Phase 1 complete!**