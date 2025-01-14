using UnityEngine;
using UnityEngine.SceneManagement;

public class WinScene : MonoBehaviour
{
    // Method to start the game
    public void PlayAgain()
    {
        SceneManager.LoadScene("GameScene");
    }

    // Method to exit the game
    public void ReturnToMenu()
    {
        SceneManager.LoadScene("MainMenu");
    }
}
