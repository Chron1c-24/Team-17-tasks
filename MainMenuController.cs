using UnityEngine;
using UnityEngine.SceneManagement;

public class MainMenuController : MonoBehaviour
{
    // Method to start the game
    public void StartGame()
    {
        SceneManager.LoadScene("GameScene"); // Replace "GameScene" with the actual name of your game scene
    }

    // Method to exit the game
    public void ExitGame()
    {
        Debug.Log("Exiting Game"); // Log message to verify the Exit button is working in the editor
        Application.Quit();        // Quit the application (this works only in a built game, not in the editor)
    }
}
