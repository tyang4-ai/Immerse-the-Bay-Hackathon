# Unity Script Annotations
**Detailed Code Explanations for HoloHuman XR**

This document provides line-by-line explanations of what each Unity script does and how it integrates with the backend.

---

## 1. ECGHeartController.cs - Main Orchestrator

### Purpose
This is the **central controller** that connects everything together. It:
- Loads ECG data from JSON files
- Calls the backend API to analyze the ECG
- Updates all UI elements (diagnosis, heart rate, status)
- Triggers heart region color changes
- Starts electrical wave animations

### Code Flow Explanation

#### Initialization (Start Method)
```csharp
void Start()
{
    // 1. GET API CLIENT
    // ECGAPIClient is a singleton - there's only one instance in the entire scene
    // If you didn't manually assign it in Inspector, this finds it automatically
    if (apiClient == null)
        apiClient = ECGAPIClient.Instance;

    // 2. VALIDATE COMPONENTS
    // Make sure you assigned the required components in Unity Inspector
    // Without HeartRegionMapping, we can't update region colors
    if (regionMapping == null)
        Debug.LogError("[ECGHeartController] HeartRegionMapping not assigned!");

    // 3. LOAD AND ANALYZE
    // If you dragged an ECG JSON file to Inspector AND checked autoAnalyzeOnStart
    // This will automatically load and analyze the ECG when you press Play
    if (ecgDataFile != null && autoAnalyzeOnStart)
    {
        LoadECGData();                    // Parse JSON → 2D array
        StartCoroutine(AnalyzeAndVisualize()); // Send to backend API
    }
}
```

#### Loading ECG Data (LoadECGData Method)
```csharp
void LoadECGData()
{
    // 1. PARSE JSON
    // Unity's JsonUtility can't parse JSON arrays directly at root level
    // So we wrap it: {"ecg_signal": [[...], [...]]} becomes {"data": {"ecg_signal": [[...]]}}
    string jsonText = "{\"data\":" + ecgDataFile.text + "}";
    ECGDataWrapper wrapper = JsonUtility.FromJson<ECGDataWrapper>(jsonText);

    // 2. VALIDATE DIMENSIONS
    // Backend expects exactly 4096 samples × 12 leads
    // If your JSON has wrong shape, this catches it before sending to API
    int samples = data.ecg_signal.Count;  // Should be 4096
    int leads = data.ecg_signal[0].Count; // Should be 12

    if (samples != 4096 || leads != 12)
    {
        Debug.LogError($"Invalid ECG shape: ({samples}, {leads})");
        return; // Don't proceed with invalid data
    }

    // 3. CONVERT TO 2D ARRAY
    // Unity C# can't send List<List<float>> directly to API
    // Convert to ecgSignal[4096, 12] for easier handling
    ecgSignal = new float[samples, leads];
    for (int i = 0; i < samples; i++)
    {
        for (int j = 0; j < leads; j++)
        {
            ecgSignal[i, j] = data.ecg_signal[i][j]; // Copy each value
        }
    }
}
```

