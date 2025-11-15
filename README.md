# HoloHuman XR: Down the Rabbit Hole

**Immerse the Bay 2025 Hackathon Project**

Explore the human body layer-by-layer with AI-powered medical insights in virtual reality.

---

## 🎯 Project Overview

HoloHuman XR is an immersive medical visualization experience for Meta Quest 2 that allows users to:
- **Peel back anatomical layers** (skin → muscle → skeleton → heart)
- **Analyze ECG signals** using AI/ML (detects 6 cardiac conditions)
- **View medical imaging** (X-rays, CT scans) in 3D VR space
- **Feel haptic feedback** simulating heartbeat and injury sensations

**Theme:** "Down the Rabbit Hole" - Dive deeper into the hidden world inside the human body

**Competition Tracks:**
- 🏆 Primary: **Virtuous Reality** (Social Good + XR)
- 🤖 Secondary: **AI Horizons** (AI + XR)

---

## ✨ Features

### Interactive 3D Anatomy
- Life-sized human body models in VR
- Peelable layers: toggle visibility of skin, muscles, skeleton, and organs
- Grab, rotate, and scale models with VR controllers

### AI-Powered ECG Analysis
- Pre-trained neural network (TensorFlow/Keras)
- Detects 6 cardiac conditions:
  - 1st degree AV block
  - Right/Left Bundle Branch Block (RBBB/LBBB)
  - Sinus bradycardia/tachycardia
  - Atrial fibrillation
- Real-time predictions with confidence scores

### Medical Imaging Viewer
- View X-rays and CT scans in VR
- Navigate through image slices
- Zoom and pan controls
- Portal effect for "diving into" scan space

### Haptic Feedback
- Heartbeat pulse synchronized with heart rate (60-120 BPM)
- Fracture sensation when touching broken bones
- Quest controller vibration

---

## 🛠️ Tech Stack

**Frontend (VR)**
- Unity 2022.3 LTS
- Unity XR Interaction Toolkit
- OpenXR Plugin (Meta Quest 2)
- C# scripting
- TextMeshPro UI

