# Main Driver File
# Handles user input, displays current GameState object
import pygame as p
import chessEngine, smartMoveFinder
from typing import Dict, List, Tuple, Any

BOARD_WIDTH: int = 512
BOARD_HEIGHT: int = 512
MOVE_LOG_PANEL_WIDTH: int = 128
MOVE_LOG_PANEL_HEIGHT: int = BOARD_HEIGHT
DIMENSION: int = 8
DEPTH: int = 2
SQ_SIZE: int = BOARD_HEIGHT // DIMENSION
FPS: int = 30
IMAGES: Dict[str, p.Surface] = {}
playerOne: bool = True  # false for ai, true for human
playerTwo: bool = False  # false for ai, true for human

# Initialize a global dictionary of images. This is called once in main
def loadImages() -> None:
    pieces: List[str] = ['wp', 'wR', 'wN', 'wB', 'wK', 'wQ', 'bp', 'bR', 'bN', 'bB', 'bK', 'bQ']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))

# Handle user and AI moves
def handleMoves(gamestate, validMoves: List, squareSelected: Tuple[int, int], playerClicks: List[Tuple[int, int]], moveMade: bool, animate: bool, gameOver: bool) -> Tuple[bool, Tuple[int, int], List[Tuple[int, int]], bool, bool, bool]:
    for e in p.event.get():
        if e.type == p.QUIT:
            return False, squareSelected, playerClicks, moveMade, animate, gameOver

        elif e.type == p.MOUSEBUTTONDOWN:
            if not gameOver:
                location: Tuple[int, int] = p.mouse.get_pos()
                column: int = location[0] // SQ_SIZE
                row: int = location[1] // SQ_SIZE
                if squareSelected == (row, column) or column >= 8:  # same square is selected
                    squareSelected = ()
                    playerClicks = []
                else:
                    squareSelected = (row, column)
                    playerClicks.append(squareSelected)
                if len(playerClicks) == 2:
                    move = chessEngine.Move(playerClicks[0], playerClicks[1], gamestate.board)
                    for i in range(len(validMoves)):
                        if move == validMoves[i]:
                            gamestate.makeMove(validMoves[i])
                            moveMade = True
                            animate = True
                            squareSelected = ()
                            playerClicks = []

                    if not moveMade:
                        playerClicks = [squareSelected]
        elif e.type == p.KEYDOWN:
            if e.key == p.K_z and (playerOne or playerTwo):
                gamestate.undoMove()
                squareSelected = ()
                playerClicks = []
                moveMade = True
                animate = False
                gameOver = False
            if e.key == p.K_r:
                gamestate = chessEngine.GameState()
                validMoves = gamestate.getValidMoves()
                squareSelected = ()
                playerClicks = []
                moveMade = False
                animate = False
                gameOver = False

    return True, squareSelected, playerClicks, moveMade, animate, gameOver

# Handle AI moves
def handleAIMove(gamestate, validMoves: List, moveMade: bool, animate: bool) -> Tuple[bool, bool]:
    AIMove = smartMoveFinder.findBestMove(gamestate, validMoves, DEPTH)
    print(AIMove)
    if AIMove is None:
        AIMove = smartMoveFinder.findRandomMove(validMoves)
    gamestate.makeMove(AIMove)
    moveMade = True
    animate = True
    return moveMade, animate

