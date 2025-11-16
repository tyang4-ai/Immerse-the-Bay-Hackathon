# Backend Development Task Split

## Team Structure
- **Backend Developer 1** (You): ECG Model Integration + Heart Rate Analysis
- **Backend Developer 2** (Teammate): Region Mapping + LLM Integration

**Working Mode:** Parallel development with clear module boundaries

---

## Backend Developer 1 (You): Core ML & Signal Processing

### Your Responsibilities

#### 1. ECG Model Integration (2 hours)
**Goal:** Load TensorFlow model and run predictions

**Tasks:**
- [ ] Create `Backend/model_loader.py`
  - Load model from `model/model.hdf5`
  - Handle model initialization errors
  - Provide `predict(ecg_signal)` function

**Code Template:**
```python
# Backend/model_loader.py

import tensorflow as tf
from tensorflow.keras.models import load_model
import numpy as np
import os

class ECGModelLoader:
    def __init__(self, model_path='model/model.hdf5'):
        self.model_path = model_path
        self.model = None
        self.condition_names = [
            '1st_degree_AV_block',
            'RBBB',
            'LBBB',
            'sinus_bradycardia',
            'atrial_fibrillation',
            'sinus_tachycardia'
        ]

    def load_model(self):
        if os.path.exists(self.model_path):
            self.model = load_model(self.model_path, compile=False)
            self.model.compile(loss='binary_crossentropy', optimizer='adam')
            print(f"ECG model loaded from {self.model_path}")
            return True
        else:
            print(f"ERROR: Model file not found at {self.model_path}")
            return False

    def predict(self, ecg_signal):
        """
        Args:
            ecg_signal: numpy array (4096, 12) or (1, 4096, 12)

        Returns:
            dict: {condition_name: probability}
        """
        if self.model is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")

        # Ensure correct shape
        if ecg_signal.shape == (4096, 12):
            ecg_signal = np.expand_dims(ecg_signal, axis=0)

        # Run inference
        predictions = self.model.predict(ecg_signal, verbose=0)[0]

        # Format as dict
        return {
            name: float(prob)
            for name, prob in zip(self.condition_names, predictions)
        }

    def get_top_condition(self, predictions_dict):
        top_condition = max(predictions_dict, key=predictions_dict.get)
        confidence = predictions_dict[top_condition]
        return top_condition, confidence
```

**Testing:**
```bash
cd Backend
python -c "from model_loader import ECGModelLoader; loader = ECGModelLoader(); loader.load_model(); print('Model loaded successfully')"
```

---

#### 2. Heart Rate Analysis - R-Peak Detection (3 hours)
**Goal:** Extract BPM and beat timing from ECG signal

**Tasks:**
- [ ] Create `Backend/ecg_heartrate_analyzer.py`
  - Implement Pan-Tompkins algorithm (simplified with scipy)
  - Detect R-peaks
  - Calculate BPM from R-R intervals
  - Return beat timestamps

