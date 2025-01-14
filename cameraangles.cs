using UnityEngine;
using System.Collections;

public class CameraSwitcher : MonoBehaviour
{
    public Transform[] cameraAngles; // Assign different camera positions/angles in the Inspector
    public float switchSpeed = 2.0f; // Speed of the camera transition
    private bool isSwitching = false; // To prevent multiple transitions at the same time

    void Update()
    {
        if (!isSwitching)
        {
            if (Input.GetKeyDown(KeyCode.F)) // Press "1" to switch to the first angle
            {
                SwitchCameraAngle(0);
            }
            if (Input.GetKeyDown(KeyCode.S)) // Press "2" to switch to the second angle
            {
                SwitchCameraAngle(1);
            }
            if (Input.GetKeyDown(KeyCode.T)) // Press "3" to switch to the third angle
            {
                SwitchCameraAngle(2);
            }

            // Add more key conditions for additional camera angles if needed
        }
    }

    void SwitchCameraAngle(int index)
    {
        if (index >= 0 && index < cameraAngles.Length)
        {
            StartCoroutine(MoveToCameraAngle(cameraAngles[index]));
        }
        else
        {
            Debug.LogWarning("Invalid camera angle index.");
        }
    }

    IEnumerator MoveToCameraAngle(Transform target)
    {
        isSwitching = true;
        while (Vector3.Distance(transform.position, target.position) > 0.1f || Quaternion.Angle(transform.rotation, target.rotation) > 0.1f)
        {
            // Smoothly interpolate the camera's position and rotation
            transform.position = Vector3.Lerp(transform.position, target.position, Time.deltaTime * switchSpeed);
            transform.rotation = Quaternion.Lerp(transform.rotation, target.rotation, Time.deltaTime * switchSpeed);
            yield return null;
        }

        // Snap to the final position and rotation to avoid small discrepancies
        transform.position = target.position;
        transform.rotation = target.rotation;
        isSwitching = false;
    }
}
