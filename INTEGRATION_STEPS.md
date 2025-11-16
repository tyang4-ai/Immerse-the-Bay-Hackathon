# Integration Guide: ECG Heart System into Main Project

## What Was Done

I've integrated the working ECG heart visualization system from `teammate-integration` into your main project (`backup-branch/My project`). Your existing heart click interaction now triggers the full ECG analysis system instead of just showing/hiding a simple model.

---

## Files Copied

### Scripts (Core Heart System)
- `Assets/Scripts/ECGAPIClient.cs` - Backend API client
- `Assets/Scripts/API/ECGDataStructures.cs` - Data models matching backend API
- `Assets/Scripts/Heart/ECGHeartController.cs` - Main heart visualization orchestrator
- `Assets/Scripts/Heart/CardiacRegionMarker.cs` - Individual region visualization
- `Assets/Scripts/Heart/HeartRegionMapping.cs` - Maps 10 cardiac regions
- `Assets/Scripts/Heart/ElectricalWaveAnimator.cs` - Electrical wave animation

### ECG Sample Data
- `Assets/Resources/ECGSamples/*.json` - Sample ECG data files:
  - synthetic_ecg_normal.json
  - synthetic_ecg_bradycardia.json
  - synthetic_ecg_tachycardia.json
  - sample_normal.json
  - sample_af.json
  - sample_rbbb.json

### Modified Script
- `Assets/Script/BodyToggleInteraction.cs` - **UPDATED** to support ECG system

---

## Unity Editor Setup (REQUIRED STEPS)

### Step 1: Install Required Package

**CRITICAL:** You must install the Newtonsoft.Json package before the scripts will compile.

1. Open your project in Unity Editor
2. Go to **Window → Package Manager**
3. Click the **+** button (top-left)
4. Select **Add package by name...**
5. Enter: `com.unity.nuget.newtonsoft-json`
6. Click **Add**
7. Wait for Unity to import the package

---

### Step 2: Create ECG Heart System GameObject

You need to create a GameObject that contains the ECG heart visualization system:

1. In your scene hierarchy, **Right-click → Create Empty**
2. Name it **"ECG Heart System"**
3. Add the **ECGHeartController** component:
   - Select "ECG Heart System" GameObject
   - In Inspector, click **Add Component**
   - Type "ECGHeartController" and select it

---

### Step 3: Create 10 Cardiac Region Markers

The heart visualization uses 10 separate region markers. You need to create these:

#### 3a. Create Region Markers Parent

1. Right-click "ECG Heart System" → **Create Empty**
2. Name it **"Heart Regions"**

#### 3b. Create Each of the 10 Regions

For each region, do the following:

1. Right-click "Heart Regions" → **3D Object → Sphere** (or use a custom marker model)
2. Name it exactly as shown below (case-sensitive!)
3. Scale it to 0.1, 0.1, 0.1 (small marker)
4. Add the **CardiacRegionMarker** component
5. In CardiacRegionMarker Inspector, set **Region Name** to match the GameObject name

**Required Region Names (EXACT spelling required):**
- `sa_node` - Sinoatrial node
- `ra` - Right atrium
- `la` - Left atrium
- `av_node` - Atrioventricular node
- `bundle_his` - Bundle of His
- `rbbb` - Right bundle branch
- `lbbb` - Left bundle branch
- `purkinje` - Purkinje fibers
- `rv` - Right ventricle
- `lv` - Left ventricle

#### 3c. Position the Regions

Position each sphere to represent the actual heart anatomy. Example positions (adjust as needed):

```
sa_node:     (0, 1.5, 0.3)    # Top-right of heart
ra:          (0.3, 1.2, 0.2)  # Right atrium
la:          (-0.3, 1.2, 0.2) # Left atrium
av_node:     (0, 0.8, 0)      # Center between atria/ventricles
bundle_his:  (0, 0.6, 0)      # Below AV node
rbbb:        (0.3, 0.3, 0)    # Right bundle
lbbb:        (-0.3, 0.3, 0)   # Left bundle
purkinje:    (0, 0, 0)        # Base of ventricles
rv:          (0.3, 0.1, 0.1)  # Right ventricle
lv:          (-0.3, 0.1, 0.1) # Left ventricle
```

---

### Step 4: Create HeartRegionMapping Component

