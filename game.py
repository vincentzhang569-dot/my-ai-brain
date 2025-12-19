import streamlit as st
import streamlit.components.v1 as components
import base64
import os
import glob
import json

# --- 1. 页面配置 ---
st.set_page_config(
    page_title="Super AI Kart: V22 Fixed",
    page_icon="🍄",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 强制全屏 CSS
st.markdown("""
    <style>
        #MainMenu, footer, header {visibility: hidden;}
        .block-container {padding: 0 !important; margin: 0 !important; overflow: hidden;}
        iframe { display: block; width: 100vw; height: 100vh; border: none; }
    </style>
""", unsafe_allow_html=True)

# --- 2. 音频数据 ---
def get_audio_data(folder_path="mp3"):
    playlist = []
    game_over_data = ""
    if os.path.exists(folder_path):
        all_files = glob.glob(os.path.join(folder_path, "*.mp3"))
        for file_path in all_files:
            filename = os.path.basename(file_path).lower()
            try:
                with open(file_path, "rb") as f:
                    b64 = base64.b64encode(f.read()).decode()
                    if "game_over.mp3" == filename: game_over_data = b64
                    else: playlist.append(b64)
            except: pass
    return json.dumps(playlist), game_over_data

playlist_json, game_over_b64 = get_audio_data("mp3")

# --- 3. 游戏核心 HTML ---
game_template = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
<style>
    /* 全局复位，防卡顿 */
    * { box-sizing: border-box; -webkit-tap-highlight-color: transparent; }
    body, html {
        margin: 0; padding: 0; width: 100%; height: 100%;
        background-color: #222; overflow: hidden;
        touch-action: none; /* 关键：禁止浏览器默认滑动 */
        user-select: none; -webkit-user-select: none;
        font-family: monospace;
    }

    /* 游戏容器 */
    #game-container {
        position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        background: #5c94fc; /* 默认天空蓝 */
        transition: transform 0.3s ease, width 0.3s ease, height 0.3s ease;
        transform-origin: top left;
    }

    /* 🔄 横屏模式 CSS */
    #game-container.landscape {
        width: 100vh; height: 100vw;
        transform: rotate(90deg) translateY(-100%);
    }

    canvas { display: block; width: 100%; height: 100%; image-rendering: pixelated; }

    /* UI 层 - 确保在最上层 */
    .ui-layer {
        position: absolute; top: 0; left: 0; width: 100%; height: 100%;
        pointer-events: none; z-index: 100;
    }

    /* 旋转按钮 - 提高 Z-Index 防止点不到 */
    #rotate-btn {
        position: absolute; top: 20px; left: 20px; 
        pointer-events: auto; z-index: 9999;
        background: rgba(0,0,0,0.7); color: #fff; 
        border: 2px solid #fff; border-radius: 8px;
        padding: 8px 12px; font-size: 16px; font-weight: bold;
        cursor: pointer;
    }
    #rotate-btn:active { background: #555; transform: scale(0.95); }

    .hud { position: absolute; color: white; font-weight: bold; font-size: 24px; text-shadow: 2px 2px 0 #000; top: 20px; }
    #score-ui { left: 120px; }
    #world-ui { right: 20px; }

    /* 📱 移动端控制器 */
    #controls {
        display: none; /* 默认隐藏 */
        position: absolute; bottom: 20px; width: 100%; height: 100px;
        pointer-events: none; z-index: 200;
        padding: 0 20px;
    }
    .touch-btn {
        position: absolute; width: 70px; height: 70px; bottom: 10px;
        background: rgba(255, 255, 255, 0.2);
        border: 2px solid rgba(255, 255, 255, 0.5);
        border-radius: 50%;
        pointer-events: auto;
        display: flex; align-items: center; justify-content: center;
        color: white; font-size: 28px; backdrop-filter: blur(4px);
    }
    .touch-btn:active, .touch-btn.active { background: rgba(255, 255, 255, 0.5); transform: scale(0.9); }
    
    #btn-left { left: 20px; }
    #btn-right { left: 110px; }
    #btn-jump { right: 30px; background: rgba(255, 0, 0, 0.2); width: 80px; height: 80px; font-size: 20px; }

    /* 开始界面 */
    #overlay {
        position: absolute; top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(0,0,0,0.85); z-index: 1000;
        display: flex; flex-direction: column; align-items: center; justify-content: center;
    }
    .pixel-font { font-family: monospace; text-transform: uppercase; }
    button.start-btn {
        background: #00C853; border: 4px solid white; color: white;
        padding: 15px 40px; font-size: 30px; cursor: pointer; margin-top: 20px;
    }

    /* 只在触摸设备显示虚拟按键 */
    @media (hover: none) and (pointer: coarse) { #controls { display: block; } }
</style>
</head>
<body>

<div id="game-container">
    <canvas id="gameCanvas"></canvas>
    
    <div class="ui-layer">
        <div id="rotate-btn" onclick="toggleLandscape()">📱 旋转/横屏</div>
        <div id="score-ui" class="hud">SCORE: <span id="s-val">0</span></div>
        <div id="world-ui" class="hud">1-1</div>
        
        <div id="controls">
            <div class="touch-btn" id="btn-left">◀</div>
            <div class="touch-btn" id="btn-right">▶</div>
            <div class="touch-btn" id="btn-jump">JUMP</div>
        </div>
    </div>
</div>

<div id="overlay">
    <h1 class="pixel-font" style="color:#ff5722; font-size: 50px; margin:0; text-align:center;">SUPER AI<br>KART V22</h1>
    <button class="start-btn pixel-font" onclick="initGame()">START</button>
</div>

<script>
// --- 初始化核心 ---
const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');
const container = document.getElementById('game-container');
let isLandscape = false;

// 解决卡顿：确保所有逻辑在 DOM 加载后就绪
function resize() {
    // 根据容器当前的实际渲染尺寸来设置 Canvas
    // 如果旋转了，width/height 会对调，所以我们要取 getBoundingClientRect
    const rect = container.getBoundingClientRect();
    // 简单的处理：Canvas 内部分辨率跟随容器的 CSS 像素
    if (isLandscape) {
         canvas.width = rect.height; // 旋转后，容器的height在视觉上是宽
         canvas.height = rect.width;
    } else {
        canvas.width = rect.width;
        canvas.height = rect.height;
    }
}

// 📱 旋转功能修复
function toggleLandscape() {
    isLandscape = !isLandscape;
    if (isLandscape) {
        container.classList.add('landscape');
    } else {
        container.classList.remove('landscape');
    }
    // 强制等待 CSS 动画完成后重置画布，防止拉伸
    setTimeout(resize, 350);
}
window.addEventListener('resize', resize);
// 初始调用
setTimeout(resize, 100);

// --- 音频引擎 (修复 Autoplay) ---
let audioCtx;
function playSound(type) {
    if(!audioCtx) return;
    const t = audioCtx.currentTime;
    const osc = audioCtx.createOscillator();
    const gain = audioCtx.createGain();
    osc.connect(gain); gain.connect(audioCtx.destination);
    
    if (type === 'jump') {
        osc.frequency.setValueAtTime(150, t); osc.frequency.linearRampToValueAtTime(300, t+0.1);
        gain.gain.setValueAtTime(0.1, t); gain.gain.linearRampToValueAtTime(0, t+0.1);
        osc.start(t); osc.stop(t+0.1);
    } else if (type === 'coin') {
        osc.type = 'sine';
        osc.frequency.setValueAtTime(1200, t); osc.frequency.setValueAtTime(1600, t+0.1);
        gain.gain.setValueAtTime(0.1, t); gain.gain.linearRampToValueAtTime(0, t+0.2);
        osc.start(t); osc.stop(t+0.2);
    }
}

// --- 游戏逻辑 ---
// 物理参数 (已调优)
const PHYS = {
    gravity: 0.7,
    accel: 0.8,    // 移动端加速度
    friction: 0.75, // 摩擦力 (越小停得越快)
    maxSpeed: 6.0, // 移动端限速
    jumpForce: -13
};

let frames = 0;
let state = { score: 0, running: false };
let input = { left: false, right: false, jump: false };
let player = { 
    x: 100, y: 100, w: 40, h: 56, 
    dx: 0, dy: 0, 
    grounded: false, 
    jumpCount: 0,  // 三段跳计数器
    facingRight: true 
};
let blocks = [];
let camX = 0;

// 地图生成 (带坑，带平台)
function generateLevel() {
    blocks = [];
    const gy = canvas.height - 80;
    
    // 生成 300 个单位的地面
    for(let i=0; i<300; i++) {
        // 随机挖坑 (10% 概率)，且不在起点
        if (i > 5 && i < 290 && Math.random() < 0.1) continue;
        
        // 地面
        blocks.push({x: i*50, y: gy, w: 50, h: 80, c: '#65e069', type: 'ground'});
        
        // 空中平台 (随机)
        if (i > 5 && Math.random() < 0.2) {
             let hOffset = 120 + Math.random() * 50;
             blocks.push({x: i*50, y: gy - hOffset, w: 50, h: 50, c: '#a0522d', type: 'brick'});
        }
    }
    player.x = 100; player.y = 0; player.dx = 0; player.dy = 0;
    camX = 0;
}

// 🎨 核心：绘制玩家 (恢复棕色帽子+小脚丫)
function drawPlayer(x, y, w, h) {
    const p = player;
    
    // 计算腿部摆动 (Running Little Feet)
    // 只有在地面且有速度时才摆动
    let legOffset = 0;
    if (p.grounded && Math.abs(p.dx) > 0.5) {
        legOffset = Math.sin(frames * 0.5) * 6; // 摆动幅度
    }

    // 1. 棕色帽子 (Brown Hat)
    ctx.fillStyle = '#8B4513'; // SaddleBrown
    ctx.fillRect(x, y, w, h * 0.25); // 帽顶
    ctx.fillRect(p.facingRight ? x + 5 : x - 5, y + h * 0.2, w, h * 0.1); // 帽檐

    // 2. 脸
    ctx.fillStyle = '#FFCC99';
    ctx.fillRect(x + 5, y + h * 0.25, w - 10, h * 0.25);

    // 3. 衣服 (红色)
    ctx.fillStyle = '#E53935';
    ctx.fillRect(x + 5, y + h * 0.5, w - 10, h * 0.25);

    // 4. 裤子 (蓝色)
    ctx.fillStyle = '#1E88E5';
    ctx.fillRect(x + 5, y + h * 0.75, w - 10, h * 0.15);

    // 5. 跑动的小脚 (棕色鞋子) - 带动画！
    ctx.fillStyle = '#5D4037';
    // 左脚 (向后摆)
    ctx.fillRect(x + 6 + legOffset, y + h - 6, 12, 6);
    // 右脚 (向前摆，相位相反)
    ctx.fillRect(x + w - 18 - legOffset, y + h - 6, 12, 6);
    
    // 眼睛 (方向感)
    ctx.fillStyle = 'black';
    let eyeX = p.facingRight ? x + 24 : x + 10;
    ctx.fillRect(eyeX, y + h * 0.35, 4, 4);
}

function update() {
    if (!state.running) return;
    frames++;
    
    // --- 1. 物理逻辑 ---
    // 左右移动
    if (input.right) player.dx += PHYS.accel;
    else if (input.left) player.dx -= PHYS.accel;
    else player.dx *= PHYS.friction; // 摩擦力生效
    
    // 限速
    if (player.dx > PHYS.maxSpeed) player.dx = PHYS.maxSpeed;
    if (player.dx < -PHYS.maxSpeed) player.dx = -PHYS.maxSpeed;
    if (Math.abs(player.dx) < 0.1) player.dx = 0;

    // 方向判断
    if (player.dx > 0) player.facingRight = true;
    if (player.dx < 0) player.facingRight = false;

    // 跳跃 (三段跳逻辑 Fixed!)
    if (input.jump) {
        let didJump = false;
        if (player.grounded) {
            player.dy = PHYS.jumpForce;
            player.jumpCount = 1;
            didJump = true;
        } else if (player.jumpCount > 0 && player.jumpCount < 3) {
            // 空中接力跳 (稍微弱一点)
            player.dy = PHYS.jumpForce * 0.85;
            player.jumpCount++;
            didJump = true;
            // 粒子特效位置
            // createParticle(player.x, player.y); 
        }
        
        if (didJump) playSound('jump');
        input.jump = false; // 消耗按键，防止长按连跳
    }

    player.dy += PHYS.gravity;
    player.x += player.dx;
    player.y += player.dy;

    // --- 2. 碰撞检测 ---
    player.grounded = false;
    let bottomY = player.y + player.h;
    
    // 掉坑判定
    if (player.y > canvas.height + 100) {
        // 重生
        player.x = camX + 100; player.y = 0; player.dy = 0; player.dx = 0;
        state.score = Math.max(0, state.score - 50);
    }

    // 砖块碰撞
    for (let b of blocks) {
        // 简单的 AABB
        if (player.x < b.x + b.w && player.x + player.w > b.x &&
            player.y < b.y + b.h && player.y + player.h > b.y) {
            
            // 落地检测
            if (player.dy > 0 && player.y + player.h - player.dy <= b.y + 15) {
                player.y = b.y - player.h;
                player.dy = 0;
                player.grounded = true;
                player.jumpCount = 0; // 落地重置跳跃次数
            }
            // 顶头检测
            else if (player.dy < 0 && player.y - player.dy >= b.y + b.h - 15) {
                player.y = b.y + b.h;
                player.dy = 0;
            }
            // 侧面检测
            else if (player.dx > 0) { player.x = b.x - player.w; player.dx = 0; }
            else if (player.dx < 0) { player.x = b.x + b.w; player.dx = 0; }
        }
    }

    // --- 3. 摄像机跟随 ---
    let targetCam = player.x - canvas.width * 0.3;
    if (targetCam < 0) targetCam = 0;
    camX += (targetCam - camX) * 0.15; // 平滑跟随

    // --- 4. 绘制 ---
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // 绘制地面
    ctx.save();
    ctx.translate(-camX, 0); // 摄像机偏移
    for (let b of blocks) {
        if (b.x + b.w > camX && b.x < camX + canvas.width) {
             ctx.fillStyle = b.c;
             ctx.fillRect(b.x, b.y, b.w, b.h);
             // 装饰线
             ctx.fillStyle = 'rgba(0,0,0,0.1)';
             ctx.fillRect(b.x, b.y, b.w, 4);
        }
    }
    
    // 绘制玩家 (绝对坐标转相对坐标)
    drawPlayer(player.x, player.y, player.w, player.h);
    
    ctx.restore();
    
    // UI 更新
    document.getElementById('s-val').innerText = state.score;
    
    requestAnimationFrame(update);
}

// --- 输入事件绑定 (修复 PC 和 移动端) ---

// 1. 移动端触摸
const bindTouch = (id, key) => {
    const el = document.getElementById(id);
    if(!el) return;
    el.addEventListener('touchstart', (e) => { 
        e.preventDefault(); 
        if(key === 'jump') {
             // 跳跃特殊处理：每次按下都触发，不需要保持 true
             input.jump = true;
        } else {
             input[key] = true; 
        }
        el.classList.add('active'); 
    }, {passive: false});
    
    el.addEventListener('touchend', (e) => { 
        e.preventDefault(); 
        if(key !== 'jump') input[key] = false; 
        el.classList.remove('active'); 
    }, {passive: false});
};
bindTouch('btn-left', 'left');
bindTouch('btn-right', 'right');
bindTouch('btn-jump', 'jump');

// 2. PC 键盘 (修复 ArrowUp)
window.addEventListener('keydown', e => {
    if(e.code === 'ArrowRight' || e.key === 'd') input.right = true;
    if(e.code === 'ArrowLeft' || e.key === 'a') input.left = true;
    if(e.code === 'Space' || e.code === 'ArrowUp' || e.key === 'w') {
        input.jump = true;
    }
});
window.addEventListener('keyup', e => {
    if(e.code === 'ArrowRight' || e.key === 'd') input.right = false;
    if(e.code === 'ArrowLeft' || e.key === 'a') input.left = false;
    if(e.code === 'Space' || e.code === 'ArrowUp' || e.key === 'w') input.jump = false;
});

// --- 游戏启动 ---
window.initGame = function() {
    // 激活 AudioContext
    audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    document.getElementById('overlay').style.display = 'none';
    resize();
    generateLevel();
    state.running = true;
    update();
}

</script>
</body>
</html>
"""

game_html = game_template.replace("__PLAYLIST_DATA__", playlist_json)
st.markdown("### 🍄 Super AI Kart V22 (Fixed & Restore)")
components.html(game_html, height=600, scrolling=False)
