using UnityEngine;

public class PuzzleManager : MonoBehaviour
{
    public static PuzzleManager Instance;
    public PuzzlePiece[] puzzlePieces; // Array to hold all the puzzle pieces
    private int currentPieceIndex = 0; // Tracks the next piece that should be placed

    void Awake()
    {
        if (Instance == null)
        {
            Instance = this;
        }
    }

    public void CheckPuzzleCompletion()
    {
        if (puzzlePieces[currentPieceIndex].IsInCorrectPosition()) 
        {
            currentPieceIndex++; // Move to the next piece in the order

            if (currentPieceIndex == puzzlePieces.Length) // If all pieces are placed correctly
            {
                DisplayWinMessage();
            }
        }
    }

    private void DisplayWinMessage()
    {
        Debug.Log("You Win!");
        // Trigger win UI or other logic
    }
}