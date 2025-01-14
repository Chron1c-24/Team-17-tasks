using UnityEngine;
using UnityEngine.SceneManagement;
using System.Collections;

public class PartAssembly : MonoBehaviour
{
    public Transform[] snapTargets; // Array of positions for parts 1 to 6
    public GameObject winMessage; // Reference to the "You Win" message
    private int currentPart = 0; // Tracks the part currently to be placed
    private int count=0;

    void Start()
    {
        winMessage.SetActive(false); // Hide win message at the start
    }

    void Update()
    {
        // You could add any other updates here if needed (e.g., drag logic)
    }

    // Call this method when a part is released after dragging
    public void CheckPartPlacement(Transform part)
    {
        if (currentPart < snapTargets.Length)
        {
            // Check if the part is close enough to the current snap target
            if (Vector3.Distance(part.position, snapTargets[currentPart].position) < 1f) 
            {
                part.position = snapTargets[currentPart].position; // Snap part into place
                currentPart++; // Move to the next part
                count++;

                // If all parts are placed correctly, show the win message
                if (count == 6)
                {
                    ShowWinMessage();
                }
            }
        }
    }

    private void ShowWinMessage()
    {
        winMessage.SetActive(true); // Show the "You Win" message
	SceneManager.LoadScene("WinScene");
    }
}