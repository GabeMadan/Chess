document.addEventListener("DOMContentLoaded", () => {
    const socket = io(); 

    const chessBoard = document.getElementById('chessBoard');
    const moveLogElement = document.getElementById('moveLog');

    let selectedSquare = null;
    let validMoves = []; 
    let moveLog = []; 
    let whiteToMove = true;
    let playerOne = true;
    let playerTwo = false;
    let aiThinking = false;
    let currentBoard = [];
    let lastMove = null;

    const SQ_SIZE = 64;
    const ANIMATION_DURATION = 300;
    const HIGHLIGHT_DELAY = 100;

    const createBoard = () => {
        for (let row = 0; row < 8; row++) {
            for (let col = 0; col < 8; col++) {
                const square = document.createElement('div');
                square.classList.add('square', (row + col) % 2 === 0 ? 'light' : 'dark');
                square.dataset.row = row;
                square.dataset.col = col;

                const overlay = document.createElement('div');
                overlay.classList.add('highlight-overlay');
                square.appendChild(overlay);

                square.addEventListener('click', onSquareClick);
                chessBoard.appendChild(square);
            }
        }
    };

    const onSquareClick = (e) => {
        if (aiThinking) return;

        const square = e.currentTarget;
        const row = parseInt(square.dataset.row);
        const col = parseInt(square.dataset.col);
        const piece = currentBoard[row][col];

        if (selectedSquare === square) {
            clearHighlights();
            selectedSquare = null;
            validMoves = [];
            return;
        }

        if ((whiteToMove && piece.startsWith('w')) || (!whiteToMove && piece.startsWith('b'))) {
            selectedSquare = square;
            highlightSquare(square);
            requestValidMoves(row, col);
        } else if (selectedSquare) {
            const startSquare = [parseInt(selectedSquare.dataset.row), parseInt(selectedSquare.dataset.col)];
            const endSquare = [row, col];

            socket.emit('makeMove', {
                startSquare: startSquare,
                endSquare: endSquare
            });

            selectedSquare = null;
            validMoves = [];
        }
    };

    const requestValidMoves = (row, col) => {
        socket.emit('getValidMoves', { row, col });
    };

    socket.on('validMoves', (data) => {
        validMoves = data.moves;
        highlightValidMoves();
    });

    const highlightSquare = (square) => {
        clearNonLastMoveHighlights();
        const overlay = square.querySelector('.highlight-overlay');
        overlay.classList.add('selected');
    };

    const highlightValidMoves = () => {
        validMoves.forEach(move => {
            const square = document.querySelector(`[data-row="${move[0]}"][data-col="${move[1]}"]`);
            if (square) {
                const overlay = square.querySelector('.highlight-overlay');
                overlay.classList.add('highlighted');
            }
        });
    };

    const clearNonLastMoveHighlights = () => {
        const overlays = document.querySelectorAll('.highlight-overlay');
        overlays.forEach(overlay => {
            overlay.classList.remove('highlighted', 'selected');
        });
    };

    const clearLastMoveHighlight = () => {
        if (lastMove) {
            const startSquareElement = document.querySelector(`[data-row="${lastMove.startSquare[0]}"][data-col="${lastMove.startSquare[1]}"]`);
            const endSquareElement = document.querySelector(`[data-row="${lastMove.endSquare[0]}"][data-col="${lastMove.endSquare[1]}"]`);

            if (startSquareElement && endSquareElement) {
                startSquareElement.querySelector('.highlight-overlay').classList.remove('last-move');
                endSquareElement.querySelector('.highlight-overlay').classList.remove('last-move');
            }
        }
    };

    socket.on('initialBoard', (data) => {
        updateBoard(data.board);
        whiteToMove = data.whiteToMove;
        playerOne = data.playerOne;
        playerTwo = data.playerTwo;
        renderMoveLog();
    });

    socket.on('moveMade', async (data) => {
        clearNonLastMoveHighlights();
        whiteToMove = data.whiteToMove;
        clearLastMoveHighlight();
        lastMove = data.move;

        if (playerTwo) {
            highlightLastMove(lastMove);
        }

        animateMove(data, async () => {
            updateBoard(data.board);
            updateMoveLog(data.move, data.board, data.move.checkmate, data.move.stalemate, data.move.check);
            if (playerOne && !playerTwo && !whiteToMove) {
                await delay(ANIMATION_DURATION);
                socket.emit('requestAIMove');
            }
        });
    });

    const updateMoveLog = (move, board, checkmate, stalemate, check) => {
        const moveString = getChessNotation(move, board, checkmate, stalemate, check);
        moveLog.push(moveString);
        renderMoveLog();
    };

    const getChessNotation = (move, board, checkmate, stalemate, check) => {
        const rankFile = (row, col) => `${String.fromCharCode(97 + col)}${8 - row}`;
        let moveString = '';

        const pieceMoved = move.pieceMoved[1];
        const isPawn = pieceMoved.toLowerCase() === 'p';

        if (pieceMoved === 'K' && Math.abs(move.startSquare[1] - move.endSquare[1]) === 2) {
            moveString = move.endSquare[1] === 6 ? 'O-O' : 'O-O-O';
        } else {
            const isCapture = move.isCapture;

            if (isCapture) {
                moveString += isPawn ? String.fromCharCode(97 + move.startSquare[1]) : pieceMoved;
                moveString += 'x';
            } else if (!isPawn) {
                moveString += pieceMoved;
            }

            moveString += rankFile(move.endSquare[0], move.endSquare[1]);

            if (move.isPromotion) {
                moveString += '=Q';
                moveString = moveString[1] == "x" ? rankFile(move.startSquare[0], move.startSquare[1])[0] + moveString.slice(1) : moveString.slice(1);
            }

            if (move.isEnpassant) {
                moveString += ' e.p.';
            }
        }
        if (checkmate) {
            moveString += '#';
        } else if (check) {
            moveString += '+';
        }

        if (stalemate) {
            moveString = '1/2-1/2';
        }

        return moveString;
    };

    const renderMoveLog = () => {
        moveLogElement.innerHTML = '<div class="move-log-title">Move Log</div>';
        const table = document.createElement('table');
        table.classList.add('move-log-table');

        const headerRow = table.insertRow(-1);
        const headerCell2 = document.createElement('th');
        headerCell2.className = 'move-log-header';
        headerCell2.textContent = 'White';
        const headerCell3 = document.createElement('th');
        headerCell3.className = 'move-log-header';
        headerCell3.textContent = 'Black';
        headerRow.appendChild(headerCell2);
        headerRow.appendChild(headerCell3);

        let row, cell1, cell2;

        for (let i = 0; i < moveLog.length; i += 2) {
            row = table.insertRow(-1);

            cell1 = row.insertCell(0);
            cell1.textContent = moveLog[i];
            cell1.className = 'white-move fixed-width-cell';

            if (i + 1 < moveLog.length) {
                cell2 = row.insertCell(1);
                cell2.textContent = moveLog[i + 1];
                cell2.className = 'black-move fixed-width-cell';
            } else {
                cell2 = row.insertCell(1);
                cell2.textContent = "";
                cell2.className = 'black-move fixed-width-cell';
            }
        }

        moveLogElement.appendChild(table);
    };

    socket.on('aiThinking', (data) => {
        aiThinking = data.thinking;
    });

    // Display game over message
    socket.on('gameOver', async (data) => {
        await delay(ANIMATION_DURATION);
        displayGameOverMessage(data.message);
    });

    const updateBoard = (board) => {
        currentBoard = board;
        const squares = document.querySelectorAll('.square');
        squares.forEach(square => {
            const row = square.dataset.row;
            const col = square.dataset.col;
            const piece = board[row][col];
            square.style.backgroundImage = piece !== '--' ? `url('/static/images/${piece}.png')` : '';
        });

        delay(HIGHLIGHT_DELAY).then(() => {
            if (lastMove) {
                const startSquareElement = document.querySelector(`[data-row="${lastMove.startSquare[0]}"][data-col="${lastMove.startSquare[1]}"]`);
                const endSquareElement = document.querySelector(`[data-row="${lastMove.endSquare[0]}"][data-col="${lastMove.endSquare[1]}"]`);

                if (startSquareElement && endSquareElement) {
                    if (playerOne && !playerTwo) {
                        startSquareElement.querySelector('.highlight-overlay').classList.add('last-move');
                        endSquareElement.querySelector('.highlight-overlay').classList.add('last-move');
                    }
                }
            }
        });
    };

    const highlightLastMove = (move) => {
        const startSquareElement = document.querySelector(`[data-row="${move.startSquare[0]}"][data-col="${move.startSquare[1]}"]`);
        const endSquareElement = document.querySelector(`[data-row="${move.endSquare[0]}"][data-col="${move.endSquare[1]}"]`);

        if (startSquareElement && endSquareElement) {
            startSquareElement.querySelector('.highlight-overlay').classList.add('last-move');
            endSquareElement.querySelector('.highlight-overlay').classList.add('last-move');
        }
    };

    // Display the game over message to the user
    const displayGameOverMessage = (message) => {
        const messageElement = document.createElement('div');
        messageElement.style.position = 'absolute';
        messageElement.style.top = '50%';
        messageElement.style.left = '50%';
        messageElement.style.transform = 'translate(-50%, -50%)';
        messageElement.style.padding = '20px';
        messageElement.style.backgroundColor = 'rgba(0, 0, 0, 0.8)';
        messageElement.style.color = 'white';
        messageElement.style.fontSize = '24px';
        messageElement.style.textAlign = 'center';
        messageElement.style.borderRadius = '10px';
        messageElement.innerText = message;

        document.body.appendChild(messageElement);

        setTimeout(() => {
            document.body.removeChild(messageElement);
        }, 5000);
    };

    // Animate the movement of a piece
    const animateMove = (data, callback) => {
        const move = data.move;
        const startSquare = move.startSquare;
        const endSquare = move.endSquare;
        const piece = move.pieceMoved;

        const startX = startSquare[1] * SQ_SIZE;
        const startY = startSquare[0] * SQ_SIZE;
        const endX = endSquare[1] * SQ_SIZE;
        const endY = endSquare[0] * SQ_SIZE;

        const startSquareElement = document.querySelector(`[data-row="${startSquare[0]}"][data-col="${startSquare[1]}"]`);
        const endSquareElement = document.querySelector(`[data-row="${endSquare[0]}"][data-col="${endSquare[1]}"]`);

        startSquareElement.style.backgroundImage = '';

        if (playerTwo) {
            highlightLastMove(lastMove);
        }

        const pieceElement = document.createElement('div');
        pieceElement.style.width = `${SQ_SIZE}px`;
        pieceElement.style.height = `${SQ_SIZE}px`;
        pieceElement.style.position = 'absolute';
        pieceElement.style.backgroundImage = `url('/static/images/${piece}.png')`;
        pieceElement.style.transform = `translate(${startX}px, ${startY}px)`;
        chessBoard.appendChild(pieceElement);

        const startTime = performance.now();

        const animate = (currentTime) => {
            const elapsedTime = currentTime - startTime;
            const progress = Math.min(elapsedTime / ANIMATION_DURATION, 1);
            const easedProgress = cubicEaseInOut(progress);

            const currentX = startX + (endX - startX) * easedProgress;
            const currentY = startY + (endY - startY) * easedProgress;
            pieceElement.style.transform = `translate(${currentX}px, ${currentY}px)`;

            if (progress < 1) {
                requestAnimationFrame(animate);
            } else {
                chessBoard.removeChild(pieceElement);
                updateBoard(data.board);
                if (callback) callback();
            }
        };

        requestAnimationFrame(animate);
    };

    // Function for smoother animations
    const cubicEaseInOut = (t) => {
        return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
    };

    const delay = (ms) => {
        return new Promise(resolve => setTimeout(resolve, ms));
    };

    createBoard();
});
