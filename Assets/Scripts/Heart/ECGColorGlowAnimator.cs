using UnityEngine;
using System.Collections;
using System.Collections.Generic;

/// <summary>
/// Maps ECG signal amplitude to heart model color and glow intensity
/// Real-time visualization of electrical activity through color changes
/// Uses actual ECG waveform data from backend
/// </summary>
public class ECGColorGlowAnimator : MonoBehaviour
{
    [Header("Heart Model")]
    [Tooltip("The heart model renderer to animate")]
    public Renderer heartRenderer;

    [Header("Color Mapping")]
    [Tooltip("Color at minimum ECG amplitude (resting)")]
    public Color minColor = new Color(0.8f, 0.3f, 0.3f); // Dark red

    [Tooltip("Color at maximum ECG amplitude (peak activity)")]
    public Color maxColor = new Color(1f, 0.9f, 0.2f); // Bright yellow

    [Tooltip("Glow color (emission)")]
    public Color glowColor = new Color(1f, 0.5f, 0.2f); // Orange glow

    [Header("Glow Intensity")]
    [Tooltip("Minimum emission intensity (resting)")]
    [Range(0f, 5f)]
    public float minGlowIntensity = 0.2f;

    [Tooltip("Maximum emission intensity (peak activity)")]
    [Range(0f, 10f)]
    public float maxGlowIntensity = 3.5f;

    [Header("ECG Settings")]
    [Tooltip("Which ECG lead to use for visualization (0-11)")]
    [Range(0, 11)]
    public int ecgLeadIndex = 1; // Lead II (index 1) - best for rhythm

    [Tooltip("Playback speed multiplier (1.0 = real-time)")]
    [Range(0.1f, 5f)]
    public float playbackSpeed = 1.0f;

    [Tooltip("Loop ECG playback continuously")]
    public bool loopPlayback = true;

    [Tooltip("Smoothing factor for color transitions (higher = smoother)")]
    [Range(0f, 1f)]
    public float smoothing = 0.7f;

    [Header("Region-Specific Coloring")]
    [Tooltip("Enable different colors for different heart regions")]
    public bool enableRegionColors = false;

    // Internal state
    private MaterialPropertyBlock propertyBlock;
    private float[,] ecgSignal;
    private int currentSampleIndex = 0;
    private bool isPlaying = false;
    private float samplingRate = 400f; // ECG sampled at 400 Hz
    private float currentAmplitude = 0f;
    private float targetAmplitude = 0f;

    // ECG normalization values
    private float ecgMin = float.MaxValue;
    private float ecgMax = float.MinValue;

    void Start()
    {
        // Get renderer if not assigned
        if (heartRenderer == null)
            heartRenderer = GetComponent<Renderer>();

        if (heartRenderer == null)
        {
            Debug.LogError("[ECGColorGlow] No renderer found on heart model!");
            return;
        }

        // Create material property block for per-instance material changes
        propertyBlock = new MaterialPropertyBlock();

        // Set initial state
        SetColorAndGlow(0f);
    }

    /// <summary>
    /// Load ECG signal data and start visualization
    /// </summary>
    public void PlayECGVisualization(float[,] ecgData, int leadIndex = -1)
    {
        if (ecgData == null || ecgData.GetLength(1) < 12)
        {
            Debug.LogError("[ECGColorGlow] Invalid ECG data!");
            return;
        }

        ecgSignal = ecgData;

        // Use specified lead or default
        if (leadIndex >= 0 && leadIndex < 12)
            ecgLeadIndex = leadIndex;

        // Normalize ECG signal for this lead
        NormalizeECGSignal();

        // Start playback
        currentSampleIndex = 0;
        isPlaying = true;

        StopAllCoroutines();
        StartCoroutine(PlaybackCoroutine());

        Debug.Log($"[ECGColorGlow] Started ECG visualization on Lead {ecgLeadIndex}");
    }

    /// <summary>
    /// Normalize ECG signal to 0-1 range for color mapping
    /// </summary>
    void NormalizeECGSignal()
    {
        ecgMin = float.MaxValue;
        ecgMax = float.MinValue;

        int samples = ecgSignal.GetLength(0);

        // Find min/max for selected lead
        for (int i = 0; i < samples; i++)
        {
            float value = ecgSignal[i, ecgLeadIndex];
            if (value < ecgMin) ecgMin = value;
            if (value > ecgMax) ecgMax = value;
        }

        Debug.Log($"[ECGColorGlow] ECG Lead {ecgLeadIndex} range: [{ecgMin:F3}, {ecgMax:F3}]");
    }

