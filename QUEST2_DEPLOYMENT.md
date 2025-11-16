# Quest 2 Deployment Guide

## Overview

This guide covers deploying your ECG heart visualization system to Meta Quest 2. The system requires network connectivity to your PC's Flask backend for ECG analysis.

---

## Prerequisites

- ✅ Meta Quest 2 with Developer Mode enabled
- ✅ USB-C cable
- ✅ PC and Quest 2 on the same WiFi network
- ✅ Unity project with ECG system working on PC

---

## Step 1: Enable Quest 2 Developer Mode

1. **Install Meta Quest App** on your phone (iOS/Android)
2. **Pair your Quest 2** with the phone app
3. **Create a Developer Organization:**
   - Go to: https://developer.oculus.com/manage/organizations/create/
   - Create an organization (free, just needs a name)
4. **Enable Developer Mode:**
   - In Meta Quest mobile app → **Menu → Devices**
   - Select your Quest 2
   - Scroll down to **Developer Mode**
   - Toggle it **ON**
5. **Restart your Quest 2**

---

## Step 2: Configure Network Settings

### 2a. Get Your PC's IP Address

Your PC's IP address: **10.32.86.82** (on Stanford network)

To verify or get updated IP:
```bash
ipconfig
```

Look for "Wireless LAN adapter" → "IPv4 Address"

### 2b. Configure Windows Firewall

**Option A: Run the automatic setup script (Recommended)**

1. **Right-click** on `quest2-setup.bat` (in project root)
2. Select **"Run as Administrator"**
3. Follow the prompts

**Option B: Manual firewall configuration**

1. Open **Windows Defender Firewall**
2. Click **Advanced Settings**
3. Click **Inbound Rules** → **New Rule**
4. Rule Type: **Port**
5. Protocol: **TCP**, Port: **5000**
6. Action: **Allow the connection**
7. Name: **"Flask ECG Backend"**
8. Click **Finish**

---

## Step 3: Update Unity Backend URL

1. **Open your Unity project**
2. **Select "ECG Heart System" GameObject**
3. Find the **ECGAPIClient** component in Inspector
4. Change **Backend URL** to:
   ```
   http://10.32.86.82:5000
   ```

   **Important:** Replace `10.32.86.82` with your actual PC IP if it's different!

---

## Step 4: Configure Unity Build Settings for Quest 2

### 4a. Switch to Android Platform

1. **File → Build Settings**
2. Select **Android** platform
3. Click **Switch Platform** (if not already on Android)
4. Wait for Unity to reimport assets

### 4b. Configure Player Settings

1. In Build Settings window, click **Player Settings**
2. Configure the following:

#### **Company & Product**
- Company Name: `YourName` (or keep default)
- Product Name: `Immerse-the-Bay Heart`

#### **XR Settings**
1. Go to **Edit → Project Settings → XR Plug-in Management**
2. Click **Android** tab (Android icon)
3. Enable **Oculus** checkbox
4. (Optional) Enable **OpenXR** checkbox

#### **Android Settings** (Player Settings → Android tab)
- **Minimum API Level:** 29 (Android 10.0) or higher
  - Your project is set to: **32** ✓
- **Scripting Backend:** IL2CPP ✓
- **Target Architectures:** ARM64 ✓ (already configured)
- **Graphics API:**
  - Remove Vulkan if present (for Quest 2 compatibility)
  - Use OpenGLES3 only

