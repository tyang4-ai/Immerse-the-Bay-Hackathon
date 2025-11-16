# ECG Color & Glow Animation Setup Guide

Your heart model will now change color and glow based on the actual ECG waveform data!

---

## What You Get

The heart will:
- **Change color** from dark red (resting) → bright yellow (peak activity)
- **Glow/emit light** that pulses with ECG amplitude
- **Flash brightly** at each heartbeat
- **Play in real-time** synchronized with actual ECG signal

---

## Setup (5 Steps)

### Step 1: Prepare Your Heart Model

**Your heart model MUST have a material with emission enabled:**

1. Select your heart model in the scene
2. Look at the Material in Inspector
3. **If using Standard Shader:**
   - Check "Emission" checkbox
   - Set Emission color to black initially (we'll control it via script)

4. **If using URP/Lit Shader:**
   - Scroll to "Emission"
   - Check "Emission" box
   - Set Emission Map to None
   - Set Emission Color to black

---

### Step 2: Add ECGColorGlowAnimator Component

**On your heart model GameObject:**

1. Select the heart model in Hierarchy
2. Click "Add Component"
3. Search for: `ECGColorGlowAnimator`
4. Add it

---

### Step 3: Configure Settings

**In the Inspector, configure ECGColorGlowAnimator:**

```
Heart Model:
  Heart Renderer: (auto-assigned or drag your heart's Renderer)

Color Mapping:
  Min Color: RGB(204, 76, 76)    // Dark red (resting)
  Max Color: RGB(255, 230, 51)   // Bright yellow (peak)
  Glow Color: RGB(255, 128, 51)  // Orange glow

Glow Intensity:
  Min Glow Intensity: 0.2   // Subtle glow at rest
  Max Glow Intensity: 3.5   // Bright flash at peak

ECG Settings:
  ECG Lead Index: 1         // Lead II (best for rhythm)
  Playback Speed: 1.0       // Real-time
  Loop Playback: ✓ (checked)
  Smoothing: 0.7            // Smooth color transitions
```

---

### Step 4: Connect to ECGHeartController

**On your GameObject with ECGHeartController:**

1. Select the GameObject (the one with ECGHeartController.cs)
2. In Inspector, find "Heart Visualization" section
3. Drag your heart model (with ECGColorGlowAnimator) to:
   - **Color Glow Animator** field

---

### Step 5: Test It!

**Press Play:**

1. Backend should be running: `python ecg_api.py`
2. Press Play in Unity
3. Watch the Console logs:
   ```
   [ECGColorGlow] Started ECG visualization on Lead 1
   [ECGColorGlow] ECG Lead 1 range: [-0.245, 1.523]
   ```
4. **Your heart should now be pulsing with colors!**

---

## Customization

### Change Colors

**Want different colors?**

1. Select heart model with ECGColorGlowAnimator
2. In Inspector, change:
   - **Min Color** - Color at rest (try blues, greens)
   - **Max Color** - Color at peak activity
   - **Glow Color** - Emission color

**Examples:**
- **Cool theme:** Min=Blue(0.3, 0.5, 1), Max=Cyan(0, 1, 1)
- **Fire theme:** Min=Red(0.8, 0.2, 0), Max=Yellow(1, 0.9, 0)
- **Medical theme:** Min=Pink(1, 0.8, 0.8), Max=Red(1, 0.3, 0.3)

### Adjust Glow Intensity

**Too bright? Too dim?**

- **Max Glow Intensity:**
  - 1.0 = Subtle glow
  - 3.5 = Moderate glow (recommended)
  - 8.0 = Very bright, dramatic

- **Min Glow Intensity:**
  - 0 = No glow at rest
  - 0.2 = Subtle ambient glow (recommended)
  - 1.0 = Always glowing

### Change Playback Speed

**Want faster/slower animation?**

- **Playback Speed:**
  - 0.5 = Half speed (slow motion)
  - 1.0 = Real-time (recommended)
  - 2.0 = Double speed (fast forward)

### Change ECG Lead

**Try different ECG leads:**

- **Lead Index: 0** = Lead I
- **Lead Index: 1** = Lead II (recommended - best rhythm)
- **Lead Index: 2** = Lead III
- **Lead Index: 6** = V1 (precordial lead)
- **Lead Index: 11** = V6

Different leads show different waveform shapes!

---

## How It Works

1. **ECG Signal → Color Mapping:**
   - Script reads ECG waveform (4096 samples at 400 Hz)
   - Normalizes amplitude to 0-1 range
   - Maps to color gradient (min → max)

2. **Real-Time Playback:**
   - Plays at 400 Hz sampling rate (2.5ms per sample)
   - Total duration: ~10.24 seconds per loop
   - Smooth interpolation for visual appeal

3. **Beat Highlighting:**
   - Backend provides exact beat timestamps
   - Quick flash at each detected heartbeat
   - Synced with actual ECG R-peaks

---

## Troubleshooting

### Heart Not Glowing

**Problem:** No glow visible

**Fix:**
1. Check material has Emission enabled
2. Increase Max Glow Intensity (try 5.0)
3. Make sure Glow Color is not black
4. Check "Enable Emission" in material settings

### Colors Not Changing

**Problem:** Heart stays one color

**Fix:**
1. Check Console for `[ECGColorGlow] Started ECG visualization`
2. Make sure Color Glow Animator field is assigned in ECGHeartController
3. Verify ECG data loaded: `[ECGHeartController] ECG loaded: 4096 samples × 12 leads`

### Animation Too Fast/Slow

**Problem:** Playback speed wrong

**Fix:**
- Adjust Playback Speed slider (try 0.5x or 2.0x)
- Check sampling rate is 400 Hz (shouldn't need to change)

### Choppy Animation

**Problem:** Color changes are jerky

**Fix:**
- Increase Smoothing slider (try 0.8 or 0.9)
- Check frame rate is stable (press Stats in Game view)

---

## Advanced: Beat Flash Only (No Continuous)

**Want flash ONLY at heartbeats, no continuous color change?**

1. Select heart model with ECGColorGlowAnimator
2. In Inspector:
   - Set Loop Playback: ✗ (unchecked)
3. The heart will only flash at beat timestamps

---

## Advanced: Static Color Based on Diagnosis

**Want to set color based on severity?**

**In your own script:**
```csharp
// Get animator
ECGColorGlowAnimator animator = heartModel.GetComponent<ECGColorGlowAnimator>();

// Set static color (0.0 = healthy green, 1.0 = severe red)
animator.SetDiagnosisColor(severity: 0.85f);
```

This stops the ECG playback and sets a static diagnostic color.

---

## What's Next?

**Now that you have color/glow working:**

1. **Try different color schemes** - Find what looks best in VR
2. **Adjust glow intensity** for your lighting setup
3. **Test on Quest 2** - Colors look different in VR headset
4. **Add region-specific colors** - Different parts glow different colors

**Optional enhancements:**
- Particle effects at peak activity
- Sound effects synchronized with beats
- UI panel showing live ECG waveform graph
- Timeline scrubber to jump to specific beats

---

## Quick Reference

**Key Scripts:**
- `ECGColorGlowAnimator.cs` - Main color/glow controller
- `ECGHeartController.cs` - Connects to backend API
- `HeartbeatPulseAnimator.cs` - Scale pulsing (different effect)

**Inspector Fields:**
- Heart Renderer → Your heart model's Renderer component
- Min/Max Color → Color gradient range
- Glow Intensity → Emission brightness range
- ECG Lead Index → Which ECG lead to visualize
- Playback Speed → Animation speed multiplier

**Console Logs to Check:**
```
[ECGColorGlow] Started ECG visualization on Lead 1
[ECGColorGlow] ECG Lead 1 range: [-0.245, 1.523]
[ECGColorGlow] Looping ECG visualization
```

---

**Your heart model should now be pulsing with realistic ECG-driven color and glow effects! 🎨✨**

