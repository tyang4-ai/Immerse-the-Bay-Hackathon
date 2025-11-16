# Unity Documentation Summary
**HoloHuman XR - Complete Unity Integration Package**

This folder contains all Unity scripts and documentation for integrating the Flask backend with VR heart visualization.

---

## 📁 Files Created

### 1. **UNITY_INTEGRATION_GUIDE.md** (MAIN GUIDE)
**Purpose:** Step-by-step instructions for complete Unity integration

**Contents:**
- ✅ Prerequisites (Unity packages, backend requirements)
- ✅ Scene hierarchy setup (10 cardiac regions)
- ✅ Script configuration (Inspector settings for all 6 scripts)
- ✅ API configuration (network setup for PC and Quest 2)
- ✅ Testing workflow (3 test scenarios + VR deployment)
- ✅ Troubleshooting (7 common issues + fixes)

**Use this when:** Setting up Unity scene from scratch

---

### 2. **MESHY_AI_PROMPTS.md** (3D MODELS)
**Purpose:** Generate separate heart components using Meshy.ai

**Contents:**
- ✅ 10 detailed AI prompts for each cardiac component
  - SA Node, RA, LA, AV Node, Bundle of His, RBBB, LBBB, Purkinje, RV, LV
- ✅ Technical specifications (size, position, color for each part)
- ✅ Meshy.ai workflow (account setup, generation settings)
- ✅ Unity import workflow (FBX import, positioning, script attachment)
- ✅ Troubleshooting Meshy.ai (polygon count, scale, materials)
- ✅ Alternative free model sources (Sketchfab, TurboSquid)

**Use this when:** Generating 3D heart model parts with AI

**Answer to your question:**
> "i want to generate each part separately, but still want them to fit together, is that possible?"

**YES! Strategy:**
1. Generate **full_heart_reference.fbx** first (reference model for scale)
2. Generate 10 individual components with **size specifications** in prompts
3. Import to Unity and **position using anatomical coordinates** from guide
4. All prompts include **same art style** and **topology** settings for consistency
5. Use reference model for **manual alignment** if needed

**Budget-friendly option:** Generate 5 critical parts (21 credits), use Unity primitives for rest

---

### 3. **SCRIPT_ANNOTATIONS.md** (CODE EXPLANATIONS)
**Purpose:** Line-by-line explanations of what each script does

**Contents:**
- ✅ **ECGHeartController** - Main orchestrator explanation
  - How it loads ECG JSON
  - How it calls backend API
  - How it updates UI and triggers animations

- ✅ **HeartRegionMapping** - Region registry explanation
  - How the lookup dictionary works
  - How regions are validated
  - How batch updates work

- ✅ **ElectricalWaveAnimator** - Wave animation explanation
  - How activation sequence is parsed
  - How timing delays are calculated
  - How connection lines are drawn

- ✅ **TimelineController** - Beat scrubbing explanation
  - How beat markers are created
  - How debouncing works
  - How nearest beat is found

- ✅ **StorytellingJourneyController** - Narrative mode explanation
  - How narrative text is fetched
  - How waypoints are created
  - How atmosphere changes

- ✅ **WaypointInteraction** - VR interaction explanation
  - How hover effects work
  - How click triggers drill-down
  - How billboard effect works

- ✅ **Complete Data Flow Diagram**
  - Shows entire pipeline from Unity Play button → Backend → Heart visualization

**Use this when:** Understanding how the code works or debugging

---

## 📊 Quick Start Checklist

### Phase 1: Setup (30 minutes)
- [ ] Install Unity packages (TextMeshPro, XR Toolkit, Newtonsoft Json)
- [ ] Start Flask backend: `cd Backend && ./venv/Scripts/python.exe ecg_api.py`
- [ ] Create Unity scene with XR Rig

### Phase 2: 3D Models (1-2 hours)
- [ ] Read `MESHY_AI_PROMPTS.md`
- [ ] Generate 10 heart components using Meshy.ai prompts
- [ ] Import FBX files to Unity `Assets/Models/Heart/`
- [ ] Position components using anatomical coordinates

### Phase 3: Script Integration (30 minutes)
- [ ] Read `UNITY_INTEGRATION_GUIDE.md` Section 3
- [ ] Drag scripts to GameObjects per Script Assignment Matrix
- [ ] Configure Inspector settings for each script
- [ ] Attach CardiacRegionMarker to all 10 regions

### Phase 4: Testing (30 minutes)
- [ ] Place sample ECG JSON in `Resources/ECGSamples/`
- [ ] Enter Play Mode
- [ ] Verify 3 test scenarios (analysis, timeline, journey mode)
- [ ] Check Console for errors

### Phase 5: VR Deployment (30 minutes)
- [ ] Update ECGAPIClient baseURL to PC's local IP
- [ ] Build for Android (Quest 2)
- [ ] Test in VR headset

---

## 🎯 Key Concepts

### Backend Integration
**Question:** How do Unity and Flask communicate?

**Answer:**
```
Unity (C#) ──HTTP POST──> Flask (Python)
                          ├─ Analyze ECG with TensorFlow model
                          ├─ Calculate region health data
                          └─ Return JSON response

Unity receives JSON <─────┘
├─ Parse response
├─ Update UI elements
├─ Change region colors
└─ Start animations
```

### Region Mapping System
**Question:** How do backend region names connect to Unity GameObjects?

**Answer:**
```
Backend sends: {"rbbb": {"severity": 0.89, "color": [1, 0, 0]}}
                  ↓
HeartRegionMapping.GetRegion("rbbb")
                  ↓
Finds GameObject with CardiacRegionMarker where regionName = "rbbb"
                  ↓
Calls marker.UpdateVisualization(0.89, Color.red)
                  ↓
Changes light color, intensity, and particle emission
```

