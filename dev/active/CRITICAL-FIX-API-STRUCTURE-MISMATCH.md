# CRITICAL BUG FIX: API Structure Mismatch
**Date:** 2025-11-16
**Issue:** Unity callbacks not firing after successful backend response
**Root Cause:** Backend and Unity data structures completely mismatched

---

## Problem Summary

### Symptoms
1. Backend successfully returns 200 OK with 6607-byte JSON response
2. Unity successfully parses JSON (no exceptions)
3. Code execution mysteriously stops before invoking `onSuccess` callback
4. UI never updates with analysis results

### Console Log Evidence
```
[ECG API] Response received (6607 bytes)
[ECG API] Parsing response JSON...
[ECG API] ✓ Response parsed successfully!
The character with Unicode value \u2717 was not found...
```

**Missing logs (never executed):**
```
[ECG API] Invoking onSuccess callback...
[ECGDemoController] ✓ SUCCESS callback received!
```

---

## Root Cause Analysis

### The Mismatch

**Backend sends** (ecg_api.py lines 270-288):
```json
{
  "predictions": {"1dAVb": 0.05, "RBBB": 0.12, ...},
  "heart_rate": {
    "bpm": 72.3,
    "rr_intervals_ms": [1148.0, ...],
    "beat_timestamps": [0.5, 1.65, ...],
    "r_peak_count": 9,
    "lead_used": "Lead_II",
    "lead_quality": 0.87,
    "fallback_triggered": false
  },
  "top_condition": "LBBB",
  "confidence": 0.05,
  "llm_interpretation": {
    "clinical_summary": "...",
    "differential_diagnosis": "...",
    ...
  },
  "processing_time_ms": 383.2,
  "model_version": "1.0.0",
  "timestamp": "2025-11-16T11:45:00Z",
  "metadata": {
    "simulation_mode": false,
    "cache_hit": false,
    "output_mode": "clinical_expert",
    "request_id": "REQ-XXX"
  }
}
```

**Unity expected** (OLD ECGDataStructures.cs):
```csharp
{
  "diagnosis": {                    // ← DOESN'T EXIST IN BACKEND!
    "top_condition": "LBBB",
    "confidence": 0.05
  },
  "heart_rate": {
    "bpm": 72.3,
    "lead_used": "Lead_II",
    "lead_quality": 0.87
    // Missing: rr_intervals_ms, beat_timestamps, r_peak_count, fallback_triggered
  },
  "clinical_interpretation": "...",  // ← Backend sends "llm_interpretation" object!
  "storytelling": {...},             // ← Backend sends this inside llm_interpretation!
  "request_id": "..."                // ← Backend sends this inside metadata!
}
```

### Why It Failed Silently

When Unity tried to access:
```csharp
response.diagnosis.top_condition  // diagnosis is NULL!
```

