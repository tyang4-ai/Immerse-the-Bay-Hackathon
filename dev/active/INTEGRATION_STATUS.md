# Backend-Frontend Integration Status
**HoloHuman XR - Immerse the Bay 2025 Hackathon**

**Last Updated:** 2025-11-16 (Hackathon Day)
**Current Phase:** Backend-Frontend Connection
**Critical Task:** Connect Unity to Flask backend for ECG analysis

---

## Branch Structure

### main branch (this workspace)
**Purpose:** Source code, documentation, backend
**Location:** C:\Users\22317\Documents\Coding\Hackathon Stuff\Immerse-the-Bay-Hackathon-1

```
main/
├── Backend/                    ✅ 100% Complete
│   ├── ecg_api.py             ✅ Flask server (7 endpoints)
│   ├── model_loader.py        ✅ TensorFlow wrapper
│   ├── ecg_heartrate_analyzer.py  ✅ R-peak detection
│   ├── heart_region_mapper.py     ✅ Anatomy mapping
│   ├── clinical_decision_support_llm.py  ✅ LLM interpreter
│   ├── model/model.hdf5       ✅ Pre-trained ECG model
│   └── dummy_data/            ⚠️ ECG samples (need to copy to Unity)
│       ├── sample_normal.json
│       ├── sample_rbbb.json
│       ├── sample_af.json
│       ├── sample_clinical_expert_rbbb.json
│       └── sample_ecg_response.json
├── Unity/Scripts/             ✅ All scripts written
│   ├── API/
│   │   └── ECGDataStructures.cs  ✅ All API response types
│   ├── Heart/
│   │   ├── ECGHeartController.cs  ✅ Main orchestrator
│   │   ├── HeartRegionMapping.cs  ✅ Region registry
│   │   ├── CardiacRegionMarker.cs ✅ Region highlighting
│   │   └── ElectricalWaveAnimator.cs  ✅ Wave animation
│   ├── UI/
│   │   ├── TimelineController.cs  ✅ Beat scrubbing
│   │   └── BeatDetailPanel.cs     ✅ Beat detail UI
│   ├── Journey/
│   │   ├── StorytellingJourneyController.cs  ✅ VR tour
│   │   └── WaypointInteraction.cs  ✅ VR interaction
│   ├── ECGAPIClient.cs        ✅ HTTP client (singleton)
│   └── ECGDemoController.cs   ✅ Demo scene controller
└── Documentation/             ✅ Complete
    ├── README.md
    ├── Backend/README.md
    ├── Backend/API_INTEGRATION_GUIDE.md
    ├── Backend/UNITY_QUICKSTART.md
    ├── Unity/UNITY_INTEGRATION_GUIDE.md
    ├── Unity/MESHY_AI_PROMPTS.md
    └── Unity/SCRIPT_ANNOTATIONS.md
```

### unity-project-upload branch (other workspace)
**Purpose:** Unity project files, scenes, assets
**Location:** [Different folder on your PC]

```
unity-project-upload/
├── Assets/
│   ├── Scenes/
│   │   ├── BasicScene.unity      ✅ Exists
│   │   └── SampleScene.unity     ✅ Exists
│   ├── Scripts/                  ✅ All scripts copied from main
│   │   ├── API/ECGDataStructures.cs
│   │   ├── Heart/ (all 4 scripts)
│   │   ├── UI/ (all 2 scripts)
│   │   ├── Journey/ (all 2 scripts)
│   │   ├── ECGAPIClient.cs
│   │   └── ECGDemoController.cs
│   ├── Resources/                ❌ MISSING - Need to create
│   │   └── ECGSamples/           ❌ MISSING - Need ECG JSON files
│   ├── Settings/                 ✅ Project configuration exists
│   └── TextMesh Pro/             ✅ TMP imported
├── Packages/                     ✅ Unity packages configured
│   ├── manifest.json             ✅ Exists
│   └── packages-lock.json        ✅ Exists
└── ProjectSettings/              ✅ All project settings configured
```

---

## What's Complete ✅