#### Analyzing ECG (AnalyzeAndVisualize Coroutine)
```csharp
public IEnumerator AnalyzeAndVisualize()
{
    // 1. UPDATE STATUS UI
    // Show "Analyzing ECG..." text in yellow to user
    UpdateStatus("Analyzing ECG...", Color.yellow);

    // 2. CALL BACKEND API
    // This is a coroutine (async operation), so "yield return" waits for completion
    yield return apiClient.AnalyzeECG(
        ecgSignal,                        // Our 4096×12 array
        outputMode: outputMode,           // "clinical_expert" or "storytelling"
        regionFocus: null,                // null = overview, "rbbb" = focus on RBBB

        // 3. ON SUCCESS CALLBACK
        // This function runs when API returns successfully
        onSuccess: (response) =>
        {
            // a. STORE RESPONSE
            lastResponse = response; // Save for later reference

            // b. UPDATE DIAGNOSIS UI
            // Shows top condition + confidence (e.g., "Sinus Rhythm 92%")
            UpdateDiagnosis(response.diagnosis);

            // c. UPDATE HEART RATE UI
            // Shows BPM + which lead was used (e.g., "72.3 BPM - Lead II")
            UpdateHeartRate(response.heart_rate);

            // d. UPDATE REGION COLORS
            // Changes color of each cardiac region based on severity
            // Green (healthy) → Yellow → Orange → Red (severe)
            UpdateRegionVisualization(response.region_health);

            // e. START ELECTRICAL WAVE ANIMATION
            // Activates regions in sequence: SA node → Atria → AV node → etc.
            if (waveAnimator != null && response.activation_sequence != null)
            {
                StartCoroutine(waveAnimator.AnimateActivationSequence(
                    response.activation_sequence,  // [[\"sa_node\", 0], [\"ra\", 25], ...]
                    regionMapping                   // Needed to find each region
                ));
            }

            // f. DISPLAY CLINICAL INTERPRETATION
            // If backend provided text explanation, show it
            if (!string.IsNullOrEmpty(response.clinical_interpretation))
            {
                UpdateInterpretation(response.clinical_interpretation);
            }
        },

        // 4. ON ERROR CALLBACK
        // This function runs if API call fails (network error, server down, etc.)
        onError: (error) =>
        {
            UpdateStatus("✗ Analysis failed", Color.red);
            Debug.LogError($"ECG Analysis failed: {error}");

            // Show error in diagnosis panel
            if (diagnosisText != null)
                diagnosisText.text = $"<color=red>Error:</color>\n{error}";
        }
    );
}
```

#### Updating Region Visualization
```csharp
void UpdateRegionVisualization(Dictionary<string, RegionHealthData> regionHealthData)
{
    // WHAT THIS DOES:
    // Backend returns health data for each of 10 regions:
    // {
    //   "sa_node": {"severity": 0.0, "color": [0, 1, 0]},  // Green (healthy)
    //   "rbbb": {"severity": 0.89, "color": [1, 0, 0]},    // Red (severe)
    //   ...
    // }
    //
    // This passes all 10 regions to HeartRegionMapping
    // Which looks up each CardiacRegionMarker and updates its color/glow
    regionMapping.UpdateAllRegions(regionHealthData);
}
```

---

## 2. HeartRegionMapping.cs - Region Registry

### Purpose
This script maintains a **centralized lookup table** of all 10 cardiac regions. Instead of searching the scene every time we need a region, we build a dictionary once at startup for fast access.

### Code Flow Explanation

#### Building the Lookup Dictionary (InitializeRegionLookup)
```csharp
private void InitializeRegionLookup()
{
    // WHAT THIS DOES:
    // You manually assign 10 regions in Unity Inspector (heartRegions array)
    // This loops through and builds a fast lookup dictionary

    regionLookup.Clear(); // Start fresh

    // LOOP THROUGH EACH REGION
    foreach (var region in heartRegions)
    {
        // 1. GET THE CardiacRegionMarker COMPONENT
        // Each region GameObject should have this script attached
        CardiacRegionMarker marker = region.regionObject.GetComponent<CardiacRegionMarker>();

        if (marker != null)
        {
            // 2. USE THE MARKER'S regionName AS KEY
            // Important: We use marker.regionName (not region.regionName)
            // This ensures it matches what you set in CardiacRegionMarker Inspector
            string key = marker.regionName; // e.g., "sa_node"

            // 3. ADD TO DICTIONARY
            // Now we can find this region instantly: regionLookup["sa_node"]
            if (!regionLookup.ContainsKey(key))
            {
                regionLookup[key] = marker;
                Debug.Log($"Registered region: {key}");
            }
            else
            {
                // ERROR: You have two regions with same name!
                Debug.LogWarning($"Duplicate region name: {key}");
            }
        }
    }
}
```

