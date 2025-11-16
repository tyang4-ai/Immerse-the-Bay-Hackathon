# Meshy.ai Prompts for Separate Heart Components
**HoloHuman XR - Generating Individual Cardiac Structures**

> **Goal:** Generate 10 individual cardiac region models that fit together anatomically
> **Platform:** https://www.meshy.ai/
> **Output Format:** FBX or GLB (Unity-compatible)
> **Total Components:** 10 separate 3D models

---

## Strategy for Modular Heart Components

### Approach: Generate with Shared Reference

To ensure all parts fit together correctly, we'll:

1. **Generate a full heart base** first (reference model)
2. **Extract/generate each component** with size/position references
3. **Use consistent scale and orientation** across all prompts
4. **Import to Unity** and position using anatomical coordinates

### Alternative Approach: Single Model with Separated Meshes

If Meshy.ai's output is a single merged mesh:
1. Generate full heart with distinct regions
2. Import to Blender
3. Separate by material/selection
4. Export each region individually

---

## Prompt Set 1: Full Heart Reference Model

### Prompt 1A: Complete Heart (Base Reference)

```
3D anatomical human heart model, photorealistic medical visualization, separated into
distinct color-coded regions: SA node (bright blue sphere), right atrium (light red),
left atrium (light pink), AV node (yellow sphere), Bundle of His (orange cylinder),
right bundle branch (orange line), left bundle branch (orange line), Purkinje fibers
(green network), right ventricle (red), left ventricle (deep red). Clean topology,
low-poly optimized for VR, subdivision-ready, no background, orthographic view,
medical textbook style, 4K PBR textures
```

**Settings:**
- Art Style: Realistic
- Topology: Quad
- Polygon Count: Medium (30-50k)
- Export: FBX

**Use:** This is your reference for scale and positioning. Import to Unity first.

---

## Prompt Set 2: Individual Cardiac Components

### Component 1: SA Node (Sinoatrial Node)

```
3D medical model of SA node (sinoatrial node), small spherical structure located
in upper right atrium, size approximately 5mm diameter, bright blue glowing material,
visible electrical fibers extending outward, anatomically accurate position,
clean mesh topology, low-poly VR-optimized, no background, medical visualization style
```

