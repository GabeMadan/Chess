document.addEventListener("DOMContentLoaded", () => {
    const playerModeBtn = document.getElementById('playerModeBtn');
    const depthSlider = document.getElementById('depthSlider');
    const depthValue = document.getElementById('depthValue');
    const startGameBtn = document.getElementById('startGameBtn');

    let playerOne = true;
    let playerTwo = false;

    playerModeBtn.addEventListener('click', () => {
        if (playerOne && !playerTwo) {
            playerModeBtn.textContent = 'Two Player';
            playerOne = true;
            playerTwo = true;
            document.getElementById('depthSliderContainer').style.display = 'none';
        } else {
            playerModeBtn.textContent = 'One Player';
            playerOne = true;
            playerTwo = false;
            document.getElementById('depthSliderContainer').style.display = 'block';
        }
    });

    depthSlider.addEventListener('input', () => {
        depthValue.textContent = depthSlider.value;
    });

    startGameBtn.addEventListener('click', () => {
        const gameOptions = {
            playerOne: playerOne,
            playerTwo: playerTwo,
            depth: parseInt(depthSlider.value)
        };

        // Send game options to the server and start the game
        fetch('/start_game', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(gameOptions)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                window.location.href = '/game';
            }
        });
    });
});