#### Updating All Regions (UpdateAllRegions)
```csharp
public void UpdateAllRegions(Dictionary<string, RegionHealthData> regionHealthData)
{
    // WHAT THIS DOES:
    // Backend sends health data for each region:
    // {
    //   "sa_node": {severity: 0.0, color: [0, 1, 0], ...},
    //   "rbbb": {severity: 0.89, color: [1, 0, 0], ...},
    //   ...
    // }
    //
    // We loop through this dictionary and update each region's visualization

    foreach (var kvp in regionHealthData) // kvp = Key-Value Pair
    {
        string regionName = kvp.Key;       // "rbbb"
        RegionHealthData healthData = kvp.Value; // {severity: 0.89, color: [1,0,0]}

        // 1. FIND THE REGION
        CardiacRegionMarker region = GetRegion(regionName); // Looks up in dictionary

        if (region != null)
        {
            // 2. CONVERT BACKEND COLOR TO UNITY COLOR
            // Backend sends RGB as array [0.0-1.0, 0.0-1.0, 0.0-1.0]
            // Unity needs Color(r, g, b)
            Color regionColor = new Color(
                healthData.color[0], // Red channel
                healthData.color[1], // Green channel
                healthData.color[2]  // Blue channel
            );

            // 3. UPDATE THE REGION'S VISUALIZATION
            // This changes the glow color, light intensity, and particle emission
            region.UpdateVisualization(healthData.severity, regionColor);
        }
    }
}
```

#### Validating Regions (ValidateRegions)
```csharp
private void ValidateRegions()
{
    // WHAT THIS DOES:
    // Checks that you assigned all 10 required regions in Unity Inspector
    // If any are missing, prints error messages so you know what to fix

    string[] requiredRegions = new string[]
    {
        "sa_node", "ra", "la", "av_node", "bundle_his",
        "rbbb", "lbbb", "purkinje", "rv", "lv"
    };

    int missingCount = 0;

    // CHECK EACH REQUIRED REGION
    foreach (string regionName in requiredRegions)
    {
        if (!regionLookup.ContainsKey(regionName))
        {
            // ERROR: You forgot to assign this region in Inspector!
            Debug.LogError($"Missing required region: {regionName}");
            missingCount++;
        }
    }

    // PRINT RESULT
    if (missingCount == 0)
        Debug.Log("✓ All 10 cardiac regions configured correctly");
    else
        Debug.LogError($"✗ {missingCount} regions missing! Check Inspector.");
}
```

---

## 3. ElectricalWaveAnimator.cs - Wave Animation

### Purpose
Animates the **electrical signal propagating through the heart** in the correct sequence and timing from the backend API.

### Code Flow Explanation

#### Main Animation Loop (AnimateSequenceInternal)
```csharp
private IEnumerator AnimateSequenceInternal(
    List<List<object>> activationSequence,
    HeartRegionMapping regionMapping)
{
    // WHAT activationSequence IS:
    // Backend sends timing for each region activation:
    // [
    //   ["sa_node", 0],        // SA node fires at 0ms
    //   ["ra", 25],            // Right atrium at 25ms
    //   ["la", 30],            // Left atrium at 30ms
    //   ["av_node", 50],       // AV node at 50ms
    //   ["bundle_his", 100],   // Bundle of His at 100ms
    //   ...
    // ]

    do // Loop if loopAnimation = true
    {
        CardiacRegionMarker previousRegion = null;
        float previousActivationTime = 0f; // Track last activation time

        // LOOP THROUGH EACH ACTIVATION STEP
        foreach (var step in activationSequence)
        {
            // 1. PARSE THE STEP
            string regionName = step[0].ToString();    // "sa_node"
            float delayMs = float.Parse(step[1].ToString()); // 0

            // 2. CALCULATE DELAY FROM PREVIOUS ACTIVATION
            // If previous was at 25ms and current is at 50ms, delay = 25ms
            float delayFromPrevious = (delayMs - previousActivationTime) / 1000f; // Convert to seconds
            delayFromPrevious = Mathf.Max(0, delayFromPrevious); // Never negative

            // 3. APPLY ANIMATION SPEED
            // animationSpeed = 2.0 means 2x faster
            float adjustedDelay = delayFromPrevious / animationSpeed;

            // 4. WAIT FOR THE CORRECT TIME
            if (adjustedDelay > 0)
            {
                yield return new WaitForSeconds(adjustedDelay);
            }

            // 5. GET THE REGION
            CardiacRegionMarker currentRegion = regionMapping.GetRegion(regionName);

            if (currentRegion != null)
            {
                // 6. TRIGGER ELECTRICAL WAVE
                // This plays particles, glows, and pulses
                currentRegion.TriggerElectricalWave();

                // 7. PULSE THE GLOW
                // Makes the light flash brighter temporarily
                StartCoroutine(currentRegion.PulseGlow(pulseDuration / animationSpeed));

                // 8. SHOW CONNECTION LINE TO PREVIOUS REGION
                // Draw a yellow line from previous region to current region
                if (showConnectionLines && previousRegion != null)
                {
                    StartCoroutine(ShowConnectionLine(
                        previousRegion.GetPosition(),    // From previous
                        currentRegion.GetPosition(),     // To current
                        lineDisplayDuration / animationSpeed // Duration
                    ));
                }

                // 9. UPDATE PREVIOUS REGION
                previousRegion = currentRegion;
            }

            previousActivationTime = delayMs; // Update for next iteration
        }

        // 10. WAIT BEFORE LOOPING
        if (loopAnimation)
        {
            yield return new WaitForSeconds(loopDelay / animationSpeed);
        }

    } while (loopAnimation); // Repeat if enabled
}
```

