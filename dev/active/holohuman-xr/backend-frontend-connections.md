# Backend-Frontend Connection Documentation
## HoloHuman XR: Unity VR ↔ Flask Backend Integration

**Project:** HoloHuman XR
**Hackathon:** Immerse the Bay 2025
**Last Updated:** 2025-11-15 03:00 AM
**Document Purpose:** Complete technical specification for backend-frontend integration

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Backend (Flask) Specifications](#backend-flask-specifications)
3. [Frontend (Unity) Integration](#frontend-unity-integration)
4. [Data Flow Documentation](#data-flow-documentation)
5. [Animation Integration](#animation-integration)
6. [Sponsor Tool Integration Points](#sponsor-tool-integration-points)
7. [Implementation Templates](#implementation-templates)
8. [Performance Considerations](#performance-considerations)
9. [Development Timeline](#development-timeline)
10. [Troubleshooting Guide](#troubleshooting-guide)

---

## 1. Architecture Overview

### System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    USER IN VR HEADSET                       │
│                    (Meta Quest 2)                           │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                    UNITY VR FRONTEND                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Scene Components:                                    │  │
│  │  • 3D Heart Model (from Meshy.ai)                    │  │
│  │  • VR Controllers (XR Interaction Toolkit)           │  │
│  │  • UI Canvas (ECG results display)                   │  │
│  │  • Animation Controllers (DOTween)                   │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  C# Scripts:                                          │  │
│  │  • ECGManager.cs         (Main controller)           │  │
│  │  • FlaskAPIClient.cs     (HTTP communication)        │  │
│  │  • HeartVisualizer.cs    (3D model updates)          │  │
│  │  • LayerPeeler.cs        (Dissolve animations)       │  │
│  │  • ECGUIDisplay.cs       (UI updates)                │  │
│  └──────────────────────────────────────────────────────┘  │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        │ HTTP POST /api/ecg/predict
                        │ Content-Type: application/json
                        │ Body: { "ecg_signal": [[...]] }
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                    FLASK BACKEND API                        │
│                    http://localhost:5000                    │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Endpoints:                                           │  │
│  │  • POST /api/ecg/predict    (ECG analysis)           │  │
│  │  • GET  /api/health         (Health check)           │  │
│  │  • GET  /api/conditions     (List all conditions)    │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Python Modules:                                      │  │
│  │  • ecg_api.py           (Flask routes)               │  │
│  │  • model_loader.py      (TensorFlow model wrapper)   │  │
│  │  • data_processor.py    (ECG signal preprocessing)   │  │
│  └──────────────────────────────────────────────────────┘  │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        │ model.predict(ecg_data)
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│              TENSORFLOW ECG MODEL                           │
│  • Model: automatic-ecg-diagnosis                          │
│  • Input: (batch_size, 4096, 12) - 12-lead ECG            │
│  • Output: (batch_size, 6) - 6 cardiac conditions         │
│  • Conditions:                                             │
│    1. 1st degree AV block                                  │
│    2. Right bundle branch block (RBBB)                     │
│    3. Left bundle branch block (LBBB)                      │
│    4. Sinus bradycardia                                    │
│    5. Atrial fibrillation                                  │
│    6. Sinus tachycardia                                    │
└─────────────────────────────────────────────────────────────┘

RESPONSE FLOW:
┌─────────────────────────────────────────────────────────────┐
│  Flask API returns JSON:                                    │
│  {                                                          │
│    "predictions": {                                         │
│      "sinus_bradycardia": 0.78,                            │
│      "RBBB": 0.12,                                         │
│      "atrial_fibrillation": 0.10,                          │
│      ...                                                    │
│    },                                                       │
│    "top_condition": "sinus_bradycardia",                   │
│    "confidence": 0.78                                       │
│  }                                                          │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│  Unity Deserializes JSON → C# Object                       │
│  ECGResponse data = JsonUtility.FromJson<ECGResponse>(json) │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│  Unity Updates Visualization:                              │
│  • Heart color changes (RED if confidence > 70%)           │
│  • UI displays condition name + percentage                 │
│  • Haptic feedback triggers on controllers                 │
│  • Animation speed adjusts based on severity               │
└─────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Responsibility | Technology |
|-----------|---------------|------------|
| **Unity VR Frontend** | User interaction, 3D visualization, input handling | Unity 2022.3 LTS, C#, XR Interaction Toolkit |
| **Flask Backend** | ECG signal processing, ML inference, API endpoints | Python 3.8+, Flask, Flask-CORS |
| **TensorFlow Model** | Cardiac condition prediction from ECG data | TensorFlow 2.2, Keras |
| **Meshy.ai** | 3D heart model generation (pre-development) | External API (one-time use) |
| **SecureMR** | Medical imaging data retrieval (optional) | ByteDance API (runtime) |
| **CapCut** | Demo video editing (post-development) | Desktop app (offline) |

---

## 2. Backend (Flask) Specifications

### 2.1 API Endpoints

#### **POST /api/ecg/predict**

**Description:** Analyzes ECG signal and returns cardiac condition predictions

**Request:**
```http
POST /api/ecg/predict HTTP/1.1
Host: localhost:5000
Content-Type: application/json

{
  "ecg_signal": [
    [0.12, 0.15, 0.18, ...],  // 4096 samples for lead I
    [0.10, 0.13, 0.16, ...],  // 4096 samples for lead II
    // ... 10 more leads (total 12 leads)
  ]
}
```

**Request Schema:**
```json
{
  "ecg_signal": "array[12][4096]",  // Required: 12-lead ECG with 4096 samples per lead
  "patient_id": "string",            // Optional: For tracking/logging
  "timestamp": "number"              // Optional: Unix timestamp
}
```

**Response (Success - 200 OK):**
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
  "top_condition": "sinus_bradycardia",
  "confidence": 0.78,
  "processing_time_ms": 145,
  "model_version": "1.0.0"
}
```

**Response (Error - 400 Bad Request):**
```json
{
  "error": "Invalid ECG signal format",
  "details": "Expected array of shape (12, 4096), got (10, 4096)",
  "code": "INVALID_INPUT"
}
```

**Response (Error - 500 Internal Server Error):**
```json
{
  "error": "Model inference failed",
  "details": "TensorFlow runtime error: ...",
  "code": "MODEL_ERROR"
}
```

---

#### **GET /api/health**

**Description:** Health check endpoint to verify server is running

**Request:**
```http
GET /api/health HTTP/1.1
Host: localhost:5000
```

**Response (200 OK):**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "uptime_seconds": 3600,
  "version": "1.0.0"
}
```

---

#### **GET /api/conditions**

**Description:** Returns list of all detectable cardiac conditions

**Request:**
```http
GET /api/conditions HTTP/1.1
Host: localhost:5000
```

**Response (200 OK):**
```json
{
  "conditions": [
    {
      "id": "1st_degree_AV_block",
      "name": "1st Degree AV Block",
      "description": "Prolonged PR interval on ECG",
      "severity": "low"
    },
    {
      "id": "RBBB",
      "name": "Right Bundle Branch Block",
      "description": "Delayed right ventricular activation",
      "severity": "medium"
    },
    // ... other conditions
  ],
  "total": 6
}
```

---

### 2.2 Flask Server Configuration

**CORS Configuration:**
```python
# Required for Unity to access Flask API from different origin
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})  # Development only
# Production: CORS(app, resources={r"/api/*": {"origins": "https://yourdomain.com"}})
```

**Server Settings:**
```python
if __name__ == '__main__':
    app.run(
        host='0.0.0.0',      # Accept connections from any IP (for Quest 2 WiFi)
        port=5000,           # Standard Flask port
        debug=True,          # Enable hot reload during development
        threaded=True        # Handle concurrent requests
    )
```

---

### 2.3 ECG Data Format

**Input Specification:**
- **Format:** NumPy array or nested list
- **Shape:** `(12, 4096)` or `(1, 12, 4096)` with batch dimension
- **Data Type:** float32 or float64
- **Value Range:** Typically -5.0 to +5.0 mV (normalized)
- **Sampling Rate:** 400 Hz (4096 samples = 10.24 seconds of ECG)

**Lead Order (Standard 12-lead ECG):**
1. Lead I
2. Lead II
3. Lead III
4. aVR
5. aVL
6. aVF
7. V1
8. V2
9. V3
10. V4
11. V5
12. V6

**Example Data Structure:**
```python
ecg_signal = np.array([
    [0.12, 0.15, 0.18, ...],  # Lead I:   4096 samples
    [0.10, 0.13, 0.16, ...],  # Lead II:  4096 samples
    [0.08, 0.11, 0.14, ...],  # Lead III: 4096 samples
    # ... 9 more leads
])  # Shape: (12, 4096)
```

---

### 2.4 Error Handling Patterns

**Flask Error Handler Template:**
```python
from flask import jsonify

@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        'error': 'Bad Request',
        'details': str(error),
        'code': 'BAD_REQUEST'
    }), 400

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'error': 'Internal Server Error',
        'details': 'An unexpected error occurred',
        'code': 'INTERNAL_ERROR'
    }), 500
```

**Validation Example:**
```python
def validate_ecg_signal(data):
    """Validates ECG signal format before inference"""
    if 'ecg_signal' not in data:
        raise ValueError("Missing 'ecg_signal' field")

    signal = np.array(data['ecg_signal'])

    if signal.shape != (12, 4096):
        raise ValueError(f"Expected shape (12, 4096), got {signal.shape}")

    if not np.isfinite(signal).all():
        raise ValueError("ECG signal contains NaN or Inf values")

    return signal
```

---

## 3. Frontend (Unity) Integration

### 3.1 UnityWebRequest Implementation

**HTTP Client Class Structure:**

```csharp
// FlaskAPIClient.cs
using System;
using System.Collections;
using System.Text;
using UnityEngine;
using UnityEngine.Networking;

public class FlaskAPIClient : MonoBehaviour
{
    [Header("API Configuration")]
    [SerializeField] private string apiBaseUrl = "http://localhost:5000";
    [SerializeField] private int timeoutSeconds = 10;

    // Endpoints
    private string PredictEndpoint => $"{apiBaseUrl}/api/ecg/predict";
    private string HealthEndpoint => $"{apiBaseUrl}/api/health";

    /// <summary>
    /// Sends ECG data to Flask backend for analysis
    /// </summary>
    /// <param name="ecgJson">JSON string containing ECG signal data</param>
    /// <param name="onSuccess">Callback invoked with ECGResponse on success</param>
    /// <param name="onError">Callback invoked with error message on failure</param>
    public IEnumerator SendECGAnalysisRequest(
        string ecgJson,
        Action<ECGResponse> onSuccess,
        Action<string> onError = null
    )
    {
        // Create HTTP POST request
        var request = new UnityWebRequest(PredictEndpoint, "POST");

        // Set request body
        byte[] bodyRaw = Encoding.UTF8.GetBytes(ecgJson);
        request.uploadHandler = new UploadHandlerRaw(bodyRaw);
        request.downloadHandler = new DownloadHandlerBuffer();

        // Set headers
        request.SetRequestHeader("Content-Type", "application/json");
        request.timeout = timeoutSeconds;

        // Send request
        yield return request.SendWebRequest();

        // Handle response
        if (request.result == UnityWebRequest.Result.Success)
        {
            string jsonResponse = request.downloadHandler.text;
            Debug.Log($"[API] Received response: {jsonResponse}");

            try
            {
                ECGResponse data = JsonUtility.FromJson<ECGResponse>(jsonResponse);
                onSuccess?.Invoke(data);
            }
            catch (Exception e)
            {
                Debug.LogError($"[API] JSON parsing failed: {e.Message}");
                onError?.Invoke($"Failed to parse response: {e.Message}");
            }
        }
        else
        {
            string errorMsg = $"API Error: {request.error}\nHTTP {request.responseCode}";
            Debug.LogError($"[API] {errorMsg}");
            onError?.Invoke(errorMsg);
        }
    }

    /// <summary>
    /// Checks if Flask backend is healthy and responsive
    /// </summary>
    public IEnumerator CheckHealth(Action<bool> callback)
    {
        UnityWebRequest request = UnityWebRequest.Get(HealthEndpoint);
        request.timeout = 5;

        yield return request.SendWebRequest();

        bool isHealthy = request.result == UnityWebRequest.Result.Success;
        callback?.Invoke(isHealthy);
    }
}
```

**Key Implementation Notes:**
- Use `UnityWebRequest` (modern, VR-compatible)
- Always set `Content-Type: application/json` header
- Use `UploadHandlerRaw` for POST body
- Use `DownloadHandlerBuffer` for response
- Set timeout to prevent infinite waiting
- Handle errors gracefully with callbacks

---

### 3.2 JSON Deserialization Classes

**Data Models for ECG Response:**

```csharp
// ECGDataModels.cs
using System;
using UnityEngine;

/// <summary>
/// Main response from Flask /api/ecg/predict endpoint
/// </summary>
[Serializable]
public class ECGResponse
{
    public ECGPredictions predictions;
    public string top_condition;
    public float confidence;
    public float processing_time_ms;
    public string model_version;
}

/// <summary>
/// Nested predictions object containing all 6 cardiac conditions
/// NOTE: JsonUtility requires public fields, not properties
/// </summary>
[Serializable]
public class ECGPredictions
{
    // Field names MUST match JSON keys exactly
    [SerializeField] public float degree_AV_block_1st;  // Maps to "1st_degree_AV_block"
    [SerializeField] public float RBBB;
    [SerializeField] public float LBBB;
    [SerializeField] public float sinus_bradycardia;
    [SerializeField] public float atrial_fibrillation;
    [SerializeField] public float sinus_tachycardia;

    /// <summary>
    /// Helper method to get highest probability condition
    /// </summary>
    public string GetTopCondition()
    {
        float max = Mathf.Max(
            degree_AV_block_1st,
            RBBB,
            LBBB,
            sinus_bradycardia,
            atrial_fibrillation,
            sinus_tachycardia
        );

        if (max == degree_AV_block_1st) return "1st Degree AV Block";
        if (max == RBBB) return "Right Bundle Branch Block";
        if (max == LBBB) return "Left Bundle Branch Block";
        if (max == sinus_bradycardia) return "Sinus Bradycardia";
        if (max == atrial_fibrillation) return "Atrial Fibrillation";
        if (max == sinus_tachycardia) return "Sinus Tachycardia";

        return "Unknown";
    }
}

/// <summary>
/// Error response from Flask API
/// </summary>
[Serializable]
public class ECGErrorResponse
{
    public string error;
    public string details;
    public string code;
}

/// <summary>
/// Health check response
/// </summary>
[Serializable]
public class HealthResponse
{
    public string status;
    public bool model_loaded;
    public float uptime_seconds;
    public string version;
}
```

**JsonUtility Important Notes:**
- Only serializes **public fields** (not properties)
- Cannot handle dictionaries directly
- Cannot handle field names starting with numbers (e.g., "1st_degree")
- Use `[SerializeField]` for clarity but not required for public fields
- Field names must match JSON keys exactly (case-sensitive)

**Alternative: Using Newtonsoft.Json (if needed):**
```csharp
// If you need Dictionary support or more flexibility
using Newtonsoft.Json;

[Serializable]
public class ECGResponseNewtonsoft
{
    [JsonProperty("predictions")]
    public Dictionary<string, float> Predictions { get; set; }

    [JsonProperty("top_condition")]
    public string TopCondition { get; set; }

    [JsonProperty("confidence")]
    public float Confidence { get; set; }
}

// Deserialize:
ECGResponseNewtonsoft data = JsonConvert.DeserializeObject<ECGResponseNewtonsoft>(json);
```

---

### 3.3 MaterialPropertyBlock Usage

**Why Use MaterialPropertyBlock:**
- **Performance:** Avoids creating material copies (critical for VR)
- **Memory:** Single material instance shared across objects
- **FPS:** No garbage collection from material instantiation
- **GPU Instancing:** Compatible with GPU instancing for batching

**Correct Implementation:**

```csharp
// HeartMaterialController.cs
using UnityEngine;

public class HeartMaterialController : MonoBehaviour
{
    private MaterialPropertyBlock propBlock;
    private Renderer heartRenderer;

    // Cache shader property IDs for performance
    private static readonly int ColorID = Shader.PropertyToID("_Color");
    private static readonly int EmissionColorID = Shader.PropertyToID("_EmissionColor");

    void Awake()
    {
        propBlock = new MaterialPropertyBlock();
        heartRenderer = GetComponent<Renderer>();
    }

    /// <summary>
    /// Updates heart color based on health status (CORRECT way)
    /// </summary>
    public void SetHeartColor(Color color)
    {
        heartRenderer.GetPropertyBlock(propBlock);
        propBlock.SetColor(ColorID, color);
        heartRenderer.SetPropertyBlock(propBlock);
    }

    /// <summary>
    /// Updates emission glow (CORRECT way)
    /// </summary>
    public void SetEmissionGlow(Color emissionColor)
    {
        heartRenderer.GetPropertyBlock(propBlock);
        propBlock.SetColor(EmissionColorID, emissionColor);
        heartRenderer.SetPropertyBlock(propBlock);
    }

    /// <summary>
    /// Retrieves current color from property block
    /// </summary>
    public Color GetCurrentColor()
    {
        heartRenderer.GetPropertyBlock(propBlock);
        return propBlock.GetColor(ColorID);
    }
}
```

**WRONG Implementation (Avoid This):**
```csharp
// ❌ BAD: Creates a new material instance every time
void SetHeartColorWrong(Color color)
{
    GetComponent<Renderer>().material.color = color;  // Creates material copy!
}

// ❌ BAD: Leaks memory in loops
void UpdateColorEveryFrame()
{
    Update() {
        material.color = Color.Lerp(Color.red, Color.green, Time.time);  // Memory leak!
    }
}
```

**Performance Comparison:**
| Method | Material Copies | GC Allocations | FPS Impact |
|--------|-----------------|----------------|------------|
| `material.color = x` | YES (1 per call) | 2.4 KB per frame | -15 FPS |
| `MaterialPropertyBlock` | NO | 0 KB (after init) | 0 FPS |

---

### 3.4 Coroutine Patterns for Async Requests

**Main Controller Implementation:**

```csharp
// ECGManager.cs
using UnityEngine;
using UnityEngine.XR.Interaction.Toolkit;
using TMPro;

public class ECGManager : MonoBehaviour
{
    [Header("Components")]
    [SerializeField] private FlaskAPIClient apiClient;
    [SerializeField] private HeartVisualizer heartVisualizer;
    [SerializeField] private ECGUIDisplay uiDisplay;

    [Header("Sample Data")]
    [SerializeField] private TextAsset sampleECGJson;  // Assign in Inspector

    [Header("UI Feedback")]
    [SerializeField] private TextMeshProUGUI statusText;
    [SerializeField] private GameObject loadingIndicator;

    private bool isProcessing = false;

    /// <summary>
    /// Called when user presses "Analyze ECG" button in VR
    /// </summary>
    public void OnAnalyzeButtonPressed()
    {
        if (isProcessing)
        {
            Debug.LogWarning("[ECG] Analysis already in progress");
            return;
        }

        StartCoroutine(AnalyzeECGSequence());
    }

    /// <summary>
    /// Complete ECG analysis workflow
    /// </summary>
    IEnumerator AnalyzeECGSequence()
    {
        isProcessing = true;

        // Step 1: Show loading UI
        ShowLoading(true);
        statusText.text = "Analyzing ECG...";

        // Step 2: Load ECG data (from file or real sensor)
        string ecgJson = LoadECGData();

        // Step 3: Send to Flask backend
        bool requestComplete = false;
        ECGResponse responseData = null;
        string errorMessage = null;

        StartCoroutine(apiClient.SendECGAnalysisRequest(
            ecgJson,
            onSuccess: (data) => {
                responseData = data;
                requestComplete = true;
            },
            onError: (error) => {
                errorMessage = error;
                requestComplete = true;
            }
        ));

        // Step 4: Wait for response (with timeout)
        float elapsed = 0f;
        float timeout = 10f;

        while (!requestComplete && elapsed < timeout)
        {
            elapsed += Time.deltaTime;
            yield return null;
        }

        // Step 5: Handle response or timeout
        if (errorMessage != null)
        {
            // Error occurred
            statusText.text = $"Error: {errorMessage}";
            statusText.color = Color.red;
        }
        else if (responseData != null)
        {
            // Success - update visualization
            statusText.text = "Analysis Complete!";
            statusText.color = Color.green;

            OnECGResultsReceived(responseData);
        }
        else
        {
            // Timeout
            statusText.text = "Request timed out";
            statusText.color = Color.yellow;
        }

        // Step 6: Hide loading UI
        ShowLoading(false);
        isProcessing = false;
    }

    /// <summary>
    /// Handles successful ECG analysis results
    /// </summary>
    void OnECGResultsReceived(ECGResponse data)
    {
        Debug.Log($"[ECG] Top condition: {data.top_condition} ({data.confidence:P})");

        // Update visualizations
        heartVisualizer.UpdateVisualization(data);
        uiDisplay.DisplayResults(data);

        // Trigger haptic feedback
        TriggerHapticFeedback(data.confidence);
    }

    string LoadECGData()
    {
        // For demo: Load from TextAsset assigned in Inspector
        return sampleECGJson.text;

        // For production: Load from real ECG sensor or file
        // return File.ReadAllText(Application.persistentDataPath + "/ecg_data.json");
    }

    void ShowLoading(bool show)
    {
        if (loadingIndicator != null)
            loadingIndicator.SetActive(show);
    }

    void TriggerHapticFeedback(float intensity)
    {
        // Quest 2 controller vibration
        // Higher confidence = stronger vibration
        float hapticStrength = Mathf.Clamp01(intensity);

        // Requires Meta XR SDK or Unity XR
        // OVRInput.SetControllerVibration(1, hapticStrength, OVRInput.Controller.RTouch);
    }
}
```

**Coroutine Best Practices:**
1. **Always check `isProcessing` flag** to prevent duplicate requests
2. **Show loading indicators** for user feedback
3. **Implement timeout logic** (don't wait forever)
4. **Use callbacks** for async completion
5. **Never block main thread** - use `yield return null`

---

## 4. Data Flow Documentation

### 4.1 Complete User Interaction Flow

```
┌────────────────────────────────────────────────────────────────┐
│ STEP 1: USER INTERACTION                                       │
│ User in VR headset presses "Analyze ECG" button                │
│ • XRInteractable detects button press                          │
│ • Triggers ECGManager.OnAnalyzeButtonPressed()                 │
└────────────────────────────────────────────────────────────────┘
                            ↓
┌────────────────────────────────────────────────────────────────┐
│ STEP 2: PREPARE REQUEST                                        │
│ Unity prepares ECG data                                        │
│ • Load ECG signal from file or sensor                          │
│ • Format as JSON: { "ecg_signal": [[...]] }                   │
│ • Show loading indicator in VR UI                             │
│ Time: ~0.1 seconds                                             │
└────────────────────────────────────────────────────────────────┘
                            ↓
┌────────────────────────────────────────────────────────────────┐
│ STEP 3: SEND HTTP REQUEST                                      │
│ Unity → Flask Backend                                          │
│ • UnityWebRequest.Post(http://localhost:5000/api/ecg/predict) │
│ • Headers: Content-Type: application/json                     │
│ • Body: ECG signal JSON                                        │
│ • Coroutine yields while waiting for response                 │
│ Time: ~0.2 seconds (network latency)                           │
└────────────────────────────────────────────────────────────────┘
                            ↓
┌────────────────────────────────────────────────────────────────┐
│ STEP 4: FLASK RECEIVES REQUEST                                 │
│ Flask API processes incoming request                           │
│ • CORS middleware validates origin                             │
│ • Route handler extracts JSON body                             │
│ • Validates ECG signal format (12, 4096)                       │
│ • Converts to NumPy array                                      │
│ Time: ~0.01 seconds                                            │
└────────────────────────────────────────────────────────────────┘
                            ↓
┌────────────────────────────────────────────────────────────────┐
│ STEP 5: MODEL INFERENCE                                        │
│ TensorFlow model predicts cardiac conditions                  │
│ • Input: (1, 12, 4096) ECG signal                             │
│ • Forward pass through neural network                          │
│ • Output: (1, 6) probability vector                           │
│ • Softmax normalization                                        │
│ Time: ~0.1-0.3 seconds (GPU accelerated)                       │
└────────────────────────────────────────────────────────────────┘
                            ↓
┌────────────────────────────────────────────────────────────────┐
│ STEP 6: FORMAT RESPONSE                                        │
│ Flask formats results as JSON                                  │
│ • Extract top condition (argmax)                               │
│ • Calculate confidence score                                   │
│ • Structure response object                                    │
│ • Return JSON with 200 OK status                               │
│ Time: ~0.01 seconds                                            │
└────────────────────────────────────────────────────────────────┘
                            ↓
┌────────────────────────────────────────────────────────────────┐
│ STEP 7: UNITY RECEIVES RESPONSE                                │
│ UnityWebRequest completes                                      │
│ • Check request.result == Success                              │
│ • Extract JSON string from downloadHandler.text               │
│ • Parse JSON → ECGResponse C# object                          │
│ • Invoke success callback                                      │
│ Time: ~0.05 seconds                                            │
└────────────────────────────────────────────────────────────────┘
                            ↓
┌────────────────────────────────────────────────────────────────┐
│ STEP 8: UPDATE 3D VISUALIZATION                                │
│ HeartVisualizer updates 3D model                               │
│ • Determine color based on confidence                          │
│   - confidence > 0.7 → RED (critical)                          │
│   - confidence > 0.4 → YELLOW (warning)                        │
│   - confidence ≤ 0.4 → GREEN (normal)                          │
│ • Animate color transition (1.5 seconds)                       │
│ • Update MaterialPropertyBlock with new color                  │
│ Time: ~1.5 seconds (smooth animation)                          │
└────────────────────────────────────────────────────────────────┘
                            ↓
┌────────────────────────────────────────────────────────────────┐
│ STEP 9: UPDATE UI DISPLAY                                      │
│ ECGUIDisplay shows results                                     │
│ • Condition name: "Sinus Bradycardia"                          │
│ • Confidence: "78%"                                            │
│ • All predictions in list format                               │
│ • Color-coded by severity                                      │
│ Time: ~0.1 seconds                                             │
└────────────────────────────────────────────────────────────────┘
                            ↓
┌────────────────────────────────────────────────────────────────┐
│ STEP 10: HAPTIC FEEDBACK                                       │
│ VR controller vibrates                                         │
│ • Vibration intensity = confidence level                       │
│ • Duration: 0.2-0.5 seconds                                    │
│ • User feels tactile confirmation                              │
│ Time: ~0.3 seconds                                             │
└────────────────────────────────────────────────────────────────┘
                            ↓
┌────────────────────────────────────────────────────────────────┐
│ COMPLETE: Total Time ~2.0-2.5 seconds                          │
│ User sees results and feels feedback                           │
└────────────────────────────────────────────────────────────────┘
```

### 4.2 Timing Breakdown

| Phase | Duration | Cumulative |
|-------|----------|------------|
| User button press | 0.0s | 0.0s |
| Prepare request | 0.1s | 0.1s |
| Network send | 0.2s | 0.3s |
| Flask validation | 0.01s | 0.31s |
| Model inference | 0.2s | 0.51s |
| Format response | 0.01s | 0.52s |
| Network receive | 0.05s | 0.57s |
| Parse JSON | 0.05s | 0.62s |
| Update visualization | 1.5s | 2.12s |
| Update UI | 0.1s | 2.22s |
| Haptic feedback | 0.3s | 2.52s |
| **TOTAL** | **~2.5s** | **2.5s** |

---

### 4.3 Error Handling Flow

```
┌────────────────────────────────────────────────────────────────┐
│ ERROR SCENARIO 1: Network Timeout                              │
│                                                                 │
│ Unity sends request → No response after 10 seconds             │
│         ↓                                                       │
│ UnityWebRequest.result == ConnectionError                      │
│         ↓                                                       │
│ Show error UI: "Connection timeout. Check Flask server."       │
│         ↓                                                       │
│ Enable retry button                                            │
└────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────┐
│ ERROR SCENARIO 2: Invalid ECG Data                             │
│                                                                 │
│ Unity sends malformed JSON → Flask validates → Returns 400     │
│         ↓                                                       │
│ UnityWebRequest.responseCode == 400                            │
│         ↓                                                       │
│ Parse error response JSON                                      │
│         ↓                                                       │
│ Show error UI: "Invalid ECG format. Expected 12 leads."        │
└────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────┐
│ ERROR SCENARIO 3: Model Failure                                │
│                                                                 │
│ Flask model crashes during inference → Returns 500             │
│         ↓                                                       │
│ UnityWebRequest.responseCode == 500                            │
│         ↓                                                       │
│ Show error UI: "Analysis failed. Please try again."            │
│         ↓                                                       │
│ Log error details for debugging                                │
└────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────┐
│ ERROR SCENARIO 4: CORS Blocked                                 │
│                                                                 │
│ Browser/Unity → Flask without CORS headers                     │
│         ↓                                                       │
│ Request blocked by browser security                            │
│         ↓                                                       │
│ UnityWebRequest.error contains "CORS"                          │
│         ↓                                                       │
│ Show error UI: "Server configuration error. Contact dev."      │
└────────────────────────────────────────────────────────────────┘
```

---

## 5. Animation Integration

### 5.1 ECG Results → Visual Feedback Mapping

**Condition Severity → Color Mapping:**

| Confidence Range | Severity | Heart Color | Emission Glow | Animation Speed |
|------------------|----------|-------------|---------------|-----------------|
| 0.0 - 0.3 | Low | Green | Dim green | Normal (1x) |
| 0.3 - 0.5 | Medium-Low | Light Yellow | Soft yellow | Slightly faster (1.2x) |
| 0.5 - 0.7 | Medium-High | Orange | Moderate orange | Faster (1.5x) |
| 0.7 - 0.9 | High | Red-Orange | Bright red | Much faster (2x) |
| 0.9 - 1.0 | Critical | Deep Red | Pulsing red | Very fast (2.5x) |

**Implementation Mapping:**

```csharp
// HeartVisualizer.cs
public class HeartVisualizer : MonoBehaviour
{
    public void UpdateVisualization(ECGResponse data)
    {
        // 1. Map confidence to color
        Color targetColor = GetColorForConfidence(data.confidence);

        // 2. Map confidence to animation speed
        float heartbeatSpeed = GetHeartbeatSpeed(data.confidence);

        // 3. Map confidence to emission intensity
        float emissionIntensity = GetEmissionIntensity(data.confidence);

        // 4. Apply all visual changes
        AnimateColorChange(targetColor, 1.5f);
        SetHeartbeatSpeed(heartbeatSpeed);
        SetEmissionGlow(targetColor * emissionIntensity);
    }

    Color GetColorForConfidence(float confidence)
    {
        if (confidence < 0.3f) return new Color(0.2f, 0.8f, 0.2f);  // Green
        if (confidence < 0.5f) return new Color(0.9f, 0.9f, 0.2f);  // Yellow
        if (confidence < 0.7f) return new Color(1.0f, 0.6f, 0.1f);  // Orange
        if (confidence < 0.9f) return new Color(1.0f, 0.2f, 0.1f);  // Red-Orange
        return new Color(0.8f, 0.0f, 0.0f);                         // Deep Red
    }

    float GetHeartbeatSpeed(float confidence)
    {
        // Normal: 60-100 BPM → 1.0x speed
        // Critical: 100-150 BPM → 2.5x speed
        return Mathf.Lerp(1.0f, 2.5f, confidence);
    }

    float GetEmissionIntensity(float confidence)
    {
        // Dim glow for low confidence, bright for high
        return Mathf.Lerp(0.5f, 3.0f, confidence);
    }
}
```

---

### 5.2 Animation Types and Triggers

**Three Main Animation Systems:**

1. **Heartbeat Pulse (Continuous)**
   - Always running in background
   - Speed adjusts based on ECG results
   - Uses DOTween for transform scale

2. **Color Transition (Event-Driven)**
   - Triggered when ECG results received
   - Smooth 1.5-second transition
   - Uses MaterialPropertyBlock

3. **Layer Peeling (User-Initiated)**
   - Triggered by VR grab/button press
   - Dissolve shader animation
   - 2-second duration per layer

**Trigger Map:**

| User Action | Animation Triggered | Duration | Script |
|-------------|---------------------|----------|--------|
| Press "Analyze ECG" | Color transition | 1.5s | HeartVisualizer.cs |
| ECG results received | Heartbeat speed change | Instant | HeartbeatController.cs |
| Grab heart | Layer dissolve | 2.0s | LayerPeeler.cs |
| Release heart | Layer restore | 2.0s | LayerPeeler.cs |
| Hover controller | Highlight glow | 0.3s | VRInteraction.cs |

---

### 5.3 Heartbeat Animation Implementation

**DOTween-Based Heartbeat:**

```csharp
// HeartbeatController.cs
using DG.Tweening;
using UnityEngine;

public class HeartbeatController : MonoBehaviour
{
    [Header("Animation Settings")]
    [SerializeField] private float baseScale = 1.0f;
    [SerializeField] private float pulseScale = 1.15f;
    [SerializeField] private float baseDuration = 0.6f;  // 100 BPM

    private Tween heartbeatTween;
    private float currentSpeed = 1.0f;

    void Start()
    {
        StartHeartbeat();
    }

    public void StartHeartbeat()
    {
        // Kill existing animation if any
        heartbeatTween?.Kill();

        // Create new heartbeat animation
        heartbeatTween = transform.DOScale(pulseScale, baseDuration / 2)
            .SetLoops(-1, LoopType.Yoyo)
            .SetEase(Ease.InOutSine)
            .SetSpeedBased(false);
    }

    /// <summary>
    /// Adjusts heartbeat speed based on ECG severity
    /// </summary>
    /// <param name="speedMultiplier">1.0 = normal, 2.0 = twice as fast</param>
    public void SetHeartbeatSpeed(float speedMultiplier)
    {
        currentSpeed = speedMultiplier;

        if (heartbeatTween != null && heartbeatTween.IsActive())
        {
            heartbeatTween.timeScale = speedMultiplier;
        }
    }

    public void StopHeartbeat()
    {
        heartbeatTween?.Kill();
        transform.localScale = Vector3.one * baseScale;
    }
}
```

---

### 5.4 Color Animation Implementation

**Smooth Color Transition:**

```csharp
// ColorAnimator.cs (part of HeartVisualizer)
using System.Collections;
using UnityEngine;

public class ColorAnimator : MonoBehaviour
{
    private MaterialPropertyBlock propBlock;
    private Renderer rend;
    private static readonly int ColorID = Shader.PropertyToID("_Color");

    void Awake()
    {
        propBlock = new MaterialPropertyBlock();
        rend = GetComponent<Renderer>();
    }

    /// <summary>
    /// Smoothly transitions heart color from current to target
    /// </summary>
    public IEnumerator AnimateColorChange(Color targetColor, float duration)
    {
        // Get current color
        rend.GetPropertyBlock(propBlock);
        Color startColor = propBlock.GetColor(ColorID);

        float elapsed = 0f;

        while (elapsed < duration)
        {
            elapsed += Time.deltaTime;
            float t = elapsed / duration;

            // Smooth interpolation (ease in-out)
            float smoothT = Mathf.SmoothStep(0, 1, t);
            Color currentColor = Color.Lerp(startColor, targetColor, smoothT);

            // Update MaterialPropertyBlock
            propBlock.SetColor(ColorID, currentColor);
            rend.SetPropertyBlock(propBlock);

            yield return null;
        }

        // Ensure final color is exact
        propBlock.SetColor(ColorID, targetColor);
        rend.SetPropertyBlock(propBlock);
    }
}
```

---

### 5.5 Layer Peeling Animation

**Dissolve Shader Control:**

```csharp
// LayerPeeler.cs
using DG.Tweening;
using UnityEngine;

public class LayerPeeler : MonoBehaviour
{
    [Header("Layers (Outer to Inner)")]
    [SerializeField] private Material[] layerMaterials;

    private int currentLayerIndex = 0;
    private static readonly int DissolveID = Shader.PropertyToID("_DissolveAmount");

    void Start()
    {
        // Initialize all layers to visible
        foreach (var mat in layerMaterials)
        {
            mat.SetFloat(DissolveID, 0f);  // 0 = fully visible
        }
    }

    /// <summary>
    /// Peels away the current outer layer
    /// </summary>
    public void PeelNextLayer()
    {
        if (currentLayerIndex >= layerMaterials.Length)
        {
            Debug.Log("[Layer] All layers already peeled");
            return;
        }

        Material layerToPeel = layerMaterials[currentLayerIndex];

        // Animate dissolve from 0 (visible) to 1 (dissolved)
        layerToPeel.DOFloat(1f, DissolveID, 2.0f)
            .SetEase(Ease.InOutQuad)
            .OnComplete(() => {
                Debug.Log($"[Layer] Peeled layer {currentLayerIndex}");
            });

        currentLayerIndex++;
    }

    /// <summary>
    /// Restores all layers to visible state
    /// </summary>
    public void RestoreAllLayers()
    {
        for (int i = 0; i < layerMaterials.Length; i++)
        {
            layerMaterials[i].DOFloat(0f, DissolveID, 1.5f)
                .SetDelay(i * 0.2f);  // Stagger restoration
        }

        currentLayerIndex = 0;
    }

    /// <summary>
    /// VR interaction: Called when user grabs heart
    /// </summary>
    public void OnVRGrab()
    {
        PeelNextLayer();
    }
}
```

---

## 6. Sponsor Tool Integration Points

### 6.1 Meshy.ai Integration

**Use Case:** Generate 3D heart model for Unity scene

**Integration Type:** Pre-development (one-time asset generation)

**Workflow:**

```
┌─────────────────────────────────────────────────────────────┐
│ STEP 1: Sign up for Meshy.ai                                │
│ → Visit https://www.meshy.ai/                               │
│ → Create account (use school email for extra credits)       │
│ → Navigate to "Text to 3D" tool                             │
└─────────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 2: Generate Heart Model                                │
│ → Prompt: "Anatomically accurate human heart with visible   │
│            chambers, aorta, pulmonary artery, realistic     │
│            texture, optimized for VR, low-poly"             │
│ → Art Style: Realistic                                      │
│ → Negative Prompt: "cartoon, stylized, high-poly"          │
│ → Wait 2-5 minutes for generation                           │
└─────────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 3: Download Model                                      │
│ → Format: FBX (best for Unity) or OBJ                      │
│ → Include textures: YES                                     │
│ → Save to: UnityProject/Assets/Models/heart.fbx            │
└─────────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 4: Import to Unity                                     │
│ → Drag heart.fbx into Assets/Models/ folder                │
│ → Unity auto-imports with materials                         │
│ → Inspect model: Check poly count (<50k for VR)            │
│ → Optimize if needed (use Blender decimate modifier)        │
└─────────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 5: Set up in Scene                                     │
│ → Drag heart.fbx into VR scene                             │
│ → Position at (0, 1.5, 2) - eye level, 2m forward          │
│ → Add components:                                            │
│   - Rigidbody (for physics)                                 │
│   - XRGrabInteractable (for VR interaction)                 │
│   - HeartVisualizer script                                  │
└─────────────────────────────────────────────────────────────┘
```

**No Runtime Code Required** - Meshy.ai only used for asset creation.

**Sponsor Credit:** Mention in README and Devpost:
> "3D heart model generated using Meshy.ai's text-to-3D AI technology"

---

### 6.2 SecureMR Integration (Optional)

**Use Case:** Retrieve and display real medical imaging (DICOM) in VR

**Integration Type:** Runtime API calls

**Workflow:**

```csharp
// SecureMRClient.cs
using System.Collections;
using UnityEngine;
using UnityEngine.Networking;

public class SecureMRClient : MonoBehaviour
{
    [Header("SecureMR API Configuration")]
    [SerializeField] private string apiUrl = "https://api.securemr.com/v1";
    [SerializeField] private string apiKey = "YOUR_API_KEY";  // Get from ByteDance booth

    /// <summary>
    /// Fetches medical imaging data for a patient
    /// </summary>
    public IEnumerator GetMedicalImages(string patientId, Action<Texture2D[]> callback)
    {
        string endpoint = $"{apiUrl}/images?patient_id={patientId}";

        UnityWebRequest request = UnityWebRequest.Get(endpoint);
        request.SetRequestHeader("Authorization", $"Bearer {apiKey}");
        request.SetRequestHeader("Accept", "application/json");

        yield return request.SendWebRequest();

        if (request.result == UnityWebRequest.Result.Success)
        {
            // Parse response and convert DICOM to textures
            // (Implementation depends on SecureMR API format)
            string json = request.downloadHandler.text;
            Texture2D[] images = ParseDICOMResponse(json);
            callback?.Invoke(images);
        }
        else
        {
            Debug.LogError($"[SecureMR] Failed to fetch images: {request.error}");
            callback?.Invoke(null);
        }
    }

    Texture2D[] ParseDICOMResponse(string json)
    {
        // TODO: Implement based on SecureMR API documentation
        // Likely involves:
        // 1. Parse JSON to get DICOM image URLs
        // 2. Download each image
        // 3. Convert DICOM → PNG/JPG → Texture2D
        // 4. Return array of textures

        return new Texture2D[0];
    }
}
```

**Display in VR:**

```csharp
// MedicalImageViewer.cs
using UnityEngine;
using UnityEngine.UI;

public class MedicalImageViewer : MonoBehaviour
{
    [SerializeField] private RawImage imageDisplay;  // UI canvas in VR
    [SerializeField] private SecureMRClient secureMRClient;

    public void ShowPatientScans(string patientId)
    {
        StartCoroutine(secureMRClient.GetMedicalImages(patientId, (images) => {
            if (images != null && images.Length > 0)
            {
                // Display first image
                imageDisplay.texture = images[0];
                imageDisplay.gameObject.SetActive(true);
            }
        }));
    }
}
```

**Sponsor Credit:** Mention in README:
> "Medical imaging powered by SecureMR (ByteDance) API"

---

### 6.3 Afference Haptic Rings Integration

**Use Case:** Provide finger-level haptic feedback when touching heart layers

**Integration Type:** SDK integration (requires Afference SDK)

**Setup:**

1. Get SDK from Afference booth at hackathon
2. Import SDK package to Unity
3. Connect rings via Bluetooth to Quest 2
4. Use SDK API in scripts

**Implementation Template:**

```csharp
// HapticFeedbackController.cs
using UnityEngine;
// using Afference.SDK;  // Import Afference SDK

public class HapticFeedbackController : MonoBehaviour
{
    // private AfferenceDevice leftHand;
    // private AfferenceDevice rightHand;

    void Start()
    {
        // Connect to Afference rings
        // leftHand = AfferenceDevice.Connect(Hand.Left);
        // rightHand = AfferenceDevice.Connect(Hand.Right);
    }

    /// <summary>
    /// Called when finger touches a heart layer
    /// </summary>
    public void OnFingerTouch(string layerName)
    {
        // Different vibration patterns for different layers
        float intensity = GetIntensityForLayer(layerName);
        float duration = 0.2f;

        // Send haptic pulse to rings
        // rightHand.SendPulse(intensity, duration);

        Debug.Log($"[Haptic] Touch feedback for {layerName}");
    }

    float GetIntensityForLayer(string layer)
    {
        // Stronger vibration for critical structures
        return layer switch
        {
            "Pericardium" => 0.3f,
            "Myocardium" => 0.5f,
            "Endocardium" => 0.7f,
            "Valves" => 0.9f,
            _ => 0.5f
        };
    }
}
```

**Trigger from VR Interaction:**

```csharp
// Add to LayerPeeler.cs or VR interaction script
void OnTriggerEnter(Collider other)
{
    if (other.CompareTag("PlayerHand"))
    {
        HapticFeedbackController haptics = FindObjectOfType<HapticFeedbackController>();
        haptics.OnFingerTouch(gameObject.name);
    }
}
```

**Sponsor Credit:**
> "Immersive haptic feedback powered by Afference haptic rings"

---

### 6.4 CapCut Integration

**Use Case:** Edit 30-second demo video for Devpost submission

**Integration Type:** Post-development (offline video editing)

**Workflow:**

```
┌─────────────────────────────────────────────────────────────┐
│ STEP 1: Record VR Gameplay                                  │
│ → Use Quest 2 screen recording (Settings → Sharing)         │
│ → OR use OBS Studio on PC (Quest Link)                      │
│ → Record 2-3 minutes of gameplay footage                    │
│ → Save as MP4 file                                           │
└─────────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 2: Import to CapCut                                     │
│ → Open CapCut desktop app                                   │
│ → Create new project (vertical 9:16 aspect ratio)           │
│ → Import gameplay footage                                    │
│ → Drag to timeline                                           │
└─────────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 3: Edit to 30 Seconds                                   │
│ → Cut out loading screens and errors                        │
│ → Highlight key moments:                                     │
│   - User pressing "Analyze ECG" button                      │
│   - Heart changing color                                     │
│   - Layer peeling animation                                  │
│   - ECG results displaying                                   │
│ → Trim to exactly 30 seconds                                │
└─────────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 4: Add Enhancements                                     │
│ → Text overlays:                                             │
│   - "HoloHuman XR"                                          │
│   - "AI-Powered ECG Analysis"                               │
│   - "Powered by Meshy.ai, SecureMR, Afference"             │
│ → Transitions between clips (fade, slide)                   │
│ → Background music (CapCut library)                         │
│ → Speed ramping for dramatic effect                         │
└─────────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 5: Export                                               │
│ → Resolution: 1080p (minimum)                               │
│ → Format: MP4                                                │
│ → Framerate: 30 FPS                                         │
│ → Upload to YouTube (required for Devpost)                  │
│ → Add link to Devpost submission                            │
└─────────────────────────────────────────────────────────────┘
```

**No Code Integration Required**

**Sponsor Credit:**
> "Demo video edited with CapCut (ByteDance)"

---

## 7. Implementation Templates

### 7.1 Flask Backend Template

**File: `Backend/ecg_api.py`**

```python
"""
HoloHuman XR - Flask Backend API
Provides ECG analysis endpoints for Unity VR frontend
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import tensorflow as tf
import time
import logging

# Initialize Flask app
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})  # Allow Unity to access

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load TensorFlow model (do this once at startup)
logger.info("Loading ECG model...")
try:
    model = tf.keras.models.load_model('automatic-ecg-diagnosis/model/model.hdf5')
    logger.info("Model loaded successfully")
except Exception as e:
    logger.error(f"Failed to load model: {e}")
    model = None

# Cardiac conditions (in model output order)
CONDITIONS = [
    '1st_degree_AV_block',
    'RBBB',
    'LBBB',
    'sinus_bradycardia',
    'atrial_fibrillation',
    'sinus_tachycardia'
]


@app.route('/api/ecg/predict', methods=['POST'])
def predict_ecg():
    """
    Analyzes ECG signal and returns cardiac condition predictions

    Request JSON:
    {
        "ecg_signal": [[...], [...], ...],  # 12 leads x 4096 samples
        "patient_id": "optional_id",
        "timestamp": 1234567890
    }

    Response JSON:
    {
        "predictions": {...},
        "top_condition": "...",
        "confidence": 0.xx,
        "processing_time_ms": 123
    }
    """
    start_time = time.time()

    try:
        # Validate request
        if not request.is_json:
            return jsonify({
                'error': 'Request must be JSON',
                'code': 'INVALID_FORMAT'
            }), 400

        data = request.get_json()

        # Extract ECG signal
        if 'ecg_signal' not in data:
            return jsonify({
                'error': 'Missing ecg_signal field',
                'code': 'MISSING_FIELD'
            }), 400

        # Convert to numpy array
        ecg_signal = np.array(data['ecg_signal'], dtype=np.float32)

        # Validate shape
        if ecg_signal.shape != (12, 4096):
            return jsonify({
                'error': f'Invalid ECG shape. Expected (12, 4096), got {ecg_signal.shape}',
                'code': 'INVALID_SHAPE'
            }), 400

        # Check for NaN/Inf
        if not np.isfinite(ecg_signal).all():
            return jsonify({
                'error': 'ECG signal contains NaN or Inf values',
                'code': 'INVALID_VALUES'
            }), 400

        # Prepare input for model (add batch dimension)
        ecg_input = np.expand_dims(ecg_signal.T, axis=0)  # Shape: (1, 4096, 12)

        # Run model inference
        logger.info(f"Running inference on ECG signal shape {ecg_input.shape}")
        predictions = model.predict(ecg_input, verbose=0)

        # Extract predictions (remove batch dimension)
        predictions_array = predictions[0]  # Shape: (6,)

        # Find top condition
        top_idx = np.argmax(predictions_array)
        top_condition = CONDITIONS[top_idx]
        confidence = float(predictions_array[top_idx])

        # Format predictions as dictionary
        predictions_dict = {
            CONDITIONS[i]: float(predictions_array[i])
            for i in range(len(CONDITIONS))
        }

        # Calculate processing time
        processing_time_ms = (time.time() - start_time) * 1000

        # Build response
        response = {
            'predictions': predictions_dict,
            'top_condition': top_condition,
            'confidence': confidence,
            'processing_time_ms': round(processing_time_ms, 2),
            'model_version': '1.0.0'
        }

        logger.info(f"Prediction: {top_condition} ({confidence:.2%}) in {processing_time_ms:.0f}ms")

        return jsonify(response), 200

    except ValueError as e:
        logger.error(f"Validation error: {e}")
        return jsonify({
            'error': str(e),
            'code': 'VALIDATION_ERROR'
        }), 400

    except Exception as e:
        logger.error(f"Inference error: {e}", exc_info=True)
        return jsonify({
            'error': 'Model inference failed',
            'details': str(e),
            'code': 'MODEL_ERROR'
        }), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Returns server health status"""
    return jsonify({
        'status': 'healthy',
        'model_loaded': model is not None,
        'version': '1.0.0'
    }), 200


@app.route('/api/conditions', methods=['GET'])
def get_conditions():
    """Returns list of all detectable conditions"""
    conditions_info = [
        {
            'id': '1st_degree_AV_block',
            'name': '1st Degree AV Block',
            'description': 'Prolonged PR interval',
            'severity': 'low'
        },
        {
            'id': 'RBBB',
            'name': 'Right Bundle Branch Block',
            'description': 'Delayed right ventricular activation',
            'severity': 'medium'
        },
        {
            'id': 'LBBB',
            'name': 'Left Bundle Branch Block',
            'description': 'Delayed left ventricular activation',
            'severity': 'medium'
        },
        {
            'id': 'sinus_bradycardia',
            'name': 'Sinus Bradycardia',
            'description': 'Heart rate < 60 BPM',
            'severity': 'low'
        },
        {
            'id': 'atrial_fibrillation',
            'name': 'Atrial Fibrillation',
            'description': 'Irregular atrial rhythm',
            'severity': 'high'
        },
        {
            'id': 'sinus_tachycardia',
            'name': 'Sinus Tachycardia',
            'description': 'Heart rate > 100 BPM',
            'severity': 'medium'
        }
    ]

    return jsonify({
        'conditions': conditions_info,
        'total': len(conditions_info)
    }), 200


if __name__ == '__main__':
    # Start Flask server
    logger.info("Starting Flask server on port 5000...")
    app.run(
        host='0.0.0.0',  # Accept connections from any IP (for Quest 2)
        port=5000,
        debug=True,      # Enable auto-reload during development
        threaded=True    # Handle multiple requests
    )
```

**To Run:**
```bash
cd Backend
venv\Scripts\activate
python ecg_api.py
```

---

### 7.2 Unity Main Controller Template

**File: `Assets/Scripts/ECGManager.cs`**

```csharp
/// <summary>
/// Main controller for ECG analysis workflow in VR
/// Coordinates between API client, visualization, and UI
/// </summary>
using System.Collections;
using UnityEngine;
using UnityEngine.XR.Interaction.Toolkit;
using TMPro;

public class ECGManager : MonoBehaviour
{
    [Header("Component References")]
    [SerializeField] private FlaskAPIClient apiClient;
    [SerializeField] private HeartVisualizer heartVisualizer;
    [SerializeField] private ECGUIDisplay uiDisplay;

    [Header("Sample Data")]
    [Tooltip("JSON file containing sample ECG data for testing")]
    [SerializeField] private TextAsset sampleECGJson;

    [Header("UI Elements")]
    [SerializeField] private TextMeshProUGUI statusText;
    [SerializeField] private GameObject loadingIndicator;

    [Header("Audio Feedback (Optional)")]
    [SerializeField] private AudioSource audioSource;
    [SerializeField] private AudioClip successSound;
    [SerializeField] private AudioClip errorSound;

    private bool isProcessing = false;

    void Start()
    {
        // Validate references
        if (apiClient == null) Debug.LogError("[ECGManager] FlaskAPIClient not assigned!");
        if (heartVisualizer == null) Debug.LogError("[ECGManager] HeartVisualizer not assigned!");
        if (uiDisplay == null) Debug.LogError("[ECGManager] ECGUIDisplay not assigned!");

        // Initial UI state
        if (statusText != null) statusText.text = "Ready";
        if (loadingIndicator != null) loadingIndicator.SetActive(false);

        Debug.Log("[ECGManager] Initialized");
    }

    /// <summary>
    /// Public method called by VR button or controller input
    /// </summary>
    public void OnAnalyzeButtonPressed()
    {
        if (isProcessing)
        {
            Debug.LogWarning("[ECGManager] Analysis already in progress");
            return;
        }

        Debug.Log("[ECGManager] Starting ECG analysis...");
        StartCoroutine(AnalyzeECGWorkflow());
    }

    /// <summary>
    /// Complete ECG analysis workflow
    /// </summary>
    private IEnumerator AnalyzeECGWorkflow()
    {
        isProcessing = true;

        // STEP 1: Show loading state
        UpdateUI("Analyzing ECG...", true);

        // STEP 2: Load ECG data
        string ecgJson = LoadECGData();
        if (string.IsNullOrEmpty(ecgJson))
        {
            HandleError("Failed to load ECG data");
            yield break;
        }

        // STEP 3: Send to backend API
        bool requestComplete = false;
        ECGResponse responseData = null;
        string errorMessage = null;

        StartCoroutine(apiClient.SendECGAnalysisRequest(
            ecgJson,
            onSuccess: (data) => {
                responseData = data;
                requestComplete = true;
            },
            onError: (error) => {
                errorMessage = error;
                requestComplete = true;
            }
        ));

        // STEP 4: Wait for response with timeout
        float elapsed = 0f;
        float timeout = 10f;  // 10 second timeout

        while (!requestComplete && elapsed < timeout)
        {
            elapsed += Time.deltaTime;

            // Update loading progress (optional)
            if (statusText != null)
            {
                int dots = (int)(elapsed * 2) % 4;
                statusText.text = "Analyzing ECG" + new string('.', dots);
            }

            yield return null;
        }

        // STEP 5: Handle response or timeout
        if (errorMessage != null)
        {
            // Error occurred
            HandleError(errorMessage);
        }
        else if (responseData != null)
        {
            // Success
            HandleSuccess(responseData);
        }
        else
        {
            // Timeout
            HandleError("Request timed out. Check Flask server.");
        }

        isProcessing = false;
    }

    /// <summary>
    /// Handles successful ECG analysis
    /// </summary>
    private void HandleSuccess(ECGResponse data)
    {
        Debug.Log($"[ECGManager] Success: {data.top_condition} ({data.confidence:P})");

        // Update UI
        UpdateUI("Analysis Complete!", false);
        if (statusText != null) statusText.color = Color.green;

        // Play success sound
        if (audioSource != null && successSound != null)
        {
            audioSource.PlayOneShot(successSound);
        }

        // Update visualizations
        if (heartVisualizer != null)
        {
            heartVisualizer.UpdateVisualization(data);
        }

        if (uiDisplay != null)
        {
            uiDisplay.DisplayResults(data);
        }

        // Trigger haptic feedback
        TriggerHapticFeedback(data.confidence);
    }

    /// <summary>
    /// Handles errors during ECG analysis
    /// </summary>
    private void HandleError(string message)
    {
        Debug.LogError($"[ECGManager] Error: {message}");

        // Update UI
        UpdateUI($"Error: {message}", false);
        if (statusText != null) statusText.color = Color.red;

        // Play error sound
        if (audioSource != null && errorSound != null)
        {
            audioSource.PlayOneShot(errorSound);
        }

        isProcessing = false;
    }

    /// <summary>
    /// Loads ECG data from file or sensor
    /// </summary>
    private string LoadECGData()
    {
        // For demo: Load from TextAsset assigned in Inspector
        if (sampleECGJson != null)
        {
            Debug.Log("[ECGManager] Loading sample ECG data from file");
            return sampleECGJson.text;
        }

        // For production: Load from real ECG device or file
        // string path = Application.persistentDataPath + "/ecg_data.json";
        // if (System.IO.File.Exists(path))
        // {
        //     return System.IO.File.ReadAllText(path);
        // }

        Debug.LogError("[ECGManager] No ECG data source configured");
        return null;
    }

    /// <summary>
    /// Updates UI elements
    /// </summary>
    private void UpdateUI(string message, bool showLoading)
    {
        if (statusText != null)
        {
            statusText.text = message;
            statusText.color = Color.white;
        }

        if (loadingIndicator != null)
        {
            loadingIndicator.SetActive(showLoading);
        }
    }

    /// <summary>
    /// Triggers VR controller haptic feedback
    /// </summary>
    private void TriggerHapticFeedback(float intensity)
    {
        // Quest 2 controller vibration
        // Intensity: 0.0 = no vibration, 1.0 = max vibration
        float hapticStrength = Mathf.Clamp01(intensity);
        float duration = 0.3f;

        // Note: Requires Meta XR SDK or Unity XR Interaction Toolkit
        // Example with Unity XR:
        // var controller = GetComponent<XRController>();
        // if (controller != null)
        // {
        //     controller.SendHapticImpulse(hapticStrength, duration);
        // }

        Debug.Log($"[ECGManager] Haptic feedback: {hapticStrength:P} for {duration}s");
    }
}
```

---

## 8. Performance Considerations

### 8.1 VR Performance Targets

**Quest 2 Requirements:**
- **Minimum FPS:** 72 FPS (13.8ms per frame)
- **Target FPS:** 90 FPS (11.1ms per frame) for smoothness
- **Maximum Frame Time:** 13.8ms (anything higher causes judder)

**Performance Budget per Frame:**
| System | Time Budget | Notes |
|--------|-------------|-------|
| Rendering | 8-10ms | Includes draw calls, shaders, post-processing |
| Scripts (Update) | 1-2ms | All MonoBehaviour Update() calls |
| Physics | 1-2ms | FixedUpdate(), collision detection |
| Network | <1ms | HTTP requests should be async (coroutines) |
| Animation | 0.5-1ms | DOTween, Animator, shader animations |
| **Total** | **<13.8ms** | **For 72 FPS** |

---

### 8.2 Optimization Techniques

#### **1. Material Property Block (CRITICAL)**

**Problem:** Changing `material.color` creates a material instance (2-4 KB + GC)

**Solution:** Use MaterialPropertyBlock

```csharp
// ❌ BAD (creates material copy every time)
GetComponent<Renderer>().material.color = Color.red;

// ✅ GOOD (reuses same material)
MaterialPropertyBlock block = new MaterialPropertyBlock();
Renderer rend = GetComponent<Renderer>();
rend.GetPropertyBlock(block);
block.SetColor("_Color", Color.red);
rend.SetPropertyBlock(block);
```

**Performance Impact:**
- Bad method: -10-15 FPS with 20 objects
- Good method: 0 FPS impact

---

#### **2. Shader Property ID Caching**

**Problem:** String lookups (`"_Color"`) are slow

**Solution:** Cache property IDs

```csharp
// ❌ BAD (string lookup every frame)
void Update() {
    material.SetFloat("_DissolveAmount", value);  // Slow!
}

// ✅ GOOD (cached int ID)
private static readonly int DissolveID = Shader.PropertyToID("_DissolveAmount");

void Update() {
    material.SetFloat(DissolveID, value);  // Fast!
}
```

**Performance Impact:** 2-3x faster property access

---

#### **3. Coroutine Best Practices**

**Problem:** Coroutines can cause frame spikes if not used correctly

**Solution:**
- Use `yield return null` to spread work across frames
- Avoid long loops in single frame
- Use `WaitForSeconds` for delays (not busy waiting)

```csharp
// ❌ BAD (blocks for entire duration)
void AnimateColor() {
    for (float t = 0; t < 1; t += 0.01f) {
        material.color = Color.Lerp(Color.red, Color.green, t);
        Thread.Sleep(16);  // Blocks main thread!
    }
}

// ✅ GOOD (non-blocking)
IEnumerator AnimateColor() {
    float elapsed = 0f;
    while (elapsed < 1f) {
        elapsed += Time.deltaTime;
        material.color = Color.Lerp(Color.red, Color.green, elapsed);
        yield return null;  // Next frame
    }
}
```

---

#### **4. DOTween vs. Coroutines**

**Performance Comparison:**

| Animation Method | Speed | GC Allocation | Ease of Use |
|------------------|-------|---------------|-------------|
| Coroutines | 1x | 40 bytes/call | Medium |
| Unity Animator | 0.8x | Variable | Easy (visual) |
| DOTween | 4x | 0 bytes (after init) | Very Easy |

**Recommendation:** Use DOTween for all animations

```csharp
// DOTween: One line, zero GC, 4x faster
transform.DOScale(1.2f, 0.5f).SetLoops(-1, LoopType.Yoyo);
```

---

#### **5. Network Request Optimization**

**Problem:** HTTP requests can block rendering if not handled properly

**Solution:**
- Always use coroutines for HTTP
- Set reasonable timeouts (5-10s)
- Cache responses when possible

```csharp
// ✅ GOOD: Async with timeout
IEnumerator SendRequest() {
    UnityWebRequest request = UnityWebRequest.Get(url);
    request.timeout = 10;  // 10 second timeout

    yield return request.SendWebRequest();  // Non-blocking

    // Process response...
}
```

**Never do this:**
```csharp
// ❌ BAD: Synchronous (blocks VR rendering!)
using (var client = new System.Net.WebClient()) {
    string response = client.DownloadString(url);  // BLOCKS!
}
```

---

#### **6. Polygon Count Limits**

**Quest 2 Recommendations:**

| Model Type | Polygon Limit | Notes |
|------------|---------------|-------|
| Hero object (heart) | 30,000-50,000 | Main focus, most detail |
| Secondary objects | 10,000-20,000 | Skeleton, organs |
| Environment | 100,000 total | Room, UI, props |
| **Scene Total** | **200,000-300,000** | **Maximum for 72 FPS** |

**Optimize 3D Models:**
1. Use Blender Decimate modifier if poly count too high
2. Remove unnecessary internal faces
3. Use normal maps for detail instead of geometry
4. Enable GPU instancing for repeated objects

---

#### **7. Texture Optimization**

**Quest 2 Texture Guidelines:**

| Use Case | Recommended Size | Format | Notes |
|----------|------------------|--------|-------|
| Heart albedo (color) | 2048x2048 | PNG/JPG | Compressed in Unity |
| Normal maps | 1024x1024 | PNG | Lower priority |
| UI textures | 512x512 | PNG | Text should be vector |
| Noise textures | 256x256 | Grayscale | For dissolve shader |

**Unity Import Settings:**
- Max Size: 2048 (for main textures)
- Compression: High Quality (ASTC 6x6)
- Generate Mip Maps: Yes (for VR)

---

#### **8. Draw Call Batching**

**Problem:** Too many draw calls = low FPS

**Solutions:**
1. **GPU Instancing:** Enable for repeated materials
2. **Material Atlasing:** Combine textures when possible
3. **Static Batching:** Mark static objects
4. **SRP Batcher:** Enable in URP settings

**Check Draw Calls:**
- Unity Editor → Window → Analysis → Frame Debugger
- Target: <100 draw calls for Quest 2

---

### 8.3 Profiling & Debugging

**Unity Profiler (Essential for VR):**

```
Window → Analysis → Profiler
```

**Key Metrics to Monitor:**
| Metric | Target | Warning | Critical |
|--------|--------|---------|----------|
| CPU Frame Time | <10ms | 10-13ms | >13ms |
| GPU Frame Time | <10ms | 10-13ms | >13ms |
| SetPass Calls | <50 | 50-100 | >100 |
| Batches | <100 | 100-200 | >200 |
| GC Allocations | 0 KB/frame | <1 KB | >1 KB |

**Profile on Device:**
1. Build to Quest 2
2. Connect via USB
3. Window → Analysis → Profiler → Remote Device
4. Select "Android Player"
5. Monitor FPS and frame time

---

## 9. Development Timeline

### Phase-by-Phase Implementation Schedule

**Total Development Time: ~18 hours**

---

### **Phase 0: Setup & Dependencies (1.5 hours)**

**Tonight (Before Main Dev Day):**

| Task | Duration | Details |
|------|----------|---------|
| Install Python dependencies | 30 min | Flask, TensorFlow, numpy |
| Download ECG model weights | 15 min | model.hdf5 (500 MB) |
| Sign up for Meshy.ai | 10 min | Create account, save API key |
| Download CapCut | 10 min | Desktop app installation |
| Install DOTween in Unity | 15 min | Asset Store download |
| Download dissolve shader | 10 min | GitHub or create basic version |

**Verification:**
- Run `pip list` → see tensorflow, flask
- Check `Backend/automatic-ecg-diagnosis/model/model.hdf5` exists
- Open Unity → Assets → DOTween folder present

---

### **Phase 1: Backend Development (3 hours)**

**Tomorrow Morning (9 AM - 12 PM):**

| Task | Duration | Details |
|------|----------|---------|
| Create ecg_api.py | 1 hour | Flask routes, model loading |
| Implement /api/ecg/predict endpoint | 45 min | Request validation, inference |
| Test with Postman | 30 min | Send test ECG data, verify response |
| Add error handling | 30 min | Try invalid inputs, check 400/500 errors |
| Document API in README | 15 min | Curl examples, JSON schemas |

**Checkpoint:** Flask server running, responds to POST with predictions

**Test Command:**
```bash
curl -X POST http://localhost:5000/api/ecg/predict \
  -H "Content-Type: application/json" \
  -d @sample_ecg.json
```

---

### **Phase 2: Unity HTTP Integration (2 hours)**

**Tomorrow Afternoon (12 PM - 2 PM):**

| Task | Duration | Details |
|------|----------|---------|
| Create FlaskAPIClient.cs | 45 min | UnityWebRequest implementation |
| Create ECGDataModels.cs | 30 min | JSON deserialization classes |
| Test API call from Unity | 30 min | Log response to console |
| Add error handling | 15 min | Timeout, connection errors |

**Checkpoint:** Unity can send HTTP request and parse JSON response

**Verification:**
```csharp
// In Unity Editor Console:
// [API] Received response: {"predictions": {...}, ...}
```

---

### **Phase 3: 3D Model Setup (2 hours)**

**Tomorrow Afternoon (2 PM - 4 PM):**

| Task | Duration | Details |
|------|----------|---------|
| Generate heart with Meshy.ai | 30 min | Submit prompt, wait, download |
| Import heart.fbx to Unity | 15 min | Drag to Assets/Models/ |
| Optimize poly count (if needed) | 30 min | Blender decimate or Unity LOD |
| Set up materials | 30 min | Apply URP shaders, test colors |
| Add to VR scene | 15 min | Position, scale, lighting |

**Checkpoint:** 3D heart model visible in VR scene, <50k polygons

---

### **Phase 4: Animation Implementation (3 hours)**

**Tomorrow Evening (4 PM - 7 PM):**

| Task | Duration | Details |
|------|----------|---------|
| Heartbeat pulse animation | 30 min | DOTween scale loop |
| MaterialPropertyBlock setup | 45 min | Create HeartMaterialController.cs |
| Color transition animation | 45 min | Lerp between health colors |
| Dissolve shader setup | 45 min | Apply to layers, test dissolve |
| LayerPeeler script | 15 min | Control dissolve amount |

**Checkpoint:** Heart pulses, changes color, layers dissolve

---

### **Phase 5: VR Interaction (2 hours)**

**Tomorrow Evening (7 PM - 9 PM):**

| Task | Duration | Details |
|------|----------|---------|
| XR Interaction Toolkit setup | 30 min | Import package, configure |
| Add VR button for ECG analysis | 30 min | World-space button |
| Grab interaction for layers | 45 min | XRGrabInteractable setup |
| Haptic feedback | 15 min | Controller vibration |

**Checkpoint:** User can press button in VR, grab heart, feel vibration

---

### **Phase 6: UI Display (1.5 hours)**

**Day 3 Morning (9 AM - 10:30 AM):**

| Task | Duration | Details |
|------|----------|---------|
| Create UI Canvas in VR | 30 min | World-space canvas setup |
| ECGUIDisplay script | 45 min | Display condition, confidence |
| Loading indicator | 15 min | Spinning icon or progress bar |

**Checkpoint:** UI shows "Sinus Bradycardia 78%" in VR

---

### **Phase 7: Integration & Testing (2 hours)**

**Day 3 Morning (10:30 AM - 12:30 PM):**

| Task | Duration | Details |
|------|----------|---------|
| Wire all components together | 45 min | ECGManager connects everything |
| End-to-end testing | 45 min | Full workflow: button → color change |
| Fix bugs | 30 min | Debug any issues |

**Checkpoint:** Complete flow works: Press button → Heart changes color

---

### **Phase 8: Polish & Optimization (2 hours)**

**Day 3 Afternoon (1 PM - 3 PM):**

| Task | Duration | Details |
|------|----------|---------|
| Performance profiling | 45 min | Check FPS, optimize if needed |
| Audio feedback | 30 min | Add success/error sounds |
| Visual polish | 30 min | Lighting, particle effects |
| Test on Quest 2 | 15 min | Build & deploy, verify 72 FPS |

---

### **Phase 9: Demo Video (1 hour)**

**Day 3 Evening (3 PM - 4 PM):**

| Task | Duration | Details |
|------|----------|---------|
| Record VR gameplay | 20 min | 2-3 minutes of footage |
| Edit in CapCut | 30 min | Cut to 30s, add text |
| Upload to YouTube | 10 min | Unlisted link for Devpost |

---

### **Phase 10: Submission (1 hour)**

**Day 4 Morning (Before Deadline):**

| Task | Duration | Details |
|------|----------|---------|
| Update README | 20 min | Add screenshots, sponsor credits |
| Create Devpost submission | 30 min | Description, video, screenshots |
| Final GitHub push | 10 min | Ensure all code committed |

---

## 10. Troubleshooting Guide

### 10.1 Common CORS Errors

#### **Problem: "CORS policy: No 'Access-Control-Allow-Origin' header"**

**Symptoms:**
- Unity request fails with CORS error
- Browser console shows CORS blocked
- Flask returns data but Unity doesn't receive it

**Solutions:**

**1. Verify Flask-CORS is installed:**
```bash
pip install flask-cors
```

**2. Check Flask CORS configuration:**
```python
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})  # Must be before routes!
```

**3. Verify CORS headers in response:**
```bash
curl -I http://localhost:5000/api/health
# Should see:
# Access-Control-Allow-Origin: *
```

**4. If still failing, add explicit headers:**
```python
from flask import make_response

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST')
    return response
```

---

### 10.2 JSON Deserialization Issues

#### **Problem: "NullReferenceException after JsonUtility.FromJson()"**

**Symptoms:**
- JSON parsing returns null
- Fields in C# class are all default values
- No error message, just null object

**Common Causes & Solutions:**

**1. Field name mismatch:**
```csharp
// ❌ WRONG (field name doesn't match JSON key)
[Serializable]
public class ECGResponse {
    public string topCondition;  // JSON has "top_condition"
}

// ✅ CORRECT (exact match)
[Serializable]
public class ECGResponse {
    public string top_condition;  // Matches JSON exactly
}
```

**2. Using properties instead of fields:**
```csharp
// ❌ WRONG (JsonUtility ignores properties)
[Serializable]
public class ECGResponse {
    public string TopCondition { get; set; }
}

// ✅ CORRECT (public fields)
[Serializable]
public class ECGResponse {
    public string top_condition;  // Field, not property
}
```

**3. Missing [Serializable] attribute:**
```csharp
// ❌ WRONG (no attribute)
public class ECGResponse {
    public string top_condition;
}

// ✅ CORRECT
[Serializable]
public class ECGResponse {
    public string top_condition;
}
```

**4. Debugging JSON parsing:**
```csharp
string json = request.downloadHandler.text;
Debug.Log($"Raw JSON: {json}");  // Check if JSON is valid

ECGResponse data = JsonUtility.FromJson<ECGResponse>(json);
if (data == null) {
    Debug.LogError("JSON parsing returned null!");
} else {
    Debug.Log($"Parsed: {data.top_condition}");
}
```

**5. For complex JSON, use Newtonsoft.Json:**
```csharp
// If JsonUtility can't handle it, use this:
using Newtonsoft.Json;

ECGResponse data = JsonConvert.DeserializeObject<ECGResponse>(json);
```

---

### 10.3 VR Performance Problems

#### **Problem: "Low FPS in VR headset (< 72 FPS)"**

**Diagnosis Steps:**

**1. Check Unity Profiler:**
```
Window → Analysis → Profiler
Connect to Quest 2 via USB
Select "Android Player" in Profiler
```

**2. Identify bottleneck:**

| High Time in Profiler | Likely Cause | Solution |
|----------------------|--------------|----------|
| `Rendering.Draw` | Too many draw calls | Enable GPU instancing, reduce objects |
| `Scripts.Update` | Heavy Update() loops | Move code to FixedUpdate or events |
| `Physics.Processing` | Too many colliders | Disable unnecessary physics |
| `UI.Canvas` | Complex UI | Separate canvases, disable when hidden |
| `Animation.Animator` | Heavy animation | Use DOTween instead of Animator |

**Common Solutions:**

**1. Reduce polygon count:**
```csharp
// Check poly count in Unity:
// Select model → Inspector → Vertices/Triangles
// Target: <50k for main object
```

**2. Optimize materials:**
```csharp
// ❌ Creating material copies
GetComponent<Renderer>().material.color = Color.red;

// ✅ Using MaterialPropertyBlock
MaterialPropertyBlock block = new MaterialPropertyBlock();
Renderer rend = GetComponent<Renderer>();
rend.GetPropertyBlock(block);
block.SetColor("_Color", Color.red);
rend.SetPropertyBlock(block);
```

**3. Disable expensive features:**
- Shadows: Quality Settings → Shadows → Disable
- Post-processing: Turn off bloom, color grading
- Reflection probes: Disable or bake

**4. Enable SRP Batcher:**
```
Edit → Project Settings → Graphics
→ Select URP Renderer
→ Enable "SRP Batcher"
```

**5. Target 72 FPS in build:**
```csharp
// In startup script:
Application.targetFrameRate = 72;
QualitySettings.vSyncCount = 0;  // VR handles vsync
```

---

### 10.4 Quest 2 Specific Gotchas

#### **Problem: "Works in Unity Editor but not on Quest 2"**

**Common Issues:**

**1. Shaders not compatible:**
- Built-in shaders don't work on Quest 2
- **Solution:** Use URP shaders only
```
Material → Shader → Universal Render Pipeline → Lit
```

**2. Build settings incorrect:**
- **Solution:** Verify Android build settings
```
File → Build Settings → Android
Texture Compression: ASTC
Graphics API: OpenGLES3 (or Vulkan)
```

**3. Missing permissions:**
- **Solution:** Add required permissions
```
Edit → Project Settings → Player → Android
Internet Access: Required
```

**4. XR Plugin not configured:**
- **Solution:** Enable Oculus/OpenXR
```
Edit → Project Settings → XR Plug-in Management
→ Check "Oculus" or "OpenXR"
```

---

#### **Problem: "Controllers not working in build"**

**Diagnosis:**
1. Check XR Interaction Toolkit is imported
2. Verify XR Rig is in scene
3. Check Input Actions are configured

**Solution:**
```
Window → Package Manager → XR Interaction Toolkit → Install
Add XR Origin prefab to scene
Add XR Interaction Manager to scene
```

---

#### **Problem: "Haptics not working"**

**Check:**
1. Using correct controller API (OVRInput or XRController)
2. Controller is detected in VR

**Solution:**
```csharp
// Unity XR:
using UnityEngine.XR;

InputDevice controller = InputDevices.GetDeviceAtXRNode(XRNode.RightHand);
if (controller.isValid) {
    controller.SendHapticImpulse(0, 0.5f, 0.3f);
}

// OR Meta XR:
// OVRInput.SetControllerVibration(1, 0.5f, OVRInput.Controller.RTouch);
```

---

### 10.5 Network Connection Issues

#### **Problem: "Unity can't connect to Flask (Connection refused)"**

**Diagnosis Checklist:**

**1. Is Flask running?**
```bash
# Should see: "Running on http://0.0.0.0:5000"
python ecg_api.py
```

**2. Is firewall blocking?**
```bash
# Windows: Allow Python through firewall
# Control Panel → Windows Defender Firewall → Allow an app
```

**3. Correct IP address?**
```csharp
// For local testing:
private string apiUrl = "http://localhost:5000";

// For Quest 2 over WiFi:
private string apiUrl = "http://192.168.1.XXX:5000";  // Your PC's IP
```

**4. Find your PC's IP:**
```bash
# Windows:
ipconfig
# Look for "IPv4 Address" under active network adapter

# Example: 192.168.1.105
```

**5. Update Unity API URL:**
```csharp
[SerializeField] private string apiBaseUrl = "http://192.168.1.105:5000";
```

**6. Test from Quest 2 browser:**
- Open browser on Quest 2
- Navigate to `http://YOUR_PC_IP:5000/api/health`
- Should see: `{"status": "healthy", ...}`

---

#### **Problem: "Request times out after 10 seconds"**

**Possible Causes:**
1. Model inference too slow
2. Network congestion
3. Flask not responding

**Solutions:**

**1. Increase timeout:**
```csharp
request.timeout = 30;  // 30 seconds instead of 10
```

**2. Optimize model inference:**
```python
# Use model.predict with batch_size=1
predictions = model.predict(ecg_input, batch_size=1, verbose=0)
```

**3. Add response streaming:**
```python
# For very slow models, send intermediate updates
# (Advanced: requires WebSockets or Server-Sent Events)
```

---

### 10.6 Model Inference Errors

#### **Problem: "TensorFlow error: Invalid input shape"**

**Error Message:**
```
ValueError: Input 0 of layer sequential is incompatible with the layer:
expected shape=(None, 4096, 12), found shape=(12, 4096)
```

**Solution:**
```python
# Check ECG signal shape
ecg_signal = np.array(data['ecg_signal'])
print(f"Shape before: {ecg_signal.shape}")  # Should be (12, 4096)

# Transpose if needed
if ecg_signal.shape == (12, 4096):
    ecg_signal = ecg_signal.T  # Now (4096, 12)

# Add batch dimension
ecg_input = np.expand_dims(ecg_signal, axis=0)  # Now (1, 4096, 12)

# Run inference
predictions = model.predict(ecg_input)
```

---

#### **Problem: "Model predictions are all NaN or very small"**

**Diagnosis:**
1. Check input data range
2. Verify model expects normalized inputs

**Solution:**
```python
# Normalize ECG signal
ecg_signal = np.array(data['ecg_signal'], dtype=np.float32)

# Check range
print(f"Min: {ecg_signal.min()}, Max: {ecg_signal.max()}")

# Normalize to [-1, 1] or [0, 1] if needed
# ecg_signal = (ecg_signal - ecg_signal.mean()) / ecg_signal.std()

# Run inference
predictions = model.predict(ecg_input)
print(f"Predictions: {predictions}")  # Should be [0, 1] range
```

---

## Summary Checklist

### Before Tomorrow's Main Dev:

**Tonight (30-45 minutes):**
- [ ] Install Python dependencies (Flask, TensorFlow)
- [ ] Download ECG model weights (model.hdf5)
- [ ] Sign up for Meshy.ai
- [ ] Download CapCut
- [ ] Create Backend folder structure

### Tomorrow's Critical Path:

**Phase 1: Backend (3 hours)**
- [ ] Create ecg_api.py with Flask routes
- [ ] Test with Postman
- [ ] Verify CORS working

**Phase 2: Unity HTTP (2 hours)**
- [ ] Create FlaskAPIClient.cs
- [ ] Test JSON deserialization
- [ ] Log response in console

**Phase 3: 3D Model (2 hours)**
- [ ] Generate heart with Meshy.ai
- [ ] Import to Unity
- [ ] Optimize if needed

**Phase 4: Animations (3 hours)**
- [ ] Heartbeat pulse (DOTween)
- [ ] Color transitions (MaterialPropertyBlock)
- [ ] Layer dissolve shader

**Phase 5: VR Integration (2 hours)**
- [ ] Add XR Interaction Toolkit
- [ ] VR button for ECG analysis
- [ ] Grab interactions

**Phase 6: Final Integration (2 hours)**
- [ ] Wire ECGManager
- [ ] End-to-end testing
- [ ] Performance check (72 FPS)

### Day 3: Polish & Submit

**Morning:**
- [ ] UI display in VR
- [ ] Bug fixes
- [ ] Audio feedback

**Afternoon:**
- [ ] Record demo video
- [ ] Edit in CapCut
- [ ] Create Devpost submission

---

**Total Implementation Time:** ~18-20 hours
**Buffer Time:** 6-8 hours for debugging/sleep
**Demo Video:** 1 hour
**Submission:** 1 hour

**This leaves you with a complete, working VR medical visualization MVP!**

---

## Document Change Log

| Date | Version | Changes |
|------|---------|---------|
| 2025-11-15 03:00 AM | 1.0.0 | Initial documentation created |

---

## Quick Reference

**Key Files:**
- Backend: `Backend/ecg_api.py`
- Unity HTTP: `Assets/Scripts/FlaskAPIClient.cs`
- Main Controller: `Assets/Scripts/ECGManager.cs`
- Animations: `Assets/Scripts/HeartVisualizer.cs`
- Data Models: `Assets/Scripts/ECGDataModels.cs`

**Key URLs:**
- Flask API: `http://localhost:5000/api/ecg/predict`
- Meshy.ai: `https://www.meshy.ai/`
- CapCut: `https://www.capcut.com/`

**Key Technologies:**
- Backend: Flask + TensorFlow + NumPy
- Frontend: Unity + C# + DOTween + XR Interaction Toolkit
- Communication: HTTP POST with JSON
- VR Platform: Meta Quest 2

**Performance Targets:**
- FPS: 72 minimum (Quest 2)
- Frame Time: <13.8ms
- Polygons: <50k for main model
- Draw Calls: <100

---

**End of Backend-Frontend Connection Documentation**