1. Select the "ECG Heart System" GameObject
2. Click **Add Component**
3. Type "HeartRegionMapping" and add it
4. In the Inspector, you'll see **Regions (Size: 0)**
5. Set size to **10**
6. Drag each of the 10 region GameObjects into the array slots:
   - Element 0: sa_node
   - Element 1: ra
   - Element 2: la
   - ... (all 10 regions)

---

### Step 5: Configure ECGHeartController

Select "ECG Heart System" and configure the **ECGHeartController** component:

#### API Client
1. Drag the **ECG Heart System** GameObject into the **Api Client** field (it will find the ECGAPIClient singleton)

#### ECG Data
1. In the **Ecg Data File** field:
   - Click the circle icon
   - Navigate to **Assets/Resources/ECGSamples/**
   - Select **synthetic_ecg_normal** (or any sample file)

#### Heart Visualization
1. Drag the **"Heart Regions"** GameObject (the parent) into **Region Mapping**
2. **Wave Animator:** Leave empty for now (optional feature)

#### UI Elements (Optional - for displaying diagnosis)
If you want to display diagnosis text:
1. Create a **TextMeshPro - Text (UI)** canvas text element
2. Drag it into the **Diagnosis Text**, **Heart Rate Text**, **Status Text** fields

---

### Step 6: Connect BodyToggleInteraction to ECG System

Find the GameObject that has your **BodyToggleInteraction** script:

1. Select it in the hierarchy
2. In the Inspector, find the **BodyToggleInteraction** component
3. You'll see new fields:
   - **Ecg Heart Controller:** Drag the "ECG Heart System" GameObject here
   - **Use ECG System:** Check this box to enable (or uncheck to use old toggle behavior)

---

### Step 7: Start the Backend Server

The ECG analysis requires a Flask backend server to be running:

1. Open a terminal/command prompt
2. Navigate to the backend folder:
   ```bash
   cd "C:/Users/22317/Immerse-the-Bay-Project/teammate-integration/Backend"
   ```
3. Install Python dependencies (first time only):
   ```bash
   pip install flask flask-cors numpy scipy
   ```
4. Start the server:
   ```bash
   python ecg_api.py
   ```
5. You should see: `Running on http://127.0.0.1:5000`

#### Configure API URL in Unity

1. Select "ECG Heart System" GameObject
2. Find the **ECGAPIClient** component (it's a singleton, might be on the same object)
3. Set **Base URL** to:
   - `http://localhost:5000` (for PC testing)
   - `http://YOUR_PC_IP:5000` (for Quest 2 deployment)

---

## How It Works Now

### Before (Old Behavior)
1. User clicks heart
2. Simple 3D heart model appears/disappears

### After (New Behavior)
1. User clicks heart
2. **BodyToggleInteraction** detects click
3. Calls **ECGHeartController.AnalyzeAndVisualize()**
4. System loads ECG data from JSON file
5. Sends ECG data to Flask backend for analysis
6. Backend returns:
   - Diagnosis (e.g., "Right Bundle Branch Block")
   - Heart rate (e.g., 72 BPM)
   - Region health data (severity + color for each of 10 regions)
   - Activation sequence (timing for electrical animation)
7. **HeartRegionMapping** updates all 10 cardiac region markers:
   - Changes glow color (green = healthy, yellow/orange/red = abnormal)
   - Changes light intensity based on severity
   - Triggers particle effects
8. **ElectricalWaveAnimator** (if configured) animates electrical signal propagation
9. Diagnosis/heart rate displayed in UI text (if configured)

---

## Testing the Integration

### Test 1: Verify Scripts Compile
1. Open your project in Unity
2. Check the Console for errors
3. If you see errors about "Newtonsoft.Json", make sure you installed the package (Step 1)

### Test 2: Verify Backend Connection
1. Start the Flask backend server
2. In Unity, click the heart
3. Check Unity Console for logs:
   - `[ECGHeartController] Loading ECG data...`
   - `[ECGAPIClient] Sending request to: http://localhost:5000/api/ecg/analyze`
   - `[ECGHeartController] Analysis complete`

### Test 3: Verify Region Visualization
1. After clicking the heart, watch the 10 region spheres
2. They should:
   - Change color (based on health)
   - Glow with varying intensity
   - Show particle effects (if configured)

### Test 4: Try Different ECG Samples
1. Select "ECG Heart System"
2. Change **Ecg Data File** to different samples:
   - `synthetic_ecg_bradycardia` - Should show slow heart rate
   - `sample_rbbb` - Should highlight right bundle branch in red
   - `sample_af` - Should show atrial fibrillation pattern

---

## Troubleshooting

### Error: "The type or namespace name 'Newtonsoft' could not be found"
**Solution:** Install Newtonsoft.Json package (see Step 1)

### Error: "ECGHeartController is not assigned"
**Solution:** Drag the ECG Heart System GameObject into the BodyToggleInteraction's ECG Heart Controller field (Step 6)

### Error: "Connection refused" or "Failed to connect to backend"
**Solution:**
1. Make sure Flask backend is running (`python ecg_api.py`)
2. Check that Base URL is set to `http://localhost:5000`
3. Check Windows Firewall isn't blocking port 5000

### Error: "Region [name] not found in mapping"
**Solution:** Make sure all 10 regions are created with EXACT names (case-sensitive)

### Regions don't change color
**Solution:**
1. Check Console for errors
2. Verify backend is returning data (check Flask terminal for request logs)
3. Make sure each region has CardiacRegionMarker component with correct Region Name

### Nothing happens when clicking heart
**Solution:**
1. Check that "Use ECG System" is checked in BodyToggleInteraction
2. Verify ECG Heart Controller field is assigned
3. Check Console for errors

---

## Optional Enhancements

### Add UI Panels
Create TextMeshPro UI elements to display:
- Diagnosis text (e.g., "Normal Sinus Rhythm")
- Heart rate (e.g., "72 BPM")
- Clinical interpretation

### Add Electrical Wave Animation
1. Create an empty GameObject under "ECG Heart System"
2. Name it "Wave Animator"
3. Add **ElectricalWaveAnimator** component
4. Drag it into ECGHeartController's **Wave Animator** field

### Add 3D Heart Model
Instead of simple spheres, import a 3D heart model from the teammate-integration folder and position the region markers on the actual heart anatomy.

### Add Timeline UI
Copy the Timeline system from teammate-integration to scrub through individual heartbeats.

### Add Storytelling Journey Mode
Copy the Journey scripts to enable narrative exploration of cardiac regions.

---

## File Structure After Integration

```
backup-branch/My project/
├── Assets/
│   ├── Script/
│   │   └── BodyToggleInteraction.cs          [MODIFIED]
│   ├── Scripts/
│   │   ├── ECGAPIClient.cs                   [NEW]
│   │   ├── API/
│   │   │   └── ECGDataStructures.cs          [NEW]
│   │   └── Heart/
│   │       ├── ECGHeartController.cs         [NEW]
│   │       ├── CardiacRegionMarker.cs        [NEW]
│   │       ├── HeartRegionMapping.cs         [NEW]
│   │       └── ElectricalWaveAnimator.cs     [NEW]
│   └── Resources/
│       └── ECGSamples/                       [NEW]
│           ├── synthetic_ecg_normal.json
│           ├── synthetic_ecg_bradycardia.json
│           ├── synthetic_ecg_tachycardia.json
│           └── ... (other samples)
└── INTEGRATION_STEPS.md                      [THIS FILE]
```

---

## Next Steps

1. Follow the Unity Editor setup steps above (Steps 1-7)
2. Test with the Flask backend running
3. Click the heart to see the ECG analysis in action
4. Experiment with different ECG sample files
5. Optionally add UI panels, timeline, or journey mode

---

## Reference Documentation

For more detailed information, see:
- [teammate-integration/Unity/HEART_DEMO_SETUP_GUIDE.md](../../teammate-integration/Unity/HEART_DEMO_SETUP_GUIDE.md) - Complete setup guide
- [teammate-integration/FOR_TEAMMATE/INTEGRATION-GUIDE.md](../../teammate-integration/FOR_TEAMMATE/INTEGRATION-GUIDE.md) - Quick integration reference

---

## Support

If you encounter issues:
1. Check the Unity Console for error messages
2. Check the Flask backend terminal for request logs
3. Verify all GameObject assignments in Inspector
4. Ensure backend server is running on port 5000
5. Test with sample ECG data first before using custom data
