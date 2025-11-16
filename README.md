# Immerse-the-Bay VR Heart Visualization System

![Unity](https://img.shields.io/badge/Unity-2022.3%20LTS-blue)
![Meta Quest 2](https://img.shields.io/badge/Meta%20Quest%202-VR-green)
![Python](https://img.shields.io/badge/Python-3.8+-yellow)

An immersive VR experience for visualizing real-time ECG (electrocardiogram) analysis with 3D cardiac region mapping. Built for Meta Quest 2 using Unity and powered by a Flask backend with machine learning-based ECG analysis.

---

## 🎯 Overview

This project provides an educational VR experience that:
- **Analyzes 12-lead ECG data** using machine learning models
- **Visualizes cardiac health** across 10 anatomical heart regions
- **Color-codes regions** based on severity (green = healthy, red = critical)
- **Animates electrical signal propagation** through the heart
- **Provides real-time diagnosis** (Normal Sinus Rhythm, RBBB, LBBB, Atrial Fibrillation, etc.)

Built for the **Immerse-the-Bay Hackathon** to make cardiac education more interactive and accessible.

---

## ✨ Features

### VR Interaction
- ✅ Click on heart to trigger ECG analysis
- ✅ 10 cardiac regions with dynamic color-coded glowing
- ✅ Real-time backend communication
- ✅ Support for Quest Link/Air Link streaming
- ✅ VR controller interaction using XR Interaction Toolkit

### ECG Analysis
- ✅ 12-lead ECG signal processing (4096 samples per lead)
- ✅ ML-based diagnosis classification
- ✅ Heart rate detection with R-peak analysis
- ✅ Regional health mapping (SA node, AV node, Bundle branches, Ventricles, etc.)
- ✅ Activation sequence timing for electrical wave animation

### Visual Effects
- ✅ Point lights with color-coded severity
- ✅ Emissive materials for glowing regions
- ✅ Particle system effects (optional)
- ✅ Electrical wave animation (optional)
- ✅ Pulsing glow effects

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Unity VR Frontend                     │
│  ┌────────────────┐  ┌──────────────────────────────┐  │
│  │  VR Interaction │  │  ECG Heart Controller        │  │
│  │  (Click Heart) │──│  - Load ECG Data             │  │
│  └────────────────┘  │  - Call Backend API          │  │
│                      │  - Update Visualizations     │  │
│  ┌────────────────┐  └──────────────────────────────┘  │
│  │ 10 Cardiac     │                ▲                    │
│  │ Region Markers │◄───────────────┘                    │
│  │ (Glowing)      │                                     │
│  └────────────────┘                                     │
└─────────────────────────────────────────────────────────┘
                           │
                           │ HTTP POST /api/ecg/analyze
                           │ (4096×12 ECG samples)
                           ▼
┌─────────────────────────────────────────────────────────┐
│              Flask Backend (Python)                      │
│  ┌────────────────────────────────────────────────────┐ │
│  │  ECG Analysis Engine                               │ │
│  │  - Signal processing (bandpass filter)            │ │
│  │  - R-peak detection (Pan-Tompkins)                │ │
│  │  - Heart rate calculation                         │ │
│  │  - ML diagnosis classification                    │ │
│  │  - Region health mapping                          │ │
│  └────────────────────────────────────────────────────┘ │
│                           │                              │
│                           │ JSON Response                │
│                           ▼                              │
│  ┌────────────────────────────────────────────────────┐ │
│  │  Response: {                                       │ │
│  │    "diagnosis": "RBBB",                            │ │
│  │    "heart_rate": 72.3,                             │ │
│  │    "region_health": {                              │ │
│  │      "rbbb": {severity: 0.89, color: [1,0,0]},    │ │
│  │      "sa_node": {severity: 0.0, color: [0,1,0]}   │ │
│  │    },                                              │ │
│  │    "activation_sequence": [...]                    │ │
│  │  }                                                 │ │
│  └────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites
- **Unity 2022.3 LTS** with Android Build Support
- **Python 3.8+** with pip
- **Meta Quest 2** with Developer Mode enabled
- **USB-C cable** or **stable WiFi** for Quest Link

### 1. Clone the Repository

```bash
git clone https://github.com/tyang4-ai/Immerse-the-Bay-Hackathon.git
cd Immerse-the-Bay-Hackathon
```

### 2. Install Unity Dependencies

1. Open the project in Unity 2022.3 LTS
2. Install required packages via Package Manager:
   ```
   - com.unity.nuget.newtonsoft-json
   - com.unity.xr.management
   - com.unity.xr.interaction.toolkit
   - TextMeshPro (if not already installed)
   ```

### 3. Install Python Backend Dependencies

```bash
cd Backend
pip install flask flask-cors numpy scipy
```

### 4. Start Flask Backend

```bash
python ecg_api.py
```

Expected output:
```
* Running on http://127.0.0.1:5000
* Running on http://0.0.0.0:5000
```

### 5. Run in Unity

1. Open Unity Editor
2. Load scene: `Assets/Scenes/BasicScene.unity`
3. Press **Play**
4. With Quest Link active, the scene will appear in VR
5. Click on the heart to trigger ECG analysis

---

## 📁 Project Structure

```
My project/
├── Assets/
│   ├── Scenes/
│   │   ├── BasicScene.unity           # Main VR scene
│   │   └── SampleScene.unity          # Alternative scene
│   ├── Scripts/
│   │   ├── ECGAPIClient.cs            # Backend API communication
│   │   ├── API/
│   │   │   └── ECGDataStructures.cs   # Data models
│   │   ├── Heart/
│   │   │   ├── ECGHeartController.cs      # Main orchestrator
│   │   │   ├── CardiacRegionMarker.cs     # Region visualization
│   │   │   ├── HeartRegionMapping.cs      # Region registry
│   │   │   ├── ElectricalWaveAnimator.cs  # Animation
│   │   │   └── RegionLightSetup.cs        # Setup helper
│   │   └── Script/
│   │       └── BodyToggleInteraction.cs   # VR click handler
│   ├── Resources/
│   │   └── ECGSamples/                # Sample ECG data files
│   │       ├── synthetic_ecg_normal.json
│   │       ├── synthetic_ecg_bradycardia.json
│   │       ├── synthetic_ecg_tachycardia.json
│   │       ├── sample_rbbb.json
│   │       └── sample_af.json
│   └── VRTemplateAssets/              # VR template assets
├── Backend/
│   ├── ecg_api.py                     # Flask REST API
│   ├── heart_region_mapper.py         # Region health mapping
│   └── ecg_heartrate_analyzer.py      # Signal processing
├── INTEGRATION_STEPS.md               # Unity setup guide
├── QUEST2_DEPLOYMENT.md               # Quest 2 deployment guide
└── README.md                          # This file
```

---

## 🎮 Usage Guide

### In VR (Quest Link):

1. **Start Flask Backend:**
   ```bash
   python Backend/ecg_api.py
   ```

2. **Launch Unity Editor** and press Play

3. **Put on Quest 2 headset** (Quest Link must be active)

4. **Point VR controller** at the heart

5. **Click trigger** to analyze ECG

6. **Observe results:**
   - 10 cardiac regions glow with health colors
   - Green = healthy
   - Yellow = mild abnormality
   - Orange = moderate issue
   - Red = critical severity

### Test Different ECG Conditions:

Change the ECG data file in Unity Inspector:
- **Normal Sinus Rhythm:** `synthetic_ecg_normal`
- **Bradycardia (slow):** `synthetic_ecg_bradycardia`
- **Tachycardia (fast):** `synthetic_ecg_tachycardia`
- **Right Bundle Branch Block:** `sample_rbbb`
- **Atrial Fibrillation:** `sample_af`

---

## 🧠 Supported ECG Diagnoses

The system can identify:
- ✅ **Normal Sinus Rhythm (NSR)** - Healthy heart
- ✅ **Sinus Bradycardia** - Slow heart rate (<60 BPM)
- ✅ **Sinus Tachycardia** - Fast heart rate (>100 BPM)
- ✅ **Right Bundle Branch Block (RBBB)** - Right conduction delay
- ✅ **Left Bundle Branch Block (LBBB)** - Left conduction delay
- ✅ **Atrial Fibrillation (AF)** - Irregular rhythm
- ✅ **1st Degree AV Block** - Delayed AV conduction

---

## 🔧 Configuration

### Unity Settings

**ECGAPIClient Component:**
- Backend URL: `http://localhost:5000` (for Quest Link)
- Backend URL: `http://YOUR_PC_IP:5000` (for standalone Quest 2)
- Timeout: 30 seconds
- Log Requests: Enabled

**ECGHeartController Component:**
- ECG Data File: Select from `Resources/ECGSamples/`
- Output Mode: `clinical_expert` or `storytelling`
- Auto Analyze On Start: Enabled/Disabled

**CardiacRegionMarker (each of 10 regions):**
- Region Name: `sa_node`, `ra`, `la`, `av_node`, `bundle_his`, `rbbb`, `lbbb`, `purkinje`, `rv`, `lv`
- Max Light Intensity: 3.0
- Pulse Speed: 2.0

### Backend Settings

**Flask Configuration (ecg_api.py):**
```python
app.run(host='0.0.0.0', port=5000, debug=True)
```

**Region Health Mapping:**
- Configurable severity thresholds
- Color gradient mapping (green → yellow → orange → red)
- Activation delay timings per condition

---

## 🎨 10 Cardiac Regions

The system visualizes these anatomical regions:

1. **SA Node** - Sinoatrial node (natural pacemaker)
2. **RA** - Right atrium
3. **LA** - Left atrium
4. **AV Node** - Atrioventricular node
5. **Bundle of His** - Electrical conduction bundle
6. **RBBB** - Right bundle branch
7. **LBBB** - Left bundle branch
8. **Purkinje Fibers** - Ventricular conduction network
9. **RV** - Right ventricle
10. **LV** - Left ventricle

Each region updates color and intensity based on ECG analysis results.

---

## 📊 Technical Details

### ECG Data Format

Input: 12-lead ECG with 4096 samples per lead
```json
{
  "ecg_signal": [
    [sample1_lead1, sample1_lead2, ..., sample1_lead12],
    [sample2_lead1, sample2_lead2, ..., sample2_lead12],
    ...
    [sample4096_lead1, sample4096_lead2, ..., sample4096_lead12]
  ]
}
```

### API Response Format

```json
{
  "diagnosis": {
    "top_condition": "RBBB",
    "confidence": 0.89
  },
  "heart_rate": {
    "bpm": 72.3,
    "lead_used": "II",
    "lead_quality": 0.95
  },
  "region_health": {
    "rbbb": {
      "severity": 0.89,
      "color": [1.0, 0.0, 0.0],
      "activation_delay_ms": 320
    },
    "sa_node": {
      "severity": 0.0,
      "color": [0.0, 1.0, 0.0],
      "activation_delay_ms": 0
    }
  },
  "activation_sequence": [
    ["sa_node", 0],
    ["ra", 25],
    ["la", 30],
    ...
  ],
  "processing_time_ms": 267.4
}
```

---

## 🔍 Troubleshooting

### VR Not Working in Unity

**Issue:** Quest 2 connected but scene doesn't appear in headset

**Solution:**
1. Enable XR Plugin Management: `Edit → Project Settings → XR Plug-in Management`
2. Check **Oculus** or **OpenXR** for PC platform
3. Ensure Quest Link is active in headset

### Backend Connection Errors

**Issue:** `Connection refused` or timeout

**Solution:**
1. Verify Flask backend is running: `python ecg_api.py`
2. Check Backend URL in Unity matches: `http://localhost:5000`
3. Check Windows Firewall (for Quest 2 network mode)

### Regions Not Glowing

**Issue:** Cardiac regions stay white or don't change color

**Solution:**
1. Verify Light components are added to each region
2. Check ECG data file is assigned in ECGHeartController
3. Review Console logs for parsing errors
4. Ensure backend is returning valid data

---

## 📚 Documentation

- **[INTEGRATION_STEPS.md](INTEGRATION_STEPS.md)** - Complete Unity setup guide
- **[QUEST2_DEPLOYMENT.md](QUEST2_DEPLOYMENT.md)** - Quest 2 deployment instructions
- **[Backend API Documentation](Backend/README.md)** - API endpoints and usage

---

## 🛠️ Development

### Adding New ECG Samples

1. Place JSON file in `Assets/Resources/ECGSamples/`
2. Format: `{"ecg_signal": [[4096 samples], [12 leads]]}`
3. Select in Unity Inspector → ECGHeartController → ECG Data File

### Customizing Region Colors

Edit `Backend/heart_region_mapper.py`:
```python
def severity_to_color(severity):
    # Customize color gradient here
    if severity < 0.25:
        return lerp(green, yellow, severity / 0.25)
    ...
```

### Adjusting Performance

For better Quest 2 performance:
1. Reduce light range: `Inspector → Light → Range = 1-2`
2. Disable shadows: `Edit → Project Settings → Quality → Shadows = Off`
3. Lower texture quality
4. Disable particle effects

---

## 🤝 Contributing

This project was built for the **Immerse-the-Bay Hackathon**. Contributions welcome!

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## 📝 License

MIT License - See LICENSE file for details

---

## 👥 Team

Built by the Immerse-the-Bay team for cardiac education in VR.

---

## 🙏 Acknowledgments

- **Meta Quest 2** for VR platform
- **Unity XR Interaction Toolkit** for VR interactions
- **Flask** for backend framework
- **PTB-XL Dataset** for ECG training data
- **Immerse-the-Bay Hackathon** organizers

---

## 📧 Contact

For questions or issues, please open a GitHub issue.

---

**Built with ❤️ for better cardiac education**

🤖 Generated with [Claude Code](https://claude.com/claude-code)
