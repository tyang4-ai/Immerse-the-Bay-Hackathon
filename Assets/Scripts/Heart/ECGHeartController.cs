using UnityEngine;
using System.Collections;
using System.Collections.Generic;
using TMPro;

/// <summary>
/// Main controller orchestrating ECG analysis and heart visualization
/// Connects backend API responses to Unity heart model
/// Handles ECG data loading, analysis requests, and UI updates
/// </summary>
public class ECGHeartController : MonoBehaviour
{
    [Header("API Client")]
    [SerializeField] private ECGAPIClient apiClient;

    [Header("ECG Data")]
    [Tooltip("Drag sample ECG JSON file from Resources folder")]
    [SerializeField] private TextAsset ecgDataFile; // e.g., sample_normal.json

    [Header("Heart Visualization")]
    [SerializeField] private HeartRegionMapping regionMapping;
    [SerializeField] private ElectricalWaveAnimator waveAnimator;
    [SerializeField] private ECGColorGlowAnimator colorGlowAnimator;

    [Header("UI Elements")]
    [SerializeField] private TMPro.TextMeshProUGUI diagnosisText;
    [SerializeField] private TMPro.TextMeshProUGUI heartRateText;
    [SerializeField] private TMPro.TextMeshProUGUI statusText;
    [SerializeField] private TMPro.TextMeshProUGUI interpretationText;

    [Header("Settings")]
    [SerializeField] private string outputMode = "clinical_expert"; // or "storytelling"
    [SerializeField] private bool autoAnalyzeOnStart = true;

    // ECG signal data (4096 samples × 12 leads)
    private float[,] ecgSignal;

    // Cached API response
    private ECGAnalysisResponse lastResponse;

    void Start()
    {
        // Get API client if not assigned
        if (apiClient == null)
            apiClient = ECGAPIClient.Instance;

        // Validate components
        if (regionMapping == null)
            Debug.LogError("[ECGHeartController] HeartRegionMapping not assigned!");

        if (waveAnimator == null)
            Debug.LogWarning("[ECGHeartController] ElectricalWaveAnimator not assigned - animations disabled");

        // Load ECG data and optionally analyze
        if (ecgDataFile != null)
        {
            LoadECGData();

            if (autoAnalyzeOnStart)
            {
                StartCoroutine(AnalyzeAndVisualize());
            }
        }
        else
        {
            Debug.LogError("[ECGHeartController] No ECG data file assigned!");
            UpdateStatus("No ECG data loaded", Color.red);
        }
    }

    /// <summary>
    /// Load ECG data from JSON TextAsset
    /// Expected format: {"ecg_signal": [[...], [...], ...]}
    /// </summary>
    void LoadECGData()
    {
        try
        {
            UpdateStatus("Loading ECG data...", Color.yellow);

            // Parse JSON directly (synthetic ECG files already have correct format)
            ECGData data = Newtonsoft.Json.JsonConvert.DeserializeObject<ECGData>(ecgDataFile.text);

            if (data == null || data.ecg_signal == null)
            {
                Debug.LogError("[ECGHeartController] Failed to parse ECG JSON");
                UpdateStatus("Failed to parse ECG data", Color.red);
                return;
            }

            // Validate dimensions
            int samples = data.ecg_signal.Count;
            int leads = data.ecg_signal.Count > 0 ? data.ecg_signal[0].Count : 0;

            if (samples != 4096 || leads != 12)
            {
                Debug.LogError($"[ECGHeartController] Invalid ECG shape: ({samples}, {leads}). Expected (4096, 12)");
                UpdateStatus($"Invalid ECG shape: ({samples}, {leads})", Color.red);
                return;
            }

            // Convert to 2D array
            ecgSignal = new float[samples, leads];
            for (int i = 0; i < samples; i++)
            {
                for (int j = 0; j < leads; j++)
                {
                    ecgSignal[i, j] = data.ecg_signal[i][j];
                }
            }

            Debug.Log($"[ECGHeartController] ECG loaded: {samples} samples × {leads} leads");
            UpdateStatus($"Loaded {samples} samples × {leads} leads", Color.green);
        }
        catch (System.Exception e)
        {
            Debug.LogError($"[ECGHeartController] Error loading ECG data: {e.Message}");
            UpdateStatus("Error loading ECG data", Color.red);
        }
    }

