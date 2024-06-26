#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from IPython.display import display, HTML

display(HTML('''
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Advanced Brick Breaker</title>
<style>
    body {
        margin: 0;
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100vh;
        background-color: #000;
    }
    canvas {
        border: 1px solid #fff;
        background-color: #000;
    }
    .scoreboard, .lives {
        position: absolute;
        top: 10px;
        left: 50%;
        transform: translateX(-50%);
        color: #fff;
        font-size: 24px;
    }
    .lives {
        top: 40px;
    }
</style>
</head>
<body>
<div class="scoreboard" id="scoreboard">Score: 0</div>
<div class="lives" id="lives">Lives: 3</div>
<canvas id="gameCanvas" width="600" height="400"></canvas>
<script>
    const canvas = document.getElementById('gameCanvas');
    const context = canvas.getContext('2d');
    const scoreboard = document.getElementById('scoreboard');
    const livesDisplay = document.getElementById('lives');

    const paddle = { width: 100, height: 10, x: canvas.width / 2 - 50, y: canvas.height - 30, speed: 5 };
    const ball = { x: canvas.width / 2, y: canvas.height / 2, radius: 10, dx: 3, dy: -3 };
    const bricks = [];
    const brickRowCount = 5;
    const brickColumnCount = 9;
    const brickWidth = 50;
    const brickHeight = 20;
    const brickPadding = 10;
    const brickOffsetTop = 30;
    const brickOffsetLeft = 35;
    const powerUps = [];
    let score = 0;
    let lives = 3;
    let gameOver = false;

    for (let c = 0; c < brickColumnCount; c++) {
        bricks[c] = [];
        for (let r = 0; r < brickRowCount; r++) {
            const status = Math.random() > 0.7 ? 2 : 1; // 30% chance of strong brick
            bricks[c][r] = { x: 0, y: 0, status: status };
        }
    }

    function drawPaddle() {
        context.fillStyle = '#0f0';
        context.fillRect(paddle.x, paddle.y, paddle.width, paddle.height);
    }

    function drawBall() {
        context.beginPath();
        context.arc(ball.x, ball.y, ball.radius, 0, Math.PI * 2);
        context.fillStyle = '#ff0';
        context.fill();
        context.closePath();
    }

    function drawBricks() {
        for (let c = 0; c < brickColumnCount; c++) {
            for (let r = 0; r < brickRowCount; r++) {
                if (bricks[c][r].status > 0) {
                    const brickX = c * (brickWidth + brickPadding) + brickOffsetLeft;
                    const brickY = r * (brickHeight + brickPadding) + brickOffsetTop;
                    bricks[c][r].x = brickX;
                    bricks[c][r].y = brickY;
                    context.fillStyle = bricks[c][r].status === 2 ? '#00f' : '#f00'; // Blue for strong, Red for normal
                    context.fillRect(brickX, brickY, brickWidth, brickHeight);
                }
            }
        }
    }

    function drawPowerUps() {
        for (const powerUp of powerUps) {
            context.fillStyle = powerUp.color;
            context.fillRect(powerUp.x, powerUp.y, powerUp.width, powerUp.height);
        }
    }

    function draw() {
        context.clearRect(0, 0, canvas.width, canvas.height);
        drawBricks();
        drawBall();
        drawPaddle();
        drawPowerUps();
        updateScoreboard();
        updateLives();
    }

    function update() {
        if (gameOver) {
            context.fillStyle = '#fff';
            context.font = '24px Arial';
            context.fillText('Game Over', canvas.width / 2 - 50, canvas.height / 2);
            return;
        }

        ball.x += ball.dx;
        ball.y += ball.dy;

        if (ball.x + ball.dx > canvas.width - ball.radius || ball.x + ball.dx < ball.radius) {
            ball.dx = -ball.dx;
        }

        if (ball.y + ball.dy < ball.radius) {
            ball.dy = -ball.dy;
        } else if (ball.y + ball.dy > canvas.height - ball.radius) {
            if (ball.x > paddle.x && ball.x < paddle.x + paddle.width) {
                ball.dy = -ball.dy;
            } else {
                lives--;
                updateLives();
                if (lives <= 0) {
                    gameOver = true;
                } else {
                    ball.x = canvas.width / 2;
                    ball.y = canvas.height / 2;
                    ball.dx = 3;
                    ball.dy = -3;
                    paddle.x = canvas.width / 2 - paddle.width / 2;
                }
            }
        }

        if (paddle.x < 0) paddle.x = 0;
        if (paddle.x > canvas.width - paddle.width) paddle.x = canvas.width - paddle.width;

        for (let c = 0; c < brickColumnCount; c++) {
            for (let r = 0; r < brickRowCount; r++) {
                const brick = bricks[c][r];
                if (brick.status > 0) {
                    if (ball.x > brick.x && ball.x < brick.x + brickWidth && ball.y > brick.y && ball.y < brick.y + brickHeight) {
                        ball.dy = -ball.dy;
                        if (brick.status === 1) {
                            brick.status = 0;
                            score++;
                            maybeSpawnPowerUp(brick.x, brick.y);
                        } else {
                            brick.status = 1;
                        }
                    }
                }
            }
        }

        for (let i = 0; i < powerUps.length; i++) {
            powerUps[i].y += powerUps[i].speed;
            if (powerUps[i].y > canvas.height) {
                powerUps.splice(i, 1);
                i--;
            } else if (powerUps[i].x > paddle.x && powerUps[i].x < paddle.x + paddle.width && powerUps[i].y > paddle.y && powerUps[i].y < paddle.y + paddle.height) {
                applyPowerUp(powerUps[i].type);
                powerUps.splice(i, 1);
                i--;
            }
        }

        draw();
        requestAnimationFrame(update);
    }

    function maybeSpawnPowerUp(x, y) {
        if (Math.random() < 0.2) { // 20% chance to spawn a power-up
            const type = Math.random() < 0.5 ? 'widen' : 'shrink';
            const color = type === 'widen' ? '#0ff' : '#f0f';
            powerUps.push({ x: x + brickWidth / 2 - 10, y: y, width: 20, height: 20, speed: 2, type: type, color: color });
        }
    }

    function applyPowerUp(type) {
        if (type === 'widen') {
            paddle.width = Math.min(paddle.width + 20, canvas.width);
        } else if (type === 'shrink') {
            paddle.width = Math.max(paddle.width - 20, 20);
        }
    }

    function updateScoreboard() {
        scoreboard.textContent = `Score: ${score}`;
    }

    function updateLives() {
        livesDisplay.textContent = `Lives: ${lives}`;
    }

    canvas.addEventListener('mousemove', function(event) {
        const rect = canvas.getBoundingClientRect();
        paddle.x = event.clientX - rect.left - paddle.width / 2;
    });

    update();
</script>
</body>
</html>
'''))