**Backend (AI/ML)**
- Python 3.8+
- Flask REST API
- TensorFlow 2.2
- Keras
- Pre-trained ECG model ([antonior92/automatic-ecg-diagnosis](https://github.com/antonior92/automatic-ecg-diagnosis))

**Hardware**
- Meta Quest 2
- Quest Link (USB-C) for development

**Assets**
- 3D models from Sketchfab, TurboSquid (low-poly, VR-optimized)
- DICOM medical imaging samples (converted to PNG)

---

## 📁 Project Structure

```
Immerse-the-Bay-Hackathon/
├── README.md                           # This file
├── RESOURCES.md                        # All resource links and tools
├── Reference/                          # Hackathon rules and dev docs
├── dev/active/holohuman-xr/           # Development documentation
│   ├── holohuman-xr-plan.md           # Comprehensive dev plan
│   ├── holohuman-xr-context.md        # Technical context and architecture
│   └── holohuman-xr-tasks.md          # Task checklist (165+ tasks)
├── .claude/                            # Custom AI agents and commands
│   ├── agents/                        # Documentation, code review, research agents
│   ├── commands/                      # Dev workflow commands
│   └── hooks/                         # Automated skill activation
├── UnityProject/                       # Unity VR application (TBD)
└── Backend/                            # Flask API for ECG analysis (TBD)
```

---

## 🚀 Getting Started

### Prerequisites
- Unity 2022.3 LTS with Android Build Support
- Python 3.8+
- Meta Quest 2 with Developer Mode enabled
- USB-C cable for Quest Link

### Unity Setup

1. **Clone this repository:**
   ```bash
   git clone https://github.com/tyang4-ai/Immerse-the-Bay-Hackathon.git
   cd Immerse-the-Bay-Hackathon
   ```

2. **Clone Unity MR Example template:**
   ```bash
   cd UnityProject
   git clone https://github.com/Unity-Technologies/mr-example-meta-openxr .
   ```

3. **Open project in Unity Hub:**
   - Add project from `UnityProject` folder
   - Unity will import and configure packages

4. **Configure for Quest 2:**
   - File → Build Settings → Android
   - Edit → Project Settings → XR Plug-in Management
   - Enable OpenXR

5. **Connect Quest 2:**
   - Enable Developer Mode via Meta app
   - Connect via USB-C
   - Build and Run (or use Quest Link for faster iteration)

### Backend Setup

1. **Create Python virtual environment:**
   ```bash
   cd Backend
   python -m venv venv

   # Windows
   venv\Scripts\activate

   # Mac/Linux
   source venv/bin/activate
   ```

2. **Clone ECG model repository:**
   ```bash
   git clone https://github.com/antonior92/automatic-ecg-diagnosis
   cd automatic-ecg-diagnosis
   ```

3. **Install dependencies:**
   ```bash
   pip install tensorflow==2.2 keras numpy flask flask-cors
   ```

4. **Download pre-trained model weights:**
   - Visit: https://doi.org/10.5281/zenodo.3625017
   - Download `model.hdf5`
   - Place in `Backend/automatic-ecg-diagnosis/model/`

5. **Run Flask server:**
   ```bash
   cd Backend
   python ecg_api.py
   # Server runs on http://localhost:5000
   ```

---

## 📚 Documentation

- **[RESOURCES.md](RESOURCES.md)** - Complete list of resources, links, tutorials, and tools
- **[Dev Plan](dev/active/holohuman-xr/holohuman-xr-plan.md)** - 36-hour comprehensive development plan
- **[Context Doc](dev/active/holohuman-xr/holohuman-xr-context.md)** - Architecture, decisions, integration points
- **[Task Checklist](dev/active/holohuman-xr/holohuman-xr-tasks.md)** - Detailed task breakdown (165+ items)

---

## 👥 Team

- **Backend Lead** - Flask API, ML model integration
- **Backend Dev** - Asset preparation, Unity-Flask integration
- **Unity Lead** - VR interactions, layer system, scene polish
- **Unity Dev** - UI/UX, medical imaging, ECG visualization

---

## 🏆 Hackathon Details

**Event:** Immerse the Bay 2025
**Dates:** November 14-16, 2025 (36 hours)
**Deadline:** Sunday, Nov 16 at 9:00 AM (HARD STOP)
**Theme:** "Down the Rabbit Hole"

**Requirements:**
- ✅ XR must be used in non-trivial way
- ✅ 30-second demo video (vertical format)
- ✅ Public GitHub repository with MIT license
- ✅ Complete Devpost submission
- ✅ Max $20 spending on paid services

---

## 🎯 Roadmap

### MVP (Minimum Viable Product)
- [x] VR scene running on Quest 2
- [ ] Interactive heart model with peelable layers
- [ ] ECG visualization with AI analysis
- [ ] Basic medical imaging viewer
- [ ] Controller haptic feedback

### Stretch Goals
- [ ] Full skeleton model
- [ ] Hand tracking support
- [ ] Portal effect for scan space
- [ ] Multiple ECG analysis modes
- [ ] Voice commands

### Future Vision (Post-Hackathon)
- Real-time ECG from wearable devices
- Patient-specific anatomical models from DICOM segmentation
- Multi-user collaboration (doctors + patients)
- AI-powered automatic anomaly detection
- Integration with hospital PACS systems
- FDA-cleared medical device classification

---

## 🤝 Contributing

This project was created for the Immerse the Bay 2025 Hackathon. Contributions are welcome post-hackathon!

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Unity MR Example Template** - https://github.com/Unity-Technologies/mr-example-meta-openxr
- **ECG Model** - [antonior92/automatic-ecg-diagnosis](https://github.com/antonior92/automatic-ecg-diagnosis) (Nature Communications 2020)
- **3D Models** - Z-Anatomy (Sketchfab), TurboSquid, Free3D
- **Medical Data** - MIT-BIH Arrhythmia Database, Medimodel
- **Immerse the Bay** - Stanford hackathon organizers

---

## 📧 Contact

GitHub: [@tyang4-ai](https://github.com/tyang4-ai)
Project Link: [https://github.com/tyang4-ai/Immerse-the-Bay-Hackathon](https://github.com/tyang4-ai/Immerse-the-Bay-Hackathon)

---

**Built with ❤️ for Immerse the Bay 2025**

*"Step into the human body, peel back its layers, and explore real medical scans from the inside."*