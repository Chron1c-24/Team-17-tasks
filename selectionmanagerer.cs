using UnityEngine;

public class SelectionManager : MonoBehaviour
{
    public ObjectRotator selectedObject;

    void Update()
    {
        if (Input.GetMouseButtonDown(0)) // Left mouse button to select
        {
            Ray ray = Camera.main.ScreenPointToRay(Input.mousePosition);
            RaycastHit hit;

            if (Physics.Raycast(ray, out hit))
            {
                // Check if the clicked object has the ObjectRotator component
                ObjectRotator rotator = hit.collider.GetComponent<ObjectRotator>();
                if (rotator != null)
                {
                    selectedObject = rotator; // Set the selected object
                }
            }
        }
    }
}
