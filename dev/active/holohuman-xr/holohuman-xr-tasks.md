# HoloHuman XR - Task Checklist

**Last Updated:** 2025-11-15 01:45 AM
**Time Remaining:** ~34.5 hours

---

## Phase 1: Foundation Setup (Hours 0-4)

### Unity Setup
- [ ] Install Unity Hub
- [ ] Install Unity 2022.3 LTS with Android Build Support
- [ ] Clone Unity MR Example template from GitHub
- [ ] Open project in Unity, verify no errors
- [ ] Enable Developer Mode on Quest 2 via Meta app
- [ ] Configure Unity project for Quest 2 (Android platform)
- [ ] Build and deploy test APK to Quest 2
- [ ] Configure Quest Link for fast iteration
- [ ] Test Quest Link working (Play mode in headset)

### Python/Flask Backend Setup
- [ ] Create `/Backend` directory in project root
- [ ] Create Python virtual environment (`python -m venv venv`)
- [ ] Activate virtual environment
- [ ] Clone `antonior92/automatic-ecg-diagnosis` repository
- [ ] Install dependencies (`pip install tensorflow==2.2 keras numpy flask flask-cors`)
- [ ] Download pre-trained model weights from Zenodo
- [ ] Place model weights in correct directory
- [ ] Create basic Flask app with `/health` endpoint
- [ ] Create `/predict` endpoint skeleton
- [ ] Test Flask server runs on `localhost:5000`
- [ ] Test `/health` endpoint returns success
- [ ] Load ECG model successfully

### Asset Acquisition
- [ ] Download low-poly heart model from TurboSquid
- [ ] Download skeleton model from Z-Anatomy (Sketchfab)
- [ ] Download 5-10 DICOM samples from Medimodel
- [ ] Convert DICOM files to PNG using Dicom2PNG.com
- [ ] Open 3D models in Blender
- [ ] Check polygon counts (heart <10k, skeleton <50k)
- [ ] Decimate models if needed
- [ ] Export optimized models as FBX
- [ ] Organize files: `Assets/Models/`, `Assets/Images/`

---

## Phase 2: Core Development (Hours 4-18)

### 3D Model Integration (Unity)
- [ ] Import heart FBX to Unity
- [ ] Import skeleton FBX to Unity
- [ ] Create materials for models
- [ ] Set up basic scene lighting
- [ ] Position heart model in VR space (life-sized)
- [ ] Position skeleton model in VR space
- [ ] Add XR Grab Interactable component to heart
- [ ] Add XR Grab Interactable component to skeleton
- [ ] Test grabbing with VR controllers
- [ ] Implement rotation controls
- [ ] Implement scaling controls (optional)
- [ ] Test performance (check FPS in headset)

### Peelable Layer System (Unity)
- [ ] Create `LayerController.cs` script
- [ ] Organize models into layer hierarchy (parent-child GameObjects)
- [ ] Create layer toggles: skin, muscle, skeleton, heart
- [ ] Implement `ToggleLayer(int layerIndex)` function
- [ ] Implement `PeelToLayer(int targetLayer)` function
- [ ] Create VR UI buttons for layer control
- [ ] Wire up buttons to LayerController functions
- [ ] Test layer visibility toggling
- [ ] Add smooth transparency transitions (optional)
- [ ] Test full "peel back" sequence

### Flask API Development (Backend)
- [ ] Create `ecg_api.py` file in `/Backend`
- [ ] Import TensorFlow and load ECG model
- [ ] Define ECG conditions array (6 conditions)
- [ ] Implement `/predict` endpoint
- [ ] Add input validation (check array shape: 4096×12)
- [ ] Reshape input data for model
- [ ] Run model.predict() on input
- [ ] Format predictions as JSON response
- [ ] Add error handling and try-catch blocks
- [ ] Enable CORS with Flask-CORS
- [ ] Test endpoint with Postman (use dummy data)
- [ ] Verify predictions are reasonable

### Unity-Flask Integration
- [ ] Create `ECGAnalyzer.cs` script in Unity
- [ ] Define `ECGRequest` and `PredictionResults` classes
- [ ] Implement `AnalyzeECG(float[][] ecgData)` function
- [ ] Create UnityWebRequest POST to `localhost:5000/predict`
- [ ] Serialize ECG data to JSON
- [ ] Send HTTP request to Flask
- [ ] Parse JSON response
- [ ] Log predictions to Unity console
- [ ] Add error handling for network failures
- [ ] Test end-to-end: Unity → Flask → Unity
- [ ] Verify predictions display correctly

