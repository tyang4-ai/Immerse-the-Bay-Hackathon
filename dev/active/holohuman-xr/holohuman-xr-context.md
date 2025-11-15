# HoloHuman XR - Project Context

**Last Updated:** 2025-11-15 03:30 AM

---

## Project Overview

**Name:** HoloHuman XR: Down the Rabbit Hole
**Event:** Immerse the Bay 2025 Hackathon (Nov 14-16, 2025)
**Team Size:** 4 people
**Time Remaining:** ~34 hours (Pencils down: Sunday 9:00 AM)
**GitHub Repository:** https://github.com/tyang4-ai/Immerse-the-Bay-Hackathon

### **Key Innovation:**
Combining **ByteDance SecureMR** medical imaging platform with **AI-powered ECG analysis** and **Meshy.ai 3D generation** for immersive medical education in VR

---

## Key Files & Locations

### Project Root
```
C:\Users\22317\Documents\Coding\Hackathon Stuff\Immerse-the-Bay-Hackathon\
```

### Documentation
- `README.md` - Project overview and setup instructions ✅ PUSHED TO GITHUB
- `LICENSE` - MIT License ✅ PUSHED TO GITHUB
- `.gitignore` - Unity + Python exclusions ✅ PUSHED TO GITHUB
- `Reference/Hackathon Rules.pdf` - Official hackathon rules and requirements ✅
- `Reference/Dev Doc.pdf` - Original project concept and technical specifications ✅
- `RESOURCES.md` - All resource links and tools ✅ PUSHED TO GITHUB
- `dev/active/holohuman-xr/holohuman-xr-plan.md` - Comprehensive development plan ✅ PUSHED TO GITHUB
- `dev/active/holohuman-xr/holohuman-xr-context.md` - This file ✅ PUSHED TO GITHUB
- `dev/active/holohuman-xr/holohuman-xr-tasks.md` - Task checklist ✅ PUSHED TO GITHUB

### Code Locations (To Be Created)
- `UnityProject/` - Unity VR application
- `Backend/` - Python Flask API for ECG analysis
- `Assets/` - 3D models, textures, DICOM images

---

## Architecture Overview

### System Components (UPDATED with Advanced Features)

```
┌─────────────────┐
│   Meta Quest 2  │
│   (Unity VR)    │
└───┬─────────┬───┘
    │         │
    │         │ HTTP GET /api/medical/images
    │         ▼
    │    ┌─────────────────┐
    │    │  SecureMR API   │
    │    │  (ByteDance)    │
    │    └─────────────────┘
    │
    │ HTTP POST /api/ecg/predict
    ▼
┌─────────────────────────────────────────┐
│  Flask API (Python)                     │
│  ┌─────────────────────────────────┐   │
│  │ 3 Analysis Pipelines:            │   │
│  │ 1. TensorFlow Model              │   │
│  │    → Condition predictions       │   │
│  │ 2. R-Peak Detection              │   │
│  │    → Heart rate + timing         │   │
│  │ 3. LLM Interpretation            │   │
│  │    → Natural language analysis   │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
         │
         ├──> TensorFlow ECG Model (6 conditions)
         │
         ├──> Pan-Tompkins Algorithm (R-peak detection)
         │
         └──> Claude API (medical interpretation)

External Tools:
┌─────────────────┐
│   Meshy.ai      │ ──> 3D Heart Model ──> Unity
└─────────────────┘

┌─────────────────┐
│   CapCut        │ ──> Demo Video Editing
└─────────────────┘
```

### Technology Stack (UPDATED)

**Frontend (Unity VR)**
- Unity 2022.3 LTS
- Unity XR Interaction Toolkit
- OpenXR Plugin for Quest 2
- C# scripting
- TextMeshPro for UI
- OVRInput for haptics

**Backend (Python)**
- Python 3.8+
- Flask + Flask-CORS
- TensorFlow 2.2
- Keras
- NumPy
- SciPy (Pan-Tompkins R-peak detection)
- anthropic (Claude API for LLM interpretation)
- Requests (HTTP client for SecureMR)

