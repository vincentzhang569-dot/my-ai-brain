import streamlit as st
import streamlit.components.v1 as components

# 页面基础配置
st.set_page_config(
    page_title="Super AI Kart: V27 Stable",
    page_icon="🍄",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 强制全屏 CSS (修复PC端边距)
st.markdown("""
    <style>
        #MainMenu, header, footer {visibility: hidden;}
        .block-container { padding: 0 !important; margin: 0 !important; max-width: 100% !important; }
        iframe { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; border: none; z-index: 9999; }
    </style>
""", unsafe_allow_html=True)

# 游戏核心代码
game_html = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<style>
    * { margin: 0; padding: 0; box-sizing: border-box; -webkit-tap-highlight-color: transparent; }
    body { background: #000; overflow: hidden; font-family: 'Arial', sans-serif; }

    /* 游戏画布 */
    #game-container {
        position: absolute; top: 0; left: 0; width: 100%; height: 100%;
        display: block; /* 默认显示，JS控制隐藏 */
    }
    canvas { display: block; width: 100%; height: 100%; }

    /* 旋转提示 (仅手机竖屏显示) */
    #rotate-hint {
        position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        background: #111; color: #fff; z-index: 10000;
        display: none; /* 默认隐藏 */
        flex-direction: column; align-items: center; justify-content: center;
        text-align: center;
    }
    .icon-spin { font-size: 60px; margin-bottom: 20px; animation: spin 2s infinite; }
    @keyframes spin { 0% { transform: rotate(0deg); } 25% { transform: rotate(-90deg); } 100% { transform: rotate(-90deg); } }

    /* UI 界面 */
    .hud { 
        position: absolute; top: 20px; 
        font-weight: bold; font-size: 20px; 
        text-shadow: 2px 2px 0 #000; pointer-events: none; z-index: 10; 
        color: white;
    }
    #score-ui { left: 20px; }
    #world-ui { right: 20px; color: #FFD700; }

    /* 移动端虚拟按键 */
    #controls {
        display: none; position: absolute; bottom: 0; width: 100%; height: 100%; pointer-events: none; z-index: 20;
    }
    .btn {
        position: absolute; bottom: 25px; width: 80px; height: 80px;
        background: rgba(255,255,255,0.25); border: 2px solid rgba(255,255,255,0.6);
        border-radius: 50%; pointer-events: auto; backdrop-filter: blur(4px);
        display: flex; align-items: center; justify-content: center;
        color: white; font-size: 30px; font-weight: bold; user-select: none;
    }
    .btn:active { background: rgba(255,255,255,0.5); transform: scale(0.9); }
    #btn-L { left: 20px; }
    #btn-R { left: 120px; }
    #btn-J { right: 30px; width: 90px; height: 90px; background: rgba(255,60,60,0.3); }

    /* 菜单层 */
    #menu {
        position: absolute; top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(0,0,0,0.85); z-index: 100;
        display: flex; flex-direction: column; align-items: center; justify-content: center;
    }
    .start-btn {
        padding: 15px 60px; font-size: 24px; background: #E040FB; color: white;
        border: none; cursor: pointer; border-radius: 8px;
        box-shadow: 0 4px 0 #AA00FF; margin-top: 20px;
        font-family: monospace;
    }
    .start-btn:active { transform: translateY(4px); box-shadow: none; }
</style>
</head>
<body>

<div id="rotate-hint">
    <div class="icon-spin">📱</div>
    <h2>请旋转手机</h2>
    <p>Landscape Mode Required</p>
</div>

<div id="game-container">
    <canvas id="c"></canvas>
    <div id="score-ui" class="hud">SCORE: 0</div>
    <div id="world-ui" class="hud">WORLD 1-1</div>
    
    <div id="controls">
        <div class="btn" id="btn-L">◀</div>
        <div class="btn" id="btn-R">▶</div>
        <div class="btn" id="btn-J">🚀</div>
    </div>

    <div id="menu">
        <h1 style="color:#fff; font-size:32px; text-shadow:0 3px 0 #000;">SUPER AI KART</h1>
        <h3 style="color:#bbb; font-size:16px; margin-bottom:10px;">V27.0: PC Fix & Physics Tune</h3>
        <button class="start-btn" onclick="startGame()">START GAME</button>
    </div>