# Main function. Handles graphics and user input
def main() -> None:
    p.init()
    screen: p.Surface = p.display.set_mode((BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH, BOARD_HEIGHT))
    clock: p.time.Clock = p.time.Clock()
    screen.fill(p.Color("white"))

    # Load images
    loadImages()

    # Display main menu and get user preferences
    gameOptions: Dict[str, Any] = mainMenu(screen, clock)

    # Apply user preferences
    global playerOne, playerTwo, DEPTH
    playerOne = gameOptions['playerOne']
    playerTwo = gameOptions['playerTwo']
    DEPTH = gameOptions['depth']

    gamestate = chessEngine.GameState()
    validMoves: List = gamestate.getValidMoves()
    moveMade: bool = False
    animate: bool = False

    running: bool = True
    moveLogFont: p.font.Font = p.font.SysFont("Times New Roman", 12, False, False)

    squareSelected: Tuple[int, int] = ()
    playerClicks: List[Tuple[int, int]] = []
    gameOver: bool = False

    while running:
        humanTurn: bool = (gamestate.whiteToMove and playerOne) or (not gamestate.whiteToMove and playerTwo)

        running, squareSelected, playerClicks, moveMade, animate, gameOver = handleMoves(
            gamestate, validMoves, squareSelected, playerClicks, moveMade, animate, gameOver
        )

        if not gameOver and not humanTurn:
            moveMade, animate = handleAIMove(gamestate, validMoves, moveMade, animate)

        if moveMade:
            if animate:
                animateMove(gamestate.moveLog[-1], screen, gamestate.board, clock)
            validMoves = gamestate.getValidMoves()
            moveMade = False
            animate = False

        drawGameState(screen, gamestate, validMoves, squareSelected, moveLogFont)

        if gamestate.checkmate:
            gameOver = True
            if gamestate.whiteToMove:
                drawText(screen, "Black wins by Checkmate")
            else:
                drawText(screen, "White wins by Checkmate")

        if gamestate.stalemate:
            gameOver = True
            drawText(screen, "Draw by Stalemate")

        clock.tick(FPS)
        p.display.flip()

def drawText(screen: p.Surface, text: str) -> None:
    font: p.font.Font = p.font.SysFont("Times New Roman", 32, True, False)
    textObject: p.Surface = font.render(text, 0, p.Color("Gray"))
    textLocation: p.Rect = p.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT).move(BOARD_WIDTH / 2 - textObject.get_width() / 2,
                                                                        BOARD_HEIGHT / 2 - textObject.get_height() / 2)
    screen.blit(textObject, textLocation)
    textObject = font.render(text, 0, p.Color("Black"))
    screen.blit(textObject, textLocation.move(2, 2))

def highlightMoves(screen: p.Surface, gamestate, validMoves: List, squareSelected: Tuple[int, int]) -> None:
    if squareSelected:
        row, column = squareSelected
        if gamestate.board[row][column][0] == ("w" if gamestate.whiteToMove else "b"):
            surface: p.Surface = p.Surface((SQ_SIZE, SQ_SIZE))
            surface.set_alpha(100)
            surface.fill(p.Color("blue"))
            screen.blit(surface, (column * SQ_SIZE, row * SQ_SIZE))
            surface.fill(p.Color("yellow"))
            for move in validMoves:
                if move.startRow == row and move.startColumn == column:
                    screen.blit(surface, (SQ_SIZE * move.endColumn, SQ_SIZE * move.endRow))

# Responsible for all graphics in gamestate
def drawGameState(screen: p.Surface, gamestate, validMoves: List, squareSelected: Tuple[int, int], moveLogFont: p.font.Font) -> None:
    drawBoard(screen)
    drawPieces(screen, gamestate.board)
    drawNotation(screen)  # Draw the notation after drawing the pieces
    highlightMoves(screen, gamestate, validMoves, squareSelected)
    drawMoveLog(screen, gamestate, moveLogFont)

# Draws the squares on the board
def drawBoard(screen: p.Surface) -> None:
    global colors
    colors = [p.Color("blanchedalmond"), p.Color("burlywood3")]
    for row in range(DIMENSION):
        for column in range(DIMENSION):
            color: p.Color = colors[(row + column) % 2]
            p.draw.rect(screen, color, p.Rect(column * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))

def drawPieces(screen: p.Surface, board: List[List[str]]) -> None:
    for row in range(DIMENSION):
        for column in range(DIMENSION):
            piece: str = board[row][column]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(column * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))

def drawNotation(screen: p.Surface) -> None:
    font: p.font.Font = p.font.SysFont("Arial", 18)  # Define the font for the notation
    for row in range(DIMENSION):
        for column in range(DIMENSION):
            # Add the notation
            if column == 0:
                label: p.Surface = font.render(str(DIMENSION - row), 1, p.Color("Black"))
                screen.blit(label, (5, row * SQ_SIZE + 5))
            if row == DIMENSION - 1:
                label = font.render(chr(97 + column), 1, p.Color("Black"))
                screen.blit(label, (column * SQ_SIZE + SQ_SIZE - 20, BOARD_HEIGHT - 20))