#### Drawing Connection Lines (ShowConnectionLine)
```csharp
private IEnumerator ShowConnectionLine(Vector3 startPos, Vector3 endPos, float duration)
{
    // WHAT THIS DOES:
    // Draws a yellow line from one region to another, then fades it out

    // 1. GET LINE RENDERER FROM POOL
    // We reuse LineRenderers instead of creating new ones (better performance)
    LineRenderer line = GetLineFromPool();
    if (line == null) yield break; // No line available

    // 2. CONFIGURE LINE
    line.gameObject.SetActive(true); // Turn on
    line.positionCount = 2;           // 2 points (start and end)
    line.SetPosition(0, startPos);   // Start at previous region
    line.SetPosition(1, endPos);     // End at current region

    // 3. FADE OUT ANIMATION
    float elapsed = 0f;
    Color startColor = new Color(1f, 1f, 0f, 1f); // Yellow opaque
    Color endColor = new Color(1f, 1f, 0f, 0f);   // Yellow transparent

    while (elapsed < duration)
    {
        elapsed += Time.deltaTime; // Increment by frame time
        float t = elapsed / duration; // 0.0 → 1.0 over duration

        // LERP (Linear Interpolation) between start and end color
        Color currentColor = Color.Lerp(startColor, endColor, t);
        line.startColor = currentColor;
        line.endColor = currentColor;

        yield return null; // Wait one frame
    }

    // 4. RETURN TO POOL
    line.gameObject.SetActive(false); // Hide for reuse
}
```

---

## 4. TimelineController.cs - Beat Scrubbing

### Purpose
Allows users to **scrub through ECG beats** on a timeline slider and view detailed information about each beat.

### Code Flow Explanation

#### Initializing Timeline (InitializeTimeline)
```csharp
public IEnumerator InitializeTimeline(float[,] ecgData)
{
    // WHAT THIS DOES:
    // Fetches all heartbeat positions from backend and creates visual markers

    ecgSignal = ecgData;
    ecgDurationSeconds = ecgData.GetLength(0) / samplingRate; // 4096 samples ÷ 400 Hz = 10.24s

    // 1. CALL BACKEND /api/ecg/beats ENDPOINT
    yield return apiClient.GetBeats(
        ecgSignal,
        onSuccess: (response) =>
        {
            // 2. STORE R-PEAK POSITIONS
            // response.r_peaks = [324, 736, 1148, 1560, ...] (sample indices)
            rPeaks = response.r_peaks;
            totalBeats = response.beat_count; // e.g., 23 beats

            // 3. CREATE VISUAL MARKERS
            // Places a small icon/marker at each beat position on timeline
            CreateBeatMarkers();

            // 4. CONFIGURE TIMELINE SLIDER
            if (timelineSlider != null)
            {
                timelineSlider.minValue = 0f;              // Start at 0 seconds
                timelineSlider.maxValue = ecgDurationSeconds; // End at 10.24 seconds
                timelineSlider.value = 0f;                 // Start at beginning
            }
        }
    );
}
```

