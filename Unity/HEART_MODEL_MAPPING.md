# Heart Model Mapping Guide
**HoloHuman XR - Map 20 Anatomical Parts to 10 ECG Regions**

---

## Your 10 Required ECG Regions

These are the regions your backend API and Unity scripts expect:

1. **sa_node** - Sinoatrial Node (pacemaker)
2. **ra** - Right Atrium
3. **la** - Left Atrium
4. **av_node** - Atrioventricular Node
5. **bundle_his** - Bundle of His
6. **rbbb** - Right Bundle Branch
7. **lbbb** - Left Bundle Branch
8. **purkinje** - Purkinje Fibers
9. **rv** - Right Ventricle
10. **lv** - Left Ventricle

---

## Your 20 Model Parts

From your downloaded model:

**Atria (4 parts):**
- Left Atrium
- Left Auricle
- Right Atrium
- Right Auricle

**Veins (7 parts):**
- Left Superior and Inferior Pulmonary Veins
- Right Superior and Inferior Pulmonary Veins
- Inferior Vena Cava
- Superior Vena Cava
- Coronary Sinus

**Cardiac Veins (3 parts):**
- Great Cardiac Vein
- Middle Cardiac Vein
- Small Cardiac Vein
- Posterior Cardiac Vein

**Arteries (3 parts):**
- Ascending Aorta
- Pulmonary Trunk
- Left Coronary Artery
- Right Coronary Artery

**Other (2 parts):**
- Ligamentum Arteriosum

**Missing from model:**
- Right Ventricle
- Left Ventricle
- SA Node (sinoatrial node)
- AV Node (atrioventricular node)
- Bundle of His
- Bundle Branches
- Purkinje Fibers

---

## 🎯 MAPPING STRATEGY

### Option A: Anatomical Grouping (RECOMMENDED)

Group your 20 parts into the 10 regions based on **electrical conduction pathways**:

#### 1. **sa_node** (SA Node - Pacemaker)
**Group these parts:**
- Right Atrium (upper portion represents SA node location)
- Superior Vena Cava (adjacent to SA node)

**Why:** SA node is located in the upper right atrium near SVC junction

---

#### 2. **ra** (Right Atrium)
**Group these parts:**
- Right Atrium (main body)
- Right Auricle (ear-shaped appendage)
- Inferior Vena Cava (drains into RA)

**Why:** These are all right atrial structures

---

#### 3. **la** (Left Atrium)
**Group these parts:**
- Left Atrium (main body)
- Left Auricle (ear-shaped appendage)
- Left Superior and Inferior Pulmonary Veins (drain into LA)
- Right Superior and Inferior Pulmonary Veins (also drain into LA)

**Why:** These are all left atrial structures

---

#### 4. **av_node** (AV Node)
**Group these parts:**
- Coronary Sinus (located near AV node)

**Why:** AV node is located near coronary sinus opening in right atrium

---

#### 5. **bundle_his** (Bundle of His)
**Group these parts:**
- (No direct anatomical match - will create empty GameObject)

**Why:** Bundle of His is internal conduction tissue, not visible externally

---

#### 6. **rbbb** (Right Bundle Branch)
**Group these parts:**
- Right Coronary Artery (follows similar path down right side)
- Small Cardiac Vein (runs along right ventricle)
- Middle Cardiac Vein (posterior interventricular)

**Why:** Right coronary artery and veins follow the right bundle branch pathway

---

#### 7. **lbbb** (Left Bundle Branch)
**Group these parts:**
- Left Coronary Artery (follows similar path down left side)
- Great Cardiac Vein (runs along left ventricle)

**Why:** Left coronary artery follows the left bundle branch pathway

---

#### 8. **purkinje** (Purkinje Fibers)
**Group these parts:**
- Posterior Cardiac Vein (spreads across ventricular walls)

**Why:** Purkinje fibers spread throughout both ventricles like cardiac veins

---

