using UnityEngine;
using UnityEngine.XR.Interaction.Toolkit;

/// <summary>
/// Handles VR interaction with waypoint markers
/// Supports XR ray pointer hover and click events
/// Displays teaser text on hover, triggers region drill-down on click
/// </summary>
[RequireComponent(typeof(XRSimpleInteractable))]
public class WaypointInteraction : MonoBehaviour
{
    [Header("Waypoint Configuration")]
    [SerializeField] private string regionName;
    [SerializeField] private string teaserText;

    [Header("Visual Feedback")]
    [SerializeField] private GameObject hoverGlowEffect;
    [SerializeField] private TMPro.TextMeshProUGUI teaserTextUI;
    [SerializeField] private GameObject teaserPanel;
    [SerializeField] private float glowIntensity = 2f;
    [SerializeField] private Color idleColor = new Color(0.3f, 0.6f, 1f); // Light blue
    [SerializeField] private Color hoverColor = new Color(1f, 0.8f, 0.2f); // Gold

    [Header("Animation")]
    [SerializeField] private float pulseSpeed = 2f;
    [SerializeField] private float pulseAmplitude = 0.2f;
    [SerializeField] private bool isPulsing = true;

    // Components
    private XRSimpleInteractable interactable;
    private Light waypointLight;
    private Renderer waypointRenderer;
    private StorytellingJourneyController journeyController;

    // State
    private bool isHovered = false;
    private float baseScale = 1f;
    private Vector3 originalScale;

    void Awake()
    {
        // Get XR interaction component
        interactable = GetComponent<XRSimpleInteractable>();

        // Get visual components
        waypointLight = GetComponentInChildren<Light>();
        waypointRenderer = GetComponentInChildren<Renderer>();

        // Store original scale
        originalScale = transform.localScale;
        baseScale = originalScale.x;

        // Setup interaction callbacks
        if (interactable != null)
        {
            interactable.hoverEntered.AddListener(OnHoverEnter);
            interactable.hoverExited.AddListener(OnHoverExit);
            interactable.selectEntered.AddListener(OnClick);
        }

        // Initialize visual state
        if (waypointLight != null)
        {
            waypointLight.color = idleColor;
            waypointLight.intensity = glowIntensity;
        }

        if (hoverGlowEffect != null)
        {
            hoverGlowEffect.SetActive(false);
        }

        if (teaserPanel != null)
        {
            teaserPanel.SetActive(false);
        }
    }

    void Update()
    {
        // Idle pulse animation
        if (isPulsing && !isHovered)
        {
            float pulse = Mathf.Sin(Time.time * pulseSpeed) * pulseAmplitude;
            float scale = baseScale + pulse;
            transform.localScale = originalScale * scale;
        }

        // Keep teaser panel facing camera
        if (teaserPanel != null && teaserPanel.activeSelf)
        {
            Camera mainCamera = Camera.main;
            if (mainCamera != null)
            {
                teaserPanel.transform.LookAt(mainCamera.transform);
                teaserPanel.transform.Rotate(0, 180, 0); // Flip to face camera
            }
        }
    }

    /// <summary>
    /// Initialize waypoint with region data
    /// Called by StorytellingJourneyController when creating waypoints
    /// </summary>
    public void Initialize(string regionName, string teaserText, StorytellingJourneyController journeyController)
    {
        this.regionName = regionName;
        this.teaserText = teaserText;
        this.journeyController = journeyController;

        Debug.Log($"[WaypointInteraction] Initialized for region: {regionName}");
    }

    /// <summary>
    /// Called when VR ray pointer hovers over waypoint
    /// </summary>
    void OnHoverEnter(HoverEnterEventArgs args)
    {
        isHovered = true;

        // Show hover glow effect
        if (hoverGlowEffect != null)
        {
            hoverGlowEffect.SetActive(true);
        }

        // Change light color to hover color
        if (waypointLight != null)
        {
            waypointLight.color = hoverColor;
            waypointLight.intensity = glowIntensity * 1.5f;
        }

        // Show teaser text panel
        if (teaserPanel != null && teaserTextUI != null)
        {
            teaserTextUI.text = teaserText;
            teaserPanel.SetActive(true);
        }

        // Scale up slightly
        transform.localScale = originalScale * 1.2f;

        Debug.Log($"[WaypointInteraction] Hover enter: {regionName}");
    }

