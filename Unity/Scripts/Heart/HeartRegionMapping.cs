using UnityEngine;
using System.Collections.Generic;

/// <summary>
/// Maps backend cardiac region names to Unity GameObjects
/// Maintains a centralized registry of all 10 cardiac region markers
/// Provides lookup functionality for ECGHeartController
/// </summary>
public class HeartRegionMapping : MonoBehaviour
{
    [System.Serializable]
    public class HeartRegion
    {
        [Tooltip("Backend region name (must match exactly)")]
        public string regionName;

        [Tooltip("GameObject with CardiacRegionMarker component")]
        public GameObject regionObject;

        [Tooltip("Material to modify for glow effect (optional)")]
        public Material regionMaterial;

        [Tooltip("Particle system for electrical effect (optional)")]
        public ParticleSystem electricalEffect;
    }

    [Header("10 Cardiac Regions")]
    [Tooltip("Drag all 10 region markers here in Inspector")]
    [SerializeField] private HeartRegion[] heartRegions = new HeartRegion[10];

    // Lookup dictionary for fast region access
    private Dictionary<string, CardiacRegionMarker> regionLookup = new Dictionary<string, CardiacRegionMarker>();

    void Awake()
    {
        InitializeRegionLookup();
    }

    void Start()
    {
        ValidateRegions();
    }

    /// <summary>
    /// Build lookup dictionary for fast region access
    /// </summary>
    private void InitializeRegionLookup()
    {
        regionLookup.Clear();

        foreach (var region in heartRegions)
        {
            if (region.regionObject != null)
            {
                CardiacRegionMarker marker = region.regionObject.GetComponent<CardiacRegionMarker>();
                if (marker != null)
                {
                    // Use regionName from marker (not from HeartRegion)
                    string key = marker.regionName;
                    if (!regionLookup.ContainsKey(key))
                    {
                        regionLookup[key] = marker;
                        Debug.Log($"[HeartRegionMapping] Registered region: {key}");
                    }
                    else
                    {
                        Debug.LogWarning($"[HeartRegionMapping] Duplicate region name: {key}");
                    }
                }
                else
                {
                    Debug.LogError($"[HeartRegionMapping] Missing CardiacRegionMarker component on {region.regionObject.name}");
                }
            }
        }

        Debug.Log($"[HeartRegionMapping] Initialized {regionLookup.Count}/10 regions");
    }

    /// <summary>
    /// Validate that all 10 required regions are configured
    /// </summary>
    private void ValidateRegions()
    {
        string[] requiredRegions = new string[]
        {
            "sa_node", "ra", "la", "av_node", "bundle_his",
            "rbbb", "lbbb", "purkinje", "rv", "lv"
        };

        int missingCount = 0;
        foreach (string regionName in requiredRegions)
        {
            if (!regionLookup.ContainsKey(regionName))
            {
                Debug.LogError($"[HeartRegionMapping] Missing required region: {regionName}");
                missingCount++;
            }
        }

        if (missingCount == 0)
        {
            Debug.Log("[HeartRegionMapping] ✓ All 10 cardiac regions configured correctly");
        }
        else
        {
            Debug.LogError($"[HeartRegionMapping] ✗ {missingCount} regions missing! Check Inspector.");
        }
    }

    /// <summary>
    /// Get CardiacRegionMarker by backend region name
    /// </summary>
    /// <param name="regionName">Backend region name (e.g., "sa_node", "rbbb")</param>
    /// <returns>CardiacRegionMarker or null if not found</returns>
    public CardiacRegionMarker GetRegion(string regionName)
    {
        if (regionLookup.ContainsKey(regionName))
        {
            return regionLookup[regionName];
        }

        Debug.LogWarning($"[HeartRegionMapping] Region not found: {regionName}");
        return null;
    }

