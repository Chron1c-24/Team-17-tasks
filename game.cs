using UnityEngine;

public class CameraMovement : MonoBehaviour
{
    public float moveSpeed = 5.0f;       // Speed for moving with WASD
    public float zoomSpeed = 10.0f;      // Speed for zooming with the scroll wheel
    public float rotationSpeed = 100.0f; // Speed for rotating with the mouse

    public float minZoomDistance = 5.0f;  // Minimum zoom distance
    public float maxZoomDistance = 50.0f; // Maximum zoom distance

    private Vector3 cameraOffset;

    void Start()
    {
        // Initialize the offset as the initial position of the camera
        cameraOffset = transform.position;
    }

    void Update()
    {
        HandleMovement();
        HandleZoom();
        HandleRotation();
    }

    void HandleMovement()
    {
        // Movement using WASD keys
        float horizontal = Input.GetAxis("Horizontal");
        float vertical = Input.GetAxis("Vertical");
        Vector3 movement = new Vector3(horizontal, 0, vertical) * moveSpeed * Time.deltaTime;
        transform.Translate(movement, Space.World);
    }

    void HandleZoom()
    {
        // Zooming with mouse scroll wheel
        float scrollInput = Input.GetAxis("Mouse ScrollWheel");
        float distance = Vector3.Distance(transform.position, Vector3.zero);

        // Adjust the zoom within min and max limits
        if (scrollInput != 0.0f && (distance > minZoomDistance || scrollInput < 0) && (distance < maxZoomDistance || scrollInput > 0))
        {
            transform.Translate(Vector3.forward * scrollInput * zoomSpeed, Space.Self);
        }
    }

    void HandleRotation()
    {
        // Rotating when the right mouse button is held down
        if (Input.GetMouseButton(1))
        {
            float mouseX = Input.GetAxis("Mouse X") * rotationSpeed * Time.deltaTime;
            float mouseY = Input.GetAxis("Mouse Y") * rotationSpeed * Time.deltaTime;

            // Rotate around the y-axis (up) and the x-axis (horizontal)
            transform.RotateAround(Vector3.zero, Vector3.up, mouseX);
            transform.RotateAround(Vector3.zero, transform.right, -mouseY);
        }
    }
}
