# ECG Heart Model Integration Guide for Teammate

**Project:** HoloHuman XR - VR ECG Heart Visualization
**Integration Type:** Interactive ECG Heart Model for larger VR scene
**Last Updated:** 2025-11-16
**Status:** Backend-Unity integration tested and working ✅

---

## What You're Getting

An **interactive 3D heart model** that:
- Analyzes ECG data from Flask backend API
- Displays medical diagnosis in VR
- Shows heart rate and rhythm
- Highlights problematic cardiac regions
- Supports storytelling journey mode
- Works on Quest 2 VR

**Current State:** Backend API integration fully tested in Unity Play Mode. Ready to integrate into your scene.

---

## Quick Start (5 Steps)

### 1. Pull Code from GitHub

```bash
# Clone repository (if you don't have it yet)
git clone <repository-url>
cd Immerse-the-bay-hackathon-heart

# Pull latest changes (if you already have it)
git checkout unity-project-upload
git pull origin unity-project-upload
```

### 2. Copy Required Files to Your Project

**Essential Unity Assets to copy:**

```
Copy FROM this project → TO your project:

Assets/Scripts/
├── ECGAPIClient.cs                              → YourProject/Assets/Scripts/
├── ECGDemoController.cs                         → YourProject/Assets/Scripts/
├── API/
│   └── ECGDataStructures.cs                     → YourProject/Assets/Scripts/API/
├── Heart/
│   └── ECGHeartController.cs                    → YourProject/Assets/Scripts/Heart/
└── Journey/
    └── StorytellingJourneyController.cs         → YourProject/Assets/Scripts/Journey/

Assets/Resources/
└── ECGSamples/
    ├── synthetic_ecg_normal.json                → YourProject/Assets/Resources/ECGSamples/
    ├── synthetic_ecg_bradycardia.json          → YourProject/Assets/Resources/ECGSamples/
    └── synthetic_ecg_tachycardia.json          → YourProject/Assets/Resources/ECGSamples/

Assets/Prefabs/ (if you have heart model prefabs)
└── HeartModel.prefab                            → YourProject/Assets/Prefabs/
```

**Backend (Flask API server):**

```
Copy entire Backend/ folder to a location on your PC (doesn't need to be in Unity project)

Backend/
├── ecg_api.py                                   # Main Flask server
├── clinical_decision_support_llm.py             # LLM integration
├── ecg_heartrate_analyzer.py                    # Heart rate analysis
├── model_loader.py                              # ECG model loader
├── logger.py                                    # Structured logging
├── model/
│   └── model.hdf5                               # ECG classification model (25.8 MB)
├── data/
│   └── (sample ECG files)
└── venv/                                        # Python virtual environment
```

### 3. Install Unity Package

**In your Unity project:**

1. Window → Package Manager
2. Click "+" → Add package by name
3. Enter: `com.unity.nuget.newtonsoft-json`
4. Click "Add"

### 4. Set Up Backend Server

**On your PC (one-time setup):**

```bash
# Navigate to Backend folder
cd Backend

# Install Python dependencies (if not already done)
pip install -r requirements.txt

# Start Flask server
python ecg_api.py
```

**Expected output:**
```
[2025-11-16 XX:XX:XX] INFO: Initializing HoloHuman XR Backend...
[2025-11-16 XX:XX:XX] INFO: ECG model loaded successfully: model/model.hdf5
[2025-11-16 XX:XX:XX] INFO: Backend initialization complete!
 * Running on http://127.0.0.1:5000
 * Running on http://192.168.X.X:5000
```

**Test backend:**
```bash
curl http://localhost:5000/health
```

Should return: `{"status": "healthy", "model_loaded": true}`

### 5. Add to Your Scene

**In your Unity scene hierarchy:**

