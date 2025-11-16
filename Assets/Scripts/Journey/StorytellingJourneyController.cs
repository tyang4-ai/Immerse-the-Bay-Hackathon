using UnityEngine;
using System.Collections;
using System.Collections.Generic;
using TMPro;

/// <summary>
/// Controls VR storytelling journey mode
/// Creates immersive narrative experience with 3D waypoints at cardiac regions
/// Handles atmosphere (lighting, particles, audio) based on storytelling content
/// Supports recursive drill-down (click region → explore that region's story)
/// </summary>
public class StorytellingJourneyController : MonoBehaviour
{
    [Header("API Client")]
    [SerializeField] private ECGAPIClient apiClient;

    [Header("UI Components")]
    [SerializeField] private TMPro.TextMeshProUGUI narrativeText;
    [SerializeField] private GameObject narrativePanel;
    [SerializeField] private TMPro.TextMeshProUGUI statusText;

    [Header("Heart Visualization")]
    [SerializeField] private HeartRegionMapping regionMapping;
    [SerializeField] private GameObject waypointPrefab; // Prefab with WaypointInteraction component

    [Header("Atmosphere Control")]
    [SerializeField] private Light ambientLight;
    [SerializeField] private ParticleSystem atmosphereParticles;
    [SerializeField] private AudioSource narrativeAudio;

    [Header("Journey Settings")]
    [SerializeField] private bool autoStartJourney = false;
    [SerializeField] private float textRevealSpeed = 0.05f; // Seconds per character
    [SerializeField] private Color healthyAtmosphereColor = new Color(0.6f, 0.8f, 1f); // Light blue
    [SerializeField] private Color unhealthyAtmosphereColor = new Color(1f, 0.4f, 0.4f); // Light red

    // Current journey state
    private StorytellingResponse currentStory;
    private List<GameObject> activeWaypoints = new List<GameObject>();
    private string currentFocusRegion = null; // null = overview, "rbbb" = focused on RBBB

    // ECG data reference
    private float[,] ecgSignal;

    void Start()
    {
        if (autoStartJourney)
        {
            // Wait for ECGHeartController to load data first
            StartCoroutine(DelayedAutoStart());
        }
    }

    IEnumerator DelayedAutoStart()
    {
        yield return new WaitForSeconds(2f);
        StartJourney();
    }

    /// <summary>
    /// Start the storytelling journey (overview mode)
    /// </summary>
    public void StartJourney()
    {
        // Get ECG data from ECGHeartController
        ECGHeartController heartController = FindFirstObjectByType<ECGHeartController>();
        if (heartController != null)
        {
            ecgSignal = heartController.GetECGSignal();
        }

        if (ecgSignal == null)
        {
            Debug.LogError("[StorytellingJourney] No ECG data loaded. Load ECG first.");
            ShowStatus("Please load ECG data first");
            return;
        }

        // Start journey with no specific region (overview)
        StartCoroutine(FetchAndDisplayStory(null));
    }

    /// <summary>
    /// Focus journey on a specific cardiac region
    /// Called when user clicks a waypoint
    /// </summary>
    /// <param name="regionName">Backend region name (e.g., "rbbb", "sa_node")</param>
    public void FocusOnRegion(string regionName)
    {
        currentFocusRegion = regionName;
        StartCoroutine(FetchAndDisplayStory(regionName));
    }

    /// <summary>
    /// Return to overview journey mode
    /// </summary>
    public void ReturnToOverview()
    {
        currentFocusRegion = null;
        StartCoroutine(FetchAndDisplayStory(null));
    }

    /// <summary>
    /// Fetch storytelling narrative from backend
    /// </summary>
    IEnumerator FetchAndDisplayStory(string focusRegion)
    {
        ShowStatus("Generating narrative...");
        ClearWaypoints();

        yield return apiClient.AnalyzeECG(
            ecgSignal,
            outputMode: "storytelling",
            regionFocus: focusRegion,
            onSuccess: (response) =>
            {
                currentStory = response.storytelling;
                DisplayNarrative();
                CreateWaypoints();
                SetAtmosphere(response.diagnosis);
                ShowStatus("");
            },
            onError: (error) =>
            {
                Debug.LogError($"[StorytellingJourney] Failed to fetch narrative: {error}");
                ShowStatus("Failed to load narrative");
            }
        );
    }

    /// <summary>
    /// Display narrative text with typewriter effect
    /// </summary>
    void DisplayNarrative()
    {
        if (currentStory == null || narrativeText == null)
            return;

        narrativePanel.SetActive(true);

        // Stop any existing typewriter coroutine
        StopCoroutine("TypewriterEffect");

        // Start typewriter effect
        StartCoroutine(TypewriterEffect(currentStory.narrative_text));

        Debug.Log($"[StorytellingJourney] Displaying narrative ({currentStory.narrative_text.Length} chars)");
    }

    /// <summary>
    /// Typewriter text reveal effect
    /// </summary>
    IEnumerator TypewriterEffect(string fullText)
    {
        narrativeText.text = "";

        foreach (char c in fullText)
        {
            narrativeText.text += c;
            yield return new WaitForSeconds(textRevealSpeed);
        }
    }