**Code Template:**
```python
# Backend/ecg_heartrate_analyzer.py

import numpy as np
from scipy.signal import butter, filtfilt, find_peaks

class ECGHeartRateAnalyzer:
    def __init__(self, sampling_rate=400):
        self.fs = sampling_rate

    def bandpass_filter(self, signal, lowcut=5, highcut=15):
        nyquist = 0.5 * self.fs
        low = lowcut / nyquist
        high = highcut / nyquist
        b, a = butter(2, [low, high], btype='band')
        return filtfilt(b, a, signal)

    def detect_r_peaks(self, ecg_signal):
        """
        Args:
            ecg_signal: (4096, 12) array or 1D array

        Returns:
            List of R-peak sample indices
        """
        # Use lead II for detection
        if len(ecg_signal.shape) > 1:
            signal = ecg_signal[:, 1]  # Lead II
        else:
            signal = ecg_signal

        # Pan-Tompkins algorithm
        filtered = self.bandpass_filter(signal)
        differentiated = np.diff(filtered)
        squared = differentiated ** 2

        # Moving window integration
        window_size = int(0.150 * self.fs)
        integrated = np.convolve(squared, np.ones(window_size)/window_size, mode='same')

        # Find peaks
        min_distance = int(0.2 * self.fs)  # 200ms = max 300 BPM
        peaks, _ = find_peaks(
            integrated,
            distance=min_distance,
            prominence=np.std(integrated) * 0.5
        )

        return peaks

    def calculate_bpm(self, r_peak_indices):
        if len(r_peak_indices) < 2:
            return 60.0, []

        rr_intervals_samples = np.diff(r_peak_indices)
        rr_intervals_ms = (rr_intervals_samples / self.fs) * 1000

        hr_per_interval = 60000 / rr_intervals_ms
        median_bpm = np.median(hr_per_interval)

        return float(median_bpm), rr_intervals_ms.tolist()

    def get_beat_timestamps(self, r_peak_indices):
        return (r_peak_indices / self.fs).tolist()

    def analyze(self, ecg_signal):
        """
        Complete analysis in one call

        Returns:
            dict: {
                'bpm': float,
                'rr_intervals_ms': list,
                'beat_timestamps': list,
                'r_peak_count': int
            }
        """
        r_peaks = self.detect_r_peaks(ecg_signal)
        bpm, rr_intervals = self.calculate_bpm(r_peaks)
        timestamps = self.get_beat_timestamps(r_peaks)

        return {
            'bpm': round(bpm, 1),
            'rr_intervals_ms': [round(rr, 1) for rr in rr_intervals],
            'beat_timestamps': [round(t, 2) for t in timestamps],
            'r_peak_count': len(r_peaks)
        }
```

**Dependencies:**
```bash
pip install scipy
```

**Testing:**
```python
# Test with synthetic data
import numpy as np
from ecg_heartrate_analyzer import ECGHeartRateAnalyzer

# Create fake ECG (simple sine wave with peaks)
time = np.linspace(0, 10, 4000)
fake_ecg = np.sin(2 * np.pi * 1.2 * time)  # 72 BPM ≈ 1.2 Hz

analyzer = ECGHeartRateAnalyzer()
result = analyzer.analyze(fake_ecg)
print(f"Detected BPM: {result['bpm']}")  # Should be ~72
print(f"Beat count: {result['r_peak_count']}")  # Should be ~12
```

---

#### 3. Flask API Structure (2 hours)
**Goal:** Create main Flask application and endpoint

**Tasks:**
- [ ] Create/Update `Backend/ecg_api.py`
  - Initialize Flask app
  - Load models on startup
  - Create `/api/ecg/analyze` endpoint
  - Integrate your modules (model + heart rate)
  - Leave placeholders for teammate's modules

**Code Template:**
```python
# Backend/ecg_api.py

from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import time

from model_loader import ECGModelLoader
from ecg_heartrate_analyzer import ECGHeartRateAnalyzer

# TODO: Import teammate's modules when ready
# from heart_region_mapper import HeartRegionMapper
# from llm_medical_interpreter import LLMMedicalInterpreter

app = Flask(__name__)
CORS(app)

# Initialize your modules
ecg_model = ECGModelLoader()
hr_analyzer = ECGHeartRateAnalyzer(sampling_rate=400)

# TODO: Initialize teammate's modules
# region_mapper = HeartRegionMapper()
# llm_interpreter = LLMMedicalInterpreter()

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

        # === YOUR PART ===
        # 1. ECG Model Predictions
        predictions_dict = ecg_model.predict(ecg_signal)
        top_condition, confidence = ecg_model.get_top_condition(predictions_dict)

        # 2. Heart Rate Analysis
        heart_rate_data = hr_analyzer.analyze(ecg_signal)

        # === TEAMMATE'S PART (Placeholder) ===
        # 3. Region Health Mapping
        region_health = {}  # TODO: Call region_mapper.get_region_health_status(predictions_dict)
        activation_sequence = []  # TODO: Call region_mapper.get_activation_sequence(region_health)

        # 4. LLM Interpretation
        llm_interpretation = {}  # TODO: Call llm_interpreter.interpret_ecg_analysis(...)

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
```