**AI/ML**
- Pre-trained ECG model (antonior92/automatic-ecg-diagnosis)
- Claude LLM API (medical interpretation and natural language generation)
- **Meshy.ai** - AI 3D model generation ⭐ SPONSOR TOOL

**Medical Imaging**
- **SecureMR** (ByteDance) - Medical imaging platform ⭐ SPONSOR TOOL
- DICOM samples (backup)

**Assets**
- **3D Models:** Meshy.ai generated (primary), Z-Anatomy/TurboSquid (backup)
- **Medical Images:** SecureMR API (primary), converted PNG (backup)
- **Audio:** WAV/MP3 for heartbeat sounds

**Development Tools**
- Git/GitHub for version control
- **CapCut** (ByteDance) - Video editing ⭐ SPONSOR TOOL
- Postman for API testing
- Unity Profiler for performance
- Quest Link for fast iteration

**Hardware**
- Meta Quest 2 (primary) ⭐ SPONSOR
- Afference rings (haptics) ⭐ SPONSOR
- Development PC (Windows)

---

## Key Design Decisions

### Decision 1: Use Unity MR Example Template
- **Why:** Saves 2-3 hours of setup time
- **Trade-off:** Less control over initial configuration
- **Impact:** Significantly faster time to first prototype

### Decision 2: OpenXR Instead of Oculus SDK
- **Why:** Meta's recommended path in 2025, better documentation
- **Trade-off:** Slightly less Quest-specific optimization
- **Impact:** Easier to port to other VR platforms later

### Decision 3: Flask API Instead of Unity Sentis
- **Why:** Faster to implement, easier debugging
- **Trade-off:** Requires running separate Python server
- **Impact:** More flexible for model updates, but adds deployment complexity

### Decision 4: Pre-trained Model, No Training
- **Why:** No time to train models in 36 hours
- **Trade-off:** Locked into specific model architecture
- **Impact:** Functional AI demo without ML expertise

### Decision 5: Controller Haptics Instead of Afference Integration
- **Why:** Afference SDK not publicly available
- **Trade-off:** Less unique hardware integration
- **Impact:** Still demonstrates haptic concept, can explain Afference as future work

### Decision 6: SecureMR Instead of Manual DICOM Conversion
- **Why:** ByteDance SecureMR provides native medical imaging API
- **Trade-off:** Depends on SecureMR availability/credentials
- **Impact:** Professional medical platform, better demo story, sponsor integration
- **Backup:** Manual DICOM → PNG conversion if SecureMR unavailable

### Decision 7: Meshy.ai for 3D Generation
- **Why:** AI-generated models faster than manual modeling/optimization
- **Trade-off:** Less control over exact geometry
- **Impact:** Saves 2-4 hours of Blender work, sponsor integration

### Decision 8: Rule-Based Anatomy Mapping (Not ML)
- **Why:** ECG model doesn't output per-region data; training new model would take 10+ hours
- **Trade-off:** Less adaptable than ML, requires medical knowledge to create
- **Impact:** Faster implementation, medically accurate, allows real-time color updates

### Decision 9: Pan-Tompkins for R-Peak Detection
- **Why:** Industry-standard algorithm, no training required, scipy implementation available
- **Trade-off:** Fixed algorithm (no customization)
- **Impact:** Reliable BPM detection, enables synchronized heartbeat animations

### Decision 10: Claude LLM for Medical Interpretation
- **Why:** Superior medical reasoning vs GPT for clinical explanations
- **Trade-off:** Requires API key and internet connection
- **Impact:** Natural language explanations for patients, clinical notes for doctors

---

## Integration Points

### Unity ↔ Flask Communication (UPDATED with Advanced Features)
- **Protocol:** HTTP REST API
- **Endpoint:** `http://localhost:5000/api/ecg/predict`
- **Request Format:**
  ```json
  {
    "ecg_signal": [[float, float, ...], ...] // 4096 samples × 12 leads
  }
  ```
