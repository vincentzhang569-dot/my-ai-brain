import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Super AI Kart: V26 Universes",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 暴力清除边距，确保全屏
st.markdown("""
    <style>
        #MainMenu, header, footer {visibility: hidden;}
        .block-container { padding: 0 !important; margin: 0 !important; max-width: 100% !important; }
        iframe { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; border: none; z-index: 9999; }
    </style>
""", unsafe_allow_html=True)

game_html = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<style>
    * { margin: 0; padding: 0; box-sizing: border-box; -webkit-tap-highlight-color: transparent; }
    body { background: #000; overflow: hidden; font-family: 'Verdana', sans-serif; }

    /* 游戏主容器 */
    #game-container {
        position: absolute; top: 0; left: 0; width: 100%; height: 100%;
        display: none; /* 默认隐藏，等旋转 */
    }
    canvas { display: block; width: 100%; height: 100%; }

    /* 旋转提示 */
    #rotate-hint {
        position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        background: #111; color: #fff; z-index: 9999;
        display: flex; flex-direction: column; align-items: center; justify-content: center;
        text-align: center;
    }
    .icon-spin { font-size: 80px; margin-bottom: 20px; animation: spin 2s infinite; }
    @keyframes spin { 0% { transform: rotate(0deg); } 25% { transform: rotate(-90deg); } 100% { transform: rotate(-90deg); } }

    /* HUD */
    .hud { position: absolute; top: 20px; color: white; font-weight: bold; font-size: 20px; text-shadow: 2px 2px 0 #000; pointer-events: none; z-index: 10; }
    #score-ui { left: 20px; }
    #world-ui { right: 20px; color: #FFD700; }

    /* 移动端控制 */
    #controls {
        display: none; position: absolute; bottom: 0; width: 100%; height: 100%; pointer-events: none; z-index: 20;
    }
    .btn {
        position: absolute; bottom: 20px; width: 85px; height: 85px;
        background: rgba(255,255,255,0.2); border: 2px solid rgba(255,255,255,0.5);
        border-radius: 50%; pointer-events: auto; backdrop-filter: blur(4px);
        display: flex; align-items: center; justify-content: center;
        color: white; font-size: 32px;
    }
    .btn:active { background: rgba(255,255,255,0.5); transform: scale(0.92); }
    #btn-L { left: 30px; }
    #btn-R { left: 130px; }
    #btn-J { right: 30px; width: 95px; height: 95px; background: rgba(255,80,80,0.3); }

    /* 菜单遮罩 */
    #menu {
        position: absolute; top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(0,0,0,0.85); z-index: 100;
        display: flex; flex-direction: column; align-items: center; justify-content: center;
    }
    .start-btn {
        padding: 15px 50px; font-size: 28px; background: #2196F3; color: white;
        border: 4px solid white; cursor: pointer; border-radius: 50px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.5); font-weight: bold;
    }
</style>
</head>
<body>

<div id="rotate-hint">
    <div class="icon-spin">📱</div>
    <h2>请横屏游戏</h2>
    <p>Please Rotate Your Device</p>
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
        <h1 style="color:#fff; font-size:40px; margin-bottom:10px; text-shadow:0 5px 0 #000;">SUPER AI KART</h1>
        <p style="color:#4fc3f7; margin-bottom:30px; font-size:18px;">V26.0: 6 Universes & BGM Restore</p>
        <button class="start-btn" onclick="startGame()">START GAME</button>
    </div>
</div>

<script>
// --- 核心变量 ---
const canvas = document.getElementById('c');
const ctx = canvas.getContext('2d');
let isMobile = /Android|iPhone|iPad/i.test(navigator.userAgent);
let running = false;
let audioCtx = null;
let loopId = null;

// --- 关卡配置 (6种地形) ---
const THEMES = [
    { name: "FOREST", bg: "#5c94fc", block: "#66BB6A", note: 440 }, // 1. 森林
    { name: "DESERT", bg: "#FFECB3", block: "#FFCA28", note: 523 }, // 2. 沙漠
    { name: "SKY",    bg: "#E1F5FE", block: "#ffffff", note: 587 }, // 3. 天空
    { name: "OCEAN",  bg: "#01579B", block: "#00ACC1", note: 392 }, // 4. 深海
    { name: "CAVE",   bg: "#3E2723", block: "#795548", note: 330 }, // 5. 地下
    { name: "SPACE",  bg: "#000000", block: "#424242", note: 659 }  // 6. 星空
];

