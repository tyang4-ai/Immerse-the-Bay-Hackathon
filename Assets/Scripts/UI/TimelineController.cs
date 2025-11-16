using UnityEngine;
using UnityEngine.UI;
using System.Collections;
using System.Collections.Generic;
using TMPro;

/// <summary>
/// Controls VR timeline UI for ECG beat scrubbing
/// Creates beat markers and handles timeline interaction
/// Fetches beat detail when user focuses on specific beat
/// </summary>
public class TimelineController : MonoBehaviour
{
    [Header("API Client")]
    [SerializeField] private ECGAPIClient apiClient;

    [Header("Timeline UI")]
    [SerializeField] private Slider timelineSlider;
    [SerializeField] private Transform beatMarkersParent;
    [SerializeField] private GameObject beatMarkerPrefab;

    [Header("Beat Detail Panel")]
    [SerializeField] private BeatDetailPanel beatDetailPanel;

    [Header("Settings")]
    [Tooltip("Debounce time in seconds before fetching beat detail")]
    [SerializeField] private float scrubDebounceTime = 0.5f;

    [Tooltip("ECG sampling rate (Hz)")]
    [SerializeField] private float samplingRate = 400f;

    // ECG data
    private float[,] ecgSignal;

    // Beat data
    private List<int> rPeaks = new List<int>();
    private int totalBeats = 0;
    private float ecgDurationSeconds = 0f;

    // Scrubbing state
    private float lastScrubTime = 0f;
    private int pendingBeatIndex = -1;
    private Coroutine debounceCoroutine;

    // Beat markers
    private List<GameObject> beatMarkerInstances = new List<GameObject>();

    void Start()
    {
        if (apiClient == null)
            apiClient = ECGAPIClient.Instance;

        // Setup timeline slider listener
        if (timelineSlider != null)
        {
            timelineSlider.onValueChanged.AddListener(OnTimelineValueChanged);
        }
    }

    /// <summary>
    /// Initialize timeline with ECG data
    /// Fetches all beat positions from backend
    /// </summary>
    public IEnumerator InitializeTimeline(float[,] ecgData)
    {
        if (ecgData == null)
        {
            Debug.LogError("[TimelineController] ECG data is null");
            yield break;
        }

        ecgSignal = ecgData;
        ecgDurationSeconds = ecgData.GetLength(0) / samplingRate;

        Debug.Log($"[TimelineController] Initializing timeline for {ecgDurationSeconds:F2}s ECG");

        // Fetch beat positions from backend
        yield return apiClient.GetBeats(
            ecgSignal,
            onSuccess: (response) =>
            {
                rPeaks = response.r_peaks;
                totalBeats = response.beat_count;

                Debug.Log($"[TimelineController] Received {totalBeats} beats");

                // Create visual beat markers
                CreateBeatMarkers();

                // Update timeline range
                if (timelineSlider != null)
                {
                    timelineSlider.minValue = 0f;
                    timelineSlider.maxValue = ecgDurationSeconds;
                    timelineSlider.value = 0f;
                }
            },
            onError: (error) =>
            {
                Debug.LogError($"[TimelineController] Failed to get beats: {error}");
            }
        );
    }

    /// <summary>
    /// Create visual markers for each beat on timeline
    /// </summary>
    void CreateBeatMarkers()
    {
        // Clear existing markers
        ClearBeatMarkers();

        if (beatMarkerPrefab == null || beatMarkersParent == null)
        {
            Debug.LogWarning("[TimelineController] Beat marker prefab or parent not assigned");
            return;
        }

        // Get timeline width for positioning
        RectTransform timelineRect = timelineSlider?.GetComponent<RectTransform>();
        if (timelineRect == null) return;

        float timelineWidth = timelineRect.rect.width;

        // Create marker for each beat
        for (int i = 0; i < rPeaks.Count; i++)
        {
            int rPeak = rPeaks[i];
            float timeSeconds = rPeak / samplingRate;
            float normalizedPosition = timeSeconds / ecgDurationSeconds;

            // Instantiate marker
            GameObject marker = Instantiate(beatMarkerPrefab, beatMarkersParent);
            RectTransform markerRect = marker.GetComponent<RectTransform>();

            if (markerRect != null)
            {
                // Position marker along timeline
                float xPos = (normalizedPosition - 0.5f) * timelineWidth;
                markerRect.anchoredPosition = new Vector2(xPos, 0f);

                // Optional: Set marker color based on position
                Image markerImage = marker.GetComponent<Image>();
                if (markerImage != null)
                {
                    markerImage.color = Color.cyan;
                }

                beatMarkerInstances.Add(marker);
            }
        }

        Debug.Log($"[TimelineController] Created {beatMarkerInstances.Count} beat markers");
    }