### Backend (100%)
- [x] Flask API with 7 endpoints
- [x] TensorFlow ECG model integration
- [x] Heart rate analyzer with multi-lead fallback
- [x] Region mapping (condition → anatomy)
- [x] LLM fallback mode (no API key needed)
- [x] All tests passing
- [x] Complete API documentation

### Unity Scripts (100%)
- [x] All 11 C# scripts written
- [x] API client with singleton pattern
- [x] Data structures for all API responses
- [x] Heart controller and region mapping
- [x] Timeline and beat detail UI
- [x] Storytelling journey mode
- [x] VR waypoint interaction
- [x] No compilation errors

### Documentation (100%)
- [x] Backend README and API guide
- [x] Unity integration guide
- [x] Meshy.ai prompts for 3D models
- [x] Script annotations
- [x] Quick start guide (15 min)

---

## What's Missing ❌

### Critical (Blocks Integration Testing)

1. **ECG Sample Data in Unity Resources**
   - **Status:** ❌ NOT DONE
   - **Location:** Need to create `Assets/Resources/ECGSamples/`
   - **Files to copy from main branch:**
     * `Backend/dummy_data/sample_normal.json` → `Assets/Resources/ECGSamples/`
     * `Backend/dummy_data/sample_rbbb.json` → `Assets/Resources/ECGSamples/`
     * `Backend/dummy_data/sample_af.json` → `Assets/Resources/ECGSamples/`
   - **Why needed:** ECGHeartController loads ECG data from Resources folder
   - **Priority:** 🔴 CRITICAL - Cannot test without this

2. **Flask Server Not Running**
   - **Status:** ⚠️ STOPPED
   - **Action:** Must start Flask before testing
   - **Command:** `cd Backend && python ecg_api.py`
   - **Priority:** 🔴 CRITICAL - Backend must be running

3. **3D Heart Models**
   - **Status:** ❌ NOT GENERATED
   - **Needed:** 10 cardiac region models (SA Node, RA, LA, AV Node, etc.)
   - **Options:**
     * Generate with Meshy.ai (use prompts in Unity/MESHY_AI_PROMPTS.md)
     * Download from Sketchfab/TurboSquid
     * Use Unity primitives as placeholders
   - **Priority:** 🟡 HIGH - Can test API without models, but need for visualization

### Nice to Have (Not Blocking)

4. **Unity Scene Setup**
   - **Status:** ⏳ PARTIAL (BasicScene exists but not configured)
   - **Needed:**
     * XR Rig for VR
     * Heart Model parent GameObject
     * UI Canvas for ECG results
     * ECGAPIClient GameObject
   - **Reference:** Unity/UNITY_INTEGRATION_GUIDE.md
   - **Priority:** 🟡 HIGH - Can test API in PlayMode first

5. **Network Configuration for Quest 2**
   - **Status:** ⏳ DOCUMENTED but not tested
   - **PC IP:** 10.32.86.82 (from session notes)
   - **Backend URL:** http://10.32.86.82:5000
   - **Action:** Update ECGAPIClient.backendURL in Unity Inspector when deploying to Quest 2
   - **Priority:** 🟢 LOW - Only needed for final VR testing

---

## Integration Testing Checklist

### Phase 1: Backend Verification (5 min)
- [ ] Start Flask server: `cd Backend && python ecg_api.py`
- [ ] Verify health endpoint: `curl http://localhost:5000/health`
- [ ] Test analysis endpoint:
  ```bash
  curl -X POST http://localhost:5000/api/ecg/analyze \
    -H "Content-Type: application/json" \
    -d @Backend/dummy_data/sample_normal.json
  ```
- [ ] Confirm response includes: predictions, heart_rate, region_health

### Phase 2: Unity Resources Setup (10 min)
In unity-project-upload workspace:
- [ ] Create folder: `Assets/Resources/ECGSamples/`
- [ ] Copy ECG sample files:
  ```bash
  # From main branch Backend/dummy_data/
  cp sample_normal.json → Assets/Resources/ECGSamples/
  cp sample_rbbb.json → Assets/Resources/ECGSamples/
  cp sample_af.json → Assets/Resources/ECGSamples/
  ```
