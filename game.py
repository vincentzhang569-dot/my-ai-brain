import streamlit as st
import streamlit.components.v1 as components
import json

# --- 1. 页面配置 ---
st.set_page_config(
    page_title="Super AI Kart: V23 Final",
    page_icon="🍄",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 暴力注入 CSS，清除 Streamlit 所有默认边距，确保 iframe 铺满
st.markdown("""
    <style>
        /* 隐藏 Streamlit 头部尾部 */
        #MainMenu, header, footer {visibility: hidden;}
        /* 清除主容器内边距 */
        .block-container {
            padding-top: 0rem !important;
            padding-bottom: 0rem !important;
            padding-left: 0rem !important;
            padding-right: 0rem !important;
            margin: 0 !important;
            max-width: 100% !important;
        }
        /* iframe 强制全屏 */
        iframe {
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            border: none;
            z-index: 9999;
        }
        /* 隐藏滚动条 */
        ::-webkit-scrollbar { display: none; }
    </style>
""", unsafe_allow_html=True)

# --- 2. 游戏核心代码 ---
game_html = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<style>
    /* 基础重置 */
    * { margin: 0; padding: 0; box-sizing: border-box; -webkit-tap-highlight-color: transparent; }
    body { background: #000; overflow: hidden; font-family: 'Courier New', monospace; touch-action: none; }

    /* 游戏画布容器 */
    #game-container {
        position: absolute; top: 0; left: 0; width: 100%; height: 100%;
        background: #5c94fc; /* 天空蓝 */
        transition: transform 0.3s;
        transform-origin: center center;
    }

    canvas { display: block; width: 100%; height: 100%; image-rendering: pixelated; }

    /* UI 层 */
    #ui-layer {
        position: absolute; top: 0; left: 0; width: 100%; height: 100%;
        pointer-events: none; z-index: 10;
    }
    
    .hud {
        position: absolute; top: 10px; 
        font-size: 24px; font-weight: bold; color: white; 
        text-shadow: 2px 2px 0 #000;
        pointer-events: none;
    }
    #score-display { left: 20px; }
    #coin-display { left: 50%; transform: translateX(-50%); color: #FFD700; }
    #world-display { right: 20px; }

    /* 虚拟按键 (默认隐藏，JS检测触摸屏开启) */
    #controls {
        display: none;
        position: absolute; bottom: 20px; width: 100%; height: 120px;
        pointer-events: none;
    }
    .btn {
        position: absolute; width: 70px; height: 70px; bottom: 10px;
        background: rgba(255,255,255,0.2); border: 2px solid rgba(255,255,255,0.6);
        border-radius: 50%; pointer-events: auto; backdrop-filter: blur(2px);
        display: flex; align-items: center; justify-content: center;
        font-size: 30px; color: white; user-select: none;
    }
    .btn:active { background: rgba(255,255,255,0.5); transform: scale(0.95); }
    #btn-left { left: 30px; }
    #btn-right { left: 120px; }
    #btn-jump { right: 30px; width: 80px; height: 80px; background: rgba(255,0,0,0.2); }

    /* 移动端横屏强制层 */
    #mobile-rotate-overlay {
        display: none; /* 默认隐藏 */
        position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(0,0,0,0.95); z-index: 99999;
        flex-direction: column; align-items: center; justify-content: center;
        color: white; text-align: center;
    }
    #rotate-confirm-btn {
        margin-top: 20px; padding: 10px 30px; background: #00C853; 
        border: none; color: white; font-size: 20px; border-radius: 5px;
    }

    /* 启动/死亡 遮罩 */
    #menu-overlay {
        position: absolute; top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(0,0,0,0.8); z-index: 100;
        display: flex; flex-direction: column; align-items: center; justify-content: center;
    }
    h1 { font-size: 50px; color: #ff9800; text-shadow: 4px 4px 0 #000; margin-bottom: 10px; text-align:center;}
    button.main-btn {
        padding: 15px 40px; font-size: 28px; background: #e91e63; color: white;
        border: 4px solid white; cursor: pointer; font-family: monospace;
        text-transform: uppercase; box-shadow: 0 6px 0 #880e4f;
    }
    button.main-btn:active { transform: translateY(4px); box-shadow: 0 2px 0 #880e4f; }

</style>
</head>
<body>

<div id="game-container">
    <canvas id="gameCanvas"></canvas>
    <div id="ui-layer">
        <div id="score-display" class="hud">SCORE: 0</div>
        <div id="coin-display" class="hud">🪙 0</div>
        <div id="world-display" class="hud">WORLD 1-1</div>
        
        <div id="controls">
            <div class="btn" id="btn-left">◀</div>
            <div class="btn" id="btn-right">▶</div>
            <div class="btn" id="btn-jump">J</div>
        </div>
    </div>
</div>

<div id="menu-overlay">
    <h1>SUPER AI KART<br>V23.0</h1>
    <p style="color:#ddd; margin-bottom:20px;">Monsters & Music Restored</p>
    <button class="main-btn" onclick="startGame()">START GAME</button>
</div>

<div id="mobile-rotate-overlay">
    <h2>📱 移动端检测</h2>
    <p>为了最佳体验，请点击下方按钮<br>并横持手机</p>
    <button id="rotate-confirm-btn" onclick="enableLandscape()">进入横屏模式</button>
</div>

<script>
// --- 全局变量 ---
const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');
const container = document.getElementById('game-container');
let audioCtx = null;
let loopId = null;
let frames = 0;
let camX = 0;
let isMobile = /Android|iPhone|iPad|iPod/i.test(navigator.userAgent);
let isLandscape = false;

// --- 音频系统 (修复无声) ---
// 简单的合成器，不需要加载外部文件，保证 100% 有声音
const SOUNDS = {
    jump: { type: 'square', freq: 150, ramp: 300, dur: 0.1 },
    coin: { type: 'sine', freq: 1200, ramp: 1800, dur: 0.15 },
    stomp: { type: 'sawtooth', freq: 100, ramp: 50, dur: 0.1 },
    powerup: { type: 'triangle', freq: 300, ramp: 600, dur: 0.3 },
    bgm_bass: [110, 110, 146, 146, 130, 130, 98, 98] // 简单的低音循环
};

function initAudio() {
    if(!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    if(audioCtx.state === 'suspended') audioCtx.resume();
}

function playSfx(name) {
    if(!audioCtx) return;
    const s = SOUNDS[name];
    const t = audioCtx.currentTime;
    const osc = audioCtx.createOscillator();
    const gain = audioCtx.createGain();
    
    osc.type = s.type;
    osc.frequency.setValueAtTime(s.freq, t);
    osc.frequency.linearRampToValueAtTime(s.ramp, t + s.dur);
    
    gain.gain.setValueAtTime(0.1, t);
    gain.gain.exponentialRampToValueAtTime(0.01, t + s.dur);
    
    osc.connect(gain);
    gain.connect(audioCtx.destination);
    osc.start(t);
    osc.stop(t + s.dur);
}

// 极简 BGM 循环
function updateMusic() {
    if (!audioCtx || frames % 30 !== 0) return; // 每半秒响一次
    const t = audioCtx.currentTime;
    const note = SOUNDS.bgm_bass[(Math.floor(frames/30)) % 8];
    const osc = audioCtx.createOscillator();
    const gain = audioCtx.createGain();
    osc.type = 'triangle';
    osc.frequency.setValueAtTime(note, t);
    gain.gain.setValueAtTime(0.05, t);
    gain.gain.linearRampToValueAtTime(0, t + 0.2);
    osc.connect(gain); gain.connect(audioCtx.destination);
    osc.start(t); osc.stop(t + 0.2);
}

// --- 游戏对象定义 ---
const PHYS = { g: 0.6, fric: 0.8, acc: 0.8, maxSpd: 6.0, jump: -13 };

let state = { score: 0, coins: 0, level: 1 };
let input = { left: false, right: false, jump: false };
let player = { x: 100, y: 0, w: 40, h: 56, dx: 0, dy: 0, grounded: false, dead: false, big: false, jumpCount: 0 };

let blocks = [];
let enemies = [];
let items = [];
let particles = [];

class Enemy {
    constructor(x, y, type) {
        this.x = x; this.y = y; this.w = 40; this.h = 40;
        this.type = type; // 0:Walker, 1:Slime, 2:Bat, 3:Spiky, 4:Bird
        this.dx = -2; this.dy = 0; this.dead = false;
        this.startY = y;
        
        // 颜色定义
        const colors = ['#8D6E63', '#66BB6A', '#7E57C2', '#2E7D32', '#FBC02D'];
        this.color = colors[type];
    }
    update() {
        if(this.dead) return;
        
        // 行为逻辑
        if(this.type === 2 || this.type === 4) { // 飞行单位
            this.x += this.dx;
            this.y = this.startY + Math.sin(frames * 0.05) * 50;
        } else { // 地面单位
            this.dy += PHYS.g;
            this.x += this.dx;
            this.y += this.dy;
            
            // 地面碰撞
            let landed = false;
            blocks.forEach(b => {
                if(this.x < b.x + b.w && this.x + this.w > b.x && this.y + this.h >= b.y && this.y + this.h <= b.y + 20) {
                    this.y = b.y - this.h; this.dy = 0; landed = true;
                }
            });
            if(this.type === 1 && landed) this.dy = -4; // 史莱姆跳跃
        }
        
        if(Math.abs(this.x - player.x) > 1200) return; // 太远不动
        if(this.x < camX - 100) return; 
    }
    draw(ctx, camX) {
        if(this.dead) return;
        ctx.fillStyle = this.color;
        ctx.fillRect(this.x - camX, this.y, this.w, this.h);
        // 眼睛
        ctx.fillStyle = 'white';
        if(this.dx < 0) ctx.fillRect(this.x - camX + 5, this.y + 10, 10, 10);
        else ctx.fillRect(this.x - camX + 25, this.y + 10, 10, 10);
    }
}

// --- 关卡生成 (修复：恢复丰富的生成逻辑) ---
function generateLevel() {
    blocks = []; enemies = []; items = []; particles = [];
    state.score = 0; state.coins = 0;
    
    const floorY = canvas.height - 80;
    
    // 1. 地面与坑
    let x = 0;
    while(x < 6000) {
        // 10% 概率生成坑 (50-150宽)，起点不生成
        if(x > 300 && Math.random() < 0.1) {
            x += 100 + Math.random() * 80;
        }
        
        // 生成一段地面
        let len = 200 + Math.random() * 400;
        blocks.push({x:x, y:floorY, w:len, h:100, type:'floor', c:'#65e069'});
        
        // 2. 地面装饰与敌人
        if(x > 300) {
            // 生成水管
            if(Math.random() < 0.3) {
                let ph = 50 + Math.random() * 50;
                blocks.push({x: x + 100, y: floorY - ph, w: 50, h: ph, type:'pipe', c:'#388E3C'});
                // 水管上的食人花(刺龟)
                if(Math.random() < 0.5) enemies.push(new Enemy(x + 105, floorY - ph - 40, 3));
            }
            
            // 生成空中砖块
            let platformStart = x + 200;
            if(platformStart < x + len - 100) {
                let py = floorY - 120;
                for(let k=0; k<3; k++) {
                    if(Math.random() < 0.7) {
                        let isQ = Math.random() < 0.3;
                        blocks.push({
                            x: platformStart + k*50, y: py, w: 50, h: 50, 
                            type: isQ ? 'qbox' : 'brick', 
                            c: isQ ? '#FFD54F' : '#8D6E63',
                            active: true
                        });
                        // 砖块上的敌人
                        if(Math.random() < 0.2) enemies.push(new Enemy(platformStart + k*50, py - 40, 1));
                    }
                }
            }
            
            // 地面敌人
            if(Math.random() < 0.6) {
                enemies.push(new Enemy(x + 300, floorY - 50, 0)); // Walker
            }
            // 空中敌人
            if(Math.random() < 0.2) {
                enemies.push(new Enemy(x + 400, floorY - 200, 2)); // Bat
            }
        }
        x += len;
    }
    
    player.x = 100; player.y = 0; player.dx = 0; player.dy = 0; player.dead = false;
    camX = 0;
}

// --- 核心更新循环 ---
function update() {
    if(player.dead) return;
    
    updateMusic(); // BGM
    frames++;
    
    // 物理
    if(input.right) player.dx += PHYS.acc;
    else if(input.left) player.dx -= PHYS.acc;
    else player.dx *= PHYS.fric;
    
    if(player.dx > PHYS.maxSpd) player.dx = PHYS.maxSpd;
    if(player.dx < -PHYS.maxSpd) player.dx = -PHYS.maxSpd;
    
    if(input.jump) {
        if(player.grounded) { player.dy = PHYS.jump; player.grounded = false; player.jumpCount=1; playSfx('jump'); }
        else if(player.jumpCount > 0 && player.jumpCount < 2) { player.dy = PHYS.jump * 0.8; player.jumpCount++; playSfx('jump'); } // 二段跳
        input.jump = false;
    }
    
    player.dy += PHYS.g;
    player.x += player.dx;
    player.y += player.dy;
    
    // 摄像机
    camX += (player.x - canvas.width * 0.3 - camX) * 0.1;
    if(camX < 0) camX = 0;
    
    // 掉落死亡
    if(player.y > canvas.height + 100) die();
    
    // 碰撞检测
    player.grounded = false;
    blocks.forEach(b => {
        if(b.x - camX > canvas.width || b.x + b.w - camX < 0) return; // 剔除屏幕外
        
        if(player.x < b.x + b.w && player.x + player.w > b.x && player.y < b.y + b.h && player.y + player.h > b.y) {
            // 落地
            if(player.dy > 0 && player.y + player.h - player.dy <= b.y + 20) {
                player.y = b.y - player.h; player.dy = 0; player.grounded = true; player.jumpCount = 0;
            }
            // 顶头
            else if(player.dy < 0 && player.y - player.dy >= b.y + b.h - 20) {
                player.y = b.y + b.h; player.dy = 0;
                // 顶砖块逻辑
                if(b.type === 'qbox' && b.active) {
                    b.active = false; b.c = '#6D4C41';
                    state.coins++; state.score += 100; playSfx('coin');
                    items.push({x: b.x, y: b.y - 40, w: 40, h: 40, type: 'mushroom', dy: -3});
                }
            }
            // 侧滑
            else if(player.dx > 0) { player.x = b.x - player.w; player.dx = 0; }
            else if(player.dx < 0) { player.x = b.x + b.w; player.dx = 0; }
        }
    });
    
    // 道具逻辑
    items.forEach((it, idx) => {
        it.y += it.dy; it.dy += 0.5;
        if(player.x < it.x + it.w && player.x + player.w > it.x && player.y < it.y + it.h && player.y + player.h > it.y) {
            // 吃到蘑菇
            player.big = true; player.h = 70; playSfx('powerup');
            items.splice(idx, 1);
        }
    });
    
    // 敌人逻辑
    enemies.forEach(e => {
        e.update();
        // 玩家碰敌人
        if(!e.dead && player.x < e.x + e.w && player.x + player.w > e.x && player.y < e.y + e.h && player.y + player.h > e.y) {
            // 踩踏
            if(player.dy > 0 && player.y + player.h < e.y + e.h * 0.6) {
                e.dead = true; player.dy = -8; state.score += 200; playSfx('stomp');
            } else {
                // 受伤
                if(player.big) { player.big = false; player.h = 56; player.dy = -5; e.x += 50; playSfx('stomp'); } // 变小弹开
                else { die(); }
            }
        }
    });

    draw();
    loopId = requestAnimationFrame(update);
}

function die() {
    player.dead = true;
    document.getElementById('menu-overlay').style.display = 'flex';
    document.querySelector('#menu-overlay h1').innerText = "GAME OVER";
}

// --- 绘制 ---
function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // 砖块
    blocks.forEach(b => {
        if(b.x + b.w < camX || b.x > camX + canvas.width) return;
        ctx.fillStyle = b.c;
        ctx.fillRect(b.x - camX, b.y, b.w, b.h);
        if(b.type === 'qbox') {
            ctx.fillStyle = 'black'; ctx.font = '30px monospace'; ctx.fillText('?', b.x - camX + 15, b.y + 35);
        }
    });
    
    // 道具
    ctx.fillStyle = 'red';
    items.forEach(it => ctx.fillRect(it.x - camX, it.y, it.w, it.h));
    
    // 敌人
    enemies.forEach(e => e.draw(ctx, camX));
    
    // 玩家
    let px = player.x - camX;
    // 棕色帽子小人复刻
    ctx.fillStyle = '#795548'; // Hat
    ctx.fillRect(px, player.y, player.w, player.h*0.3);
    ctx.fillStyle = '#FFCC80'; // Face
    ctx.fillRect(px+5, player.y+player.h*0.3, player.w-10, player.h*0.2);
    ctx.fillStyle = '#F44336'; // Shirt
    ctx.fillRect(px+2, player.y+player.h*0.5, player.w-4, player.h*0.25);
    ctx.fillStyle = '#1565C0'; // Pants
    ctx.fillRect(px+5, player.y+player.h*0.75, player.w-10, player.h*0.25);
    
    // UI
    document.getElementById('score-display').innerText = `SCORE: ${state.score}`;
    document.getElementById('coin-display').innerText = `🪙 ${state.coins}`;
}

// --- 启动与适配 ---
function startGame() {
    initAudio(); // 必须在点击事件中触发
    document.getElementById('menu-overlay').style.display = 'none';
    resize();
    generateLevel();
    if(loopId) cancelAnimationFrame(loopId);
    update();
}

function resize() {
    // 强制使用窗口大小
    let w = window.innerWidth;
    let h = window.innerHeight;
    
    // 如果在横屏模式下，这里需要做特殊处理
    if(isLandscape) {
        // 实际上CSS已经旋转了容器，但canvas分辨率需要匹配逻辑尺寸
        // 交换宽高
        canvas.width = h;
        canvas.height = w;
    } else {
        canvas.width = w;
        canvas.height = h;
    }
}

// --- 移动端强力适配 ---
function checkMobile() {
    if(isMobile) {
        document.getElementById('controls').style.display = 'block';
        document.getElementById('mobile-rotate-overlay').style.display = 'flex';
        document.getElementById('menu-overlay').style.display = 'none'; // 先隐藏主菜单
    }
}

window.enableLandscape = function() {
    isLandscape = true;
    container.style.width = '100vh';
    container.style.height = '100vw';
    container.style.transform = 'rotate(90deg)';
    // 修正坐标系偏移
    container.style.position = 'absolute';
    container.style.top = '100%'; 
    container.style.left = '0';
    container.style.transformOrigin = '0 0';
    
    document.getElementById('mobile-rotate-overlay').style.display = 'none';
    document.getElementById('menu-overlay').style.display = 'flex'; // 显示开始菜单
    resize();
}

// 输入绑定
const addTouch = (id, k) => {
    const el = document.getElementById(id);
    el.addEventListener('touchstart', e => { e.preventDefault(); input[k] = true; el.style.background = 'rgba(255,255,255,0.5)'; });
    el.addEventListener('touchend', e => { e.preventDefault(); if(k!=='jump') input[k] = false; el.style.background = ''; });
}
if(isMobile) {
    addTouch('btn-left', 'left'); addTouch('btn-right', 'right'); addTouch('btn-jump', 'jump');
}

window.addEventListener('keydown', e => {
    if(e.code==='ArrowRight'||e.code==='KeyD') input.right=true;
    if(e.code==='ArrowLeft'||e.code==='KeyA') input.left=true;
    if(e.code==='Space'||e.code==='ArrowUp'||e.code==='KeyW') input.jump=true;
});
window.addEventListener('keyup', e => {
    if(e.code==='ArrowRight'||e.code==='KeyD') input.right=false;
    if(e.code==='ArrowLeft'||e.code==='KeyA') input.left=false;
    if(e.code==='Space'||e.code==='ArrowUp'||e.code==='KeyW') input.jump=false;
});

window.addEventListener('resize', resize);
window.onload = checkMobile;

</script>
</body>
</html>
"""

st.components.v1.html(game_html, height=800)
