# HoloHuman XR - Unity Heart Demo Setup Guide

**Complete guide for creating a VR heart visualization scene that displays ECG analysis data**

**Last Updated:** 2025-11-15
**Target Platform:** Unity 2021.3+ for Oculus Quest 2
**Backend Status:** ✅ 100% Complete

---

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Project Architecture](#project-architecture)
4. [Phase 1: Meshy.ai Heart Model Generation](#phase-1-meshyai-heart-model-generation)
5. [Phase 2: Unity Scene Setup](#phase-2-unity-scene-setup)
6. [Phase 3: Cardiac Region System](#phase-3-cardiac-region-system)
7. [Phase 4: ECG Integration](#phase-4-ecg-integration)
8. [Phase 5: Timeline & Beat Detail](#phase-5-timeline--beat-detail)
9. [Phase 6: Storytelling Journey Mode](#phase-6-storytelling-journey-mode)
10. [Testing & Troubleshooting](#testing--troubleshooting)
11. [Performance Optimization](#performance-optimization)
12. [Complete Code Reference](#complete-code-reference)

---

## Overview

### What You're Building

An immersive VR experience that visualizes cardiac electrical conduction through a 3D heart model, driven by real ECG analysis data from your backend API.

### Key Features

- **3D Heart Model** - Generated with Meshy.ai, optimized for Quest 2
- **10 Cardiac Regions** - SA node, AV node, His bundle, RBBB, LBBB, RA, LA, RV, LV, Purkinje fibers
- **Real-time ECG Analysis** - Backend provides diagnosis, heart rate, region health
- **Color-Coded Health** - Green (healthy) → Yellow (moderate) → Red (critical)
- **Electrical Wave Animation** - Visualize signal propagation through heart
- **Timeline Scrubbing** - Explore individual heartbeats in VR
- **Storytelling Journey** - "Down the Rabbit Hole" educational narrative with waypoints

### Backend Integration

Your Flask backend (100% complete) provides:
- ✅ 7 production-ready API endpoints
- ✅ ECG analysis with 6 cardiac condition detection
- ✅ 10-region cardiac mapping system
- ✅ Storytelling mode with narratives
- ✅ All performance targets met (<300ms analysis, <100ms beat detection)

**Backend Documentation:**
- [Backend/UNITY_QUICKSTART.md](../Backend/UNITY_QUICKSTART.md) - 15-minute quick start
- [Backend/API_INTEGRATION_GUIDE.md](../Backend/API_INTEGRATION_GUIDE.md) - Complete API reference
- [dev/active/unity-integration-context.md](../dev/active/unity-integration-context.md) - Unity integration context

---

## Prerequisites

### Required Software

- **Unity:** 2021.3 LTS or later
- **Oculus Integration SDK:** For Quest 2 VR support
- **Python 3.11+** (for backend)
- **Meshy.ai Account:** Free tier available (see Phase 1)

### Unity Packages

Install via Unity Package Manager:
```
com.unity.nuget.newtonsoft-json  (JSON parsing)
com.unity.xr.oculus              (Quest 2 VR)
com.unity.xr.interaction.toolkit (VR interactions)
```

### Backend Setup

**Start Flask server before Unity testing:**
```bash
cd Backend
python ecg_api.py
```

**Verify backend is running:**
```bash
curl http://localhost:5000/health
# Should return: {"status": "healthy", "model_loaded": true, ...}
```

**Network URLs:**
- **PC Unity Editor:** `http://localhost:5000`
- **Quest 2 VR:** `http://YOUR_PC_IP:5000` (e.g., `http://10.32.86.82:5000`)

**Note:** No Anthropic API key needed! Your backend uses fallback mode with pre-written narratives.

---

## Project Architecture

### Folder Structure

```
Assets/
├── Models/
│   └── heart.fbx                    # Meshy.ai generated heart model
├── Materials/
│   ├── HeartBase.mat                # Base heart material
│   └── RegionGlow.mat               # Emissive material for regions
├── Prefabs/
│   ├── CardiacRegionMarker.prefab   # Region visualization prefab
│   ├── BeatMarker.prefab            # Timeline beat marker
│   └── Waypoint.prefab              # Journey waypoint marker
├── Resources/
│   ├── sample_normal.json           # From Backend/dummy_data/
│   ├── sample_bradycardia.json
│   └── sample_tachycardia.json
├── Scenes/
│   └── HoloHumanVR.unity           # Main VR scene
└── Scripts/
    ├── API/
    │   └── ECGAPIClient.cs         # HTTP client (from Backend docs)
    ├── Heart/
    │   ├── CardiacRegionMarker.cs  # Individual region control
    │   ├── ECGHeartController.cs   # Main orchestrator
    │   ├── HeartRegionMapping.cs   # Region mapping system
    │   └── ElectricalWaveAnimator.cs # Wave animation
    ├── UI/
    │   ├── TimelineController.cs   # Beat scrubbing
    │   └── BeatDetailPanel.cs      # Beat detail display
    └── Journey/
        ├── StorytellingJourneyController.cs # VR narrative
        └── WaypointInteraction.cs  # Waypoint interactions
```

### Unity Scene Hierarchy

```
HoloHumanVR_Scene
├── XR Origin (VR Camera + Controllers)
├── Directional Light
├── Environment
│   └── DarkSpace (black skybox)
├── Heart System
│   ├── HeartModel (3D mesh from Meshy.ai)
│   ├── RegionMarkers (Parent)
│   │   ├── SANode_Marker
│   │   ├── AVNode_Marker
│   │   ├── BundleOfHis_Marker
│   │   ├── RightBundleBranch_Marker
│   │   ├── LeftBundleBranch_Marker
│   │   ├── PurkinjeFibers_Marker
│   │   ├── RightAtrium_Marker
│   │   ├── LeftAtrium_Marker
│   │   ├── RightVentricle_Marker
│   │   └── LeftVentricle_Marker
│   └── Controllers
│       ├── ECGHeartController
│       ├── HeartRegionMapping
│       └── ElectricalWaveAnimator
├── ECG System
│   ├── ECGAPIClient (Singleton)
│   └── TimelineController
├── UI Canvas (World Space)
│   ├── DiagnosisPanel
│   ├── HeartRateDisplay
│   ├── RegionInfoPanel
│   ├── TimelineSlider
│   └── AnalyzeButton
└── Journey System
    └── StorytellingJourneyController
```

---

## Phase 1: Meshy.ai Heart Model Generation

### Why Meshy.ai?

- **AI-powered 3D generation** from text prompts
- **VR-optimized** low-poly models
- **Fast generation** (2-5 minutes)
- **Free tier available** (50 credits/month)
- **Sponsor tool** for Immerse the Bay Hackathon

### Step 1: Sign Up (5 minutes)

1. Visit: https://www.meshy.ai/
2. Click "Sign Up" (use school email for extra credits)
3. Verify email
4. You get **50 free credits** (1 credit = 1 generation)

### Step 2: Generate Heart Model (10-15 minutes)

1. **Navigate to:** "Text to 3D" in top menu
2. **Enter prompt:**
   ```
   Anatomically accurate human heart with visible chambers (right atrium, left atrium, right ventricle, left ventricle), conduction system pathways visible, realistic medical visualization texture, optimized for VR, low-poly geometry, separated anatomical regions, educational model
   ```

3. **Settings:**
   - **Art Style:** Realistic
   - **Topology:** Quad (better for animation)
   - **Poly Count:** Medium (20k-50k triangles)
   - **Negative Prompt:** "cartoon, stylized, anime, high-poly, smooth, simplified, oversimplified"

4. **Click "Generate"** - Wait 2-5 minutes

5. **Preview:**
   - Rotate model to check all angles
   - Verify chambers are visible
   - Check poly count (should be <50k for Quest 2)

6. **Regenerate if needed:**
   - If too simple: Add "detailed conduction pathways" to prompt
   - If too complex: Add "low-poly, game-ready" to prompt
   - Try 2-3 variations to get best result

### Step 3: Download Model (2 minutes)

1. **Click "Download"**
2. **Select Format:** FBX (best for Unity)
3. **Include Textures:** YES (check the box)
4. **Download to:** `Assets/Models/heart.fbx`

**Expected Files:**
- `heart.fbx` (3D model)
- `heart_BaseColor.png` (diffuse texture)
- `heart_Normal.png` (normal map - optional)
- `heart_Roughness.png` (roughness - optional)

### Step 4: Import to Unity (5 minutes)

1. **Drag `heart.fbx`** into `Assets/Models/` folder in Unity

2. **Unity auto-imports:**
   - Creates mesh
   - Creates materials
   - Assigns textures

3. **Check Inspector:**
   - Select `heart.fbx` in Project window
   - Go to "Model" tab
   - **Scale Factor:** 1.0
   - **Mesh Compression:** Off (for VR quality)
   - Click "Apply"

4. **Verify Poly Count:**
   - Select `heart` mesh in scene
   - Check Stats window: Should be <50,000 tris
   - If >50k: See [Optimization](#heart-model-too-high-poly) section

5. **Position in Scene:**
   - Drag `heart.fbx` into Hierarchy
   - Set Transform:
     - Position: (0, 1.5, 2) - Eye level, 2m forward
     - Rotation: (0, 0, 0)
     - Scale: (0.3, 0.3, 0.3) - Adjust to hand size

### Alternative: Free Heart Models (Backup Plan)

If Meshy.ai doesn't work:

**TurboSquid (Free):**
- https://www.turbosquid.com/Search/3D-Models/free/low-poly/human-heart
- Filter: Free, <50k polygons, FBX format

**Sketchfab (Z-Anatomy):**
- https://sketchfab.com/Z-Anatomy
- Search: "human heart low poly"
- Download as FBX

**Free3D:**
- https://free3d.com/3d-models/lowpoly-heart
- Filter: Free downloads, FBX format

---

## Phase 2: Unity Scene Setup

### Step 1: Install Required Packages (5 minutes)

**Unity Package Manager** (Window → Package Manager):

1. **Newtonsoft.Json** (JSON parsing)
   ```
   Add package by name: com.unity.nuget.newtonsoft-json
   ```

2. **XR Plugin Management** (VR support)
   ```
   Add package by name: com.unity.xr.management
   ```

3. **XR Interaction Toolkit** (VR interactions)
   ```
   Add package by name: com.unity.xr.interaction.toolkit
   ```

4. **Oculus XR Plugin** (Quest 2)
   ```
   Add package by name: com.unity.xr.oculus
   ```

### Step 2: Create Folder Structure (2 minutes)

Right-click in Project window → Create Folder:
```
Assets/
├── Models/
├── Materials/
├── Prefabs/
├── Resources/
├── Scenes/
└── Scripts/
    ├── API/
    ├── Heart/
    ├── UI/
    └── Journey/
```

### Step 3: Copy ECG API Client (3 minutes)

1. **Open:** `Backend/API_INTEGRATION_GUIDE.md`
2. **Copy entire `ECGAPIClient.cs`** code (lines ~200-800)
3. **Create new script:** `Assets/Scripts/API/ECGAPIClient.cs`
4. **Paste code** and save

**The script includes:**
- Singleton pattern for global access
- All 7 API endpoint methods
- 15+ response model classes for JSON deserialization
- Error handling with structured error IDs
- Unity coroutine-based async requests

### Step 4: Copy Sample ECG Data (2 minutes)

**Copy from backend to Unity:**
```bash
# Copy these files from Backend/dummy_data/ to Assets/Resources/
sample_normal.json        # 72 BPM healthy heart
sample_bradycardia.json   # 50 BPM slow heart
sample_tachycardia.json   # 110 BPM fast heart
```

**In Unity:**
- Drag JSON files into `Assets/Resources/` folder
- Unity auto-imports as TextAsset

### Step 5: Create Main Scene (10 minutes)

1. **Create new scene:** File → New Scene → Basic (Built-in Render Pipeline)
2. **Save as:** `Assets/Scenes/HoloHumanVR.unity`

3. **Set up XR Rig:**
   - GameObject → XR → XR Origin (Action-based)
   - This creates VR camera and controllers
   - Position at (0, 0, 0)

4. **Configure lighting:**
   - Select Directional Light
   - Color: Dark blue (#202040) - "Down the Rabbit Hole" theme
   - Intensity: 0.5

5. **Set Skybox:**
   - Window → Rendering → Lighting Settings
   - Skybox Material: None (or create dark material)
   - Ambient Color: Very dark gray (#0A0A0A)

6. **Place heart model:**
   - Drag `heart.fbx` from Models/ into Hierarchy
   - Rename to "HeartModel"
   - Position: (0, 1.5, 2) - Eye level, 2m forward
   - Add XR Grab Interactable component (for VR rotation)

7. **Create ECG System GameObjects:**
   - Create Empty: "ECG System" at (0,0,0)
   - Create Empty child: "ECG API Client"
   - Add Component: ECGAPIClient script
   - **Set Backend URL in Inspector:** `http://localhost:5000`

8. **Test Scene:**
   - Press Play
   - You should see heart model in Game view
   - Check Console for "ECGAPIClient initialized" (no errors)

---

## Phase 3: Cardiac Region System

### Understanding the 10 Cardiac Regions

Your backend maps ECG conditions to 10 specific cardiac anatomical regions:

| Region | Backend Name | Anatomical Location | Function |
|--------|--------------|---------------------|----------|
| **SA Node** | `sa_node` | Top of right atrium | Natural pacemaker, initiates heartbeat |
| **Right Atrium** | `ra` | Upper right chamber | Receives deoxygenated blood |
| **Left Atrium** | `la` | Upper left chamber | Receives oxygenated blood |
| **AV Node** | `av_node` | Between atria/ventricles | Delays signal 0.1s |
| **Bundle of His** | `bundle_his` | Top of interventricular septum | Conducts to bundle branches |
| **Right Bundle Branch** | `rbbb` | Right side of septum | Conducts to right ventricle |
| **Left Bundle Branch** | `lbbb` | Left side of septum | Conducts to left ventricle |
| **Purkinje Fibers** | `purkinje` | Inner ventricular walls | Final conduction network |
| **Right Ventricle** | `rv` | Lower right chamber | Pumps to lungs |
| **Left Ventricle** | `lv` | Lower left chamber | Pumps to body |

### Backend Response Structure

When you call `POST /api/ecg/analyze`, you receive:

```json
{
  "region_health": {
    "sa_node": {
      "severity": 0.0,               // 0.0 = healthy, 1.0 = critical
      "color": [0.0, 1.0, 0.0],      // RGB green (healthy)
      "activation_delay_ms": 0,      // Normal timing
      "affected_by": []              // No conditions
    },
    "rbbb": {
      "severity": 0.89,              // 89% severity (critical)
      "color": [1.0, 0.0, 0.0],      // RGB red (critical)
      "activation_delay_ms": 320,    // DELAYED (normal: 160ms)
      "affected_by": ["RBBB"]        // Condition affecting this region
    },
    // ... all 10 regions
  },
  "activation_sequence": [
    ["sa_node", 0],          // Fires at 0ms
    ["ra", 25],              // Activates at 25ms
    ["la", 30],              // Activates at 30ms
    ["av_node", 50],         // Activates at 50ms
    ["bundle_his", 150],     // Activates at 150ms
    ["rbbb", 320],           // DELAYED! (normal: 160ms)
    ["lbbb", 160],           // Normal timing
    ["purkinje", 180],
    ["rv", 360],             // DELAYED (normal: 200ms)
    ["lv", 200]
  ]
}
```

### Option A: Separated Mesh Parts (If Meshy.ai Generated Them)

**If your heart model has separate mesh parts for each region:**

1. **Expand `HeartModel` in Hierarchy**
2. **You'll see child meshes like:**
   - `SA_Node_Mesh`
   - `RightAtrium_Mesh`
   - `AV_Node_Mesh`
   - etc.

3. **Rename to match backend names:**
   - Rename each mesh to exact backend name: `sa_node`, `ra`, `la`, `av_node`, `bundle_his`, `rbbb`, `lbbb`, `purkinje`, `rv`, `lv`

4. **Add CardiacRegionMarker script to each:**
   - Select each mesh
   - Add Component → CardiacRegionMarker
   - Set `regionName` field to match (e.g., "sa_node")

5. **Create emissive materials:**
   - Create Material: `RegionGlow`
   - Shader: Standard
   - Enable Emission: Check the box
   - Emission Color: Will be set via script
   - Assign to each region mesh

### Option B: Single Mesh (Most Likely Scenario)

**If your heart model is ONE solid mesh:**

You'll create empty GameObject "markers" at anatomical positions.

**Step 1: Create marker prefab (10 minutes)**

1. **Create Empty GameObject:** "CardiacRegionMarker"
2. **Add Components:**
   - CardiacRegionMarker script (see Scripts section)
   - Light component (Point Light)
     - Color: White (will be changed by script)
     - Range: 0.5
     - Intensity: 0 (will be animated)
   - Particle System (optional - for electrical effect)
3. **Save as Prefab:** `Assets/Prefabs/CardiacRegionMarker.prefab`

**Step 2: Position 10 markers on heart model (20-30 minutes)**

Create 10 instances of the prefab and position manually:

```
Heart System/
└── RegionMarkers/
    ├── SANode_Marker
    │   Position: Top of right atrium (approx: (0.15, 0.3, 0))
    │   regionName: "sa_node"
    │
    ├── RightAtrium_Marker
    │   Position: Center of right atrium (approx: (0.1, 0.15, 0))
    │   regionName: "ra"
    │
    ├── LeftAtrium_Marker
    │   Position: Center of left atrium (approx: (-0.1, 0.15, 0))
    │   regionName: "la"
    │
    ├── AVNode_Marker
    │   Position: Between atria and ventricles (approx: (0, 0, 0))
    │   regionName: "av_node"
    │
    ├── BundleOfHis_Marker
    │   Position: Top of septum (approx: (0, -0.05, 0.05))
    │   regionName: "bundle_his"
    │
    ├── RightBundleBranch_Marker
    │   Position: Right side of septum (approx: (0.08, -0.15, 0.05))
    │   regionName: "rbbb"
    │
    ├── LeftBundleBranch_Marker
    │   Position: Left side of septum (approx: (-0.08, -0.15, 0.05))
    │   regionName: "lbbb"
    │
    ├── PurkinjeFibers_Marker
    │   Position: Inner ventricular walls (approx: (0, -0.25, 0.08))
    │   regionName: "purkinje"
    │
    ├── RightVentricle_Marker
    │   Position: Center of right ventricle (approx: (0.1, -0.2, 0))
    │   regionName: "rv"
    │
    └── LeftVentricle_Marker
        Position: Center of left ventricle (approx: (-0.1, -0.2, 0))
        regionName: "lv"
```

**Tips for positioning:**
- Use Scene view to rotate heart and find correct positions
- Reference anatomical diagrams (Google "heart conduction system")
- Positions are approximate - visual accuracy is more important than exact mm
- Press F to focus on selected marker in Scene view

**Step 3: Configure HeartRegionMapping script**

1. **Create Empty GameObject:** "HeartRegionMapping" (child of Heart System)
2. **Add script:** HeartRegionMapping (see Scripts section)
3. **In Inspector, drag all 10 markers** into `heartRegions` array (size 10)
4. **Verify each marker has correct `regionName`** string set

---

## Phase 4: ECG Integration

### Step 1: Create ECGHeartController (Main Orchestrator)

This script connects everything:
- Loads ECG data from JSON file
- Calls backend API
- Updates region marker colors based on severity
- Triggers electrical wave animation

**Location:** `Assets/Scripts/Heart/ECGHeartController.cs`
**Full code:** See [Scripts folder](Scripts/Heart/ECGHeartController.cs)

**Key responsibilities:**
```csharp
void Start()
{
    LoadECGData();                    // Parse JSON file
    StartCoroutine(AnalyzeAndVisualize()); // Call API
}

void UpdateHeartRegions(RegionHealthData)
{
    // Update marker colors based on severity
    // Green (healthy) → Yellow (moderate) → Red (critical)
}

IEnumerator AnimateActivationSequence(ActivationSequence)
{
    // Animate electrical wave through regions in order
    // Use activation timing from backend
}
```

### Step 2: Set Up ECGHeartController GameObject

1. **Create Empty GameObject:** "ECGHeartController" (child of Heart System)
2. **Add Component:** ECGHeartController script
3. **In Inspector:**
   - **API Client:** Drag "ECG API Client" GameObject
   - **ECG Data File:** Drag `sample_normal.json` from Resources
   - **Region Markers:** Array of 10 markers (drag all 10)
   - **Diagnosis Text:** Create UI Text and drag here
   - **Heart Rate Text:** Create UI Text and drag here

### Step 3: Test ECG Integration

1. **Start Flask backend:**
   ```bash
   cd Backend
   python ecg_api.py
   ```

2. **Press Play in Unity**

3. **Expected Console Output:**
   ```
   [ECG API] Backend is healthy! Model loaded: True
   ECG loaded: 4096 samples × 12 leads
   [ECG API] POST /api/ecg/analyze (mode: clinical_expert)
   [ECG API] Analysis complete: sinus_bradycardia (92%)
   [ECG API] Heart rate: 52.3 BPM
   [ECG API] Processing time: 267.4ms
   Updating region: sa_node (severity: 0.0, color: green)
   Updating region: rbbb (severity: 0.89, color: red)
   ...
   ```

4. **Expected Visuals:**
   - Region markers change color based on severity
   - Healthy regions glow green
   - Affected regions glow yellow/orange/red
   - Electrical wave animates through regions in sequence

### Step 4: Color Mapping System

**Backend provides RGB colors:**
```json
"color": [1.0, 0.0, 0.0]  // Red for critical severity
"color": [1.0, 0.5, 0.0]  // Orange for moderate
"color": [0.0, 1.0, 0.0]  // Green for healthy
```

**Unity converts to Color:**
```csharp
Color regionColor = new Color(
    health.color[0],  // R
    health.color[1],  // G
    health.color[2]   // B
);

// Apply to Light component
light.color = regionColor;
light.intensity = health.severity * 3f; // Brighter = more severe

// Apply to Emissive material
material.SetColor("_EmissionColor", regionColor * 2f);
```

---

## Phase 5: Timeline & Beat Detail

### Overview

Create a VR timeline UI that lets users:
- See all heartbeats as markers on a timeline
- Scrub through time using VR controller
- Focus on individual beats to see P-QRS-T waveform details

### Backend Endpoints Used

**1. Get all beat positions:**
```http
POST /api/ecg/beats
Response: {
  "r_peaks": [30, 357, 690, 1023, 1357, ...],  // Sample indices
  "beat_count": 13,
  "avg_rr_interval_ms": 831.5
}
```

**2. Get single beat detail:**
```http
POST /api/ecg/beat/2
Response: {
  "beat_index": 2,
  "waveform": {
    "p_wave": {"onset": 630, "peak": 640, "offset": 660},
    "qrs_complex": {"onset": 670, "peak": 690, "offset": 720},
    "t_wave": {"onset": 740, "peak": 769, "offset": 769}
  },
  "intervals": {
    "pr_interval_ms": 100.0,
    "qrs_duration_ms": 125.0,
    "qt_interval_ms": 247.5
  }
}
```

### Step 1: Create Timeline UI (15 minutes)

1. **Create UI Canvas:**
   - GameObject → UI → Canvas
   - Canvas: Render Mode = World Space
   - Position: (0, 1.0, 2.5) - Below eye level
   - Scale: (0.001, 0.001, 0.001) - Smaller for VR
   - Width: 2000, Height: 400

2. **Create Timeline Slider:**
   - Right-click Canvas → UI → Slider
   - Rename to "TimelineSlider"
   - RectTransform: Width 1800, Height 60
   - Min Value: 0, Max Value: 10.24 (10.24 seconds of ECG)

3. **Create Beat Marker Prefab:**
   - Create UI → Image
   - Size: 10x40 pixels
   - Color: Cyan (#00FFFF)
   - Save as Prefab: `BeatMarker.prefab`

4. **Create Beat Markers Parent:**
   - Create Empty under Canvas: "BeatMarkersParent"
   - This will hold all beat marker instances

### Step 2: Implement TimelineController

**Location:** `Assets/Scripts/UI/TimelineController.cs`
**Full code:** See [Scripts folder](Scripts/UI/TimelineController.cs)

**Key methods:**
```csharp
public void InitializeTimeline(List<int> rPeaks)
{
    // Create visual markers for each beat
    foreach (int rPeak in rPeaks)
    {
        float timeSeconds = rPeak / 400f; // 400 Hz sampling
        CreateBeatMarker(timeSeconds);
    }
}

public void OnTimelineValueChanged(float normalizedTime)
{
    // User scrubbed timeline
    // Find nearest beat and show detail
    int beatIndex = FindNearestBeat(normalizedTime);
    ShowBeatDetail(beatIndex);
}
```

### Step 3: Create Beat Detail Panel (10 minutes)

1. **Create UI Panel:**
   - Right-click Canvas → UI → Panel
   - Rename to "BeatDetailPanel"
   - Size: 800x600
   - Position: Right side of timeline

2. **Add TextMeshPro fields:**
   - `BeatIndexText`: "Beat #2"
   - `PRIntervalText`: "PR Interval: 100ms"
   - `QRSDurationText`: "QRS Duration: 125ms"
   - `QTIntervalText`: "QT Interval: 247ms"
   - `AnnotationText`: "Wide QRS complex (possible bundle branch block)"

3. **Add waveform visualization (optional):**
   - Use Unity LineRenderer to draw P-QRS-T waveform
   - Plot raw samples from beat detail response

### Step 4: Wire Up Timeline System

1. **Create Empty GameObject:** "TimelineController" (child of ECG System)
2. **Add Component:** TimelineController script
3. **In Inspector:**
   - **Timeline Slider:** Drag TimelineSlider UI
   - **Beat Markers Parent:** Drag BeatMarkersParent
   - **Beat Marker Prefab:** Drag BeatMarker prefab
   - **Beat Detail Panel:** Drag BeatDetailPanel

4. **Connect to ECGHeartController:**
   ```csharp
   // In ECGHeartController.cs Start():
   yield return apiClient.GetBeats(
       ecgSignal,
       onSuccess: (response) =>
       {
           // Pass beat positions to timeline
           timelineController.InitializeTimeline(response.r_peaks);
       }
   );
   ```

### Step 5: Test Timeline

1. **Press Play**
2. **Expected:**
   - Timeline slider appears in VR
   - Beat markers appear at correct positions (13 beats)
   - Scrubbing timeline updates beat detail panel
   - Console shows: "Beat detail fetched for beat #X"

---

## Phase 6: Storytelling Journey Mode

### Overview

Storytelling mode transforms the VR experience into an educational journey through the heart's electrical system, using your backend's pre-written narratives.

### Backend Storytelling API

```http
POST /api/ecg/analyze
{
  "ecg_signal": [...],
  "output_mode": "storytelling",
  "region_focus": "rbbb"  // Optional: focus on specific region
}

Response: {
  "storytelling_narrative": {
    "location_name": "Right Bundle Branch",
    "narrative": "You find yourself in the Right Bundle Branch...",
    "waypoints": [
      {
        "region": "av_node",
        "teaser": "Where the signal first slowed down"
      },
      {
        "region": "bundle_his",
        "teaser": "The fork in the road"
      },
      {
        "region": "rbbb",
        "teaser": "The blocked pathway"
      }
    ],
    "atmosphere": {
      "lighting": "dim red pulse",
      "sound": "slow irregular heartbeat",
      "particles": "electrical sparks"
    }
  }
}
```

### Step 1: Create Waypoint Prefab (10 minutes)

1. **Create 3D Sphere:**
   - GameObject → 3D Object → Sphere
   - Scale: (0.05, 0.05, 0.05) - Small marker
   - Material: Emissive cyan

2. **Add WorldSpace UI Label:**
   - Create UI → Text - TextMeshPro (child of sphere)
   - Canvas: Render Mode = World Space
   - Position above sphere
   - Font Size: 24
   - Color: White

3. **Add Components:**
   - WaypointInteraction script (handles click)
   - Sphere Collider (for ray interaction)

4. **Save as Prefab:** `Waypoint.prefab`

### Step 2: Implement StorytellingJourneyController

**Location:** `Assets/Scripts/Journey/StorytellingJourneyController.cs`
**Full code:** See [Scripts folder](Scripts/Journey/StorytellingJourneyController.cs)

**Key methods:**
```csharp
public void StartJourney(string regionFocus = null)
{
    // Call storytelling API
    yield return apiClient.AnalyzeECG(
        ecgSignal,
        outputMode: "storytelling",
        regionFocus: regionFocus,
        onSuccess: (response) =>
        {
            DisplayNarrative(response.storytelling_narrative);
            CreateWaypoints(response.storytelling_narrative.waypoints);
            SetAtmosphere(response.storytelling_narrative.atmosphere);
        }
    );
}

void CreateWaypoints(List<Waypoint> waypoints)
{
    // Create 3D waypoint markers at cardiac regions
    foreach (var waypoint in waypoints)
    {
        Vector3 position = FindRegionPosition(waypoint.region);
        CreateWaypointMarker(position, waypoint.teaser);
    }
}
```

### Step 3: Create Narrative UI Panel (10 minutes)

1. **Create UI Panel:**
   - Right-click Canvas → UI → Panel
   - Rename to "NarrativePanel"
   - Size: 1000x400
   - Position: Top center of view
   - Background: Semi-transparent dark (#00000080)

2. **Add TextMeshPro fields:**
   - `LocationNameText`: Large bold text for location
   - `NarrativeText`: Scrollable text area for story
   - `AtmosphereText`: Small text for atmosphere description

### Step 4: Implement Atmosphere System (15 minutes)

**Create AtmosphereController.cs:**

```csharp
public class AtmosphereController : MonoBehaviour
{
    [SerializeField] private Light directionalLight;
    [SerializeField] private ParticleSystem particleEffect;
    [SerializeField] private AudioSource audioSource;

    public void SetAtmosphere(AtmosphereData atmosphere)
    {
        // Parse atmosphere description
        // Example: {"lighting": "dim red pulse", "sound": "slow heartbeat", ...}

        // Adjust lighting
        if (atmosphere.lighting.Contains("red"))
        {
            directionalLight.color = Color.red;
            StartCoroutine(PulseLighting());
        }

        // Adjust particles
        if (atmosphere.particles.Contains("sparks"))
        {
            particleEffect.Play();
        }

        // Adjust sound
        if (atmosphere.sound.Contains("heartbeat"))
        {
            audioSource.clip = heartbeatClip;
            audioSource.Play();
        }
    }
}
```

### Step 5: Add VR Interaction

**Waypoint Click Handler:**
```csharp
// WaypointInteraction.cs
public class WaypointInteraction : MonoBehaviour
{
    public string regionName;
    public string teaserText;

    void OnMouseDown() // Works with VR ray pointer
    {
        // User clicked waypoint, drill down to this region
        FindObjectOfType<StorytellingJourneyController>()
            .StartJourney(regionName); // Recursive journey!
    }
}
```

### Step 6: Test Journey Mode

1. **Press Play**
2. **Trigger journey:**
   - Click "Start Journey" button
   - Or call `journeyController.StartJourney()` in code

3. **Expected:**
   - Narrative panel shows story text
   - Waypoint markers appear at cardiac regions
   - Lighting/atmosphere changes based on narrative
   - Clicking waypoint drills down to that region's story

---

## Testing & Troubleshooting

### Pre-Flight Checklist

**Backend:**
- [ ] Flask server running (`python Backend/ecg_api.py`)
- [ ] `/health` endpoint returns 200 OK
- [ ] Sample ECG data in `Backend/dummy_data/`

**Unity:**
- [ ] Newtonsoft.Json package installed
- [ ] ECGAPIClient.cs no compile errors
- [ ] Backend URL set correctly in Inspector
- [ ] Heart model imported (<50k triangles)
- [ ] All 10 region markers created and positioned

### Common Issues

#### "Cannot connect to server"

**Symptoms:** Console shows "Connection refused" or timeout

**Fix:**
```bash
# 1. Restart Flask server
cd Backend
python ecg_api.py

# 2. Test from browser
http://localhost:5000/health

# 3. Check Backend URL in Unity Inspector
Should be: http://localhost:5000 (PC)
           http://YOUR_IP:5000 (Quest 2)

# 4. Check firewall (Windows)
Allow Python through firewall for Private networks
```

#### "Invalid ECG shape" error

**Symptoms:** API returns 400 error

**Fix:**
- Use sample data from `Backend/dummy_data/`
- Verify JSON structure: `{"ecg_signal": [[...], [...], ...]}`
- Shape must be exactly (4096, 12) - 4096 samples × 12 leads

#### Regions not updating colors

**Symptoms:** All markers stay same color

**Fix:**
```csharp
// Check CardiacRegionMarker script:
// 1. Verify Light component exists
Debug.Log($"Light: {GetComponent<Light>()}");

// 2. Verify regionName is set correctly
Debug.Log($"Region name: {regionName}");

// 3. Check severity value
Debug.Log($"Severity: {severity}");

// 4. Check region_health response
// In ECGHeartController, add:
Debug.Log(JsonUtility.ToJson(response.region_health));
```

#### Electrical wave animation not playing

**Symptoms:** No animation, or all regions activate at once

**Fix:**
```csharp
// Check activation_sequence response
Debug.Log(JsonUtility.ToJson(response.activation_sequence));

// Verify delay timing in ElectricalWaveAnimator:
float delaySeconds = activationDelayMs / 1000f;
yield return new WaitForSeconds(delaySeconds);

// Check coroutine is actually running
Debug.Log($"Animating region: {regionName} at {Time.time}s");
```

#### Heart model too high-poly

**Symptoms:** FPS drops below 72 on Quest 2

**Fix (Blender):**
1. Export heart.fbx from Unity
2. Import to Blender
3. Select mesh → Add Modifier → Decimate
4. Set Ratio to 0.3-0.5 (reduces to 30-50% polygons)
5. Apply modifier
6. File → Export → FBX
7. Re-import to Unity

#### Quest 2 can't connect to backend

**Symptoms:** Works in Unity Editor, but not on Quest 2

**Fix:**
```bash
# 1. Find PC IP address
ipconfig  # Windows
ifconfig  # Mac/Linux
# Look for IPv4: 192.168.1.XXX

# 2. Update Unity Backend URL
http://192.168.1.XXX:5000  # Use your IP

# 3. Ensure PC and Quest 2 on same WiFi

# 4. Test from Quest 2 browser
Open browser on Quest 2
Navigate to: http://192.168.1.XXX:5000/health
Should return JSON

# 5. Allow firewall
Windows Settings → Firewall → Allow Python
```

---

## Performance Optimization

### Quest 2 Target: 72 FPS (13.9ms frame budget)

### 1. Heart Model Optimization

**Poly Count:**
- Target: <30,000 triangles
- Max acceptable: 50,000 triangles
- Check: Select model → Stats window

**Materials:**
- Use Standard shader (not HDRP/URP)
- Minimize texture size: 1024x1024 max
- Use texture compression: ASTC 6x6

**Lighting:**
- Use baked lighting where possible
- Limit real-time lights to 4-6
- Disable shadows on region marker lights

### 2. API Call Optimization

**Cache responses:**
```csharp
// Don't call API every frame
private Dictionary<string, AnalysisResponse> responseCache = new();

IEnumerator AnalyzeECG(string sampleName)
{
    if (responseCache.ContainsKey(sampleName))
    {
        UseC achedResponse(responseCache[sampleName]);
        yield break;
    }

    // Call API only if not cached
    yield return apiClient.AnalyzeECG(...);
    responseCache[sampleName] = response;
}
```

**Async timeline updates:**
```csharp
// Don't call beat detail API during scrubbing
// Only call when user stops scrubbing for 0.5s
private float lastScrubTime;
private int pendingBeatIndex;

void OnTimelineScrubbe d(float time)
{
    lastScrubTime = Time.time;
    pendingBeatIndex = FindNearestBeat(time);
}

void Update()
{
    if (Time.time - lastScrubTime > 0.5f && pendingBeatIndex >= 0)
    {
        StartCoroutine(FetchBeatDetail(pendingBeatIndex));
        pendingBeatIndex = -1;
    }
}
```

### 3. Particle System Optimization

**Region marker particles:**
- Max Particles: 50 per system
- Emission Rate: 10-20 per second
- Particle Size: Small (0.01-0.02)
- Use GPU Instancing: Check the box

### 4. UI Optimization

**TextMeshPro:**
- Use SDFs (Signed Distance Fields)
- Limit text updates to max 5 per second
- Pool text objects, don't create/destroy

**Canvas:**
- Use World Space canvas (not Screen Space Overlay)
- Separate canvases for static vs dynamic UI
- Disable raycast target on non-interactive elements

### 5. Profiling

**Unity Profiler** (Window → Analysis → Profiler):
- Monitor CPU time: Should be <13.9ms
- Monitor GPU time: Should be <13.9ms
- Check API coroutines: Should not block main thread

**Oculus Developer Hub:**
- Install from Oculus website
- Monitor frame rate in real-time on Quest 2
- Check thermal throttling

---

## Complete Code Reference

### File: CardiacRegionMarker.cs

**Purpose:** Controls individual cardiac region visualization (color, glow, particles)

**Location:** `Assets/Scripts/Heart/CardiacRegionMarker.cs`

**See:** [Unity/Scripts/Heart/CardiacRegionMarker.cs](Scripts/Heart/CardiacRegionMarker.cs)

**Key features:**
- Updates glow color based on severity
- Triggers electrical wave particle effect
- Pulsing animation for active regions
- Integrates with Light and ParticleSystem components

---

### File: ECGHeartController.cs

**Purpose:** Main orchestrator connecting API, heart model, and UI

**Location:** `Assets/Scripts/Heart/ECGHeartController.cs`

**See:** [Unity/Scripts/Heart/ECGHeartController.cs](Scripts/Heart/ECGHeartController.cs)

**Key features:**
- Loads ECG data from JSON
- Calls backend `/api/ecg/analyze`
- Updates all 10 region markers with health data
- Triggers electrical wave animation sequence
- Updates diagnosis UI

---

### File: HeartRegionMapping.cs

**Purpose:** Maps backend region names to Unity GameObjects

**Location:** `Assets/Scripts/Heart/HeartRegionMapping.cs`

**See:** [Unity/Scripts/Heart/HeartRegionMapping.cs](Scripts/Heart/HeartRegionMapping.cs)

**Key features:**
- Serializable array of 10 regions
- Lookup by region name
- Material and GameObject references
- Inspector-friendly configuration

---

### File: ElectricalWaveAnimator.cs

**Purpose:** Animates electrical signal propagation through heart

**Location:** `Assets/Scripts/Heart/ElectricalWaveAnimator.cs`

**See:** [Unity/Scripts/Heart/ElectricalWaveAnimator.cs](Scripts/Heart/ElectricalWaveAnimator.cs)

**Key features:**
- Uses backend activation_sequence timing
- Coroutine-based animation
- Triggers region particle effects in sequence
- Pulsing glow animation

---

### File: TimelineController.cs

**Purpose:** VR timeline UI for beat scrubbing

**Location:** `Assets/Scripts/UI/TimelineController.cs`

**See:** [Unity/Scripts/UI/TimelineController.cs](Scripts/UI/TimelineController.cs)

**Key features:**
- Creates beat markers from r_peaks data
- VR slider interaction
- Finds nearest beat on scrub
- Calls beat detail API

---

### File: BeatDetailPanel.cs

**Purpose:** Displays P-QRS-T waveform details for focused beat

**Location:** `Assets/Scripts/UI/BeatDetailPanel.cs`

**See:** [Unity/Scripts/UI/BeatDetailPanel.cs](Scripts/UI/BeatDetailPanel.cs)

**Key features:**
- Displays PR interval, QRS duration, QT interval
- Shows beat annotations
- Optional LineRenderer for waveform visualization
- Updates on timeline scrub

---

### File: StorytellingJourneyController.cs

**Purpose:** VR narrative journey through cardiac regions

**Location:** `Assets/Scripts/Journey/StorytellingJourneyController.cs`

**See:** [Unity/Scripts/Journey/StorytellingJourneyController.cs](Scripts/Journey/StorytellingJourneyController.cs)

**Key features:**
- Calls storytelling API with region focus
- Creates 3D waypoint markers
- Displays narrative text
- Sets VR atmosphere (lighting, particles, sound)
- Recursive journey mode (click waypoint → drill down)

---

### File: WaypointInteraction.cs

**Purpose:** Handles VR interaction with waypoint markers

**Location:** `Assets/Scripts/Journey/WaypointInteraction.cs`

**See:** [Unity/Scripts/Journey/WaypointInteraction.cs](Scripts/Journey/WaypointInteraction.cs)

**Key features:**
- VR ray pointer detection
- Click to drill down to region
- Hover glow effect
- Teaser text display

---

## Next Steps

### Immediate (This Week)

1. **Complete Phase 1-3:** Get basic ECG visualization working
2. **Test with all 3 sample files:**
   - `sample_normal.json` - Should show all green regions
   - `sample_bradycardia.json` - Should show slow wave animation
   - `sample_tachycardia.json` - Should show fast wave animation

### Before Hackathon Demo

1. **Polish VR interactions:**
   - Smooth timeline scrubbing
   - Clear waypoint indicators
   - Readable UI text at VR distances

2. **Add audio:**
   - Heartbeat sound synchronized with animation
   - UI click sounds
   - Atmospheric background audio

3. **Test on Quest 2:**
   - Deploy to device
   - Verify 72 FPS performance
   - Test network connection to backend
   - Practice demo flow

### Optional Enhancements

1. **Multiple ECG samples:**
   - Load different patient ECGs
   - Compare normal vs. abnormal hearts
   - Save/load user favorites

2. **Advanced animations:**
   - Blood flow visualization
   - Valve opening/closing
   - Heart muscle contraction

3. **Educational mode:**
   - Quiz system
   - Anatomy labels
   - Condition explanations

---

## Resources

### Backend Documentation
- [Backend/UNITY_QUICKSTART.md](../Backend/UNITY_QUICKSTART.md) - 15-minute integration guide
- [Backend/API_INTEGRATION_GUIDE.md](../Backend/API_INTEGRATION_GUIDE.md) - Complete API reference
- [Backend/ENHANCEMENT_STATUS.md](../Backend/ENHANCEMENT_STATUS.md) - Backend implementation details
- [dev/active/unity-integration-context.md](../dev/active/unity-integration-context.md) - Unity context

### Unity Documentation
- [XR Interaction Toolkit](https://docs.unity3d.com/Packages/com.unity.xr.interaction.toolkit@2.5/manual/index.html)
- [TextMeshPro](https://docs.unity3d.com/Packages/com.unity.textmeshpro@3.0/manual/index.html)
- [Particle System](https://docs.unity3d.com/Manual/class-ParticleSystem.html)

### Meshy.ai
- [Meshy.ai Website](https://www.meshy.ai/)
- [Text to 3D Tutorial](https://docs.meshy.ai/text-to-3d)
- [FBX Export Guide](https://docs.meshy.ai/export)

### Anatomical References
- [Heart Conduction System Diagram](https://www.google.com/search?q=heart+conduction+system+diagram&tbm=isch)
- [ECG Waveform Explanation](https://litfl.com/ecg-waveform/)
- [Cardiac Anatomy 3D](https://www.visiblebody.com/learn/heart)

---

## Support

**Stuck?** Check these resources:

1. **Backend API issues:** See [Backend/API_INTEGRATION_GUIDE.md](../Backend/API_INTEGRATION_GUIDE.md) Troubleshooting section
2. **Unity compile errors:** Verify all packages installed correctly
3. **VR headset issues:** Check Oculus Integration SDK setup
4. **Network issues:** See [dev/active/unity-integration-context.md](../dev/active/unity-integration-context.md) Network Configuration

---

**Last Updated:** 2025-11-15
**Project:** HoloHuman XR
**Hackathon:** Immerse the Bay 2025
**Backend Version:** 1.0.0 (All 3 Phases Complete)

**Ready to build! 🚀**
