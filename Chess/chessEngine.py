from typing import List, Tuple

# Class to represent the current state of the chess game.
# Also responsible for determining the valid moves at current state and keeps a move log.
class GameState:
    def __init__(self):
        # The board is represented by a 2D list where each element is a string indicating the piece or an empty square.
        self.board: List[List[str]] = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        ]

        self.whiteToMove: bool = True
        
        self.moveLog: List[Move] = []
        
        # Dictionary mapping piece types to their respective move functions.
        self.movefunctions: dict = {'p': self.getPawnMoves, 'R': self.getRookMoves, 'N': self.getNightMoves, 'B': self.getBishopMoves, 'Q': self.getQueenMoves, 'K': self.getKingMoves}
        
        self.inCheck: bool = False
        self.checkmate: bool = False
        self.stalemate: bool = False
        
        self.whiteKingLocation: Tuple[int, int] = (7, 4)
        self.blackKingLocation: Tuple[int, int] = (0, 4)
        
        # Lists to keep track of pins and checks.
        self.pins: List[Tuple[int, int, int, int]] = []
        self.checks: List[Tuple[int, int, int, int]] = []

        # Tuple to store the en passant square.
        self.enpassantPossible: Tuple[int, int] = ()
        
        # List to keep track of the en passant history.
        self.enpassantPossibleLog: List[Tuple[int, int]] = [self.enpassantPossible]
        
        # Current castling rights.
        self.currentCastlingRights: CastleRights = CastleRights(True, True, True, True)
        
        # List to keep track of the castling rights history.
        self.castleRightsLog: List[CastleRights] = [CastleRights(self.currentCastlingRights.wks, self.currentCastlingRights.bks, self.currentCastlingRights.wqs, self.currentCastlingRights.bqs)]

    # Method to convert the board state to FEN notation.
    def boardToFEN(self) -> str:
        fen: str = ""
        for row in self.board:
            emptyCount: int = 0
            for square in row:
                if square == "--":
                    emptyCount += 1
                else:
                    if emptyCount > 0:
                        fen += str(emptyCount)
                        emptyCount = 0
                    fen += square[1] if square[0] == "w" else square[1].lower()
            if emptyCount > 0:
                fen += str(emptyCount)
            fen += '/'
        fen = fen[:-1]
        
        # Add other FEN components (active color, castling availability, en passant target square, halfmove clock, fullmove number)
        fen += ' b ' if not self.whiteToMove else ' w '
        fen += '-'  # castling availability placeholder
        fen += ' - 0 1'  # en passant, halfmove clock, fullmove number placeholder
        return fen

    # Method to make a move on the board.
    def makeMove(self, move: 'Move') -> None:
        self.board[move.startRow][move.startColumn] = "--"
        self.board[move.endRow][move.endColumn] = move.pieceMoved
        self.moveLog.append(move)
        self.whiteToMove = not self.whiteToMove
        if move.pieceMoved == "wK":
            self.whiteKingLocation = (move.endRow, move.endColumn)
        elif move.pieceMoved == "bK":
            self.blackKingLocation = (move.endRow, move.endColumn)
        if move.isPawnPromotion:
            self.board[move.endRow][move.endColumn] = move.pieceMoved[0] + "Q"
        if move.pieceMoved[1] == "p" and abs(move.startRow - move.endRow) == 2:
            self.enpassantPossible = ((move.startRow + move.endRow)//2, move.startColumn)
        else:
            self.enpassantPossible = ()
        if move.isEnpassantMove:
            self.board[move.startRow][move.endColumn] = "--"
        if move.isCastleMove:
            if move.endColumn - move.startColumn == 2:
                self.board[move.endRow][move.endColumn - 1] = self.board[move.endRow][move.endColumn + 1]
                self.board[move.endRow][move.endColumn + 1] = "--"
            else:
                self.board[move.endRow][move.endColumn + 1] = self.board[move.endRow][move.endColumn - 2]
                self.board[move.endRow][move.endColumn - 2] = "--"
        self.enpassantPossibleLog.append(self.enpassantPossible)
        self.updateCastleRights(move)
        self.castleRightsLog.append(CastleRights(self.currentCastlingRights.wks, self.currentCastlingRights.bks, self.currentCastlingRights.wqs, self.currentCastlingRights.bqs))

    # Method to undo the last move made.
    def undoMove(self) -> None:
        if len(self.moveLog) != 0:
            move: Move = self.moveLog.pop()
            self.board[move.startRow][move.startColumn] = move.pieceMoved
            self.board[move.endRow][move.endColumn] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove
            if move.pieceMoved == 'wK':
                self.whiteKingLocation = (move.startRow, move.startColumn)
            elif move.pieceMoved == 'bK':
                self.blackKingLocation = (move.startRow, move.startColumn)
            if move.isEnpassantMove:
                self.board[move.endRow][move.endColumn] = '--'
                self.board[move.startRow][move.endColumn] = move.pieceCaptured
            self.enpassantPossibleLog.pop()
            self.enpassantPossible = self.enpassantPossibleLog[-1]
            self.castleRightsLog.pop()
            newRights: CastleRights = self.castleRightsLog[-1]
            self.currentCastlingRights = CastleRights(newRights.wks, newRights.bks, newRights.wqs, newRights.bqs)
            if move.isCastleMove:
                if move.endColumn - move.startColumn == 2: 
                    self.board[move.endRow][move.endColumn+1] = self.board[move.endRow][move.endColumn-1]
                    self.board[move.endRow][move.endColumn-1] = '--'
                else:
                    self.board[move.endRow][move.endColumn-2] = self.board[move.endRow][move.endColumn+1]
                    self.board[move.endRow][move.endColumn+1] = '--'
        self.checkmate = False
        self.stalemate = False

    # Method to update the castling rights based on the move made.
    def updateCastleRights(self, move: 'Move') -> None:
        if move.pieceMoved == "wK":
            self.currentCastlingRights.wks = False
            self.currentCastlingRights.wqs = False
        elif move.pieceMoved == "bK":
            self.currentCastlingRights.bks = False
            self.currentCastlingRights.bqs = False
        elif move.pieceMoved == "wR":
            if move.startRow == 7:
                if move.startColumn == 0:
                    self.currentCastlingRights.wqs = False
                elif move.startColumn == 7:
                    self.currentCastlingRights.wks = False
        elif move.pieceMoved == "bR":
            if move.startRow == 0:
                if move.startColumn == 0:
                    self.currentCastlingRights.bqs = False
                elif move.startColumn == 7:
                    self.currentCastlingRights.bks = False
        if move.pieceCaptured == "wR":
            if move.endRow == 7:
                if move.endColumn == 0:
                    self.currentCastlingRights.wqs = False
                elif move.endColumn == 7:
                    self.currentCastlingRights.wks = False
        elif move.pieceCaptured == "bR":
            if move.endRow == 0:
                if move.endColumn == 0:
                    self.currentCastlingRights.bqs = False
                elif move.endColumn == 7:
                    self.currentCastlingRights.bks = False

    # Method to get all valid moves considering checks and pins.
    def getValidMoves(self) -> List['Move']:
        checkCastleRights: CastleRights = CastleRights(self.currentCastlingRights.wks, self.currentCastlingRights.bks, self.currentCastlingRights.wqs, self.currentCastlingRights.bqs)
        checkEnpassantPossible: Tuple[int, int] = self.enpassantPossible
        moves: List[Move] = []
        self.inCheck, self.pins, self.checks = self.checksForPinsAndChecks()
        if self.whiteToMove:
            self.getCastleMoves(self.whiteKingLocation[0], self.whiteKingLocation[1], moves)
            kingRow: int = self.whiteKingLocation[0]
            kingColumn: int = self.whiteKingLocation[1]
        else:
            self.getCastleMoves(self.blackKingLocation[0], self.blackKingLocation[1], moves)
            kingRow: int = self.blackKingLocation[0]
            kingColumn: int = self.blackKingLocation[1]
        if self.inCheck:
            if len(self.checks) == 1:
                moves = moves + self.getAllPossibleMoves()
                check: Tuple[int, int, int, int] = self.checks[0]
                checkRow: int = check[0]
                checkColumn: int = check[1]
                pieceChecking: str = self.board[checkRow][checkColumn]
                validSquares: List[Tuple[int, int]] = []
                if pieceChecking[1] == "N":
                    validSquares = [(checkRow, checkColumn)]
                else:
                    for i in range(1, 8):
                        validSquare: Tuple[int, int] = (kingRow + check[2]*i, kingColumn + check[3]*i)
                        validSquares.append(validSquare)
                        if validSquare[0] == checkRow and validSquare[1] == checkColumn:
                            break
                for i in range(len(moves)-1, -1, -1):
                    if moves[i].pieceMoved[1] != "K":
                        if not (moves[i].endRow, moves[i].endColumn) in validSquares:
                            moves.remove(moves[i])
            else:
                self.getKingMoves(kingRow, kingColumn, moves)
        else:
            moves = moves + self.getAllPossibleMoves()
        self.currentCastlingRights = checkCastleRights
        self.enpassantPossible = checkEnpassantPossible
        if len(moves) == 0:
            if self.inCheck:
                self.checkmate = True
            else:
                self.stalemate = True
        return moves

    # Method to determine if the current player is in check.
    def inCheck(self) -> bool:
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:
            return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])

    # Method to determine if a square is under attack.
    def squareUnderAttack(self, row: int, column: int) -> bool:
        self.whiteToMove = not self.whiteToMove
        opponentMoves: List[Move] = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove
        for move in opponentMoves:
            if move.endRow == row and move.endColumn == column:
                return True
        kingRow, kingColumn = self.blackKingLocation if self.whiteToMove else self.whiteKingLocation
        rowMoves = (-1, -1, -1, 0, 0, 1, 1, 1)
        columnMoves = (-1, 0, 1, -1, 1, -1, 0, 1)
        for i in range(8):
            if row + rowMoves[i] == kingRow and column + columnMoves[i] == kingColumn:
                return True
        return False

    # Method to check for pins and checks on the king.
    def checksForPinsAndChecks(self) -> Tuple[bool, List[Tuple[int, int, int, int]], List[Tuple[int, int, int, int]]]:
        pins: List[Tuple[int, int, int, int]] = []
        checks: List[Tuple[int, int, int, int]] = []
        inCheck: bool = False
        if self.whiteToMove:
            enemyColor: str = "b"
            sameColor: str = "w"
            startRow: int = self.whiteKingLocation[0]
            startColumn: int = self.whiteKingLocation[1]
        else:
            enemyColor: str = "w"
            sameColor: str = "b"
            startRow: int = self.blackKingLocation[0]
            startColumn: int = self.blackKingLocation[1]
        directions: Tuple[Tuple[int, int]] = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        for i in range(len(directions)):
            d: Tuple[int, int] = directions[i]
            possiblePin: Tuple[int, int, int, int] = ()
            for j in range(1, 8):
                endRow: int = startRow + d[0] * j
                endColumn: int = startColumn + d[1] * j
                if 0 <= endRow < 8 and 0 <= endColumn < 8:
                    endPiece: str = self.board[endRow][endColumn]
                    if endPiece[0] == sameColor and endPiece[1] != "K":
                        if possiblePin == ():
                            possiblePin = (endRow, endColumn, d[0], d[1])
                        else:
                            break
                    elif endPiece[0] == enemyColor:
                        type: str = endPiece[1]
                        if (0 <= i <= 3 and type == "R") or (4 <= i <= 7 and type == "B") or (j == 1 and type == "p" and ((enemyColor == "w" and 6 <= i <= 7) or (enemyColor == "b" and 4 <= i <= 5))) or (type == "Q") or (j == 1 and type == "K"):
                            if possiblePin == ():
                                inCheck = True
                                checks.append((endRow, endColumn, d[0], d[1]))
                                break
                            else:
                                pins.append(possiblePin)
                                break
                        else:
                            break
                else:
                    break
        nightMoves: Tuple[Tuple[int, int]] = ((1, 2), (-1, 2), (1, -2), (-1, -2), (2, 1), (-2, 1), (2, -1), (-2, -1))
        for n in nightMoves:
            endRow = startRow + n[0]
            endColumn = startColumn + n[1]
            if 0 <= endRow < 8 and 0 <= endColumn < 8:
                endPiece = self.board[endRow][endColumn]
                if endPiece[0] == enemyColor and endPiece[1] == "N":
                    inCheck = True
                    checks.append((endRow, endColumn, n[0], n[1]))
        return inCheck, pins, checks

    # Method to get all possible moves without considering checks.
    def getAllPossibleMoves(self) -> List['Move']:
        moves: List[Move] = []
        for row in range(len(self.board)):
            for column in range(len(self.board[row])):
                turn: str = self.board[row][column][0]
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece: str = self.board[row][column][1]
                    self.movefunctions[piece](row, column, moves)
        return moves

    # Method to get all possible pawn moves.
    def getPawnMoves(self, row: int, column: int, moves: List['Move']) -> None:
        piecePinned: bool = False
        pinDirection: Tuple[int, int] = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == column:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        if self.whiteToMove:
            moveAmount: int = -1
            startRow: int = 6
            enemyColor: str = "b"
            kingRow, kingColumn = self.whiteKingLocation
        else:
            moveAmount: int = 1
            startRow: int = 1
            enemyColor: str = "w"
            kingRow, kingColumn = self.blackKingLocation
        if self.board[row + moveAmount][column] == "--":
            if not piecePinned or pinDirection == (moveAmount, 0):
                moves.append(Move((row, column), (row + moveAmount, column), self.board))
                if row == startRow and self.board[row + 2*moveAmount][column] == "--":
                    moves.append(Move((row, column), (row + 2*moveAmount, column), self.board))
        if column-1 >= 0:
            if not piecePinned or pinDirection == (moveAmount, -1):
                if self.board[row + moveAmount][column-1][0] == enemyColor:
                    moves.append(Move((row, column), (row + moveAmount, column-1), self.board))
                if (row + moveAmount, column - 1) == self.enpassantPossible:
                    attackingPiece = blockingPiece = False
                    if kingRow == row:
                        if kingColumn < column:
                            insideRange = range(kingColumn + 1, column-1)
                            outsideRange = range(column+1, 8)
                        else:
                            insideRange = range(kingColumn - 1, column, -1)
                            outsideRange = range(column - 2, -1, -1)
                        for i in insideRange:
                            if self.board[row][i] != "--":
                                blockingPiece = True
                        for i in outsideRange:
                            square = self.board[row][i]
                            if square[0] == enemyColor and (square[1] == "R" or square[1] == "Q"):
                                attackingPiece = True
                            elif square != "--":
                                blockingPiece = True
                    if not attackingPiece or blockingPiece:
                        moves.append(Move((row, column), (row + moveAmount, column - 1), self.board, isEnpassantMove=True))
        if column+1 <= 7:
            if not piecePinned or pinDirection == (moveAmount, 1):
                if self.board[row + moveAmount][column+1][0] == enemyColor:
                    moves.append(Move((row, column), (row + moveAmount, column+1), self.board))
                if (row + moveAmount, column + 1) == self.enpassantPossible:
                    attackingPiece = blockingPiece = False
                    if kingRow == row:
                        if kingColumn < column:
                            insideRange = range(kingColumn + 1, column)
                            outsideRange = range(column+2, 8)
                        else:
                            insideRange = range(kingColumn - 1, column + 1, -1)
                            outsideRange = range(column - 1, -1, -1)
                        for i in insideRange:
                            if self.board[row][i] != "--":
                                blockingPiece = True
                        for i in outsideRange:
                            square = self.board[row][i]
                            if square[0] == enemyColor and (square[1] == "R" or square[1] == "Q"):
                                attackingPiece = True
                            elif square != "--":
                                blockingPiece = True
                    if not attackingPiece or blockingPiece:
                        moves.append(Move((row, column), (row + moveAmount, column + 1), self.board, isEnpassantMove=True))

    # Method to get all possible rook moves.
    def getRookMoves(self, row: int, column: int, moves: List['Move']) -> None:
        piecePinned: bool = False
        pinDirection: Tuple[int, int] = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == column:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                if self.board[row][column][1] != "Q":
                    self.pins.remove(self.pins[i])
                break
        directions: Tuple[Tuple[int, int]] = ((-1, 0), (1, 0), (0, -1), (0, 1))
        opposite_color: str = 'b' if self.whiteToMove else 'w'
        for d in directions:
            for i in range(1, 8):
                end_row: int = row + d[0] * i
                end_col: int = column + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8:  
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        end_piece: str = self.board[end_row][end_col]
                        if end_piece == "--":  
                            moves.append(Move((row, column), (end_row, end_col), self.board))
                        elif end_piece[0] == opposite_color:  
                            moves.append(Move((row, column), (end_row, end_col), self.board))
                            break
                        else:
                            break
                else:  
                    break

    # Method to get all possible knight moves.
    def getNightMoves(self, row: int, column: int, moves: List['Move']) -> None:
        piecePinned: bool = False
        pinDirection: Tuple[int, int] = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == column:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        NightMoves: Tuple[Tuple[int, int]] = ((1, 2), (-1, 2), (1, -2), (-1, -2), (2, 1), (-2, 1), (2, -1), (-2, -1))
        same_color: str = 'w' if self.whiteToMove else 'b'
        for i in NightMoves:
            end_row: int = row + i[0]
            end_col: int = column + i[1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:  
                if not piecePinned:
                    end_piece: str = self.board[end_row][end_col]
                    if end_piece[0] != same_color:  
                        moves.append(Move((row, column), (end_row, end_col), self.board))

    # Method to get all possible bishop moves.
    def getBishopMoves(self, row: int, column: int, moves: List['Move']) -> None:
        piecePinned: bool = False
        pinDirection: Tuple[int, int] = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == column:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                if self.board[row][column][1] != "Q":
                    self.pins.remove(self.pins[i])
                break
        directions: Tuple[Tuple[int, int]] = ((-1, 1), (1, 1), (1, -1), (-1, -1))
        opposite_color: str = 'b' if self.whiteToMove else 'w'
        for d in directions:
            for i in range(1, 8):
                end_row: int = row + d[0] * i
                end_col: int = column + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8:  
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        end_piece: str = self.board[end_row][end_col]
                        if end_piece == "--":  
                            moves.append(Move((row, column), (end_row, end_col), self.board))
                        elif end_piece[0] == opposite_color:  
                            moves.append(Move((row, column), (end_row, end_col), self.board))
                            break
                        else:  
                            break

    # Method to get all possible king moves.
    def getKingMoves(self, row: int, column: int, moves: List['Move']) -> None:
        rowMoves: Tuple[int, ...] = (-1, -1, -1, 0, 0, 1, 1, 1)
        columnMoves: Tuple[int, ...] = (-1, 0, 1, -1, 1, -1, 0, 1)
        same_color: str = 'w' if self.whiteToMove else 'b'
        for i in range(8):
            end_row: int = row + rowMoves[i]
            end_col: int = column + columnMoves[i]
            if 0 <= end_row < 8 and 0 <= end_col < 8:  
                end_piece: str = self.board[end_row][end_col]
                if end_piece[0] != same_color:  
                    if same_color == "w":
                        self.whiteKingLocation = (end_row, end_col)
                    else:
                        self.blackKingLocation = (end_row, end_col)
                    inCheck, pins, checks = self.checksForPinsAndChecks()
                    if not inCheck:
                        moves.append(Move((row, column), (end_row, end_col), self.board))
                    if same_color == "w":
                        self.whiteKingLocation = (row, column)
                    else:
                        self.blackKingLocation = (row, column)

    # Method to get all possible castling moves.
    def getCastleMoves(self, row: int, column: int, moves: List['Move']) -> None:
        if self.inCheck:
            return
        if (self.whiteToMove and self.currentCastlingRights.wks) or (not self.whiteToMove and self.currentCastlingRights.bks):
            if self.board[row][column + 1] == "--" and self.board[row][column + 2] == "--":
                if not self.squareUnderAttack(row, column + 1) and not self.squareUnderAttack(row, column + 2):
                    if not self.squareUnderAttack(row, column):
                        moves.append(Move((row, column), (row, column + 2), self.board, isCastleMove=True))
        if (self.whiteToMove and self.currentCastlingRights.wqs) or (not self.whiteToMove and self.currentCastlingRights.bqs):
            if self.board[row][column - 1] == "--" and self.board[row][column - 2] == "--" and self.board[row][column - 3] == "--":
                if not self.squareUnderAttack(row, column - 1) and not self.squareUnderAttack(row, column - 2):
                    if not self.squareUnderAttack(row, column):
                        moves.append(Move((row, column), (row, column - 2), self.board, isCastleMove=True))

    # Method to get all possible queen moves.
    def getQueenMoves(self, row: int, column: int, moves: List['Move']) -> None:
        self.getRookMoves(row, column, moves)
        self.getBishopMoves(row, column, moves)

# Class to represent castling rights for both players.
class CastleRights:
    def __init__(self, wks: bool, bks: bool, wqs: bool, bqs: bool):
        self.wks: bool = wks
        self.bks: bool = bks
        self.wqs: bool = wqs
        self.bqs: bool = bqs

# Class to represent a chess move.
class Move:
    ranksToRows: dict = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks: dict = {v: k for k, v in ranksToRows.items()}
    filesToCols: dict = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles: dict = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq: Tuple[int, int], endSq: Tuple[int, int], board: List[List[str]], isEnpassantMove: bool = False, isCastleMove: bool = False):
        self.startRow: int = startSq[0]
        self.startColumn: int = startSq[1]
        self.endRow: int = endSq[0]
        self.endColumn: int = endSq[1]
        self.pieceMoved: str = board[self.startRow][self.startColumn]
        self.pieceCaptured: str = board[self.endRow][self.endColumn]
        self.isPawnPromotion: bool = False
        self.isEnpassantMove: bool = isEnpassantMove
        self.isCheck: bool = False
        self.isCheckmate: bool = False
        self.isDraw: bool = False

        if self.pieceMoved == "wp" and self.endRow == 0:
            self.isPawnPromotion = True
        elif self.pieceMoved == "bp" and self.endRow == 7:
            self.isPawnPromotion = True
        if self.isEnpassantMove:
            self.pieceCaptured = "wp" if self.pieceMoved == "bp" else "bp"
        self.isCapture: bool = self.pieceCaptured != "--"
        self.moveID: int = self.startRow * 1000 + self.startColumn * 100 + self.endRow * 10 + self.endColumn
        self.isCastleMove: bool = isCastleMove

    # Method to check if two moves are equal.
    def __eq__(self, other: object) -> bool:
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    # Method to get the chess notation for the move.
    def getChessNotation(self) -> str:
        return self.getRankFile(self.startRow, self.startColumn) + self.getRankFile(self.endRow, self.endColumn)

    # Method to get the rank and file of a square.
    def getRankFile(self, row: int, column: int) -> str:
        return self.colsToFiles[column] + self.rowsToRanks[row]

    # Method to get the string representation of the move.
    def __str__(self) -> str:
        if self.isCastleMove:
            return "O-O" if self.endColumn == 6 else "O-O-O"
        
        endSquare: str = self.getRankFile(self.endRow, self.endColumn)
        if self.pieceMoved[1] == "p":
            if self.isCapture:
                moveString: str = self.colsToFiles[self.startColumn] + "x" + endSquare
            else:
                moveString = endSquare
            if self.isPawnPromotion:
                moveString += "=Q"  
            if self.isEnpassantMove:
                moveString += " e.p."
        else:
            moveString = self.pieceMoved[1]
            if self.isCapture:
                moveString += "x"
            moveString += endSquare
        if self.isCheckmate:
            moveString += "#"
        elif self.isCheck:
            moveString += "+"
        elif self.isDraw:
            moveString = "1/2 1/2"
        return moveString
