# Unity Play Mode Testing Guide
**Purpose:** Test Unity-Backend integration in Editor Play Mode
**Date:** 2025-11-16
**Backend:** http://localhost:5000 (running)

---

## Prerequisites ✅

- ✅ Unity Editor open with your scene
- ✅ Flask backend running at http://localhost:5000
- ✅ All compilation errors fixed (0 errors)
- ✅ TextMeshPro package installed
- ✅ Newtonsoft.Json installed

---

## Phase 1: Set Up ECGAPIClient (Backend Connection)

### Step 1.1: Create ECGAPIClient GameObject

**In Unity Hierarchy:**
1. Right-click in Hierarchy
2. Create Empty → Name it `ECGAPIClient`
3. Select `ECGAPIClient` GameObject

### Step 1.2: Add ECGAPIClient Script

**In Inspector (with ECGAPIClient selected):**
1. Click "Add Component"
2. Search for "ECGAPIClient"
3. Click to add the script

### Step 1.3: Configure ECGAPIClient Settings

**In Inspector, you should see:**

```
ECGAPIClient (Script)

Backend Configuration:
  Backend URL: http://localhost:5000    ← VERIFY THIS

Request Settings:
  Timeout Seconds: 30
  Log Requests: ✓ (checked)             ← KEEP CHECKED for testing
```

**Important:**
- For PC testing: Use `http://localhost:5000`
- For Quest 2 VR: Use `http://10.32.86.82:5000`

---

## Phase 2: Set Up Simple API Test (ECGDemoController)

### Step 2.1: Create UI Canvas

**In Unity Hierarchy:**
1. Right-click → UI → Canvas
2. This creates:
   - Canvas
   - EventSystem

3. Select Canvas, verify settings:
   - Render Mode: Screen Space - Overlay
   - Canvas Scaler: Scale With Screen Size

### Step 2.2: Create TextMeshPro UI Elements

**Create Diagnosis Text:**
1. Right-click Canvas → UI → Text - TextMeshPro
2. Rename to `DiagnosisText`
3. In Inspector (RectTransform):
   - Anchor: Top-Left
   - Pos X: 20, Pos Y: -20
   - Width: 400, Height: 100
4. In TextMeshPro component:
   - Font Size: 24
   - Text: "Waiting for analysis..."
   - Color: White

**Create Heart Rate Text:**
1. Right-click Canvas → UI → Text - TextMeshPro
2. Rename to `HeartRateText`
3. In Inspector (RectTransform):
   - Anchor: Top-Left
   - Pos X: 20, Pos Y: -140
   - Width: 400, Height: 100
4. In TextMeshPro component:
   - Font Size: 24
   - Text: "Heart Rate: --"
   - Color: White

**Create Status Text:**
1. Right-click Canvas → UI → Text - TextMeshPro
2. Rename to `StatusText`
3. In Inspector (RectTransform):
   - Anchor: Top-Left
   - Pos X: 20, Pos Y: -260
   - Width: 400, Height: 60
4. In TextMeshPro component:
   - Font Size: 18
   - Text: "Initializing..."
   - Color: Yellow

### Step 2.3: Create ECGDemoController GameObject

**In Unity Hierarchy:**
1. Right-click → Create Empty
2. Name it `ECGDemoController`
3. Select `ECGDemoController` GameObject

### Step 2.4: Add ECGDemoController Script

**In Inspector (with ECGDemoController selected):**
1. Click "Add Component"
2. Search for "ECGDemoController"
3. Click to add the script

### Step 2.5: Configure ECGDemoController

**In Inspector, you should see:**

```
ECGDemoController (Script)

ECG Data:
  Ecg Data File: None (TextAsset)       ← ASSIGN FILE HERE

UI:
  Diagnosis Text: None (TMP_Text)       ← DRAG DiagnosisText here
  Heart Rate Text: None (TMP_Text)      ← DRAG HeartRateText here
  Status Text: None (TMP_Text)          ← DRAG StatusText here
```

**Assign ECG Sample File:**
1. Click the circle next to "Ecg Data File"
2. Search for: `synthetic_ecg_normal`
3. Select it (should be in Assets/Resources/ECGSamples/)

**Assign UI Elements:**
1. Drag `DiagnosisText` from Hierarchy → "Diagnosis Text" field
2. Drag `HeartRateText` from Hierarchy → "Heart Rate Text" field
3. Drag `StatusText` from Hierarchy → "Status Text" field

---

## Phase 3: Run Play Mode Test

### Step 3.1: Verify Backend is Running

**Open a terminal and check:**
```bash
curl http://localhost:5000/health
```

**Expected output:**
```json
{
  "status": "healthy",
  "model_loaded": true
}
```

If backend is NOT running, restart it:
```bash
cd Backend
./venv/Scripts/python.exe ecg_api.py
```

### Step 3.2: Start Play Mode

**In Unity:**
1. Click the **Play** button (▶) at the top of Unity Editor
2. Unity should enter Play Mode (screen tints blue)

### Step 3.3: Watch the UI

**You should see the following sequence:**

**1. Initial State (0-1 seconds):**
```
StatusText: "Loading ECG data..."
```

**2. Data Loaded (1-2 seconds):**
```
StatusText: "Loaded 4096 samples × 12 leads"
```

**3. Analyzing (2-3 seconds):**
```
StatusText: "Analyzing ECG..."
```

**4. Results Displayed (3-5 seconds):**
```
DiagnosisText: "LBBB
                Confidence: 5%"

HeartRateText: "72.3 BPM
                Lead: II (Quality: 0.87)"

StatusText: "✓ Analysis complete (383ms)"
```

### Step 3.4: Check Console Logs