    /// <summary>
    /// Analyze ECG and update heart visualization
    /// Main integration point with backend API
    /// </summary>
    public IEnumerator AnalyzeAndVisualize()
    {
        if (ecgSignal == null)
        {
            Debug.LogError("[ECGHeartController] No ECG data loaded");
            yield break;
        }

        UpdateStatus("Analyzing ECG...", Color.yellow);

        // Call backend API
        yield return apiClient.AnalyzeECG(
            ecgSignal,
            outputMode: outputMode,
            regionFocus: null, // Set to specific region for storytelling drill-down
            onSuccess: (response) =>
            {
                lastResponse = response;

                // Update diagnosis UI
                UpdateDiagnosis(response.diagnosis);

                // Update heart rate UI
                UpdateHeartRate(response.heart_rate);

                // Start ECG color/glow visualization with actual waveform
                if (colorGlowAnimator != null && ecgSignal != null)
                {
                    // Play ECG waveform visualization
                    colorGlowAnimator.PlayECGVisualization(ecgSignal, leadIndex: 1); // Lead II

                    // Highlight beats with flash effect
                    if (response.heart_rate.beat_timestamps != null && response.heart_rate.beat_timestamps.Count > 0)
                    {
                        colorGlowAnimator.HighlightBeats(response.heart_rate.beat_timestamps);
                    }
                }

                // Update region colors based on health data
                UpdateRegionVisualization(response.region_health);

                // Animate electrical wave propagation
                if (waveAnimator != null && response.activation_sequence != null)
                {
                    StartCoroutine(waveAnimator.AnimateActivationSequence(
                        response.activation_sequence,
                        regionMapping
                    ));
                }

                // Display clinical interpretation
                if (!string.IsNullOrEmpty(response.clinical_interpretation))
                {
                    UpdateInterpretation(response.clinical_interpretation);
                }

                UpdateStatus($"✓ Analysis complete ({response.processing_time_ms:F0}ms)", Color.green);

                Debug.Log($"[ECGHeartController] Analysis complete: {response.diagnosis.top_condition} ({response.diagnosis.confidence:P0})");
            },
            onError: (error) =>
            {
                UpdateStatus("✗ Analysis failed", Color.red);
                Debug.LogError($"[ECGHeartController] ECG Analysis failed: {error}");

                if (diagnosisText != null)
                    diagnosisText.text = $"<color=red>Error:</color>\n{error}";
            }
        );
    }

    /// <summary>
    /// Update diagnosis UI with result
    /// </summary>
    void UpdateDiagnosis(DiagnosisData diagnosis)
    {
        if (diagnosisText == null) return;

        // Format diagnosis text
        string conditionName = FormatConditionName(diagnosis.top_condition);
        string confidencePercent = (diagnosis.confidence * 100f).ToString("F0");

        diagnosisText.text = $"<b>{conditionName}</b>\nConfidence: {confidencePercent}%";

        // Color-code based on severity
        Color diagnosisColor = GetSeverityColor(diagnosis.confidence);
        diagnosisText.color = diagnosisColor;

        Debug.Log($"[ECGHeartController] Diagnosis: {conditionName} ({confidencePercent}%)");
    }