</div>

<script>
const canvas = document.getElementById('c');
const ctx = canvas.getContext('2d');

// --- 1. 严格的设备检测 (修复PC打不开的问题) ---
// 只有检测到这些关键字才认为是移动端
const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);

let running = false;
let audioCtx = null;
let loopId = null;

// --- 2. 物理手感调优 (减速版) ---
const PHYSICS = {
    acc: 0.2,       // 加速度 (原0.5 -> 0.2, 起步更稳)
    friction: 0.88, // 摩擦力 (原0.85 -> 0.88, 刹车更快)
    maxSpd: 3.2,    // 最大速度 (原4.5 -> 3.2, 更好控制)
    jumpForce: -10, // 跳跃高度
    gravity: 0.55   // 重力
};

// 关卡配置
const THEMES = [
    { name: "FOREST", bg: "#64B5F6", block: "#81C784" },
    { name: "DESERT", bg: "#FFF176", block: "#FFD54F" }, 
    { name: "SKY",    bg: "#E1F5FE", block: "#ffffff" },
    { name: "CAVE",   bg: "#4E342E", block: "#8D6E63" },
    { name: "SPACE",  bg: "#212121", block: "#616161" },
    { name: "OCEAN",  bg: "#0277BD", block: "#00ACC1" }
];

let state = { level: 0, score: 0, transition: false };
let player = { x:100, y:0, w:32, h:44, dx:0, dy:0, ground:false, jumps:0, dead:false };
let input = { l:false, r:false, j:false, jLock:false };
let blocks = [];
let enemies = [];
let goal = null;
let camX = 0;
let frames = 0;

// 音频
function playTone(freq, type, dur) {
    if(!audioCtx) return;
    const t = audioCtx.currentTime;
    const osc = audioCtx.createOscillator();
    const g = audioCtx.createGain();
    osc.type = type; osc.frequency.setValueAtTime(freq, t);
    g.gain.setValueAtTime(0.05, t); g.gain.exponentialRampToValueAtTime(0.001, t+dur);
    osc.connect(g); g.connect(audioCtx.destination);
    osc.start(t); osc.stop(t+dur);
}

// 关卡生成
function initLevel(idx) {
    blocks = []; enemies = []; goal = null;
    let theme = THEMES[idx % THEMES.length];
    
    // 地面
    blocks.push({x:-200, y:canvas.height-60, w:800, h:100, c: theme.block});
    
    let x = 600;
    // 关卡长度随难度增加
    let endX = 3000 + idx * 500; 
    
    while(x < endX) {
        // 沟壑
        if(Math.random() < 0.2) x += 120;
        
        let w = 200 + Math.random()*300;
        let h = 100;
        blocks.push({x:x, y:canvas.height-60, w:w, h:h, c: theme.block});
        
        // 障碍物/平台
        if(Math.random() < 0.7) {
            let by = canvas.height - 180 - Math.random()*100;
            blocks.push({x:x+50, y:by, w:80, h:30, c: theme.block});
            // 怪物
            if(Math.random() < 0.3) {
                enemies.push({x:x+80, y:canvas.height-100, w:36, h:36, dx:-1.5, type: idx%3, dead:false});
            }
        }
        x += w;
    }
    
    // 终点
    goal = { x: x+200, y: canvas.height-160, w: 80, h: 100 };
    blocks.push({x: x+100, y: canvas.height-60, w: 300, h: 100, c: theme.block});
    
    player.x = 100; player.y = 0; player.dx=0; player.dy=0; player.dead=false; 
    state.transition = false; camX = 0;
}

