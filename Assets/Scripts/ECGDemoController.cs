using UnityEngine;
using System.Collections;
using System.Collections.Generic;
using TMPro;

public class ECGDemoController : MonoBehaviour
{
    [Header("ECG Data")]
    public TextAsset ecgDataFile;  // Drag sample_normal.json here

    [Header("UI")]
    public TMPro.TextMeshProUGUI diagnosisText;
    public TMPro.TextMeshProUGUI heartRateText;
    public TMPro.TextMeshProUGUI statusText;

    private ECGAPIClient apiClient;
    private float[,] ecgSignal;

    void Start()
    {
        Debug.Log("[ECGDemoController] Start() called");

        // Check if UI elements are assigned
        if (diagnosisText == null || heartRateText == null || statusText == null)
        {
            Debug.LogError("[ECGDemoController] UI elements not assigned in Inspector!");
            return;
        }

        // Check if ECG data file is assigned
        if (ecgDataFile == null)
        {
            Debug.LogError("[ECGDemoController] ECG Data File not assigned in Inspector!");
            statusText.text = "ERROR: No ECG file assigned";
            return;
        }

        statusText.text = "Initializing...";
        Debug.Log("[ECGDemoController] Waiting for API client...");

        // Wait for ECGAPIClient to be ready
        StartCoroutine(WaitForAPIClient());
    }

    IEnumerator WaitForAPIClient()
    {
        // Wait up to 5 seconds for ECGAPIClient to initialize
        float timeout = 5f;
        float elapsed = 0f;

        while (ECGAPIClient.Instance == null && elapsed < timeout)
        {
            yield return new WaitForSeconds(0.1f);
            elapsed += 0.1f;
        }

        if (ECGAPIClient.Instance == null)
        {
            Debug.LogError("[ECGDemoController] ECGAPIClient not found! Make sure ECGAPIClient GameObject exists in scene.");
            statusText.text = "ERROR: API Client not found";
            yield break;
        }

        apiClient = ECGAPIClient.Instance;
        Debug.Log("[ECGDemoController] API client found!");

        statusText.text = "Loading ECG data...";
        LoadECGData();

        if (ecgSignal != null)
        {
            StartCoroutine(AnalyzeECG());
        }
    }

    void LoadECGData()
    {
        Debug.Log("[ECGDemoController] Loading ECG data from file...");

        try
        {
            // Parse JSON - synthetic ECG files have direct {"ecg_signal": [...]} format
            // Use Newtonsoft.Json for better parsing
            var data = Newtonsoft.Json.JsonConvert.DeserializeObject<ECGData>(ecgDataFile.text);

            if (data == null || data.ecg_signal == null)
            {
                throw new System.Exception("Failed to parse ECG data - null result");
            }

            int samples = data.ecg_signal.Count;
            int leads = data.ecg_signal[0].Count;

            Debug.Log($"[ECGDemoController] Parsing {samples} samples × {leads} leads...");

            ecgSignal = new float[samples, leads];
            for (int i = 0; i < samples; i++)
            {
                for (int j = 0; j < leads; j++)
                {
                    ecgSignal[i, j] = data.ecg_signal[i][j];
                }
            }

            statusText.text = $"Loaded {samples} samples × {leads} leads";
            Debug.Log($"[ECGDemoController] ✓ ECG loaded successfully: {samples} samples × {leads} leads");
        }
        catch (System.Exception e)
        {
            Debug.LogError($"[ECGDemoController] Failed to load ECG data: {e.Message}");
            Debug.LogError($"[ECGDemoController] Stack trace: {e.StackTrace}");
            statusText.text = "ERROR: Failed to load ECG data";
            ecgSignal = null;
        }
    }

    IEnumerator AnalyzeECG()
    {
        Debug.Log("[ECGDemoController] Starting ECG analysis...");
        statusText.text = "Analyzing ECG...";

        if (apiClient == null)
        {
            Debug.LogError("[ECGDemoController] API client is null!");
            statusText.text = "ERROR: API client missing";
            yield break;
        }

        if (ecgSignal == null)
        {
            Debug.LogError("[ECGDemoController] ECG signal is null!");
            statusText.text = "ERROR: ECG data missing";
            yield break;
        }

        yield return apiClient.AnalyzeECG(
            ecgSignal,
            outputMode: "clinical_expert",
            onSuccess: (response) =>
            {
                try
                {
                    Debug.Log("[ECGDemoController] ✓ SUCCESS callback received!");
                    Debug.Log($"[ECGDemoController] Response type: {response.GetType().Name}");

                    // Display results
                    Debug.Log("[ECGDemoController] Setting diagnosis text...");
                    diagnosisText.text = $"<b>{response.diagnosis.top_condition}</b>\n" +
                                        $"Confidence: {response.diagnosis.confidence:P0}";

                    Debug.Log("[ECGDemoController] Setting heart rate text...");
                    heartRateText.text = $"<b>{response.heart_rate.bpm:F1} BPM</b>\n" +
                                        $"Lead: {response.heart_rate.lead_used}";

                    Debug.Log("[ECGDemoController] Setting status text...");
                    statusText.text = $"Analysis complete ({response.processing_time_ms:F0}ms)";

                    Debug.Log("=== ECG Analysis Results ===");
                    Debug.Log($"Diagnosis: {response.diagnosis.top_condition} ({response.diagnosis.confidence:P0})");
                    Debug.Log($"Heart Rate: {response.heart_rate.bpm:F1} BPM");
                    Debug.Log($"Processing Time: {response.processing_time_ms:F1}ms");
                    Debug.Log("\nClinical Interpretation:");
                    Debug.Log(response.clinical_interpretation);
                }
                catch (System.Exception e)
                {
                    Debug.LogError($"[ECGDemoController] Exception in onSuccess callback: {e.Message}");
                    Debug.LogError($"[ECGDemoController] Stack trace: {e.StackTrace}");
                    statusText.text = $"ERROR in callback: {e.Message}";
                }
            },
            onError: (error) =>
            {
                statusText.text = "✗ Analysis failed";
                diagnosisText.text = $"<color=red>Error:</color>\n{error}";
                Debug.LogError($"ECG Analysis failed: {error}");
            }
        );
    }
}

// ECGWrapper and ECGData classes are now defined in ECGDataStructures.cs
// (removed duplicate definitions)
