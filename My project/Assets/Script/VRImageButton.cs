using UnityEngine;

public class VRImageButton : MonoBehaviour
{
    public GameObject myObject;
    public VRButtonManager buttonManager;
    public string controllerTag = "Controller";
    
    private bool isControllerInside = false;
    private bool wasButtonPressed = false;

    void Update()
    {
        if (isControllerInside)
        {
            bool buttonPressed = Input.GetMouseButtonDown(0) || Input.GetButtonDown("Fire1");

            if (buttonPressed && !wasButtonPressed)
            {
                ToggleObject();
                wasButtonPressed = true;
            }
            else if (!buttonPressed)
            {
                wasButtonPressed = false;
            }
        }
    }

    void OnTriggerEnter(Collider other)
    {
        if (other.CompareTag(controllerTag))
        {
            isControllerInside = true;
            Debug.Log("Controller entered: " + gameObject.name);
        }
    }

    void OnTriggerExit(Collider other)
    {
        if (other.CompareTag(controllerTag))
        {
            isControllerInside = false;
            wasButtonPressed = false;
            Debug.Log("Controller exited: " + gameObject.name);
        }
    }

    void ToggleObject()
    {
        if (buttonManager != null && myObject != null)
        {
            buttonManager.ToggleObject(myObject);
            Debug.Log("Toggled object: " + myObject.name);
        }
        else
        {
            Debug.LogError("Button Manager or My Object not assigned on " + gameObject.name);
        }
    }
}