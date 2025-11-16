using UnityEngine;
using System.Collections;
using System.Collections.Generic;

/// <summary>
/// Animates the heart model to pulse in sync with ECG heartbeat data
/// Uses actual beat timestamps from backend API
/// Supports both continuous pulsing and single-beat playback
/// </summary>
public class HeartbeatPulseAnimator : MonoBehaviour
{
    [Header("Heart Model")]
    [Tooltip("The heart model transform to animate")]
    public Transform heartModel;

    [Header("Pulse Settings")]
    [Tooltip("Scale multiplier at peak of pulse (1.0 = no change, 1.1 = 10% larger)")]
    [Range(1.0f, 1.5f)]
    public float pulseScaleMultiplier = 1.15f;

    [Tooltip("Duration of pulse animation in seconds")]
    [Range(0.1f, 1.0f)]
    public float pulseDuration = 0.3f;

    [Tooltip("Animation curve for pulse (ease in/out for realistic heartbeat)")]
    public AnimationCurve pulseCurve = AnimationCurve.EaseInOut(0, 0, 1, 1);

    [Header("Pulse Color (Optional)")]
    [Tooltip("Enable color pulse on heart material")]
    public bool enableColorPulse = true;

    [Tooltip("Color at peak of pulse")]
    public Color pulseColor = new Color(1f, 0.3f, 0.3f); // Red

    [Tooltip("Normal heart color")]
    public Color normalColor = new Color(1f, 0.8f, 0.8f); // Light pink

    [Header("Continuous Loop")]
    [Tooltip("Loop heartbeat animation continuously (uses heart rate from API)")]
    public bool continuousPulse = true;

    [Tooltip("BPM for continuous pulse (overridden by API data if available)")]
    public float defaultBPM = 72f;

    // Internal state
    private Vector3 originalScale;
    private Renderer heartRenderer;
    private MaterialPropertyBlock propertyBlock;
    private bool isAnimating = false;
    private float currentBPM;
    private List<float> beatTimestamps;
    private int currentBeatIndex = 0;
    private float ecgStartTime;

    void Start()
    {
        // Get heart model if not assigned
        if (heartModel == null)
            heartModel = transform;

        // Store original scale
        originalScale = heartModel.localScale;

        // Get renderer for color pulse
        heartRenderer = heartModel.GetComponent<Renderer>();
        if (heartRenderer != null && enableColorPulse)
        {
            propertyBlock = new MaterialPropertyBlock();
            heartRenderer.GetPropertyBlock(propertyBlock);
            propertyBlock.SetColor("_BaseColor", normalColor);
            propertyBlock.SetColor("_Color", normalColor); // Standard shader
            heartRenderer.SetPropertyBlock(propertyBlock);
        }

        // Start continuous pulse with default BPM
        currentBPM = defaultBPM;
        if (continuousPulse)
        {
            StartCoroutine(ContinuousPulseLoop());
        }
    }

    /// <summary>
    /// Set heart rate from API response and update pulse timing
    /// </summary>
    public void SetHeartRate(HeartRateData heartRateData)
    {
        if (heartRateData == null) return;

        currentBPM = heartRateData.bpm;
        beatTimestamps = heartRateData.beat_timestamps;

        Debug.Log($"[HeartbeatPulse] Updated heart rate: {currentBPM:F1} BPM, {beatTimestamps?.Count ?? 0} beats");

        // Restart continuous pulse with new timing
        if (continuousPulse && !isAnimating)
        {
            StopAllCoroutines();
            StartCoroutine(ContinuousPulseLoop());
        }
    }

    /// <summary>
    /// Play heartbeat animation synchronized with ECG data
    /// Uses actual beat timestamps from backend
    /// </summary>
    public void PlayECGSynchronized(List<float> timestamps, float startTime = 0f)
    {
        if (timestamps == null || timestamps.Count == 0)
        {
            Debug.LogWarning("[HeartbeatPulse] No beat timestamps provided");
            return;
        }

        beatTimestamps = timestamps;
        ecgStartTime = startTime;
        currentBeatIndex = 0;

        StopAllCoroutines();
        StartCoroutine(ECGSynchronizedPulse());
    }

