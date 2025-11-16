# Dummy Data for Unity Development

## Purpose

This folder contains sample JSON responses that match the **exact structure** the Flask backend API will return. Use these files to develop and test the Unity VR frontend **before** the real backend is complete.

---

## Files

| File | Condition | BPM | Description |
|------|-----------|-----|-------------|
| `sample_normal.json` | Normal sinus rhythm | 72.5 | Healthy heart, all regions green |
| `sample_ecg_response.json` | Sinus bradycardia | 52.3 | Slow heart rate, mostly healthy |
| `sample_rbbb.json` | Right bundle branch block | 95.2 | Right ventricle conduction delay, red regions |
| `sample_af.json` | Atrial fibrillation | 118.7 | Irregular atrial rhythm, critical severity |

---

## JSON Structure

All files follow this structure:

```json
{
  "predictions": { ... },           // 6 condition probabilities
  "heart_rate": { ... },            // BPM, R-R intervals, beat timestamps
  "region_health": { ... },         // Per-region severity + colors
  "activation_sequence": [ ... ],   // Electrical activation timing
  "llm_interpretation": { ... },    // Claude API explanations
  "top_condition": "string",        // Most likely diagnosis
  "confidence": 0.0-1.0,            // Confidence score
  "processing_time_ms": float,      // Backend processing time
  "model_version": "1.0.0",         // Model version
  "timestamp": "ISO8601"            // Analysis timestamp
}
```

---

## How to Use in Unity

### Method 1: Load from TextAsset

1. Copy JSON files to `UnityProject/Assets/Resources/DummyData/`
2. In Unity Inspector, drag JSON files as TextAssets
3. Parse in C#:

```csharp
using UnityEngine;

public class DummyDataLoader : MonoBehaviour
{
    public TextAsset sampleNormalData;
    public TextAsset sampleRBBBData;
    public TextAsset sampleAFData;

    public void TestWithDummyData()
    {
        // Parse JSON
        string jsonText = sampleNormalData.text;
        ECGAnalysisResponse response = JsonUtility.FromJson<ECGAnalysisResponse>(jsonText);

        // Use the data
        Debug.Log($"BPM: {response.heart_rate.bpm}");
        Debug.Log($"Top Condition: {response.top_condition}");

        // Update visualizations
        HeartBeatSynchronizer beatSync = FindObjectOfType<HeartBeatSynchronizer>();
        beatSync.SetHeartRateData(response.heart_rate.bpm, response.heart_rate.beat_timestamps);

        HeartRegionColorizer colorizer = FindObjectOfType<HeartRegionColorizer>();
        colorizer.UpdateRegionColors(response.region_health);
    }
}
```

### Method 2: Mock API Server (Testing)

Use Python's built-in HTTP server to serve dummy data:

```bash
cd Backend/dummy_data
python -m http.server 8000
```

Then access files at `http://localhost:8000/sample_normal.json`

### Method 3: Unity HTTP Request

```csharp
using UnityEngine.Networking;
using System.Collections;

IEnumerator LoadDummyData(string filename)
{
    string url = $"file://{Application.dataPath}/Resources/DummyData/{filename}";

    UnityWebRequest request = UnityWebRequest.Get(url);
    yield return request.SendWebRequest();

    if (request.result == UnityWebRequest.Result.Success)
    {
        string json = request.downloadHandler.text;
        ProcessECGResponse(json);
    }
}
```

---

## Field Descriptions

### `predictions`
Dictionary of condition names → probabilities (0.0-1.0)

**Conditions:**
- `1st_degree_AV_block`: Delayed AV node conduction
- `RBBB`: Right bundle branch block
- `LBBB`: Left bundle branch block
- `sinus_bradycardia`: Slow heart rate (< 60 BPM)
- `atrial_fibrillation`: Irregular atrial rhythm
- `sinus_tachycardia`: Fast heart rate (> 100 BPM)

### `heart_rate`
- `bpm`: Beats per minute (float)
- `rr_intervals_ms`: R-R intervals in milliseconds (array)
- `beat_timestamps`: When each beat occurs in seconds (array)
- `r_peak_count`: Total number of detected heartbeats (int)

### `region_health`
Dictionary mapping region name → health data

**Regions:**
- `sa_node`: Sinoatrial node (pacemaker)
- `ra`: Right atrium
- `la`: Left atrium
- `av_node`: Atrioventricular node
- `bundle_his`: Bundle of His
- `rbbb`: Right bundle branch
- `lbbb`: Left bundle branch
- `purkinje`: Purkinje fibers
- `rv`: Right ventricle
- `lv`: Left ventricle

**Health Data:**
- `severity`: 0.0 (healthy) to 1.0 (critical)
- `color`: RGB array [r, g, b] - values 0.0-1.0
- `activation_delay_ms`: Electrical activation timing (milliseconds from SA node)
- `affected_by`: Array of condition names affecting this region

### `activation_sequence`
Array of `[region_name, delay_ms]` pairs, sorted by activation time.
Use this to animate the electrical activation wave spreading through the heart.

### `llm_interpretation`
- `plain_english_summary`: 2-3 sentence overview
- `severity_assessment.overall`: "low" | "moderate" | "high"
- `patient_explanation`: Detailed patient-friendly explanation
- `clinical_notes`: Technical medical notes
- `visualization_suggestions`: Hints for VR visualization
  - `highlight_regions`: Array of regions to emphasize
  - `recommended_view`: Suggested camera angle
  - `animation_speed`: "slow" | "normal" | "fast"
  - `color_emphasis`: Textual color recommendations