**Testing:**
```bash
# Start server
python ecg_api.py

# Test health endpoint
curl http://localhost:5000/health

# Test with dummy ECG (from another terminal)
python test_api.py  # Create this test script
```

---

#### 4. Testing & Documentation (1 hour)
**Tasks:**
- [ ] Create test script with sample ECG data
- [ ] Test each module independently
- [ ] Test full API endpoint
- [ ] Document any issues for teammate

---

### Your Estimated Timeline

| Task | Duration | Dependencies |
|------|----------|--------------|
| ECG Model Integration | 2 hours | Model file exists |
| Heart Rate Analysis | 3 hours | scipy installed |
| Flask API Structure | 2 hours | Flask installed |
| Testing | 1 hour | All above complete |
| **TOTAL** | **8 hours** | |

---

## Backend Developer 2 (Teammate): Mapping & LLM

### Teammate's Responsibilities

#### 1. Heart Region Mapper (3 hours)
**Goal:** Map ECG conditions to anatomical regions with colors

**Tasks:**
- [ ] Create `Backend/heart_region_mapper.py`
  - Define anatomical regions (SA node, AV node, bundles, chambers)
  - Map 6 conditions → affected regions
  - Calculate severity per region
  - Convert severity → RGB color spectrum
  - Generate activation sequence timing

**Interface:**
```python
class HeartRegionMapper:
    def get_region_health_status(self, predictions_dict):
        """
        Args:
            predictions_dict: {condition_name: probability}

        Returns:
            {
                region_name: {
                    'severity': 0.0-1.0,
                    'color': [r, g, b],
                    'activation_delay_ms': float,
                    'affected_by': [condition_names]
                }
            }
        """
        pass

    def get_activation_sequence(self, region_health):
        """
        Returns:
            List of [region_name, delay_ms] sorted by activation time
        """
        pass
```

**Reference:** See `dummy_data/sample_*.json` for expected output format

---

#### 2. Clinical Decision Support LLM (4 hours) ✅ COMPLETED
**Goal:** Use Claude API to provide clinical decision support for expert physicians

**Note:** Refactored from `llm_medical_interpreter.py` to `clinical_decision_support_llm.py` to focus on doctor-facing clinical guidance rather than patient education.

**Tasks:**
- [x] Create `Backend/clinical_decision_support_llm.py`
  - Set up Anthropic Claude API client
  - Build structured prompts for clinical experts
  - Parse JSON responses
  - Implement fallback clinical guidance
  - Support dual output modes (clinical_expert + patient_education)

**Interface:**
```python
class ClinicalDecisionSupportLLM:
    def __init__(self, api_key=None):
        """
        Args:
            api_key: Anthropic API key (or use ANTHROPIC_API_KEY env var)
        """
        pass

    def analyze(self, predictions_dict, heart_rate_data, region_health,
                top_condition, confidence, output_mode='clinical_expert'):
        """
        Args:
            output_mode: 'clinical_expert' (default) or 'patient_education' (legacy)

        Returns (clinical_expert mode):
            {
                'differential_diagnosis': {
                    'primary_diagnosis': str,
                    'alternative_diagnoses': [str],
                    'reasoning': str,
                    'probability_interpretation': str
                },
                'risk_assessment': {
                    'urgency': 'immediate|urgent|routine',
                    'stroke_risk': str,
                    'sudden_death_risk': str,
                    'progression_risk': str,
                    'risk_factors': [str]
                },
                'clinical_correlations': {...},
                'recommended_workup': {
                    'immediate_tests': [str],
                    'follow_up_tests': [str],
                    'specialist_referrals': [str],
                    'imaging': [str]
                },
                'treatment_considerations': {...},
                'vr_visualization_strategy': {
                    'primary_view': str,
                    'regions_to_emphasize': [str],
                    'animation_recommendations': str,
                    'comparison_views': [str],
                    'teaching_points': [str],
                    'interactive_elements': [str]
                },
                'literature_references': {...},
                'critical_alerts': [str]
            }

        Returns (patient_education mode - legacy):
            {
                'plain_english_summary': str,
                'severity_assessment': {...},
                'patient_explanation': str,
                'clinical_notes': str,
                'visualization_suggestions': {...}
            }
        """
        pass

    # Legacy method for backward compatibility
    def interpret_ecg_analysis(self, ...):
        # Calls analyze() with output_mode='patient_education'
        pass
```