    /// <summary>
    /// Clear all beat markers
    /// </summary>
    void ClearBeatMarkers()
    {
        foreach (var marker in beatMarkerInstances)
        {
            if (marker != null)
                Destroy(marker);
        }
        beatMarkerInstances.Clear();
    }

    /// <summary>
    /// Handle timeline slider value change (VR scrubbing)
    /// </summary>
    void OnTimelineValueChanged(float timeSeconds)
    {
        // Update scrub time
        lastScrubTime = Time.time;

        // Find nearest beat
        int nearestBeatIndex = FindNearestBeat(timeSeconds);
        if (nearestBeatIndex >= 0)
        {
            pendingBeatIndex = nearestBeatIndex;

            // Highlight beat marker
            HighlightBeatMarker(nearestBeatIndex);

            // Start debounce coroutine
            if (debounceCoroutine != null)
            {
                StopCoroutine(debounceCoroutine);
            }
            debounceCoroutine = StartCoroutine(DebounceAndFetchBeatDetail());
        }
    }

    /// <summary>
    /// Debounce scrubbing and fetch beat detail after user stops
    /// </summary>
    IEnumerator DebounceAndFetchBeatDetail()
    {
        yield return new WaitForSeconds(scrubDebounceTime);

        // Check if user is still scrubbing
        if (Time.time - lastScrubTime >= scrubDebounceTime && pendingBeatIndex >= 0)
        {
            // Fetch beat detail from backend
            yield return FetchBeatDetail(pendingBeatIndex);
            pendingBeatIndex = -1;
        }
    }

    /// <summary>
    /// Fetch beat detail from backend and display in panel
    /// </summary>
    IEnumerator FetchBeatDetail(int beatIndex)
    {
        if (ecgSignal == null)
        {
            Debug.LogError("[TimelineController] No ECG data loaded");
            yield break;
        }

        Debug.Log($"[TimelineController] Fetching detail for beat #{beatIndex}");

        yield return apiClient.GetBeatDetail(
            ecgSignal,
            beatIndex,
            onSuccess: (response) =>
            {
                Debug.Log($"[TimelineController] Beat detail received for beat #{beatIndex}");

                // Display in beat detail panel
                if (beatDetailPanel != null)
                {
                    beatDetailPanel.DisplayBeatDetail(response);
                }
            },
            onError: (error) =>
            {
                Debug.LogError($"[TimelineController] Failed to get beat detail: {error}");
            }
        );
    }

    /// <summary>
    /// Find nearest beat index to given time
    /// </summary>
    int FindNearestBeat(float timeSeconds)
    {
        if (rPeaks.Count == 0) return -1;

        int targetSample = Mathf.RoundToInt(timeSeconds * samplingRate);

        int nearestIndex = 0;
        int minDistance = Mathf.Abs(rPeaks[0] - targetSample);

        for (int i = 1; i < rPeaks.Count; i++)
        {
            int distance = Mathf.Abs(rPeaks[i] - targetSample);
            if (distance < minDistance)
            {
                minDistance = distance;
                nearestIndex = i;
            }
        }

        return nearestIndex;
    }

    /// <summary>
    /// Highlight specific beat marker
    /// </summary>
    void HighlightBeatMarker(int beatIndex)
    {
        // Reset all markers to default color
        foreach (var marker in beatMarkerInstances)
        {
            Image img = marker?.GetComponent<Image>();
            if (img != null)
                img.color = Color.cyan;
        }

        // Highlight selected marker
        if (beatIndex >= 0 && beatIndex < beatMarkerInstances.Count)
        {
            Image img = beatMarkerInstances[beatIndex]?.GetComponent<Image>();
            if (img != null)
                img.color = Color.yellow; // Highlighted color
        }
    }

    /// <summary>
    /// Jump to specific beat index
    /// </summary>
    public void JumpToBeat(int beatIndex)
    {
        if (beatIndex < 0 || beatIndex >= rPeaks.Count) return;

        float timeSeconds = rPeaks[beatIndex] / samplingRate;

        if (timelineSlider != null)
        {
            timelineSlider.value = timeSeconds;
        }

        StartCoroutine(FetchBeatDetail(beatIndex));
    }

    /// <summary>
    /// Get total beat count
    /// </summary>
    public int GetBeatCount()
    {
        return totalBeats;
    }

    void OnDestroy()
    {
        if (timelineSlider != null)
        {
            timelineSlider.onValueChanged.RemoveListener(OnTimelineValueChanged);
        }
    }
}
