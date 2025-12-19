import streamlit as st
import streamlit.components.v1 as components
import base64
import os
import glob
import json

# --- 1. 页面配置 (移除所有多余边距) ---
st.set_page_config(
    page_title="Super AI Kart: V21 Mobile",
    page_icon="🍄",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 暴力清除 Streamlit 默认的 Padding，确保真全屏
st.markdown("""
    <style>
        #MainMenu, footer, header {visibility: hidden;}
        .block-container {padding: 0 !important; margin: 0 !important; overflow: hidden;}
        body { margin: 0; padding: 0; overflow: hidden; background: black;}
        iframe { display: block; }
    </style>
""", unsafe_allow_html=True)

# --- 2. 音频数据读取 (保持不变) ---
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
    /* 全局复位 */
    * { box-sizing: border-box; -webkit-tap-highlight-color: transparent; }
    body, html {
        margin: 0; padding: 0; width: 100%; height: 100%;
        background-color: #000; overflow: hidden;
        font-family: 'Courier New', monospace; /* 使用通用字体防止加载失败 */
        touch-action: none; user-select: none; -webkit-user-select: none;
    }

    /* 游戏容器：核心层 */
    #app-root {
        position: relative;
        width: 100vw; height: 100vh;
        background: #333;
        overflow: hidden;
    }

    /* 🎮 强制横屏的核心黑科技 */
    /* 当激活 .landscape 类时，强制旋转容器 */
    #app-root.landscape {
        width: 100vh; /* 宽变成了高 */
        height: 100vw; /* 高变成了宽 */
        transform-origin: top left;
        transform: rotate(90deg) translateY(-100%);
        position: absolute;
        top: 0; left: 0;
    }

    canvas { display: block; width: 100%; height: 100%; image-rendering: pixelated; }

    /* UI 层 */
    .ui-layer {
        position: absolute; top: 0; left: 0; width: 100%; height: 100%;
        pointer-events: none; /* 让点击穿透到 Canvas 或 按钮 */
        z-index: 10;
    }

    /* 文字显示 */
    .hud-text {
        position: absolute; color: white; font-weight: bold; font-size: 20px;
        text-shadow: 2px 2px 0 #000; top: 10px;
    }
    #score-box { left: 15px; }
    #coin-box { left: 50%; transform: translateX(-50%); color: #FFD700; }
    #world-box { right: 15px; color: #7FFF00; }

    /* 🔄 横屏切换按钮 (做小一点，放在左上角) */
    #rotate-btn {
        position: absolute; top: 50px; left: 15px; pointer-events: auto;
        background: rgba(0,0,0,0.6); color: white; border: 1px solid #fff;
        padding: 5px 10px; font-size: 14px; border-radius: 4px; z-index: 999;
    }

    /* 📱 移动端控制器 (针对性优化：分离、半透明、适中大小) */
    #controls {
        position: absolute; bottom: 0; left: 0; width: 100%; height: 100%;
        pointer-events: none; z-index: 20;
        display: none; /* 默认隐藏，JS判断是手机才显示 */
    }
    
    .touch-zone {
        position: absolute; bottom: 20px;
        display: flex; gap: 15px; pointer-events: auto;
    }

    /* 左手：左右移动 */
    #d-pad { left: 25px; }
    /* 右手：跳跃 */
    #action-pad { right: 25px; }

    .btn {
        width: 65px; height: 65px; /* 尺寸缩小到 65px */
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.15); /* 很淡的背景 */
        border: 2px solid rgba(255, 255, 255, 0.3);
        display: flex; align-items: center; justify-content: center;
        color: white; font-size: 24px; font-weight: bold;
        backdrop-filter: blur(2px);
    }
    .btn:active, .btn.active { background: rgba(255, 255, 255, 0.4); transform: scale(0.95); }
    
    /* 遮罩层 */
    #overlay {
        position: absolute; top:0; left:0; width:100%; height:100%;
        background: rgba(0,0,0,0.85); z-index: 50;
        display: flex; flex-direction: column; align-items: center; justify-content: center;
    }
    h1 { font-size: 40px; color: #FF4500; margin-bottom: 10px; text-align: center; text-shadow: 4px 4px #000;}
    .menu-btn {
        background: #00AA00; color: white; border: 3px solid white;
        padding: 10px 30px; font-size: 24px; margin-top: 20px; cursor: pointer;
        font-family: monospace; text-transform: uppercase;
    }

    /* 仅在移动设备显示控制器 */
    @media (hover: none) and (pointer: coarse) {
        #controls { display: block; }
    }
</style>
</head>
<body>

<div id="app-root">
    <canvas id="gameCanvas"></canvas>
    
    <div class="ui-layer">
        <div id="rotate-btn" onclick="toggleLandscape()">📱 旋转/横屏</div>
        <div id="score-box" class="hud-text">SCORE: <span id="s-val">0</span></div>
        <div id="coin-box" class="hud-text">💰 <span id="c-val">0</span></div>
        <div id="world-box" class="hud-text">1-<span id="l-val">1</span></div>
    </div>

    <div id="controls">
        <div id="d-pad" class="touch-zone">
            <div class="btn" id="btn-left">◀</div>
            <div class="btn" id="btn-right">▶</div>
        </div>
        <div id="action-pad" class="touch-zone">
            <div class="btn" id="btn-jump">J</div>
        </div>
    </div>

    <div id="overlay">
        <h1>SUPER AI KART<br><span style="font-size:20px;color:#ccc">Mobile Remaster</span></h1>
        <button class="menu-btn" onclick="startGame()">START GAME</button>
        <p style="color:#666; font-size:12px; margin-top:20px">Auto-Landscape Enabled</p>
    </div>
</div>

<script>
// --- 初始化 ---
const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');
const root = document.getElementById('app-root');

// --- 📱 核心：真·横屏适配 ---
let isLandscapeMode = false;

function toggleLandscape() {
    isLandscapeMode = !isLandscapeMode;
    if (isLandscapeMode) {
        root.classList.add('landscape');
    } else {
        root.classList.remove('landscape');
    }
    // 强制延迟重置画布尺寸，因为 DOM 旋转需要时间
    setTimeout(resizeCanvas, 100); 
    setTimeout(resizeCanvas, 500); 
}

function resizeCanvas() {
    // 获取容器现在的逻辑宽高
    const w = root.clientWidth;
    const h = root.clientHeight;
    
    // 无论是否旋转，Canvas 都要填满它的容器
    canvas.width = w;
    canvas.height = h;
    
    // 如果是横屏模式，摄像机要适应宽屏
    if(!player.dead) drawGame();
}
window.addEventListener('resize', resizeCanvas);

// --- 音频系统 (简化版防止报错) ---
const playlist = __PLAYLIST_DATA__;
let audioCtx = null;
let musicInterval = null;

function playSound(type) {
    if(!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    if(audioCtx.state === 'suspended') audioCtx.resume();
    
    const t = audioCtx.currentTime;
    const osc = audioCtx.createOscillator();
    const gain = audioCtx.createGain();
    osc.connect(gain); gain.connect(audioCtx.destination);

    if(type === 'jump') {
        osc.frequency.setValueAtTime(200, t); osc.frequency.linearRampToValueAtTime(400, t+0.1);
        gain.gain.setValueAtTime(0.1, t); gain.gain.linearRampToValueAtTime(0, t+0.1);
        osc.start(t); osc.stop(t+0.1);
    } else if (type === 'coin') {
        osc.frequency.setValueAtTime(1000, t); osc.frequency.setValueAtTime(1500, t+0.1);
        gain.gain.setValueAtTime(0.1, t); gain.gain.linearRampToValueAtTime(0, t+0.2);
        osc.start(t); osc.stop(t+0.2);
    } else if (type === 'bgm') {
        // 极简 BGM 循环
        const base = 220; 
        osc.type = 'triangle';
        osc.frequency.setValueAtTime(base, t);
        gain.gain.setValueAtTime(0.05, t); gain.gain.linearRampToValueAtTime(0, t+0.5);
        osc.start(t); osc.stop(t+0.5);
    }
}

// 简单的节奏器
function startMusic() {
    if(musicInterval) clearInterval(musicInterval);
    musicInterval = setInterval(() => {
        if(Math.random() > 0.5) playSound('bgm');
    }, 400);
}

// --- 游戏逻辑 ---
// 🔧 物理参数调优 (手感核心)
const IS_MOBILE = /Android|webOS|iPhone|iPad|iPod|BlackBerry/i.test(navigator.userAgent);
const PHYS = {
    maxSpeed: IS_MOBILE ? 5.5 : 8.0, // 移动端降速，防跑过头
    accel: 0.6,    // 加速度减小，更线性
    friction: 0.82, // 摩擦力增大，松手即停
    jumpForce: -14
};

let state = { score:0, coins:0, level:1 };
let player = { x:100, y:100, w:40, h:56, dx:0, dy:0, grounded:false, dead:false, jumpCount:0 };
let input = { left:false, right:false, jump:false };
let entities = []; // 所有的砖块、敌人都在这里
let camX = 0;
let loopId = null;

function initLevel(lvl) {
    entities = [];
    const gy = canvas.height - 80;
    
    // 地面
    for(let i=0; i<200; i++) {
        // 留坑
        if(i > 10 && i < 150 && Math.random() < 0.1) continue;
        
        entities.push({type:'ground', x:i*50, y:gy, w:50, h:80, c:'#66BB6A'});
        
        // 随机生成平台和怪物
        if(i > 10 && Math.random() < 0.3) {
            // 砖块
            entities.push({type:'brick', x:i*50, y:gy-120, w:50, h:50, c:'#8D6E63'});
            // 怪物
            if(Math.random() < 0.4) {
                 entities.push({type:'enemy', x:i*50, y:gy-40, w:40, h:40, dx:-2, dy:0, c:'#D32F2F', dead:false});
            }
        }
    }
    // 终点
    entities.push({type:'pipe', x:200*50, y:gy-60, w:60, h:140, c:'#388E3C'});
    
    player.x = 100; player.y = gy-200; player.dx = 0; player.dy = 0;
    camX = 0;
}

function update() {
    if(player.dead) return;
    
    // 1. 物理计算
    if (input.right) player.dx += PHYS.accel;
    else if (input.left) player.dx -= PHYS.accel;
    else player.dx *= PHYS.friction;

    // 速度限制
    if (player.dx > PHYS.maxSpeed) player.dx = PHYS.maxSpeed;
    if (player.dx < -PHYS.maxSpeed) player.dx = -PHYS.maxSpeed;
    if (Math.abs(player.dx) < 0.1) player.dx = 0;

    // 跳跃
    if (input.jump) {
        if (player.grounded) {
             player.dy = PHYS.jumpForce; player.grounded = false; player.jumpCount = 1; playSound('jump');
        } else if (player.jumpCount < 2) { // 二段跳即可，不用三段，太乱
             player.dy = PHYS.jumpForce * 0.8; player.jumpCount++; playSound('jump');
        }
        input.jump = false; // 消耗按键
    }

    player.dy += 0.8; // 重力
    player.x += player.dx;
    player.y += player.dy;
    
    // 掉落死亡
    if(player.y > canvas.height + 200) gameOver();

    // 2. 摄像机
    let targetCamX = player.x - canvas.width * 0.3;
    if(targetCamX < 0) targetCamX = 0;
    camX += (targetCamX - camX) * 0.15; // 平滑跟随

    // 3. 碰撞检测
    player.grounded = false;
    entities.forEach(e => {
        let ex = e.x - camX; // 渲染坐标
        
        // 玩家碰撞检测 (使用绝对坐标)
        if (rectIntersect(player, e)) {
            if (e.type === 'enemy' && !e.dead) {
                // 踩头判定
                if (player.dy > 0 && player.y + player.h < e.y + e.h * 0.5) {
                    e.dead = true; player.dy = -8; state.score += 100; playSound('coin');
                } else {
                    gameOver();
                }
            } else if (e.type === 'ground' || e.type === 'brick' || e.type === 'pipe') {
                // 简单的AABB解决
                // 落地
                if (player.dy > 0 && player.y + player.h - player.dy <= e.y + 10) {
                     player.y = e.y - player.h; player.dy = 0; player.grounded = true; player.jumpCount = 0;
                }
                // 顶头
                else if (player.dy < 0 && player.y - player.dy >= e.y + e.h - 10) {
                    player.y = e.y + e.h; player.dy = 0;
                }
                // 侧面撞
                else if (player.dx > 0) { player.x = e.x - player.w; player.dx = 0; }
                else if (player.dx < 0) { player.x = e.x + e.w; player.dx = 0; }
            }
        }
        
        // 敌人移动逻辑
        if(e.type === 'enemy' && !e.dead) {
            e.x += e.dx;
            if(Math.abs(e.x - player.x) > 1000) return; // 太远不计算
            // 简单的来回巡逻
            // 这里省略复杂的敌人碰撞地形，简化为悬空巡逻或地面巡逻
        }
    });

    drawGame();
    loopId = requestAnimationFrame(update);
}

function rectIntersect(r1, r2) {
    return r1.x < r2.x + r2.w && r1.x + r1.w > r2.x &&
           r1.y < r2.y + r2.h && r1.y + r1.h > r2.y;
}

function drawGame() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // 绘制实体
    entities.forEach(e => {
        let ex = e.x - camX;
        if (ex > -100 && ex < canvas.width + 100) {
            if (e.type === 'enemy' && e.dead) return;
            ctx.fillStyle = e.c;
            if (e.type === 'enemy') {
                // 简单的怪物
                ctx.beginPath(); ctx.arc(ex + e.w/2, e.y + e.h/2, e.w/2, 0, Math.PI*2); ctx.fill();
                // 眼睛
                ctx.fillStyle = 'white'; ctx.fillRect(ex+5, e.y+10, 10, 10); ctx.fillRect(ex+25, e.y+10, 10, 10);
            } else {
                ctx.fillRect(ex, e.y, e.w, e.h);
                // 砖块纹理
                if(e.type === 'brick') {
                    ctx.strokeStyle = 'rgba(0,0,0,0.3)'; ctx.lineWidth = 2; ctx.strokeRect(ex, e.y, e.w, e.h);
                }
            }
        }
    });

    // 绘制玩家 (经典小人)
    let px = player.x - camX;
    ctx.fillStyle = "#FF0000"; ctx.fillRect(px, player.y, player.w, player.h); // 身体
    ctx.fillStyle = "#FFCC80"; ctx.fillRect(px+5, player.y+5, player.w-10, 15); // 脸
    // 眼睛方向
    let eyeX = player.dx >= 0 ? px + 20 : px + 10;
    ctx.fillStyle = "black"; ctx.fillRect(eyeX, player.y+8, 5, 5);

    // 更新 UI 数据
    document.getElementById('s-val').innerText = state.score;
}

function startGame() {
    document.getElementById('overlay').style.display = 'none';
    player.dead = false;
    resizeCanvas(); // 确保开始时尺寸对
    initLevel(1);
    startMusic();
    update();
}

function gameOver() {
    player.dead = true;
    cancelAnimationFrame(loopId);
    document.getElementById('overlay').style.display = 'flex';
    document.querySelector('#overlay h1').innerHTML = "GAME OVER<br><span style='font-size:20px'>Tap to Reset</span>";
}

// --- 输入绑定 (V21 改进版) ---
const bindBtn = (id, key) => {
    const el = document.getElementById(id);
    el.addEventListener('touchstart', (e) => { 
        e.preventDefault(); 
        input[key] = true; 
        el.classList.add('active'); 
    }, {passive: false});
    el.addEventListener('touchend', (e) => { 
        e.preventDefault(); 
        if (key !== 'jump') input[key] = false; // 跳跃在逻辑中自动重置
        el.classList.remove('active'); 
    }, {passive: false});
};

bindBtn('btn-left', 'left');
bindBtn('btn-right', 'right');
bindBtn('btn-jump', 'jump');

// 键盘兼容
window.addEventListener('keydown', e => {
    if(e.code==='ArrowLeft') input.left=true;
    if(e.code==='ArrowRight') input.right=true;
    if(e.code==='Space') input.jump=true;
});
window.addEventListener('keyup', e => {
    if(e.code==='ArrowLeft') input.left=false;
    if(e.code==='ArrowRight') input.right=false;
    if(e.code==='Space') input.jump=false;
});

</script>
</body>
</html>
"""

game_html = game_template.replace("__PLAYLIST_DATA__", playlist_json)
st.markdown("### 🍄 Super AI Kart V21 (Immersive Landscape)")
components.html(game_html, height=600, scrolling=False)
