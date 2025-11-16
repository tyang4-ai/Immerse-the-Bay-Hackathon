using UnityEngine;
using System.Collections;
using System.Collections.Generic;

/// <summary>
/// Animates electrical wave propagation through the heart
/// Uses activation_sequence timing from backend API
/// Triggers particle effects and glow pulses on each region
/// </summary>
public class ElectricalWaveAnimator : MonoBehaviour
{
    [Header("Animation Settings")]
    [Tooltip("Speed multiplier for animation (1.0 = real-time, 2.0 = 2x speed)")]
    [SerializeField] private float animationSpeed = 1.0f;

    [Tooltip("Pulse duration for each region glow (seconds)")]
    [SerializeField] private float pulseDuration = 0.5f;

    [Tooltip("Loop animation continuously")]
    [SerializeField] private bool loopAnimation = true;

    [Tooltip("Delay between animation loops (seconds)")]
    [SerializeField] private float loopDelay = 1.0f;

    [Header("Visual Effects")]
    [Tooltip("Show connection lines between activating regions")]
    [SerializeField] private bool showConnectionLines = true;

    [SerializeField] private LineRenderer connectionLinePrefab;
    [SerializeField] private float lineDisplayDuration = 0.3f;

    // Active animation coroutine
    private Coroutine activeAnimation;

    // Line renderer pool
    private List<LineRenderer> linePool = new List<LineRenderer>();

    /// <summary>
    /// Start electrical wave animation using backend activation sequence
    /// </summary>
    /// <param name="activationSequence">List of [region_name, delay_ms] from backend</param>
    /// <param name="regionMapping">Heart region mapping for region lookup</param>
    public IEnumerator AnimateActivationSequence(
        List<List<object>> activationSequence,
        HeartRegionMapping regionMapping)
    {
        if (activationSequence == null || activationSequence.Count == 0)
        {
            Debug.LogWarning("[ElectricalWaveAnimator] Empty activation sequence");
            yield break;
        }

        if (regionMapping == null)
        {
            Debug.LogError("[ElectricalWaveAnimator] HeartRegionMapping is null");
            yield break;
        }

        // Stop any existing animation
        if (activeAnimation != null)
        {
            StopCoroutine(activeAnimation);
        }

        // Start new animation
        activeAnimation = StartCoroutine(AnimateSequenceInternal(activationSequence, regionMapping));
    }

    /// <summary>
    /// Internal coroutine for animation loop
    /// </summary>
    private IEnumerator AnimateSequenceInternal(
        List<List<object>> activationSequence,
        HeartRegionMapping regionMapping)
    {
        do
        {
            Debug.Log($"[ElectricalWaveAnimator] Starting electrical wave animation ({activationSequence.Count} steps)");

            CardiacRegionMarker previousRegion = null;
            float previousActivationTime = 0f;

            foreach (var step in activationSequence)
            {
                // Parse step: [region_name, delay_ms]
                string regionName = step[0].ToString();
                float delayMs = float.Parse(step[1].ToString());

                // Calculate actual delay from previous activation
                float delayFromPrevious = (delayMs - previousActivationTime) / 1000f;
                delayFromPrevious = Mathf.Max(0, delayFromPrevious); // Ensure non-negative

                // Apply animation speed multiplier
                float adjustedDelay = delayFromPrevious / animationSpeed;

                // Wait for activation time
                if (adjustedDelay > 0)
                {
                    yield return new WaitForSeconds(adjustedDelay);
                }

                // Get region marker
                CardiacRegionMarker currentRegion = regionMapping.GetRegion(regionName);
                if (currentRegion != null)
                {
                    // Trigger electrical wave effect
                    currentRegion.TriggerElectricalWave();

                    // Pulse glow
                    StartCoroutine(currentRegion.PulseGlow(pulseDuration / animationSpeed));

                    // Show connection line from previous region
                    if (showConnectionLines && previousRegion != null && connectionLinePrefab != null)
                    {
                        StartCoroutine(ShowConnectionLine(
                            previousRegion.GetPosition(),
                            currentRegion.GetPosition(),
                            lineDisplayDuration / animationSpeed
                        ));
                    }

                    Debug.Log($"[ElectricalWaveAnimator] Activated {regionName} at {delayMs}ms");

                    previousRegion = currentRegion;
                }
                else
                {
                    Debug.LogWarning($"[ElectricalWaveAnimator] Region not found: {regionName}");
                }

                previousActivationTime = delayMs;
            }

            Debug.Log("[ElectricalWaveAnimator] Animation sequence complete");

            // Wait before looping
            if (loopAnimation)
            {
                yield return new WaitForSeconds(loopDelay / animationSpeed);
            }

        } while (loopAnimation);

        activeAnimation = null;
    }

    /// <summary>
    /// Show connection line between two regions
    /// </summary>
    private IEnumerator ShowConnectionLine(Vector3 startPos, Vector3 endPos, float duration)
    {
        // Get line renderer from pool or create new
        LineRenderer line = GetLineFromPool();
        if (line == null) yield break;

        // Configure line
        line.gameObject.SetActive(true);
        line.positionCount = 2;
        line.SetPosition(0, startPos);
        line.SetPosition(1, endPos);

        // Fade in/out
        float elapsed = 0f;
        Color startColor = new Color(1f, 1f, 0f, 1f); // Yellow
        Color endColor = new Color(1f, 1f, 0f, 0f);   // Transparent

        while (elapsed < duration)
        {
            elapsed += Time.deltaTime;
            float t = elapsed / duration;

            Color currentColor = Color.Lerp(startColor, endColor, t);
            line.startColor = currentColor;
            line.endColor = currentColor;

            yield return null;
        }

        // Return to pool
        line.gameObject.SetActive(false);
    }

    /// <summary>
    /// Get line renderer from pool
    /// </summary>
    private LineRenderer GetLineFromPool()
    {
        // Find inactive line
        foreach (var line in linePool)
        {
            if (!line.gameObject.activeSelf)
                return line;
        }

        // Create new line if pool is empty
        if (connectionLinePrefab != null)
        {
            LineRenderer newLine = Instantiate(connectionLinePrefab, transform);
            newLine.gameObject.SetActive(false);
            linePool.Add(newLine);
            return newLine;
        }

        return null;
    }

    /// <summary>
    /// Stop current animation
    /// </summary>
    public void StopAnimation()
    {
        if (activeAnimation != null)
        {
            StopCoroutine(activeAnimation);
            activeAnimation = null;
        }

        // Deactivate all lines
        foreach (var line in linePool)
        {
            line.gameObject.SetActive(false);
        }

        Debug.Log("[ElectricalWaveAnimator] Animation stopped");
    }

    /// <summary>
    /// Set animation speed multiplier
    /// </summary>
    public void SetAnimationSpeed(float speed)
    {
        animationSpeed = Mathf.Max(0.1f, speed); // Min speed 0.1x
        Debug.Log($"[ElectricalWaveAnimator] Animation speed set to {animationSpeed}x");
    }

    /// <summary>
    /// Toggle animation looping
    /// </summary>
    public void SetLooping(bool loop)
    {
        loopAnimation = loop;
        Debug.Log($"[ElectricalWaveAnimator] Looping {(loop ? "enabled" : "disabled")}");
    }

    void OnDestroy()
    {
        StopAnimation();
    }
}