def drawMoveLog(screen: p.Surface, gamestate, font: p.font.Font) -> None:
    moveLogRect: p.Rect = p.Rect(BOARD_WIDTH, 0, MOVE_LOG_PANEL_WIDTH, MOVE_LOG_PANEL_HEIGHT)
    p.draw.rect(screen, p.Color("black"), moveLogRect)
    lst: List = []
    moveLog: List = gamestate.moveLog
    if gamestate.moveLog:
        lst.append(gamestate.moveLog[-1])
    if gamestate.inCheck:
        lst[-1].isCheck = True
    if gamestate.checkmate:
        lst[-1].isCheckmate = True
    if gamestate.stalemate:
        lst[-1].isDraw = True
    whiteMoves: List[str] = ["White"]
    blackMoves: List[str] = ["Black"]

    for i in range(0, len(moveLog), 2):
        whiteMoves.append(str(moveLog[i]))
        if i + 1 < len(moveLog):
            blackMoves.append(str(moveLog[i + 1]))
        else:
            blackMoves.append(" ")

    padding: int = 5
    textY: int = padding
    lineSpacing: int = 2

    # Draw White moves
    for move in whiteMoves:
        textLocation: p.Rect = moveLogRect.move(padding, textY)
        textObject: p.Surface = font.render(move, True, p.Color("white"))
        screen.blit(textObject, textLocation)
        textY += textObject.get_height() + lineSpacing

    # Reset textY for Black moves
    textY = padding
    # Calculate the starting X position for Black moves
    blackX: int = BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH // 2 + padding

    # Draw Black moves
    for move in blackMoves:
        textLocation = moveLogRect.move(blackX - BOARD_WIDTH, textY)
        textObject = font.render(move, True, p.Color("white"))
        screen.blit(textObject, textLocation)
        textY += textObject.get_height() + lineSpacing

def cubicEaseInOut(t: float) -> float:
    if t < 0.5:
        return 4 * (t ** 3)
    else:
        f: float = (t - 1)
        return 4 * (f ** 3) + 1

