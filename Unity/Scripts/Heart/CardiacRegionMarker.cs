using UnityEngine;

/// <summary>
/// Controls visualization for a single cardiac region marker
/// Manages glow color, intensity, and particle effects based on region health severity
/// Attached to each of the 10 cardiac region GameObjects
/// </summary>
public class CardiacRegionMarker : MonoBehaviour
{
    [Header("Region Configuration")]
    [Tooltip("Backend region name (e.g., 'sa_node', 'rbbb', 'av_node')")]
    public string regionName;

    [Header("Visual Components")]
    [SerializeField] private Light glowLight;
    [SerializeField] private ParticleSystem electricalEffect;
    [SerializeField] private Renderer regionRenderer; // Optional: if using mesh instead of marker

    [Header("Visual Settings")]
    [Range(0f, 1f)]
    [SerializeField] private float severity = 0f; // 0 = healthy, 1 = critical
    [SerializeField] private Color currentColor = Color.green;
    [SerializeField] private float maxLightIntensity = 3f;
    [SerializeField] private float maxParticleEmission = 50f;

    [Header("Animation")]
    [SerializeField] private bool isPulsing = false;
    [SerializeField] private float pulseSpeed = 2f;
    [SerializeField] private float pulseAmplitude = 0.5f;

    private Material glowMaterial;
    private float baseLightIntensity;
    private ParticleSystem.EmissionModule emissionModule;

    void Awake()
    {
        // Get components
        if (glowLight == null)
            glowLight = GetComponent<Light>();

        if (electricalEffect == null)
            electricalEffect = GetComponentInChildren<ParticleSystem>();

        if (regionRenderer == null)
            regionRenderer = GetComponent<Renderer>();

        // Initialize particle system
        if (electricalEffect != null)
        {
            emissionModule = electricalEffect.emission;
            emissionModule.rateOverTime = 0; // Start with no particles
        }

        // Create glow material for emissive regions
        if (regionRenderer != null)
        {
            glowMaterial = regionRenderer.material;
            glowMaterial.EnableKeyword("_EMISSION");
        }
    }

    void Start()
    {
        // Store base light intensity
        if (glowLight != null)
            baseLightIntensity = glowLight.intensity;

        // Initialize as healthy (green, no glow)
        UpdateVisualization(0f, Color.green);
    }

    void Update()
    {
        // Pulse animation if active
        if (isPulsing && glowLight != null)
        {
            float pulse = Mathf.Sin(Time.time * pulseSpeed) * pulseAmplitude;
            glowLight.intensity = baseLightIntensity + pulse;
        }
    }

    /// <summary>
    /// Update region visualization based on health data from backend
    /// </summary>
    /// <param name="newSeverity">Severity 0.0-1.0 (0=healthy, 1=critical)</param>
    /// <param name="newColor">RGB color from backend (green, yellow, orange, red)</param>
    public void UpdateVisualization(float newSeverity, Color newColor)
    {
        severity = Mathf.Clamp01(newSeverity);
        currentColor = newColor;

        // Update Light component
        if (glowLight != null)
        {
            glowLight.color = currentColor;
            baseLightIntensity = severity * maxLightIntensity;
            glowLight.intensity = baseLightIntensity;
        }

        // Update emissive material
        if (glowMaterial != null)
        {
            glowMaterial.SetColor("_EmissionColor", currentColor * severity * 2f);
        }

        // Update particle emission rate
        if (electricalEffect != null)
        {
            emissionModule.rateOverTime = severity * maxParticleEmission;
        }

        Debug.Log($"[CardiacRegionMarker] Updated {regionName}: severity={severity:F2}, color={currentColor}");
    }

    /// <summary>
    /// Trigger electrical wave particle effect
    /// Called during activation sequence animation
    /// </summary>
    public void TriggerElectricalWave()
    {
        if (electricalEffect != null)
        {
            electricalEffect.Play();
            Debug.Log($"[CardiacRegionMarker] Electrical wave triggered at {regionName}");
        }

        // Start pulse animation
        StartCoroutine(PulseGlow(0.5f));
    }

    /// <summary>
    /// Pulse the glow light for a duration
    /// </summary>
    /// <param name="duration">Duration of pulse in seconds</param>
    public System.Collections.IEnumerator PulseGlow(float duration)
    {
        isPulsing = true;
        yield return new WaitForSeconds(duration);
        isPulsing = false;

        // Reset to base intensity
        if (glowLight != null)
            glowLight.intensity = baseLightIntensity;
    }

    /// <summary>
    /// Get the world position of this region marker
    /// Used by waypoint system and camera focus
    /// </summary>
    public Vector3 GetPosition()
    {
        return transform.position;
    }

    /// <summary>
    /// Highlight this region (for user selection or waypoint focus)
    /// </summary>
    public void Highlight(bool enable)
    {
        if (enable)
        {
            if (glowLight != null)
                glowLight.intensity = maxLightIntensity;

            isPulsing = true;
        }
        else
        {
            if (glowLight != null)
                glowLight.intensity = baseLightIntensity;

            isPulsing = false;
        }
    }

    // Visualize region position in Scene view
    void OnDrawGizmos()
    {
        // Color-code gizmo by severity
        if (Application.isPlaying)
        {
            Gizmos.color = currentColor;
        }
        else
        {
            // Default color in edit mode
            Gizmos.color = Color.cyan;
        }

        Gizmos.DrawWireSphere(transform.position, 0.02f);

        // Draw region name label
        #if UNITY_EDITOR
        UnityEditor.Handles.Label(transform.position + Vector3.up * 0.05f, regionName);
        #endif
    }
}
