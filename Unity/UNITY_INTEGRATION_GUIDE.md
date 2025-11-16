# Complete Unity Integration Guide
**HoloHuman XR - 3D Heart Visualization with ECG Analysis**

> **Purpose:** This guide provides step-by-step instructions to integrate the Flask backend with Unity VR frontend.
> **Target Platform:** Meta Quest 2 VR headset
> **Unity Version:** 2021.3 LTS or higher recommended
> **Estimated Setup Time:** 2-3 hours

---

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Scene Setup](#scene-setup)
3. [Script Integration](#script-integration)
4. [API Configuration](#api-configuration)
5. [Testing Workflow](#testing-workflow)
6. [Troubleshooting](#troubleshooting)

---

## 1. Prerequisites

### Required Unity Packages
Install these via **Window → Package Manager**:

```
✓ TextMeshPro (com.unity.textmeshpro)
✓ XR Interaction Toolkit (com.unity.xr.interaction.toolkit) v2.0+
✓ Newtonsoft Json (com.unity.nuget.newtonsoft-json)
✓ XR Plugin Management (com.unity.xr.management)
✓ Oculus XR Plugin (com.unity.xr.oculus)
```

### Backend Requirements
- Flask server running on local network
- Backend address: **http://localhost:5000** (PC) or **http://YOUR_IP:5000** (Quest 2)
- All 7 endpoints operational (see `BACKEND_API_RESPONSES.json`)

### Assets Needed
- **3D Heart Model** (from Meshy.ai - see prompts below)
- **ECG Sample Data** (JSON files in `Resources/ECGSamples/`)
- **UI Prefabs** (beat markers, waypoints, panels)

---

## 2. Scene Setup

### Step 1: Create Scene Hierarchy

```
🎬 HoloHeartScene
├── 🎥 XR Rig (Camera + Controllers from XR Interaction Toolkit)
├── 💓 HeartModel
│   ├── 🔴 SA_Node_Marker (with CardiacRegionMarker.cs)
│   ├── 🔴 RA_Marker
│   ├── 🔴 LA_Marker
│   ├── 🔴 AV_Node_Marker
│   ├── 🔴 BundleOfHis_Marker
│   ├── 🔴 RBBB_Marker
│   ├── 🔴 LBBB_Marker
│   ├── 🔴 Purkinje_Marker
│   ├── 🔴 RV_Marker
│   └── 🔴 LV_Marker
├── 🎛️ UI
│   ├── 📊 DiagnosisPanel (Canvas)
│   ├── 📈 TimelinePanel (Canvas with Slider)
│   ├── 📝 BeatDetailPanel (Canvas)
│   ├── 📖 NarrativePanel (Canvas)
│   └── ⚙️ StatusDisplay (Canvas)
├── 🎮 Controllers
│   ├── ECGHeartController (MAIN CONTROLLER)
│   ├── HeartRegionMapping
│   ├── ElectricalWaveAnimator
│   ├── TimelineController
│   └── StorytellingJourneyController
└── 🌍 Environment
    ├── Directional Light
    ├── Ambient Light (for atmosphere control)
    └── Atmosphere Particles (optional)
```

### Step 2: Position Heart Model

1. Import heart model FBX from Meshy.ai
2. Place at **world origin** (0, 0, 0)
3. Scale to appropriate size (approximately 0.2 - 0.5 units for VR)
4. Position **1.5 units** in front of XR Rig camera

### Step 3: Create Region Markers

**Option A: Mesh-Based Regions** (if Meshy.ai exports separate parts):
```
1. Each heart region is a separate mesh (sa_node.fbx, rbbb.fbx, etc.)
2. Attach CardiacRegionMarker.cs to each mesh
3. Set regionName to match backend: "sa_node", "rbbb", "av_node", etc.
4. Add Light component (Point Light, Range: 0.5, Intensity: 2.0)
5. Add Particle System (optional, for electrical effects)
```

**Option B: Empty GameObject Markers** (if single solid heart mesh):
```
1. Create 10 Empty GameObjects as children of HeartModel
2. Position them at anatomical locations:
   - SA Node: Upper right atrium
   - AV Node: Between atria and ventricles
   - Bundle of His: Septum between ventricles
   - RBBB/LBBB: Left/right bundle branches
   - Purkinje: Ventricular walls
   - RA/LA: Right/left atria
   - RV/LV: Right/left ventricles
3. Attach CardiacRegionMarker.cs to each
4. Add Light + ParticleSystem components
```

**Anatomical Reference Positions** (approximate):
```csharp
SA Node:      ( 0.05,  0.08,  0.02)  // Upper right atrium
RA:           ( 0.06,  0.03,  0.01)  // Right atrium
LA:           (-0.06,  0.03,  0.01)  // Left atrium
AV Node:      ( 0.00,  0.00,  0.00)  // Between atria/ventricles
Bundle of His:( 0.00, -0.02,  0.00)  // Septum
RBBB:         ( 0.04, -0.05,  0.00)  // Right bundle branch
LBBB:         (-0.04, -0.05,  0.00)  // Left bundle branch
Purkinje:     ( 0.00, -0.08,  0.00)  // Ventricular walls
RV:           ( 0.05, -0.06,  0.02)  // Right ventricle
LV:           (-0.05, -0.06,  0.02)  // Left ventricle
```

---

## 3. Script Integration

### Script Assignment Matrix

| GameObject | Script | Purpose |
|------------|--------|---------|
| `Controllers/ECGController` | **ECGHeartController.cs** | Main orchestrator - connects API to visuals |
| `Controllers/RegionMapper` | **HeartRegionMapping.cs** | Registry of 10 cardiac regions |
| `Controllers/WaveAnimator` | **ElectricalWaveAnimator.cs** | Electrical wave animation |
| `Controllers/Timeline` | **TimelineController.cs** | Beat scrubbing UI |
| `Controllers/StoryJourney` | **StorytellingJourneyController.cs** | Narrative mode |
| Each region marker | **CardiacRegionMarker.cs** | Individual region visualization |
| UI/BeatDetailPanel | **BeatDetailPanel.cs** | Beat detail display |
| (Waypoint prefab) | **WaypointInteraction.cs** | Journey waypoint clicks |
| API Singleton | **ECGAPIClient.cs** | Backend communication |

### Detailed Script Configuration

#### 3.1 ECGHeartController (Main Controller)

**Location:** Create empty GameObject `Controllers/ECGController`

**Inspector Settings:**
```
┌─ ECG Heart Controller ───────────────────┐
│ API Client: [Drag ECGAPIClient GameObject] │
│                                             │
│ ECG Data:                                   │
│   ecgDataFile: [Drag sample_normal.json]   │
│                                             │
│ Heart Visualization:                        │
│   regionMapping: [Drag RegionMapper]        │
│   waveAnimator: [Drag WaveAnimator]         │
│                                             │
│ UI Elements:                                │
│   diagnosisText: [Drag DiagnosisText TMP]   │
│   heartRateText: [Drag HeartRateText TMP]   │
│   statusText: [Drag StatusText TMP]         │
│   interpretationText: [Drag InterpText TMP] │
│                                             │
│ Settings:                                   │
│   outputMode: "clinical_expert"             │
│   autoAnalyzeOnStart: ✓                     │
└─────────────────────────────────────────────┘
```

**What it does:**
1. **Loads ECG JSON** from Resources folder (4096x12 array)
2. **Calls /api/ecg/analyze** endpoint on start
3. **Updates UI** with diagnosis + heart rate
4. **Triggers region colors** via HeartRegionMapping
5. **Starts electrical animation** via ElectricalWaveAnimator

#### 3.2 HeartRegionMapping

**Location:** Create empty GameObject `Controllers/RegionMapper`

**Inspector Settings:**
```
┌─ Heart Region Mapping ──────────────────┐
│ Heart Regions (Array Size: 10):         │
│                                          │
│ [0] regionName: "sa_node"                │
│     regionObject: [Drag SA_Node_Marker]  │
│     regionMaterial: [Optional]           │
│     electricalEffect: [Optional PS]      │
│                                          │
│ [1] regionName: "ra"                     │
│     regionObject: [Drag RA_Marker]       │
│                                          │
│ [2] regionName: "la"                     │
│ [3] regionName: "av_node"                │
│ [4] regionName: "bundle_his"             │
│ [5] regionName: "rbbb"                   │
│ [6] regionName: "lbbb"                   │
│ [7] regionName: "purkinje"               │
│ [8] regionName: "rv"                     │
│ [9] regionName: "lv"                     │
└──────────────────────────────────────────┘
```

**Critical:** Region names MUST match backend exactly:
- ✓ "sa_node", "ra", "la", "av_node", "bundle_his", "rbbb", "lbbb", "purkinje", "rv", "lv"
- ✗ "SA_Node", "saNode", "SA Node" (WRONG)

#### 3.3 ElectricalWaveAnimator

**Location:** Create empty GameObject `Controllers/WaveAnimator`

**Inspector Settings:**
```
┌─ Electrical Wave Animator ──────────────┐
│ Animation Settings:                      │
│   animationSpeed: 1.0                    │
│   pulseDuration: 0.5                     │
│   loopAnimation: ✓                       │
│   loopDelay: 1.0                         │
│                                          │
│ Visual Effects:                          │
│   showConnectionLines: ✓                 │
│   connectionLinePrefab: [LineRenderer]   │
│   lineDisplayDuration: 0.3               │
└──────────────────────────────────────────┘
```

**What it does:**
1. Reads `activation_sequence` from API response
2. Triggers regions in order with timing: `[["sa_node", 0], ["ra", 25], ["la", 30], ...]`
3. Calls `TriggerElectricalWave()` on each CardiacRegionMarker
4. Shows connection lines between regions (optional)
5. Loops animation continuously

#### 3.4 TimelineController

**Location:** Create empty GameObject `Controllers/Timeline`

**Inspector Settings:**
```
┌─ Timeline Controller ────────────────────┐
│ API Client: [Drag ECGAPIClient]          │
│                                           │
│ Timeline UI:                              │
│   timelineSlider: [Drag UI Slider]        │
│   beatMarkersParent: [Drag Parent Trans]  │
│   beatMarkerPrefab: [Drag Marker Prefab]  │
│                                           │
│ Beat Detail Panel:                        │
│   beatDetailPanel: [Drag BeatPanel]       │
│                                           │
│ Settings:                                 │
│   scrubDebounceTime: 0.5                  │
│   samplingRate: 400                       │
└───────────────────────────────────────────┘
```

**What it does:**
1. Calls `/api/ecg/beats` to get all R-peak positions
2. Creates visual beat markers on timeline
3. Detects slider dragging (VR controller input)
4. Waits 0.5s after scrubbing stops (debounce)
5. Calls `/api/ecg/beat/{index}` for focused beat
6. Displays P-QRS-T intervals in BeatDetailPanel

#### 3.5 StorytellingJourneyController

**Location:** Create empty GameObject `Controllers/StoryJourney`

**Inspector Settings:**
```
┌─ Storytelling Journey Controller ────────┐
│ API Client: [Drag ECGAPIClient]           │
│                                            │
│ UI Components:                             │
│   narrativeText: [Drag NarrativeText TMP]  │
│   narrativePanel: [Drag NarrativePanel]    │
│   statusText: [Drag StatusText TMP]        │
│                                            │
│ Heart Visualization:                       │
│   regionMapping: [Drag RegionMapper]       │
│   waypointPrefab: [Drag WaypointPrefab]    │
│                                            │
│ Atmosphere Control:                        │
│   ambientLight: [Drag Light]               │
│   atmosphereParticles: [Drag PS]           │
│   narrativeAudio: [Drag AudioSource]       │
│                                            │
│ Journey Settings:                          │
│   autoStartJourney: false                  │
│   textRevealSpeed: 0.05                    │
│   healthyAtmosphereColor: (0.6, 0.8, 1.0)  │
│   unhealthyAtmosphereColor: (1.0, 0.4, 0.4)│
└────────────────────────────────────────────┘
```

**What it does:**
1. Calls `/api/ecg/analyze` with `output_mode="storytelling"`
2. Displays narrative with typewriter effect
3. Creates 3D waypoint markers at cardiac regions
4. Changes lighting color based on diagnosis (blue=healthy, red=unhealthy)
5. Handles waypoint clicks for regional drill-down

#### 3.6 CardiacRegionMarker (Attach to each region)

**Inspector Settings:**
```
┌─ Cardiac Region Marker ─────────────────┐
│ Region Configuration:                    │
│   regionName: "sa_node"  (EXACT MATCH)   │
│                                          │
│ Visual Components:                       │
│   glowLight: [Auto-detected Light]       │
│   electricalEffect: [Auto-detected PS]   │
│   regionRenderer: [Auto-detected]        │
│                                          │
│ Visual Settings:                         │
│   severity: 0.0 (updated by API)         │
│   currentColor: (0, 1, 0) Green          │
│   maxLightIntensity: 3.0                 │
│   maxParticleEmission: 50                │
│                                          │
│ Animation:                               │
│   isPulsing: false                       │
│   pulseSpeed: 2.0                        │
│   pulseAmplitude: 0.5                    │
└──────────────────────────────────────────┘
```

---

## 4. API Configuration

### 4.1 ECGAPIClient Setup

Create a **singleton GameObject** in scene:

```
GameObject: API/ECGAPIClient
Script: ECGAPIClient.cs
```

**Inspector Settings:**
```
┌─ ECG API Client ────────────────────────┐
│ Backend Configuration:                  │
│   baseURL: "http://localhost:5000"      │
│   (Quest 2: "http://YOUR_IP:5000")      │
│                                         │
│ Request Settings:                       │
│   timeout: 30                           │
│   retryAttempts: 3                      │
│   enableLogging: ✓                      │
└─────────────────────────────────────────┘
```

**Network Configuration for Quest 2:**

1. Find PC IP address:
   ```bash
   ipconfig  # Windows
   ifconfig  # Mac/Linux
   ```

2. Update `baseURL` in ECGAPIClient:
   ```
   http://192.168.1.XXX:5000  (replace XXX with your PC's IP)
   ```

3. Ensure Flask server allows external connections:
   ```python
   app.run(host='0.0.0.0', port=5000)  # Listens on all network interfaces
   ```

4. Configure Windows Firewall:
   - Allow inbound connections on port 5000
   - Or temporarily disable firewall for testing

### 4.2 ECG Sample Data

Place ECG JSON files in `Assets/Resources/ECGSamples/`:

```
Resources/
└── ECGSamples/
    ├── sample_normal.json      (Normal sinus rhythm, 72 BPM)
    ├── sample_bradycardia.json (Slow heart, 50 BPM)
    ├── sample_tachycardia.json (Fast heart, 110 BPM)
    ├── sample_afib.json        (Atrial fibrillation)
    └── sample_rbbb.json        (Right bundle branch block)
```

**JSON Format:**
```json
{
  "ecg_signal": [
    [0.01, 0.02, ..., 0.05],  // Sample 0 (12 leads)
    [0.02, 0.03, ..., 0.04],  // Sample 1
    ...                        // 4096 total samples
    [0.01, 0.02, ..., 0.03]   // Sample 4095
  ]
}
```

---

## 5. Testing Workflow

### Test 1: Basic ECG Analysis

1. **Start Flask Backend:**
   ```bash
   cd Backend
   ./venv/Scripts/python.exe ecg_api.py
   ```

2. **Enter Play Mode in Unity**

3. **Expected Behavior:**
   - Status text shows "Loading ECG data..."
   - Then "Analyzing ECG..."
   - Diagnosis panel updates with condition + confidence
   - Heart rate panel shows BPM
   - 10 cardiac regions change color based on severity
   - Electrical wave animation starts

4. **Check Console for Logs:**
   ```
   [ECGHeartController] ECG loaded: 4096 samples × 12 leads
   [ECGHeartController] Analysis complete: Sinus Rhythm (92%)
   [HeartRegionMapping] Updated 10 cardiac regions
   [ElectricalWaveAnimator] Starting electrical wave animation (10 steps)
   ```

### Test 2: Timeline Scrubbing

1. **Interact with Timeline Slider** (use mouse in Editor, VR controller on Quest)

2. **Expected Behavior:**
   - Beat markers appear along timeline
   - Hovering over timeline shows nearest beat index
   - After 0.5s of stopping, Beat Detail Panel appears
   - Shows PR interval, QRS duration, QT interval
   - Waveform visualization appears (if enabled)

3. **Check Console:**
   ```
   [TimelineController] Received 23 beats
   [TimelineController] Created 23 beat markers
   [TimelineController] Fetching detail for beat #5
   [BeatDetailPanel] Displayed detail for beat #5
   ```

### Test 3: Storytelling Journey Mode

1. **Call `StorytellingJourneyController.StartJourney()`** (attach to UI button)

2. **Expected Behavior:**
   - Narrative text appears with typewriter effect
   - 3D waypoints spawn at cardiac regions
   - Ambient lighting changes color (blue/red)
   - Waypoints glow and pulse

3. **Click a Waypoint:**
   - Narrative updates to focus on that region
   - New waypoints appear for sub-regions
   - Atmosphere transitions smoothly

4. **Check Console:**
   ```
   [StorytellingJourney] Created 5 waypoints
   [WaypointInteraction] Clicked waypoint: rbbb
   [StorytellingJourney] Displaying narrative (487 chars)
   ```

### Test 4: VR Deployment to Quest 2

1. **Build Settings:**
   ```
   Platform: Android
   Texture Compression: ASTC
   IL2CPP
   ARM64
   ```

2. **Player Settings:**
   ```
   Company Name: YourName
   Product Name: HoloHuman XR
   Minimum API Level: 29 (Android 10)
   Graphics API: OpenGLES3, Vulkan
   ```

3. **XR Plugin Management:**
   ```
   ✓ Oculus
   Stereo Rendering Mode: Multiview
   ```

4. **Build and Deploy:**
   ```
   File → Build Settings → Build and Run
   Connect Quest 2 via USB
   Enable Developer Mode on Quest
   ```

5. **Test in VR:**
   - All UI panels should be readable at 1.5m distance
   - Timeline scrubbing works with controller ray
   - Waypoints respond to controller hover/click
   - Frame rate stable at 72 FPS

---

## 6. Troubleshooting

### Issue 1: "ECG data file not assigned"

**Cause:** `ecgDataFile` not set in ECGHeartController Inspector

**Fix:**
```
1. Place ECG JSON in Assets/Resources/ECGSamples/
2. Drag JSON file to ECGHeartController → ecgDataFile field
3. Ensure file is a TextAsset (Unity recognizes .json automatically)
```

### Issue 2: "Failed to connect to backend"

**Cause:** Flask server not running or wrong IP address

**Fix:**
```
1. Verify Flask server is running: http://localhost:5000/api/health
2. Check ECGAPIClient baseURL matches Flask address
3. For Quest 2: Use PC's local IP (not localhost)
4. Check Windows Firewall allows port 5000
```

### Issue 3: Regions not updating colors

**Cause:** Region names mismatch between Unity and backend

**Fix:**
```
1. Open HeartRegionMapping Inspector
2. Verify all 10 regionNames EXACTLY match backend:
   - "sa_node" (not "SA_Node" or "saNode")
   - "rbbb" (not "RBBB" or "right_bundle")
3. Check Console for "Region not found: XXX" warnings
```

### Issue 4: Timeline shows no beats

**Cause:** `/api/ecg/beats` endpoint returning empty r_peaks

**Fix:**
```
1. Test endpoint manually:
   curl http://localhost:5000/api/ecg/beats -X POST -H "Content-Type: application/json" -d @sample_normal.json
2. Check response has "r_peaks": [324, 736, ...]
3. Verify ECG signal has valid waveform data
4. Check TimelineController → samplingRate = 400 Hz
```

### Issue 5: Waypoints not clickable in VR

**Cause:** Missing XR Interactable component

**Fix:**
```
1. Ensure waypoint prefab has XRSimpleInteractable component
2. Add Collider to waypoint (Sphere Collider recommended)
3. Set Layer to "Interactable" (create if needed)
4. Verify XR Ray Interactor on VR controller
```

### Issue 6: Performance drops below 72 FPS

**Cause:** Too many particles, inefficient materials, or high polygon count

**Fix:**
```
1. Reduce heart model polygon count (<50k triangles)
2. Use MaterialPropertyBlock instead of material instances
3. Limit particle emission rate (<100 particles/sec)
4. Disable connection lines if not needed
5. Use single-pass stereo rendering
6. Profile with Unity Profiler (CPU + GPU)
```

### Issue 7: JSON parsing errors

**Cause:** ECG JSON format doesn't match expected structure

**Fix:**
```
1. Verify JSON format matches:
   {"ecg_signal": [[...], [...], ...]}
2. Ensure 4096 samples × 12 leads
3. Check for NaN or Infinity values
4. Use Python script to generate valid test data:
   Backend/data/generate_test_ecg.py
```

---

## Quick Reference

### Backend Endpoints
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/health` | GET | Server health check |
| `/api/ecg/analyze` | POST | Full ECG analysis |
| `/api/ecg/beats` | POST | Get all R-peak positions |
| `/api/ecg/beat/<index>` | POST | Get detail for specific beat |
| `/api/ecg/segment` | POST | Analyze ECG segment |
| `/api/ecg/stream` | POST | Real-time streaming (unused) |

### Color Severity Mapping
| Severity | Color | RGB | Condition |
|----------|-------|-----|-----------|
| 0.0 - 0.3 | Green | (0, 1, 0) | Healthy |
| 0.3 - 0.6 | Yellow | (1, 1, 0) | Mild |
| 0.6 - 0.8 | Orange | (1, 0.5, 0) | Moderate |
| 0.8 - 1.0 | Red | (1, 0, 0) | Severe |

### Performance Targets (Quest 2)
- **Frame Rate:** 72 FPS (13.9ms frame budget)
- **API Response:** <300ms for /analyze
- **Polygon Count:** <50k total triangles
- **Draw Calls:** <150 per frame
- **Memory:** <2GB total

---

## Next Steps

After completing integration:

1. **Test all 5 sample ECG files** (normal, bradycardia, tachycardia, afib, rbbb)
2. **Record video demonstration** for hackathon submission
3. **Create user guide** for judges/users
4. **Optimize performance** for stable 72 FPS on Quest 2
5. **Add audio feedback** (heartbeat sound, voiceover narration)
6. **Polish UI** (colors, fonts, spacing)
7. **Test edge cases** (network failures, invalid data)

---

**Documentation Version:** 1.0
**Last Updated:** 2025-11-15
**Contact:** GitHub Issues - https://github.com/tyang4-ai/Immerse-the-Bay-Hackathon/issues
