using UnityEngine;

public class BodyToggleInteraction : MonoBehaviour
{
    [Header("Models to Toggle")]
    [Tooltip("Drag the two 3D models you want to show/hide here")]
    public GameObject[] modelsToToggle;

    private bool areModelsVisible = false;

    void Start()
    {
        // Make sure models start as hidden
        Debug.Log("Starting BodyToggleInteraction - Initial setup");
        foreach (GameObject model in modelsToToggle)
        {
            if (model != null)
            {
                model.SetActive(false);
                Debug.Log("Set " + model.name + " to inactive at start");
            }
            else
            {
                Debug.LogWarning("One of the models in the array is null!");
            }
        }
        areModelsVisible = false;
    }

    // This method will be called by your VR interaction system
    public void OnRayInteract()
    {
        Debug.Log("OnRayInteract called! Current state: " + areModelsVisible);
        ToggleModels();
    }

    private void ToggleModels()
    {
        // Flip the state
        areModelsVisible = !areModelsVisible;
        
        Debug.Log("Toggling models to: " + areModelsVisible);

        // Apply the state to all models
        foreach (GameObject model in modelsToToggle)
        {
            if (model != null)
            {
                model.SetActive(areModelsVisible);
                Debug.Log("Set " + model.name + " to: " + areModelsVisible);
            }
        }
    }

    // If using XR Interaction Toolkit
    public void OnSelectEntered(UnityEngine.XR.Interaction.Toolkit.SelectEnterEventArgs args)
    {
        Debug.Log("OnSelectEntered called!");
        ToggleModels();
    }
}