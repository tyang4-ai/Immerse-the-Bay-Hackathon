# Backend API - HoloHuman XR

Flask-based REST API for ECG analysis with TensorFlow model inference, heart rate detection, anatomical region mapping, and LLM-powered medical interpretation.

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Setup Instructions](#setup-instructions)
3. [Architecture Overview](#architecture-overview)
4. [API Endpoints](#api-endpoints)
5. [Development Workflow](#development-workflow)
6. [Testing](#testing)
7. [Task Split](#task-split)
8. [Troubleshooting](#troubleshooting)

---

## Quick Start

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set environment variable for Claude API
export ANTHROPIC_API_KEY="your-api-key-here"  # On Windows: set ANTHROPIC_API_KEY=your-key

# 4. Run Flask server
python ecg_api.py

# 5. Test health endpoint
curl http://localhost:5000/health
```

---

## Setup Instructions

### Prerequisites

- **Python:** 3.8+ (3.9 recommended)
- **OS:** Windows, macOS, or Linux
- **RAM:** 4 GB minimum (8 GB recommended for TensorFlow)
- **Storage:** 500 MB for model weights and dependencies

### Step 1: Clone Repository

```bash
git clone https://github.com/tyang4-ai/Immerse-the-Bay-Hackathon.git
cd Immerse-the-Bay-Hackathon/Backend
```

### Step 2: Create Virtual Environment

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**
```cmd
python -m venv venv
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Note:** This installs all required dependencies including TensorFlow 2.20, Flask, NumPy, SciPy, and Anthropic SDK.

### Step 4: Download ECG Model

The pre-trained ECG model is already included in `model/model.hdf5` (25.8 MB).

If missing, download from:
- **Zenodo:** https://zenodo.org/record/4916206
- Place `model.hdf5` in `Backend/model/` directory

### Step 5: Set Up Environment Variables

Create a `.env` file in `Backend/` directory:

```bash
ANTHROPIC_API_KEY=your-claude-api-key-here
FLASK_ENV=development
FLASK_DEBUG=True
```

**Get Claude API Key:**
1. Sign up at https://console.anthropic.com
2. Navigate to API Keys
3. Create a new key
4. Copy and paste into `.env` file

### Step 6: Verify Installation

```bash
# Run test script
python -c "import tensorflow as tf; import scipy; import anthropic; print('All dependencies installed!')"

# Check model file
ls -lh model/model.hdf5  # Should show ~26 MB file
```

---

## Architecture Overview

### 3 Analysis Pipelines

```
ECG Signal Input (4096 samples × 12 leads)
        │
        ├──> [Pipeline 1] TensorFlow Model
        │    ├─> Condition predictions (6 probabilities)
        │    └─> Top condition + confidence
        │
        ├──> [Pipeline 2] Pan-Tompkins R-Peak Detection
        │    ├─> Heart rate (BPM)
        │    ├─> R-R intervals
        │    ├─> Beat timestamps
        │    └─> R-peak count
        │
        └──> [Pipeline 3] Heart Region Mapper
             ├─> Condition → Anatomy mapping
             ├─> Per-region severity scores
             ├─> Color assignments (RGB)
             ├─> Activation delays
             └─> Activation sequence
                      │
                      └──> [Pipeline 4] Claude LLM Interpreter
                           ├─> Plain English summary
                           ├─> Severity assessment
                           ├─> Patient explanation
                           ├─> Clinical notes
                           └─> Visualization suggestions

All pipelines → Combined JSON Response → Unity VR Frontend
```

### File Structure

```
Backend/
├── ecg_api.py                              # Flask routes (7 endpoints)
├── model_loader.py                         # TensorFlow model wrapper
├── ecg_heartrate_analyzer.py               # Multi-lead R-peak detection with fallback
├── heart_region_mapper.py                  # Condition → anatomy mapping
├── clinical_decision_support_llm.py        # Claude API with 3 output modes
├── logger.py                               # Structured logging with request IDs
├── requirements.txt                        # Python dependencies
├── model/
│   └── model.hdf5                          # Pre-trained ECG weights (25.8 MB)
├── dummy_data/
│   ├── README.md                           # Unity integration guide
│   ├── sample_normal.json                  # Healthy heart example
│   ├── sample_bradycardia.json             # Sinus bradycardia
│   └── sample_tachycardia.json             # Sinus tachycardia
├── tests/                                  # Comprehensive test suites
│   ├── test_api.py                         # Full API tests
│   ├── test_storytelling.py                # Storytelling mode tests
│   ├── test_hr_fallback.py                 # Heart rate fallback tests
│   └── test_phase3.py                      # Temporal drilldown tests
├── API_INTEGRATION_GUIDE.md                # Complete Unity integration guide
├── UNITY_QUICKSTART.md                     # 15-minute quick start guide
├── ENHANCEMENT_STATUS.md                   # Phase 1-3 implementation status
└── README.md                               # This file
```

---

## API Endpoints

### 7 Production-Ready Endpoints

| Endpoint | Purpose | Avg Response | Documentation |
|----------|---------|--------------|---------------|
| POST /api/ecg/analyze | Full ECG analysis | ~260ms | [API Guide](API_INTEGRATION_GUIDE.md#1-post-apiecganalyze---full-ecg-analysis) |
| GET /health | Server health check | <10ms | [API Guide](API_INTEGRATION_GUIDE.md#2-get-health---server-health-check) |
| POST /api/ecg/beats | Fast R-peak detection | ~50ms | [API Guide](API_INTEGRATION_GUIDE.md#3-post-apiecgbeats---fast-r-peak-detection) |
| POST /api/ecg/beat/<index> | Single beat analysis | ~52ms | [API Guide](API_INTEGRATION_GUIDE.md#4-post-apiecgbeatindex---single-beat-analysis) |
| POST /api/ecg/segment | Time window analysis | ~36ms | [API Guide](API_INTEGRATION_GUIDE.md#5-post-apiecgsegment---time-window-analysis) |
| GET /api/cache/stats | Cache performance | <10ms | [API Guide](API_INTEGRATION_GUIDE.md#6-get-apicachestats---cache-performance) |
| POST /api/cache/clear | Clear cache | <10ms | [API Guide](API_INTEGRATION_GUIDE.md#7-post-apicacheclear---clear-cache) |

**Complete API documentation:** See [API_INTEGRATION_GUIDE.md](API_INTEGRATION_GUIDE.md)

### POST /api/ecg/analyze - Full ECG Analysis (Primary Endpoint)

**Description:** Analyzes ECG signal with 3 output modes: clinical_expert, patient_education, storytelling

**Request:**
```json
{
  "ecg_signal": [[...], [...], ...],  // 4096 samples × 12 leads (float array)
  "output_mode": "clinical_expert",   // "clinical_expert" | "patient_education" | "storytelling"
  "region_focus": "rbbb"              // Optional for storytelling mode
}
```

**Response:**
```json
{
  "predictions": {
    "1st_degree_AV_block": 0.05,
    "RBBB": 0.12,
    "LBBB": 0.03,
    "sinus_bradycardia": 0.78,
    "atrial_fibrillation": 0.10,
    "sinus_tachycardia": 0.15
  },
  "heart_rate": {
    "bpm": 52.3,
    "rr_intervals_ms": [1148.0, 1152.5, ...],
    "beat_timestamps": [0.5, 1.65, 2.8, ...],
    "r_peak_count": 9
  },
  "region_health": {
    "sa_node": {
      "severity": 0.5,
      "color": [1.0, 0.65, 0.0],
      "activation_delay_ms": 0,
      "affected_by": ["sinus_bradycardia"]
    },
    // ... 9 more regions
  },
  "activation_sequence": [
    ["sa_node", 0],
    ["ra", 25],
    // ... ordered by timing
  ],
  "llm_interpretation": {
    "plain_english_summary": "...",
    "severity_assessment": {...},
    "patient_explanation": "...",
    "clinical_notes": "...",
    "visualization_suggestions": {...}
  },
  "top_condition": "sinus_bradycardia",
  "confidence": 0.78,
  "processing_time_ms": 187.3,
  "model_version": "1.0.0",
  "timestamp": "2025-11-15T03:30:00Z"
}
```

**See full response schema and all 7 endpoints:** [API_INTEGRATION_GUIDE.md](API_INTEGRATION_GUIDE.md)

**Unity Quick Start (15 minutes):** [UNITY_QUICKSTART.md](UNITY_QUICKSTART.md)

---

## Development Workflow

### Backend Developer 1 (ML + Signals)

**Your tasks:** See [TASK_SPLIT.md](TASK_SPLIT.md) for detailed breakdown

1. **ECG Model Integration** (2 hours)
   - Implement `model_loader.py`
   - Test with sample ECG data

2. **Heart Rate Analysis** (3 hours)
   - Implement `ecg_heartrate_analyzer.py`
   - Pan-Tompkins R-peak detection

3. **Flask API Structure** (2 hours)
   - Create `ecg_api.py` with endpoints
   - Set up CORS and error handling

### Backend Developer 2 (Mapping + LLM) ✅ COMPLETED

**Teammate tasks:** See [TASK_SPLIT.md](TASK_SPLIT.md)

1. **Heart Region Mapper** (3 hours) ✅
   - Implemented `heart_region_mapper.py`
   - Condition → anatomy lookup tables with severity/color/timing

2. **Clinical Decision Support LLM** (4 hours) ✅
   - Implemented `clinical_decision_support_llm.py` (refactored from `llm_medical_interpreter.py`)
   - Dual modes: clinical_expert (doctor-focused) + patient_education (legacy)
   - See [Refactoring Rationale](#llm-refactoring-rationale) below

3. **Integration** (1 hour) ⏳
   - Ready to connect with Dev 1's Flask API when available

### Integration Point

Both developers merge at `ecg_api.py`:

```python
# ecg_api.py integration point
from model_loader import ECGModelLoader
from ecg_heartrate_analyzer import ECGHeartRateAnalyzer
from heart_region_mapper import HeartRegionMapper
from clinical_decision_support_llm import ClinicalDecisionSupportLLM

# All pipelines combined in /api/ecg/predict endpoint
# Use output_mode='clinical_expert' for doctor-focused guidance
```

---

## LLM Refactoring Rationale

### From Patient Education to Clinical Decision Support

**Original Design** (`llm_medical_interpreter.py`):
- Targeted general patients
- Plain English summaries
- Patient-friendly explanations
- Simplified severity ratings (low/moderate/high)

**Refactored Design** (`clinical_decision_support_llm.py`):
- Targeted expert physicians (cardiologists, ER doctors)
- Technical medical terminology
- Evidence-based clinical pathways
- Comprehensive decision support

### Why the Change?

This VR application is designed for **doctors and medical professionals**, not patients. The original patient-education approach was misaligned with the target audience.

### What Changed?

**Clinical Expert Mode (NEW - Default)**:
```python
clinical_llm.analyze(..., output_mode='clinical_expert')
```

Returns:
- **Differential diagnosis**: Alternative diagnoses to consider
- **Risk assessment**: Urgency, stroke risk, sudden death risk
- **Recommended workup**: Immediate tests, imaging, specialist referrals
- **Treatment considerations**: Medications to consider/avoid, device therapy
- **VR visualization strategy**: Specific animation recommendations for teaching
- **Literature references**: Guidelines, evidence, clinical pearls
- **Critical alerts**: Time-sensitive findings requiring immediate action

**Patient Education Mode (LEGACY - Backward Compatible)**:
```python
clinical_llm.analyze(..., output_mode='patient_education')
# OR use legacy method
clinical_llm.interpret_ecg_analysis(...)
```

Returns original patient-friendly format for potential future use.

### Example Comparison

**RBBB Case - Clinical Expert Mode**:
- "89% confidence for RBBB. The concurrent mild sinus tachycardia (18%) may represent compensatory response to reduced cardiac output from dyssynchronous ventricular contraction."
- "Recommended workup: Transthoracic echocardiogram to assess RV size/function, BNP if dyspnea present"
- "Avoid Class IC antiarrhythmics (flecainide, propafenone) - contraindicated if structural heart disease"

**RBBB Case - Patient Education Mode** (Legacy):
- "Right Bundle Branch Block means the electrical pathway that signals your right ventricle to contract is blocked or delayed..."
- "This can be a normal finding in some people, but it's important to have it evaluated by a cardiologist"

### VR Use Cases

**Teaching Rounds**:
- Doctor presents case to residents using VR
- LLM provides teaching points synchronized with 3D visualization
- Interactive elements explain pathophysiology

**Diagnostic Consultation**:
- Doctor reviews ECG findings in VR
- LLM suggests differential diagnoses and next steps
- Critical alerts highlighted for time-sensitive conditions

**Patient Explanation** (Future):
- After diagnosis, doctor can switch to patient education mode
- Simplified explanations for shared decision-making
- VR visualization helps patient understand their condition

---

## Testing

### Run All Test Suites

```bash
# Test full API functionality
python tests/test_api.py

# Test storytelling mode
python tests/test_storytelling.py

# Test heart rate multi-lead fallback
python tests/test_hr_fallback.py

# Test Phase 3 temporal drilldown endpoints
python tests/test_phase3.py
```

**All tests passing ✓** (as of 2025-11-15)

### Test Individual Endpoints with cURL

```bash
# Health check
curl http://localhost:5000/health

# Full ECG analysis
curl -X POST http://localhost:5000/api/ecg/analyze \
  -H "Content-Type: application/json" \
  -d @dummy_data/sample_normal.json

# Fast beat detection
curl -X POST http://localhost:5000/api/ecg/beats \
  -H "Content-Type: application/json" \
  -d @dummy_data/sample_normal.json

# Single beat detail
curl -X POST http://localhost:5000/api/ecg/beat/2 \
  -H "Content-Type: application/json" \
  -d @dummy_data/sample_normal.json
```

### Unity Integration Testing

See [UNITY_QUICKSTART.md](UNITY_QUICKSTART.md) for 15-minute Unity setup guide.

---

## Task Split

**Full task breakdown:** [TASK_SPLIT.md](TASK_SPLIT.md)

**Quick summary:**

| Developer | Modules | Est. Time |
|-----------|---------|-----------|
| Dev 1 (You) | Model loader, R-peak detection, Flask API | 7 hours |
| Dev 2 (Teammate) | Region mapper, LLM interpreter, integration | 8 hours |

**Parallel development:** Both developers can work independently until integration phase.

---

## Troubleshooting

### Issue: TensorFlow version incompatibility

**Symptoms:** `pip install tensorflow==2.2` fails

**Solution:**
```bash
# Try newer TensorFlow version
pip install tensorflow==2.8

# OR use conda
conda install tensorflow==2.2
```

### Issue: Model file not found

**Symptoms:** `FileNotFoundError: model/model.hdf5`

**Solution:**
```bash
# Verify file exists
ls -lh model/model.hdf5

# If missing, download from Zenodo
wget https://zenodo.org/record/4916206/files/model.hdf5 -O model/model.hdf5
```

### Issue: CORS errors from Unity

**Symptoms:** Unity request blocked by CORS policy

**Solution:**
```python
# In ecg_api.py, ensure CORS is enabled
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})
```

### Issue: Claude API rate limit

**Symptoms:** `anthropic.RateLimitError`

**Solution:**
- Claude API has rate limits for free tier
- Cache LLM responses for identical conditions
- Consider fallback: return condition name without interpretation

### Issue: Flask server not accessible from Quest 2

**Symptoms:** Unity cannot connect to `http://localhost:5000`

**Solution:**
```bash
# Find your local IP address
ipconfig  # Windows
ifconfig  # macOS/Linux

# Change Flask host to accept external connections
app.run(host='0.0.0.0', port=5000)  # In ecg_api.py

# Update Unity to use your IP instead of localhost
# Example: http://192.168.1.100:5000
```

### Issue: Slow inference time

**Symptoms:** API response takes >2 seconds

**Solution:**
- First request is slow (model loading) - this is normal
- Subsequent requests should be <500ms
- If still slow, disable LLM interpreter for testing
- Consider running on GPU if available

---

## Additional Resources

- **ECG Model Paper:** https://arxiv.org/abs/1909.09960
- **Pan-Tompkins Algorithm:** https://en.wikipedia.org/wiki/Pan%E2%80%93Tompkins_algorithm
- **Claude API Docs:** https://docs.anthropic.com/claude/reference/
- **Flask Documentation:** https://flask.palletsprojects.com/
- **Unity Integration Guide:** `dummy_data/README.md`

---

## Environment Variables Reference

Create `.env` file in `Backend/` directory:

```bash
# Required for LLM interpretation
ANTHROPIC_API_KEY=sk-ant-...

# Optional Flask configuration
FLASK_ENV=development
FLASK_DEBUG=True
FLASK_PORT=5000

# Optional model configuration
MODEL_PATH=model/model.hdf5
SAMPLING_RATE=400
```

Load in Python:

```python
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('ANTHROPIC_API_KEY')
```

---

## License

MIT License - See root `LICENSE` file

---

## Contact

**Project:** HoloHuman XR
**Hackathon:** Immerse the Bay 2025
**GitHub:** https://github.com/tyang4-ai/Immerse-the-Bay-Hackathon
**Team:** 4 developers (2 Unity, 2 Backend)