### Separate Heart Components
**Question:** How do 10 separate FBX files fit together?

**Answer:**
```
1. Generate full_heart_reference.fbx (reference for scale)
2. Import to Unity at (0, 0, 0), scale to 0.3 units
3. Import each component FBX
4. Position relative to reference using anatomical coordinates:
   sa_node.localPosition = (0.05, 0.08, 0.02)
   ra.localPosition = (0.06, 0.03, 0.01)
   ...
5. All components become children of HeartModel parent
```

**If they don't fit perfectly:**
- Manual adjustment in Unity Scene view
- Use reference model as visual guide
- Gizmos show region connections in Scene view

---

## 🐛 Common Issues

### "Region not found: rbbb"
**Cause:** Region name mismatch
**Fix:** Check HeartRegionMapping Inspector → regionName must be exactly "rbbb" (lowercase, no spaces)

### "Failed to connect to backend"
**Cause:** Flask not running or wrong IP
**Fix:**
- Verify: http://localhost:5000/api/health
- Quest 2: Change baseURL to PC's IP (not localhost)

### "ECG data file not assigned"
**Cause:** Missing JSON in Inspector
**Fix:** Drag sample_normal.json to ECGHeartController → ecgDataFile field

### Heart model parts don't align
**Cause:** Different scales or import settings
**Fix:**
- Check all FBX Import Settings → Scale Factor = 1
- Use full_heart_reference for manual alignment
- Apply same localScale to all components

---

## 📚 Documentation Hierarchy

```
Unity/
├── UNITY_INTEGRATION_GUIDE.md  ← START HERE (setup instructions)
│   └─ References all other docs
│
├── MESHY_AI_PROMPTS.md  ← Read when generating 3D models
│   └─ 10 AI prompts + import workflow
│
├── SCRIPT_ANNOTATIONS.md  ← Read when understanding code
│   └─ Line-by-line explanations
│
├── BACKEND_API_RESPONSES.json  ← Reference when debugging API
│   └─ All 7 endpoint response examples
│
├── HEART_DEMO_SETUP_GUIDE.md  ← Alternative guide (more visual)
│   └─ Meshy workflow + animation details
│
└── Scripts/
    ├── Heart/
    │   ├── ECGHeartController.cs
    │   ├── HeartRegionMapping.cs
    │   ├── ElectricalWaveAnimator.cs
    │   └── CardiacRegionMarker.cs
    ├── UI/
    │   ├── TimelineController.cs
    │   └── BeatDetailPanel.cs
    └── Journey/
        ├── StorytellingJourneyController.cs
        └── WaypointInteraction.cs
```

---

## 🎓 Learning Path

### Beginner (Never used Unity before)
1. Read: UNITY_INTEGRATION_GUIDE.md (Section 1-2)
2. Follow: Scene Setup instructions
3. Copy: Inspector settings exactly as shown
4. Test: Basic ECG Analysis (Test 1)

### Intermediate (Used Unity, new to VR/API)
1. Skim: UNITY_INTEGRATION_GUIDE.md
2. Focus: Section 3 (Script Integration) + Section 4 (API Config)
3. Read: SCRIPT_ANNOTATIONS.md (understand data flow)
4. Test: All 3 test scenarios

### Advanced (Want to modify/extend code)
1. Read: SCRIPT_ANNOTATIONS.md (complete understanding)
2. Reference: BACKEND_API_RESPONSES.json (API contract)
3. Modify: Scripts as needed
4. Test: Edge cases

---

## 💡 Pro Tips

### Tip 1: Use Separate Scenes
Create 3 scenes for easier testing:
- `TestScene_BasicAnalysis.unity` - Just ECG analysis
- `TestScene_Timeline.unity` - Timeline scrubbing
- `TestScene_Journey.unity` - Storytelling mode

### Tip 2: Cache ECG Data
Don't reload JSON every Play:
```csharp
// In ECGHeartController:
private static float[,] cachedECGSignal;

void LoadECGData() {
    if (cachedECGSignal != null) {
        ecgSignal = cachedECGSignal;
        return;
    }
    // ... normal loading ...
    cachedECGSignal = ecgSignal;
}
```

### Tip 3: Debug UI in VR
Add floating debug panel showing:
- Current API call
- Response time
- FPS counter
- Network status

### Tip 4: Prefab Everything
Save as prefabs:
- Complete HeartModel with all 10 regions
- UI panels (diagnosis, timeline, etc.)
- Waypoint marker with all components

### Tip 5: Use Git LFS for Models
FBX files are large, use Git LFS:
```bash
git lfs track "*.fbx"
git lfs track "*.hdf5"
```

---

## 🎬 Next Steps

After completing integration:

1. **Record Demo Video**
   - Show ECG analysis
   - Show timeline scrubbing
   - Show storytelling journey
   - Show VR interaction

2. **Performance Optimization**
   - Profile with Unity Profiler
   - Reduce polygon count if FPS < 72
   - Use occlusion culling
   - Optimize materials

3. **Add Polish**
   - Heartbeat sound effect
   - Voiceover narration
   - UI animations
   - Loading screens

4. **Prepare for Hackathon**
   - Write project description
   - Create slide deck
   - Test on Quest 2
   - Prepare for questions

---

**Documentation Created:** 2025-11-15
**Total Pages:** ~100+ pages of documentation
**Scripts Explained:** 6 Unity C# scripts
**3D Models:** 10 Meshy.ai prompts
**Test Scenarios:** 4 complete workflows

**Ready for:** Immerse the Bay Hackathon 🏆