def animateMove(move, screen: p.Surface, board: List[List[str]], clock: p.time.Clock, totalDuration: float = 0.2) -> None:
    coords: List[Tuple[int, int]] = []
    dR: int = move.endRow - move.startRow
    dC: int = move.endColumn - move.startColumn
    framesPerSecond: int = 144
    frameCount: int = int(totalDuration * framesPerSecond)
    for frame in range(frameCount + 1):
        t: float = frame / frameCount
        easedT: float = cubicEaseInOut(t)
        row: float = move.startRow + dR * easedT
        column: float = move.startColumn + dC * easedT
        drawBoard(screen)
        drawPieces(screen, board)
        drawNotation(screen)  # Draw the notation after drawing the pieces
        color: p.Color = colors[(move.endRow + move.endColumn) % 2]
        endSquare: p.Rect = p.Rect(move.endColumn * SQ_SIZE, move.endRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, endSquare)
        if move.pieceCaptured != "--" and not move.isEnpassantMove:
            screen.blit(IMAGES[move.pieceCaptured], endSquare)
        if move.pieceMoved != "--":
            screen.blit(IMAGES[move.pieceMoved], p.Rect(column * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(framesPerSecond)

def drawCheckerboard(screen: p.Surface) -> None:
    colors: List[p.Color] = [p.Color("blanchedalmond"), p.Color("burlywood3")]
    total_columns: int = (BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH) // SQ_SIZE
    for row in range(DIMENSION):
        for col in range(total_columns):  # Extend the checkerboard to cover the move log panel area
            color = colors[(row + col) % 2]
            p.draw.rect(screen, color, p.Rect(col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))

def mainMenu(screen: p.Surface, clock: p.time.Clock) -> Dict[str, Any]:
    font: p.font.Font = p.font.SysFont("Times New Roman", 32, True, False)
    smallFont: p.font.Font = p.font.SysFont("Times New Roman", 24, False, False)

    titleText: p.Surface = font.render("Chess", True, p.Color("Black"))
    playerModeText: p.Surface = smallFont.render("One Player", True, p.Color("Black"))
    playButtonText: p.Surface = smallFont.render("Play", True, p.Color("Black"))

    depth: int = DEPTH
    userColor: str = "white"
    playerOne: bool = True
    playerTwo: bool = False
    draggingSlider: bool = False

    sliderWidth: int = 150
    sliderHeight: int = 10
    handleRadius: int = 10

    buttonRects: Dict[str, p.Rect] = {}

    def calculatePositions() -> Tuple[int, int]:
        center_x: int = (BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH) // 2
        center_y: int = BOARD_HEIGHT // 2
        extra_width: int = 20

        buttonRects["playerMode"] = p.Rect(center_x - playerModeText.get_width() // 2 - extra_width // 2,
                                           center_y - 100, playerModeText.get_width() + extra_width,
                                           playerModeText.get_height())
        buttonRects["play"] = p.Rect(center_x - playButtonText.get_width() // 2 - extra_width // 2,
                                     center_y + 70, playButtonText.get_width() + extra_width,
                                     playButtonText.get_height())

        sliderX: int = center_x - sliderWidth // 2
        sliderY: int = center_y - 30  # Move the slider 30 pixels higher
        return sliderX, sliderY

    sliderX, sliderY = calculatePositions()

    while True:
        drawCheckerboard(screen)  # Draw the checkerboard background

        center_x: int = (BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH) // 2

        screen.blit(titleText, (center_x - titleText.get_width() // 2, sliderY - 200))

        # Center the text within the buttons
        screen.blit(playerModeText, (buttonRects["playerMode"].centerx - playerModeText.get_width() // 2, buttonRects["playerMode"].y))
        screen.blit(playButtonText, (buttonRects["play"].centerx - playButtonText.get_width() // 2, buttonRects["play"].y))

        if playerOne and not playerTwo:
            # Draw slider
            p.draw.rect(screen, p.Color("Black"), (sliderX, sliderY, sliderWidth, sliderHeight))
            handleX: int = sliderX + int((depth / 5) * sliderWidth)
            p.draw.circle(screen, p.Color("Black"), (handleX, sliderY + sliderHeight // 2), handleRadius)

            depthText: p.Surface = smallFont.render(f"Depth: {depth}", True, p.Color("Black"))
            screen.blit(depthText, (center_x - depthText.get_width() // 2, sliderY + 20))

        # Draw button outlines and handle hover effects
        mousePos: Tuple[int, int] = p.mouse.get_pos()
        for key, rect in buttonRects.items():
            if rect.collidepoint(mousePos):
                p.draw.rect(screen, p.Color("Gray"), rect, 2)
            else:
                p.draw.rect(screen, p.Color("Black"), rect, 2)

        for event in p.event.get():
            if event.type == p.QUIT:
                p.quit()
                quit()
            elif event.type == p.MOUSEBUTTONDOWN:
                mouseX, mouseY = event.pos
                if buttonRects["playerMode"].collidepoint(mouseX, mouseY):
                    if playerOne and not playerTwo:
                        playerModeText = smallFont.render("Two Player", True, p.Color("Black"))
                        playerOne = True
                        playerTwo = True
                    else:
                        playerModeText = smallFont.render("One Player", True, p.Color("Black"))
                        playerOne = True
                        playerTwo = False
                elif playerOne and not playerTwo and sliderY - handleRadius <= mouseY <= sliderY + sliderHeight + handleRadius and sliderX <= mouseX <= sliderX + sliderWidth:
                    draggingSlider = True
                elif buttonRects["play"].collidepoint(mouseX, mouseY):
                    return {"playerOne": playerOne, "playerTwo": playerTwo, "depth": depth, "userColor": userColor}
            elif event.type == p.MOUSEBUTTONUP:
                draggingSlider = False
            elif event.type == p.MOUSEMOTION and draggingSlider:
                mouseX, mouseY = event.pos
                newDepth: int = int(((mouseX - sliderX) / sliderWidth) * 5)
                depth = max(0, min(5, newDepth))

        p.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()
