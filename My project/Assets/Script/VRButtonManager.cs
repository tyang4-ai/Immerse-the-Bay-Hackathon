using UnityEngine;

public class VRButtonManager : MonoBehaviour
{
    public GameObject[] allObjects = new GameObject[6];
    public GameObject defaultObject;
    
    private GameObject currentlyActiveObject = null;

    void Start()
    {
        foreach (GameObject obj in allObjects)
        {
            if (obj != null)
            {
                obj.SetActive(false);
            }
        }
        
        if (defaultObject != null)
        {
            defaultObject.SetActive(true);
            currentlyActiveObject = defaultObject;
        }
    }

    public void ToggleObject(GameObject objectToToggle)
    {
        if (currentlyActiveObject == objectToToggle)
        {
            objectToToggle.SetActive(false);
            currentlyActiveObject = null;
            
            if (defaultObject != null && defaultObject != objectToToggle)
            {
                defaultObject.SetActive(true);
                currentlyActiveObject = defaultObject;
            }
        }
        else
        {
            foreach (GameObject obj in allObjects)
            {
                if (obj != null)
                {
                    obj.SetActive(false);
                }
            }
            
            if (defaultObject != null)
            {
                defaultObject.SetActive(false);
            }
            
            objectToToggle.SetActive(true);
            currentlyActiveObject = objectToToggle;
        }
    }
}