#### 9. **rv** (Right Ventricle)
**Group these parts:**
- Pulmonary Trunk (exits from RV)
- Ligamentum Arteriosum (connects to pulmonary trunk)

**Why:** Pulmonary trunk originates from right ventricle

---

#### 10. **lv** (Left Ventricle)
**Group these parts:**
- Ascending Aorta (exits from LV)

**Why:** Aorta originates from left ventricle

---

## 📋 QUICK REFERENCE TABLE

| ECG Region | Model Parts to Group | Parent GameObject Name |
|------------|---------------------|------------------------|
| **sa_node** | Right Atrium (upper) + Superior Vena Cava | Region_SA_Node |
| **ra** | Right Atrium + Right Auricle + Inferior Vena Cava | Region_RA |
| **la** | Left Atrium + Left Auricle + All Pulmonary Veins | Region_LA |
| **av_node** | Coronary Sinus | Region_AV_Node |
| **bundle_his** | (Empty - add primitive) | Region_Bundle_His |
| **rbbb** | Right Coronary Artery + Small Cardiac Vein + Middle Cardiac Vein | Region_RBBB |
| **lbbb** | Left Coronary Artery + Great Cardiac Vein | Region_LBBB |
| **purkinje** | Posterior Cardiac Vein | Region_Purkinje |
| **rv** | Pulmonary Trunk + Ligamentum Arteriosum | Region_RV |
| **lv** | Ascending Aorta | Region_LV |

---

## 🛠️ UNITY IMPLEMENTATION STEPS

### Step 1: Create Parent GameObjects (5 min)

1. **In Hierarchy, create 10 empty GameObjects:**
   - Right-click in Hierarchy → Create Empty
   - Name them: `Region_SA_Node`, `Region_RA`, `Region_LA`, etc.