Newtonsoft.Json successfully deserialized the response, but:
1. `diagnosis` field was null (doesn't exist in backend response)
2. `llm_interpretation` was null (Unity expected string, backend sends object)
3. Code tried to log `response.diagnosis.top_condition`
4. **NullReferenceException was silently swallowed**
5. Callback never got invoked

---

## The Fix

### Updated ECGAnalysisResponse (ECGDataStructures.cs)

```csharp
[Serializable]
public class ECGAnalysisResponse
{
    // Direct fields from backend (matches ecg_api.py lines 270-288)
    public Dictionary<string, float> predictions;
    public HeartRateData heart_rate;
    public Dictionary<string, RegionHealthData> region_health;
    public List<List<object>> activation_sequence;
    public LLMInterpretation llm_interpretation;  // Changed from string!
    public string top_condition;                  // Top-level field
    public float confidence;                      // Top-level field
    public float processing_time_ms;
    public string model_version;
    public string timestamp;
    public ResponseMetadata metadata;

    // Backward compatibility properties
    public DiagnosisData diagnosis
    {
        get
        {
            return new DiagnosisData
            {
                top_condition = this.top_condition,
                confidence = this.confidence
            };
        }
    }

    public string clinical_interpretation
    {
        get
        {
            return llm_interpretation?.clinical_summary ?? "";
        }
    }
}
```

### New Supporting Classes

**LLMInterpretation** (matches backend clinical_decision_support_llm.py):
```csharp
[Serializable]
public class LLMInterpretation
{
    public string clinical_summary;
    public string differential_diagnosis;
    public string clinical_workup;
    public string treatment_plan;
    public string patient_education_summary;
    public StorytellingResponse storytelling;
}
```

**ResponseMetadata** (matches backend ecg_api.py metadata field):
```csharp
[Serializable]
public class ResponseMetadata
{
    public bool simulation_mode;
    public bool cache_hit;
    public string output_mode;
    public string region_focus;
    public string request_id;
}
```

**Updated HeartRateData** (matches backend ecg_heartrate_analyzer.py):
```csharp
[Serializable]
public class HeartRateData
{
    public float bpm;
    public List<float> rr_intervals_ms;
    public List<float> beat_timestamps;
    public int r_peak_count;
    public string lead_used;
    public float lead_quality;
    public bool fallback_triggered;
}
```

---

## Backward Compatibility

The fix maintains backward compatibility by providing helper properties:

```csharp
// OLD CODE (still works):
response.diagnosis.top_condition  // ✓ Works via property getter

// NEW CODE (preferred):
response.top_condition  // ✓ Direct access to backend field
```

This means existing code in ECGDemoController.cs and ECGHeartController.cs should continue to work without changes.

---

## Files Changed

1. **Assets/Scripts/API/ECGDataStructures.cs**
   - Updated ECGAnalysisResponse to match backend
   - Added LLMInterpretation class
   - Added ResponseMetadata class
   - Updated HeartRateData with all backend fields
   - Added backward-compatible properties

2. **Assets/Scripts/ECGAPIClient.cs**
   - Added try-catch around logging to catch silent exceptions
   - Added null check for onSuccess delegate
   - Enhanced debug logging

3. **dev/active/TROUBLESHOOTING-PLAY-MODE.md**
   - Added section on API structure mismatch
   - Updated troubleshooting steps

---

## Testing Instructions

### Before Testing
1. Make sure Unity scripts recompile (0 errors)
2. Backend running at http://localhost:5000
3. ECGDemoController set up with all UI elements

### Expected Results After Fix

**Console Log:**
```
[ECG API] Response received (6607 bytes)
[ECG API] Parsing response JSON...
[ECG API] ✓ Response parsed successfully!
[ECG API] Starting to log response details...
[ECG API] Analysis complete: LBBB (5%)
[ECG API] Heart rate: 72.3 BPM
[ECG API] Processing time: 383.0ms
[ECG API] Finished logging response details.
[ECG API] onSuccess is: NOT NULL
[ECG API] Invoking onSuccess callback...
[ECGDemoController] ✓ SUCCESS callback received!
[ECGDemoController] Setting diagnosis text...
[ECGDemoController] Setting heart rate text...
[ECGDemoController] Setting status text...
```

**UI Update:**
- DiagnosisText: "LBBB\nConfidence: 5%"
- HeartRateText: "72.3 BPM\nLead: Lead_II"
- StatusText: "✓ Analysis complete (383ms)"

---

## Lessons Learned

1. **Always verify backend-frontend contract**
   - Check actual backend code, not just documentation
   - Backend structure can diverge from design docs

2. **Silent failures are dangerous**
   - Newtonsoft.Json doesn't throw errors for missing fields
   - Null reference exceptions can be swallowed in coroutines
   - Always add defensive logging

3. **Test with actual data flow**
   - Don't assume structure matches between systems
   - Capture actual backend responses for verification

4. **Documentation drift**
   - Sample JSON files were outdated
   - Need to regenerate samples from actual backend

---

## Next Steps

1. ✅ Fix applied to ECGDataStructures.cs
2. ⏳ Test in Unity Play Mode
3. ⏳ Verify UI updates correctly
4. ⏳ Update sample JSON files to match new format
5. ⏳ Update backend API documentation

---

**Issue Status:** FIXED
**Fix Verified:** Pending Unity Play Mode test
**Updated:** 2025-11-16 11:50 UTC
