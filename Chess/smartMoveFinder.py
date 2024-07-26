import random
import numpy as np
import chessMain

# Constants for checkmate and stalemate scores
CHECKMATE = 1000
STALEMATE = 0

# Dictionary to hold the base scores for each piece
pieceScores = {"K": 0, "Q": 8, "R": 5, "N": 3, "B": 3, "p": 1}

# Positional scores for knights
knightScores = np.array([[1, 1, 1, 1, 1, 1, 1, 1],
                         [1, 2, 2, 2, 2, 2, 2, 1],
                         [1, 2, 3, 3, 3, 3, 2, 1],
                         [1, 2, 4, 4, 4, 4, 2, 1],
                         [1, 2, 4, 4, 4, 4, 2, 1],
                         [1, 2, 3, 3, 3, 3, 2, 1],
                         [1, 2, 2, 2, 2, 2, 2, 1],
                         [1, 1, 1, 1, 1, 1, 1, 1]])

# Positional scores for bishops
bishopScores = np.array([[4, 3, 2, 1, 1, 2, 3, 4],
                         [3, 4, 3, 2, 2, 3, 4, 3],
                         [2, 3, 4, 3, 3, 4, 3, 2],
                         [1, 2, 3, 4, 4, 3, 2, 1],
                         [1, 2, 3, 4, 4, 3, 2, 1],
                         [2, 3, 4, 3, 3, 4, 3, 2],
                         [3, 4, 3, 2, 2, 3, 4, 3],
                         [4, 3, 2, 1, 1, 2, 3, 4]])

# Positional scores for queens
queenScores = np.array([[1, 1, 1, 3, 1, 1, 1, 1],
                        [1, 2, 3, 3, 3, 1, 1, 1],
                        [1, 4, 3, 3, 3, 4, 2, 1],
                        [1, 2, 3, 3, 3, 2, 2, 1],
                        [1, 2, 3, 3, 3, 2, 2, 1],
                        [1, 4, 3, 3, 3, 4, 2, 1],
                        [1, 1, 2, 3, 3, 1, 1, 1],
                        [1, 1, 1, 3, 1, 1, 1, 1]])

# Positional scores for rooks
rookScores = np.array([[4, 3, 4, 4, 4, 4, 3, 4],
                       [4, 4, 4, 4, 4, 4, 4, 4],
                       [1, 1, 2, 3, 3, 2, 1, 1],
                       [1, 2, 3, 4, 4, 3, 2, 1],
                       [1, 2, 3, 4, 4, 3, 2, 1],
                       [1, 1, 2, 2, 2, 2, 1, 1],
                       [4, 4, 4, 4, 4, 4, 4, 4],
                       [4, 3, 4, 4, 4, 4, 3, 4]])

# Positional scores for white pawns
whitePawnScores = np.array([[8, 8, 8, 8, 8, 8, 8, 8],
                            [8, 8, 8, 8, 8, 8, 8, 8],
                            [5, 6, 6, 7, 7, 6, 6, 5],
                            [2, 3, 3, 5, 5, 3, 3, 2],
                            [1, 2, 3, 4, 4, 3, 2, 1],
                            [1, 2, 2, 3, 3, 2, 1, 1],
                            [1, 1, 1, 0, 0, 1, 1, 1],
                            [0, 0, 0, 0, 0, 0, 0, 0]])

# Positional scores for black pawns
blackPawnScores = np.array([[0, 0, 0, 0, 0, 0, 0, 0],
                            [1, 1, 1, 0, 0, 1, 1, 1],
                            [1, 2, 2, 3, 3, 2, 1, 1],
                            [1, 2, 3, 4, 4, 3, 2, 1],
                            [2, 3, 3, 5, 5, 3, 3, 2],
                            [5, 6, 6, 7, 7, 6, 6, 5],
                            [8, 8, 8, 8, 8, 8, 8, 8],
                            [8, 8, 8, 8, 8, 8, 8, 8]])

# Dictionary to hold positional scores for each piece type
piecePositionScores = {"N": knightScores, "Q": queenScores, "B": bishopScores, "R": rookScores, "bp": blackPawnScores, "wp": whitePawnScores}

# Function to find a random move from a list of valid moves
def findRandomMove(validMoves):
    return validMoves[random.randint(0, len(validMoves) - 1)]

