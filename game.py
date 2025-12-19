import streamlit as st
import streamlit.components.v1 as components
import json

# --- 1. 页面配置 ---
st.set_page_config(
    page_title="Super AI Kart: V24 Stable",
    page_icon="🍄",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 暴力注入 CSS：解决 PC 端画面太大的问题，同时保证移动端全屏
st.markdown("""
    <style>
        #MainMenu, header, footer {visibility: hidden;}
        .block-container {
            padding: 0 !important; margin: 0 !important;
            max-width: 100% !important; overflow: hidden;
        }
        iframe {
            display: block;
            width: 100vw;
            height: 100vh;
            border: none;
        }
    </style>
""", unsafe_allow_html=True)

# --- 2. 游戏核心 HTML ---
game_html = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<style>
    /* 全局复位 */
    * { margin: 0; padding: 0; box-sizing: border-box; -webkit-tap-highlight-color: transparent; }
    body { 
        background: #222; 
        overflow: hidden; 
        font-family: 'Courier New', monospace; 
        display: flex; align-items: center; justify-content: center;
        height: 100vh; width: 100vw;
    }

    /* 🎮 游戏容器：PC端限制大小，移动端全屏 */
    #game-wrapper {
        position: relative;
        background: #5c94fc;
        overflow: hidden;
        box-shadow: 0 0 50px rgba(0,0,0,0.5);
    }

    /* PC 端默认样式：4:3 比例，最大宽度 800px */
    @media (min-width: 769px) {
        #game-wrapper {
            width: 800px;
            height: 600px;
            border: 4px solid #fff;
            border-radius: 8px;
        }
    }

    /* 📱 移动端样式：强制填满，且处理旋转 */
    @media (max-width: 768px) {
        #game-wrapper {
            width: 100%; height: 100%; border: none;
        }
        /* 强制横屏的各种魔法 */
        #game-wrapper.landscape-mode {
            width: 100vh; height: 100vw;
            transform: rotate(90deg);
            transform-origin: top left;
            position: absolute; top: 0; left: 100%;
        }
    }

    canvas { display: block; width: 100%; height: 100%; image-rendering: pixelated; }

    /* UI文字 */
    .hud {
        position: absolute; top: 15px; 
        font-size: 20px; font-weight: bold; color: white; 
        text-shadow: 2px 2px 0 #000; pointer-events: none; z-index: 10;
        font-family: monospace;
    }
    #score-ui { left: 20px; }
    #coin-ui { left: 50%; transform: translateX(-50%); color: #FFD700; }

    /* 虚拟按键 (移动端) */
    #controls {
        display: none; /* 默认隐藏 */
        position: absolute; bottom: 10px; width: 100%; height: 120px;
        pointer-events: none; z-index: 20;
    }
    .btn {
        position: absolute; width: 70px; height: 70px; bottom: 20px;
        background: rgba(255,255,255,0.25); border: 2px solid rgba(255,255,255,0.6);
        border-radius: 50%; pointer-events: auto; backdrop-filter: blur(4px);
        display: flex; align-items: center; justify-content: center;
        font-size: 28px; color: white;
    }
    .btn:active { background: rgba(255,255,255,0.6); transform: scale(0.9); }
    #btn-L { left: 30px; }
    #btn-R { left: 120px; }
    #btn-J { right: 30px; width: 85px; height: 85px; background: rgba(255,50,50,0.3); }

    /* 遮罩层 (开始/结束) */
    #overlay {
        position: absolute; top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(0,0,0,0.85); z-index: 100;
        display: flex; flex-direction: column; align-items: center; justify-content: center;
        text-align: center;
    }
    h1 { color: #ff9800; text-shadow: 3px 3px 0 #000; margin-bottom: 20px; font-size: 40px; }
    p { color: #ccc; margin-bottom: 30px; font-size: 14px; max-width: 80%; }
    
    .action-btn {
        background: #00C853; color: white; border: 3px solid white;
        padding: 12px 30px; font-size: 22px; cursor: pointer;
        font-family: monospace; text-transform: uppercase;
        box-shadow: 0 4px 0 #00600f;
    }
    .action-btn:active { transform: translateY(4px); box-shadow: none; }
    
    .rotate-hint {
        display: none; margin-top: 15px; color: #4fc3f7; font-size: 12px;
    }
</style>
</head>
<body>

<div id="game-wrapper">
    <canvas id="gameCanvas"></canvas>
    
    <div id="score-ui" class="hud">SCORE: 0</div>
    <div id="coin-ui" class="hud">🪙 0</div>

    <div id="controls">
        <div class="btn" id="btn-L">◀</div>
        <div class="btn" id="btn-R">▶</div>
        <div class="btn" id="btn-J">J</div>
    </div>

    <div id="overlay">
        <h1 id="title-text">SUPER AI<br>KART V24</h1>
        <p id="sub-text">PC: 800x600 Fixed<br>Mobile: Auto-Rotate Fixed</p>
        <button class="action-btn" onclick="startGame()">START GAME</button>
        <div class="rotate-hint" id="rotate-hint">ℹ️ 点击开始后将自动横屏</div>
    </div>
</div>

<script>
const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');
const wrapper = document.getElementById('game-wrapper');
let isMobile = /Android|iPhone|iPad|iPod/i.test(navigator.userAgent);
let audioCtx = null;
let loopId = null;
let frames = 0;

// --- 适配逻辑 ---
function resize() {
    // Canvas 分辨率始终跟随容器的物理像素
    // 这里非常重要：必须获取 wrapper 的实际渲染大小，而不是 window
    const rect = wrapper.getBoundingClientRect();
    canvas.width = rect.width;
    canvas.height = rect.height;
}
window.addEventListener('resize', resize);
if(isMobile) {
    document.getElementById('controls').style.display = 'block';
    document.getElementById('rotate-hint').style.display = 'block';
}

// --- 音频系统 ---
const SOUNDS = {
    jump: { f: 150, t: 'square', d: 0.1 },
    coin: { f: 1200, t: 'sine', d: 0.1 },
    stomp: { f: 100, t: 'sawtooth', d: 0.1 },
    bgm: [110, 110, 147, 147, 131, 131, 98, 98]
};
function playSfx(key) {
    if(!audioCtx) return;
    const s = SOUNDS[key];
    const t = audioCtx.currentTime;
    const osc = audioCtx.createOscillator();
    const gain = audioCtx.createGain();
    osc.type = s.t; osc.frequency.setValueAtTime(s.f, t);
    if(key==='jump') osc.frequency.linearRampToValueAtTime(s.f*2, t+s.d);
    gain.gain.setValueAtTime(0.1, t); gain.gain.linearRampToValueAtTime(0, t+s.d);
    osc.connect(gain); gain.connect(audioCtx.destination);
    osc.start(t); osc.stop(t+s.d);
}

// --- 游戏状态与实体 ---
let state = { score:0, coins:0 };
let input = { l:false, r:false, j:false, jPressed:false }; // jPressed 用于防连触
let player = { x:100, y:0, w:36, h:50, dx:0, dy:0, ground:false, jumps:0, dead:false };
let camX = 0;
let blocks = [];
let enemies = [];

class Enemy {
    constructor(x, y, t) {
        this.x = x; this.y = y; this.w = 40; this.h = 40; this.t = t;
        this.dx = -2; this.dead = false;
        this.c = ['#D32F2F', '#388E3C', '#7B1FA2', '#FBC02D'][t % 4];
    }
    update() {
        if(this.dead) return;
        this.x += this.dx;
        // 简单巡逻
        if(frames % 100 === 0) this.dx *= -1;
    }
    draw() {
        if(this.dead) return;
        if(this.x < camX - 50 || this.x > camX + canvas.width + 50) return;
        ctx.fillStyle = this.c;
        ctx.fillRect(this.x - camX, this.y, this.w, this.h);
        // 眼睛
        ctx.fillStyle = 'white';
        let ex = this.dx < 0 ? 5 : 25;
        ctx.fillRect(this.x - camX + ex, this.y + 8, 8, 8);
    }
}

// --- 生成关卡 (防摔死优化版) ---
function initLevel() {
    blocks = []; enemies = [];
    state.score = 0; state.coins = 0;
    
    const gy = canvas.height - 80;
    
    // 1. 安全重生区 (前 500px 绝对平坦)
    blocks.push({x: -100, y: gy, w: 600, h: 200, t: 'floor', c: '#66BB6A'});
    
    // 2. 随机地图
    let tx = 500;
    while(tx < 5000) {
        let gap = Math.random() < 0.15 ? 100 + Math.random()*80 : 0;
        let len = 200 + Math.random()*300;
        
        if(gap > 0) tx += gap;
        
        blocks.push({x: tx, y: gy, w: len, h: 200, t: 'floor', c: '#66BB6A'});
        
        // 装饰与敌人
        if(Math.random() < 0.4) {
            // 空中平台
            let py = gy - (100 + Math.random()*50);
            blocks.push({x: tx+50, y: py, w: 100, h: 40, t: 'brick', c: '#8D6E63'});
            // 敌人
            if(Math.random() < 0.5) enemies.push(new Enemy(tx+80, gy-40, Math.floor(Math.random()*4)));
        }
        
        tx += len;
    }
    
    // 重置玩家 (绝对安全位置)
    player.x = 100; 
    player.y = 0; // 从天而降
    player.dx = 0; 
    player.dy = 0; 
    player.dead = false;
    camX = 0;
}

// --- 核心循环 ---
function update() {
    if(player.dead) return;
    frames++;
    
    // BGM 节奏
    if(audioCtx && frames % 30 === 0) {
        const t = audioCtx.currentTime;
        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        osc.frequency.setValueAtTime(SOUNDS.bgm[Math.floor(frames/30)%8], t);
        gain.gain.setValueAtTime(0.05, t); gain.gain.linearRampToValueAtTime(0, t+0.1);
        osc.connect(gain); gain.connect(audioCtx.destination);
        osc.start(t); osc.stop(t+0.1);
    }

    // 1. 物理计算
    // 左右移动
    let accel = 0.8;
    if(input.r) player.dx += accel;
    else if(input.l) player.dx -= accel;
    else player.dx *= 0.75; // 摩擦力
    
    // 限速
    if(player.dx > 6) player.dx = 6;
    if(player.dx < -6) player.dx = -6;
    
    // 跳跃 (核心修复：三段跳 + 防连按)
    // 只有当 input.j 为 true 且之前没有“锁住”时才触发
    if (input.j && !input.jPressed) {
        let didJump = false;
        if(player.ground) { 
            player.dy = -13; player.jumps = 1; didJump = true; 
        } else if (player.jumps > 0 && player.jumps < 3) {
            player.dy = -11; player.jumps++; didJump = true; // 空中跳跃力度稍小
        }
        
        if(didJump) {
            playSfx('jump');
            input.jPressed = true; // 锁住，直到松开按键
        }
    }
    // 如果松开按键，解锁
    if (!input.j) {
        input.jPressed = false;
    }

    player.dy += 0.6; // 重力
    player.x += player.dx;
    player.y += player.dy;
    
    // 摄像机平滑跟随
    let targetCam = player.x - canvas.width * 0.3;
    if(targetCam < 0) targetCam = 0;
    camX += (targetCam - camX) * 0.15;

    // 掉落死亡检测 (放宽判定)
    if(player.y > canvas.height + 200) gameOver();

    // 2. 碰撞检测
    player.ground = false;
    blocks.forEach(b => {
        // 优化：只检测屏幕附近的砖块
        if(b.x > camX + canvas.width || b.x + b.w < camX) return;
        
        if(AABB(player, b)) {
            // 落地
            if(player.dy > 0 && player.y + player.h - player.dy <= b.y + 20) {
                player.y = b.y - player.h; player.dy = 0; player.ground = true; player.jumps = 0;
            }
            // 顶头
            else if(player.dy < 0 && player.y - player.dy >= b.y + b.h - 20) {
                player.y = b.y + b.h; player.dy = 0;
            }
            // 侧面
            else if(player.dx > 0) { player.x = b.x - player.w; player.dx = 0; }
            else if(player.dx < 0) { player.x = b.x + b.w; player.dx = 0; }
        }
    });

    // 敌人碰撞
    enemies.forEach(e => {
        e.update();
        if(!e.dead && AABB(player, e)) {
            if(player.dy > 0 && player.y + player.h < e.y + e.h * 0.7) {
                e.dead = true; player.dy = -8; state.score += 100; playSfx('stomp');
            } else {
                gameOver();
            }
        }
    });

    draw();
    loopId = requestAnimationFrame(update);
}

function AABB(a, b) {
    return a.x < b.x + b.w && a.x + a.w > b.x && a.y < b.y + b.h && a.y + a.h > b.y;
}

// --- 绘制 ---
function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // 地面/砖块
    blocks.forEach(b => {
        if(b.x > camX + canvas.width || b.x + b.w < camX) return;
        ctx.fillStyle = b.c;
        ctx.fillRect(b.x - camX, b.y, b.w, b.h);
        // 简单的草地装饰
        if(b.t === 'floor') {
             ctx.fillStyle = '#81C784'; ctx.fillRect(b.x - camX, b.y, b.w, 10);
        }
    });

    // 敌人
    enemies.forEach(e => e.draw());

    // 玩家绘制 (带小脚丫)
    let px = player.x - camX;
    let py = player.y;
    
    // 脚步动画计算
    let legOffset = 0;
    if(Math.abs(player.dx) > 0.1 && player.ground) {
        legOffset = Math.sin(frames * 0.5) * 8; // 幅度加大
    }

    // 1. 后脚 (深棕色)
    ctx.fillStyle = '#3E2723';
    ctx.fillRect(px + 8 + legOffset, py + player.h - 8, 10, 8);

    // 2. 身体 (红) & 裤子 (蓝)
    ctx.fillStyle = '#F44336'; ctx.fillRect(px, py + 15, player.w, 20); // 衣
    ctx.fillStyle = '#1565C0'; ctx.fillRect(px, py + 35, player.w, 15); // 裤

    // 3. 前脚 (深棕色 - 相位相反)
    ctx.fillStyle = '#3E2723';
    ctx.fillRect(px + player.w - 18 - legOffset, py + player.h - 8, 10, 8);

    // 4. 头 & 帽子
    ctx.fillStyle = '#FFCC80'; ctx.fillRect(px + 4, py + 8, 28, 18); // 脸
    ctx.fillStyle = '#8D6E63'; ctx.fillRect(px, py, player.w, 10); // 帽顶
    ctx.fillRect(player.dx >= 0 ? px+5 : px-5, py+8, player.w, 5); // 帽檐

    // UI 更新
    document.getElementById('score-ui').innerText = `SCORE: ${state.score}`;
}

// --- 游戏控制 ---
function startGame() {
    // 激活音频
    audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    
    // 隐藏菜单
    document.getElementById('overlay').style.display = 'none';
    
    // 移动端：强制触发横屏样式
    if(isMobile) {
        wrapper.classList.add('landscape-mode');
        // 延时一下等旋转动画结束再初始化尺寸
        setTimeout(() => {
            resize();
            initLevel();
            if(loopId) cancelAnimationFrame(loopId);
            update();
        }, 500);
    } else {
        resize();
        initLevel();
        if(loopId) cancelAnimationFrame(loopId);
        update();
    }
}

function gameOver() {
    player.dead = true;
    document.getElementById('overlay').style.display = 'flex';
    document.querySelector('#overlay h1').innerHTML = "GAME OVER";
    document.querySelector('#overlay button').innerText = "TRY AGAIN";
}

// 输入监听
const bindKey = (id, k) => {
    let el = document.getElementById(id);
    el.addEventListener('touchstart', e => { e.preventDefault(); input[k] = true; el.style.background = 'rgba(255,255,255,0.6)'; });
    el.addEventListener('touchend', e => { e.preventDefault(); input[k] = false; el.style.background = ''; });
};
if(isMobile) {
    bindKey('btn-L', 'l'); bindKey('btn-R', 'r'); bindKey('btn-J', 'j');
}

window.addEventListener('keydown', e => {
    if(e.code==='ArrowLeft'||e.key==='a') input.l = true;
    if(e.code==='ArrowRight'||e.key==='d') input.r = true;
    if(e.code==='Space'||e.key==='w'||e.code==='ArrowUp') input.j = true;
});
window.addEventListener('keyup', e => {
    if(e.code==='ArrowLeft'||e.key==='a') input.l = false;
    if(e.code==='ArrowRight'||e.key==='d') input.r = false;
    if(e.code==='Space'||e.key==='w'||e.code==='ArrowUp') input.j = false;
});

</script>
</body>
</html>
"""

st.components.v1.html(game_html, height=700)