let gameState = { 
    level: 0, 
    score: 0, 
    coins: 0,
    transitioning: false 
};

// --- 音频引擎 (BGM + 音效) ---
let nextNoteTime = 0;
let noteIndex = 0;
// 简单的旋律库 (频率数组)
const MELODIES = [
    [330, 330, 330, 262, 330, 392, 196], // Mario Style
    [523, 587, 659, 587, 523, 494, 440], // Desert Scale
    [659, 880, 659, 587, 523, 440, 523], // Sky High
    [196, 262, 330, 392, 330, 262, 196], // Ocean Walts
    [130, 146, 155, 146, 130, 110, 98],  // Cave Deep
    [880, 784, 698, 587, 523, 440, 392]  // Space
];

function initAudio() {
    if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    if (audioCtx.state === 'suspended') audioCtx.resume();
}

function playTone(freq, type, dur, vol=0.1) {
    if(!audioCtx) return;
    const t = audioCtx.currentTime;
    const osc = audioCtx.createOscillator();
    const gain = audioCtx.createGain();
    osc.type = type; 
    osc.frequency.setValueAtTime(freq, t);
    gain.gain.setValueAtTime(vol, t);
    gain.gain.exponentialRampToValueAtTime(0.01, t + dur);
    osc.connect(gain); gain.connect(audioCtx.destination);
    osc.start(t); osc.stop(t + dur);
}

function updateMusic() {
    if(!audioCtx || gameState.transitioning) return;
    if (audioCtx.currentTime >= nextNoteTime) {
        const melody = MELODIES[gameState.level % MELODIES.length];
        const freq = melody[noteIndex % melody.length];
        // 播放背景音符
        playTone(freq, 'triangle', 0.2, 0.05);
        nextNoteTime = audioCtx.currentTime + 0.3; // 节奏
        noteIndex++;
    }
}

// --- 游戏实体 ---
let player = { x:100, y:0, w:36, h:50, dx:0, dy:0, ground:false, jumps:0, dead:false };
let input = { l:false, r:false, j:false, jLock:false };
let camX = 0;
let blocks = [];
let enemies = [];
let winPipe = null; // 终点管子

class Enemy {
    constructor(x, y, type) {
        this.x = x; this.y = y; this.w = 40; this.h = 40; this.t = type;
        this.dx = -2; this.dead = false;
        // 颜色区分怪物: 0=Goomba(红), 1=Slime(绿), 2=Bat(紫)
        this.c = ['#D32F2F', '#7CB342', '#7E57C2'][type % 3];
    }
    update() {
        if(this.dead) return;
        this.x += this.dx;
        // 简单的巡逻 AI
        if(frames % 120 === 0) this.dx *= -1;
        // 蝙蝠飞行动画
        if(this.t === 2) this.y += Math.sin(frames * 0.1) * 2;
    }
    draw() {
        if(this.dead) return;
        if(this.x < camX-50 || this.x > camX+canvas.width+50) return;
        ctx.fillStyle = this.c;
        ctx.fillRect(this.x-camX, this.y, this.w, this.h);
        // 眼睛
        ctx.fillStyle = '#fff';
        let ex = this.dx < 0 ? 5 : 25;
        ctx.fillRect(this.x-camX+ex, this.y+10, 10, 10);
    }
}

// --- 关卡生成 ---
function initLevel(levelIdx) {
    blocks = []; enemies = [];
    let theme = THEMES[levelIdx % THEMES.length];
    
    // 1. 安全起跑线
    blocks.push({x:-200, y:canvas.height-80, w:1000, h:100, c: theme.block});
    
    // 2. 随机生成路段
    let x = 800;
    let endX = 4000; // 关卡长度
    
    while(x < endX) {
        // 沟壑 (星空/天空图沟壑更多)
        if(Math.random() < 0.2) x += 150;
        
        let w = 300 + Math.random()*400;
        blocks.push({x:x, y:canvas.height-80, w:w, h:100, c: theme.block});
        
        // 装饰与怪物
        if(Math.random() < 0.6) {
            // 浮空砖
            let py = canvas.height - 200 - Math.random()*100;
            blocks.push({x:x+100, y:py, w:80, h:40, c: theme.block});
            // 怪物
            if(Math.random() < 0.4) {
                enemies.push(new Enemy(x+150, canvas.height-120, Math.floor(Math.random()*3)));
            }
        }
        x += w;
    }
    
    // 3. 终点水管
    winPipe = { x: x + 200, y: canvas.height - 180, w: 80, h: 100 };
    // 水管底座
    blocks.push({x: x + 100, y: canvas.height-80, w: 400, h: 100, c: theme.block});
    
    // 重置主角
    player.x = 100; player.y = 0; player.dx = 0; player.dy = 0; 
    player.dead = false; gameState.transitioning = false;
    camX = 0;
}