#### Creating Beat Markers (CreateBeatMarkers)
```csharp
void CreateBeatMarkers()
{
    // WHAT THIS DOES:
    // Creates visual markers (small icons) at each heartbeat position on timeline UI

    // 1. CLEAR OLD MARKERS
    ClearBeatMarkers(); // Remove any existing markers

    // 2. GET TIMELINE WIDTH
    RectTransform timelineRect = timelineSlider?.GetComponent<RectTransform>();
    float timelineWidth = timelineRect.rect.width; // e.g., 800 pixels

    // 3. CREATE MARKER FOR EACH BEAT
    for (int i = 0; i < rPeaks.Count; i++)
    {
        int rPeak = rPeaks[i];                  // e.g., 736 (sample index)
        float timeSeconds = rPeak / samplingRate; // 736 ÷ 400 = 1.84 seconds
        float normalizedPosition = timeSeconds / ecgDurationSeconds; // 1.84 ÷ 10.24 = 0.18 (18% along timeline)

        // 4. INSTANTIATE MARKER PREFAB
        GameObject marker = Instantiate(beatMarkerPrefab, beatMarkersParent);
        RectTransform markerRect = marker.GetComponent<RectTransform>();

        if (markerRect != null)
        {
            // 5. POSITION MARKER ALONG TIMELINE
            // normalizedPosition 0.0 → left end, 1.0 → right end
            float xPos = (normalizedPosition - 0.5f) * timelineWidth;
            markerRect.anchoredPosition = new Vector2(xPos, 0f);

            // 6. SET MARKER COLOR
            Image markerImage = marker.GetComponent<Image>();
            if (markerImage != null)
            {
                markerImage.color = Color.cyan; // Default beat marker color
            }

            beatMarkerInstances.Add(marker); // Track for later cleanup
        }
    }
}
```

#### Handling Timeline Scrubbing (OnTimelineValueChanged)
```csharp
void OnTimelineValueChanged(float timeSeconds)
{
    // WHAT THIS DOES:
    // User drags timeline slider → find nearest beat → wait 0.5s → fetch beat detail

    // 1. UPDATE SCRUB TIME
    lastScrubTime = Time.time; // Record when user last moved slider

    // 2. FIND NEAREST BEAT
    int nearestBeatIndex = FindNearestBeat(timeSeconds);

    if (nearestBeatIndex >= 0)
    {
        // 3. STORE PENDING BEAT INDEX
        pendingBeatIndex = nearestBeatIndex;

        // 4. HIGHLIGHT BEAT MARKER
        HighlightBeatMarker(nearestBeatIndex); // Change color to yellow

        // 5. START DEBOUNCE COROUTINE
        // This waits 0.5s before calling API (avoids spamming API while scrubbing)
        if (debounceCoroutine != null)
        {
            StopCoroutine(debounceCoroutine); // Cancel previous wait
        }
        debounceCoroutine = StartCoroutine(DebounceAndFetchBeatDetail());
    }
}
```

#### Debouncing API Calls (DebounceAndFetchBeatDetail)
```csharp
IEnumerator DebounceAndFetchBeatDetail()
{
    // WHAT THIS DOES:
    // Waits 0.5 seconds after user stops scrubbing, then fetches beat detail

    // 1. WAIT FOR DEBOUNCE TIME
    yield return new WaitForSeconds(scrubDebounceTime); // Wait 0.5s

    // 2. CHECK IF USER STOPPED SCRUBBING
    // If user moved slider again during wait, Time.time - lastScrubTime < 0.5
    if (Time.time - lastScrubTime >= scrubDebounceTime && pendingBeatIndex >= 0)
    {
        // 3. USER STOPPED → FETCH BEAT DETAIL
        yield return FetchBeatDetail(pendingBeatIndex);
        pendingBeatIndex = -1; // Clear pending
    }
}
```