    /// <summary>
    /// Get all region markers as array
    /// </summary>
    public CardiacRegionMarker[] GetAllRegions()
    {
        CardiacRegionMarker[] regions = new CardiacRegionMarker[regionLookup.Count];
        regionLookup.Values.CopyTo(regions, 0);
        return regions;
    }

    /// <summary>
    /// Get region position by name (for waypoint placement)
    /// </summary>
    public Vector3 GetRegionPosition(string regionName)
    {
        CardiacRegionMarker region = GetRegion(regionName);
        if (region != null)
        {
            return region.GetPosition();
        }

        Debug.LogWarning($"[HeartRegionMapping] Cannot get position for region: {regionName}");
        return Vector3.zero;
    }

    /// <summary>
    /// Update all regions with health data from backend
    /// </summary>
    /// <param name="regionHealthData">Dictionary of region_name -> health data</param>
    public void UpdateAllRegions(Dictionary<string, RegionHealthData> regionHealthData)
    {
        foreach (var kvp in regionHealthData)
        {
            string regionName = kvp.Key;
            RegionHealthData healthData = kvp.Value;

            CardiacRegionMarker region = GetRegion(regionName);
            if (region != null)
            {
                // Convert backend RGB array to Unity Color
                Color regionColor = new Color(
                    healthData.color[0], // R
                    healthData.color[1], // G
                    healthData.color[2]  // B
                );

                // Update region visualization
                region.UpdateVisualization(healthData.severity, regionColor);
            }
        }

        Debug.Log($"[HeartRegionMapping] Updated {regionHealthData.Count} regions with health data");
    }

    /// <summary>
    /// Reset all regions to healthy state (green, no glow)
    /// </summary>
    public void ResetAllRegions()
    {
        foreach (var marker in regionLookup.Values)
        {
            marker.UpdateVisualization(0f, Color.green);
        }

        Debug.Log("[HeartRegionMapping] Reset all regions to healthy state");
    }

    /// <summary>
    /// Highlight a specific region (for waypoint focus)
    /// </summary>
    public void HighlightRegion(string regionName, bool enable)
    {
        CardiacRegionMarker region = GetRegion(regionName);
        if (region != null)
        {
            region.Highlight(enable);
        }
    }

    // Visualize region connections in Scene view
    void OnDrawGizmos()
    {
        if (!Application.isPlaying || regionLookup.Count == 0)
            return;

        // Draw lines showing electrical conduction pathway
        // SA node → Atria → AV node → Bundle of His → Branches → Purkinje → Ventricles

        Gizmos.color = Color.yellow;

        // SA node to atria
        DrawConnection("sa_node", "ra");
        DrawConnection("sa_node", "la");

        // Atria to AV node
        DrawConnection("ra", "av_node");
        DrawConnection("la", "av_node");

        // AV node to Bundle of His
        DrawConnection("av_node", "bundle_his");

        // Bundle of His to bundle branches
        DrawConnection("bundle_his", "rbbb");
        DrawConnection("bundle_his", "lbbb");

        // Bundle branches to Purkinje
        DrawConnection("rbbb", "purkinje");
        DrawConnection("lbbb", "purkinje");

        // Purkinje to ventricles
        DrawConnection("purkinje", "rv");
        DrawConnection("purkinje", "lv");
    }

    private void DrawConnection(string from, string to)
    {
        CardiacRegionMarker fromRegion = GetRegion(from);
        CardiacRegionMarker toRegion = GetRegion(to);

        if (fromRegion != null && toRegion != null)
        {
            Gizmos.DrawLine(fromRegion.GetPosition(), toRegion.GetPosition());
        }
    }
}

/// <summary>
/// Region health data structure (matches backend response)
/// </summary>
[System.Serializable]
public class RegionHealthData
{
    public float severity;           // 0.0 = healthy, 1.0 = critical
    public float[] color;            // RGB array [R, G, B]
    public float activation_delay_ms; // Activation timing in milliseconds
    public string[] affected_by;     // List of conditions affecting this region
}