**Open Console Window (Window → General → Console)**

**Expected logs (in order):**

```
[ECG API] Backend is healthy! Model loaded: True
ECG loaded: 4096 samples × 12 leads
[ECG API] POST /api/ecg/analyze (mode: clinical_expert)
[ECG API] Analysis complete: LBBB (5%)
[ECG API] Heart rate: 72.3 BPM
[ECG API] Processing time: 383.0ms

=== ECG Analysis Results ===
Diagnosis: LBBB (5%)
Heart Rate: 72.3 BPM
Processing Time: 383.1ms

Clinical Interpretation:
[Full clinical text...]
```

---

## Phase 4: Verify Backend Logs

**Check your backend terminal/console:**

You should see:
```
2025-11-16 XX:XX:XX - werkzeug - INFO - 127.0.0.1 - - [16/Nov/2025 XX:XX:XX] "POST /api/ecg/analyze HTTP/1.1" 200 -
2025-11-16 XX:XX:XX - ecg_api - INFO - [REQ-XXXXXX] ECG analysis completed in XXX.XXms
```

---

## Troubleshooting

### Problem: "Backend not reachable" error

**Symptoms:**
- Console shows: `[ECG API] Backend not reachable: Connection refused`

**Solution:**
1. Stop Play Mode (▶ button)
2. Check backend is running: `curl http://localhost:5000/health`
3. If not running, restart backend:
   ```bash
   cd Backend
   ./venv/Scripts/python.exe ecg_api.py
   ```
4. Wait for "Running on http://127.0.0.1:5000" message
5. Try Play Mode again

### Problem: UI shows "Error: Missing required field: ecg_signal"

**Symptoms:**
- StatusText shows: "✗ Analysis failed"
- DiagnosisText shows: "Error: Missing required field: ecg_signal"

**Solution:**
1. Check you assigned the correct ECG file
2. File should be: `synthetic_ecg_normal` (NOT `sample_normal`)
3. The file should contain raw ECG signal data, not API response
4. Stop Play Mode, reassign the file, try again

### Problem: NullReferenceException for UI elements

**Symptoms:**
- Console shows: `NullReferenceException: Object reference not set to an instance of an object`
- UI text doesn't update

**Solution:**
1. Stop Play Mode
2. Select ECGDemoController GameObject
3. Verify all 3 UI fields are assigned (not "None")
4. Drag the TextMeshPro objects from Hierarchy to the fields
5. Try Play Mode again

### Problem: "Type or namespace 'TMPro' could not be found"

**Symptoms:**
- Compilation errors about TMPro

**Solution:**
1. In Unity: Window → Package Manager
2. Search for "TextMeshPro"
3. Click "Install" or "Import"
4. Wait for import to complete
5. Try Play Mode again

### Problem: JSON parsing error

**Symptoms:**
- Console shows: `JSON parsing error: ...`

**Solution:**
1. The ECG sample file might be corrupted
2. Try a different ECG file:
   - `synthetic_ecg_bradycardia` (50 BPM)
   - `synthetic_ecg_tachycardia` (110 BPM)
3. Check file exists: Assets/Resources/ECGSamples/synthetic_ecg_normal.json

---

## Expected Test Results

### ✅ Success Criteria

- [x] Play Mode starts without errors
- [x] Backend health check succeeds (Console log)
- [x] ECG data loads (4096×12 shown in StatusText)
- [x] API request sent (Console log: "POST /api/ecg/analyze")
- [x] Response received within 500ms
- [x] Diagnosis displayed (e.g., "LBBB")
- [x] Heart rate displayed (e.g., "72.3 BPM")
- [x] Status shows "✓ Analysis complete"

### 📊 Performance Metrics

Monitor these values:
- **Processing Time:** Should be < 500ms (shown in StatusText)
- **Frame Rate:** Should stay at 60+ FPS (Unity Stats window)
- **Memory Usage:** Should not increase significantly over time

---

## Next Steps After Successful Test

Once basic API test works:

1. **Test Different ECG Samples:**
   - Change "Ecg Data File" to `synthetic_ecg_bradycardia`
   - Press Play → Should show ~50 BPM
   - Change to `synthetic_ecg_tachycardia`
   - Press Play → Should show ~110 BPM

2. **Test ECGHeartController:**
   - Add your heart model to the scene
   - Attach ECGHeartController script
   - Configure region markers
   - Test region color visualization

3. **Test Beat Detection:**
   - Use `/api/ecg/beats` endpoint
   - Verify R-peak detection
   - Test timeline scrubbing

4. **Test Network Mode (Quest 2):**
   - Change Backend URL to `http://10.32.86.82:5000`
   - Build to Quest 2
   - Test from VR headset

---

## Quick Reference: Inspector Settings Checklist

### ECGAPIClient
- ✓ Backend URL: http://localhost:5000
- ✓ Timeout: 30
- ✓ Log Requests: checked

### ECGDemoController
- ✓ Ecg Data File: synthetic_ecg_normal
- ✓ Diagnosis Text: DiagnosisText (TMP)
- ✓ Heart Rate Text: HeartRateText (TMP)
- ✓ Status Text: StatusText (TMP)

### Canvas
- ✓ Render Mode: Screen Space - Overlay
- ✓ Canvas Scaler: Scale With Screen Size

---

## Resources

- Backend API Docs: `docs/backend-api-specification.md`
- Unity Integration Guide: `docs/unity-integration-guide.md`
- Test Results: `dev/active/test-results-2025-11-16.md`
- ECG Samples: `Assets/Resources/ECGSamples/`

---

**Ready to test?** Follow Phase 1 → Phase 2 → Phase 3 in order!