2. **Make them children of your heart model:**
   ```
   HeartModel (parent)
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

---

### Step 2: Group Model Parts (10 min)

**For each region, drag the corresponding model parts as children:**

#### Example: Region_RA
```
Region_RA (empty parent)
├── Right Atrium (model mesh)
├── Right Auricle (model mesh)
└── Inferior Vena Cava (model mesh)
```

**Repeat for all 10 regions using the table above.**

---

### Step 3: Add CardiacRegionMarker Scripts (5 min)

**For each of the 10 region parent GameObjects:**

1. **Select Region_SA_Node**
2. **Inspector → Add Component → "CardiacRegionMarker"**
3. **Set Region Name field:** `sa_node` (exact lowercase, match the backend API)
4. **Repeat for all 10 regions**

**IMPORTANT: Region names must exactly match:**
- sa_node
- ra
- la
- av_node
- bundle_his
- rbbb
- lbbb
- purkinje
- rv
- lv

---

### Step 4: Handle Missing Parts (5 min)

**For regions with no matching model parts:**

**Region_Bundle_His:**
1. Create a small sphere primitive as a child
2. Position it between atria and ventricles (center of heart)
3. Scale: 0.1, 0.1, 0.1
4. Make it semi-transparent (Material → Rendering Mode → Transparent)

**Optional - Add visual markers to all regions:**
- Add a small point light to each region parent
- Will glow when that region is affected
- Easy to see in VR

---

## 🎨 VISUAL ENHANCEMENT (Optional - 10 min)

### Add Glow Effects to Each Region

**For each region parent GameObject:**

1. **Add a Point Light component:**
   - Intensity: 0 (will be controlled by script)
   - Range: 2
   - Color: White (will change based on severity)

2. **Add a Particle System (optional):**
   - Shape: Sphere
   - Start Lifetime: 1
   - Start Speed: 0.5
   - Emission Rate: 0 (will be controlled by script)

**CardiacRegionMarker script will automatically control these!**

---

## ⚡ ALTERNATIVE: Simple Approach (Fastest - 5 min)

**If you're short on time:**

### Don't group the parts at all!

1. **Create 10 empty GameObjects** with region names
2. **Position them roughly** where each region should be
3. **Add Point Lights** to each (for glow effect)
4. **Add CardiacRegionMarker scripts**
5. **Let the lights show affected regions**

**Your existing model parts stay separate** - they're just visual anatomy
**The 10 region markers** are functional electrical pathway indicators

**This actually looks better in VR** - clearer to see which electrical region is affected!

---

## 🔍 VERIFICATION CHECKLIST

After setup, verify:

- [ ] 10 Region parent GameObjects created
- [ ] Each region has CardiacRegionMarker script attached
- [ ] Region name fields set correctly (lowercase, exact match)
- [ ] Model parts grouped under appropriate regions
- [ ] HeartRegionMapping script can find all regions
- [ ] Press Play → Console shows all regions registered

**Check Console for:**
```
[HeartRegionMapping] Registered region: sa_node
[HeartRegionMapping] Registered region: ra
[HeartRegionMapping] Registered region: la
... (should see all 10)
```

---

## 🎯 WHAT EACH REGION DOES

When ECG analysis runs:

1. **Backend sends severity for each region** (0.0 to 1.0)
2. **Backend sends color for each region** (RGB values)
3. **CardiacRegionMarker receives this data**
4. **Visual effects update:**
   - Point Light intensity = severity
   - Point Light color = region color
   - Particle emission rate = severity
   - All grouped mesh materials can glow

**Example:** RBBB detected (89% severity)
- Region_RBBB light turns red
- Intensity increases to 0.89
- Particles emit
- All parts in that group glow red

---

## 📊 EXPECTED VISUAL RESULT

**During ECG analysis of RBBB patient:**

| Region | Effect |
|--------|--------|
| sa_node | Orange glow (mild - 0.5 severity) |
| ra | Normal (0.0 severity) |
| la | Normal (0.0 severity) |
| av_node | Normal (0.0 severity) |
| bundle_his | Normal (0.0 severity) |
| **rbbb** | **Red glow (severe - 0.89 severity)** ← Main issue! |
| lbbb | Normal (0.0 severity) |
| purkinje | Normal (0.0 severity) |
| rv | Orange glow (affected - 0.4 severity) |
| lv | Normal (0.0 severity) |

**Judges will clearly see:** Right Bundle Branch is blocked!

---

## 🆘 TROUBLESHOOTING

### "HeartRegionMapping can't find region"
**Cause:** Region name mismatch
**Fix:**
- Select region GameObject
- CardiacRegionMarker → Region Name field
- Must be exact: `sa_node` (not "SA Node" or "sa node")

### "All regions glow the same color"
**Cause:** Shared material on model parts
**Fix:**
- Select each mesh
- Inspector → Materials → Click material
- Duplicate material (Ctrl+D)
- Assign unique material to each region group

### "Can't see the glow effect"
**Cause:** No light component
**Fix:**
- Add Point Light to each region parent
- Set Range: 2
- Set Intensity: 0 (script will control it)

---

## 💡 PRO TIP: Color-Code in Unity Editor

**To help you visualize regions:**

1. **Create colored materials:**
   - Right-click in Project → Create → Material
   - Name: `Mat_SA_Node`, `Mat_RA`, etc.
   - Set Base Color to unique color for each

2. **Assign to region children:**
   - Helps you see which parts belong to which region
   - Makes debugging easier

3. **In Play mode:**
   - Materials will change based on ECG data
   - Your debug colors help you confirm regions are grouped correctly

---

## ✅ SUMMARY

**What you're doing:**
- Grouping 20 visible anatomical parts into 10 functional electrical regions
- Adding marker scripts to each region
- Letting the backend control visual effects based on ECG analysis

**Time estimate:**
- Quick approach: 5 minutes (empty regions + lights)
- Full approach: 25 minutes (group all parts + effects)

**My recommendation:**
Start with **quick approach** to test backend connection, then enhance visuals later if time permits!

---

**Created:** 2025-11-16
**Purpose:** Map anatomical heart model to electrical conduction regions
**Next:** Set up HeartRegionMapping to find all 10 regions
