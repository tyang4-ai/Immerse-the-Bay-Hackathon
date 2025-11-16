using UnityEngine;
using UnityEngine.UI;
using TMPro;
using System.Collections.Generic;

/// <summary>
/// Displays detailed information for a single heartbeat
/// Shows P-QRS-T intervals, waveform components, and annotations
/// Optionally visualizes waveform using LineRenderer
/// </summary>
public class BeatDetailPanel : MonoBehaviour
{
    [Header("UI Text Elements")]
    [SerializeField] private TMPro.TextMeshProUGUI beatIndexText;
    [SerializeField] private TMPro.TextMeshProUGUI prIntervalText;
    [SerializeField] private TMPro.TextMeshProUGUI qrsDurationText;
    [SerializeField] private TMPro.TextMeshProUGUI qtIntervalText;
    [SerializeField] private TMPro.TextMeshProUGUI annotationsText;
    [SerializeField] private TMPro.TextMeshProUGUI leadUsedText;

    [Header("Waveform Visualization (Optional)")]
    [SerializeField] private LineRenderer waveformLine;
    [SerializeField] private float waveformHeight = 100f;
    [SerializeField] private float waveformWidth = 400f;
    [SerializeField] private bool showWaveform = true;

    [Header("Component Highlights")]
    [SerializeField] private Image pWaveHighlight;
    [SerializeField] private Image qrsHighlight;
    [SerializeField] private Image tWaveHighlight;

    /// <summary>
    /// Display beat detail from backend response
    /// </summary>
    public void DisplayBeatDetail(BeatDetailResponse response)
    {
        if (response == null)
        {
            Debug.LogError("[BeatDetailPanel] Response is null");
            return;
        }

        // Display beat index
        if (beatIndexText != null)
        {
            beatIndexText.text = $"Beat #{response.beat_index}";
        }

        // Display intervals
        if (response.intervals != null)
        {
            if (prIntervalText != null)
                prIntervalText.text = $"PR Interval: {response.intervals.pr_interval_ms:F1} ms";

            if (qrsDurationText != null)
            {
                string qrsText = $"QRS Duration: {response.intervals.qrs_duration_ms:F1} ms";

                // Highlight if wide QRS
                if (response.intervals.qrs_duration_ms > 120f)
                {
                    qrsText += " <color=red>(Wide)</color>";
                }

                qrsDurationText.text = qrsText;
            }

            if (qtIntervalText != null)
                qtIntervalText.text = $"QT Interval: {response.intervals.qt_interval_ms:F1} ms";
        }

        // Display annotations
        if (annotationsText != null && response.annotations != null && response.annotations.Count > 0)
        {
            string annotationsStr = string.Join("\n• ", response.annotations);
            annotationsText.text = "• " + annotationsStr;
        }
        else if (annotationsText != null)
        {
            annotationsText.text = "No abnormalities detected";
        }

        // Display lead used
        if (leadUsedText != null)
        {
            leadUsedText.text = $"Lead: {response.lead_used}";
        }

        // Visualize waveform if enabled
        if (showWaveform && response.raw_samples != null)
        {
            VisualizeWaveform(response);
        }

        // Highlight waveform components
        HighlightComponents(response.waveform_components);

        Debug.Log($"[BeatDetailPanel] Displayed detail for beat #{response.beat_index}");
    }

    /// <summary>
    /// Visualize ECG waveform using LineRenderer
    /// </summary>
    void VisualizeWaveform(BeatDetailResponse response)
    {
        if (waveformLine == null || response.raw_samples == null || response.raw_samples.lead_II == null)
        {
            return;
        }

        List<float> samples = response.raw_samples.lead_II;
        int sampleCount = samples.Count;

        if (sampleCount == 0) return;

        // Configure LineRenderer
        waveformLine.positionCount = sampleCount;

        // Find min/max for scaling
        float minVal = float.MaxValue;
        float maxVal = float.MinValue;

        foreach (float sample in samples)
        {
            if (sample < minVal) minVal = sample;
            if (sample > maxVal) maxVal = sample;
        }

        float range = maxVal - minVal;
        if (range < 0.001f) range = 1f; // Avoid division by zero

        // Set positions
        for (int i = 0; i < sampleCount; i++)
        {
            float x = (i / (float)(sampleCount - 1)) * waveformWidth;
            float normalizedY = (samples[i] - minVal) / range;
            float y = normalizedY * waveformHeight;

            waveformLine.SetPosition(i, new Vector3(x, y, 0f));
        }

        Debug.Log($"[BeatDetailPanel] Visualized waveform with {sampleCount} samples");
    }

    /// <summary>
    /// Highlight P-QRS-T waveform components with colors
    /// </summary>
    void HighlightComponents(WaveformComponents components)
    {
        if (components == null) return;

        // P Wave - Blue
        if (pWaveHighlight != null && components.p_wave != null)
        {
            pWaveHighlight.color = new Color(0.3f, 0.6f, 1f, 0.5f); // Light blue
            pWaveHighlight.gameObject.SetActive(true);
        }

        // QRS Complex - Red
        if (qrsHighlight != null && components.qrs_complex != null)
        {
            qrsHighlight.color = new Color(1f, 0.3f, 0.3f, 0.5f); // Light red
            qrsHighlight.gameObject.SetActive(true);
        }

        // T Wave - Green
        if (tWaveHighlight != null && components.t_wave != null)
        {
            tWaveHighlight.color = new Color(0.3f, 1f, 0.3f, 0.5f); // Light green
            tWaveHighlight.gameObject.SetActive(true);
        }
    }

    /// <summary>
    /// Hide the beat detail panel
    /// </summary>
    public void Hide()
    {
        gameObject.SetActive(false);
    }

    /// <summary>
    /// Show the beat detail panel
    /// </summary>
    public void Show()
    {
        gameObject.SetActive(true);
    }

    /// <summary>
    /// Clear all displayed data
    /// </summary>
    public void Clear()
    {
        if (beatIndexText != null) beatIndexText.text = "No beat selected";
        if (prIntervalText != null) prIntervalText.text = "PR Interval: --";
        if (qrsDurationText != null) qrsDurationText.text = "QRS Duration: --";
        if (qtIntervalText != null) qtIntervalText.text = "QT Interval: --";
        if (annotationsText != null) annotationsText.text = "";
        if (leadUsedText != null) leadUsedText.text = "Lead: --";

        if (waveformLine != null)
            waveformLine.positionCount = 0;

        if (pWaveHighlight != null) pWaveHighlight.gameObject.SetActive(false);
        if (qrsHighlight != null) qrsHighlight.gameObject.SetActive(false);
        if (tWaveHighlight != null) tWaveHighlight.gameObject.SetActive(false);
    }
}