### ECG Visualization (Unity)
- [ ] Create LineRenderer for ECG waveform
- [ ] Load sample ECG data from file (or generate synthetic)
- [ ] Plot ECG data in 3D VR space
- [ ] Add time axis and labels
- [ ] Create TextMeshPro UI panel for predictions
- [ ] Display prediction results (condition names + confidence)
- [ ] Highlight top prediction
- [ ] Create "Analyze ECG" button in VR
- [ ] Wire button to trigger ECGAnalyzer
- [ ] Test full ECG flow: display → analyze → show results

---

## Phase 3: Medical Imaging & Polish (Hours 18-28)

### DICOM Image Viewer (Unity)
- [ ] Import PNG medical images to Unity
- [ ] Create UI Image component for display
- [ ] Create image array in script
- [ ] Implement "Next Image" button
- [ ] Implement "Previous Image" button
- [ ] Add zoom control (pinch or button)
- [ ] Add pan control (drag)
- [ ] Create labels for each image (anatomical region)
- [ ] Position viewer in VR space
- [ ] Test navigation through images
- [ ] Add portal effect (optional stretch goal)

### Haptic Feedback System (Unity)
- [ ] Create `HapticController.cs` script
- [ ] Implement `HeartbeatPulse(float bpm)` function
- [ ] Use InvokeRepeating to create rhythmic pulses
- [ ] Call OVRInput.SetControllerVibration for each pulse
- [ ] Create heart rate slider UI (60-120 BPM)
- [ ] Wire slider to HeartbeatPulse function
- [ ] Test heartbeat vibration at different BPMs
- [ ] Implement `FractureFeedback()` function
- [ ] Add collision detection on bone model
- [ ] Trigger fracture vibration on touch
- [ ] Test haptic timing and intensity

### VR UI/UX Polish (Unity)
- [ ] Design main menu layout
- [ ] Create layer toggle buttons (4 buttons: skin, muscle, skeleton, heart)
- [ ] Create heart rate slider
- [ ] Create "Analyze ECG" button
- [ ] Create "View Medical Images" button
- [ ] Add TextMeshPro labels for all UI elements
- [ ] Implement VR pointer/raycast from controller
- [ ] Add button hover effects (color change, scale)
- [ ] Test all UI interactions in headset
- [ ] Ensure text readable at VR distances
- [ ] Adjust UI positioning for ergonomics

### Scene Polish & Theme (Unity)
- [ ] Create "rabbit hole" tunnel environment
- [ ] Add particle effects (floating, ethereal)
- [ ] Set up ambient lighting (dark, mysterious)
- [ ] Add point light on heart (glow effect)
- [ ] Sync heart glow with heart rate
- [ ] Add red glow to fracture region on skeleton
- [ ] Create portal ring effect for scan space
- [ ] Add heartbeat sound effect
- [ ] Add ambient background audio
- [ ] Test visual theme matches "Down the Rabbit Hole"

---

## Phase 4: Testing & Optimization (Hours 28-32)

### Performance Optimization (Unity)
- [ ] Open Unity Profiler
- [ ] Run scene in Play mode with profiling
- [ ] Check average FPS (target: 72+)
- [ ] Identify performance bottlenecks
- [ ] Reduce polygon counts if FPS low
- [ ] Optimize draw calls (check batching)
- [ ] Disable or reduce shadow quality
- [ ] Lower texture resolutions if needed
- [ ] Test on actual Quest 2 hardware (not just Link)
- [ ] Monitor battery drain
- [ ] Verify no overheating
- [ ] Ensure consistent 72 FPS with all features active

### Integration Testing
- [ ] Test complete user flow start-to-finish
- [ ] Verify all layer toggles work
- [ ] Verify ECG analysis completes successfully
- [ ] Verify medical image viewer navigates correctly
- [ ] Verify haptic feedback syncs properly
- [ ] Test Flask API under repeated requests
- [ ] Test error handling (disconnect Flask server, reconnect)
- [ ] Test edge cases (invalid ECG data, missing images)
- [ ] Build APK and deploy to Quest 2
- [ ] Test standalone APK (no Quest Link)
- [ ] Verify demo can be completed in 2-3 minutes

### Bug Fixes & Refinement
- [ ] Create list of all bugs found during testing
- [ ] Triage bugs by severity (critical, important, minor)
- [ ] Fix all critical bugs (crashes, broken features)
- [ ] Fix important bugs (if time allows)
- [ ] Refine interactions based on feedback
- [ ] Adjust UI positioning/sizing
- [ ] Tweak haptic timing
- [ ] Add visual feedback for all interactions
- [ ] Clean up code and add comments
- [ ] Remove debug logs and test code

