# HoloHuman XR - Resource Links

**Quick access to all tools, assets, and documentation**

---

## Unity & VR Development

### Templates & Setup
- **Unity MR Example (Quest 2):** https://github.com/Unity-Technologies/mr-example-meta-openxr
- **Meta Quest Setup Guide:** https://developers.meta.com/horizon/documentation/unity/unity-project-setup/
- **Unity Sentis (ML inference):** https://docs.unity3d.com/Packages/com.unity.sentis@2.1/manual/index.html

### Learning Resources
- **Unity XR Toolkit Docs:** https://docs.unity3d.com/Packages/com.unity.xr.interaction.toolkit@2.5/manual/index.html
- **Quest Developer Center:** https://developer.oculus.com/

---

## 3D Models (Free)

### Anatomy Models
- **Z-Anatomy (Skeleton/Organs):** https://sketchfab.com/Z-Anatomy
  - License: CC BY-SA
  - Quality: High poly (needs decimation)

- **TurboSquid (Heart - Low Poly):** https://www.turbosquid.com/Search/3D-Models/free/low-poly/human-heart
  - License: Royalty-free
  - Quest-ready options available

- **Free3D (Heart Models):** https://free3d.com/3d-models/lowpoly-heart
  - 29 free models
  - Various formats

- **CGTrader (VR/AR Models):** https://www.cgtrader.com/3d-models/character/anatomy/3d-human-heart-model-vr-ar-low-poly
  - Optimized for VR/AR
  - Check pricing

### Optimization Tools
- **Blender (Free):** https://www.blender.org/
  - Use Decimate modifier to reduce polygon count
  - Target: <50k triangles for Quest 2

---

## ECG & Medical AI

### Pre-trained Models
- **Automatic ECG Diagnosis:** https://github.com/antonior92/automatic-ecg-diagnosis
  - Pre-trained weights: https://doi.org/10.5281/zenodo.3625017
  - Paper: Nature Communications 2020
  - 6 cardiac conditions detected

- **ECG Heartbeat Classification:** https://github.com/CVxTz/ECG_Heartbeat_Classification
  - Keras/TensorFlow
  - MIT-BIH dataset compatible

### ECG Datasets (Free)
- **MIT-BIH Arrhythmia Database:** https://physionet.org/content/mitdb/
  - 48 half-hour recordings
  - 110,000+ annotated beats
  - License: Open Data Commons Attribution
  - Size: 104.3 MB

### Python Libraries
```bash
pip install biosppy wfdb neurokit2 tensorflow keras numpy flask flask-cors
```

- **BioSPPy:** Biosignal processing
- **WFDB:** PhysioNet data reader
- **NeuroKit2:** ECG simulation & processing

---

## Medical Imaging (DICOM)

### Free DICOM Samples
- **Medimodel:** https://medimodel.com/sample-dicom-files/
  - CT, MRI, X-ray samples
  - Anonymized datasets

- **RuboMedical:** https://www.rubomedical.com/dicom_files/
  - Direct download links
  - Various modalities

- **3DICOM Viewer Library:** https://3dicomviewer.com/dicom-library/
  - NIfTi and DICOM formats
  - Research/education use

- **OsiriX Library:** https://www.osirix-viewer.com/resources/dicom-image-library/
  - Click thumbnails to download
  - JPEG2000 compressed

### DICOM Converters

**Online (Free):**
- **Dicom2PNG:** https://www.dicom2png.com/
- **OnlineConverter:** https://www.onlineconverter.com/dicom-to-png
- **GroupDocs:** https://products.groupdocs.app/conversion/dicom-to-png

**Desktop Software (Free):**
- **Weasis:** https://weasis.org/en/ (Cross-platform)
- **MicroDicom:** https://www.microdicom.com/ (Windows)
- **Horos:** https://horosproject.org/ (Mac only)
- **3D Slicer:** https://www.slicer.org/ (Advanced 3D visualization)

### Python DICOM Processing
```python
pip install pydicom pillow
```
```python
import pydicom
from PIL import Image

ds = pydicom.dcmread('sample.dcm')
img = Image.fromarray(ds.pixel_array)
img.save('output.png')
```

---

## Backend Development

### Flask + Unity Integration
- **Tutorial:** https://syedakbar.co/connecting-unity-with-a-database-using-python-flask-rest-webservice/
- **Flask REST API:** https://pythonbasics.org/flask-rest-api/
- **Flask-CORS:** https://flask-cors.readthedocs.io/