**Technical Specs:**
- Size: 5mm diameter sphere
- Position: Upper right atrium (0.05, 0.08, 0.02)
- Color: Bright blue (#3399FF)
- Export Name: `sa_node.fbx`

---

### Component 2: Right Atrium (RA)

```
3D anatomical model of right atrium chamber, smooth muscular walls, semi-transparent
light red material, trabeculated inner surface, superior and inferior vena cava
entry points visible, anatomically accurate shape, moderate detail, VR-optimized
polygon count, PBR materials, no background
```

**Technical Specs:**
- Size: ~4cm × 3cm
- Position: Right upper heart (0.06, 0.03, 0.01)
- Color: Light red (#FF8080)
- Export Name: `ra.fbx`

---

### Component 3: Left Atrium (LA)

```
3D anatomical model of left atrium chamber, smooth muscular walls, semi-transparent
light pink material, four pulmonary vein entry points visible, slightly smaller than
right atrium, anatomically accurate shape, moderate detail, VR-optimized,
PBR materials, no background
```

**Technical Specs:**
- Size: ~3.5cm × 2.8cm
- Position: Left upper heart (-0.06, 0.03, 0.01)
- Color: Light pink (#FFAAAA)
- Export Name: `la.fbx`

---

### Component 4: AV Node (Atrioventricular Node)

```
3D medical model of AV node (atrioventricular node), small oval structure located
in interatrial septum near tricuspid valve, size approximately 6mm × 3mm,
bright yellow glowing material, visible connecting fibers to Bundle of His,
anatomically accurate position, clean topology, VR-optimized, no background
```

**Technical Specs:**
- Size: 6mm × 3mm oval
- Position: Between atria and ventricles (0.00, 0.00, 0.00)
- Color: Yellow (#FFFF00)
- Export Name: `av_node.fbx`

---

### Component 5: Bundle of His

```
3D medical model of Bundle of His, thick cylindrical nerve bundle, approximately
15mm long and 3mm diameter, bright orange fibrous material with visible striations,
originates from AV node and descends along interventricular septum, anatomically
accurate path, clean topology, VR-optimized, no background
```

**Technical Specs:**
- Size: 15mm length × 3mm diameter
- Position: Septum between ventricles (0.00, -0.02, 0.00)
- Color: Orange (#FF8800)
- Export Name: `bundle_his.fbx`

---

### Component 6: Right Bundle Branch (RBBB)

```
3D medical model of right bundle branch, thin branching nerve fibers, extends from
Bundle of His along right side of interventricular septum toward right ventricle,
bright orange cable-like structure with visible branches, length approximately 30mm,
diameter 2mm at base tapering to 0.5mm, anatomically accurate path, clean topology,
VR-optimized, no background
```

**Technical Specs:**
- Size: 30mm branching structure
- Position: Right septum (0.04, -0.05, 0.00)
- Color: Orange (#FF8800)
- Export Name: `rbbb.fbx`

---

### Component 7: Left Bundle Branch (LBBB)

```
3D medical model of left bundle branch, thin branching nerve fibers, extends from
Bundle of His along left side of interventricular septum toward left ventricle,
bright orange cable-like structure with multiple fine branches, length approximately
25mm, diameter 2mm at base tapering to 0.5mm, anatomically accurate path,
clean topology, VR-optimized, no background
```

**Technical Specs:**
- Size: 25mm branching structure
- Position: Left septum (-0.04, -0.05, 0.00)
- Color: Orange (#FF8800)
- Export Name: `lbbb.fbx`

---

### Component 8: Purkinje Fibers Network

```
3D medical model of Purkinje fiber network, intricate web of fine electrical
fibers distributed throughout ventricular walls, bright green glowing threads,
tree-like branching pattern spreading across inner ventricular surface, individual
fibers 0.5mm diameter, highly detailed network, anatomically accurate distribution,
clean topology, VR-optimized, no background
```

**Technical Specs:**
- Size: Covers ventricular walls
- Position: Ventricular walls (0.00, -0.08, 0.00)
- Color: Bright green (#00FF88)
- Export Name: `purkinje.fbx`

---

### Component 9: Right Ventricle (RV)

```
3D anatomical model of right ventricle chamber, thick muscular walls with
trabeculations, triangular cross-section shape, semi-transparent red material,
visible papillary muscles and chordae tendineae, tricuspid valve at inlet,
pulmonary valve at outlet, anatomically accurate shape, moderate detail,
VR-optimized polygon count, PBR materials, no background
```

**Technical Specs:**
- Size: ~5cm × 4cm × 6cm
- Position: Right lower heart (0.05, -0.06, 0.02)
- Color: Red (#FF4444)
- Export Name: `rv.fbx`

---

### Component 10: Left Ventricle (LV)

```
3D anatomical model of left ventricle chamber, very thick muscular walls
(10-15mm thickness), elliptical/conical shape, semi-transparent deep red material,
visible papillary muscles and chordae tendineae, mitral valve at inlet, aortic
valve at outlet, most muscular chamber, anatomically accurate shape with apex,
moderate detail, VR-optimized polygon count, PBR materials, no background
```

**Technical Specs:**
- Size: ~5cm × 4cm × 7cm
- Position: Left lower heart (-0.05, -0.06, 0.02)
- Color: Deep red (#CC0000)
- Export Name: `lv.fbx`

---

## Meshy.ai Generation Workflow

### Step 1: Create Account
1. Go to https://www.meshy.ai/
2. Sign up (free tier: 50 credits/month)
3. Each generation costs ~1-5 credits depending on quality

### Step 2: Generate Each Component

For each of the 10 prompts above:

1. **Select "Text to 3D"**
2. **Paste prompt** from above
3. **Configure Settings:**
   ```
   Art Style: Realistic
   Negative Prompt: "cartoon, stylized, anime, low quality, deformed"
   Topology: Quad (cleaner for Unity)
   Polygon Count: Medium (30-50k per component)
   ```
4. **Generate** (takes 3-5 minutes)
5. **Download FBX** format
6. **Rename file** to exact name (sa_node.fbx, ra.fbx, etc.)

### Step 3: Quality Check

After generation, check each model for:
- ✓ Reasonable polygon count (<10k per small component, <30k per chamber)
- ✓ Clean UV mapping (for textures)
- ✓ Proper orientation (Y-up for Unity)
- ✓ No missing faces or holes
- ✓ Appropriate scale (use reference heart for comparison)

---

## Unity Import Workflow

### Step 1: Import All FBX Files

```
Unity Project
└── Assets/
    └── Models/
        └── Heart/
            ├── full_heart_reference.fbx  (reference model)
            ├── sa_node.fbx
            ├── ra.fbx
            ├── la.fbx
            ├── av_node.fbx
            ├── bundle_his.fbx
            ├── rbbb.fbx
            ├── lbbb.fbx
            ├── purkinje.fbx
            ├── rv.fbx
            └── lv.fbx
```

### Step 2: Configure Import Settings

Select all FBX files, set:
```
Model Tab:
  Scale Factor: 1
  Mesh Compression: Off
  Read/Write Enabled: ✓
  Optimize Mesh: ✓
  Generate Colliders: ☐

Rig Tab:
  Animation Type: None

Materials Tab:
  Material Creation Mode: Standard (Specular)
  Extract Textures: ✓
```

### Step 3: Assemble in Scene

1. **Drag full_heart_reference.fbx** to scene at (0, 0, 0)
2. **Scale to VR size** (approximately 0.3 units)
3. **For each component:**
   ```
   - Drag component FBX into scene
   - Make child of HeartModel GameObject
   - Position relative to reference model
   - Match scale with reference
   - Adjust rotation if needed
   ```

4. **Use anatomical positions** from Integration Guide:
   ```csharp
   // Example positioning script
   sa_node.transform.localPosition = new Vector3(0.05f, 0.08f, 0.02f);
   ra.transform.localPosition = new Vector3(0.06f, 0.03f, 0.01f);
   // ... etc for all 10 components
   ```

### Step 4: Attach CardiacRegionMarker Scripts

For each component:
1. Select component GameObject
2. Add Component → **CardiacRegionMarker**
3. Set **regionName** to exact backend name:
   ```
   sa_node → "sa_node"
   ra → "ra"
   la → "la"
   av_node → "av_node"
   bundle_his → "bundle_his"
   rbbb → "rbbb"
   lbbb → "lbbb"
   purkinje → "purkinje"
   rv → "rv"
   lv → "lv"
   ```
4. Add **Light** component (Point Light, Range: 0.5, Intensity: 2.0)
5. Add **Particle System** (optional, for electrical effects)

---

## Troubleshooting Meshy.ai

### Issue 1: Models don't fit together

**Solution:**
- Generate all components in a single session
- Use same "Art Style" and "Topology" settings
- Include size references in prompts (5mm, 4cm, etc.)
- Use full_heart_reference for manual alignment in Unity

### Issue 2: Too many polygons (>100k total)

**Solution:**
- Request "low-poly" or "VR-optimized" in prompts
- Use Medium or Low polygon count setting
- Decimate in Blender if needed (Modifiers → Decimate, Ratio: 0.5)

### Issue 3: Materials look wrong in Unity

**Solution:**
- Extract textures in Import Settings
- Create custom PBR materials with:
  - Albedo color matching prompt
  - Emission for glow effects
  - Metallic: 0.0, Smoothness: 0.3
- Use MaterialPropertyBlock for runtime color changes

### Issue 4: Components are wrong scale

**Solution:**
```
1. Import full_heart_reference first
2. Measure its bounds in Unity (should be ~0.1-0.3 units)
3. Scale all components proportionally:
   scale = referenceHeight / componentHeight
4. Apply scale in Import Settings before instantiating
```

---

## Alternative: Free Heart Models

If Meshy.ai credits run out, use these free resources:

### Option 1: Sketchfab
- **URL:** https://sketchfab.com/search?q=human+heart&type=models&features=downloadable
- **License:** CC-BY (requires attribution)
- **Example:** "Anatomical Heart" by Renafox (24k polygons)

### Option 2: TurboSquid Free
- **URL:** https://www.turbosquid.com/Search/3D-Models/free/heart
- **Format:** FBX, OBJ
- **Note:** Lower quality, may need cleanup

### Option 3: Free3D
- **URL:** https://free3d.com/3d-models/heart
- **Format:** OBJ, FBX
- **Note:** Variable quality

### Blender Separation Workflow

If you get a single merged heart model:

1. **Import to Blender**
2. **Enter Edit Mode** (Tab)
3. **Select faces** for each region (Box Select, Circle Select)
4. **Separate by Selection** (P → Selection)
5. **Rename objects** to backend names (sa_node, ra, etc.)
6. **Export each** as individual FBX
   - File → Export → FBX
   - Selected Objects Only
   - Apply Scalings: FBX All

---

## Prompt Optimization Tips

### Tip 1: Be Specific About Size
```
❌ "small SA node"
✓ "SA node, 5mm diameter sphere"
```

### Tip 2: Request Clean Topology
```
❌ "3D heart SA node"
✓ "3D heart SA node, clean quad topology, VR-optimized"
```

### Tip 3: Specify Materials
```
❌ "blue SA node"
✓ "bright blue glowing material with emission, PBR textures"
```

### Tip 4: Use Negative Prompts
```
Negative: "cartoon, stylized, anime, low-poly icons, low quality, deformed,
           asymmetric, extra parts, missing parts, pixelated"
```

### Tip 5: Request Consistent Style
```
Add to all prompts: "medical textbook visualization, photorealistic,
                      anatomically accurate, no background"
```

---

## Budget-Friendly Strategy

If you have limited Meshy.ai credits (50 free/month):

### Priority Generation Order:
1. **full_heart_reference** (5 credits) - MUST HAVE
2. **sa_node** (3 credits) - small, critical
3. **av_node** (3 credits) - small, critical
4. **lv** (5 credits) - largest chamber, prominent
5. **rv** (5 credits) - second largest chamber

**Remaining components:** Use simplified Unity primitives:
- **Atria (RA/LA):** Unity Sphere scaled + deformed
- **Bundle branches (RBBB/LBBB):** Unity Cylinder scaled thin
- **Bundle of His:** Unity Cylinder
- **Purkinje:** Unity Line Renderer with branching

**Total Cost:** ~21 credits (leaves 29 for revisions)

---

## Expected Results

After completing this workflow, you'll have:

✓ **10 individual FBX files** with clean geometry
✓ **Consistent scale** across all components
✓ **Anatomically accurate positioning** in Unity
✓ **Each component** has CardiacRegionMarker script attached
✓ **Region names** match backend exactly
✓ **VR-optimized** polygon counts (<50k total)
✓ **Ready for real-time** color/glow updates from API

---

**Document Version:** 1.0
**Last Updated:** 2025-11-15
**Meshy.ai Free Credits:** 50/month
**Estimated Total Credits Needed:** 35-45 credits
