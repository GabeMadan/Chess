Single-Player/Multiplayer Chess Game with AI Engine


Overview

This is a chess game implemented using Python and Pygame. The game supports both human vs. human and human vs. AI modes. The AI's depth of search can be adjusted, and the game includes a graphical user interface for ease of play.

Features
- Play against another human or an AI.
- Adjustable AI difficulty.
- Animated piece movement.
- Move log display.
- In-game status messages (Check, Checkmate, Stalemate).

Requirements
- Python 3
- Pygame

Installation
- Clone the repository
- Navigate to the Chess directory:
- Run the game using python Chessmain.py

Game controls:
- Use the mouse to select and move pieces.
- Use the z key to undo the last move.
- Use the r key to reset the game.

File Structure
- main.py: Main driver file that handles user input, displays the current game state, and contains the main game loop.
- chessEngine.py: Contains the game logic and mechanics.
- smartMoveFinder.py: Contains the AI logic for finding the best move.
- images/: Directory containing images of the chess pieces.

Parts of this project were inspired/learned from Eddie Sharick's video series (https://youtu.be/EnYui0e73Rs?si=DAgm1oTz-cS58oAe)