### API Testing Tools
- **Postman:** https://www.postman.com/downloads/
- **Thunder Client:** VS Code extension
- **curl:** Built into Windows/Mac/Linux

---

## Git & Version Control

### GitHub Setup
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/yourusername/HoloHuman-XR.git
git push -u origin main
```

### MIT License Template
```text
MIT License

Copyright (c) 2025 [Your Team Name]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## DevPost Submission

### Requirements Checklist
- [ ] Project title and tagline
- [ ] Detailed description (500+ words)
- [ ] Demo video (30 seconds, vertical format)
- [ ] GitHub repository link (public, MIT license)
- [ ] Built with technologies list
- [ ] Challenges faced section
- [ ] What we learned section
- [ ] What's next for the project

### Video Recording Tools
- **OBS Studio:** https://obsproject.com/ (Free, desktop recording)
- **Meta Quest Screen Recording:** Built-in (Share button)
- **Video Editing:** DaVinci Resolve (free), CapCut, iMovie

---

## Hackathon-Specific

### Event Info
- **Dates:** Nov 14-16, 2025
- **Pencils Down:** Sunday 9:00 AM (HARD DEADLINE)
- **Judging:** Sunday 12:00 PM
- **Closing Ceremony:** Sunday 1:00 PM

### Competition Tracks
1. **Creative Zenith** - Best Creative XR
2. **Virtuous Reality** - Social Good + XR ← **PRIMARY TARGET**
3. **AI Horizons** - AI + XR ← **SECONDARY**
4. **Game Changer** - Gaming in XR
5. **Wild West** - Unconventional/experimental

### Prize
- Up to 4 Meta Quest 2 headsets per winning team

---

## Performance Optimization

### Quest 2 Specifications
- **CPU:** Qualcomm Snapdragon XR2
- **GPU:** Adreno 650
- **RAM:** 6 GB
- **Display:** 1832 × 1920 per eye
- **Refresh Rate:** 72 Hz (90 Hz experimental)
- **Target FPS:** 72 FPS minimum

### Optimization Guidelines
- **Total Scene Polygons:** <1M triangles
- **Individual Models:** <50k triangons
- **Texture Resolution:** 2048×2048 max (prefer 1024×1024)
- **Draw Calls:** <100 per frame
- **Lighting:** Use baked lighting where possible
- **Shadows:** Disable or use low-quality settings

### Unity Optimization Tools
- **Profiler:** Window → Analysis → Profiler
- **Frame Debugger:** Window → Analysis → Frame Debugger
- **Oculus Performance Metrics:** OVR Performance HUD

---

## Communication & Support

### Team Collaboration Tools
- **Discord:** Real-time chat
- **GitHub Projects:** Task tracking
- **Google Docs:** Shared documentation
- **Trello/Notion:** Project management

### Debugging Resources
- **Unity Forums:** https://forum.unity.com/
- **Stack Overflow:** https://stackoverflow.com/questions/tagged/unity3d
- **Reddit:** r/Unity3D, r/oculus, r/virtualreality

---

## Emergency Backup Plans

### If Behind Schedule
1. **Simplify to heart-only demo** (skip skeleton)
2. **Use fake ECG predictions** (skip ML integration)
3. **Pre-rendered images** (skip real-time DICOM)
4. **Controller haptics only** (skip Afference)

### If Technical Issues
1. **Unity won't build:** Use Quest Link for demo
2. **ML model fails:** Hardcoded predictions
3. **Models too heavy:** Use Unity primitives
4. **No internet:** Have offline backups of all assets

---

## Quick Command Reference

### Python Environment
```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate

# Install requirements
pip install -r requirements.txt

# Run Flask server
python ecg_api.py
```

### Unity Build
```bash
# Build settings shortcut: Ctrl+Shift+B (Windows) / Cmd+Shift+B (Mac)
# Platform: Android
# Texture Compression: ASTC
# Build and Run (with Quest connected)
```

### Git Commands
```bash
# Check status
git status

# Add all changes
git add .

# Commit with message
git commit -m "Add feature X"

# Push to GitHub
git push origin main

# Pull latest changes
git pull origin main
```

---

**Bookmark this page for quick access to all resources!** 🔖