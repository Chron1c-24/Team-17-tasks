using System.Collections.Generic;
using UnityEngine;

public class ObjectRotator : MonoBehaviour
{
    public float rotationSpeed = 100f;
    private SelectionManager selectionManager;

    // List to store rotation values for each piece (in Euler angles)
    public List<Vector3> rotationValues = new List<Vector3>();

    void Start()
    {
        // Find the SelectionManager in the scene
        selectionManager = FindObjectOfType<SelectionManager>();
    }

    void Update()
    {
        // Only rotate if this is the selected object
        if (selectionManager != null && selectionManager.selectedObject == this)
        {
            // Rotate around Z-axis
            if (Input.GetKey(KeyCode.Q))
            {
                RotateLeftZ();
            }
            if (Input.GetKey(KeyCode.E))
            {
                RotateRightZ();
            }

            // Rotate around Y-axis
            if (Input.GetKey(KeyCode.A))
            {
                RotateLeftY();
            }
            if (Input.GetKey(KeyCode.D))
            {
                RotateRightY();
            }

            // Rotate around X-axis
            if (Input.GetKey(KeyCode.Z))
            {
                RotateLeftX();
            }
            if (Input.GetKey(KeyCode.C))
            {
                RotateRightX();
            }

            // Update the rotation values for this piece
            UpdateRotationValues();
        }
    }

    void RotateLeftZ()
    {
        transform.Rotate(Vector3.forward, rotationSpeed * Time.deltaTime, Space.World);
    }

    void RotateRightZ()
    {
        transform.Rotate(Vector3.forward, -rotationSpeed * Time.deltaTime, Space.World);
    }

    void RotateLeftY()
    {
        transform.Rotate(Vector3.up, rotationSpeed * Time.deltaTime, Space.World);
    }

    void RotateRightY()
    {
        transform.Rotate(Vector3.up, -rotationSpeed * Time.deltaTime, Space.World);
    }

    void RotateLeftX()
    {
        transform.Rotate(Vector3.right, rotationSpeed * Time.deltaTime, Space.World);
    }

    void RotateRightX()
    {
        transform.Rotate(Vector3.right, -rotationSpeed * Time.deltaTime, Space.World);
    }

    void UpdateRotationValues()
    {
        // Ensure the list has enough entries for each piece
        if (rotationValues.Count <= selectionManager.selectedObject.transform.GetSiblingIndex())
        {
            // Expand the list with zeroes to cover all objects up to the current piece index
            for (int i = rotationValues.Count; i <= selectionManager.selectedObject.transform.GetSiblingIndex(); i++)
            {
                rotationValues.Add(Vector3.zero);
            }
        }

        // Store the current rotation values (Euler angles) for the selected piece
        rotationValues[selectionManager.selectedObject.transform.GetSiblingIndex()] = transform.eulerAngles;
    }
}
