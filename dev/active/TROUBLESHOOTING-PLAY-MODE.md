# Play Mode Troubleshooting Guide

## Issue: UI Not Updating, No API Calls

**Symptoms:**
- UI stays on "Loading ECG data..." or "Initializing..."
- No API calls in backend logs
- No Console errors

---

## Quick Fixes (Try These First)

### Fix 1: Verify ECGAPIClient GameObject Exists ✅

**In Unity Hierarchy:**
1. Look for GameObject named `ECGAPIClient`
2. If it doesn't exist:
   - Right-click Hierarchy → Create Empty
   - Name it `ECGAPIClient`
   - Select it → Inspector → Add Component → `ECGAPIClient`
   - Verify "Backend URL" = `http://localhost:5000`

### Fix 2: Check Script Execution Order

**Problem:** ECGDemoController might start before ECGAPIClient initializes

**Solution (FIXED):**
- Updated ECGDemoController.cs with `WaitForAPIClient()` coroutine
- Now waits up to 5 seconds for API client to be ready
- Will show clear error if API client not found

### Fix 3: Verify All Inspector Fields Assigned

**Select ECGDemoController GameObject in Hierarchy**

**In Inspector, verify:**
- ✓ Ecg Data File: `synthetic_ecg_normal` (NOT "None")
- ✓ Diagnosis Text: Assigned to DiagnosisText GameObject
- ✓ Heart Rate Text: Assigned to HeartRateText GameObject
- ✓ Status Text: Assigned to StatusText GameObject

**If any show "None":**
1. Stop Play Mode
2. Drag the appropriate GameObject from Hierarchy to the field
3. Try Play Mode again

---

## Detailed Debugging Steps

### Step 1: Check Console Logs

**Open Console (Window → General → Console)**

**Expected logs when working:**
```
[ECGDemoController] Start() called
[ECGDemoController] Waiting for API client...
[ECG API] Backend is healthy! Model loaded: True
[ECGDemoController] API client found!
[ECGDemoController] Loading ECG data from file...
[ECGDemoController] ECG loaded: 4096 samples × 12 leads
[ECGDemoController] Starting ECG analysis...
[ECG API] POST /api/ecg/analyze (mode: clinical_expert)
```

**If you see:**

#### Error: "ECGAPIClient not found!"
```
[ECGDemoController] ECGAPIClient not found! Make sure ECGAPIClient GameObject exists in scene.
```

**Solution:**
- You forgot to create ECGAPIClient GameObject
- Follow Fix 1 above

#### Error: "UI elements not assigned in Inspector!"
```
[ECGDemoController] UI elements not assigned in Inspector!
```

**Solution:**
- Follow Fix 3 above
- Make sure all 3 TextMeshPro fields are assigned

#### Error: "ECG Data File not assigned in Inspector!"
```
[ECGDemoController] ECG Data File not assigned in Inspector!
```

**Solution:**
- Select ECGDemoController GameObject
- In Inspector, click circle next to "Ecg Data File"
- Select `synthetic_ecg_normal`

#### Error: "Failed to load ECG data"
```
[ECGDemoController] Failed to load ECG data: <exception message>
```

**Solution:**
- The ECG file format might be wrong
- Try using `synthetic_ecg_normal` instead of `sample_normal`
- Check Assets/Resources/ECGSamples/ folder exists

---

### Step 2: Verify Backend is Running

**Check backend terminal/console:**

Should see:
```
 * Running on http://127.0.0.1:5000
 * Running on http://10.32.86.82:5000
```

**If backend is NOT running:**
```bash
cd Backend
./venv/Scripts/python.exe ecg_api.py
```

**Test backend manually:**
```bash
curl http://localhost:5000/health
```

Should return:
```json
{
  "status": "healthy",
  "model_loaded": true
}
```

---

### Step 3: Check Script Compilation

**Bottom-right of Unity Editor:**

Should show: `0 Errors` and `0 Warnings`

**If you see errors:**
1. Stop Play Mode
2. Fix all compilation errors first
3. Wait for Unity to finish recompiling
4. Try Play Mode again

---

### Step 4: Verify Scene Setup

**In Hierarchy, you should have:**
```
ECGAPIClient (with ECGAPIClient.cs script)
ECGDemoController (with ECGDemoController.cs script)
Canvas
  ├── DiagnosisText (TextMeshPro)
  ├── HeartRateText (TextMeshPro)
  └── StatusText (TextMeshPro)
EventSystem
```

**Missing GameObjects?**
- Follow the setup guide in unity-play-mode-testing-guide.md
- Phase 1 and Phase 2 sections

---

## Advanced Debugging

### Enable Verbose Logging

**In ECGAPIClient GameObject Inspector:**
- ✓ Check "Log Requests"

