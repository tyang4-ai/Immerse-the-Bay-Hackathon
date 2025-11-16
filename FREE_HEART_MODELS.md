# Free 3D Heart Models for HoloHuman XR Demo
**Alternative to Meshy.ai - Open Source Models**

Since Meshy.ai is having issues, here are the **best free 3D heart models** for your hackathon demo.

---

## 🏆 TOP RECOMMENDATIONS (Best for Your Demo)

### 1. **Realistic Human Heart by neshallads** ⭐ BEST CHOICE
**Platform:** Sketchfab
**Link:** https://sketchfab.com/3d-models/realistic-human-heart-3f8072336ce94d18b3d0d055a1ece089

**Why This One:**
- ✅ High quality, anatomically accurate
- ✅ Ready for AR/VR and educational use
- ✅ Free download (Creative Commons)
- ✅ Includes chambers (atria, ventricles)
- ✅ Works perfectly with Unity

**Download:**
1. Click "Download 3D Model" button
2. Select FBX or GLB format (both work in Unity)
3. Import to Unity: Assets/Models/Heart/

---

### 2. **Cardiac Anatomy Series by HannahNewey** ⭐ PERFECT FOR YOUR PROJECT
**Platform:** Sketchfab
**Links:**
- External view: https://sketchfab.com/3d-models/cardiac-anatomy-external-view-of-human-heart-a3f0ea2030214a6bbaa97e7357eebd58
- Cardiac veins: https://sketchfab.com/3d-models/cardiac-anatomy-cardiac-veins-of-the-heart-faa6c5b169ec4928bda1f6bf36e0fcb6
- Coronary arteries: https://sketchfab.com/3d-models/cardiac-anatomy-coronary-arteries-of-the-heart-00b5f4ec0b984325b453f8df07cd0cb5

**Why These:**
- ✅ Made by medical professional
- ✅ Separate anatomical components
- ✅ Can combine to show different systems
- ✅ Educational quality
- ✅ Free CC license

**Strategy:**
Download all 3 and combine them in Unity to show:
- Heart structure (external)
- Electrical conduction pathways (veins/arteries map to your regions)
- Multiple visualization layers

---

### 3. **Human Heart Internal Structure by Haiqa Arif** ⭐ SHOWS CHAMBERS
**Platform:** Sketchfab
**Link:** https://sketchfab.com/3d-models/human-heart-internal-structure-3d-model-21d346f72230432e8ed5fe448b03cca5

**Why This One:**
- ✅ Shows internal chambers clearly
- ✅ Perfect for "peeling layers" visualization
- ✅ Educational detail level
- ✅ Free download

**Use Case:** Great for showing atria vs ventricles separation

---

### 4. **Internal Heart Anatomy by VisibleHeartLabs** (Medical Grade!)
**Platform:** Sketchfab
**Link:** https://sketchfab.com/3d-models/internal-heart-anatomy-heart0612-fb9b10956eb64fbab6c9606179e946a3

**Why This One:**
- ✅ Based on real donated heart
- ✅ Medical research quality
- ✅ Shows actual cardiac anatomy
- ✅ Very impressive for judges

**Note:** From University of Minnesota's Visible Heart Lab - legitimate medical data!

---

## 🎯 RECOMMENDED STRATEGY FOR DEMO

Since you need 10 cardiac regions but can't generate separate models, here's the **smart approach:**

### Plan A: Use 1 Complete Model + Unity Primitives (FASTEST - 30 min)