**Dependencies:**
```bash
pip install anthropic
```

**Environment Variable:**
```bash
export ANTHROPIC_API_KEY=sk-ant-...
```

**Reference:**
- Clinical expert mode: See `dummy_data/sample_clinical_expert_rbbb.json`
- Patient education mode: See `dummy_data/sample_rbbb.json` `llm_interpretation` field

---

#### 3. Integration with Flask API (1 hour)
**Tasks:**
- [ ] Update `Backend/ecg_api.py` (in progress by Dev 1)
  - Import your modules
  - Call region mapper
  - Call LLM interpreter
  - Add to JSON response

**Integration Point:**
```python
# In ecg_api.py
from heart_region_mapper import HeartRegionMapper
from clinical_decision_support_llm import ClinicalDecisionSupportLLM

region_mapper = HeartRegionMapper()
clinical_llm = ClinicalDecisionSupportLLM()

@app.route('/api/ecg/analyze', methods=['POST'])
def analyze_ecg():
    # ... Dev 1's code ...

    # YOUR PART:
    region_health = region_mapper.get_region_health_status(predictions_dict)
    activation_sequence = region_mapper.get_activation_sequence(region_health)

    # Use clinical expert mode (doctor-focused)
    llm_interpretation = clinical_llm.analyze(
        predictions_dict, heart_rate_data, region_health,
        top_condition, confidence,
        output_mode='clinical_expert'  # or 'patient_education' for legacy
    )

    # ... return response ...
```

---

#### 4. Testing & Documentation (1 hour)
**Tasks:**
- [ ] Test region mapping with sample predictions
- [ ] Test LLM API (ensure valid JSON output)
- [ ] Test fallback mode (no API key)
- [ ] Verify output matches dummy data structure

---

### Teammate's Estimated Timeline

| Task | Duration | Dependencies |
|------|----------|--------------|
| Heart Region Mapper | 3 hours | Medical knowledge |
| LLM Integration | 4 hours | Anthropic API key |
| Flask Integration | 1 hour | Dev 1's API ready |
| Testing | 1 hour | All modules ready |
| **TOTAL** | **9 hours** | |

---

## Integration Points

### Data Flow

```
┌─────────────────────────────────────────┐
│  Flask Endpoint (ecg_api.py)            │
│  (Both developers contribute)           │
└─────────────────┬───────────────────────┘
                  │
                  ▼
         ECG Signal Input
                  │
    ┌─────────────┴─────────────┐
    │                           │
    ▼                           ▼
┌─────────────┐           ┌─────────────┐
│  DEV 1      │           │  DEV 2      │
│             │           │             │
│ Model       │           │ Region      │
│ Predictions │──────────▶│ Mapper      │
│             │           │             │
│ Heart Rate  │           │ LLM         │
│ Analysis    │──────────▶│ Interpreter │
└─────────────┘           └─────────────┘
       │                         │
       └─────────┬───────────────┘
                 │
                 ▼
          Combined JSON Response
```

### Module Independence

**Dev 1's modules** can work independently:
- Model predictions work without region mapping
- Heart rate analysis works without LLM

**Dev 2's modules** depend on Dev 1's output:
- Region mapper needs predictions_dict
- LLM needs predictions + heart_rate + region_health

### Merge Strategy

1. **Dev 1** creates `ecg_api.py` with placeholders
2. **Dev 2** develops modules independently
3. Both commit to separate branches:
   - `backend-dev1-ecg-model`
   - `backend-dev2-mapping-llm`
4. Test individually
5. Merge into `main` when both ready
6. Final integration testing together

---

## Communication Protocol

### Daily Check-ins
- Morning: Share progress, blockers
- Evening: Commit code, update status

