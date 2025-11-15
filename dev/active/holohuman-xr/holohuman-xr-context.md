# HoloHuman XR - Project Context

**Last Updated:** 2025-11-15 01:45 AM

---

## Project Overview

**Name:** HoloHuman XR: Down the Rabbit Hole
**Event:** Immerse the Bay 2025 Hackathon (Nov 14-16, 2025)
**Team Size:** 4 people
**Time Remaining:** ~34.5 hours (Pencils down: Sunday 9:00 AM)

---

## Key Files & Locations

### Project Root
```
C:\Users\22317\Documents\Coding\Hackathon Stuff\Immerse-the-Bay-Hackathon\
```

### Documentation
- `Reference/Hackathon Rules.pdf` - Official hackathon rules and requirements
- `Reference/Dev Doc.pdf` - Original project concept and technical specifications
- `HACKATHON_QUICK_START.md` - Quick reference guide (CREATED)
- `RESOURCES.md` - All resource links and tools (CREATED)
- `dev/active/holohuman-xr/holohuman-xr-plan.md` - Comprehensive development plan (CREATED)
- `dev/active/holohuman-xr/holohuman-xr-context.md` - This file

### Code Locations (To Be Created)
- `UnityProject/` - Unity VR application
- `Backend/` - Python Flask API for ECG analysis
- `Assets/` - 3D models, textures, DICOM images

---

## Architecture Overview

### System Components

```
┌─────────────────┐
│   Meta Quest 2  │
│   (Unity VR)    │
└────────┬────────┘
         │ HTTP POST
         │ /predict
         ▼
┌─────────────────┐
│  Flask API      │
│  (Python)       │
└────────┬────────┘
         │ model.predict()
         ▼
┌─────────────────┐
│  Pre-trained    │
│  ECG Model      │
│  (TensorFlow)   │
└─────────────────┘
```

### Technology Stack

**Frontend (Unity VR)**
- Unity 2022.3 LTS
- Unity XR Interaction Toolkit
- OpenXR Plugin for Quest 2
- C# scripting
- TextMeshPro for UI
- OVRInput for haptics

**Backend (Python)**
- Python 3.8+
- Flask (web server)
- Flask-CORS (cross-origin requests)
- TensorFlow 2.2 (ML model)
- Keras (model wrapper)
- NumPy (data processing)

**Assets**
- 3D Models: FBX/OBJ format from Sketchfab, TurboSquid
- Medical Images: PNG converted from DICOM
- Audio: WAV/MP3 for heartbeat sounds

**Development Tools**
- Git/GitHub for version control
- Blender for 3D model optimization
- Postman for API testing
- Unity Profiler for performance
- Quest Link for fast iteration

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

### Decision 6: DICOM → PNG Instead of Real-time DICOM
- **Why:** Simpler implementation, no complex library integration
- **Trade-off:** Can't load arbitrary DICOM files
- **Impact:** Sufficient for demo, conversion process documented

---

## Integration Points

### Unity ↔ Flask Communication
- **Protocol:** HTTP REST API
- **Endpoint:** `http://localhost:5000/predict`
- **Request Format:**
  ```json
  {
    "ecg_signal": [[float, float, ...], ...] // 4096 samples × 12 leads
  }
  ```
- **Response Format:**
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
    "top_condition": "sinus_bradycardia",
    "confidence": 0.78
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
flask
flask-cors
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
- Research phase completed thoroughly before coding
- Clear documentation and quick-start guides created
- Team roles assigned (2 Unity, 2 Backend)
- Hardware acquired and ready

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

## Next Immediate Steps

1. **Unity Team:** Begin Unity + Android Build Support installation (30 min)
2. **Backend Team:** Create Python virtual environment, clone ECG repo (15 min)
3. **Asset Team:** Start downloading heart and skeleton models (30 min)
4. **All:** Review comprehensive plan and ask questions

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
- **Responsibilities:** Flask API, ML model integration, API testing
- **Skills:** Python, backend development, ML familiarity
- **Current Task:** Set up Python environment and ECG model

### Backend Team Member 2 (Person 4)
- **Responsibilities:** Asset preparation, Unity-Flask integration, documentation
- **Skills:** Not familiar with bio stuff (noted)
- **Current Task:** Download DICOM samples and convert to PNG

---

**This context document should be updated throughout the hackathon as decisions are made and implementation progresses.**