---

## Phase 5: Presentation Preparation (Hours 32-36)

### Demo Video Recording
- [ ] Write 30-second script
  - 0-5s: Title card
  - 5-10s: Put on Quest, see body
  - 10-15s: Peel layers
  - 15-20s: ECG analysis
  - 20-25s: Haptic feedback
  - 25-30s: Team credits
- [ ] Practice demo sequence 3-5 times
- [ ] Set up screen recording on Quest 2
- [ ] Record multiple takes
- [ ] Select best take
- [ ] Transfer video to computer
- [ ] Edit to vertical format (9:16)
- [ ] Add title cards
- [ ] Add team names
- [ ] Add "Immerse the Bay 2025" branding
- [ ] Export video (1080p minimum)
- [ ] Upload to hosting (YouTube, Vimeo)

### GitHub Repository Setup
- [ ] Create public repository "HoloHuman-XR"
- [ ] Add MIT License file
- [ ] Create comprehensive README.md
  - Project description
  - Features list
  - Setup instructions (Unity)
  - Setup instructions (Flask)
  - Team members
  - Built with section
  - License
- [ ] Create .gitignore (Unity + Python)
- [ ] Commit all Unity project files
- [ ] Commit all Backend Python files
- [ ] Commit documentation
- [ ] Push to GitHub
- [ ] Verify repository is public
- [ ] Test cloning repo to verify it works

### Devpost Submission
- [ ] Create new Devpost project
- [ ] Enter project title: "HoloHuman XR: Down the Rabbit Hole"
- [ ] Enter tagline (1 sentence)
- [ ] Write detailed description (500+ words)
  - Inspiration
  - What it does
  - How we built it
  - Challenges we ran into
  - Accomplishments we're proud of
  - What we learned
  - What's next for HoloHuman XR
- [ ] Upload demo video
- [ ] Add GitHub repository link
- [ ] Add "Built With" technologies
  - Unity
  - Meta Quest 2
  - TensorFlow
  - Flask
  - Python
  - C#
  - OpenXR
- [ ] Add team members
- [ ] Select competition tracks
  - Primary: Virtuous Reality
  - Secondary: AI Horizons
- [ ] Proofread entire submission
- [ ] Submit on Devpost
- [ ] Verify submission successful

### Presentation Practice
- [ ] Assign speaking roles (who says what)
- [ ] Prepare 3-minute pitch outline
  - Problem statement (30s)
  - Solution overview (30s)
  - Live demo (90s)
  - Future vision (30s)
- [ ] Practice pitch 3+ times
- [ ] Time each practice (ensure <3 min)
- [ ] Prepare for Q&A (anticipate questions)
- [ ] Have backup plan if Quest fails (show video)
- [ ] Print any needed materials (if allowed)
- [ ] Charge Quest 2 to 100%
- [ ] Test demo one final time

---

## Backup Plans (Use If Behind Schedule)

### Simplified Core Demo (If at Hour 24 and not done)
- [ ] Keep only heart model (remove skeleton)
- [ ] Use simulated ECG (hardcoded predictions)
- [ ] Use 3 medical images (instead of 5-10)
- [ ] Remove portal effect
- [ ] Simplify haptics (heartbeat only, no fracture)
- [ ] Basic UI (text + 2 buttons)
- [ ] Focus remaining time on polish and demo

### Emergency Fallbacks
- [ ] **If ML fails:** Create `/predict-fake` endpoint with random predictions
- [ ] **If Unity build fails:** Demo via Quest Link
- [ ] **If models too heavy:** Use Unity primitive shapes (cubes, spheres)
- [ ] **If Quest breaks:** Show video-only demo
- [ ] **If Flask issues:** Hardcode predictions in Unity

---

## Final Checklist (Before Submission)

### Technical
- ✅ VR scene runs at 72 FPS
- ✅ All core features functional
- ✅ No critical bugs
- ✅ Demo completable in 2-3 minutes
- ✅ Standalone APK works

### Hackathon Requirements
- ✅ Uses XR in non-trivial way
- ✅ 30-second vertical video recorded
- ✅ GitHub repo public with MIT license
- ✅ Devpost submission complete
- ✅ Submitted before 9:00 AM deadline

### Presentation
- ✅ Demo rehearsed 3+ times
- ✅ Pitch timed at <3 minutes
- ✅ Team knows their roles
- ✅ Backup plan ready
- ✅ Quest 2 charged to 100%

---

**Track your progress by checking off items as you complete them. Update this file frequently throughout the hackathon.**