    /// <summary>
    /// Called when VR ray pointer exits waypoint
    /// </summary>
    void OnHoverExit(HoverExitEventArgs args)
    {
        isHovered = false;

        // Hide hover glow effect
        if (hoverGlowEffect != null)
        {
            hoverGlowEffect.SetActive(false);
        }

        // Restore light color to idle
        if (waypointLight != null)
        {
            waypointLight.color = idleColor;
            waypointLight.intensity = glowIntensity;
        }

        // Hide teaser text panel
        if (teaserPanel != null)
        {
            teaserPanel.SetActive(false);
        }

        // Restore scale
        transform.localScale = originalScale;

        Debug.Log($"[WaypointInteraction] Hover exit: {regionName}");
    }

    /// <summary>
    /// Called when user clicks waypoint with VR controller
    /// Triggers regional drill-down in journey mode
    /// </summary>
    void OnClick(SelectEnterEventArgs args)
    {
        if (journeyController == null)
        {
            Debug.LogWarning("[WaypointInteraction] No journey controller assigned!");
            return;
        }

        Debug.Log($"[WaypointInteraction] Clicked waypoint: {regionName}");

        // Trigger regional drill-down
        journeyController.FocusOnRegion(regionName);

        // Optional: Play click sound
        PlayClickSound();

        // Optional: Visual feedback
        StartCoroutine(ClickFeedback());
    }

    /// <summary>
    /// Visual feedback on click (brief flash)
    /// </summary>
    System.Collections.IEnumerator ClickFeedback()
    {
        // Flash bright white
        if (waypointLight != null)
        {
            Color originalColor = waypointLight.color;
            float originalIntensity = waypointLight.intensity;

            waypointLight.color = Color.white;
            waypointLight.intensity = glowIntensity * 3f;

            yield return new WaitForSeconds(0.1f);

            waypointLight.color = originalColor;
            waypointLight.intensity = originalIntensity;
        }
    }

    /// <summary>
    /// Play click sound effect
    /// </summary>
    void PlayClickSound()
    {
        AudioSource audioSource = GetComponent<AudioSource>();
        if (audioSource != null && audioSource.clip != null)
        {
            audioSource.Play();
        }
    }

    /// <summary>
    /// Highlight waypoint (called externally for guidance)
    /// </summary>
    public void Highlight(bool enable)
    {
        if (enable)
        {
            if (waypointLight != null)
            {
                waypointLight.color = hoverColor;
                waypointLight.intensity = glowIntensity * 2f;
            }

            if (hoverGlowEffect != null)
            {
                hoverGlowEffect.SetActive(true);
            }

            isPulsing = true;
        }
        else
        {
            if (waypointLight != null)
            {
                waypointLight.color = idleColor;
                waypointLight.intensity = glowIntensity;
            }

            if (hoverGlowEffect != null && !isHovered)
            {
                hoverGlowEffect.SetActive(false);
            }

            isPulsing = true;
        }
    }

    /// <summary>
    /// Get region name for this waypoint
    /// </summary>
    public string GetRegionName()
    {
        return regionName;
    }

    /// <summary>
    /// Set teaser text (update after initialization)
    /// </summary>
    public void SetTeaserText(string newTeaserText)
    {
        teaserText = newTeaserText;
        if (teaserTextUI != null)
        {
            teaserTextUI.text = teaserText;
        }
    }

    void OnDestroy()
    {
        // Clean up event listeners
        if (interactable != null)
        {
            interactable.hoverEntered.RemoveListener(OnHoverEnter);
            interactable.hoverExited.RemoveListener(OnHoverExit);
            interactable.selectEntered.RemoveListener(OnClick);
        }
    }

    // Visualize waypoint in Scene view
    void OnDrawGizmos()
    {
        Gizmos.color = isHovered ? hoverColor : idleColor;
        Gizmos.DrawWireSphere(transform.position, 0.03f);

        // Draw region name label
        #if UNITY_EDITOR
        if (!string.IsNullOrEmpty(regionName))
        {
            UnityEditor.Handles.Label(transform.position + Vector3.up * 0.05f, regionName);
        }
        #endif
    }
}
