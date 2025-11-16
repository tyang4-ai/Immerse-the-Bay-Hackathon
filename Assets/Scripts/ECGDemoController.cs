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
        apiClient = ECGAPIClient.Instance;
        statusText.text = "Loading ECG data...";

        LoadECGData();
        StartCoroutine(AnalyzeECG());
    }

    void LoadECGData()
    {
        // Parse JSON
        var wrapper = JsonUtility.FromJson<ECGWrapper>("{\"data\":" + ecgDataFile.text + "}");
        var data = wrapper.data;

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

        statusText.text = $"Loaded {samples} samples × {leads} leads";
        Debug.Log($"ECG loaded: {samples} samples × {leads} leads");
    }

    IEnumerator AnalyzeECG()
    {
        statusText.text = "Analyzing ECG...";

        yield return apiClient.AnalyzeECG(
            ecgSignal,
            outputMode: "clinical_expert",
            onSuccess: (response) =>
            {
                // Display results
                diagnosisText.text = $"<b>{response.diagnosis.top_condition}</b>\n" +
                                    $"Confidence: {response.diagnosis.confidence:P0}";

                heartRateText.text = $"<b>{response.heart_rate.bpm:F1} BPM</b>\n" +
                                    $"Lead: {response.heart_rate.lead_used} (Quality: {response.heart_rate.lead_quality:F2})";

                statusText.text = $"✓ Analysis complete ({response.processing_time_ms:F0}ms)";

                Debug.Log("=== ECG Analysis Results ===");
                Debug.Log($"Diagnosis: {response.diagnosis.top_condition} ({response.diagnosis.confidence:P0})");
                Debug.Log($"Heart Rate: {response.heart_rate.bpm:F1} BPM");
                Debug.Log($"Processing Time: {response.processing_time_ms:F1}ms");
                Debug.Log("\nClinical Interpretation:");
                Debug.Log(response.clinical_interpretation);
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
