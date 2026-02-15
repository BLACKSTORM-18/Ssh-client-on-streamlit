import streamlit as st
import streamlit.components.v1 as components

# Setting up the page config for that premium feel
st.set_page_config(
    page_title="NEON SNAKE 2077",
    page_icon="🐍",
    layout="centered",
    initial_sidebar_state="collapsed"
)

def main():
    # Streamlit UI elements (Title and Instructions)
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
            
            .main {
                background-color: #0a0a0c;
            }
            .title-container {
                text-align: center;
                padding: 20px;
                font-family: 'Orbitron', sans-serif;
            }
            .glitch {
                font-size: 3rem;
                font-weight: bold;
                text-transform: uppercase;
                position: relative;
                text-shadow: 0.05em 0 0 #00fffc, -0.03em -0.04em 0 #fc00ff,
                             0.025em 0.04em 0 #fffc00;
                animation: glitch 725ms infinite;
            }
            @keyframes glitch {
                0% { text-shadow: 0.05em 0 0 #00fffc, -0.03em -0.04em 0 #fc00ff, 0.025em 0.04em 0 #fffc00; }
                14% { text-shadow: 0.05em 0 0 #00fffc, -0.03em -0.04em 0 #fc00ff, 0.025em 0.04em 0 #fffc00; }
                15% { text-shadow: -0.05em -0.025em 0 #00fffc, 0.025em 0.025em 0 #fc00ff, -0.05em -0.05em 0 #fffc00; }
                49% { text-shadow: -0.05em -0.025em 0 #00fffc, 0.025em 0.025em 0 #fc00ff, -0.05em -0.05em 0 #fffc00; }
                50% { text-shadow: 0.025em 0.05em 0 #00fffc, 0.05em 0 0 #fc00ff, 0 -0.05em 0 #fffc00; }
                99% { text-shadow: 0.025em 0.05em 0 #00fffc, 0.05em 0 0 #fc00ff, 0 -0.05em 0 #fffc00; }
                100% { text-shadow: -0.025em 0 0 #00fffc, -0.025em -0.025em 0 #fc00ff, -0.025em -0.05em 0 #fffc00; }
            }
            .subtitle {
                color: #00fffc;
                font-family: 'Orbitron', sans-serif;
                letter-spacing: 2px;
                margin-bottom: 20px;
            }
        </style>
        <div class="title-container">
            <h1 class="glitch">NEON SNAKE</h1>
            <p class="subtitle">VIRTUAL REALITY INTERFACE // V.2.0.77</p>
        </div>
    """, unsafe_allow_html=True)

    # The Game Logic (HTML + JS for high performance)
    game_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {
                background: transparent;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                margin: 0;
                overflow: hidden;
                font-family: 'Orbitron', sans-serif;
                color: #00fffc;
            }
            #game-container {
                position: relative;
                border: 2px solid #00fffc;
                box-shadow: 0 0 20px #00fffc, inset 0 0 10px #00fffc;
                border-radius: 10px;
                background: rgba(0, 0, 0, 0.8);
            }
            canvas {
                display: block;
                image-rendering: pixelated;
            }
            .stats {
                display: flex;
                justify-content: space-between;
                width: 400px;
                padding: 10px;
                font-size: 1.2rem;
                text-shadow: 0 0 5px #00fffc;
            }
            #overlay {
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                background: rgba(0, 0, 0, 0.85);
                z-index: 10;
                text-align: center;
                cursor: pointer;
            }
            .btn {
                background: transparent;
                border: 1px solid #fc00ff;
                color: #fc00ff;
                padding: 10px 20px;
                font-family: 'Orbitron', sans-serif;
                font-size: 1rem;
                cursor: pointer;
                transition: all 0.3s;
                margin-top: 15px;
            }
            .btn:hover {
                background: #fc00ff;
                color: black;
                box-shadow: 0 0 15px #fc00ff;
            }
            .controls-hint {
                margin-top: 20px;
                font-size: 0.8rem;
                color: #666;
            }
        </style>
        <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap" rel="stylesheet">
    </head>
    <body>
        <div class="stats">
            <div>SCORE: <span id="score">000</span></div>
            <div>HIGH: <span id="highScore">000</span></div>
        </div>
        
        <div id="game-container">
            <div id="overlay">
                <h1 style="color: #fc00ff; text-shadow: 0 0 10px #fc00ff;">SYSTEM READY</h1>
                <p>INITIALIZE NEURAL LINK</p>
                <button class="btn" onclick="startGame()">START MISSION</button>
                <div class="controls-hint">USE ARROW KEYS OR SWIPE TO NAVIGATE</div>
            </div>
            <canvas id="snakeCanvas" width="400" height="400"></canvas>
        </div>

        <script>
            const canvas = document.getElementById('snakeCanvas');
            const ctx = canvas.getContext('2d');
            const scoreEl = document.getElementById('score');
            const highScoreEl = document.getElementById('highScore');
            const overlay = document.getElementById('overlay');

            const gridSize = 20;
            const tileCount = canvas.width / gridSize;
            
            let score = 0;
            let highScore = localStorage.getItem('snakeHighScore') || 0;
            highScoreEl.innerText = highScore.toString().padStart(3, '0');

            let snake = [{x: 10, y: 10}];
            let food = {x: 5, y: 5};
            let dx = 0;
            let dy = 0;
            let nextDx = 0;
            let nextDy = 0;
            let gameLoop;
            let isRunning = false;
            let speed = 100;

            function startGame() {
                overlay.style.display = 'none';
                resetGame();
                isRunning = true;
                if(gameLoop) clearInterval(gameLoop);
                gameLoop = setInterval(draw, speed);
            }

            function resetGame() {
                score = 0;
                scoreEl.innerText = '000';
                snake = [{x: 10, y: 10}];
                nextDx = 1;
                nextDy = 0;
                dx = 1;
                dy = 0;
                placeFood();
            }

            function placeFood() {
                food.x = Math.floor(Math.random() * tileCount);
                food.y = Math.floor(Math.random() * tileCount);
                // Don't place food on snake body
                snake.forEach(part => {
                    if(part.x === food.x && part.y === food.y) placeFood();
                });
            }

            function draw() {
                update();
                
                // Background clear
                ctx.fillStyle = '#0a0a0c';
                ctx.fillRect(0, 0, canvas.width, canvas.height);
                
                // Draw Grid (Subtle)
                ctx.strokeStyle = '#1a1a1f';
                ctx.lineWidth = 0.5;
                for(let i=0; i<canvas.width; i+=gridSize) {
                    ctx.beginPath(); ctx.moveTo(i, 0); ctx.lineTo(i, canvas.height); ctx.stroke();
                    ctx.beginPath(); ctx.moveTo(0, i); ctx.lineTo(canvas.width, i); ctx.stroke();
                }

                // Draw Food
                ctx.fillStyle = '#fc00ff';
                ctx.shadowBlur = 15;
                ctx.shadowColor = '#fc00ff';
                ctx.beginPath();
                ctx.arc(food.x * gridSize + gridSize/2, food.y * gridSize + gridSize/2, gridSize/2.5, 0, Math.PI*2);
                ctx.fill();
                ctx.shadowBlur = 0;

                // Draw Snake
                snake.forEach((part, index) => {
                    const isHead = index === 0;
                    ctx.fillStyle = isHead ? '#00fffc' : '#009d9b';
                    ctx.shadowBlur = isHead ? 15 : 0;
                    ctx.shadowColor = '#00fffc';
                    
                    // Rounded snake body
                    const padding = 2;
                    ctx.beginPath();
                    ctx.roundRect(
                        part.x * gridSize + padding, 
                        part.y * gridSize + padding, 
                        gridSize - padding*2, 
                        gridSize - padding*2, 
                        5
                    );
                    ctx.fill();
                });
            }

            function update() {
                dx = nextDx;
                dy = nextDy;

                const head = {x: snake[0].x + dx, y: snake[0].y + dy};

                // Wall collision (Wrap around or Die? Let's do Die for that hardcore vibe)
                if (head.x < 0 || head.x >= tileCount || head.y < 0 || head.y >= tileCount) {
                    gameOver();
                    return;
                }

                // Self collision
                for(let i = 0; i < snake.length; i++) {
                    if(snake[i].x === head.x && snake[i].y === head.y) {
                        gameOver();
                        return;
                    }
                }

                snake.unshift(head);

                // Food collision
                if (head.x === food.x && head.y === food.y) {
                    score += 10;
                    scoreEl.innerText = score.toString().padStart(3, '0');
                    if (score > highScore) {
                        highScore = score;
                        highScoreEl.innerText = highScore.toString().padStart(3, '0');
                        localStorage.setItem('snakeHighScore', highScore);
                    }
                    placeFood();
                    // Optional: increase speed
                } else {
                    snake.pop();
                }
            }

            function gameOver() {
                isRunning = false;
                clearInterval(gameLoop);
                overlay.style.display = 'flex';
                overlay.querySelector('h1').innerText = 'CRITICAL FAILURE';
                overlay.querySelector('p').innerText = 'NEURAL LINK SEVERED. SCORE: ' + score;
                overlay.querySelector('button').innerText = 'REBOOT SYSTEM';
            }

            // Controls
            window.addEventListener('keydown', e => {
                switch(e.key) {
                    case 'ArrowUp': if(dy !== 1) { nextDx = 0; nextDy = -1; } break;
                    case 'ArrowDown': if(dy !== -1) { nextDx = 0; nextDy = 1; } break;
                    case 'ArrowLeft': if(dx !== 1) { nextDx = -1; nextDy = 0; } break;
                    case 'ArrowRight': if(dx !== -1) { nextDx = 1; nextDy = 0; } break;
                }
            });

            // Touch support
            let touchStartX = 0;
            let touchStartY = 0;
            canvas.addEventListener('touchstart', e => {
                touchStartX = e.touches[0].clientX;
                touchStartY = e.touches[0].clientY;
                e.preventDefault();
            }, {passive: false});

            canvas.addEventListener('touchmove', e => {
                if (!isRunning) return;
                let touchEndX = e.touches[0].clientX;
                let touchEndY = e.touches[0].clientY;
                
                let diffX = touchEndX - touchStartX;
                let diffY = touchEndY - touchStartY;

                if (Math.abs(diffX) > Math.abs(diffY)) {
                    if (diffX > 0 && dx !== -1) { nextDx = 1; nextDy = 0; }
                    else if (diffX < 0 && dx !== 1) { nextDx = -1; nextDy = 0; }
                } else {
                    if (diffY > 0 && dy !== -1) { nextDx = 0; nextDy = 1; }
                    else if (diffY < 0 && dy !== 1) { nextDx = 0; nextDy = -1; }
                }
                e.preventDefault();
            }, {passive: false});

        </script>
    </body>
    </html>
    """

    # Rendering the component
    components.html(game_html, height=550)

    # Sidebar for the "vibe"
    with st.sidebar:
        st.header("🎮 GAME SETTINGS")
        st.write("Current Driver: **User_01**")
        st.write("Latency: **0.2ms**")
        st.divider()
        st.info("Pro Tip: Don't hit the walls. It's bad for your health.")
        if st.button("RESET GLOBAL CACHE"):
            st.toast("Cache purged. System refreshed.")

if __name__ == "__main__":
    main()