    /// <summary>
    /// Continuous pulse loop using BPM
    /// </summary>
    IEnumerator ContinuousPulseLoop()
    {
        while (continuousPulse)
        {
            // Calculate interval from BPM
            float intervalSeconds = 60f / currentBPM;

            // Trigger pulse
            yield return StartCoroutine(PulseBeat());

            // Wait until next beat
            float waitTime = intervalSeconds - pulseDuration;
            if (waitTime > 0)
                yield return new WaitForSeconds(waitTime);
        }
    }

    /// <summary>
    /// ECG-synchronized pulse using actual beat timestamps
    /// </summary>
    IEnumerator ECGSynchronizedPulse()
    {
        float elapsedTime = 0f;

        while (currentBeatIndex < beatTimestamps.Count)
        {
            float nextBeatTime = beatTimestamps[currentBeatIndex];
            float timeUntilBeat = nextBeatTime - elapsedTime;

            // Wait until next beat
            if (timeUntilBeat > 0)
            {
                yield return new WaitForSeconds(timeUntilBeat);
                elapsedTime += timeUntilBeat;
            }

            // Trigger pulse
            yield return StartCoroutine(PulseBeat());

            currentBeatIndex++;
        }

        Debug.Log("[HeartbeatPulse] ECG synchronized playback complete");

        // Resume continuous pulse after ECG playback
        if (continuousPulse)
        {
            StartCoroutine(ContinuousPulseLoop());
        }
    }

    /// <summary>
    /// Single heartbeat pulse animation
    /// </summary>
    IEnumerator PulseBeat()
    {
        if (isAnimating) yield break;

        isAnimating = true;

        float elapsed = 0f;

        while (elapsed < pulseDuration)
        {
            elapsed += Time.deltaTime;
            float t = elapsed / pulseDuration;

            // Use animation curve for realistic heartbeat
            float curveValue = pulseCurve.Evaluate(t);

            // Scale pulse (grows then shrinks back)
            float scale = Mathf.Lerp(1f, pulseScaleMultiplier, curveValue);
            heartModel.localScale = originalScale * scale;

            // Color pulse (optional)
            if (enableColorPulse && heartRenderer != null && propertyBlock != null)
            {
                Color currentColor = Color.Lerp(normalColor, pulseColor, curveValue);
                propertyBlock.SetColor("_BaseColor", currentColor);
                propertyBlock.SetColor("_Color", currentColor);
                heartRenderer.SetPropertyBlock(propertyBlock);
            }

            yield return null;
        }

        // Reset to original state
        heartModel.localScale = originalScale;

        if (enableColorPulse && heartRenderer != null && propertyBlock != null)
        {
            propertyBlock.SetColor("_BaseColor", normalColor);
            propertyBlock.SetColor("_Color", normalColor);
            heartRenderer.SetPropertyBlock(propertyBlock);
        }

        isAnimating = false;
    }

    /// <summary>
    /// Manually trigger a single pulse
    /// </summary>
    public void TriggerPulse()
    {
        if (!isAnimating)
        {
            StartCoroutine(PulseBeat());
        }
    }

    /// <summary>
    /// Stop all pulse animations
    /// </summary>
    public void StopPulse()
    {
        StopAllCoroutines();
        isAnimating = false;
        heartModel.localScale = originalScale;

        if (enableColorPulse && heartRenderer != null && propertyBlock != null)
        {
            propertyBlock.SetColor("_BaseColor", normalColor);
            propertyBlock.SetColor("_Color", normalColor);
            heartRenderer.SetPropertyBlock(propertyBlock);
        }
    }

    /// <summary>
    /// Resume continuous pulse
    /// </summary>
    public void ResumePulse()
    {
        if (!continuousPulse) return;

        StopAllCoroutines();
        StartCoroutine(ContinuousPulseLoop());
    }

    void OnDestroy()
    {
        // Reset scale on cleanup
        if (heartModel != null)
            heartModel.localScale = originalScale;
    }
}