### Code Reviews
- Dev 1 reviews Dev 2's mapping logic
- Dev 2 reviews Dev 1's signal processing

### Questions to Coordinate
- API response structure (use dummy_data as contract)
- Error handling strategy
- Fallback behavior if modules fail

---

## Testing Strategy

### Unit Tests

**Dev 1:**
```python
# test_model.py
def test_model_loads():
    loader = ECGModelLoader()
    assert loader.load_model() == True

def test_prediction_shape():
    loader = ECGModelLoader()
    loader.load_model()
    fake_ecg = np.random.randn(4096, 12)
    predictions = loader.predict(fake_ecg)
    assert len(predictions) == 6
```

**Dev 2:**
```python
# test_region_mapper.py
def test_severity_to_color():
    mapper = HeartRegionMapper()
    color = mapper.severity_to_color(0.0)
    assert color == (0.0, 1.0, 0.0)  # Green

def test_region_mapping():
    mapper = HeartRegionMapper()
    predictions = {'RBBB': 0.9, ...}
    regions = mapper.get_region_health_status(predictions)
    assert regions['rbbb']['severity'] > 0.8
```

### Integration Test

```python
# test_full_api.py
import requests

def test_full_workflow():
    # Send sample ECG
    response = requests.post(
        'http://localhost:5000/api/ecg/analyze',
        json={'ecg_signal': fake_ecg_data}
    )

    assert response.status_code == 200
    data = response.json()

    # Check all sections exist
    assert 'predictions' in data
    assert 'heart_rate' in data
    assert 'region_health' in data
    assert 'llm_interpretation' in data
```

---

## Deliverables Checklist

### Dev 1 (You)
- [ ] `Backend/model_loader.py`
- [ ] `Backend/ecg_heartrate_analyzer.py`
- [ ] `Backend/ecg_api.py` (structure + your parts)
- [ ] `Backend/test_model.py`
- [ ] `Backend/test_heartrate.py`
- [ ] `Backend/requirements.txt` (update with scipy)

### Dev 2 (Teammate)
- [ ] `Backend/heart_region_mapper.py`
- [ ] `Backend/llm_medical_interpreter.py`
- [ ] Integration code for `ecg_api.py`
- [ ] `Backend/test_region_mapper.py`
- [ ] `Backend/test_llm.py`
- [ ] `Backend/requirements.txt` (update with anthropic)

### Together
- [ ] `Backend/test_full_api.py`
- [ ] `Backend/README.md` (setup instructions)
- [ ] Verify output matches `dummy_data/*.json`

---

## Dependencies

**Both need:**
```bash
pip install flask flask-cors numpy
```

**Dev 1 only:**
```bash
pip install tensorflow==2.2 scipy
```

**Dev 2 only:**
```bash
pip install anthropic
```

**Combined `requirements.txt`:**
```
flask>=2.0.0
flask-cors>=3.0.0
numpy>=1.19.0
tensorflow==2.2
scipy>=1.7.0
anthropic>=0.8.0
```

---

## Success Criteria

### Individual Success
- [ ] Your modules run independently
- [ ] Unit tests pass
- [ ] Code documented with docstrings

### Integration Success
- [ ] Combined API returns valid JSON
- [ ] Output structure matches dummy_data
- [ ] Flask server runs without errors
- [ ] Health endpoint returns 200 OK
- [ ] Response time < 500ms

### Demo Ready
- [ ] Unity teammate can connect and receive data
- [ ] All 4 test cases work (normal, bradycardia, RBBB, AF)
- [ ] Fallbacks work if LLM unavailable
- [ ] No crashes during continuous testing

---

## Emergency Fallbacks

**If Dev 1 blocked:**
- Use dummy_data responses directly from Flask
- Unity continues development

**If Dev 2 blocked:**
- Skip region mapping (return empty dict)
- Skip LLM (return null)
- Unity works with predictions + heart_rate only

**If both blocked:**
- Flask serves dummy_data files directly
- Unity development unaffected

---

**Remember:** Use `dummy_data/*.json` as your API contract. If output doesn't match, fix it!

Good luck! 🚀
