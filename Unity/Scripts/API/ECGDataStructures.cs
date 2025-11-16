using System;
using System.Collections.Generic;

/// <summary>
/// C# data structures matching backend API response format
/// These classes mirror the JSON structure from Flask backend
/// Used for deserializing API responses with Newtonsoft.Json or Unity's JsonUtility
/// </summary>

// ============================================================================
// MAIN API RESPONSE STRUCTURES
// ============================================================================

/// <summary>
/// Complete ECG analysis response from /api/ecg/analyze endpoint
/// </summary>
[Serializable]
public class ECGAnalysisResponse
{
    public DiagnosisData diagnosis;
    public HeartRateData heart_rate;
    public Dictionary<string, RegionHealthData> region_health;
    public List<List<object>> activation_sequence;
    public string clinical_interpretation;
    public StorytellingResponse storytelling;
    public float processing_time_ms;
    public string request_id;
}

/// <summary>
/// Diagnosis data with top condition and probabilities
/// </summary>
[Serializable]
public class DiagnosisData
{
    public string top_condition;           // e.g., "1dAVb", "RBBB", "NSR"
    public float confidence;               // 0.0-1.0
    public List<ConditionProbability> top_conditions;
}

/// <summary>
/// Individual condition with probability
/// </summary>
[Serializable]
public class ConditionProbability
{
    public string condition;               // e.g., "RBBB"
    public float probability;              // 0.0-1.0
}

/// <summary>
/// Heart rate data with lead quality
/// </summary>
[Serializable]
public class HeartRateData
{
    public float bpm;                      // Beats per minute (e.g., 72.3)
    public string lead_used;               // e.g., "Lead_II", "Lead_V1"
    public float lead_quality;             // 0.0-1.0
}

// ============================================================================
// BEAT DETECTION RESPONSE
// ============================================================================

/// <summary>
/// Response from /api/ecg/beats endpoint
/// Contains all R-peak positions
/// </summary>
[Serializable]
public class BeatsResponse
{
    public List<int> r_peaks;              // Sample indices of R-peaks (e.g., [324, 736, 1148, ...])
    public int beat_count;                 // Total number of beats
    public float avg_rr_interval_ms;       // Average RR interval in milliseconds
    public float heart_rate_bpm;           // Calculated heart rate
    public string lead_used;               // Lead used for detection
    public string rhythm;                  // Rhythm classification (e.g., "regular", "irregular")
    public float lead_quality;             // Lead quality score (0.0-1.0)
}

// ============================================================================
// BEAT DETAIL RESPONSE
// ============================================================================

/// <summary>
/// Response from /api/ecg/beat/{index} endpoint
/// Contains detailed P-QRS-T interval information for specific beat
/// </summary>
[Serializable]
public class BeatDetailResponse
{
    public int beat_index;                 // Index of this beat (0-based)
    public BeatIntervals intervals;        // P-QRS-T intervals
    public List<string> annotations;       // Medical annotations (e.g., ["Normal sinus beat"])
    public RawSamples raw_samples;         // Raw ECG waveform samples
    public WaveformComponents waveform_components;
    public string lead_used;               // Lead used for analysis
}

/// <summary>
/// P-QRS-T interval measurements for a single beat
/// </summary>
[Serializable]
public class BeatIntervals
{
    public float pr_interval_ms;           // PR interval (normal: 120-200ms)
    public float qrs_duration_ms;          // QRS duration (normal: 60-120ms)
    public float qt_interval_ms;           // QT interval (normal: 350-450ms)
}

/// <summary>
/// Raw ECG samples for waveform visualization
/// </summary>
[Serializable]
public class RawSamples
{
    public List<float> lead_II;            // Lead II samples (primary)
    public List<float> lead_V1;            // Lead V1 samples (optional)
}

/// <summary>
/// P-QRS-T waveform component positions
/// Each component has [start_index, end_index]
/// </summary>
[Serializable]
public class WaveformComponents
{
    public List<int> p_wave;               // [start, end] sample indices
    public List<int> qrs_complex;          // [start, end] sample indices
    public List<int> t_wave;               // [start, end] sample indices
}

// ============================================================================
// SEGMENT ANALYSIS RESPONSE
// ============================================================================