    /// <summary>
    /// Create 3D waypoint markers at cardiac region positions
    /// </summary>
    void CreateWaypoints()
    {
        if (currentStory == null || currentStory.waypoints == null)
            return;

        foreach (var waypoint in currentStory.waypoints)
        {
            // Get region position from HeartRegionMapping
            Vector3 position = regionMapping.GetRegionPosition(waypoint.region_name);

            if (position != Vector3.zero)
            {
                // Instantiate waypoint marker
                GameObject waypointObj = Instantiate(waypointPrefab, position, Quaternion.identity);
                waypointObj.transform.SetParent(this.transform);

                // Configure waypoint component
                WaypointInteraction interaction = waypointObj.GetComponent<WaypointInteraction>();
                if (interaction != null)
                {
                    interaction.Initialize(
                        regionName: waypoint.region_name,
                        teaserText: waypoint.teaser_text,
                        journeyController: this
                    );
                }

                activeWaypoints.Add(waypointObj);

                Debug.Log($"[StorytellingJourney] Created waypoint for {waypoint.region_name} at {position}");
            }
            else
            {
                Debug.LogWarning($"[StorytellingJourney] Could not find position for region: {waypoint.region_name}");
            }
        }

        Debug.Log($"[StorytellingJourney] Created {activeWaypoints.Count} waypoints");
    }

    /// <summary>
    /// Clear all waypoint markers
    /// </summary>
    void ClearWaypoints()
    {
        foreach (GameObject waypoint in activeWaypoints)
        {
            Destroy(waypoint);
        }
        activeWaypoints.Clear();
    }

    /// <summary>
    /// Set VR atmosphere based on diagnosis
    /// Adjusts lighting, particles, and audio
    /// </summary>
    void SetAtmosphere(DiagnosisData diagnosis)
    {
        if (diagnosis == null)
            return;

        // Determine if overall heart is healthy
        bool isHealthy = true;
        foreach (var condition in diagnosis.top_conditions)
        {
            if (condition.probability > 0.5f)
            {
                isHealthy = false;
                break;
            }
        }

        // Set ambient lighting color
        if (ambientLight != null)
        {
            Color targetColor = isHealthy ? healthyAtmosphereColor : unhealthyAtmosphereColor;
            StartCoroutine(LerpLightColor(targetColor, 2f));
        }

        // Control atmosphere particles
        if (atmosphereParticles != null)
        {
            var main = atmosphereParticles.main;
            if (isHealthy)
            {
                main.startColor = new Color(0.6f, 0.8f, 1f, 0.3f); // Light blue
            }
            else
            {
                main.startColor = new Color(1f, 0.4f, 0.4f, 0.3f); // Light red
            }

            if (!atmosphereParticles.isPlaying)
                atmosphereParticles.Play();
        }

        // Optional: Play ambient audio
        if (narrativeAudio != null && narrativeAudio.clip != null)
        {
            if (!narrativeAudio.isPlaying)
                narrativeAudio.Play();
        }
    }

    /// <summary>
    /// Smoothly transition ambient light color
    /// </summary>
    IEnumerator LerpLightColor(Color targetColor, float duration)
    {
        Color startColor = ambientLight.color;
        float elapsed = 0f;

        while (elapsed < duration)
        {
            ambientLight.color = Color.Lerp(startColor, targetColor, elapsed / duration);
            elapsed += Time.deltaTime;
            yield return null;
        }

        ambientLight.color = targetColor;
    }

    /// <summary>
    /// Show status message to user
    /// </summary>
    void ShowStatus(string message)
    {
        if (statusText != null)
        {
            statusText.text = message;
            statusText.gameObject.SetActive(!string.IsNullOrEmpty(message));
        }
    }

    /// <summary>
    /// Get current narrative text (for external UI display)
    /// </summary>
    public string GetCurrentNarrative()
    {
        return currentStory?.narrative_text ?? "";
    }

    /// <summary>
    /// Check if journey is currently focused on a region
    /// </summary>
    public bool IsFocused()
    {
        return currentFocusRegion != null;
    }

    /// <summary>
    /// Get current focus region name
    /// </summary>
    public string GetCurrentFocusRegion()
    {
        return currentFocusRegion;
    }

    /// <summary>
    /// Skip typewriter effect and show full text immediately
    /// </summary>
    public void SkipTypewriter()
    {
        StopCoroutine("TypewriterEffect");
        if (currentStory != null)
        {
            narrativeText.text = currentStory.narrative_text;
        }
    }

    /// <summary>
    /// Hide narrative panel
    /// </summary>
    public void HideNarrative()
    {
        if (narrativePanel != null)
            narrativePanel.SetActive(false);
    }

    /// <summary>
    /// Show narrative panel
    /// </summary>
    public void ShowNarrative()
    {
        if (narrativePanel != null)
            narrativePanel.SetActive(true);
    }
}

// StorytellingResponse and WaypointData classes are now defined in ECGDataStructures.cs
// (removed duplicate definitions)
