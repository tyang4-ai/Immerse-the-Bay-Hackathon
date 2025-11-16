# Quick Region Markers Setup - Light Bulb Approach
**HoloHuman XR - 10 ECG Regions with Point Lights**

**Time to complete:** 15 minutes
**Result:** Working ECG visualization with glowing regions

---

## 🎯 What You're Creating

10 empty GameObjects positioned around your heart model, each with:
- **Point Light** (will glow when region is affected)
- **Small Sphere** (visual marker to see where it is)
- **CardiacRegionMarker script** (receives data from backend)

---

## 📍 STEP-BY-STEP GUIDE

### Setup 1: Create Your First Region Marker (3 min)

Let's create the SA Node region as an example:

#### 1. Create Empty GameObject
1. **Hierarchy** → Right-click → **Create Empty**
2. **Rename** to: `Region_SA_Node`
3. **Position** at: `(0, 0, 0)` for now (we'll move it in a moment)

#### 2. Add Visual Sphere
1. **Right-click Region_SA_Node** → **3D Object** → **Sphere**
2. **Rename** the sphere to: `Marker_Sphere`
3. **Set scale:** `(0.05, 0.05, 0.05)` - small marker
4. **Inspector** → **Mesh Renderer** → **Materials**
5. **Create new material:**
   - Right-click in Project → Create → Material
   - Name: `Mat_SANode_Debug`
   - Albedo Color: **Yellow** (helps you see it)
6. **Drag material** onto the sphere

#### 3. Add Point Light
1. **Right-click Region_SA_Node** → **Light** → **Point Light**
2. **Configure the light:**
   - **Intensity:** 0 (script will control this)
   - **Range:** 2
   - **Color:** White (script will change this)
   - **Mode:** Realtime
   - **Shadow Type:** No Shadows (for performance)

#### 4. Add CardiacRegionMarker Script
1. **Select Region_SA_Node** (parent)
2. **Inspector** → **Add Component**
3. **Search:** `CardiacRegionMarker`
4. **Click** to add it
5. **Region Name field:** Type exactly `sa_node` (lowercase with underscore)

#### 5. Position the Marker
1. **Select Region_SA_Node**
2. **Inspector** → **Transform** → **Position**
3. **Set to:** See position table below

**Your hierarchy should look like:**
```
Region_SA_Node
├── Marker_Sphere (small yellow sphere)
└── Point Light (invisible, will glow when activated)
```

---

## 📊 EXACT POSITIONS FOR ALL 10 REGIONS

**Copy these positions for each region marker:**

### Assuming your heart model is centered at (0, 0, 0)

| Region GameObject | Region Name (in script) | Position (X, Y, Z) | Debug Color |
|-------------------|------------------------|-------------------|-------------|
| Region_SA_Node | `sa_node` | **(0.15, 0.25, 0.1)** | Yellow |
| Region_RA | `ra` | **(0.2, 0.1, 0.05)** | Light Blue |
| Region_LA | `la` | **(-0.2, 0.1, 0.05)** | Light Red |
| Region_AV_Node | `av_node` | **(0.05, 0.0, 0.0)** | Orange |
| Region_Bundle_His | `bundle_his` | **(0.0, -0.05, 0.0)** | Purple |
| Region_RBBB | `rbbb` | **(0.15, -0.15, 0.0)** | Red |
| Region_LBBB | `lbbb` | **(-0.15, -0.15, 0.0)** | Pink |
| Region_Purkinje | `purkinje` | **(0.0, -0.25, 0.0)** | Green |
| Region_RV | `rv` | **(0.15, -0.2, 0.1)** | Dark Blue |
| Region_LV | `lv` | **(-0.15, -0.2, 0.1)** | Dark Red |

**Visual layout:**
```
        SA_Node (top right, yellow)
           |
    LA ----+---- RA (middle, left/right)
    (red)       (blue)
           |
       AV_Node (center, orange)
           |
    Bundle_His (center down, purple)
           |
    LBBB --+-- RBBB (left/right, pink/red)
           |
      Purkinje (bottom center, green)
           |
      LV --+-- RV (left/right, dark colors)
```

---

## 🚀 QUICK CREATE SCRIPT (Copy-Paste Method)

### Create All 10 Regions Fast (10 min)

**For each region, repeat these steps:**

#### Region 1: SA_Node
1. **Hierarchy** → Right-click → Create Empty → Name: `Region_SA_Node`
2. **Position:** (0.15, 0.25, 0.1)
3. **Right-click Region_SA_Node** → 3D Object → Sphere
   - Scale: (0.05, 0.05, 0.05)
   - Material: Yellow
4. **Right-click Region_SA_Node** → Light → Point Light
   - Intensity: 0
   - Range: 2
5. **Add Component → CardiacRegionMarker**
   - Region Name: `sa_node`

#### Region 2: RA
1. **Hierarchy** → Right-click → Create Empty → Name: `Region_RA`
2. **Position:** (0.2, 0.1, 0.05)
3. **Right-click Region_RA** → 3D Object → Sphere
   - Scale: (0.05, 0.05, 0.05)
   - Material: Light Blue
4. **Right-click Region_RA** → Light → Point Light
   - Intensity: 0
   - Range: 2
5. **Add Component → CardiacRegionMarker**
   - Region Name: `ra`

#### Region 3: LA
1. **Hierarchy** → Right-click → Create Empty → Name: `Region_LA`
2. **Position:** (-0.2, 0.1, 0.05)
3. **Right-click Region_LA** → 3D Object → Sphere
   - Scale: (0.05, 0.05, 0.05)
   - Material: Light Red
4. **Right-click Region_LA** → Light → Point Light
   - Intensity: 0
   - Range: 2
5. **Add Component → CardiacRegionMarker**
   - Region Name: `la`

#### Region 4: AV_Node
1. **Hierarchy** → Right-click → Create Empty → Name: `Region_AV_Node`
2. **Position:** (0.05, 0.0, 0.0)
3. **Right-click Region_AV_Node** → 3D Object → Sphere
   - Scale: (0.05, 0.05, 0.05)
   - Material: Orange
4. **Right-click Region_AV_Node** → Light → Point Light
   - Intensity: 0
   - Range: 2
5. **Add Component → CardiacRegionMarker**
   - Region Name: `av_node`

#### Region 5: Bundle_His
1. **Hierarchy** → Right-click → Create Empty → Name: `Region_Bundle_His`
2. **Position:** (0.0, -0.05, 0.0)
3. **Right-click Region_Bundle_His** → 3D Object → Sphere
   - Scale: (0.05, 0.05, 0.05)
   - Material: Purple
4. **Right-click Region_Bundle_His** → Light → Point Light
   - Intensity: 0
   - Range: 2
5. **Add Component → CardiacRegionMarker**
   - Region Name: `bundle_his`

#### Region 6: RBBB
1. **Hierarchy** → Right-click → Create Empty → Name: `Region_RBBB`
2. **Position:** (0.15, -0.15, 0.0)
3. **Right-click Region_RBBB** → 3D Object → Sphere
   - Scale: (0.05, 0.05, 0.05)
   - Material: Red
4. **Right-click Region_RBBB** → Light → Point Light
   - Intensity: 0
   - Range: 2
5. **Add Component → CardiacRegionMarker**
   - Region Name: `rbbb`

#### Region 7: LBBB
1. **Hierarchy** → Right-click → Create Empty → Name: `Region_LBBB`
2. **Position:** (-0.15, -0.15, 0.0)
3. **Right-click Region_LBBB** → 3D Object → Sphere
   - Scale: (0.05, 0.05, 0.05)
   - Material: Pink
4. **Right-click Region_LBBB** → Light → Point Light
   - Intensity: 0
   - Range: 2
5. **Add Component → CardiacRegionMarker**
   - Region Name: `lbbb`

#### Region 8: Purkinje
1. **Hierarchy** → Right-click → Create Empty → Name: `Region_Purkinje`
2. **Position:** (0.0, -0.25, 0.0)
3. **Right-click Region_Purkinje** → 3D Object → Sphere
   - Scale: (0.05, 0.05, 0.05)
   - Material: Green
4. **Right-click Region_Purkinje** → Light → Point Light
   - Intensity: 0
   - Range: 2
5. **Add Component → CardiacRegionMarker**
   - Region Name: `purkinje`

#### Region 9: RV
1. **Hierarchy** → Right-click → Create Empty → Name: `Region_RV`
2. **Position:** (0.15, -0.2, 0.1)
3. **Right-click Region_RV** → 3D Object → Sphere
   - Scale: (0.05, 0.05, 0.05)
   - Material: Dark Blue
4. **Right-click Region_RV** → Light → Point Light
   - Intensity: 0
   - Range: 2
5. **Add Component → CardiacRegionMarker**
   - Region Name: `rv`

#### Region 10: LV
1. **Hierarchy** → Right-click → Create Empty → Name: `Region_LV`
2. **Position:** (-0.15, -0.2, 0.1)
3. **Right-click Region_LV** → 3D Object → Sphere
   - Scale: (0.05, 0.05, 0.05)
   - Material: Dark Red
4. **Right-click Region_LV** → Light → Point Light
   - Intensity: 0
   - Range: 2
5. **Add Component → CardiacRegionMarker**
   - Region Name: `lv`

---

## 🎨 VISUAL ADJUSTMENT (After Creating All 10)

### Step 1: Look at Your Heart Model

1. **Click on your heart model** in Hierarchy
2. **Frame it in Scene view** (press F key)
3. **Note where the regions actually are** on YOUR specific model

### Step 2: Adjust Marker Positions

**Your model might be different scale/orientation, so adjust positions:**

**Quick anatomy guide:**
- **SA Node:** Upper right atrium (top right of heart)
- **RA:** Right side, upper chamber
- **LA:** Left side, upper chamber
- **AV Node:** Center, between atria and ventricles
- **Bundle of His:** Center, going down
- **RBBB:** Right side, lower pathway
- **LBBB:** Left side, lower pathway
- **Purkinje:** Spread across bottom (ventricular walls)
- **RV:** Right ventricle (lower right)
- **LV:** Left ventricle (lower left)

**To move markers:**
1. **Select the region** in Hierarchy
2. **Scene view:** Use Move tool (W key) to drag it
3. **Place near** the corresponding part of your heart anatomy
4. **Doesn't need to be perfect!** Approximate is fine

---

## 🔧 MAKE ALL REGIONS CHILDREN OF HEART MODEL

**Keep everything organized:**

1. **In Hierarchy, create empty GameObject:** `HeartRegions`
2. **Drag all 10 Region_XXX objects** under HeartRegions
3. **Make HeartRegions a child** of your heart model

**Final hierarchy:**
```
HeartModel (your downloaded model)
├── (all your model parts: atria, veins, etc.)
└── HeartRegions (empty parent)
    ├── Region_SA_Node
    ├── Region_RA
    ├── Region_LA
    ├── Region_AV_Node
    ├── Region_Bundle_His
    ├── Region_RBBB
    ├── Region_LBBB
    ├── Region_Purkinje
    ├── Region_RV
    └── Region_LV
```

**Benefit:** When you scale/move heart model, all regions move with it!

---

## ✅ VERIFICATION CHECKLIST

After creating all 10 regions:

- [ ] 10 Region GameObjects created
- [ ] Each has a small sphere child (colored for debugging)
- [ ] Each has a Point Light child (intensity 0, range 2)
- [ ] Each has CardiacRegionMarker script attached
- [ ] Region Name field set correctly for each (lowercase with underscore)
- [ ] All regions visible in Scene view around heart model
- [ ] All regions are children of HeartRegions parent

---

## 🧪 TEST IT!

### Quick Test (Before Full Integration)

1. **Select Region_RBBB**
2. **In Inspector → Point Light component**
3. **Set Intensity to 5** (manually)
4. **Set Color to Red**
5. **Look in Scene/Game view** → Should see red glow!
6. **Set Intensity back to 0**

**If you see the glow, everything is set up correctly!**

---

## 🔗 CONNECT TO HEARTHREGIONMAPPING

### Final Step: Let the Scripts Find Your Regions

1. **Create empty GameObject:** `Controllers`
2. **Add Component:** `HeartRegionMapping`
3. **Inspector → HeartRegionMapping script:**
   - It will automatically find all CardiacRegionMarker scripts in the scene
   - No need to manually assign anything!

4. **Check Console when you press Play:**
   ```
   [HeartRegionMapping] Registered region: sa_node
   [HeartRegionMapping] Registered region: ra
   ... (should see all 10)
   ```

**If you see all 10 registered → SUCCESS!**

---

## 🎬 WHAT HAPPENS DURING ECG ANALYSIS

**When you analyze RBBB ECG:**

1. **Backend sends data:**
   ```json
   "region_health": {
     "rbbb": {
       "severity": 0.89,
       "color": [1.0, 0.0, 0.0]  // Red
     }
   }
   ```

2. **ECGHeartController receives data**

3. **HeartRegionMapping finds Region_RBBB**

4. **CardiacRegionMarker on Region_RBBB updates:**
   - Point Light intensity = 0.89 (very bright)
   - Point Light color = Red
   - Marker sphere glows red

5. **You see:** RBBB region lights up RED on the heart!

---

## 💡 PRO TIPS

### Tip 1: Adjust Light Range
If lights are too bright/dim:
- Select region → Point Light component
- Change **Range** (2 is default, try 1.5-3.0)

### Tip 2: Hide Debug Spheres in Final Demo
Before final demo:
- Select each region
- Find the Marker_Sphere child
- **Uncheck the box** next to its name (disables it)
- Only lights will show (cleaner look!)

### Tip 3: Add Line Renderers for Electrical Pathways
For extra visual impact:
- Add Line Renderer components between regions
- Show electrical signal flowing from SA → RA → LA → AV → etc.
- Animate the line during analysis

### Tip 4: Make Spheres Emissive
Instead of plain colored spheres:
- Create material with Emission enabled
- Set Emission color to match region
- Spheres glow even when lights are off!

---

## 📊 EXPECTED RESULT

**After setup, you'll have:**

✅ 10 colored marker spheres positioned around heart
✅ 10 point lights ready to glow
✅ All scripts connected and ready for backend data
✅ Easy to see which regions are affected during ECG analysis

**Time spent:** 15 minutes
**Impressiveness:** High - judges will clearly see electrical pathways!

---

## 🆘 COMMON ISSUES

### "I can't see the spheres"
- Check scale: Should be 0.05 (very small)
- Check camera position: Frame the heart (F key)
- Check materials: Make sure colors are assigned

### "Lights don't appear"
- Intensity is 0 by default (correct!)
- Manually set intensity to 5 to test
- Check Range is set to 2

### "Script can't find regions"
- Check Region Name field is exact: `sa_node` not "sa_node" or "SA Node"
- Check CardiacRegionMarker is on PARENT not sphere/light
- Press Play and check Console for registration messages

### "All regions glow the same"
- Each region should have its own Point Light component
- Make sure lights are children of DIFFERENT region parents

---

## ✅ FINAL CHECKLIST

**Before testing with backend:**

- [ ] All 10 regions created
- [ ] All positioned around heart (approximate is fine!)
- [ ] All have CardiacRegionMarker script with correct name
- [ ] All have Point Light (intensity 0, range 2)
- [ ] All have debug sphere (optional, for visualization)
- [ ] HeartRegionMapping script added to Controllers GameObject
- [ ] Press Play → Console shows all 10 regions registered

**If all checked → Ready to test with ECG backend!** 🎉

---

**Created:** 2025-11-16
**Time to complete:** 15 minutes
**Next step:** Follow QUICK_UNITY_SETUP.md to connect to backend