1. **Download:** "Realistic Human Heart" (recommendation #1)
2. **In Unity:**
   - Import the complete heart model
   - Create 10 empty GameObjects positioned at cardiac regions:
     - SA Node → Small sphere at top right
     - AV Node → Small sphere at center
     - Bundle of His → Line renderer down septum
     - RBBB/LBBB → Line renderers to ventricles
     - RA/LA/RV/LV → Position at chamber centers
     - Purkinje → Network of lines at ventricle walls
3. **Attach CardiacRegionMarker to each primitive**
4. **Use glow/particle effects** to highlight regions during ECG analysis

**Pros:**
- ✅ Fast to implement (30 minutes)
- ✅ Clear visualization of electrical pathways
- ✅ Judges will understand the concept
- ✅ Can animate signals flowing through primitives

---

### Plan B: Multiple Models Combined (BETTER - 1 hour)

1. **Download all 3 from HannahNewey** (external + veins + arteries)
2. **Import to Unity** and align them as layers
3. **Assign regions to different model parts:**
   - External view → Base heart structure
   - Veins → Electrical pathways (SA node, AV node paths)
   - Arteries → Bundle branches
4. **Use transparency** to show different layers
5. **Highlight specific vessels** to represent conduction paths

**Pros:**
- ✅ Multiple anatomical layers (fits your "peeling" concept)
- ✅ More visually impressive
- ✅ Shows real cardiac anatomy

---

### Plan C: Single High-Quality Model (SIMPLEST - 15 min)

1. **Download:** "Realistic Human Heart" or "Internal Structure"
2. **In Unity:** Place markers/lights on the heart surface at region locations
3. **Use visual effects:**
   - Lights that pulse at each region
   - Particle systems for electrical waves
   - Color overlays for affected areas
4. **No separate meshes needed** - just visual indicators

**Pros:**
- ✅ Extremely fast to set up
- ✅ Still shows ECG analysis working
- ✅ Focuses on backend integration (which works!)

---

## 📥 QUICK DOWNLOAD GUIDE

### Sketchfab Download Steps:
1. Go to model link
2. Click **"Download 3D Model"** button (bottom right)
3. **Login/Signup** (free account, takes 30 seconds)
4. Select format: **GLB** or **FBX** (both work in Unity)
5. Click Download
6. Extract ZIP file

### Import to Unity:
1. Create folder: `Assets/Models/Heart/`
2. Drag downloaded file into Unity
3. Unity will auto-import (may take a few seconds)
4. Drag model from Project window into Scene
5. Adjust scale: Usually set to 0.3-0.5 for VR comfort

---

## 🔗 ALL LINKS (Quick Reference)

**Sketchfab (BEST SOURCE):**
- Realistic Human Heart: https://sketchfab.com/3d-models/realistic-human-heart-3f8072336ce94d18b3d0d055a1ece089
- External Anatomy: https://sketchfab.com/3d-models/cardiac-anatomy-external-view-of-human-heart-a3f0ea2030214a6bbaa97e7357eebd58
- Internal Structure: https://sketchfab.com/3d-models/human-heart-internal-structure-3d-model-21d346f72230432e8ed5fe448b03cca5
- Visible Heart Lab: https://sketchfab.com/3d-models/internal-heart-anatomy-heart0612-fb9b10956eb64fbab6c9606179e946a3
- Beating Heart (animated!): https://sketchfab.com/3d-models/beating-human-heart-da560808739246a0a79a37291d492c1d

**TurboSquid (More Options):**
- Free Human Heart Models: https://www.turbosquid.com/Search/3D-Models/free/human-heart
- Free Anatomy Models: https://www.turbosquid.com/3d-model/free/anatomy/human-heart

**Other Free Sources:**
- embodi3D.com: https://www.embodi3d.com/files/category/21-heart/
- Clara.io: https://clara.io/library?query=heart
- Open3dModel: https://open3dmodel.com/3d-models/heart

---

## ⚡ FASTEST PATH TO DEMO (My Recommendation)

**Time:** 20 minutes total

1. **Download (5 min):**
   - Go to: https://sketchfab.com/3d-models/realistic-human-heart-3f8072336ce94d18b3d0d055a1ece089
   - Download GLB format
   - Extract to Assets/Models/Heart/

2. **Import to Unity (2 min):**
   - Drag GLB into Unity
   - Place in Scene at (0, 0, 0)
   - Set scale to 0.3

3. **Create Region Markers (10 min):**
   - Create 10 empty GameObjects as children of heart
   - Position them at cardiac region locations (use visual guides)
   - Add small primitive spheres or lights
   - Attach CardiacRegionMarker scripts
   - Set region names (sa_node, av_node, etc.)

4. **Test (3 min):**
   - Press Play
   - Watch regions light up based on ECG analysis!

**This gives you a working demo that:**
- ✅ Shows real heart anatomy
- ✅ Highlights affected regions
- ✅ Demonstrates backend-frontend integration
- ✅ Looks professional for judges

---

## 💡 PRO TIPS

### Tip 1: Use Glow Materials
Instead of complex models, use **emissive materials** to make regions glow:
```csharp
// In CardiacRegionMarker.cs
Renderer renderer = GetComponent<Renderer>();
renderer.material.EnableKeyword("_EMISSION");
renderer.material.SetColor("_EmissionColor", regionColor * severity);
```

### Tip 2: Particle Systems for Electrical Waves
Create electrical propagation visually:
- Line Renderer between regions (following activation_sequence)
- Particle trail that flows along the path
- Makes the demo more impressive than separate meshes!

### Tip 3: Multiple Camera Angles
Set up camera positions to show:
- Full heart view
- Close-up of affected region
- Electrical pathway animation
- Switches automatically during storytelling mode

### Tip 4: Color-Coded Regions
Since you can't separate meshes easily:
- Project colored lights onto heart surface
- Use Unity's Projector component
- Each region gets a colored spotlight
- Intensity = severity from API

---

## 🎬 DEMO SCRIPT

**What to show judges:**

1. **Load ECG data** (sample_rbbb.json)
2. **Backend analyzes** → RBBB detected (89% confidence)
3. **Heart model appears**
4. **Regions light up:**
   - SA Node: Orange (mild issue)
   - Right Bundle Branch: Red (severe blockage)
   - RV: Orange (affected by delay)
5. **Electrical wave animation** flows through heart
6. **UI shows:** "Right Bundle Branch Block - 89%"
7. **VR interaction:** Grab and rotate heart

**Judges see:**
- ✅ Real ECG analysis with AI
- ✅ Anatomically accurate visualization
- ✅ Backend-frontend integration working
- ✅ VR interaction
- ✅ Educational value

---

## 📊 Comparison Table

| Model | Quality | Setup Time | Demo Impact | License |
|-------|---------|------------|-------------|---------|
| Realistic Human Heart | ⭐⭐⭐⭐⭐ | 15 min | High | CC Free |
| HannahNewey Series | ⭐⭐⭐⭐ | 60 min | Very High | CC Free |
| Internal Structure | ⭐⭐⭐⭐ | 20 min | High | CC Free |
| Visible Heart Lab | ⭐⭐⭐⭐⭐ | 15 min | Very High | CC Free |
| Unity Primitives + Model | ⭐⭐⭐ | 30 min | Medium | N/A |

---

## ✅ ACTION PLAN

**Right now (choose one):**

### Option A: Quick & Simple (15 min)
1. Download "Realistic Human Heart" from Sketchfab
2. Import to Unity
3. Use colored lights to mark regions
4. Test with backend → **DONE!**

### Option B: Better Quality (1 hour)
1. Download all 3 HannahNewey models
2. Combine in Unity as layers
3. Create region markers
4. Add particle effects
5. Test → **Professional demo!**

### Option C: Hybrid (30 min) ⭐ **RECOMMENDED**
1. Download "Realistic Human Heart"
2. Create 10 primitive spheres at region positions
3. Attach CardiacRegionMarker scripts
4. Add glow materials and particle trails
5. Test → **Best balance of time/quality!**

---

## 🆘 TROUBLESHOOTING

### "Sketchfab download requires login"
- Create free account (30 seconds)
- No credit card needed
- Just email signup

### "Model is too big/small in Unity"
- Select model in Hierarchy
- Inspector → Transform → Scale
- Try: 0.3 for VR comfort distance

### "Model has too many polygons"
- Unity → Select model in Project
- Inspector → Model tab
- Mesh Compression: High
- OR use lower poly version from TurboSquid

### "Can't separate model into regions"
- Don't need to! Use Plan C (lights/markers)
- Or use Blender to separate (but takes time)

---

**BOTTOM LINE:** Download "Realistic Human Heart" from Sketchfab and use colored lights/spheres to mark regions. **20 minutes to working demo!**

---

**Created:** 2025-11-16
**For:** HoloHuman XR - Immerse the Bay 2025
**Status:** Ready to download and use