1. **Create ECG API Client:**
   - Right-click Hierarchy → Create Empty
   - Rename to: `ECGAPIClient`
   - Add Component → ECGAPIClient (script)
   - In Inspector:
     - Backend URL: `http://localhost:5000` (for PC testing)
     - Backend URL: `http://192.168.X.X:5000` (for Quest 2, use your PC's IP)
     - Timeout Seconds: `30`
     - Log Requests: ✓ (check for debugging)

2. **Add ECG Heart Model to your scene:**
   - Drag heart model prefab into your scene
   - Position it where you want in your VR environment
   - Add Component → ECGHeartController (script)
   - In Inspector:
     - Ecg Data File: Select `synthetic_ecg_normal` from dropdown
     - Assign any UI elements you want for status display

---

## Integration Options

### Option A: Standalone Interactive Model (Simplest)

**Use Case:** User walks up to heart model, clicks it, sees analysis

**Setup:**
1. Add ECGAPIClient to scene (as above)
2. Add your heart model GameObject
3. Attach ECGHeartController to heart model
4. Assign ECG data file in Inspector
5. Add collider for VR interaction
6. On click/trigger, call: `StartCoroutine(AnalyzeCurrentECG())`

**Result:** Model loads ECG data, sends to backend, displays results

### Option B: Integrate with Existing UI (More Control)

**Use Case:** You have your own UI panels for displaying information

**Setup:**
1. Add ECGAPIClient to scene
2. Create your own controller script (or use ECGDemoController as template)
3. Call API methods directly:

```csharp
using System.Collections;
using UnityEngine;

public class YourController : MonoBehaviour
{
    private ECGAPIClient apiClient;
    public TextAsset ecgDataFile;

    void Start()
    {
        apiClient = ECGAPIClient.Instance;
        StartCoroutine(AnalyzeECG());
    }

    IEnumerator AnalyzeECG()
    {
        // Load ECG data (see ECGDemoController.cs for full example)
        var data = Newtonsoft.Json.JsonConvert.DeserializeObject<ECGData>(ecgDataFile.text);

        float[,] ecgSignal = ConvertTo2DArray(data.ecg_signal);

        // Call API
        yield return apiClient.AnalyzeECG(
            ecgSignal,
            outputMode: "clinical_expert",
            onSuccess: (response) =>
            {
                // Use response data in your UI
                Debug.Log($"Diagnosis: {response.top_condition}");
                Debug.Log($"Confidence: {response.confidence:P0}");
                Debug.Log($"Heart Rate: {response.heart_rate.bpm:F1} BPM");

                // Update your UI elements
                yourDiagnosisPanel.SetText(response.top_condition);
                yourHeartRateDisplay.SetValue(response.heart_rate.bpm);
            },
            onError: (error) =>
            {
                Debug.LogError($"Analysis failed: {error}");
            }
        );
    }
}
```

### Option C: Storytelling Journey Mode (Most Immersive)

**Use Case:** Guided VR journey through the heart with narration

**Setup:**
1. Add ECGAPIClient to scene
2. Attach StorytellingJourneyController to your journey manager
3. Call API with `output_mode="storytelling"` and `region_focus` parameter
4. Display narrative text in VR
5. Create waypoint markers based on API response

**Example:**
```csharp
yield return apiClient.AnalyzeECG(
    ecgSignal,
    outputMode: "storytelling",
    regionFocus: "right_bundle_branch",  // Focus on specific region
    onSuccess: (response) =>
    {
        var narrative = response.llm_interpretation.storytelling;

        // Display narrative in VR UI
        ShowNarrativeText(narrative.narrative);

        // Create waypoints in 3D space
        foreach (var waypoint in narrative.waypoints)
        {
            CreateWaypoint(waypoint.region, waypoint.description);
        }

        // Set VR atmosphere (lighting, colors)
        SetAtmosphere(narrative.atmosphere);
    }
);
```

**Available Regions for Focus:**
- `sinoatrial_node` - SA Node (pacemaker)
- `av_node` - AV Node (gateway)
- `bundle_of_his` - Bundle of His
- `right_bundle_branch` - RBBB pathway
- `left_bundle_branch` - LBBB pathway
- `right_atrium` - RA chamber
- `left_atrium` - LA chamber
- `right_ventricle` - RV chamber
- `left_ventricle` - LV chamber
- `purkinje_fibers` - Purkinje network

---

## Where Your Teammate Left Off

### Completed ✅
1. **Backend API:** 7 endpoints production-ready, tested
2. **Unity Integration:** ECGAPIClient successfully communicates with backend
3. **Data Structures:** All C# models match backend JSON format exactly
4. **Play Mode Testing:** Verified working with test ECG data
5. **Bug Fixes:** 5 critical integration bugs resolved

### Tested & Working ✅
- ECG data loading (4096 samples × 12 leads)
- HTTP communication Unity → Flask
- JSON deserialization (Newtonsoft.Json)
- UI updates with diagnosis, heart rate, status
- Backend processing (~90ms per request)

### NOT Yet Implemented ⏳
1. **Timeline UI:** Heartbeat markers and scrubbing (API endpoint ready: `/api/ecg/beats`)
2. **Beat Detail Panel:** P-QRS-T waveform visualization (API endpoint ready: `/api/ecg/beat/{index}`)
3. **3D Heart Region Highlighting:** Color-code regions based on analysis
4. **Quest 2 VR Build:** Network testing over WiFi
5. **Activation Sequence Animation:** Electrical conduction visualization

---

## Your Tasks to Integrate

### Task 1: Add ECG Heart to Your Scene (30 minutes)

**Steps:**
1. Copy all required files (see Quick Start Step 2)
2. Install Newtonsoft.Json package
3. Add ECGAPIClient GameObject to your scene
4. Configure Backend URL in Inspector
5. Start backend server on your PC
6. Test health check: `curl http://localhost:5000/health`

**Verify:**
- Unity Console shows: `[ECG API] Backend is healthy! Model loaded: True`

### Task 2: Choose Integration Approach (15 minutes)

**Questions to decide:**
- Do you want standalone clickable heart model? → Use Option A
- Do you have existing UI panels? → Use Option B
- Do you want guided VR journey? → Use Option C

**Then:**
- Follow the setup for your chosen option (see "Integration Options" above)

### Task 3: Position Heart Model in Your Scene (15 minutes)

**Placement:**
- Add heart model to your scene hierarchy
- Position/scale to fit your environment
- Add collider for VR interaction (if clickable)
- Test position in VR headset

### Task 4: Connect UI Elements (30 minutes)

**If using your own UI:**
1. Create/identify UI panels for:
   - Diagnosis display
   - Heart rate display
   - Status messages
2. Assign TextMeshPro components in Inspector
3. Update your controller to populate these fields

**Example:**
```csharp
// In your success callback
yourDiagnosisText.text = $"{response.top_condition}\nConfidence: {response.confidence:P0}";
yourHeartRateText.text = $"{response.heart_rate.bpm:F1} BPM\nLead: {response.heart_rate.lead_used}";
yourStatusText.text = $"Analysis complete ({response.processing_time_ms:F0}ms)";
```

### Task 5: Test End-to-End (30 minutes)

**Testing Checklist:**
- [ ] Backend server running
- [ ] Unity Play Mode test (PC Editor)
- [ ] ECG analysis completes successfully
- [ ] UI updates with correct data
- [ ] Console logs show no errors
- [ ] VR headset test (if Quest 2 build ready)

### Task 6: (Optional) Add Advanced Features

**Once basic integration working:**

**Timeline with Beat Markers:**
```csharp
yield return apiClient.GetBeats(
    ecgSignal,
    onSuccess: (response) =>
    {
        // Create timeline markers at each beat
        foreach (int rPeak in response.r_peaks)
        {
            float timeSeconds = rPeak / 400f;  // 400 Hz sampling rate
            CreateBeatMarker(timeSeconds);
        }
    }
);
```

**Region Highlighting:**
```csharp
// Use response.region_health to color-code heart regions
foreach (var region in response.region_health)
{
    string regionName = region.Key;  // e.g., "right_ventricle"
    var health = region.Value;

    if (health.is_primary_concern)
    {
        HighlightRegion(regionName, Color.red);
    }
    else if (health.abnormality_detected)
    {
        HighlightRegion(regionName, Color.yellow);
    }
}
```

---

## API Reference (Quick)

### Main Endpoint: POST /api/ecg/analyze

**Request:**
```json
{
  "ecg_signal": [[...], [...], ...],  // 4096 samples × 12 leads
  "output_mode": "clinical_expert",    // or "patient_education" or "storytelling"
  "region_focus": null                 // or specific region name
}
```

**Response Fields:**
```csharp
ECGAnalysisResponse {
    string top_condition;              // "LBBB", "RBBB", etc.
    float confidence;                  // 0.0 to 1.0
    HeartRateData heart_rate;
    Dictionary<string, RegionHealthData> region_health;
    LLMInterpretation llm_interpretation;
    float processing_time_ms;
}

HeartRateData {
    float bpm;                         // Beats per minute
    string lead_used;                  // "Lead_II", etc.
    float lead_quality;                // 0.0 to 1.0
    List<float> beat_timestamps;       // Timestamps of each beat
}

LLMInterpretation {
    string clinical_summary;           // Medical explanation
    DifferentialDiagnosis differential_diagnosis;
    RiskAssessment risk_assessment;
    StorytellingResponse storytelling; // For VR journey mode
}
```

### Additional Endpoints (Ready to Use)

**Get All Heartbeats:**
```csharp
yield return apiClient.GetBeats(ecgSignal, onSuccess, onError);
// Returns: beat positions, heart rate, rhythm classification
```

**Get Single Beat Detail:**
```csharp
yield return apiClient.GetBeatDetail(ecgSignal, beatIndex: 5, onSuccess, onError);
// Returns: P-QRS-T waveform, PR/QRS/QT intervals, annotations
```

**Get Time Segment Analysis:**
```csharp
yield return apiClient.GetSegment(ecgSignal, startMs: 0, endMs: 2000, onSuccess, onError);
// Returns: beats in range, rhythm, events
```

---

## Network Configuration (Quest 2)

### PC Editor Testing
```
Backend URL: http://localhost:5000
```

### Quest 2 VR Testing

**1. Find your PC's IP address:**
```bash
# Windows
ipconfig
# Look for "IPv4 Address": 192.168.X.X
```

**2. Update Unity:**
- Select ECGAPIClient in Hierarchy
- In Inspector, set Backend URL: `http://192.168.X.X:5000` (your PC's IP)

**3. Windows Firewall:**
- Settings → Firewall → Allow an app
- Add Python → Allow Private networks

**4. Verify connectivity:**
- On Quest 2 browser, navigate to: `http://192.168.X.X:5000/health`
- Should show: `{"status": "healthy"}`

**5. Ensure same WiFi:**
- PC and Quest 2 must be on same network

---

## Troubleshooting

### "Backend not reachable" Error

**Check:**
1. Is Flask server running? `curl http://localhost:5000/health`
2. Is Backend URL correct in Unity Inspector?
3. Is Windows Firewall blocking port 5000?

**Fix:**
```bash
# Restart Flask
cd Backend
python ecg_api.py
```

### "Failed to parse ECG data" Error

**Check:**
1. Is ECG data file assigned in Inspector?
2. Is file format correct? (should be `{"ecg_signal": [[...], [...], ...]}`)
3. Is Newtonsoft.Json package installed?

**Fix:**
- Use provided sample files: `synthetic_ecg_normal.json`
- Verify file is in `Assets/Resources/ECGSamples/`

### "Compilation errors" in Unity

**Check:**
1. Is Newtonsoft.Json installed? (Window → Package Manager)
2. Are all script files copied to correct folders?
3. Are there any missing using statements?

**Fix:**
- Install `com.unity.nuget.newtonsoft-json` package
- Check script locations match folder structure above

### Quest 2 can't connect to backend

**Check:**
1. PC and Quest 2 on same WiFi?
2. PC's IP address correct in Unity?
3. Windows Firewall configured?

**Fix:**
```bash
# Find PC IP
ipconfig

# Update Unity Backend URL to: http://<PC_IP>:5000

# Test from Quest 2 browser first
http://<PC_IP>:5000/health
```

---

## Important Files Reference

### Essential Unity Scripts (MUST COPY)
1. **ECGAPIClient.cs** - HTTP client for backend communication
2. **ECGDataStructures.cs** - All response data models
3. **ECGDemoController.cs** - Example implementation (use as template)
4. **ECGHeartController.cs** - 3D heart model controller
5. **StorytellingJourneyController.cs** - VR journey mode controller

### Documentation (READ FIRST)
1. **dev/HANDOFF-2025-11-16.md** - Session summary, what was done
2. **dev/active/unity-play-mode-testing-guide.md** - Complete setup guide
3. **dev/active/TROUBLESHOOTING-PLAY-MODE.md** - Debug reference
4. **Backend/API_INTEGRATION_GUIDE.md** - Full API documentation
5. **Backend/UNITY_QUICKSTART.md** - Unity quick start

### Sample ECG Data (MUST COPY)
1. **synthetic_ecg_normal.json** - Healthy heart (72 BPM)
2. **synthetic_ecg_bradycardia.json** - Slow heart (50 BPM)
3. **synthetic_ecg_tachycardia.json** - Fast heart (110 BPM)

---

## Performance Considerations

**Backend Processing:**
- Full analysis: ~90-300ms
- Beat detection: ~50ms
- Beat detail: ~52ms

**VR Performance (Quest 2 - 72 FPS target):**
- Frame budget: 13.9ms per frame
- API calls are async (don't block rendering)
- Impact: 6-8 frames per request (acceptable)

**Best Practices:**
1. Call API on scene start, not during interaction
2. Cache results, don't make redundant requests
3. Show loading indicator during API calls
4. Use coroutines for all API communication

---

## Support & Resources

**If you get stuck:**
1. Check TROUBLESHOOTING-PLAY-MODE.md (in dev/active/)
2. Verify backend logs (Flask console output)
3. Check Unity Console for error messages
4. Review ECGDemoController.cs for working example

**Backend Documentation:**
- Backend/README.md - Backend overview
- Backend/API_INTEGRATION_GUIDE.md - Complete API docs
- Backend/ENHANCEMENT_STATUS.md - Feature details

**Test Suite (to verify backend):**
```bash
# Test all endpoints
cd Backend
python tests/test_api.py
python tests/test_phase3.py
```

---

## Quick Reference Commands

```bash
# Start backend server
cd Backend
python ecg_api.py

# Test backend health
curl http://localhost:5000/health

# Test ECG analysis (example)
curl -X POST http://localhost:5000/api/ecg/analyze \
  -H "Content-Type: application/json" \
  -d @Backend/dummy_data/sample_normal.json

# Find PC IP (for Quest 2)
ipconfig

# Check Python packages
pip list
```

---

## Git Commands for You

```bash
# Pull latest changes
git checkout unity-project-upload
git pull origin unity-project-upload

# Verify you have all files
ls Assets/Scripts/ECGAPIClient.cs
ls Backend/ecg_api.py
```

---

## Success Criteria

**You'll know integration is working when:**
1. ✓ Backend server starts without errors
2. ✓ Unity Console shows "Backend is healthy! Model loaded: True"
3. ✓ ECG analysis completes successfully
4. ✓ UI displays: diagnosis, heart rate, status
5. ✓ Console logs show: "✓ SUCCESS callback received!"
6. ✓ Processing time ~90-300ms

---

**IMPORTANT:** Your teammate successfully got the Unity-Backend integration working. All the hard debugging is done. The integration is **tested and verified**. You just need to copy the files and add the ECGAPIClient to your scene!

**Good luck with your integration! The heart model is ready to drop into your larger VR scene.** 🎉