/// <summary>
/// Response from /api/ecg/segment endpoint
/// Analyzes a specific time segment of ECG
/// </summary>
[Serializable]
public class SegmentAnalysisResponse
{
    public float start_time;               // Start time in seconds
    public float end_time;                 // End time in seconds
    public DiagnosisData diagnosis;
    public HeartRateData heart_rate;
    public int beat_count;                 // Beats in this segment
    public List<string> arrhythmias;       // Detected arrhythmias
}

/// <summary>
/// Alternative SegmentResponse structure (used by ECGAPIClient)
/// </summary>
[Serializable]
public class SegmentResponse
{
    public Segment segment;
    public float processing_time_ms;
}

[Serializable]
public class Segment
{
    public float start_ms;
    public float end_ms;
    public float duration_ms;
    public int beats_in_segment;
    public string rhythm_analysis;
    public List<Event> events;
    public string lead_used;
}

[Serializable]
public class Event
{
    public string type;
    public float time_ms;
}

// ============================================================================
// STORYTELLING RESPONSE
// ============================================================================
// NOTE: These may be duplicated in StorytellingJourneyController.cs
// If you get "duplicate definition" errors, remove the definitions from
// StorytellingJourneyController.cs and keep these

[Serializable]
public class StorytellingResponse
{
    public string narrative_text;
    public List<WaypointData> waypoints;
}

[Serializable]
public class WaypointData
{
    public string region_name;
    public string teaser_text;
}

// ============================================================================
// REGION HEALTH DATA
// ============================================================================
// NOTE: This may be duplicated in HeartRegionMapping.cs
// If you get "duplicate definition" error, remove the definition from
// HeartRegionMapping.cs and keep this one

[Serializable]
public class RegionHealthData
{
    public float severity;                 // 0.0 = healthy, 1.0 = critical
    public float[] color;                  // RGB array [R, G, B]
    public float activation_delay_ms;      // Activation timing in milliseconds
    public string[] affected_by;           // List of conditions affecting this region
}

// ============================================================================
// HEALTH CHECK RESPONSE
// ============================================================================

/// <summary>
/// Response from /api/health endpoint
/// </summary>
[Serializable]
public class HealthCheckResponse
{
    public string status;                  // "healthy"
    public string model_status;            // "loaded" or "error"
    public string api_mode;                // "anthropic" or "fallback"
}

/// <summary>
/// Alternative HealthResponse structure (used by ECGAPIClient)
/// </summary>
[Serializable]
public class HealthResponse
{
    public string status;
    public bool model_loaded;
    public bool simulation_mode;
    public CacheStats cache_stats;
}

[Serializable]
public class CacheStats
{
    public int hits;
    public int misses;
    public float hit_rate;
}

// ============================================================================
// ERROR RESPONSE
// ============================================================================

/// <summary>
/// Error response structure from backend
/// </summary>
[Serializable]
public class ErrorResponse
{
    public string error;                   // Error message
    public string error_id;                // Error ID for debugging
    public string request_id;              // Request ID for debugging
    public int status_code;                // HTTP status code
}

// ============================================================================
// REQUEST STRUCTURES
// ============================================================================

/// <summary>
/// Request payload for /api/ecg/analyze endpoint
/// </summary>
[Serializable]
public class ECGAnalyzeRequest
{
    public List<List<float>> ecg_signal;
    public string output_mode;
    public string region_focus;
}

// ============================================================================
// HELPER STRUCTURES FOR JSON PARSING
// ============================================================================

/// <summary>
/// Wrapper for ECG signal data during JSON parsing
/// Unity's JsonUtility can't parse root-level arrays, so we wrap them
/// </summary>
[Serializable]
public class ECGDataWrapper
{
    public ECGData data;
}

/// <summary>
/// Alternative wrapper name (ECGWrapper) for compatibility
/// </summary>
[Serializable]
public class ECGWrapper
{
    public ECGData data;
}

/// <summary>
/// ECG signal data structure
/// Contains 4096 samples × 12 leads
/// </summary>
[Serializable]
public class ECGData
{
    public List<List<float>> ecg_signal;   // [4096][12] array
}

// ============================================================================
// CONDITION NAME MAPPINGS
// ============================================================================

