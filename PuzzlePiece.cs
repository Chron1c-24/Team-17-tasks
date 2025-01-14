using UnityEngine;

public class PuzzlePiece : MonoBehaviour
{
    private Vector3 initialPosition;
    private Vector3 screenPoint;
    private Vector3 offset;
    private bool isDragging = false;
    private bool isInCorrectPosition = false;
    public float snapDistance = 0.5f; // Distance to snap
    public PuzzlePiece[] adjacentPieces; // Array of adjacent pieces this piece can snap to
    private PuzzleManager puzzleManager;

    void Start()
    {
        initialPosition = transform.position;
        puzzleManager = FindObjectOfType<PuzzleManager>(); // Get the PuzzleManager
    }

    void OnMouseDown()
    {
        if (!isInCorrectPosition)
        {
            screenPoint = Camera.main.WorldToScreenPoint(gameObject.transform.position);
            offset = gameObject.transform.position - Camera.main.ScreenToWorldPoint(new Vector3(Input.mousePosition.x, Input.mousePosition.y, screenPoint.z));
            isDragging = true;

            // Remove the parent object so the piece is independent
            transform.SetParent(null);
        }
    }

    void OnMouseDrag()
    {
        if (isDragging)
        {
            Vector3 cursorPoint = new Vector3(Input.mousePosition.x, Input.mousePosition.y, screenPoint.z);
            Vector3 cursorPosition = Camera.main.ScreenToWorldPoint(cursorPoint) + offset;
            transform.position = cursorPosition;
        }
    }

    void OnMouseUp()
    {
        isDragging = false;

        // Check if the piece is within the snap distance of any allowed adjacent pieces
        bool snapped = false;
        foreach (var adjacent in adjacentPieces)
        {
            if (Vector3.Distance(transform.position, adjacent.transform.position) <= snapDistance)
            {
                transform.position = adjacent.transform.position;
                isInCorrectPosition = true;
                snapped = true;
                puzzleManager.CheckPuzzleCompletion(); // Check puzzle completion
                break;
            }
        }

        // If no adjacent piece was snapped, return to the original position
        if (!snapped && Vector3.Distance(transform.position, initialPosition) <= snapDistance)
        {
            transform.position = initialPosition;
        }
    }

    public bool IsInCorrectPosition()
    {
        return isInCorrectPosition;
    }
}