let frames = 0;

function update() {
    if(!running) return;
    frames++;
    
    updateMusic(); // 播放BGM
    
    // --- 钻管过关逻辑 ---
    if(gameState.transitioning) {
        // 下潜动画
        player.y += 2;
        player.h -= 1; // 变扁
        if(player.h <= 0) {
            // 切换下一关
            gameState.level++;
            initLevel(gameState.level);
        }
        draw();
        requestAnimationFrame(update);
        return;
    }

    // --- 物理引擎 (减速优化版) ---
    // 移动端/PC 通用减速
    let acc = 0.5; // 加速度减小
    let friction = 0.85; // 摩擦力增大
    let maxSpd = 4.5; // 最大速度降低 (原6.0)

    if(input.r) player.dx += acc;
    else if(input.l) player.dx -= acc;
    else player.dx *= friction;
    
    if(player.dx > maxSpd) player.dx = maxSpd;
    if(player.dx < -maxSpd) player.dx = -maxSpd;
    
    // 跳跃
    if(input.j && !input.jLock) {
        let jumped = false;
        if(player.ground) {
            player.dy = -11; player.jumps = 1; jumped = true;
            playTone(150, 'square', 0.1);
        } else if(player.jumps > 0 && player.jumps < 3) {
            // 多段跳
            player.dy = -10; player.jumps++; jumped = true;
            playTone(250 + player.jumps*50, 'sawtooth', 0.2); // 火箭音效
        }
        if(jumped) input.jLock = true;
    }
    if(!input.j) input.jLock = false;

    player.dy += 0.5; // 重力
    player.x += player.dx;
    player.y += player.dy;
    
    // 摄像机
    camX += (player.x - canvas.width*0.3 - camX) * 0.1;
    
    // 死亡判定
    if(player.y > canvas.height + 100) {
        player.dead = true;
        document.getElementById('menu').style.display = 'flex';
        document.querySelector('#menu h1').innerText = "GAME OVER";
    }

    // --- 碰撞检测 ---
    player.ground = false;
    
    // 1. 地形碰撞
    blocks.forEach(b => {
        if(AABB(player, b)) {
            if(player.dy > 0 && player.y+player.h-player.dy <= b.y+25) {
                player.y = b.y - player.h; player.dy = 0; player.ground = true; player.jumps = 0;
            } else if(player.dy < 0 && player.y-player.dy >= b.y+b.h-20) {
                player.y = b.y + b.h; player.dy = 0;
            } else if(player.dx > 0) { player.x = b.x - player.w; player.dx = 0; }
            else if(player.dx < 0) { player.x = b.x + b.w; player.dx = 0; }
        }
    });

    // 2. 怪物碰撞
    enemies.forEach(e => {
        e.update();
        if(AABB(player, e) && !e.dead) {
            // 踩头
            if(player.dy > 0 && player.y + player.h < e.y + e.h*0.7) {
                e.dead = true; player.dy = -7; gameState.score += 200;
                playTone(100, 'square', 0.1);
            } else {
                player.dead = true; // 碰到死
                document.getElementById('menu').style.display = 'flex';
                document.querySelector('#menu h1').innerText = "GAME OVER";
            }
        }
    });
    
    // 3. 终点水管检测
    if(winPipe && AABB(player, winPipe)) {
        // 站在水管口
        if(player.ground && Math.abs(player.x - winPipe.x) < 30) {
             gameState.transitioning = true;
             playTone(600, 'sine', 1.0); // 钻管音效
        }
    }

    draw();
    loopId = requestAnimationFrame(update);
}

function AABB(r1, r2) {
    return r1.x < r2.x + r2.w && r1.x + r1.w > r2.x &&
           r1.y < r2.y + r2.h && r1.y + r1.h > r2.y;
}