    /// <summary>
    /// Main playback loop - updates color/glow based on ECG waveform
    /// </summary>
    IEnumerator PlaybackCoroutine()
    {
        int totalSamples = ecgSignal.GetLength(0);

        while (isPlaying)
        {
            // Get current ECG amplitude
            float rawAmplitude = ecgSignal[currentSampleIndex, ecgLeadIndex];

            // Normalize to 0-1 range
            targetAmplitude = Mathf.InverseLerp(ecgMin, ecgMax, rawAmplitude);

            // Smooth amplitude changes for better visuals
            currentAmplitude = Mathf.Lerp(currentAmplitude, targetAmplitude, 1f - smoothing);

            // Update heart color and glow
            SetColorAndGlow(currentAmplitude);

            // Advance to next sample
            currentSampleIndex++;

            // Loop or stop at end
            if (currentSampleIndex >= totalSamples)
            {
                if (loopPlayback)
                {
                    currentSampleIndex = 0;
                    Debug.Log("[ECGColorGlow] Looping ECG visualization");
                }
                else
                {
                    isPlaying = false;
                    Debug.Log("[ECGColorGlow] ECG visualization complete");
                    break;
                }
            }

            // Calculate wait time based on sampling rate and playback speed
            float sampleInterval = (1f / samplingRate) / playbackSpeed;
            yield return new WaitForSeconds(sampleInterval);
        }
    }

    /// <summary>
    /// Set heart color and glow intensity based on ECG amplitude
    /// </summary>
    void SetColorAndGlow(float normalizedAmplitude)
    {
        if (heartRenderer == null || propertyBlock == null) return;

        // Get current property block
        heartRenderer.GetPropertyBlock(propertyBlock);

        // Map amplitude to color (min -> max)
        Color currentColor = Color.Lerp(minColor, maxColor, normalizedAmplitude);

        // Map amplitude to glow intensity
        float glowIntensity = Mathf.Lerp(minGlowIntensity, maxGlowIntensity, normalizedAmplitude);

        // Apply to material (supports both Standard and URP shaders)
        propertyBlock.SetColor("_BaseColor", currentColor);  // URP
        propertyBlock.SetColor("_Color", currentColor);      // Standard

        // Set emission (glow)
        Color emissionColor = glowColor * glowIntensity;
        propertyBlock.SetColor("_EmissionColor", emissionColor);

        // Apply property block
        heartRenderer.SetPropertyBlock(propertyBlock);
    }

    /// <summary>
    /// Sync with beat timestamps for precise heartbeat highlighting
    /// </summary>
    public void HighlightBeats(List<float> beatTimestamps)
    {
        if (beatTimestamps == null || beatTimestamps.Count == 0) return;

        StartCoroutine(BeatHighlightCoroutine(beatTimestamps));
    }

    /// <summary>
    /// Coroutine to flash glow at each heartbeat
    /// </summary>
    IEnumerator BeatHighlightCoroutine(List<float> beatTimestamps)
    {
        foreach (float timestamp in beatTimestamps)
        {
            yield return new WaitForSeconds(timestamp);

            // Flash at beat
            StartCoroutine(FlashGlow());
        }
    }

    /// <summary>
    /// Quick flash of maximum glow
    /// </summary>
    IEnumerator FlashGlow()
    {
        float flashDuration = 0.15f;
        float elapsed = 0f;

        while (elapsed < flashDuration)
        {
            elapsed += Time.deltaTime;
            float t = elapsed / flashDuration;

            // Pulse intensity (0 -> 1 -> 0)
            float intensity = Mathf.Sin(t * Mathf.PI);
            float flashIntensity = Mathf.Lerp(currentAmplitude, 1f, intensity);

            SetColorAndGlow(flashIntensity);

            yield return null;
        }

        // Return to current amplitude
        SetColorAndGlow(currentAmplitude);
    }

    /// <summary>
    /// Stop ECG visualization
    /// </summary>
    public void StopVisualization()
    {
        isPlaying = false;
        StopAllCoroutines();
        SetColorAndGlow(0f);
    }

    /// <summary>
    /// Pause playback
    /// </summary>
    public void PauseVisualization()
    {
        isPlaying = false;
    }

    /// <summary>
    /// Resume playback
    /// </summary>
    public void ResumeVisualization()
    {
        if (ecgSignal != null && !isPlaying)
        {
            isPlaying = true;
            StartCoroutine(PlaybackCoroutine());
        }
    }

    /// <summary>
    /// Set static color based on diagnosis severity
    /// </summary>
    public void SetDiagnosisColor(float severity)
    {
        StopAllCoroutines();
        isPlaying = false;

        // Map severity to color (0 = healthy green, 1 = severe red)
        Color diagnosisColor = Color.Lerp(Color.green, Color.red, severity);
        float diagnosisGlow = Mathf.Lerp(0.5f, 3f, severity);

        if (heartRenderer != null && propertyBlock != null)
        {
            heartRenderer.GetPropertyBlock(propertyBlock);
            propertyBlock.SetColor("_BaseColor", diagnosisColor);
            propertyBlock.SetColor("_Color", diagnosisColor);
            propertyBlock.SetColor("_EmissionColor", diagnosisColor * diagnosisGlow);
            heartRenderer.SetPropertyBlock(propertyBlock);
        }

        Debug.Log($"[ECGColorGlow] Set diagnosis color (severity: {severity:P0})");
    }

    void OnDestroy()
    {
        // Reset to default color
        if (heartRenderer != null && propertyBlock != null)
        {
            SetColorAndGlow(0f);
        }
    }
}