- **Response Format (Extended):**
  ```json
  {
    "predictions": {
      "1st_degree_AV_block": 0.05,
      "RBBB": 0.12,
      "LBBB": 0.03,
      "sinus_bradycardia": 0.78,
      "atrial_fibrillation": 0.10,
      "sinus_tachycardia": 0.15
    },
    "heart_rate": {
      "bpm": 52.3,
      "rr_intervals_ms": [1148.0, 1152.5, ...],
      "beat_timestamps": [0.5, 1.65, 2.8, ...],
      "r_peak_count": 9
    },
    "region_health": {
      "sa_node": {
        "severity": 0.5,
        "color": [1.0, 0.65, 0.0],
        "activation_delay_ms": 0,
        "affected_by": ["sinus_bradycardia"]
      },
      // ... 9 more anatomical regions
    },
    "activation_sequence": [
      ["sa_node", 0],
      ["ra", 25],
      ["la", 30],
      // ... ordered by timing
    ],
    "llm_interpretation": {
      "plain_english_summary": "...",
      "severity_assessment": {...},
      "patient_explanation": "...",
      "clinical_notes": "...",
      "visualization_suggestions": {...}
    },
    "top_condition": "sinus_bradycardia",
    "confidence": 0.78,
    "processing_time_ms": 187.3,
    "model_version": "1.0.0",
    "timestamp": "2025-11-15T03:30:00Z"
  }
  ```

### 3D Model → Unity Import
- **Source Formats:** FBX, OBJ
- **Target:** Unity Prefabs
- **Optimization:** <50k triangles for skeleton, <10k for heart
- **Materials:** Standard shader with emission for glow effects

### DICOM → PNG → Unity Texture
- **Conversion Tool:** Dicom2PNG.com or MicroDicom
- **Resolution:** 1024×1024 or 2048×2048
- **Format:** PNG with transparency
- **Import:** Unity Texture2D, applied to UI panels

---

## Dependencies