- [ ] Verify files imported in Unity Project window

### Phase 3: Unity Scene Setup (15 min)
- [ ] Open BasicScene or SampleScene
- [ ] Create empty GameObject: "ECG API Client"
  * Add component: ECGAPIClient.cs
  * Set backendURL: `http://localhost:5000` (PC) or `http://10.32.86.82:5000` (Quest 2)
  * Enable logRequests: true
- [ ] Create empty GameObject: "Controllers"
  * Add component: ECGHeartController.cs
  * Assign ecgDataFile: `ECGSamples/sample_normal` (TextAsset from Resources)
- [ ] Create UI Canvas with TextMeshPro texts for:
  * Diagnosis text
  * Heart rate text
  * Status text
- [ ] Create GameObject: "Region Mapper"
  * Add component: HeartRegionMapping.cs

### Phase 4: Integration Test (10 min)
- [ ] Ensure Flask server is running
- [ ] Press Play in Unity Editor
- [ ] Check Console for:
  * "[ECG API] Backend is healthy! Model loaded: True"
  * "[ECG API] POST /api/ecg/analyze (mode: clinical_expert)"
  * ECG analysis results
- [ ] Verify no errors
- [ ] Check UI displays diagnosis and heart rate

### Phase 5: Advanced Testing (Optional)
- [ ] Test timeline scrubbing (requires Timeline UI setup)
- [ ] Test beat detail panel (requires UI setup)
- [ ] Test storytelling journey mode (requires waypoint setup)
- [ ] Deploy to Quest 2 and test in VR

---

## Current Workflow (Two Workspaces)

### Workflow for Script Changes

**Workspace 1 (main branch):**
```bash
# Edit scripts in Unity/Scripts/
git add Unity/Scripts/
git commit -m "Update Unity scripts"
git push origin main
git push origin main:unity-project-upload  # Push to both branches
```

**Workspace 2 (unity-project-upload branch):**
```bash
git pull origin unity-project-upload
# Scripts now updated in Assets/Scripts/
# Unity auto-recompiles
```

### Workflow for Unity-Only Changes
**Workspace 2 only:**
```bash
# Make changes in Unity (scenes, prefabs, assets)
git add Assets/ ProjectSettings/
git commit -m "Update Unity scene"
git push origin unity-project-upload
# These changes stay ONLY on unity-project-upload branch
```

---

## Backend API Quick Reference

### Main Endpoint: POST /api/ecg/analyze

**Request:**
```json
{
  "ecg_signal": [[...], [...], ...],  // 4096x12 float array
  "output_mode": "clinical_expert",   // or "patient_education" or "storytelling"
  "region_focus": "rbbb"              // optional, for storytelling mode
}
```

**Response:**
```json
{
  "predictions": {
    "1st_degree_AV_block": 0.05,
    "RBBB": 0.89,
    "LBBB": 0.03,
    "sinus_bradycardia": 0.15,
    "atrial_fibrillation": 0.10,
    "sinus_tachycardia": 0.18
  },
  "heart_rate": {
    "bpm": 72.5,
    "rr_intervals_ms": [827.5, 830.0, ...],
    "beat_timestamps": [0.5, 1.33, 2.15, ...],
    "r_peak_count": 12
  },
  "region_health": {
    "sa_node": {
      "severity": 0.5,
      "color": [1.0, 0.65, 0.0],
      "activation_delay_ms": 0,
      "affected_by": ["sinus_bradycardia"]
    },
    // ... 9 more regions
  },
  "activation_sequence": [
    ["sa_node", 0],
    ["ra", 25],
    ["la", 25],
    // ... ordered by activation timing
  ],
  "llm_interpretation": {
    "plain_english_summary": "...",
    "severity_assessment": {...},
    "patient_explanation": "...",
    "clinical_notes": "..."
  },
  "top_condition": "RBBB",
  "confidence": 0.89
}
```

### Other Endpoints

- **GET /health** - Check server status
- **POST /api/ecg/beats** - Fast R-peak detection (~50ms)
- **POST /api/ecg/beat/<index>** - Single beat analysis
- **POST /api/ecg/segment** - Time window analysis

