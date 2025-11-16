# API Reference - HoloHuman XR Backend

Complete API documentation for the Flask backend ECG analysis service.

**Base URL:** `http://localhost:5000`
**Version:** 1.0.0
**Last Updated:** 2025-11-15 03:30 AM

---

## Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Endpoints](#endpoints)
   - [POST /api/ecg/predict](#post-apiecgpredict)
   - [GET /api/health](#get-apihealth)
   - [GET /api/conditions](#get-apiconditions)
4. [Data Models](#data-models)
5. [Error Codes](#error-codes)
6. [Rate Limiting](#rate-limiting)
7. [Examples](#examples)

---

## Overview

The HoloHuman XR backend provides a REST API for analyzing 12-lead ECG signals using:
- **TensorFlow model** for cardiac condition prediction
- **Pan-Tompkins algorithm** for heart rate analysis
- **Rule-based mapping** for anatomical region health
- **Claude LLM** for medical interpretation

### Key Features

- 6 cardiac condition detection
- Real-time heart rate and BPM calculation
- Per-region severity mapping (10 anatomical regions)
- Natural language medical explanations
- Visualization suggestions for VR

### Technology Stack

- Flask + Flask-CORS
- TensorFlow 2.2+
- SciPy (signal processing)
- Anthropic Claude API

---

## Authentication

**Current version:** No authentication required (development)

**Production recommendation:** Add API key authentication:

```http
Authorization: Bearer YOUR_API_KEY
```

---

## Endpoints

### POST /api/ecg/predict

**Description:** Analyzes a 12-lead ECG signal and returns comprehensive cardiac analysis including condition predictions, heart rate, anatomical region health, and LLM-generated medical interpretation.

**URL:** `/api/ecg/predict`

**Method:** `POST`

**Content-Type:** `application/json`

#### Request Body

```json
{
  "ecg_signal": [[float]],  // Required: 2D array (12 leads × 4096 samples)
  "patient_id": "string",    // Optional: Patient identifier
  "timestamp": number        // Optional: Unix timestamp
}
```

**Field Specifications:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `ecg_signal` | `float[][]` | Yes | 12-lead ECG data, shape (12, 4096) |
| `patient_id` | `string` | No | Patient identifier for logging |
| `timestamp` | `number` | No | Unix timestamp of ECG capture |

**ECG Signal Format:**
- **Shape:** (12, 4096) - 12 leads, 4096 samples each
- **Sampling Rate:** 400 Hz (10.24 seconds of data)
- **Value Range:** -5.0 to +5.0 mV (typical)
- **Lead Order:** I, II, III, aVR, aVL, aVF, V1, V2, V3, V4, V5, V6

#### Response (Success - 200 OK)

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
    "rr_intervals_ms": [1148.0, 1152.5, 1149.8, 1150.2, 1149.0, 1151.3, 1148.7, 1150.9],
    "beat_timestamps": [0.5, 1.65, 2.8, 3.95, 5.1, 6.25, 7.4, 8.55, 9.7],
    "r_peak_count": 9
  },
  "region_health": {
    "sa_node": {
      "severity": 0.5,
      "color": [1.0, 0.65, 0.0],
      "activation_delay_ms": 0,
      "affected_by": ["sinus_bradycardia"]
    },
    "ra": {
      "severity": 0.156,
      "color": [0.624, 1.0, 0.0],
      "activation_delay_ms": 25,
      "affected_by": ["sinus_bradycardia"]
    },
    "la": {
      "severity": 0.156,
      "color": [0.624, 1.0, 0.0],
      "activation_delay_ms": 30,
      "affected_by": ["sinus_bradycardia"]
    },
    "av_node": {
      "severity": 0.025,
      "color": [0.1, 1.0, 0.0],
      "activation_delay_ms": 50,
      "affected_by": ["1st_degree_AV_block"]
    },
    "bundle_his": {
      "severity": 0.0125,
      "color": [0.05, 1.0, 0.0],
      "activation_delay_ms": 150,
      "affected_by": ["1st_degree_AV_block"]
    },
    "rbbb": {
      "severity": 0.12,
      "color": [0.48, 1.0, 0.0],
      "activation_delay_ms": 160,
      "affected_by": ["RBBB"]
    },
    "lbbb": {
      "severity": 0.03,
      "color": [0.12, 1.0, 0.0],
      "activation_delay_ms": 160,
      "affected_by": ["LBBB"]
    },
    "purkinje": {
      "severity": 0.048,
      "color": [0.192, 1.0, 0.0],
      "activation_delay_ms": 180,
      "affected_by": ["RBBB"]
    },
    "rv": {
      "severity": 0.084,
      "color": [0.336, 1.0, 0.0],
      "activation_delay_ms": 200,
      "affected_by": ["RBBB"]
    },
    "lv": {
      "severity": 0.021,
      "color": [0.084, 1.0, 0.0],
      "activation_delay_ms": 200,
      "affected_by": ["LBBB"]
    }
  },
  "activation_sequence": [
    ["sa_node", 0],
    ["ra", 25],
    ["la", 30],
    ["av_node", 50],
    ["bundle_his", 150],
    ["rbbb", 160],
    ["lbbb", 160],
    ["purkinje", 180],
    ["rv", 200],
    ["lv", 200]
  ],
  "llm_interpretation": {
    "plain_english_summary": "Sinus bradycardia detected - your heart is beating slower than normal at 52 beats per minute.",
    "severity_assessment": {
      "overall": "low",
      "regions": {
        "most_affected_region": "sa_node",
        "severity_explanation": "The SA node (heart's natural pacemaker) is firing at a slower rate than typical, resulting in a heart rate below 60 BPM."
      }
    },
    "patient_explanation": "Sinus bradycardia means your heart is beating slower than the typical range (60-100 BPM). At 52 BPM, your heart rate is mildly reduced. This can be completely normal, especially if you're an athlete or physically fit. However, if you're experiencing symptoms like dizziness, fatigue, or shortness of breath, you should consult a doctor. Many people with sinus bradycardia have no symptoms and require no treatment.",
    "clinical_notes": "ECG findings: Sinus bradycardia at 52.3 BPM. Regular rhythm with normal P-wave morphology. PR interval within normal limits. QRS complexes normal duration. No evidence of bundle branch blocks or AV blocks. Recommendation: Clinical correlation. If asymptomatic and physically active, likely benign. Consider evaluation if symptomatic or new-onset.",
    "visualization_suggestions": {
      "highlight_regions": ["sa_node"],
      "recommended_view": "electrical_pathway",
      "animation_speed": "slow",
      "color_emphasis": "The SA node should be colored orange/yellow to indicate it's the primary affected region. The slow heart rate should be reflected in slower heartbeat animations. All other regions should be green, showing normal conduction despite the slow rate."
    }
  },
  "top_condition": "sinus_bradycardia",
  "confidence": 0.78,
  "processing_time_ms": 187.3,
  "model_version": "1.0.0",
  "timestamp": "2025-11-15T03:30:00Z"
}
```

#### Response (Error - 400 Bad Request)

```json
{
  "error": "Invalid ECG signal format",
  "details": "Expected array of shape (12, 4096), got (10, 4096)",
  "code": "INVALID_INPUT"
}
```

#### Response (Error - 500 Internal Server Error)

```json
{
  "error": "Model inference failed",
  "details": "TensorFlow runtime error: ...",
  "code": "MODEL_ERROR"
}
```

---

### GET /api/health

**Description:** Health check endpoint to verify the server is running and the model is loaded.

**URL:** `/api/health`

**Method:** `GET`

#### Response (200 OK)

```json
{
  "status": "healthy",
  "model_loaded": true,
  "uptime_seconds": 3600,
  "version": "1.0.0",
  "timestamp": "2025-11-15T03:30:00Z"
}
```

#### Response (503 Service Unavailable)

```json
{
  "status": "unhealthy",
  "model_loaded": false,
  "error": "Model failed to load",
  "details": "FileNotFoundError: model/model.hdf5"
}
```

---

### GET /api/conditions

**Description:** Returns a list of all detectable cardiac conditions with metadata.

**URL:** `/api/conditions`

**Method:** `GET`

#### Response (200 OK)

```json
{
  "conditions": [
    {
      "id": "1st_degree_AV_block",
      "name": "1st Degree AV Block",
      "description": "Prolonged PR interval (>200ms) indicating delayed conduction through the AV node",
      "severity": "low",
      "affected_regions": ["av_node", "bundle_his"]
    },
    {
      "id": "RBBB",
      "name": "Right Bundle Branch Block",
      "description": "Delayed right ventricular activation due to right bundle branch conduction block",
      "severity": "medium",
      "affected_regions": ["rbbb", "rv", "purkinje"]
    },
    {
      "id": "LBBB",
      "name": "Left Bundle Branch Block",
      "description": "Delayed left ventricular activation due to left bundle branch conduction block",
      "severity": "medium",
      "affected_regions": ["lbbb", "lv", "purkinje"]
    },
    {
      "id": "sinus_bradycardia",
      "name": "Sinus Bradycardia",
      "description": "Slow heart rate (<60 BPM) with normal sinus rhythm",
      "severity": "low",
      "affected_regions": ["sa_node", "ra", "la"]
    },
    {
      "id": "atrial_fibrillation",
      "name": "Atrial Fibrillation",
      "description": "Irregular and chaotic atrial electrical activity resulting in irregular ventricular response",
      "severity": "high",
      "affected_regions": ["ra", "la", "av_node"]
    },
    {
      "id": "sinus_tachycardia",
      "name": "Sinus Tachycardia",
      "description": "Fast heart rate (>100 BPM) with normal sinus rhythm",
      "severity": "low",
      "affected_regions": ["sa_node", "ra", "la"]
    }
  ],
  "total": 6,
  "version": "1.0.0"
}
```

---

## Data Models

### ECGPredictions

Dictionary mapping condition IDs to probability scores (0.0-1.0).

```typescript
interface ECGPredictions {
  "1st_degree_AV_block": number;    // 0.0 - 1.0
  "RBBB": number;                    // 0.0 - 1.0
  "LBBB": number;                    // 0.0 - 1.0
  "sinus_bradycardia": number;       // 0.0 - 1.0
  "atrial_fibrillation": number;     // 0.0 - 1.0
  "sinus_tachycardia": number;       // 0.0 - 1.0
}
```

### HeartRate

Heart rate analysis data from R-peak detection.

```typescript
interface HeartRate {
  bpm: number;                       // Beats per minute
  rr_intervals_ms: number[];         // R-R intervals in milliseconds
  beat_timestamps: number[];         // Beat times in seconds from start
  r_peak_count: number;              // Total number of detected heartbeats
}
```

### RegionHealth

Health data for a single anatomical region.

```typescript
interface RegionHealth {
  severity: number;                  // 0.0 (healthy) to 1.0 (critical)
  color: [number, number, number];   // RGB color (0.0-1.0 range)
  activation_delay_ms: number;       // Electrical activation delay (ms)
  affected_by: string[];             // Array of condition IDs affecting this region
}
```

**10 Anatomical Regions:**
1. `sa_node` - Sinoatrial node (pacemaker)
2. `ra` - Right atrium
3. `la` - Left atrium
4. `av_node` - Atrioventricular node
5. `bundle_his` - Bundle of His
6. `rbbb` - Right bundle branch
7. `lbbb` - Left bundle branch
8. `purkinje` - Purkinje fibers
9. `rv` - Right ventricle
10. `lv` - Left ventricle

### ActivationSequence

Ordered array of [region_name, delay_ms] pairs showing electrical activation timing.

```typescript
type ActivationSequence = [string, number][];

// Example:
[
  ["sa_node", 0],        // Fires first
  ["ra", 25],            // 25ms after SA node
  ["la", 30],            // 30ms after SA node
  ["av_node", 50],       // 50ms after SA node
  // ... continues
]
```

### LLMInterpretation

Natural language medical interpretation from Claude API.

```typescript
interface LLMInterpretation {
  plain_english_summary: string;     // 2-3 sentence overview
  severity_assessment: {
    overall: "low" | "moderate" | "high";
    regions: {
      most_affected_region: string;
      severity_explanation: string;
    };
  };
  patient_explanation: string;       // Patient-friendly detailed explanation
  clinical_notes: string;            // Technical medical notes for clinicians
  visualization_suggestions: {
    highlight_regions: string[];     // Regions to emphasize in VR
    recommended_view: string;        // Suggested camera angle
    animation_speed: "slow" | "normal" | "fast";
    color_emphasis: string;          // Textual color recommendations
  };
}
```

---

## Error Codes

| Code | HTTP Status | Description | Solution |
|------|-------------|-------------|----------|
| `INVALID_INPUT` | 400 | ECG signal format incorrect | Verify shape is (12, 4096) |
| `MISSING_FIELD` | 400 | Required field missing | Include `ecg_signal` in request body |
| `INVALID_VALUE` | 400 | ECG contains NaN/Inf | Check data preprocessing |
| `MODEL_ERROR` | 500 | TensorFlow inference failed | Check model file and TF version |
| `LLM_ERROR` | 500 | Claude API call failed | Verify ANTHROPIC_API_KEY env variable |
| `RATE_LIMIT` | 429 | Too many requests | Wait before retrying |
| `INTERNAL_ERROR` | 500 | Unexpected server error | Check Flask logs |

---

## Rate Limiting

**Current version:** No rate limiting (development)

**Production recommendation:**
- 60 requests per minute per IP
- 1000 requests per hour per API key
- LLM calls limited by Claude API quotas

---

## Examples

### Example 1: Normal Sinus Rhythm

**Request:**
```bash
curl -X POST http://localhost:5000/api/ecg/predict \
  -H "Content-Type: application/json" \
  -d @Backend/dummy_data/sample_normal.json
```

**Response:**
- All regions green (severity ~0.0)
- BPM: 72.5
- Top condition: "normal"
- Confidence: 0.95

### Example 2: Atrial Fibrillation

**Request:**
```bash
curl -X POST http://localhost:5000/api/ecg/predict \
  -H "Content-Type: application/json" \
  -d @Backend/dummy_data/sample_af.json
```

**Response:**
- Both atria red (severity 0.8)
- BPM: 118.7 (irregular)
- Top condition: "atrial_fibrillation"
- Confidence: 0.92

### Example 3: Health Check

**Request:**
```bash
curl http://localhost:5000/api/health
```

**Response:**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "uptime_seconds": 3600,
  "version": "1.0.0",
  "timestamp": "2025-11-15T03:30:00Z"
}
```

### Example 4: Unity C# Integration

```csharp
using UnityEngine;
using UnityEngine.Networking;
using System.Collections;
using System.Text;

public class ECGAPIClient : MonoBehaviour
{
    private string apiUrl = "http://localhost:5000/api/ecg/predict";

    public IEnumerator AnalyzeECG(float[][] ecgSignal)
    {
        // Create JSON request
        var request = new {
            ecg_signal = ecgSignal,
            patient_id = "test_patient_001"
        };
        string jsonBody = JsonUtility.ToJson(request);

        // Send POST request
        UnityWebRequest www = new UnityWebRequest(apiUrl, "POST");
        www.uploadHandler = new UploadHandlerRaw(Encoding.UTF8.GetBytes(jsonBody));
        www.downloadHandler = new DownloadHandlerBuffer();
        www.SetRequestHeader("Content-Type", "application/json");

        yield return www.SendWebRequest();

        if (www.result == UnityWebRequest.Result.Success)
        {
            string response = www.downloadHandler.text;
            ECGResponse data = JsonUtility.FromJson<ECGResponse>(response);

            Debug.Log($"Top Condition: {data.top_condition}");
            Debug.Log($"Heart Rate: {data.heart_rate.bpm} BPM");
            Debug.Log($"Confidence: {data.confidence}");
        }
        else
        {
            Debug.LogError($"Error: {www.error}");
        }
    }
}
```

---

## Versioning

**Current Version:** 1.0.0

**Version Format:** MAJOR.MINOR.PATCH

- **MAJOR:** Breaking API changes
- **MINOR:** New features (backwards compatible)
- **PATCH:** Bug fixes

---

## Support

**Documentation:** See `Backend/README.md` for setup instructions

**Troubleshooting:** See `Backend/README.md` troubleshooting section

**Unity Integration:** See `Backend/dummy_data/README.md`

**Task Division:** See `Backend/TASK_SPLIT.md` for backend development workflow

---

## License

MIT License - See root `LICENSE` file

**Project:** HoloHuman XR
**Hackathon:** Immerse the Bay 2025
**GitHub:** https://github.com/tyang4-ai/Immerse-the-Bay-Hackathon
