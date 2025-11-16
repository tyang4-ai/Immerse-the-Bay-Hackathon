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
// API Response Models
// ============================================================================
// All API response structures are now defined in ECGDataStructures.cs
// (removed duplicate definitions to avoid compilation errors)