/// <summary>
/// Helper class for converting backend condition codes to readable names
/// </summary>
public static class ConditionNames
{
    private static readonly Dictionary<string, string> nameMap = new Dictionary<string, string>
    {
        { "1dAVb", "First Degree AV Block" },
        { "RBBB", "Right Bundle Branch Block" },
        { "LBBB", "Left Bundle Branch Block" },
        { "SB", "Sinus Bradycardia" },
        { "AF", "Atrial Fibrillation" },
        { "ST", "Sinus Tachycardia" },
        { "NSR", "Normal Sinus Rhythm" }
    };

    /// <summary>
    /// Convert backend code to readable name
    /// </summary>
    public static string GetReadableName(string code)
    {
        if (nameMap.ContainsKey(code))
            return nameMap[code];

        // Fallback: convert snake_case to Title Case
        return code.Replace("_", " ");
    }

    /// <summary>
    /// Get all condition codes
    /// </summary>
    public static string[] GetAllCodes()
    {
        return new string[] { "1dAVb", "RBBB", "LBBB", "SB", "AF", "ST", "NSR" };
    }
}

// ============================================================================
// COLOR SEVERITY MAPPINGS
// ============================================================================

/// <summary>
/// Helper class for severity-based color mapping
/// </summary>
public static class SeverityColors
{
    /// <summary>
    /// Get color based on severity (0.0-1.0)
    /// Green (healthy) → Yellow → Orange → Red (severe)
    /// </summary>
    public static UnityEngine.Color GetColorForSeverity(float severity)
    {
        if (severity < 0.3f)
            return UnityEngine.Color.green;      // Healthy: 0.0-0.3
        else if (severity < 0.6f)
            return UnityEngine.Color.yellow;     // Mild: 0.3-0.6
        else if (severity < 0.8f)
            return new UnityEngine.Color(1f, 0.5f, 0f); // Moderate: 0.6-0.8 (orange)
        else
            return UnityEngine.Color.red;        // Severe: 0.8-1.0
    }

    /// <summary>
    /// Convert backend RGB array [R, G, B] to Unity Color
    /// </summary>
    public static UnityEngine.Color FromRGBArray(float[] rgb)
    {
        if (rgb == null || rgb.Length < 3)
            return UnityEngine.Color.white;

        return new UnityEngine.Color(rgb[0], rgb[1], rgb[2]);
    }
}

// ============================================================================
// EXTENSION METHODS
// ============================================================================

/// <summary>
/// Extension methods for ECG data structures
/// </summary>
public static class ECGDataExtensions
{
    /// <summary>
    /// Check if diagnosis indicates healthy heart
    /// </summary>
    public static bool IsHealthy(this DiagnosisData diagnosis)
    {
        if (diagnosis == null) return true;

        // Consider healthy if top condition is NSR with high confidence
        if (diagnosis.top_condition == "NSR" && diagnosis.confidence > 0.7f)
            return true;

        // Or if all conditions have low probability
        foreach (var condition in diagnosis.top_conditions)
        {
            if (condition.probability > 0.5f)
                return false;
        }

        return true;
    }

    /// <summary>
    /// Check if heart rate is in normal range (60-100 BPM)
    /// </summary>
    public static bool IsNormalRange(this HeartRateData heartRate)
    {
        if (heartRate == null) return true;
        return heartRate.bpm >= 60f && heartRate.bpm <= 100f;
    }

    /// <summary>
    /// Get heart rate category
    /// </summary>
    public static string GetCategory(this HeartRateData heartRate)
    {
        if (heartRate == null) return "Unknown";

        if (heartRate.bpm < 60f)
            return "Bradycardia";
        else if (heartRate.bpm > 100f)
            return "Tachycardia";
        else
            return "Normal";
    }

    /// <summary>
    /// Check if QRS is wide (>120ms indicates bundle branch block)
    /// </summary>
    public static bool IsWideQRS(this BeatIntervals intervals)
    {
        if (intervals == null) return false;
        return intervals.qrs_duration_ms > 120f;
    }

    /// <summary>
    /// Check if PR interval is prolonged (>200ms indicates AV block)
    /// </summary>
    public static bool IsProlongedPR(this BeatIntervals intervals)
    {
        if (intervals == null) return false;
        return intervals.pr_interval_ms > 200f;
    }
}