**This will show:**
- Every API request URL and method
- Response parsing status
- Processing times

### Check Network Traffic

**Windows Command Prompt:**
```bash
curl -v http://localhost:5000/health
```

**Should show:**
```
< HTTP/1.1 200 OK
< Content-Type: application/json
{
  "status": "healthy",
  "model_loaded": true
}
```

**If connection refused:**
- Backend is not running
- Restart backend: `cd Backend && ./venv/Scripts/python.exe ecg_api.py`

---

## Common Mistakes

### ❌ Wrong ECG File Format
**Problem:** Using `sample_normal.json` instead of `synthetic_ecg_normal.json`

**Symptom:** Error "Missing required field: ecg_signal"

**Solution:**
- `sample_*.json` = API response examples (NOT raw ECG data)
- `synthetic_ecg_*.json` = Raw ECG signal data (CORRECT)

### ❌ Missing Newtonsoft.Json Package
**Problem:** Newtonsoft.Json not installed

**Symptom:** Compilation error about JsonConvert

**Solution:**
1. Window → Package Manager
2. + → Add package from git URL
3. Enter: `com.unity.nuget.newtonsoft-json`
4. Click Add

### ❌ Script Execution Order
**Problem:** ECGDemoController runs before ECGAPIClient Awake()

**Symptom:** apiClient is null

**Solution:** (ALREADY FIXED)
- Updated ECGDemoController to wait for API client
- Uses `WaitForAPIClient()` coroutine with 5s timeout

---

## Still Not Working?

### Create Minimal Test Scene

1. **File → New Scene**
2. **Save as "TestAPI"**
3. **Add only:**
   - ECGAPIClient GameObject
   - ECGDemoController GameObject
   - Canvas with 3 TextMeshPro elements
4. **Assign all Inspector fields**
5. **Press Play**

**If this works:**
- Problem is in your original scene (conflicting scripts?)

**If this still doesn't work:**
- Check Console for errors
- Share Console output for further debugging

---

## Console Output Reference

### ✅ Successful Test Run

```
[ECGDemoController] Start() called
[ECGDemoController] Waiting for API client...
[ECG API] Backend is healthy! Model loaded: True
[ECGDemoController] API client found!
[ECGDemoController] Loading ECG data from file...
[ECGDemoController] ECG loaded: 4096 samples × 12 leads
[ECGDemoController] Starting ECG analysis...
[ECG API] POST /api/ecg/analyze (mode: clinical_expert)
[ECG API] Analysis complete: LBBB (5%)
[ECG API] Heart rate: 72.3 BPM
[ECG API] Processing time: 383.0ms
=== ECG Analysis Results ===
Diagnosis: LBBB (5%)
Heart Rate: 72.3 BPM
Processing Time: 383.1ms
```

### ❌ Failed - API Client Missing

```
[ECGDemoController] Start() called
[ECGDemoController] Waiting for API client...
[ECGDemoController] ECGAPIClient not found! Make sure ECGAPIClient GameObject exists in scene.
```

### ❌ Failed - Backend Not Running

```
[ECGDemoController] Start() called
[ECGDemoController] Waiting for API client...
[ECG API] Backend not reachable: Connection refused
[ECG API] Make sure Flask server is running at http://localhost:5000
```

---

## Latest Issue: Response Parsed But Callback Not Invoked (2025-11-16)

**Symptoms:**
- Log shows: `[ECG API] ✓ Response parsed successfully!`
- But NO callback invocation logs appear
- UI never updates with results
- Backend logs show successful 200 OK response

**Investigation:**
- Added debug logging to track execution flow
- Code execution stops inside `if (logRequests)` block
- Likely exception when accessing response fields

**Fix Applied:**
- Wrapped logging in try-catch to catch silent exceptions
- Added null check for onSuccess delegate
- Will reveal exact failure point

**Next Steps:**
1. Run Play Mode again
2. Check Console for new debug messages:
   - "Starting to log response details..."
   - "Exception while logging response: ..."
   - "onSuccess is: NULL" or "NOT NULL"

---

## Quick Checklist

Before pressing Play:

- [ ] ECGAPIClient GameObject exists in scene
- [ ] ECGAPIClient.cs script attached
- [ ] Backend URL = `http://localhost:5000`
- [ ] ECGDemoController GameObject exists
- [ ] ECGDemoController.cs script attached
- [ ] Ecg Data File assigned (synthetic_ecg_normal)
- [ ] All 3 UI TextMeshPro fields assigned
- [ ] Backend Flask server running
- [ ] 0 compilation errors in Unity
- [ ] Console window open to see logs

---

**Updated:** 2025-11-16 03:05
**Version:** 2.0 (with WaitForAPIClient fix)
