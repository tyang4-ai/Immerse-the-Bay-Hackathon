# Quick Unity Setup Guide
**5-Minute Integration Test**
**HoloHuman XR - Immerse the Bay 2025**

This guide gets you from Unity scripts to a working backend connection in 5 minutes.

---

## Prerequisites

- [ ] Unity project open (unity-project-upload workspace)
- [ ] All scripts copied to Assets/Scripts/ (already done via git)
- [ ] Flask backend running (`cd Backend && python ecg_api.py`)
- [ ] ECG sample files in Assets/Resources/ECGSamples/ (run copy_ecg_samples_to_unity.bat)

---

## Step 1: Create Test Scene (1 minute)

1. **Open any scene** (BasicScene.unity or create new)

---

## Step 2: Create ECG API Client GameObject (30 seconds)

1. **Create empty GameObject:**
   - Hierarchy → Right-click → Create Empty
   - Rename to: `ECG API Client`

2. **Add ECGAPIClient script:**
   - Select "ECG API Client" GameObject
   - Inspector → Add Component → Search "ECGAPIClient"
   - Click "ECG API Client" script

3. **Configure settings:**
   - Backend URL: `http://localhost:5000` (for PC testing)
   - Log Requests: ✓ (checked)
   - Timeout Seconds: 30

---

## Step 3: Create UI Canvas (1 minute)

1. **Create Canvas:**
   - Hierarchy → Right-click → UI → Canvas
   - Rename to: `ECG Results UI`

2. **Create 3 TextMeshPro texts:**

   **Diagnosis Text:**
   - Canvas → Right-click → UI → Text - TextMeshPro
   - Rename: `DiagnosisText`
   - Position: X=0, Y=100, Z=0
   - Width: 400, Height: 100
   - Font Size: 24
   - Alignment: Center
   - Text: "Waiting for analysis..."

   **Heart Rate Text:**
   - Canvas → Right-click → UI → Text - TextMeshPro
   - Rename: `HeartRateText`
   - Position: X=0, Y=0, Z=0
   - Width: 400, Height: 80
   - Font Size: 20
   - Alignment: Center
   - Text: "-- BPM"

   **Status Text:**
   - Canvas → Right-click → UI → Text - TextMeshPro
   - Rename: `StatusText`
   - Position: X=0, Y=-100, Z=0
   - Width: 600, Height: 60
   - Font Size: 16
   - Alignment: Center
   - Text: "Ready"

---

## Step 4: Create Demo Controller (1 minute)

1. **Create empty GameObject:**
   - Hierarchy → Right-click → Create Empty
   - Rename to: `Demo Controller`

2. **Add ECGDemoController script:**
   - Select "Demo Controller"
   - Inspector → Add Component → Search "ECGDemoController"

3. **Assign references:**
   - ECG Data File: **Drag** `Assets/Resources/ECGSamples/sample_normal` from Project window
   - Diagnosis Text: **Drag** DiagnosisText from Hierarchy
   - Heart Rate Text: **Drag** HeartRateText from Hierarchy
   - Status Text: **Drag** StatusText from Hierarchy

---

## Step 5: Test! (30 seconds)

1. **Verify Flask server is running:**
   - Check console for: "Running on http://127.0.0.1:5000"
   - OR run: `cd Backend && python ecg_api.py`

2. **Press Play in Unity:**
   - Click Play button (top center)

3. **Watch Console window:**
   - Should see: `[ECG API] Backend is healthy! Model loaded: True`
   - Should see: `[ECG API] POST /api/ecg/analyze (mode: clinical_expert)`
   - Should see: `=== ECG Analysis Results ===`

4. **Check UI (Game view):**
   - Diagnosis Text should show: "sinus_bradycardia" or detected condition
   - Heart Rate Text should show: "~72 BPM"
   - Status Text should show: "✓ Analysis complete (XXXms)"

---

## Expected Console Output

```
[ECG API] Backend is healthy! Model loaded: True
ECG loaded: 4096 samples × 12 leads
[ECG API] POST /api/ecg/analyze (mode: clinical_expert)
=== ECG Analysis Results ===
Diagnosis: sinus_bradycardia (78%)
Heart Rate: 72.5 BPM
Processing Time: 260.2ms

Clinical Interpretation:
This ECG demonstrates sinus bradycardia with a heart rate of 72 BPM.
The electrical conduction through the heart follows the normal pathway...
[rest of LLM interpretation]
```

---

## Troubleshooting

### Issue: "Backend not reachable"
**Fix:**
1. Open new terminal
2. `cd Backend`
3. `python ecg_api.py`
4. Verify: http://localhost:5000/health opens in browser

### Issue: "ECG data file not assigned"
**Fix:**
1. Select Demo Controller in Hierarchy
2. Inspector → ECG Data File field
3. Drag `Resources/ECGSamples/sample_normal` from Project window
4. Should show as TextAsset

### Issue: "NullReferenceException: diagnosisText"
**Fix:**
1. Select Demo Controller
2. Verify all 3 text fields are assigned in Inspector
3. Drag UI text GameObjects from Hierarchy to Inspector slots

### Issue: "The namespace 'TMPro' could not be found"
**Fix:**
1. Window → Package Manager
2. Search "TextMesh Pro"
3. Click Import TMP Essentials
4. Restart Unity

---

## Next Steps After Successful Test

### Advanced Integration (ECGHeartController)

Once basic test works, create full heart visualization:

1. **Create Controllers GameObject:**
   - Add ECGHeartController script
   - Assign all references (API client, region mapping, etc.)

2. **Create 10 Heart Region GameObjects:**
   - Each with CardiacRegionMarker script
   - Set regionName: sa_node, ra, la, av_node, etc.

3. **Setup Region Mapping:**
   - Create GameObject with HeartRegionMapping script
   - Assign all 10 region GameObjects

4. **Test full pipeline:**
   - Press Play
   - Watch regions light up based on analysis

---

## Files Summary

**Required in Unity Project:**
```
Assets/
├── Resources/
│   └── ECGSamples/
│       ├── sample_normal.json     ← REQUIRED
│       ├── sample_rbbb.json
│       └── sample_af.json
├── Scripts/
│   ├── ECGAPIClient.cs            ← REQUIRED
│   ├── ECGDemoController.cs       ← REQUIRED
│   └── API/ECGDataStructures.cs   ← REQUIRED
└── Scenes/
    └── BasicScene.unity           ← Your test scene
```

**Required in Backend (main branch):**
```
Backend/
├── ecg_api.py                     ← MUST BE RUNNING
├── model/model.hdf5               ← Model file
└── dummy_data/sample_normal.json  ← Source data
```

---

## Success Checklist

- [ ] Flask server running (no errors)
- [ ] Unity project open in Editor
- [ ] ECG API Client GameObject in scene
- [ ] Demo Controller GameObject with script attached
- [ ] sample_normal.json assigned to Demo Controller
- [ ] 3 UI texts created and assigned
- [ ] Press Play
- [ ] Console shows "Backend is healthy"
- [ ] Console shows "=== ECG Analysis Results ==="
- [ ] UI displays diagnosis and heart rate
- [ ] No errors in Console

**If all checked → Integration successful!** 🎉

---

## Time Estimate

- First time setup: **5 minutes**
- Repeat setup (new scene): **2 minutes**

---

**Document Created:** 2025-11-16
**For:** Unity developers on HoloHuman XR team
**Next:** Full heart visualization with ECGHeartController