---

## Color Interpretation

**Severity → Color Mapping:**

| Severity | Color (RGB) | Hex | Health Status |
|----------|-------------|-----|---------------|
| 0.00 - 0.25 | Green → Yellow | #00FF00 → #FFFF00 | Healthy |
| 0.25 - 0.50 | Yellow → Orange | #FFFF00 → #FFA500 | Warning |
| 0.50 - 0.75 | Orange → Red | #FFA500 → #FF0000 | Concerning |
| 0.75 - 1.00 | Deep Red | #FF0000 → #CC0000 | Critical |

**Implementation:**
The `color` field in `region_health` is already calculated. Just use it directly:

```csharp
Color regionColor = new Color(
    regionData.color[0],
    regionData.color[1],
    regionData.color[2]
);
renderer.material.color = regionColor;
```

---

## Animation Timing

### Heartbeat Animation

Use `heart_rate.beat_timestamps` for precise timing:

```csharp
IEnumerator PlaybackTimedBeats(List<float> timestamps)
{
    float startTime = Time.time;
    foreach (float timestamp in timestamps)
    {
        // Wait until this beat's time
        yield return new WaitUntil(() => (Time.time - startTime) >= timestamp);

        // Trigger beat animation
        TriggerHeartBeat();
    }
}
```

### Activation Sequence Animation

Use `activation_sequence` to show electrical activation spreading:

```csharp
IEnumerator PlayActivationSequence(List<(string, float)> sequence)
{
    foreach (var (regionName, delayMs) in sequence)
    {
        yield return new WaitForSeconds(delayMs / 1000f);

        // Light up this region
        ActivateRegionGlow(regionName);
    }
}
```

---

## Testing Checklist

Test each feature with all 4 dummy data files:

- [ ] Heart beat animation syncs with BPM
  - Normal: 72.5 BPM → ~0.83s per beat
  - RBBB: 95.2 BPM → ~0.63s per beat
  - AF: 118.7 BPM → ~0.51s per beat (irregular!)

- [ ] Region colors update correctly
  - Normal: All green
  - Bradycardia: SA node orange, others yellow/green
  - RBBB: Right bundle + RV red, purkinje orange
  - AF: Both atria deep red, AV node orange

- [ ] Activation sequence plays in correct order
  - Normal: SA → atria → AV → bundles → ventricles
  - RBBB: LV activates before RV (delayed)
  - AF: Chaotic atrial activation (no order)

- [ ] LLM explanation displays
  - Summary text readable in VR
  - Severity indicator shows correct color
  - Visualization suggestions applied

- [ ] Haptic feedback
  - Fires on each beat timestamp
  - Irregular in AF case

---

## Expected Behavior by Condition

### Normal Sinus Rhythm (`sample_normal.json`)
- **Visual:** Entire heart green
- **Animation:** Smooth, regular heartbeat at 72 BPM
- **Activation:** Clean wave from SA → atria → ventricles
- **UI:** "Normal sinus rhythm" with green severity indicator

### Sinus Bradycardia (`sample_ecg_response.json`)
- **Visual:** SA node orange, other regions green/yellow
- **Animation:** Slow heartbeat at 52 BPM
- **Activation:** Normal sequence, just slower
- **UI:** "Slow heart rate" with yellow/low severity

### Right Bundle Branch Block (`sample_rbbb.json`)
- **Visual:** Right bundle branch RED, RV orange, purkinje orange
- **Animation:** Normal rate at 95 BPM
- **Activation:** Left ventricle lights up, then PAUSE, then right ventricle
- **UI:** "Right bundle branch block" with orange/moderate severity

### Atrial Fibrillation (`sample_af.json`)
- **Visual:** Both atria deep RED, AV node orange
- **Animation:** Irregular heartbeat averaging 119 BPM
- **Activation:** Chaotic flickering in atria, irregular ventricle activation
- **UI:** "Atrial fibrillation" with RED/high severity indicator

---

## Troubleshooting

**Issue:** JSON parsing fails
**Solution:** Ensure C# class structure matches JSON exactly. Use `[Serializable]` attribute and public fields.

**Issue:** Colors look wrong
**Solution:** Verify Unity is using RGB 0.0-1.0 range, not 0-255. Convert if needed: `color / 255f`

**Issue:** Animations too fast/slow
**Solution:** Check `Time.deltaTime` usage in animations. Ensure not running in FixedUpdate.

**Issue:** LLM text too long for UI
**Solution:** Use TextMeshPro with auto-sizing or scroll view. Test with AF sample (longest text).

---

## Next Steps

1. **Develop Unity scripts** using this dummy data
2. **Test all 4 conditions** to ensure robust parsing
3. **Verify VR performance** (target: 72 FPS on Quest 2)
4. **Once backend is ready**, swap dummy data loader with real API client

---

## Questions?

Contact your backend teammate if:
- JSON structure is unclear
- You need additional sample conditions
- Fields are missing that Unity needs
- Data format doesn't match Unity expectations

**Remember:** These files represent the **final API contract**. The real backend will return exactly this structure!
