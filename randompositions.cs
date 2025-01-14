using UnityEngine;

public class RandomPositioner : MonoBehaviour
{
    private Vector3 originalPosition; // Stores the correct position
    private Quaternion originalRotation; // Stores the correct rotation
    public float randomRange = 5f; // Adjust the range for random positioning
    public float randomRotationRange = 180f; // Adjust the range for random rotation (e.g., -180 to 180 degrees)

    void Start()
    {
        // Store the object's original position and rotation
        originalPosition = transform.position;
        originalRotation = transform.rotation;

        // Set a random starting position and rotation within the specified range
        RandomizePositionAndRotation();
    }

    void RandomizePositionAndRotation()
    {
        // Generate random position offsets within the range
        float randomX = Random.Range(-randomRange, randomRange);
        float randomY = Random.Range(0, randomRange);
        float randomZ = Random.Range(-randomRange, randomRange);

        // Apply the random offset to the object's original position
        transform.position = new Vector3(
            originalPosition.x + randomX,
            originalPosition.y + randomY,
            originalPosition.z + randomZ
        );

        // Generate random rotation offsets within the rotation range
        float randomRotX = Random.Range(-randomRotationRange, randomRotationRange);
        float randomRotY = Random.Range(-randomRotationRange, randomRotationRange);
        float randomRotZ = Random.Range(-randomRotationRange, randomRotationRange);

        // Apply the random rotation to the object's original rotation
        transform.rotation = Quaternion.Euler(
            originalRotation.eulerAngles.x + randomRotX,
            originalRotation.eulerAngles.y + randomRotY,
            originalRotation.eulerAngles.z + randomRotZ
        );
    }

    // Optional: Call this to reset the position and rotation to the original ones when needed
    public void ResetPositionAndRotation()
    {
        transform.position = originalPosition;
        transform.rotation = originalRotation;
    }
}