### External Assets Required
1. **Heart Model** - Low-poly (<10k tri) from TurboSquid/Free3D
2. **Skeleton Model** - From Z-Anatomy on Sketchfab, decimated to <50k tri
3. **DICOM Samples** - 5-10 images from Medimodel or RuboMedical
4. **ECG Model Weights** - From Zenodo (antonior92's pre-trained model)
5. **ECG Dataset** - MIT-BIH for testing (optional)

### Unity Packages
- XR Plugin Management (com.unity.xr.management)
- OpenXR Plugin (com.unity.xr.openxr)
- XR Interaction Toolkit (com.unity.xr.interaction.toolkit)
- TextMeshPro (com.unity.textmeshpro)
- Input System (com.unity.inputsystem)

### Python Packages
```txt
tensorflow==2.2
keras
numpy
scipy
anthropic
flask
flask-cors
requests
```

---

## Critical Paths & Blockers

### Must Complete for MVP
1. ✅ Unity project set up and deploying to Quest 2
2. ✅ Heart model imported and interactive in VR
3. ✅ Flask API running and accepting requests
4. ✅ Unity-Flask communication working
5. ✅ Basic ECG visualization
6. ✅ Layer toggle system functional

### Nice to Have (Can Be Cut)
- Full skeleton model
- Portal effect for scan space
- Advanced haptic patterns
- Multiple ECG analysis modes
- Hand tracking support

### Known Blockers
1. **TensorFlow Version Compatibility** - May need different Python version
   - *Mitigation:* Use virtual environment, test early
2. **Unity Build Time** - First APK build can take 15+ minutes
   - *Mitigation:* Use Quest Link for development
3. **3D Model Polygon Count** - Models may be too heavy
   - *Mitigation:* Decimate in Blender before importing
4. **CORS Issues** - Flask may block Unity requests
   - *Mitigation:* Install and configure Flask-CORS

---

## Environment & Configuration

### Development Machine Requirements
- **OS:** Windows 10+ or macOS 12+
- **RAM:** 16 GB minimum (Unity + VR development)
- **Storage:** 50 GB free (Unity, assets, builds)
- **GPU:** Discrete GPU recommended for Unity editor VR testing
- **USB:** USB-C port for Quest Link

### Quest 2 Configuration
- **Developer Mode:** Enabled via Meta app on phone
- **Connection:** USB-C cable or WiFi (Quest Link)
- **Storage:** 50+ GB free for APK testing
- **Firmware:** Latest version (auto-updates)

### Network Configuration
- **Flask Server:** Runs on `localhost:5000`
- **Unity Client:** Connects to `http://localhost:5000` when on same machine
- **CORS:** Enabled for Unity domain
- **Firewall:** May need to allow Flask through Windows Firewall

---

## Testing Strategy

### Unit Testing
- **Flask API:** Test endpoints with Postman/curl before Unity integration
- **Unity Scripts:** Test individual components in isolation
- **3D Models:** Import and test performance individually

### Integration Testing
- **Unity → Flask:** Test HTTP communication with simple requests
- **VR Interactions:** Test each interaction type (grab, rotate, button press)
- **Performance:** Profile with Unity Profiler, monitor FPS

### User Testing
- **Full Demo Flow:** Walk through complete experience start to finish
- **Edge Cases:** Test error handling (server down, invalid input, etc.)
- **Quest Hardware:** Test on actual Quest 2, not just Quest Link

### Performance Testing
- **FPS Target:** 72 FPS minimum on Quest 2
- **Polygon Budget:** <1M triangles total in scene
- **Memory:** Monitor with Oculus Performance HUD
- **Battery:** Ensure reasonable drain (<20%/hour)

---

## Troubleshooting Guide

### Common Issues

**Issue:** Unity build fails with "Unable to find Android SDK"
- **Fix:** Install Android Build Support through Unity Hub

**Issue:** Quest Link not connecting
- **Fix:** Enable Developer Mode on Quest 2, check USB cable, restart Meta app

**Issue:** Flask returns CORS error
- **Fix:** Install Flask-CORS, add `CORS(app)` to Flask code

**Issue:** 3D model appears black in Unity
- **Fix:** Assign material with Standard shader, check lighting

**Issue:** FPS drops below 60
- **Fix:** Reduce polygon count, disable shadows, lower texture resolution

**Issue:** HTTP request from Unity times out
- **Fix:** Ensure Flask server is running, check localhost URL, increase timeout

**Issue:** ECG model fails to load
- **Fix:** Verify TensorFlow version compatibility, check model file path

---

## Important Constraints

### Time Constraints
- **Hard Deadline:** Sunday 9:00 AM (no exceptions)
- **System Pull:** 9:01 AM (automated, cannot be delayed)
- **Buffer Time:** Reserve last 6 hours for submission

### Technical Constraints
- **Quest 2 Hardware:** Limited GPU/CPU compared to desktop
- **No Internet During Demo:** Assume no network access during judging
- **APK Size Limit:** 1 GB maximum for Quest apps
- **ML Model Size:** Model must fit in Unity build or run on localhost

### Hackathon Rules
- **Team Size:** 2-4 people (we have 4 ✓)
- **XR Requirement:** Must use XR in non-trivial way ✓
- **Spending Limit:** ≤$20 total (we're using free tools ✓)
- **Code License:** Must be open source MIT ✓
- **DevPost:** Required with 30-second video ✓

---

## Observations & Gotchas

### Things That Went Well
- ✅ Research phase completed thoroughly before coding
- ✅ Clear documentation and quick-start guides created
- ✅ Team roles assigned (2 Unity, 2 Backend)
- ✅ Hardware acquired and ready
- ✅ GitHub repository created and documentation pushed
- ✅ MIT License added
- ✅ Professional README with setup instructions
- ✅ Custom .claude agents and commands configured

### Things to Watch Out For
1. **Scope Creep:** Theme "Down the Rabbit Hole" could inspire endless features
2. **Perfectionism:** Polish can consume unlimited time
3. **ML Complexity:** ECG model integration may take longer than expected
4. **First-time VR:** Learning curve for Unity XR Toolkit
5. **Build Times:** IL2CPP builds are slow (10-15 min per build)

### Best Practices Learned
- Use Quest Link for development, build APK only 2-3 times
- Test Flask API independently before Unity integration
- Download all assets early (don't rely on last-minute downloads)
- Have backup plans for every high-risk component
- Time-box tasks strictly to prevent overruns

---

## Session Progress

### Completed (Saturday 1:37 AM - 2:00 AM)
- ✅ Researched Unity XR setup, 3D models, ECG AI, medical imaging
- ✅ Created comprehensive development plan (36-hour timeline)
- ✅ Created project context documentation
- ✅ Created detailed task checklist (165+ tasks)
- ✅ Created resource links document
- ✅ Set up GitHub repository with MIT License
- ✅ Pushed all documentation to GitHub
- ✅ Configured .gitignore for Unity + Python
- ✅ Created professional README

### Completed (Saturday 2:00 AM - 3:30 AM)
- ✅ Researched ECG model testing and anatomy mapping
- ✅ Designed 3 advanced features (R-peak detection, region coloring, LLM interpretation)
- ✅ Created 4 dummy JSON files for Unity development
- ✅ Created comprehensive dummy data README (570+ lines)
- ✅ Split backend tasks between 2 developers (TASK_SPLIT.md)
- ✅ Updated architecture diagrams with 3 analysis pipelines
- ✅ Updated technology stack (scipy, anthropic)
- ✅ Added new design decisions (anatomy mapping, Pan-Tompkins, Claude LLM)
- ✅ Updated API contract with extended response schema
- ✅ Created Backend README with setup instructions
- ✅ Created comprehensive API reference documentation

### Current Session Notes
- **Time Spent:** ~90 minutes on research, planning, and documentation
- **Advanced Features:** R-peak detection, region health mapping, LLM interpretation
- **Files Created:** 7 new files (4 JSON samples, 3 documentation files)
- **Documentation Updated:** 2 files (context.md with new architecture)
- **Backend Ready:** Complete API contract, task split, setup guide
- **Next Phase:** Push all changes to GitHub, then begin implementation

## Next Immediate Steps

### Right Now (Priority 1)
1. **Unity Team:** Begin Unity 2022.3 LTS installation with Android Build Support (~30-45 min)
2. **Backend Team:** Create Python virtual environment, clone ECG repo (~15 min)
3. **Asset Team:** Start downloading heart and skeleton models (~30 min)

### Hour 1-2 (Priority 2)
4. **Unity Team:** Clone MR Example template from GitHub
5. **Backend Team:** Download pre-trained ECG model weights from Zenodo
6. **Asset Team:** Download DICOM samples and convert to PNG

### Hour 2-4 (Priority 3)
7. **Unity Team:** First test build to Quest 2
8. **Backend Team:** Set up Flask API skeleton
9. **Asset Team:** Optimize models in Blender if needed
10. **All:** Review comprehensive plan and synchronize progress

---

## Team Contact & Roles

### Unity Team Lead (Person 1)
- **Responsibilities:** Unity setup, VR interactions, layer system, scene polish
- **Skills:** Unity experience, C# programming
- **Current Task:** Install Unity 2022.3 LTS with Android Build Support

### Unity Team Member 2 (Person 2)
- **Responsibilities:** UI/UX, medical imaging viewer, ECG visualization
- **Skills:** UI design, 3D art
- **Current Task:** Download and optimize 3D models

### Backend Team Lead (You)
- **Responsibilities:** Flask API, ML model integration, API testing, documentation, GitHub management
- **Skills:** Python, backend development, ML familiarity
- **Current Task:** ✅ GitHub setup complete - Next: Set up Python environment and ECG model
- **Completed This Session:**
  - Created comprehensive development documentation
  - Set up GitHub repository with MIT License
  - Pushed all documentation to remote repository
  - Configured git and .gitignore

### Backend Team Member 2 (Person 4)
- **Responsibilities:** Asset preparation, Unity-Flask integration, documentation
- **Skills:** Not familiar with bio stuff (noted)
- **Current Task:** Download DICOM samples and convert to PNG

---

**This context document should be updated throughout the hackathon as decisions are made and implementation progresses.**