function update() {
    if(!running) return;
    frames++;
    
    // --- 钻管动画 ---
    if(state.transition) {
        player.y += 3;
        if(player.y > canvas.height) {
            state.level++;
            initLevel(state.level);
        }
        draw();
        requestAnimationFrame(update);
        return;
    }

    // --- 物理计算 (V27 减速版) ---
    if(input.r) player.dx += PHYSICS.acc;
    else if(input.l) player.dx -= PHYSICS.acc;
    else player.dx *= PHYSICS.friction;
    
    // 限制最大速度
    if(player.dx > PHYSICS.maxSpd) player.dx = PHYSICS.maxSpd;
    if(player.dx < -PHYSICS.maxSpd) player.dx = -PHYSICS.maxSpd;
    
    // 跳跃
    if(input.j && !input.jLock) {
        let jumped = false;
        if(player.ground) {
            player.dy = PHYSICS.jumpForce; player.jumps=1; jumped=true;
            playTone(200, 'square', 0.1);
        } else if(player.jumps > 0 && player.jumps < 3) {
            player.dy = PHYSICS.jumpForce * 0.9; player.jumps++; jumped=true;
            playTone(400, 'sawtooth', 0.15); // 二段跳音效
        }
        if(jumped) input.jLock = true;
    }
    if(!input.j) input.jLock = false;

    player.dy += PHYSICS.gravity;
    player.x += player.dx;
    player.y += player.dy;
    
    // 摄像机跟随
    camX += (player.x - canvas.width*0.35 - camX) * 0.1;
    
    // 掉落死亡
    if(player.y > canvas.height + 100) gameOver();

    // 碰撞检测
    player.ground = false;
    blocks.forEach(b => {
        if(b.x > camX+canvas.width || b.x+b.w < camX) return;
        if(colCheck(player, b)) {
            // 简单的 AABB 响应
            let pBottom = player.y + player.h;
            let bBottom = b.y + b.h;
            // 触地
            if(player.dy >= 0 && pBottom - player.dy <= b.y + 10) {
                player.y = b.y - player.h; player.dy = 0; player.ground = true; player.jumps = 0;
            } 
            // 撞头
            else if(player.dy < 0 && player.y - player.dy >= bBottom - 10) {
                player.y = bBottom; player.dy = 0;
            }
            // 侧向
            else if(player.dx > 0) { player.x = b.x - player.w; player.dx = 0; }
            else if(player.dx < 0) { player.x = b.x + b.w; player.dx = 0; }
        }
    });
    
    // 怪物
    enemies.forEach(e => {
        if(e.dead) return;
        e.x += e.dx;
        if(frames % 100 === 0) e.dx *= -1;
        
        if(colCheck(player, e)) {
            // 踩踏判定
            if(player.dy > 0 && player.y + player.h < e.y + e.h * 0.7) {
                e.dead = true; player.dy = -6; state.score += 100;
                playTone(600, 'sine', 0.1);
            } else {
                gameOver();
            }
        }
    });

    // 终点检测
    if(goal && colCheck(player, goal)) {
        if(player.ground && Math.abs(player.x - goal.x) < 20) {
            state.transition = true;
            playTone(800, 'sine', 0.5);
        }
    }

    draw();
    loopId = requestAnimationFrame(update);
}

function colCheck(a, b) {
    return a.x < b.x + b.w && a.x + a.w > b.x && a.y < b.y + b.h && a.y + a.h > b.y;
}

function gameOver() {
    player.dead = true;
    document.getElementById('menu').style.display = 'flex';
    document.querySelector('#menu h1').innerText = "GAME OVER";
}