// --- 绘制渲染 ---
function draw() {
    let theme = THEMES[gameState.level % THEMES.length];
    
    // 1. 背景 (纯色 + 星星/云朵 简化版)
    ctx.fillStyle = theme.bg;
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // 2. 砖块
    blocks.forEach(b => {
        if(b.x > camX+canvas.width || b.x+b.w < camX) return;
        ctx.fillStyle = b.c;
        ctx.fillRect(b.x-camX, b.y, b.w, b.h);
        // 纹理线
        ctx.strokeStyle = "rgba(0,0,0,0.2)"; ctx.lineWidth = 2;
        ctx.strokeRect(b.x-camX, b.y, b.w, b.h);
    });

    // 3. 终点水管
    if(winPipe) {
        let px = winPipe.x - camX;
        // 管身
        ctx.fillStyle = '#00C853';
        ctx.fillRect(px, winPipe.y, winPipe.w, winPipe.h);
        // 管口
        ctx.fillRect(px-10, winPipe.y, winPipe.w+20, 30);
        ctx.fillStyle = '#000'; ctx.font="20px Arial"; ctx.fillText("GOAL", px+15, winPipe.y+70);
    }
    
    // 4. 怪物
    enemies.forEach(e => e.draw());

    // 5. 玩家绘制
    let px = player.x - camX;
    let py = player.y;

    // --- 火箭火焰 (Jet Flame) ---
    // 只有在二段跳/三段跳且上升时显示
    if(player.jumps > 0 && player.dy < 0) {
        ctx.fillStyle = (frames % 4 < 2) ? '#FFEB3B' : '#FF5722'; // 黄红交替
        ctx.beginPath();
        ctx.moveTo(px + 10, py + player.h);
        ctx.lineTo(px + player.w - 10, py + player.h);
        ctx.lineTo(px + player.w / 2, py + player.h + 20); // 喷射长度
        ctx.fill();
    }

    // 脚步动画
    let legL = 0, legR = 0;
    if(player.ground && Math.abs(player.dx) > 0.1) {
        legL = Math.sin(frames * 0.5) * 6;
        legR = Math.sin(frames * 0.5 + Math.PI) * 6;
    }

    // 绘制小人
    ctx.fillStyle = '#3E2723'; // 鞋
    ctx.fillRect(px+5, py+player.h-8+legL, 10, 8); // 左
    ctx.fillRect(px+player.w-15, py+player.h-8+legR, 10, 8); // 右
    
    ctx.fillStyle = '#D32F2F'; ctx.fillRect(px, py+14, player.w, 20); // 衣
    ctx.fillStyle = '#1976D2'; ctx.fillRect(px, py+34, player.w, 16); // 裤
    ctx.fillStyle = '#FFCC80'; ctx.fillRect(px+4, py+6, 28, 18); // 脸
    ctx.fillStyle = '#B71C1C'; ctx.fillRect(px, py, player.w, 8); // 帽顶
    ctx.fillRect(player.dx>=0?px+6:px-6, py+6, player.w, 4); // 帽檐

    // UI
    document.getElementById('score-ui').innerText = `SCORE: ${gameState.score}`;
    document.getElementById('world-ui').innerText = `WORLD 1-${gameState.level+1} (${theme.name})`;
}

// --- 控制逻辑 ---
function checkOrientation() {
    if(isMobile && window.innerHeight > window.innerWidth) {
        document.getElementById('rotate-hint').style.display = 'flex';
        document.getElementById('game-container').style.display = 'none';
        running = false;
    } else {
        document.getElementById('rotate-hint').style.display = 'none';
        document.getElementById('game-container').style.display = 'block';
        resize();
        if(!running && !player.dead && frames > 0) running = true; 
    }
}
function resize() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
}
window.addEventListener('resize', () => setTimeout(checkOrientation, 200));

function startGame() {
    initAudio();
    document.getElementById('menu').style.display = 'none';
    gameState.level = 0;
    initLevel(0);
    running = true;
    checkOrientation();
    if(!loopId) update();
}

// 触摸事件
const bind = (id, k) => {
    let b = document.getElementById(id);
    b.addEventListener('touchstart', e=>{e.preventDefault(); input[k]=true; b.style.opacity=0.5;});
    b.addEventListener('touchend', e=>{e.preventDefault(); input[k]=false; b.style.opacity=1;});
}
if(isMobile) {
    document.getElementById('controls').style.display = 'block';
    bind('btn-L', 'l'); bind('btn-R', 'r'); bind('btn-J', 'j');
}
window.addEventListener('keydown', e=>{
    if(e.key==='a') input.l=true; if(e.key==='d') input.r=true; if(e.key==='w'||e.code==='Space') input.j=true;
});
window.addEventListener('keyup', e=>{
    if(e.key==='a') input.l=false; if(e.key==='d') input.r=false; if(e.key==='w'||e.code==='Space') input.j=false;
});

</script>
</body>
</html>
"""

st.components.v1.html(game_html, height=800)