#### Fetching Beat Detail (FetchBeatDetail)
```csharp
IEnumerator FetchBeatDetail(int beatIndex)
{
    // WHAT THIS DOES:
    // Calls /api/ecg/beat/{index} to get P-QRS-T intervals for focused beat

    // 1. CALL BACKEND API
    yield return apiClient.GetBeatDetail(
        ecgSignal,
        beatIndex,  // e.g., 5 (5th heartbeat)
        onSuccess: (response) =>
        {
            // 2. RESPONSE CONTAINS:
            // - beat_index: 5
            // - intervals: {pr_interval_ms: 160, qrs_duration_ms: 90, qt_interval_ms: 380}
            // - annotations: ["Normal sinus beat"]
            // - raw_samples: {lead_II: [...]}
            // - waveform_components: {p_wave: [start, end], qrs_complex: [start, end], ...}

            // 3. DISPLAY IN BEAT DETAIL PANEL
            if (beatDetailPanel != null)
            {
                beatDetailPanel.DisplayBeatDetail(response);
            }
        }
    );
}
```

---

## 5. StorytellingJourneyController.cs - Narrative Mode

### Purpose
Creates an **immersive storytelling experience** by displaying medical narratives and placing interactive 3D waypoints at cardiac regions.

### Code Flow Explanation

#### Fetching Narrative (FetchAndDisplayStory)
```csharp
IEnumerator FetchAndDisplayStory(string focusRegion)
{
    // WHAT THIS DOES:
    // Calls backend with output_mode="storytelling" to get narrative text and waypoints

    // 1. CLEAR OLD WAYPOINTS
    ClearWaypoints(); // Remove previous waypoints from scene

    // 2. CALL BACKEND API
    yield return apiClient.AnalyzeECG(
        ecgSignal,
        outputMode: "storytelling",  // Request narrative instead of clinical data
        focusRegion: focusRegion,    // null = overview, "rbbb" = focus on RBBB
        onSuccess: (response) =>
        {
            // 3. RESPONSE CONTAINS:
            // response.storytelling = {
            //   narrative_text: "The heart's electrical system begins at the SA node...",
            //   waypoints: [
            //     {region_name: "rbbb", teaser_text: "Right Bundle Branch: Delayed activation"},
            //     {region_name: "lv", teaser_text: "Left Ventricle: Compensating for delay"},
            //     ...
            //   ]
            // }

            currentStory = response.storytelling;

            // 4. DISPLAY NARRATIVE TEXT
            DisplayNarrative(); // Shows text with typewriter effect

            // 5. CREATE 3D WAYPOINTS
            CreateWaypoints(); // Spawn waypoint markers in 3D space

            // 6. SET ATMOSPHERE
            SetAtmosphere(response.diagnosis); // Change lighting/particles
        }
    );
}
```

#### Displaying Narrative (TypewriterEffect)
```csharp
IEnumerator TypewriterEffect(string fullText)
{
    // WHAT THIS DOES:
    // Reveals text character-by-character like a typewriter

    narrativeText.text = ""; // Start with empty text

    // LOOP THROUGH EACH CHARACTER
    foreach (char c in fullText)
    {
        narrativeText.text += c; // Add one character
        yield return new WaitForSeconds(textRevealSpeed); // Wait 0.05s (configurable)
    }

    // Example:
    // Frame 1: ""
    // Frame 2: "T"
    // Frame 3: "Th"
    // Frame 4: "The"
    // Frame 5: "The "
    // Frame 6: "The h"
    // ...
}
```

#### Creating Waypoints (CreateWaypoints)
```csharp
void CreateWaypoints()
{
    // WHAT THIS DOES:
    // Backend sends waypoint data, we create 3D markers at those locations

    // LOOP THROUGH EACH WAYPOINT
    foreach (var waypoint in currentStory.waypoints)
    {
        // waypoint = {region_name: "rbbb", teaser_text: "Right Bundle Branch: Delayed"}

        // 1. GET REGION POSITION FROM HEART MODEL
        Vector3 position = regionMapping.GetRegionPosition(waypoint.region_name);
        // Returns (0.04, -0.05, 0.00) for RBBB, for example

        if (position != Vector3.zero)
        {
            // 2. INSTANTIATE WAYPOINT PREFAB AT REGION
            GameObject waypointObj = Instantiate(waypointPrefab, position, Quaternion.identity);
            waypointObj.transform.SetParent(this.transform);

            // 3. INITIALIZE WAYPOINT INTERACTION
            WaypointInteraction interaction = waypointObj.GetComponent<WaypointInteraction>();
            if (interaction != null)
            {
                interaction.Initialize(
                    regionName: waypoint.region_name,   // "rbbb"
                    teaserText: waypoint.teaser_text,   // "Right Bundle Branch: Delayed"
                    journeyController: this              // Reference back to this controller
                );
            }

            activeWaypoints.Add(waypointObj); // Track for later cleanup
        }
    }
}
```

