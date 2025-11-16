# Quick Fix: No ECGDemoController Logs

## Problem
You see `[ECG API] Backend is healthy!` but NO logs from ECGDemoController

## Cause
ECGDemoController GameObject doesn't exist in your scene

## Solution (2 minutes)

### Step 1: Create ECGDemoController GameObject

**In Unity Hierarchy (Play Mode STOPPED):**
1. Right-click in Hierarchy
2. Create Empty
3. Name it: `ECGDemoController`

### Step 2: Add ECGDemoController Script

**With ECGDemoController selected:**
1. In Inspector, click "Add Component"
2. Search: `ECGDemoController`
3. Click to add the script

### Step 3: Assign ECG Data File

**In Inspector, under "ECG Data":**
1. Click the circle ⭕ next to "Ecg Data File"
2. Search: `synthetic_ecg_normal`
3. Double-click to select it

### Step 4: Assign UI Elements

**In Inspector, under "UI":**

**For Diagnosis Text:**
1. Drag `DiagnosisText` from Hierarchy → drop on "Diagnosis Text" field

**For Heart Rate Text:**
1. Drag `HeartRateText` from Hierarchy → drop on "Heart Rate Text" field

**For Status Text:**
1. Drag `StatusText` from Hierarchy → drop on "Status Text" field

### Step 5: Verify Setup

**Inspector should now show:**
```
ECGDemoController (Script)

ECG Data:
  Ecg Data File: synthetic_ecg_normal ✓

UI:
  Diagnosis Text: DiagnosisText (TextMeshProUGUI) ✓
  Heart Rate Text: HeartRateText (TextMeshProUGUI) ✓
  Status Text: StatusText (TextMeshProUGUI) ✓
```

### Step 6: Press Play

**Expected Console output:**
```
[ECG API] Backend is healthy! Model loaded: True
[ECGDemoController] Start() called
[ECGDemoController] Waiting for API client...
[ECGDemoController] API client found!
[ECGDemoController] Loading ECG data from file...
[ECGDemoController] ECG loaded: 4096 samples × 12 leads
[ECGDemoController] Starting ECG analysis...
[ECG API] POST /api/ecg/analyze (mode: clinical_expert)
```

---

## Still No Logs After This?

### Check Console Filter

**In Unity Console window (bottom):**
- Make sure "Collapse" is UNCHECKED ☐
- Make sure filter shows "All" or "Log" (not just Errors/Warnings)

### Check Script Execution Order

**If you see "[ECG API] Backend is healthy!" but nothing else:**

1. Stop Play Mode
2. Edit → Project Settings → Script Execution Order
3. Make sure ECGAPIClient runs before Default Time (should be automatic)
4. Try Play Mode again

---

## Expected Result

**UI should show:**
```
DiagnosisText:    LBBB
                  Confidence: 5%

HeartRateText:    72.3 BPM
                  Lead: II (Quality: 0.87)

StatusText:       ✓ Analysis complete (383ms)
```

**Console should show:**
- Health check ✓
- Demo controller start ✓
- API client found ✓
- ECG loaded ✓
- Analysis started ✓
- Results received ✓
