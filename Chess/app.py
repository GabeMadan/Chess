from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import chessEngine, smartMoveFinder
import time

# Initialize Flask application and SocketIO for real-time communication
app = Flask(__name__)
socketio = SocketIO(app)

playerOne: bool = True  # Indicates if player one is a human
playerTwo: bool = False  # Indicates if player two is a human (for two-player mode)
DEPTH: int = 2  # AI search depth
game_state: chessEngine.GameState = chessEngine.GameState()  
valid_moves: list[chessEngine.Move] = game_state.getValidMoves() 
move_made: bool = False
animate: bool = False
game_over: bool = False
ai_thinking: bool = False

@app.route('/')
def menu() -> str:
    """Render the main menu."""
    return render_template('menu.html')

@app.route('/start_game', methods=['POST'])
def start_game() -> jsonify:
    """
    Start a new game with specified settings.
    Resets the game state and updates player modes and AI depth.
    """
    global playerOne, playerTwo, DEPTH, game_state, valid_moves, move_made, animate, game_over
    data = request.json
    playerOne = data['playerOne']
    playerTwo = data['playerTwo']
    DEPTH = data['depth']


    game_state = chessEngine.GameState()
    valid_moves = game_state.getValidMoves()
    move_made = False
    animate = False
    game_over = False
    return jsonify(success=True)

@app.route('/game')
def game() -> str:
    """Render the game board."""
    return render_template('index.html')

@socketio.on('connect')
def handle_connect() -> None:
    """
    Handle a new connection to the server.
    Emit the initial board state and player information to the client.
    """
    global game_state
    emit('initialBoard', {
        'board': game_state.board,
        'whiteToMove': game_state.whiteToMove,
        'playerOne': playerOne,
        'playerTwo': playerTwo
    })

@socketio.on('getValidMoves')
def handle_get_valid_moves(data: dict) -> None:
    """
    Handle request for valid moves for a selected piece.
    Emit valid moves to the client.
    """
    global valid_moves, game_state
    row: int = data['row']
    col: int = data['col']
    piece_color: str = 'w' if game_state.whiteToMove else 'b'
    piece: str = game_state.board[row][col]
    
    if piece.startswith(piece_color):
        moves = [
            (move.endRow, move.endColumn)
            for move in valid_moves
            if move.startRow == row and move.startColumn == col
        ]
        emit('validMoves', {'moves': moves})

@socketio.on('makeMove')
def handle_make_move(data: dict) -> None:
    """
    Handle a move made by the player.
    Validate the move and update the game state, then emit the updated board state.
    """
    global game_state, valid_moves, move_made, animate, game_over, ai_thinking

    move = chessEngine.Move(data['startSquare'], data['endSquare'], game_state.board)
    
    for valid_move in valid_moves:
        if move == valid_move:
            is_capture: bool = game_state.board[valid_move.endRow][valid_move.endColumn] != '--' or valid_move.isEnpassantMove
            game_state.makeMove(valid_move)
            move_made = True
            animate = True
            valid_moves = game_state.getValidMoves()
            is_promotion: bool = valid_move.isPawnPromotion
            in_check: bool = game_state.inCheck
            checkmate: bool = game_state.checkmate
            stalemate: bool = game_state.stalemate

            emit('moveMade', {
                'board': game_state.board,
                'whiteToMove': game_state.whiteToMove,
                'move': {
                    'startSquare': data['startSquare'],
                    'endSquare': data['endSquare'],
                    'pieceMoved': game_state.board[data['endSquare'][0]][data['endSquare'][1]],
                    'isCapture': is_capture,
                    'isPromotion': is_promotion,
                    'isEnpassant': valid_move.isEnpassantMove,
                    'check': in_check,
                    'checkmate': checkmate,
                    'stalemate': stalemate
                }
            })
            check_game_over_conditions()
            break

    # Initiate AI move if it's AI's turn in one-player mode
    if move_made and not game_state.whiteToMove and playerOne and not playerTwo and not ai_thinking:
        ai_thinking = True
        socketio.emit('aiThinking', {'thinking': True})
        socketio.start_background_task(delayed_ai_move)

def delayed_ai_move() -> None:
    """Introduce a delay before the AI calculates its move, that way the animation can finish."""
    time.sleep(0.3)
    handle_ai_move()

def handle_ai_move() -> None:
    """
    Calculate and make the AI's move.
    Update the game state and emit the updated board state.
    """
    global game_state, valid_moves, move_made, animate, ai_thinking
    ai_move = smartMoveFinder.findBestMove(game_state, valid_moves, DEPTH)
    
    if ai_move is None:
        ai_move = smartMoveFinder.findRandomMove(valid_moves)
    
    is_capture: bool = game_state.board[ai_move.endRow][ai_move.endColumn] != '--' or ai_move.isEnpassantMove
    game_state.makeMove(ai_move)
    move_made = True
    animate = True
    valid_moves = game_state.getValidMoves()

    is_promotion: bool = ai_move.isPawnPromotion
    in_check: bool = game_state.inCheck
    checkmate: bool = game_state.checkmate
    stalemate: bool = game_state.stalemate

    socketio.emit('moveMade', {
        'board': game_state.board,
        'whiteToMove': game_state.whiteToMove,
        'move': {
            'startSquare': [ai_move.startRow, ai_move.startColumn],
            'endSquare': [ai_move.endRow, ai_move.endColumn],
            'pieceMoved': game_state.board[ai_move.endRow][ai_move.endColumn],
            'isCapture': is_capture,
            'isPromotion': is_promotion,
            'isEnpassant': ai_move.isEnpassantMove,
            'check': in_check,
            'checkmate': checkmate,
            'stalemate': stalemate
        }
    })
    check_game_over_conditions()
    socketio.emit('aiThinking', {'thinking': False})
    ai_thinking = False

def check_game_over_conditions() -> None:
    global game_state, game_over
    if game_state.checkmate:
        game_over = True
        winner = "White" if not game_state.whiteToMove else "Black"
        socketio.emit('gameOver', {'message': f'{winner} wins by checkmate'})
    elif game_state.stalemate:
        game_over = True
        socketio.emit('gameOver', {'message': 'Draw by stalemate'})

# Start the Flask app with SocketIO support in debug mode
if __name__ == "__main__":
    socketio.run(app, debug=True)
