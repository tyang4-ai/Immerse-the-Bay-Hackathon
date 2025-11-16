# HoloHuman XR Backend - API Integration Guide

**Project:** Immerse the Bay 2025 Hackathon
**Last Updated:** 2025-11-15
**Backend Version:** 1.0.0 (Phases 1-3 Complete)

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Architecture Overview](#architecture-overview)
3. [API Endpoints Reference](#api-endpoints-reference)
4. [Unity C# Integration](#unity-c-integration)
5. [Error Handling](#error-handling)
6. [Performance Optimization](#performance-optimization)
7. [Network Configuration](#network-configuration)
8. [Troubleshooting](#troubleshooting)

---

## Quick Start

### Backend Setup (5 minutes)

```bash
# 1. Navigate to Backend directory
cd Backend

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Set Anthropic API key
# Windows:
set ANTHROPIC_API_KEY=your_api_key_here
# macOS/Linux:
export ANTHROPIC_API_KEY=your_api_key_here

# 6. Start server
python ecg_api.py
```

**Server Address:** `http://localhost:5000`
**Health Check:** `http://localhost:5000/health`

### Unity Setup (2 minutes)

1. Install **Newtonsoft.Json** package via Unity Package Manager
2. Copy C# examples from [Unity C# Integration](#unity-c-integration) section
3. Configure backend URL in Unity Inspector
4. Test connection with health endpoint

---

## Architecture Overview

### Backend Technology Stack

```
┌─────────────────────────────────────────────────────────┐
│                   Flask REST API                        │
│                  (Python 3.10+)                         │
├─────────────────────────────────────────────────────────┤
│  • TensorFlow 2.20 - ML inference (ECG classification)  │
│  • Anthropic Claude - LLM clinical interpretation       │
│  • NumPy/SciPy - Signal processing                      │
│  • functools.lru_cache - Response caching (128 entries) │
└─────────────────────────────────────────────────────────┘
```

### ECG Processing Pipeline

```
Unity (VR Client)
   │
   ├─ POST /api/ecg/analyze ──┐
   │                          │
   ▼                          ▼
┌────────────────────────────────────────┐
│  1. Input Validation                   │
│     - Shape check: (4096, 12)          │
│     - NaN/Inf detection                │
│     - Amplitude range: ±5mV            │
└────────────────────────────────────────┘
   │
   ▼
┌────────────────────────────────────────┐
│  2. Multi-Lead Heart Rate Analysis     │
│     Priority: II → V1 → V5 → I → aVF   │
│     - Pan-Tompkins R-peak detection    │
│     - Signal quality assessment        │
│     - Automatic fallback if corrupted  │
└────────────────────────────────────────┘
   │
   ▼
┌────────────────────────────────────────┐
│  3. TensorFlow ML Classification       │
│     - 6 cardiac conditions detected    │
│     - Confidence scores (0.0-1.0)      │
│     - Simulation fallback mode         │
└────────────────────────────────────────┘
   │
   ▼
┌────────────────────────────────────────┐
│  4. Heart Region Mapping               │
│     - 10 anatomical regions            │
│     - Severity scores (0.0-1.0)        │
│     - Conduction path affected         │
└────────────────────────────────────────┘
   │
   ▼
┌────────────────────────────────────────┐
│  5. Claude LLM Interpretation          │
│     - 3 output modes (clinical/patient/storytelling)
│     - Cached responses (~50ms hit)     │
│     - Fallback narratives if offline   │
└────────────────────────────────────────┘
   │
   ▼
JSON Response → Unity VR
```

### 7 Production-Ready Endpoints

| Endpoint | Purpose | Avg Response Time | Use Case |
|----------|---------|-------------------|----------|
| **POST /api/ecg/analyze** | Full ECG analysis | ~260ms (cold), ~50ms (cached) | Medical interpretation |
| **GET /health** | Server health check | <10ms | Startup validation |
| **GET /api/cache/stats** | Cache performance | <10ms | Performance monitoring |
| **POST /api/cache/clear** | Clear cache | <10ms | Admin/debugging |
| **POST /api/ecg/beats** | Fast R-peak detection | ~50ms | VR timeline scrubbing |
| **POST /api/ecg/beat/<index>** | Single beat analysis | ~52ms | Beat detail panel |
| **POST /api/ecg/segment** | Time window analysis | ~36ms | VR playback control |

---

## API Endpoints Reference

### 1. POST /api/ecg/analyze - Full ECG Analysis

**Primary endpoint for medical interpretation with 3 output modes.**

#### Request

```http
POST http://localhost:5000/api/ecg/analyze
Content-Type: application/json

{
  "ecg_signal": [[...], [...], ...],  // 4096 samples × 12 leads (float array)
  "output_mode": "clinical_expert",   // "clinical_expert" | "patient_education" | "storytelling"
  "region_focus": "rbbb"              // Optional: "sa", "av", "his", "rbbb", "lbbb", etc.
}
```

**ECG Signal Format:**
- **Shape:** `(4096, 12)` - 4096 time samples × 12 ECG leads
- **Sampling Rate:** 400 Hz (10.24 seconds of data)
- **Leads Order:** `[I, II, III, aVR, aVL, aVF, V1, V2, V3, V4, V5, V6]`
- **Amplitude:** -5.0 to +5.0 millivolts (typical range)
- **Data Type:** Float32 array

#### Response (output_mode: "clinical_expert")

```json
{
  "diagnosis": {
    "top_condition": "sinus_bradycardia",
    "confidence": 0.92,
    "all_conditions": {
      "1st_degree_AV_block": 0.05,
      "RBBB": 0.12,
      "LBBB": 0.03,
      "sinus_bradycardia": 0.92,
      "atrial_fibrillation": 0.01,
      "sinus_tachycardia": 0.02
    }
  },
  "heart_rate": {
    "bpm": 52.3,
    "rr_intervals_ms": [1147.5, 1150.0, 1145.2, ...],
    "beat_timestamps": [75.0, 1222.5, 2372.5, ...],
    "r_peak_count": 9,
    "lead_used": "II",
    "lead_quality": 0.98,
    "fallback_triggered": false
  },
  "region_health": {
    "sa_node": {"severity": 0.85, "description": "Sinus node dysfunction"},
    "av_node": {"severity": 0.15, "description": "Normal AV conduction"},
    "his_bundle": {"severity": 0.10, "description": "Normal conduction"},
    "rbbb": {"severity": 0.20, "description": "Minor right bundle delay"},
    "lbbb": {"severity": 0.05, "description": "Normal left bundle"},
    "right_atrium": {"severity": 0.10, "description": "Normal atrial function"},
    "left_atrium": {"severity": 0.10, "description": "Normal atrial function"},
    "right_ventricle": {"severity": 0.15, "description": "Mildly affected"},
    "left_ventricle": {"severity": 0.10, "description": "Normal ventricular function"},
    "purkinje": {"severity": 0.15, "description": "Minor conduction delay"}
  },
  "clinical_interpretation": "CLINICAL DECISION SUPPORT:\n\nDIFFERENTIAL DIAGNOSIS:\n1. Sinus Bradycardia (92% confidence)\n   - Heart rate 52 BPM (below 60 BPM threshold)\n   - Regular sinus rhythm with P waves preceding each QRS\n   - SA node firing rate is physiologically slowed\n\n2. Possible Contributors:\n   - Minor RBBB pattern (12% confidence)\n   - First-degree AV block cannot be ruled out (5%)\n\nWORKUP RECOMMENDATIONS:\n- Review patient medications (beta-blockers, calcium channel blockers)\n- Assess for symptoms: dizziness, syncope, fatigue\n- Consider Holter monitor if symptomatic\n- Evaluate electrolytes (K+, Mg2+, Ca2+)\n\nTREATMENT CONSIDERATIONS:\n- If asymptomatic: Observation, no immediate intervention\n- If symptomatic: Consider dose reduction of rate-limiting drugs\n- If severe: Pacemaker evaluation may be warranted\n\nCRITICAL FINDINGS: None requiring immediate intervention",
  "processing_time_ms": 267.43,
  "timestamp": "2025-11-16T01:47:17Z",
  "simulation_mode": false,
  "request_id": "REQ-A7F2B9C1"
}
```

#### Response (output_mode: "storytelling")

```json
{
  "diagnosis": { ... },
  "heart_rate": { ... },
  "region_health": { ... },
  "storytelling_narrative": {
    "location_name": "Right Bundle Branch",
    "narrative": "You descend into the right bundle branch, expecting rapid conduction. Instead, you find a blockage—the electrical highway is severed. Signals that should pass in milliseconds are delayed by 145ms. The Purkinje fibers wait impatiently, their rhythmic pulse faltering...",
    "medical_insight": "Complete RBBB shows QRS duration ≥120ms with rsR' pattern in V1-V2. The right ventricle depolarizes late, creating the characteristic wide QRS complex.",
    "waypoints": [
      {
        "region": "purkinje",
        "description": "Follow the dying signal to the Purkinje network",
        "teaser": "The final frontier: Can the signal reach the muscle fibers?"
      },
      {
        "region": "rv",
        "description": "Enter the delayed right ventricle",
        "teaser": "Witness the delayed contraction firsthand"
      }
    ],
    "atmosphere": "Dark pathway with flickering red warning lights. Electrical signals move sluggishly, like traffic in a construction zone. You hear the distant echo of heartbeats, but they're out of sync.",
    "region_focus": "rbbb"
  },
  "processing_time_ms": 312.55,
  "timestamp": "2025-11-16T02:15:33Z",
  "simulation_mode": false,
  "request_id": "REQ-C3D8E4F0"
}
```

#### Error Response

```json
{
  "error": "Invalid ECG shape: expected (4096, 12), got (2048, 12)",
  "error_id": "ERR-XR-A3F7B2",
  "timestamp": "2025-11-16T01:47:17Z"
}
```

**HTTP Status Codes:**
- `200` - Success
- `400` - Invalid input (shape mismatch, NaN/Inf, amplitude out of range)
- `500` - Internal server error

---

### 2. GET /health - Server Health Check

**Check if backend server is running and ready.**

#### Request

```http
GET http://localhost:5000/health
```

#### Response

```json
{
  "status": "healthy",
  "model_loaded": true,
  "simulation_mode": false,
  "cache_stats": {
    "hits": 42,
    "misses": 18,
    "hit_rate": 70.0
  },
  "timestamp": "2025-11-16T01:47:17Z"
}
```

**Use Case:** Call this endpoint when your Unity app starts to verify backend connectivity.

---

### 3. POST /api/ecg/beats - Fast R-Peak Detection

**Detect all heartbeats for VR timeline scrubbing (81% faster than full analysis).**

#### Request

```http
POST http://localhost:5000/api/ecg/beats
Content-Type: application/json

{
  "ecg_signal": [[...], [...], ...]  // 4096 × 12 array
}
```

#### Response

```json
{
  "r_peaks": [30, 357, 690, 1023, 1357, 1690, 2023, 2357, 2690, 3023, 3357, 3690, 4020],
  "beat_count": 13,
  "avg_rr_interval_ms": 831.5,
  "rhythm": "regular",
  "lead_used": "II",
  "lead_quality": 1.0,
  "processing_time_ms": 54.76,
  "timestamp": "2025-11-16T01:47:17Z"
}
```

**Response Fields:**
- `r_peaks` - Array of R-peak sample indices (0-4095)
- `beat_count` - Total number of beats detected
- `avg_rr_interval_ms` - Average time between beats in milliseconds
- `rhythm` - "regular" (CV < 0.15) or "irregular" (CV ≥ 0.15)
- `lead_used` - ECG lead used for detection (II, V1, V5, I, or aVF)
- `lead_quality` - Quality score 0.0-1.0 (>0.8 = excellent)

**Use Case:** Display beat markers on VR timeline for scrubbing/navigation.

---

### 4. POST /api/ecg/beat/<index> - Single Beat Analysis

**Analyze a specific heartbeat with P-QRS-T waveform detection (78% faster than full analysis).**

#### Request

```http
POST http://localhost:5000/api/ecg/beat/2
Content-Type: application/json

{
  "ecg_signal": [[...], [...], ...]  // 4096 × 12 array
}
```

**Path Parameter:**
- `<index>` - Beat index (0-based, use beat_count from /api/ecg/beats to validate)

#### Response

```json
{
  "beat_index": 2,
  "r_peak_sample": 690,
  "waveform": {
    "p_wave": {
      "onset": 630,
      "peak": 640,
      "offset": 660
    },
    "qrs_complex": {
      "onset": 670,
      "peak": 690,
      "offset": 720
    },
    "t_wave": {
      "onset": 740,
      "peak": 769,
      "offset": 769
    }
  },
  "intervals": {
    "pr_interval_ms": 100.0,
    "qrs_duration_ms": 125.0,
    "qt_interval_ms": 247.5
  },
  "raw_samples": [0.05, 0.07, 0.12, ..., -0.03],  // 160 samples (±200ms window)
  "lead_used": "II",
  "annotations": "Wide QRS complex (possible bundle branch block)",
  "processing_time_ms": 51.50,
  "timestamp": "2025-11-16T01:47:18Z"
}
```

**Waveform Fields:**
- `p_wave` - Atrial depolarization (typically -60ms to -30ms before R-peak)
- `qrs_complex` - Ventricular depolarization (typically -20ms to +30ms around R-peak)
- `t_wave` - Ventricular repolarization (typically +20ms to +120ms after QRS)
- All positions are sample indices (0-4095)

**ECG Intervals:**
- `pr_interval_ms` - P-wave onset to QRS onset (normal: 120-200ms)
- `qrs_duration_ms` - QRS complex width (normal: <120ms, wide: ≥120ms)
- `qt_interval_ms` - QRS onset to T-wave offset (normal: <440ms)

**Annotations:**
- `"Normal sinus beat"` - No abnormalities detected
- `"Wide QRS complex (possible bundle branch block)"` - QRS > 120ms
- `"Prolonged PR interval (possible AV block)"` - PR > 200ms

**Use Case:** Display beat detail panel when user clicks on a specific beat in VR.

---

### 5. POST /api/ecg/segment - Time Window Analysis

**Analyze a specific time range for VR playback control (87% faster than full analysis).**

#### Request

```http
POST http://localhost:5000/api/ecg/segment
Content-Type: application/json

{
  "ecg_signal": [[...], [...], ...],  // 4096 × 12 array
  "start_ms": 0.0,
  "end_ms": 2000.0
}
```

**Time Parameters:**
- `start_ms` - Start time in milliseconds (0.0 to ECG duration)
- `end_ms` - End time in milliseconds (must be > start_ms)
- ECG duration: `(4096 / 400Hz) * 1000 = 10240ms`

#### Response

```json
{
  "segment": {
    "start_ms": 0.0,
    "end_ms": 2000.0,
    "duration_ms": 2000.0,
    "beats_in_segment": 3,
    "rhythm_analysis": "Regular sinus rhythm",
    "events": [
      {"type": "r_peak", "time_ms": 75.0},
      {"type": "r_peak", "time_ms": 892.5},
      {"type": "r_peak", "time_ms": 1725.0}
    ],
    "lead_used": "II"
  },
  "processing_time_ms": 39.88,
  "timestamp": "2025-11-16T01:47:18Z"
}
```

**Rhythm Analysis:**
- `"Regular sinus rhythm"` - CV < 0.10
- `"Mildly irregular rhythm"` - 0.10 ≤ CV < 0.20
- `"Irregular rhythm (possible arrhythmia)"` - CV ≥ 0.20
- CV = Coefficient of Variation (RR interval variability)

**Use Case:** Display beats within current VR playback window as user scrubs timeline.

---

### 6. GET /api/cache/stats - Cache Performance

**Monitor LLM response cache performance.**

#### Request

```http
GET http://localhost:5000/api/cache/stats
```

#### Response

```json
{
  "hits": 42,
  "misses": 18,
  "hit_rate": 70.0,
  "cache_size": 128
}
```

**Use Case:** Debug performance issues or monitor cache effectiveness.

---

### 7. POST /api/cache/clear - Clear Cache

**Clear the LLM response cache (admin/debugging).**

#### Request

```http
POST http://localhost:5000/api/cache/clear
```

#### Response

```json
{
  "message": "Cache cleared successfully",
  "previous_stats": {
    "hits": 42,
    "misses": 18
  }
}
```

**Use Case:** Force fresh LLM responses during development/testing.

---

## Unity C# Integration

### Complete ECG API Client

Create `ECGAPIClient.cs` in your Unity project:

```csharp
using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Networking;
using Newtonsoft.Json;

public class ECGAPIClient : MonoBehaviour
{
    [Header("Backend Configuration")]
    [Tooltip("Backend server URL (e.g., http://192.168.1.100:5000 for Quest 2)")]
    public string backendURL = "http://localhost:5000";

    [Header("Request Settings")]
    public int timeoutSeconds = 30;
    public bool logRequests = true;

    // Singleton instance
    public static ECGAPIClient Instance { get; private set; }

    void Awake()
    {
        if (Instance == null)
        {
            Instance = this;
            DontDestroyOnLoad(gameObject);
        }
        else
        {
            Destroy(gameObject);
        }
    }

    void Start()
    {
        StartCoroutine(CheckServerHealth());
    }

    /// <summary>
    /// Check if backend server is healthy
    /// </summary>
    public IEnumerator CheckServerHealth()
    {
        string url = $"{backendURL}/health";

        using (UnityWebRequest request = UnityWebRequest.Get(url))
        {
            request.timeout = 5;  // 5 second timeout for health check

            yield return request.SendWebRequest();

            if (request.result == UnityWebRequest.Result.Success)
            {
                var response = JsonConvert.DeserializeObject<HealthResponse>(request.downloadHandler.text);
                Debug.Log($"[ECG API] Backend is healthy! Model loaded: {response.model_loaded}");

                if (response.simulation_mode)
                {
                    Debug.LogWarning("[ECG API] Backend running in SIMULATION mode (no ML model)");
                }
            }
            else
            {
                Debug.LogError($"[ECG API] Backend not reachable: {request.error}");
                Debug.LogError($"[ECG API] Make sure Flask server is running at {backendURL}");
            }
        }
    }

    /// <summary>
    /// Analyze full ECG with medical interpretation
    /// </summary>
    public IEnumerator AnalyzeECG(
        float[,] ecgSignal,
        string outputMode = "clinical_expert",
        string regionFocus = null,
        Action<ECGAnalysisResponse> onSuccess = null,
        Action<string> onError = null)
    {
        string url = $"{backendURL}/api/ecg/analyze";

        // Create request payload
        var payload = new ECGAnalyzeRequest
        {
            ecg_signal = ConvertTo2DList(ecgSignal),
            output_mode = outputMode,
            region_focus = regionFocus
        };

        string jsonPayload = JsonConvert.SerializeObject(payload);

        if (logRequests)
        {
            Debug.Log($"[ECG API] POST /api/ecg/analyze (mode: {outputMode})");
        }

        using (UnityWebRequest request = new UnityWebRequest(url, "POST"))
        {
            byte[] bodyRaw = System.Text.Encoding.UTF8.GetBytes(jsonPayload);
            request.uploadHandler = new UploadHandlerRaw(bodyRaw);
            request.downloadHandler = new DownloadHandlerBuffer();
            request.SetRequestHeader("Content-Type", "application/json");
            request.timeout = timeoutSeconds;

            yield return request.SendWebRequest();

            if (request.result == UnityWebRequest.Result.Success)
            {
                try
                {
                    var response = JsonConvert.DeserializeObject<ECGAnalysisResponse>(request.downloadHandler.text);

                    if (logRequests)
                    {
                        Debug.Log($"[ECG API] Analysis complete: {response.diagnosis.top_condition} ({response.diagnosis.confidence:P0})");
                        Debug.Log($"[ECG API] Heart rate: {response.heart_rate.bpm:F1} BPM");
                        Debug.Log($"[ECG API] Processing time: {response.processing_time_ms:F1}ms");
                    }

                    onSuccess?.Invoke(response);
                }
                catch (Exception e)
                {
                    Debug.LogError($"[ECG API] Failed to parse response: {e.Message}");
                    onError?.Invoke($"JSON parsing error: {e.Message}");
                }
            }
            else
            {
                HandleError(request, onError);
            }
        }
    }

    /// <summary>
    /// Get all heartbeat positions (fast, for timeline scrubbing)
    /// </summary>
    public IEnumerator GetBeats(
        float[,] ecgSignal,
        Action<BeatsResponse> onSuccess = null,
        Action<string> onError = null)
    {
        string url = $"{backendURL}/api/ecg/beats";

        var payload = new { ecg_signal = ConvertTo2DList(ecgSignal) };
        string jsonPayload = JsonConvert.SerializeObject(payload);

        if (logRequests)
        {
            Debug.Log($"[ECG API] POST /api/ecg/beats");
        }

        using (UnityWebRequest request = new UnityWebRequest(url, "POST"))
        {
            byte[] bodyRaw = System.Text.Encoding.UTF8.GetBytes(jsonPayload);
            request.uploadHandler = new UploadHandlerRaw(bodyRaw);
            request.downloadHandler = new DownloadHandlerBuffer();
            request.SetRequestHeader("Content-Type", "application/json");
            request.timeout = timeoutSeconds;

            yield return request.SendWebRequest();

            if (request.result == UnityWebRequest.Result.Success)
            {
                try
                {
                    var response = JsonConvert.DeserializeObject<BeatsResponse>(request.downloadHandler.text);

                    if (logRequests)
                    {
                        Debug.Log($"[ECG API] Detected {response.beat_count} beats ({response.rhythm})");
                        Debug.Log($"[ECG API] Lead used: {response.lead_used} (quality: {response.lead_quality:F2})");
                    }

                    onSuccess?.Invoke(response);
                }
                catch (Exception e)
                {
                    Debug.LogError($"[ECG API] Failed to parse response: {e.Message}");
                    onError?.Invoke($"JSON parsing error: {e.Message}");
                }
            }
            else
            {
                HandleError(request, onError);
            }
        }
    }

    /// <summary>
    /// Get single beat detail with P-QRS-T waveform
    /// </summary>
    public IEnumerator GetBeatDetail(
        float[,] ecgSignal,
        int beatIndex,
        Action<BeatDetailResponse> onSuccess = null,
        Action<string> onError = null)
    {
        string url = $"{backendURL}/api/ecg/beat/{beatIndex}";

        var payload = new { ecg_signal = ConvertTo2DList(ecgSignal) };
        string jsonPayload = JsonConvert.SerializeObject(payload);

        if (logRequests)
        {
            Debug.Log($"[ECG API] POST /api/ecg/beat/{beatIndex}");
        }

        using (UnityWebRequest request = new UnityWebRequest(url, "POST"))
        {
            byte[] bodyRaw = System.Text.Encoding.UTF8.GetBytes(jsonPayload);
            request.uploadHandler = new UploadHandlerRaw(bodyRaw);
            request.downloadHandler = new DownloadHandlerBuffer();
            request.SetRequestHeader("Content-Type", "application/json");
            request.timeout = timeoutSeconds;

            yield return request.SendWebRequest();

            if (request.result == UnityWebRequest.Result.Success)
            {
                try
                {
                    var response = JsonConvert.DeserializeObject<BeatDetailResponse>(request.downloadHandler.text);

                    if (logRequests)
                    {
                        Debug.Log($"[ECG API] Beat {beatIndex} detail: PR={response.intervals.pr_interval_ms}ms, QRS={response.intervals.qrs_duration_ms}ms");
                    }

                    onSuccess?.Invoke(response);
                }
                catch (Exception e)
                {
                    Debug.LogError($"[ECG API] Failed to parse response: {e.Message}");
                    onError?.Invoke($"JSON parsing error: {e.Message}");
                }
            }
            else
            {
                HandleError(request, onError);
            }
        }
    }

    /// <summary>
    /// Get segment analysis for time window
    /// </summary>
    public IEnumerator GetSegment(
        float[,] ecgSignal,
        float startMs,
        float endMs,
        Action<SegmentResponse> onSuccess = null,
        Action<string> onError = null)
    {
        string url = $"{backendURL}/api/ecg/segment";

        var payload = new
        {
            ecg_signal = ConvertTo2DList(ecgSignal),
            start_ms = startMs,
            end_ms = endMs
        };
        string jsonPayload = JsonConvert.SerializeObject(payload);

        if (logRequests)
        {
            Debug.Log($"[ECG API] POST /api/ecg/segment ({startMs}-{endMs}ms)");
        }

        using (UnityWebRequest request = new UnityWebRequest(url, "POST"))
        {
            byte[] bodyRaw = System.Text.Encoding.UTF8.GetBytes(jsonPayload);
            request.uploadHandler = new UploadHandlerRaw(bodyRaw);
            request.downloadHandler = new DownloadHandlerBuffer();
            request.SetRequestHeader("Content-Type", "application/json");
            request.timeout = timeoutSeconds;

            yield return request.SendWebRequest();

            if (request.result == UnityWebRequest.Result.Success)
            {
                try
                {
                    var response = JsonConvert.DeserializeObject<SegmentResponse>(request.downloadHandler.text);

                    if (logRequests)
                    {
                        Debug.Log($"[ECG API] Segment: {response.segment.beats_in_segment} beats, {response.segment.rhythm_analysis}");
                    }

                    onSuccess?.Invoke(response);
                }
                catch (Exception e)
                {
                    Debug.LogError($"[ECG API] Failed to parse response: {e.Message}");
                    onError?.Invoke($"JSON parsing error: {e.Message}");
                }
            }
            else
            {
                HandleError(request, onError);
            }
        }
    }

    /// <summary>
    /// Handle API errors with structured error responses
    /// </summary>
    private void HandleError(UnityWebRequest request, Action<string> onError)
    {
        try
        {
            var errorResponse = JsonConvert.DeserializeObject<ErrorResponse>(request.downloadHandler.text);
            Debug.LogError($"[ECG API] Error {errorResponse.error_id}: {errorResponse.error}");
            onError?.Invoke($"[{errorResponse.error_id}] {errorResponse.error}");
        }
        catch
        {
            Debug.LogError($"[ECG API] Request failed: {request.error}");
            onError?.Invoke(request.error);
        }
    }

    /// <summary>
    /// Convert Unity float[,] array to List<List<float>> for JSON serialization
    /// </summary>
    private List<List<float>> ConvertTo2DList(float[,] array)
    {
        int samples = array.GetLength(0);
        int leads = array.GetLength(1);

        var list = new List<List<float>>(samples);
        for (int i = 0; i < samples; i++)
        {
            var row = new List<float>(leads);
            for (int j = 0; j < leads; j++)
            {
                row.Add(array[i, j]);
            }
            list.Add(row);
        }
        return list;
    }
}

// ============================================================================
// API Response Models (use Newtonsoft.Json for deserialization)
// ============================================================================

[Serializable]
public class HealthResponse
{
    public string status;
    public bool model_loaded;
    public bool simulation_mode;
    public CacheStats cache_stats;
}

[Serializable]
public class CacheStats
{
    public int hits;
    public int misses;
    public float hit_rate;
}

[Serializable]
public class ECGAnalyzeRequest
{
    public List<List<float>> ecg_signal;
    public string output_mode;
    public string region_focus;
}

[Serializable]
public class ECGAnalysisResponse
{
    public Diagnosis diagnosis;
    public HeartRate heart_rate;
    public Dictionary<string, RegionHealth> region_health;
    public string clinical_interpretation;
    public StorytellingNarrative storytelling_narrative;  // Only in storytelling mode
    public float processing_time_ms;
    public string timestamp;
    public bool simulation_mode;
    public string request_id;
}

[Serializable]
public class Diagnosis
{
    public string top_condition;
    public float confidence;
    public Dictionary<string, float> all_conditions;
}

[Serializable]
public class HeartRate
{
    public float bpm;
    public List<float> rr_intervals_ms;
    public List<float> beat_timestamps;
    public int r_peak_count;
    public string lead_used;
    public float lead_quality;
    public bool fallback_triggered;
}

[Serializable]
public class RegionHealth
{
    public float severity;
    public string description;
}

[Serializable]
public class StorytellingNarrative
{
    public string location_name;
    public string narrative;
    public string medical_insight;
    public List<Waypoint> waypoints;
    public string atmosphere;
    public string region_focus;
}

[Serializable]
public class Waypoint
{
    public string region;
    public string description;
    public string teaser;
}

[Serializable]
public class BeatsResponse
{
    public List<int> r_peaks;
    public int beat_count;
    public float avg_rr_interval_ms;
    public string rhythm;
    public string lead_used;
    public float lead_quality;
    public float processing_time_ms;
}

[Serializable]
public class BeatDetailResponse
{
    public int beat_index;
    public int r_peak_sample;
    public Waveform waveform;
    public Intervals intervals;
    public List<float> raw_samples;
    public string lead_used;
    public string annotations;
    public float processing_time_ms;
}

[Serializable]
public class Waveform
{
    public WaveComponent p_wave;
    public WaveComponent qrs_complex;
    public WaveComponent t_wave;
}

[Serializable]
public class WaveComponent
{
    public int onset;
    public int peak;
    public int offset;
}

[Serializable]
public class Intervals
{
    public float pr_interval_ms;
    public float qrs_duration_ms;
    public float qt_interval_ms;
}

[Serializable]
public class SegmentResponse
{
    public Segment segment;
    public float processing_time_ms;
}

[Serializable]
public class Segment
{
    public float start_ms;
    public float end_ms;
    public float duration_ms;
    public int beats_in_segment;
    public string rhythm_analysis;
    public List<Event> events;
    public string lead_used;
}

[Serializable]
public class Event
{
    public string type;
    public float time_ms;
}

[Serializable]
public class ErrorResponse
{
    public string error;
    public string error_id;
}
```

### Example Usage in Unity Controller

Create `ECGDemoController.cs`:

```csharp
using UnityEngine;
using System.Collections;

public class ECGDemoController : MonoBehaviour
{
    public TextAsset ecgDataFile;  // Assign JSON file from Backend/dummy_data/

    private ECGAPIClient apiClient;
    private float[,] ecgSignal;

    void Start()
    {
        apiClient = ECGAPIClient.Instance;
        LoadECGData();
        StartCoroutine(RunECGAnalysis());
    }

    void LoadECGData()
    {
        // Load ECG from JSON file
        var data = JsonUtility.FromJson<ECGDataFile>(ecgDataFile.text);

        int samples = data.ecg_signal.Count;
        int leads = data.ecg_signal[0].Count;

        ecgSignal = new float[samples, leads];
        for (int i = 0; i < samples; i++)
        {
            for (int j = 0; j < leads; j++)
            {
                ecgSignal[i, j] = data.ecg_signal[i][j];
            }
        }

        Debug.Log($"Loaded ECG: {samples} samples × {leads} leads");
    }

    IEnumerator RunECGAnalysis()
    {
        // 1. Get all beats for timeline
        yield return apiClient.GetBeats(
            ecgSignal,
            onSuccess: (response) =>
            {
                Debug.Log($"Detected {response.beat_count} beats");
                foreach (int rPeak in response.r_peaks)
                {
                    // Create beat marker on VR timeline at position rPeak
                }
            },
            onError: (error) => Debug.LogError($"Get beats failed: {error}")
        );

        // 2. Analyze beat #2 in detail
        yield return apiClient.GetBeatDetail(
            ecgSignal,
            beatIndex: 2,
            onSuccess: (response) =>
            {
                Debug.Log($"Beat 2: PR={response.intervals.pr_interval_ms}ms, QRS={response.intervals.qrs_duration_ms}ms");
                // Display beat detail panel in VR
            },
            onError: (error) => Debug.LogError($"Get beat detail failed: {error}")
        );

        // 3. Get full medical interpretation
        yield return apiClient.AnalyzeECG(
            ecgSignal,
            outputMode: "clinical_expert",
            onSuccess: (response) =>
            {
                Debug.Log($"Diagnosis: {response.diagnosis.top_condition} ({response.diagnosis.confidence:P0})");
                Debug.Log($"Heart Rate: {response.heart_rate.bpm:F1} BPM");
                Debug.Log(response.clinical_interpretation);
                // Display medical interpretation in VR UI
            },
            onError: (error) => Debug.LogError($"Analysis failed: {error}")
        );
    }
}

[System.Serializable]
public class ECGDataFile
{
    public System.Collections.Generic.List<System.Collections.Generic.List<float>> ecg_signal;
}
```

---

## Error Handling

### Structured Error Responses

All API errors return consistent JSON format:

```json
{
  "error": "Human-readable error message",
  "error_id": "ERR-XR-A3F7B2",
  "timestamp": "2025-11-16T01:47:17Z"
}
```

**Error ID Format:** `ERR-XR-XXXXXX` (6-character random hex)

### Common Errors

| HTTP Status | Error | Cause | Solution |
|-------------|-------|-------|----------|
| **400** | Invalid ECG shape | Shape != (4096, 12) | Verify ECG data has 4096 samples × 12 leads |
| **400** | Signal contains NaN/Inf | Invalid float values | Check data loading, replace NaN with 0.0 |
| **400** | Signal amplitude out of range | Values outside ±5mV | Normalize signal to millivolts |
| **400** | Signal has very low variance | Flat/dead signal | Verify signal is loaded correctly |
| **400** | Beat index out of range | Invalid beat index | Call /api/ecg/beats first to get beat_count |
| **400** | Invalid time range | end_ms < start_ms | Ensure start_ms < end_ms |
| **500** | Internal server error | Backend crash | Check Flask server logs |

### Unity Error Handling Pattern

```csharp
yield return apiClient.AnalyzeECG(
    ecgSignal,
    onSuccess: (response) =>
    {
        // Success path
        Debug.Log($"Analysis complete: {response.diagnosis.top_condition}");
    },
    onError: (error) =>
    {
        // Error path - show user-friendly message
        if (error.Contains("ERR-XR"))
        {
            // Structured backend error
            ShowErrorMessage($"ECG Analysis Failed: {error}");
        }
        else
        {
            // Network error
            ShowErrorMessage("Cannot connect to backend server. Please check your network connection.");
        }
    }
);
```

---

## Performance Optimization

### Backend Performance Metrics

| Endpoint | Cold (ms) | Cached (ms) | Speedup |
|----------|-----------|-------------|---------|
| /api/ecg/analyze (full) | 260 | 50 | 81% |
| /api/ecg/beats | 50 | - | - |
| /api/ecg/beat/<index> | 52 | - | - |
| /api/ecg/segment | 36 | - | - |

### Unity Performance Tips

1. **Reuse ECG Data**
   ```csharp
   // Bad: Send ECG with every request
   yield return apiClient.GetBeats(ecgSignal, ...);
   yield return apiClient.GetBeatDetail(ecgSignal, 0, ...);  // Redundant

   // Good: Send ECG once, cache beat positions
   BeatsResponse beats = null;
   yield return apiClient.GetBeats(
       ecgSignal,
       onSuccess: (response) => beats = response
   );

   // Use cached beat positions for timeline markers
   foreach (int rPeak in beats.r_peaks)
   {
       CreateTimelineMarker(rPeak);
   }
   ```

2. **Use Fast Endpoints for VR Interaction**
   ```csharp
   // For timeline scrubbing: Use /api/ecg/beats (50ms)
   // For beat detail panel: Use /api/ecg/beat/<index> (52ms)
   // For full medical interpretation: Use /api/ecg/analyze (260ms)
   ```

3. **Async Loading Pattern**
   ```csharp
   void Start()
   {
       // Load ECG in background
       StartCoroutine(LoadAndAnalyzeECG());

       // Show loading UI
       loadingScreen.SetActive(true);
   }

   IEnumerator LoadAndAnalyzeECG()
   {
       yield return LoadECGFromFile();
       yield return apiClient.AnalyzeECG(ecgSignal, ...);

       loadingScreen.SetActive(false);
       ShowResults();
   }
   ```

4. **Quest 2 VR Frame Budget**
   - Target: 72 FPS (13.9ms per frame)
   - Network calls run on separate thread (no frame drop)
   - All temporal endpoints <60ms (well within budget)

---

## Network Configuration

### Local Development (PC Unity Editor)

```csharp
// ECGAPIClient configuration in Unity Inspector
Backend URL: http://localhost:5000
```

**Flask Server:**
```bash
python ecg_api.py
# Server starts at http://localhost:5000
```

### Quest 2 VR Deployment (Same WiFi Network)

**Step 1: Find Your PC's Local IP Address**

Windows:
```bash
ipconfig
# Look for "IPv4 Address" under your WiFi adapter
# Example: 192.168.1.100
```

macOS/Linux:
```bash
ifconfig
# Look for "inet" under your WiFi interface
# Example: 192.168.1.100
```

**Step 2: Configure Flask to Listen on All Interfaces**

Edit `ecg_api.py` (line ~780):
```python
if __name__ == '__main__':
    initialize()
    app.run(host='0.0.0.0', port=5000, debug=False)  # Change host to 0.0.0.0
```

**Step 3: Allow Firewall Access**

Windows:
- Windows Defender Firewall → Allow an app through firewall
- Add Python → Allow on Private networks

macOS:
```bash
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --add /usr/bin/python3
```

**Step 4: Update Unity Backend URL**

```csharp
// ECGAPIClient configuration in Unity Inspector
Backend URL: http://192.168.1.100:5000  // Use your PC's IP
```

**Step 5: Test Connection**

Build to Quest 2, then in VR:
- Check Debug.Log output in Logcat
- Should see: `[ECG API] Backend is healthy!`

**Troubleshooting:**
- Ensure PC and Quest 2 are on same WiFi network
- Disable VPN on PC
- Check Flask server logs: `python ecg_api.py`
- Test from Quest 2 browser: `http://192.168.1.100:5000/health`

---

## Troubleshooting

### Issue: "Cannot connect to backend server"

**Symptoms:**
```
[ECG API] Backend not reachable: Could not resolve host
```

**Solutions:**
1. Verify Flask server is running: `http://localhost:5000/health` (should return JSON)
2. Check `backendURL` in Unity Inspector matches Flask address
3. For Quest 2: Use PC's local IP (not localhost)
4. Disable firewall temporarily to test

---

### Issue: "Invalid ECG shape" error

**Symptoms:**
```json
{
  "error": "Invalid ECG shape: expected (4096, 12), got (2048, 12)",
  "error_id": "ERR-XR-A3F7B2"
}
```

**Solutions:**
1. Verify ECG data has exactly **4096 samples × 12 leads**
2. Check JSON file format:
   ```json
   {
     "ecg_signal": [
       [v1_sample1, v2_sample1, ..., v12_sample1],  // Sample 0
       [v1_sample2, v2_sample2, ..., v12_sample2],  // Sample 1
       ...
       [v1_sample4096, v2_sample4096, ..., v12_sample4096]  // Sample 4095
     ]
   }
   ```
3. Verify `ConvertTo2DList()` produces correct dimensions

---

### Issue: "Signal has very low variance" error

**Symptoms:**
```json
{
  "error": "Signal has very low variance - appears to be flat/corrupted",
  "error_id": "ERR-XR-B8D3E1"
}
```

**Solutions:**
1. Check ECG signal isn't all zeros
2. Verify amplitude scaling (should be in millivolts, typically -1.0 to +1.0)
3. Use test data from `Backend/dummy_data/sample_normal.json`

---

### Issue: Slow response times (>1000ms)

**Possible Causes:**
1. **First request after server start** - Model loading takes ~2 seconds
2. **Cache miss** - Full analysis with Claude API takes ~450ms
3. **Network latency** - Quest 2 WiFi connection slow

**Solutions:**
1. Call `/health` endpoint on app startup to warm up server
2. Use temporal endpoints (/api/ecg/beats, /api/ecg/beat, /api/ecg/segment) for VR interaction
3. Monitor cache hit rate: `/api/cache/stats` (target >60%)
4. Check network latency with ping test

---

### Issue: "ANTHROPIC_API_KEY not set" warning

**Symptoms:**
```
[WARNING] ANTHROPIC_API_KEY not set - LLM interpretation will use fallback narratives
```

**Impact:** Backend still works, but uses canned responses instead of AI-generated interpretations

**Solution:**
```bash
# Windows
set ANTHROPIC_API_KEY=your_api_key_here

# macOS/Linux
export ANTHROPIC_API_KEY=your_api_key_here

# Restart Flask server
python ecg_api.py
```

---

### Issue: "Beat index out of range" error

**Symptoms:**
```json
{
  "error": "Beat index 15 out of range (0-12)",
  "error_id": "ERR-XR-C9E4F2",
  "beat_count": 13
}
```

**Solution:**
Always call `/api/ecg/beats` first to get `beat_count`, then validate index:

```csharp
BeatsResponse beats = ...;  // From /api/ecg/beats

int requestedBeat = 15;
if (requestedBeat < 0 || requestedBeat >= beats.beat_count)
{
    Debug.LogError($"Invalid beat index: {requestedBeat} (valid: 0-{beats.beat_count - 1})");
    return;
}

// Now safe to request beat detail
yield return apiClient.GetBeatDetail(ecgSignal, requestedBeat, ...);
```

---

## Appendix: ECG Data Format

### Sample ECG File Structure

File: `Backend/dummy_data/sample_normal.json`

```json
{
  "ecg_signal": [
    [0.05, -0.02, -0.07, 0.03, 0.08, 0.05, 0.12, 0.15, 0.10, 0.08, 0.18, 0.20],  // Sample 0
    [0.06, -0.01, -0.06, 0.04, 0.09, 0.06, 0.13, 0.16, 0.11, 0.09, 0.19, 0.21],  // Sample 1
    ...  // 4094 more samples
  ]
}
```

### ECG Lead Order

| Index | Lead Name | Clinical Significance |
|-------|-----------|----------------------|
| 0 | I | Lateral wall (left ventricle) |
| 1 | II | Inferior wall (best for R-peak detection) |
| 2 | III | Inferior wall |
| 3 | aVR | Right atrium |
| 4 | aVL | Lateral wall |
| 5 | aVF | Inferior wall |
| 6 | V1 | Right ventricle, septal wall |
| 7 | V2 | Septal wall |
| 8 | V3 | Anterior wall |
| 9 | V4 | Anterior wall |
| 10 | V5 | Lateral wall |
| 11 | V6 | Lateral wall |

### Cardiac Conditions Detected

| Condition | Description | Typical Findings |
|-----------|-------------|------------------|
| **1st_degree_AV_block** | Delayed AV conduction | PR interval > 200ms |
| **RBBB** | Right bundle branch block | QRS ≥ 120ms, rsR' in V1-V2 |
| **LBBB** | Left bundle branch block | QRS ≥ 120ms, broad R in V5-V6 |
| **sinus_bradycardia** | Slow heart rate | HR < 60 BPM |
| **atrial_fibrillation** | Irregular atrial rhythm | Absent P waves, irregular RR |
| **sinus_tachycardia** | Fast heart rate | HR > 100 BPM |

---

## Support & Resources

**Documentation:**
- Backend Enhancement Status: `Backend/ENHANCEMENT_STATUS.md`
- Unity Quick Start: `Backend/UNITY_QUICKSTART.md`
- Phase 2/3 Implementation Guide: `Backend/PHASE2_PHASE3_GUIDE.md`

**Test Suites:**
- All tests: `Backend/tests/`
- API test: `python tests/test_api.py`
- Storytelling test: `python tests/test_storytelling.py`
- Heart rate fallback test: `python tests/test_hr_fallback.py`
- Phase 3 endpoints test: `python tests/test_phase3.py`

**Sample Data:**
- Normal ECG: `Backend/dummy_data/sample_normal.json`
- Bradycardia ECG: `Backend/dummy_data/sample_bradycardia.json`
- Tachycardia ECG: `Backend/dummy_data/sample_tachycardia.json`

**Project Repository:**
- GitHub: [Your GitHub URL]
- Immerse the Bay 2025 Hackathon

---

**Last Updated:** 2025-11-15
**Backend Version:** 1.0.0 (All 3 Phases Complete)
**Endpoints:** 7 production-ready
**Test Coverage:** 100% (all tests passing)

For questions or issues, please check the [Troubleshooting](#troubleshooting) section or consult `Backend/ENHANCEMENT_STATUS.md` for implementation details.