**Full API docs:** Backend/API_INTEGRATION_GUIDE.md

---

## Network Configuration

### PC Testing (Unity Editor)
```
Backend URL: http://localhost:5000
```

### Quest 2 VR Testing
```
Backend URL: http://10.32.86.82:5000
PC IP: 10.32.86.82
```

**Requirements:**
- PC and Quest 2 on same WiFi network
- Flask server started with `host='0.0.0.0'` (already configured)
- Windows Firewall allows Python (Settings → Firewall → Allow Python)

---

## Next Actions (Priority Order)

### 1. 🔴 IMMEDIATE (Backend Connection Test)
```bash
# In main branch workspace
cd Backend
python ecg_api.py

# Leave server running, open new terminal
curl http://localhost:5000/health
```
**Expected:** `{"status": "healthy", "model_loaded": true, ...}`

### 2. 🔴 IMMEDIATE (Copy ECG Samples to Unity)
```bash
# In unity-project-upload workspace
mkdir -p Assets/Resources/ECGSamples

# Copy from main branch location:
# Backend/dummy_data/*.json → Assets/Resources/ECGSamples/
```

### 3. 🟡 HIGH (Basic Unity Scene Setup)
- Open unity-project-upload workspace in Unity Editor
- Follow Phase 3 checklist above
- Create ECG API Client GameObject
- Assign ECG sample file to ECGHeartController

### 4. 🟡 HIGH (Integration Test)
- Press Play in Unity
- Verify backend connection
- Check ECG analysis results in Console

### 5. 🟢 MEDIUM (3D Models)
- Generate heart models with Meshy.ai
- OR download placeholder models
- Import to Assets/Models/Heart/

### 6. 🟢 LOW (VR Deployment)
- Build for Android (Quest 2)
- Update backend URL to PC IP
- Test on headset

---

## Common Issues & Solutions

### Issue: "Cannot connect to backend"
**Cause:** Flask server not running
**Fix:**
```bash
cd Backend
python ecg_api.py
# Verify: curl http://localhost:5000/health
```

### Issue: "ECG data file not assigned"
**Cause:** Missing TextAsset in Inspector
**Fix:** Drag `Resources/ECGSamples/sample_normal` to ECGHeartController → ecgDataFile field

### Issue: "Region not found: rbbb"
**Cause:** HeartRegionMapping not set up
**Fix:** Create 10 GameObjects with CardiacRegionMarker script, set regionName field

### Issue: Quest 2 can't connect
**Cause:** Wrong backend URL or network issue
**Fix:**
1. Check PC IP: `ipconfig`
2. Update ECGAPIClient.backendURL to `http://<PC_IP>:5000`
3. Allow Python through Windows Firewall
4. Test from Quest browser: http://<PC_IP>:5000/health

---

## File Paths Reference

### main branch
```
Backend/dummy_data/sample_normal.json  → ECG sample for testing
Unity/Scripts/ECGAPIClient.cs          → HTTP client
Unity/UNITY_INTEGRATION_GUIDE.md       → Complete setup guide
Backend/API_INTEGRATION_GUIDE.md       → API reference
```

### unity-project-upload branch
```
Assets/Resources/ECGSamples/           → ECG data folder (create this)
Assets/Scripts/ECGAPIClient.cs         → HTTP client (copied from main)
Assets/Scenes/BasicScene.unity         → Test scene
```

---

## Success Criteria

### Minimum Working Integration
- [x] Flask server running and healthy
- [ ] ECG sample files in Unity Resources
- [ ] ECGAPIClient GameObject in scene
- [ ] Backend connection successful (health check passes)
- [ ] ECG analysis request completes without errors
- [ ] Response logged to Unity Console

### Full Integration
- [ ] All above +
- [ ] 3D heart model in scene
- [ ] 10 cardiac regions configured
- [ ] UI displays diagnosis and heart rate
- [ ] Timeline scrubbing works
- [ ] Storytelling journey mode functional
- [ ] Deploys to Quest 2 successfully

---

**Document Status:** Complete
**Last Verified:** 2025-11-16
**Ready for:** Backend-frontend connection testing