# Function to find the best move using a simple minimax algorithm with a depth of 1
def findMove(gamestate, validMoves):
    turnMultiplier = 1 if gamestate.whiteToMove else -1
    opponentMinMaxScore = CHECKMATE
    bestPlayerMove = None
    random.shuffle(validMoves)

    for playerMove in validMoves:
        gamestate.makeMove(playerMove)
        opponentMoves = gamestate.getValidMoves()
        if gamestate.stalemate:
            opponentMaxScore = STALEMATE
        elif gamestate.checkmate:
            opponentMaxScore = -CHECKMATE
        else:
            opponentMaxScore = -CHECKMATE
            for opponentMove in opponentMoves:
                gamestate.makeMove(opponentMove)
                gamestate.getValidMoves()
                if gamestate.checkmate:
                    score = CHECKMATE
                elif gamestate.stalemate: 
                    score = STALEMATE
                else:
                    score = -turnMultiplier * scoreBoard(gamestate.board)
                if score > opponentMaxScore:
                    opponentMaxScore = score
                gamestate.undoMove()
        if opponentMaxScore < opponentMinMaxScore:
            opponentMinMaxScore = opponentMaxScore
            bestPlayerMove = playerMove
        gamestate.undoMove()

    return bestPlayerMove

# Function to find the best move using a minimax algorithm with a given depth
def findBestMove(gamestate, validMoves, DEPTH):
    global nextMove, counter
    counter = 0
    random.shuffle(validMoves)
    nextMove = None
    findMoveNegaMaxAlphaBeta(gamestate, validMoves, DEPTH, DEPTH, -2*CHECKMATE, 2*CHECKMATE, 1 if gamestate.whiteToMove else -1)
    return nextMove

# Function to find the best move using a minimax algorithm with a given depth (no alpha-beta pruning)
def findMoveMinMax(gamestate, validMoves, depth, ttl_depth, whiteToMove):
    global nextMove
    if depth == 0:
        return scoreBoard(gamestate)

    if whiteToMove:
        maxScore = -CHECKMATE
        for move in validMoves:
            gamestate.makeMove(move)
            nextMoves = gamestate.getValidMoves()
            score = findMoveMinMax(gamestate, nextMoves, depth - 1, ttl_depth, False)
            if score > maxScore:
                maxScore = score
                if depth == ttl_depth:
                    nextMove = move
            gamestate.undoMove()
        return maxScore

    else:
        minScore = CHECKMATE
        for move in validMoves:
            gamestate.makeMove(move)
            nextMoves = gamestate.getValidMoves()
            score = findMoveMinMax(gamestate, nextMoves, depth - 1, ttl_depth, True)
            if score < minScore:
                minScore = score
                if depth == ttl_depth:
                    nextMove = move
            gamestate.undoMove()
        return minScore

# Function to find the best move using a negamax algorithm with a given depth (no alpha-beta pruning)
def findMoveNegaMax(gamestate, validMoves, depth, ttl_depth, turnMultiplier):
    global nextMove, counter
    counter += 1
    if depth == 0:
        return turnMultiplier * scoreBoard(gamestate)
    maxScore = -CHECKMATE

    for move in validMoves:
        gamestate.makeMove(move)
        nextMoves = gamestate.getValidMoves()
        score = -findMoveNegaMax(gamestate, nextMoves, depth - 1, ttl_depth, -turnMultiplier)
        if score > maxScore:
            maxScore = score
            if depth == ttl_depth:
                nextMove = move
                print(move, score)
        gamestate.undoMove()
    return maxScore

# Function to find the best move using a negamax algorithm with alpha-beta pruning
def findMoveNegaMaxAlphaBeta(gamestate, validMoves, depth, ttl_depth, alpha, beta, turnMultiplier):
    global nextMove, counter
    counter += 1
    if depth == 0:
        return turnMultiplier * scoreBoard(gamestate)
    maxScore = -CHECKMATE

    for move in validMoves:
        gamestate.makeMove(move)
        nextMoves = gamestate.getValidMoves()
        score = -findMoveNegaMaxAlphaBeta(gamestate, nextMoves, depth - 1, ttl_depth, -beta, -alpha, -turnMultiplier)
        if score > maxScore:
            maxScore = score
            if depth == ttl_depth:
                nextMove = move
                print(move, score)
        gamestate.undoMove()
        if maxScore > alpha:
            alpha = maxScore
        if alpha >= beta:
            break
    return maxScore

# Function to score the board based on piece positions and checkmate/stalemate conditions
# Positive score is good for white, negative is good for black
def scoreBoard(gamestate):
    if gamestate.checkmate:
        if gamestate.whiteToMove:
            return -CHECKMATE
        else:
            return CHECKMATE
    if gamestate.stalemate:
        return STALEMATE

    score = 0
    for row in range(len(gamestate.board)):
        for column in range(len(gamestate.board[row])):
            square = gamestate.board[row][column]
            if square != "--":
                piecePositionScore = 0
                if square[1] != "K":
                    if square[1] == "p":
                        piecePositionScore = piecePositionScores[square][row][column]
                    else:
                        piecePositionScore = piecePositionScores[square[1]][row][column]
                if square[0] == "w":
                    score += pieceScores[square[1]] + piecePositionScore * 0.2
                elif square[0] == "b":
                    score -= pieceScores[square[1]] + piecePositionScore * 0.2
    return score