function draw() {
    // 0. 清屏 & 背景
    let theme = THEMES[state.level % THEMES.length];
    ctx.fillStyle = theme.bg;
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // 1. 砖块
    blocks.forEach(b => {
        if(b.x > camX+canvas.width || b.x+b.w < camX) return;
        ctx.fillStyle = b.c;
        ctx.fillRect(b.x-camX, b.y, b.w, b.h);
        ctx.lineWidth = 2; ctx.strokeStyle = "rgba(0,0,0,0.1)"; 
        ctx.strokeRect(b.x-camX, b.y, b.w, b.h);
    });

    // 2. 终点管子
    if(goal) {
        let gx = goal.x - camX;
        ctx.fillStyle = "#43A047";
        ctx.fillRect(gx, goal.y, goal.w, goal.h); // 管身
        ctx.fillRect(gx-10, goal.y, goal.w+20, 30); // 管口
        ctx.fillStyle = "#fff"; ctx.font="16px Arial"; ctx.fillText("GOAL", gx+18, goal.y+60);
    }

    // 3. 怪物
    enemies.forEach(e => {
        if(e.dead || e.x > camX+canvas.width || e.x+e.w < camX) return;
        ctx.fillStyle = ["#E53935", "#8E24AA", "#3949AB"][e.type];
        ctx.fillRect(e.x-camX, e.y, e.w, e.h);
        // 眼睛
        ctx.fillStyle = "#fff";
        ctx.fillRect(e.x-camX+5, e.y+10, 8, 8);
        ctx.fillRect(e.x-camX+e.w-13, e.y+10, 8, 8);
    });

    // 4. 玩家 (V27 重绘：防止颠倒，结构清晰)
    let px = player.x - camX;
    let py = player.y;
    
    // 火箭喷射 (二段跳/三段跳)
    if(player.jumps > 0 && player.dy < 0) {
        ctx.fillStyle = (frames%6<3) ? "#FFC107" : "#FF5722";
        ctx.beginPath();
        ctx.moveTo(px+10, py+player.h);
        ctx.lineTo(px+player.w-10, py+player.h);
        ctx.lineTo(px+player.w/2, py+player.h+15);
        ctx.fill();
    }
    
    // 腿部动画 (限制幅度，防止穿模倒立)
    let legOffset = 0;
    if(player.ground && Math.abs(player.dx) > 0.1) {
        legOffset = Math.sin(frames * 0.8) * 5; 
    }

    // 绘制身体 (从上到下，绝对坐标)
    // 帽子
    ctx.fillStyle = "#D84315"; 
    ctx.fillRect(px, py, player.w, 10);
    // 脸
    ctx.fillStyle = "#FFCCBC";
    ctx.fillRect(px+4, py+10, player.w-8, 10);
    // 身体
    ctx.fillStyle = "#1565C0";
    ctx.fillRect(px, py+20, player.w, 14);
    // 腿 (左右脚)
    ctx.fillStyle = "#5D4037";
    ctx.fillRect(px+4, py+34 + legOffset, 10, 10); // 左脚
    ctx.fillRect(px+player.w-14, py+34 - legOffset, 10, 10); // 右脚
    
    // UI更新
    document.getElementById('score-ui').innerText = `SCORE: ${state.score}`;
    document.getElementById('world-ui').innerText = `WORLD 1-${state.level+1} (${theme.name})`;
}

// --- 适配逻辑 ---
function checkDevice() {
    // 只有在真的是手机，且真的是竖屏时，才阻断游戏
    if(isMobile && window.innerHeight > window.innerWidth) {
        document.getElementById('rotate-hint').style.display = 'flex';
        document.getElementById('game-container').style.display = 'none';
        if(running) running = false;
    } else {
        document.getElementById('rotate-hint').style.display = 'none';
        document.getElementById('game-container').style.display = 'block';
        resize();
        if(!running && !player.dead && frames > 0) {
            running = true; update();
        }
    }
}
function resize() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
}
window.addEventListener('resize', () => setTimeout(checkDevice, 100));
setInterval(checkDevice, 1000); // 轮询检查

function startGame() {
    audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    document.getElementById('menu').style.display = 'none';
    state.level = 0; state.score = 0;
    initLevel(0);
    running = true;
    checkDevice();
    if(!loopId) update();
}

// 触摸控制
if(isMobile) {
    document.getElementById('controls').style.display = 'block';
    const bindBtn = (id, key) => {
        let btn = document.getElementById(id);
        btn.addEventListener('touchstart', (e)=>{ e.preventDefault(); input[key]=true; });
        btn.addEventListener('touchend', (e)=>{ e.preventDefault(); input[key]=false; });
    };
    bindBtn('btn-L', 'l'); bindBtn('btn-R', 'r'); bindBtn('btn-J', 'j');
}

// 键盘控制
window.addEventListener('keydown', e => {
    if(e.key==='a' || e.key==='ArrowLeft') input.l = true;
    if(e.key==='d' || e.key==='ArrowRight') input.r = true;
    if(e.key==='w' || e.key===' ' || e.key==='ArrowUp') input.j = true;
});
window.addEventListener('keyup', e => {
    if(e.key==='a' || e.key==='ArrowLeft') input.l = false;
    if(e.key==='d' || e.key==='ArrowRight') input.r = false;
    if(e.key==='w' || e.key===' ' || e.key==='ArrowUp') input.j = false;
});

</script>
</body>
</html>
"""

st.components.v1.html(game_html, height=800)