#### Setting Atmosphere (SetAtmosphere)
```csharp
void SetAtmosphere(DiagnosisData diagnosis)
{
    // WHAT THIS DOES:
    // Changes VR environment lighting/particles based on heart health

    // 1. DETERMINE IF HEART IS HEALTHY
    bool isHealthy = true;
    foreach (var condition in diagnosis.top_conditions)
    {
        if (condition.probability > 0.5f) // If any condition > 50% probability
        {
            isHealthy = false; // Heart has issues
            break;
        }
    }

    // 2. SET LIGHTING COLOR
    if (ambientLight != null)
    {
        Color targetColor = isHealthy
            ? healthyAtmosphereColor    // Light blue (0.6, 0.8, 1.0)
            : unhealthyAtmosphereColor; // Light red (1.0, 0.4, 0.4)

        // Smoothly transition to new color over 2 seconds
        StartCoroutine(LerpLightColor(targetColor, 2f));
    }

    // 3. CHANGE PARTICLE COLOR
    if (atmosphereParticles != null)
    {
        var main = atmosphereParticles.main;
        main.startColor = isHealthy
            ? new Color(0.6f, 0.8f, 1f, 0.3f)  // Light blue particles
            : new Color(1f, 0.4f, 0.4f, 0.3f); // Light red particles
    }
}
```

---

## 6. WaypointInteraction.cs - VR Waypoint Clicks

### Purpose
Handles **VR controller interaction** with waypoint markers (hover, click).

### Code Flow Explanation

#### Setting Up Interaction (Awake)
```csharp
void Awake()
{
    // 1. GET XR INTERACTION COMPONENT
    // This component detects VR ray pointer hover/click events
    interactable = GetComponent<XRSimpleInteractable>();

    // 2. REGISTER EVENT LISTENERS
    if (interactable != null)
    {
        // When VR ray pointer starts hovering
        interactable.hoverEntered.AddListener(OnHoverEnter);

        // When VR ray pointer stops hovering
        interactable.hoverExited.AddListener(OnHoverExit);

        // When user clicks with VR controller trigger
        interactable.selectEntered.AddListener(OnClick);
    }

    // 3. INITIALIZE VISUAL STATE
    if (waypointLight != null)
    {
        waypointLight.color = idleColor; // Light blue when idle
        waypointLight.intensity = glowIntensity; // Glow strength
    }
}
```

#### Hover Effect (OnHoverEnter)
```csharp
void OnHoverEnter(HoverEnterEventArgs args)
{
    // WHAT THIS DOES:
    // User points VR controller ray at waypoint → show hover effects

    isHovered = true;

    // 1. SHOW GLOW EFFECT
    if (hoverGlowEffect != null)
    {
        hoverGlowEffect.SetActive(true); // Turn on particle system or halo
    }

    // 2. CHANGE LIGHT COLOR
    if (waypointLight != null)
    {
        waypointLight.color = hoverColor; // Light blue → Gold
        waypointLight.intensity = glowIntensity * 1.5f; // Brighter
    }

    // 3. SHOW TEASER TEXT PANEL
    if (teaserPanel != null && teaserTextUI != null)
    {
        teaserTextUI.text = teaserText; // "Right Bundle Branch: Delayed activation"
        teaserPanel.SetActive(true); // Show floating text panel
    }

    // 4. SCALE UP SLIGHTLY
    transform.localScale = originalScale * 1.2f; // Grow 20%
}
```