#### **Quality Settings** (for Quest 2 performance)
1. **Edit → Project Settings → Quality**
2. Select **Android** platform
3. Set quality level to **Medium** or **Low**
4. Disable **Shadows** or set to **Hard Shadows Only**
5. **Pixel Light Count:** 1-2 (you have 10 region lights, but they don't need to be pixel lights)

---

## Step 5: Connect Quest 2 to PC

1. **Put on Quest 2 headset**
2. **Connect USB-C cable** from PC to Quest 2
3. **In Quest 2 headset**, you'll see a prompt:
   - "Allow USB Debugging?"
   - Check **"Always allow from this computer"**
   - Click **OK**

### Verify Connection

In Unity:
1. **File → Build Settings**
2. Under "Run Device", you should see:
   - **Quest 2** or **Oculus Quest 2** listed

If not detected:
- Unplug and replug USB cable
- Restart Quest 2
- Try a different USB cable or port

---

## Step 6: Build and Deploy

### Option A: Build and Run (Recommended)

1. **File → Build Settings**
2. Make sure **Android** is selected
3. **Run Device:** Select **Quest 2**
4. Click **Build And Run**
5. Choose a filename (e.g., `HeartECG.apk`)
6. Unity will build and automatically install to Quest 2

### Option B: Build APK, Install Manually

1. **File → Build Settings**
2. Click **Build**
3. Save as `HeartECG.apk`
4. Install using ADB:
   ```bash
   adb install HeartECG.apk
   ```

---

## Step 7: Start Flask Backend

**CRITICAL:** The Flask backend must be running on your PC before using the app on Quest 2!

1. Open Command Prompt/Terminal
2. Navigate to backend folder:
   ```bash
   cd "C:\Users\22317\Immerse-the-Bay-Project\teammate-integration\Backend"
   ```
3. Start the server:
   ```bash
   python ecg_api.py
   ```
4. You should see:
   ```
   * Running on http://0.0.0.0:5000
   ```

**Keep this terminal window open!** The backend must stay running while using the Quest 2 app.

---

## Step 8: Test on Quest 2

1. **Put on Quest 2 headset**
2. **Open your app** from the Quest 2 library (under "Unknown Sources")
3. **Click on the heart**
4. **Check for ECG analysis:**
   - The 10 cardiac regions should glow with colors
   - Green = healthy
   - Yellow/Orange/Red = abnormalities detected

### Troubleshooting Network Connection

If the regions don't update or stay white:

1. **Check Flask backend is running** on PC (see Step 7)
2. **Check PC and Quest 2 are on same WiFi network**
3. **Verify backend URL** in Unity is correct: `http://10.32.86.82:5000`
4. **Test backend connectivity** from Quest 2:
   - Use Quest 2 browser
   - Navigate to: `http://10.32.86.82:5000/health`
   - Should show: `{"status": "healthy", ...}`

---

## Network Configuration Summary

```
┌─────────────┐                  ┌─────────────┐
│             │                  │             │
│  Quest 2    │  ◄───WiFi───►   │   PC        │
│             │                  │             │
│ Unity App   │                  │ Flask API   │
│ (Android)   │  http://IP:5000  │ (Python)    │
│             │                  │             │
└─────────────┘                  └─────────────┘
      │                                │
      │                                │
      └────────── Stanford WiFi ───────┘
           (10.32.x.x network)
```

**Key Points:**
- Quest 2 IP: Assigned by WiFi router (e.g., 10.32.x.x)
- PC IP: **10.32.86.82**
- Backend runs on: `http://0.0.0.0:5000` (listens on all interfaces)
- Unity connects to: `http://10.32.86.82:5000`

---

## Common Issues & Solutions

### Issue 1: "Connection refused" or timeout

**Cause:** Firewall blocking port 5000

**Solution:**
1. Run `quest2-setup.bat` as Administrator
2. OR temporarily disable Windows Firewall
3. OR manually add firewall rule (see Step 2b)

### Issue 2: Quest 2 not detected in Unity

**Cause:** USB debugging not enabled or driver issues

**Solution:**
1. Check Developer Mode is enabled on Quest 2
2. Reconnect USB cable
3. In Quest 2, approve USB debugging prompt
4. Try different USB cable/port
5. Install Oculus ADB drivers: https://developer.oculus.com/downloads/package/oculus-adb-drivers/

### Issue 3: App crashes on Quest 2

**Cause:** Performance issues or missing dependencies

**Solution:**
1. Check Unity Console for build errors
2. Reduce quality settings (Edit → Project Settings → Quality)
3. Disable shadows on region lights
4. Check IL2CPP build completed successfully

### Issue 4: Regions don't update colors

**Cause:** Network connectivity or backend not running

**Solution:**
1. Verify Flask backend is running (`python ecg_api.py`)
2. Check PC IP address hasn't changed (`ipconfig`)
3. Update Backend URL in Unity if IP changed
4. Test backend from Quest 2 browser: `http://10.32.86.82:5000/health`
5. Check Unity Console logs in Logcat:
   ```bash
   adb logcat -s Unity
   ```

### Issue 5: Poor performance / low FPS

**Cause:** Too many lights or complex rendering

**Solution:**
1. Reduce light range on cardiac regions (Inspector: Range = 1-2)
2. Disable shadows: Edit → Project Settings → Quality → Shadows = Off
3. Lower texture quality
4. Use Low/Medium quality preset for Android
5. Disable particle effects (optional)

---

## Performance Optimization Tips

### For Quest 2 (Mobile VR):

1. **Limit lights:**
   - Quest 2 struggles with many real-time lights
   - Consider using emissive materials instead of lights
   - Or reduce light range to 1-2 meters

2. **Reduce draw calls:**
   - Combine meshes where possible
   - Use texture atlases

3. **Target 72 FPS:**
   - Quest 2 native refresh rate is 72Hz
   - Use Unity Profiler to identify bottlenecks

4. **Optimize ECG data transfer:**
   - The system sends 4096×12 samples (49KB) to backend
   - Network latency on WiFi: ~50-200ms
   - Consider caching analysis results

---

## Advanced: Using Quest Link Instead of WiFi

If you have issues with WiFi connectivity, you can use Quest Link (wired connection):

1. **Enable Quest Link** in Quest 2
2. **Connect USB cable** (must be USB 3.0 or higher)
3. **Use localhost** in Unity:
   - Backend URL: `http://localhost:5000` (instead of IP)
4. **Build and test** via Quest Link

This eliminates network latency but requires the Quest 2 to stay tethered to PC.

---

## Deployment Checklist

Before deploying to Quest 2:

- [ ] Developer Mode enabled on Quest 2
- [ ] PC and Quest 2 on same WiFi network
- [ ] PC IP address confirmed: `10.32.86.82`
- [ ] Windows Firewall configured (port 5000 allowed)
- [ ] Unity Backend URL set to: `http://10.32.86.82:5000`
- [ ] Unity Build Settings → Android platform
- [ ] XR Plugin Management → Oculus enabled
- [ ] Quest 2 connected via USB and detected
- [ ] Flask backend running on PC
- [ ] Test backend health: `http://10.32.86.82:5000/health`

---

## Next Steps

Once deployed and working:

1. **Test different ECG samples** - Try bradycardia, tachycardia
2. **Add UI panels** - Display diagnosis text in VR
3. **Add electrical wave animation** - Visual signal propagation
4. **Optimize performance** - Reduce lights, use emissive materials
5. **Add hand tracking** - Use hand gestures instead of controllers

---

## Support & Resources

- **Meta Quest Developer Portal:** https://developer.oculus.com/
- **Unity XR Documentation:** https://docs.unity3d.com/Manual/XR.html
- **ADB Commands:** https://developer.android.com/studio/command-line/adb
- **Project Documentation:** See `INTEGRATION_STEPS.md`

---

**Generated with Claude Code**
