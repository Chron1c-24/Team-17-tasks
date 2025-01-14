using UnityEngine;
using TMPro; // Required for TextMeshProUGUI
using UnityEngine.SceneManagement; // Required to manage scenes
using UnityEditor; // For SceneAsset support

public class GameTimer : MonoBehaviour
{
    public float totalTime = 180.0f; // 3 minutes in seconds
    private float remainingTime;
    private bool isTimerRunning = false;

    public TextMeshProUGUI timerText; // Drag and drop a TextMeshProUGUI element here
    public SceneAsset sceneToLoad; // Drag a scene into this slot in the Inspector

    void Start()
    {
        remainingTime = totalTime;
        isTimerRunning = true;
    }

    void Update()
    {
        if (isTimerRunning)
        {
            if (remainingTime > 0)
            {
                remainingTime -= Time.deltaTime;
                UpdateTimerDisplay();
            }
            else
            {
                remainingTime = 0;
                isTimerRunning = false;
                TimerEnded();
            }
        }

        // Manually trigger the scene change (you can replace the key with any desired input)
        if (Input.GetKeyDown(KeyCode.L)) // For example, press 'L' to load the scene manually
        {
            LoadSceneManually();
        }
    }

    void UpdateTimerDisplay()
    {
        // Display time in minutes and seconds
        int minutes = Mathf.FloorToInt(remainingTime / 60);
        int seconds = Mathf.FloorToInt(remainingTime % 60);
        timerText.text = string.Format("{0:00}:{1:00}", minutes, seconds);
    }

    void TimerEnded()
    {
        Debug.Log("Time's up! Game Over.");
        // Automatically load the scene when the timer ends
        LoadSceneManually();
    }

    void LoadSceneManually()
    {
        if (sceneToLoad != null)
        {
            // Load the scene using the name from the SceneAsset
            string sceneName = sceneToLoad.name;
            Debug.Log("Manually loading scene: " + sceneName);
            SceneManager.LoadScene(sceneName);
        }
        else
        {
            Debug.LogWarning("No scene assigned to load.");
        }
    }
}
