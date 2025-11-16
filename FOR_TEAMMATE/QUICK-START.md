# Quick Start for Your Teammate

**Hi! Your teammate has prepared the ECG heart model for you to integrate into your VR scene.**

---

## Step 1: Get the Code

Run these commands in your terminal/command prompt:

```bash
# Clone the repository (if you don't have it yet)
git clone https://github.com/tyang4-ai/Immerse-the-Bay-Hackathon.git
cd Immerse-the-Bay-Hackathon

# Or if you already have it, just pull the latest changes
git checkout unity-project-upload
git pull origin unity-project-upload
```

**✓ You now have all the code!**

---

## Step 2: Copy Files to Your Project

**Copy these folders from the downloaded repo to YOUR Unity project:**

```
FROM Downloaded Repo → TO Your Unity Project:

Assets/Scripts/
├── ECGAPIClient.cs                  → YourProject/Assets/Scripts/
├── ECGDemoController.cs             → YourProject/Assets/Scripts/
├── API/ECGDataStructures.cs         → YourProject/Assets/Scripts/API/
├── Heart/ECGHeartController.cs      → YourProject/Assets/Scripts/Heart/
└── Journey/StorytellingJourneyController.cs → YourProject/Assets/Scripts/Journey/

Assets/Resources/ECGSamples/
├── synthetic_ecg_normal.json        → YourProject/Assets/Resources/ECGSamples/
├── synthetic_ecg_bradycardia.json   → YourProject/Assets/Resources/ECGSamples/
└── synthetic_ecg_tachycardia.json   → YourProject/Assets/Resources/ECGSamples/
```

**Also copy the entire Backend/ folder** to somewhere on your PC (doesn't need to be in Unity project).

---

## Step 3: Install Unity Package

**In YOUR Unity project:**

1. Open Window → Package Manager
2. Click the "+" button → "Add package by name"
3. Type: `com.unity.nuget.newtonsoft-json`
4. Click "Add"

**✓ Package installed!**

---

## Step 4: Start the Backend Server

**Open terminal/command prompt, navigate to the Backend folder you copied:**

```bash
cd Backend

# Start the Flask server
python ecg_api.py
```

**You should see:**
```
[INFO] Initializing HoloHuman XR Backend...
[INFO] ECG model loaded successfully
 * Running on http://127.0.0.1:5000
 * Running on http://192.168.X.X:5000
```

**Test it works:**
```bash
curl http://localhost:5000/health
```

Should return: `{"status": "healthy", "model_loaded": true}`

**✓ Backend server running!**

---

## Step 5: Add to Your Scene

**In YOUR Unity scene:**

1. **Create ECG API Client GameObject:**
   - Right-click in Hierarchy → Create Empty
   - Rename to: `ECGAPIClient`
   - Click "Add Component" → Search for `ECGAPIClient` → Add it
   - In Inspector:
     - Backend URL: `http://localhost:5000`
     - Timeout Seconds: `30`
     - Log Requests: ✓ (check this box)

2. **Add your heart model to the scene** (wherever you want it positioned)

3. **Attach ECGHeartController** (if using the 3D heart visualization):
   - Select your heart model GameObject
   - Click "Add Component" → Search for `ECGHeartController` → Add it
   - In Inspector:
     - Ecg Data File: Select `synthetic_ecg_normal` from dropdown

**✓ Scene setup complete!**

---

## Step 6: Test It!

**Press Play in Unity.**

**You should see in Console:**
```
[ECG API] Backend is healthy! Model loaded: True
[ECGDemoController] ✓ ECG loaded successfully: 4096 samples × 12 leads
[ECG API] Analysis complete: LBBB (5%)
[ECGDemoController] ✓ SUCCESS callback received!
```

**✓ IT WORKS!**

---

## What's Working

Your teammate already got this working and tested:
- ✅ Unity → Flask backend communication
- ✅ ECG data loading and analysis
- ✅ JSON parsing (all data structures match backend)
- ✅ UI updates with diagnosis and heart rate
- ✅ Error handling and logging

**All the hard debugging is done!** You just need to position the heart model in your scene and connect your UI elements.

---

## Integration Options

### Option A: Standalone Clickable Heart
- User clicks heart model
- Model analyzes ECG data
- Shows diagnosis floating above heart
- **Simplest option!**

### Option B: Connect to Your Existing UI
- You call the API from your own script
- Display results in your UI panels
- See `ECGDemoController.cs` for example code

### Option C: VR Journey Mode
- Guided tour through the heart
- Narrative storytelling
- Waypoint markers
- Atmosphere changes
- **Most immersive!**

---

## Need Help?

**Read these files (in the repo you downloaded):**

1. **TEAMMATE-INTEGRATION-GUIDE.md** ← Full detailed guide
2. **dev/active/unity-play-mode-testing-guide.md** ← Setup instructions
3. **dev/active/TROUBLESHOOTING-PLAY-MODE.md** ← If something goes wrong

**Or look at working example:**
- `Assets/Scripts/ECGDemoController.cs` - Shows how to call the API

---

## Common Issues

### "Backend not reachable"
**Fix:** Make sure Flask server is running: `python ecg_api.py`

### "Failed to parse ECG data"
**Fix:** Make sure Newtonsoft.Json package is installed (Step 3)

### Compilation errors
**Fix:** Check that all scripts are in correct folders (Step 2)

---

## Quest 2 Testing (Optional)

**If testing on Quest 2 VR headset:**

1. Find your PC's IP address: `ipconfig` (Windows) or `ifconfig` (Mac/Linux)
2. In Unity, select ECGAPIClient GameObject
3. Change Backend URL to: `http://192.168.X.X:5000` (your PC's IP)
4. Make sure PC and Quest 2 are on **same WiFi network**
5. Allow Python through Windows Firewall

---

## That's It!

The integration is **fully tested and working**. Your teammate spent ~2 hours debugging to make sure everything works perfectly.

Just follow the steps above and you'll have a working ECG heart model in your scene! 🎉

**Questions?** Check TEAMMATE-INTEGRATION-GUIDE.md for detailed explanations.