#### Click Handler (OnClick)
```csharp
void OnClick(SelectEnterEventArgs args)
{
    // WHAT THIS DOES:
    // User clicks waypoint with VR controller → drill down to that region's story

    if (journeyController == null)
    {
        Debug.LogWarning("No journey controller assigned!");
        return;
    }

    // 1. TRIGGER REGIONAL DRILL-DOWN
    // This calls FetchAndDisplayStory("rbbb") to get focused narrative
    journeyController.FocusOnRegion(regionName);

    // 2. PLAY CLICK SOUND
    PlayClickSound(); // Audio feedback

    // 3. VISUAL FEEDBACK
    StartCoroutine(ClickFeedback()); // Brief white flash
}
```

#### Billboard Effect (Update)
```csharp
void Update()
{
    // WHAT THIS DOES:
    // Makes teaser panel always face the camera (billboard effect)

    // 1. IDLE PULSE ANIMATION
    if (isPulsing && !isHovered)
    {
        float pulse = Mathf.Sin(Time.time * pulseSpeed) * pulseAmplitude;
        float scale = baseScale + pulse; // Oscillate between 1.0 and 1.2
        transform.localScale = originalScale * scale;
    }

    // 2. BILLBOARD TEASER PANEL
    if (teaserPanel != null && teaserPanel.activeSelf)
    {
        Camera mainCamera = Camera.main;
        if (mainCamera != null)
        {
            // Make panel look at camera
            teaserPanel.transform.LookAt(mainCamera.transform);

            // Flip 180° so text reads correctly
            teaserPanel.transform.Rotate(0, 180, 0);
        }
    }
}
```

---

## Summary of Data Flow

### Complete Integration Flow:

```
1. USER PRESSES PLAY IN UNITY
   ↓
2. ECGHeartController.Start()
   ├─ Loads sample_normal.json
   ├─ Parses JSON → float[4096, 12]
   └─ Calls AnalyzeAndVisualize()
      ↓
3. ECGAPIClient.AnalyzeECG()
   ├─ Sends POST to http://localhost:5000/api/ecg/analyze
   ├─ Body: {"ecg_signal": [[...]], "output_mode": "clinical_expert"}
   └─ Waits for response...
      ↓
4. BACKEND PROCESSES ECG
   ├─ TensorFlow model predicts: "Sinus Rhythm" 92%
   ├─ Calculates heart rate: 72.3 BPM (Lead II)
   ├─ Maps conditions to regions:
   │   sa_node: severity 0.0, color [0, 1, 0] (green)
   │   rbbb: severity 0.89, color [1, 0, 0] (red)
   │   ...
   └─ Returns JSON response
      ↓
5. ECGHeartController RECEIVES RESPONSE
   ├─ Updates diagnosisText: "Sinus Rhythm 92%"
   ├─ Updates heartRateText: "72.3 BPM - Lead II"
   └─ Calls HeartRegionMapping.UpdateAllRegions()
      ↓
6. HeartRegionMapping.UpdateAllRegions()
   ├─ Loops through 10 regions
   └─ For each region:
      ├─ Converts color [1, 0, 0] → Color(1, 0, 0)
      └─ Calls CardiacRegionMarker.UpdateVisualization()
         ↓
7. CardiacRegionMarker.UpdateVisualization()
   ├─ Sets light color to red
   ├─ Sets light intensity based on severity (0.89 * 3.0 = 2.67)
   └─ Sets particle emission rate (0.89 * 50 = 44.5 particles/sec)
      ↓
8. ElectricalWaveAnimator STARTS
   ├─ Reads activation_sequence: [["sa_node", 0], ["ra", 25], ...]
   └─ Animates each region in order
      ↓
9. USER SEES:
   ├─ Heart regions change color (green/yellow/orange/red)
   ├─ Electrical wave animates SA→Atria→AV→Bundle→Ventricles
   ├─ Diagnosis panel shows "Sinus Rhythm 92%"
   └─ Heart rate panel shows "72.3 BPM"
```

---

**Document Version:** 1.0
**Last Updated:** 2025-11-15