    /// <summary>
    /// Update heart rate UI
    /// </summary>
    void UpdateHeartRate(HeartRateData heartRate)
    {
        if (heartRateText == null) return;

        heartRateText.text = $"<b>{heartRate.bpm:F1} BPM</b>\n" +
                            $"Lead: {heartRate.lead_used} (Quality: {heartRate.lead_quality:F2})";

        // Color-code BPM based on range
        Color bpmColor = Color.white;
        if (heartRate.bpm < 60)
            bpmColor = new Color(0.5f, 0.7f, 1f); // Light blue (bradycardia)
        else if (heartRate.bpm > 100)
            bpmColor = new Color(1f, 0.5f, 0.5f); // Light red (tachycardia)
        else
            bpmColor = Color.green; // Normal

        heartRateText.color = bpmColor;

        Debug.Log($"[ECGHeartController] Heart Rate: {heartRate.bpm:F1} BPM (Lead {heartRate.lead_used})");
    }

    /// <summary>
    /// Update clinical interpretation text
    /// </summary>
    void UpdateInterpretation(string interpretation)
    {
        if (interpretationText == null) return;

        interpretationText.text = interpretation;
        Debug.Log($"[ECGHeartController] Interpretation: {interpretation.Substring(0, Mathf.Min(100, interpretation.Length))}...");
    }

    /// <summary>
    /// Update all region visualizations based on health data from backend
    /// </summary>
    void UpdateRegionVisualization(Dictionary<string, RegionHealthData> regionHealthData)
    {
        if (regionMapping == null)
        {
            Debug.LogWarning("[ECGHeartController] HeartRegionMapping not assigned, cannot update regions");
            return;
        }

        // Use HeartRegionMapping to update all regions at once
        regionMapping.UpdateAllRegions(regionHealthData);

        Debug.Log($"[ECGHeartController] Updated {regionHealthData.Count} cardiac regions");
    }

    /// <summary>
    /// Update status text with color
    /// </summary>
    void UpdateStatus(string message, Color color)
    {
        if (statusText != null)
        {
            statusText.text = message;
            statusText.color = color;
        }
    }

    /// <summary>
    /// Format condition name for display (convert snake_case to Title Case)
    /// </summary>
    string FormatConditionName(string conditionName)
    {
        if (string.IsNullOrEmpty(conditionName))
            return "Unknown";

        // Replace underscores with spaces and capitalize
        string formatted = conditionName.Replace("_", " ");

        // Simple title case (capitalize first letter of each word)
        System.Globalization.TextInfo textInfo = new System.Globalization.CultureInfo("en-US", false).TextInfo;
        formatted = textInfo.ToTitleCase(formatted);

        return formatted;
    }

    /// <summary>
    /// Get color based on severity/confidence
    /// </summary>
    Color GetSeverityColor(float severity)
    {
        if (severity < 0.3f)
            return Color.green;
        else if (severity < 0.6f)
            return Color.yellow;
        else if (severity < 0.8f)
            return new Color(1f, 0.5f, 0f); // Orange
        else
            return Color.red;
    }

    /// <summary>
    /// Public method to switch ECG samples
    /// </summary>
    public void LoadAndAnalyze(TextAsset newEcgData)
    {
        ecgDataFile = newEcgData;
        LoadECGData();
        StartCoroutine(AnalyzeAndVisualize());
    }

    /// <summary>
    /// Public method to re-analyze current ECG with different mode
    /// </summary>
    public void ReanalyzeWithMode(string mode)
    {
        outputMode = mode;
        StartCoroutine(AnalyzeAndVisualize());
    }

    /// <summary>
    /// Reset heart visualization to healthy state
    /// </summary>
    public void ResetVisualization()
    {
        if (regionMapping != null)
        {
            regionMapping.ResetAllRegions();
        }

        if (diagnosisText != null)
            diagnosisText.text = "No analysis";

        if (heartRateText != null)
            heartRateText.text = "-- BPM";

        if (interpretationText != null)
            interpretationText.text = "";

        UpdateStatus("Ready", Color.white);
    }
    /// <summary>
    /// Get the loaded ECG signal data
    /// Used by other controllers (e.g., StorytellingJourneyController) to access ECG data
    /// </summary>
    public float[,] GetECGSignal()
    {
        return ecgSignal;
    }

}

// ECGDataWrapper and ECGData classes are now defined in ECGDataStructures.cs
// (removed duplicate definitions)
