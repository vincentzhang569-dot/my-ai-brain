import streamlit as st
import streamlit.components.v1 as components
import base64
import os
import glob
import json

# --- 1. 页面配置 (强制宽屏模式，手机端更友好) ---
st.set_page_config(
    page_title="Super AI Kart: Mobile Remaster",
    page_icon="🍄",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 隐藏 Streamlit 默认的菜单和页脚，争取更多手机屏幕空间
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .block-container {padding-top: 0rem; padding-bottom: 0rem; padding-left: 0rem; padding-right: 0rem;}
    </style>
""", unsafe_allow_html=True)

# --- 2. 音频数据 (保持兼容) ---
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

# --- 3. 游戏核心 (HTML/JS) ---
game_template = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
<style>
    @import url('https://fonts.googleapis.com/css2?family=VT323&display=swap');
    
    /* 全局样式：禁止选择，禁止触摸默认行为 */
    body {
        margin: 0;
        background-color: #000;
        color: white;
        font-family: 'VT323', monospace;
        overflow: hidden; /* 禁止滚动 */
        height: 100vh;
        width: 100vw;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        touch-action: none; /* 关键：禁止浏览器处理触摸手势 */
        -webkit-touch-callout: none;
        -webkit-user-select: none;
        user-select: none;
    }

    #game-wrapper {
        position: relative;
        width: 100%;
        height: 100%;
        max-width: 800px; /* PC端限制最大宽度 */
        aspect-ratio: 16/9; /* 保持比例 */
        background-color: #333;
        overflow: hidden;
        box-shadow: 0 0 20px rgba(0,0,0,0.5);
    }
    
    /* 手机端全屏覆盖 */
    @media (max-width: 800px) {
        #game-wrapper {
            width: 100vw;
            height: 100vh;
            max-width: none;
            border-radius: 0;
            aspect-ratio: auto;
        }
    }

    canvas { display: block; width: 100%; height: 100%; image-rendering: pixelated; }

    /* UI 文本 */
    .ui-text { position: absolute; color: white; text-shadow: 2px 2px #000; z-index: 10; pointer-events: none; font-size: clamp(20px, 5vw, 32px); font-weight: bold; }
    #score-board { top: 10px; left: 10px; } 
    #coin-board { top: 10px; left: 50%; transform: translateX(-50%); color: #FFD700; } 
    #level-board { top: 10px; right: 10px; color: #00FF00; }

    /* 遮罩层 */
    #overlay {
        position: absolute; top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(0,0,0,0.85);
        display: flex; flex-direction: column; align-items: center; justify-content: center;
        z-index: 20;
    }
    h1 { font-size: clamp(40px, 10vw, 90px); margin: 0; color: #FF4500; text-shadow: 4px 4px #000; letter-spacing: 5px; text-align: center; }
    
    /* 按钮样式 */
    .btn-container { display: flex; gap: 20px; margin-top: 20px; }
    button.pixel-btn {
        background: #00AA00; border: 4px solid #fff; color: white;
        font-family: 'VT323'; font-size: clamp(20px, 6vw, 36px);
        padding: 10px 30px; cursor: pointer;
        box-shadow: 0 6px 0 #005500; text-transform: uppercase;
    }
    button.pixel-btn:active { transform: translateY(6px); box-shadow: none; }
    button.red-btn { background: #CC0000; box-shadow: 0 6px 0 #660000; }
    button.blue-btn { background: #0066CC; box-shadow: 0 6px 0 #003366; }

    /* 📱 移动端控制器 (针对性优化) */
    #controls {
        position: absolute;
        bottom: 20px; /* 稍微抬高，避开底部横条 */
        width: 100%;
        height: 120px;
        display: flex;
        justify-content: space-between;
        padding: 0 20px;
        box-sizing: border-box;
        z-index: 30; /* 提高层级 */
        pointer-events: none; /* 让触摸穿透透明区域 */
    }
    .ctrl-group { display: flex; gap: 15px; pointer-events: auto; align-items: center; }
    
    .ctrl-btn {
        width: 70px; height: 70px;
        background: rgba(255, 255, 255, 0.15);
        border: 2px solid rgba(255, 255, 255, 0.4);
        border-radius: 12px;
        display: flex; align-items: center; justify-content: center;
        font-size: 30px; color: white;
        user-select: none;
        backdrop-filter: blur(4px);
        touch-action: none; /* 关键 */
    }
    .ctrl-btn:active, .ctrl-btn.active { background: rgba(255, 255, 255, 0.4); transform: scale(0.95); }
    
    .btn-a {
        border-radius: 50%; width: 80px; height: 80px;
        background: rgba(255, 69, 0, 0.3);
        font-size: 24px;
    }
    .btn-a:active, .btn-a.active { background: rgba(255, 69, 0, 0.6); }

    /* PC端隐藏控制器 */
    @media (min-width: 1024px) { #controls { display: none; } }
</style>
</head>
<body>
<div id="game-wrapper">
    <div id="score-board" class="ui-text">SCORE: <span id="score-val">0</span></div>
    <div id="coin-board" class="ui-text">💰 <span id="coin-val">0</span></div>
    <div id="level-board" class="ui-text">WORLD <span id="level-val">1-1</span></div>
    
    <div id="overlay">
        <h1 id="title-text">SUPER AI<br>KART</h1>
        <p id="sub-text" style="color:#aaa;font-size:18px;margin-top:10px;">Music Generated by AI 🎵</p>
        <div id="start-btn-group" class="btn-container"><button class="pixel-btn" onclick="tryStartGame()">START</button></div>
        <div id="retry-btn-group" class="btn-container" style="display:none;">
            <button class="pixel-btn blue-btn" onclick="retryLevel()">Retry</button>
            <button class="pixel-btn red-btn" onclick="tryStartGame()">Reset</button>
        </div>
    </div>
    
    <canvas id="gameCanvas"></canvas>
    
    <div id="controls">
        <div class="ctrl-group">
            <div class="ctrl-btn" id="btn-left">◀</div>
            <div class="ctrl-btn" id="btn-right">▶</div>
        </div>
        <div class="ctrl-group">
            <div class="ctrl-btn btn-a" id="btn-jump">JUMP</div>
        </div>
    </div>
</div>

<script>
// --- 全局变量与配置 ---
const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');
const wrapper = document.getElementById('game-wrapper');

// 🎧 音乐配置：定义不同关卡的风格
const MUSIC_THEMES = [
    { type: 'grass', bass: 'square', lead: 'triangle', scale: [261.6, 293.6, 329.6, 392.0, 440.0, 523.2], bpm: 150 }, // C Major Pentatonic
    { type: 'dark', bass: 'sawtooth', lead: 'square', scale: [130.8, 146.8, 155.5, 196.0, 207.6, 261.6], bpm: 120 }, // C Minor (Spooky)
    { type: 'sky', bass: 'sine', lead: 'sawtooth', scale: [349.2, 440.0, 523.2, 587.3, 659.2, 698.4], bpm: 180 }   // F Lydian ish (Floaty)
];

const bgmPlaylist = __PLAYLIST_DATA__;
const gameOverB64 = "__GAMEOVER_DATA__";
let audioCtx = null;
let musicInterval = null;
let currentMusicNote = 0;

// --- 📱 核心修复：更智能的 Canvas 尺寸控制 ---
function resizeCanvas() {
    // 获取 wrapper 的实际显示大小
    const rect = wrapper.getBoundingClientRect();
    canvas.width = rect.width;
    canvas.height = rect.height;
    // 强制重绘一次避免闪烁
    if(!player.dead) drawGame(); 
}
window.addEventListener('resize', resizeCanvas);
// 初始加载延迟一点执行，确保 CSS 生效
setTimeout(resizeCanvas, 100);

// --- 🎵 AI 音乐合成引擎 (V2.0 多风格版) ---
function startProceduralBGM(levelIndex) {
    if(musicInterval) clearInterval(musicInterval);
    if(!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    
    // 根据关卡选择主题 (0, 1, 2 循环)
    const theme = MUSIC_THEMES[(levelIndex - 1) % MUSIC_THEMES.length];
    const beatTime = 60 / theme.bpm; 
    let tick = 0;

    musicInterval = setInterval(() => {
        if(audioCtx.state === 'suspended') audioCtx.resume();
        const t = audioCtx.currentTime;

        // Bassline (贝斯)：每拍一次，更稳定的节奏
        if (tick % 2 === 0) {
            const osc = audioCtx.createOscillator();
            const gain = audioCtx.createGain();
            osc.type = theme.bass;
            // 根音或五音
            const bassNote = (Math.random() > 0.5 ? theme.scale[0] : theme.scale[3]) / 2; 
            osc.frequency.setValueAtTime(bassNote, t);
            gain.gain.setValueAtTime(0.1, t);
            gain.gain.exponentialRampToValueAtTime(0.01, t + 0.3);
            osc.connect(gain); gain.connect(audioCtx.destination);
            osc.start(t); osc.stop(t + 0.3);
        }

        // Melody (主旋律)：随机性更强，但限定在音阶内
        if (Math.random() > 0.2) {
            const osc = audioCtx.createOscillator();
            const gain = audioCtx.createGain();
            osc.type = theme.lead;
            
            // 简单的随机游走算法
            const noteIndex = Math.floor(Math.random() * theme.scale.length);
            let noteFreq = theme.scale[noteIndex];
            // 偶尔高八度
            if (Math.random() > 0.8) noteFreq *= 2;

            osc.frequency.setValueAtTime(noteFreq, t);
            gain.gain.setValueAtTime(0.05, t); // 音量小一点，不刺耳
            gain.gain.exponentialRampToValueAtTime(0.001, t + 0.2); // 快速衰减
            osc.connect(gain); gain.connect(audioCtx.destination);
            osc.start(t); osc.stop(t + 0.2);
        }
        tick++;
    }, beatTime * 1000);
}

function stopMusic() {
    if (musicInterval) { clearInterval(musicInterval); musicInterval = null; }
}

async function playMusic(type, level) {
    // 优先尝试合成音乐，因为更稳定且符合关卡特色
    if (type === 'gameover') {
        stopMusic();
        // 简单的失败音效
        if(!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        const t = audioCtx.currentTime;
        const o = audioCtx.createOscillator(); const g = audioCtx.createGain();
        o.type='sawtooth'; o.frequency.setValueAtTime(100, t); o.frequency.linearRampToValueAtTime(30, t+1);
        g.gain.setValueAtTime(0.2, t); g.gain.linearRampToValueAtTime(0, t+1);
        o.connect(g); g.connect(audioCtx.destination); o.start(t); o.stop(t+1);
    } else {
        // 启动对应关卡的 AI 音乐
        startProceduralBGM(level);
    }
}

function playSound(type) {
    if(!audioCtx) return;
    const t = audioCtx.currentTime;
    const o = audioCtx.createOscillator(); const g = audioCtx.createGain();
    o.connect(g); g.connect(audioCtx.destination);
    
    if (type === 'jump') {
        o.type = 'square';
        o.frequency.setValueAtTime(150, t); o.frequency.linearRampToValueAtTime(300, t+0.1);
        g.gain.setValueAtTime(0.1, t); g.gain.linearRampToValueAtTime(0, t+0.1);
        o.start(t); o.stop(t+0.1);
    } else if (type === 'coin') {
        o.type = 'sine';
        o.frequency.setValueAtTime(1200, t); o.frequency.setValueAtTime(1600, t+0.1);
        g.gain.setValueAtTime(0.1, t); g.gain.linearRampToValueAtTime(0, t+0.2);
        o.start(t); o.stop(t+0.2);
    }
}

// --- 游戏逻辑 ---
const BIOMES={
    grass:{bg:'#5c94fc',ground:'#51D96C',monsters:['walker','slime']}, 
    dark:{bg:'#222',ground:'#555',monsters:['bat','spiky']}, 
    sky:{bg:'#87CEEB',ground:'#FFF',monsters:['bird']}
};

let state={level:1,score:0,coins:0}, frames=0, blocks=[], enemies=[], items=[], clouds=[], camX=0, finishLine=0, loopId=null;
let input={left:false,right:false,jump:false};
let player={x:100,y:200,w:40,h:56,dx:0,dy:0,grounded:false,jumpCount:0,dead:false,facingRight:true, enteringPipe:false};

// 📱 移动端参数调整
const IS_MOBILE = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
const MAX_SPEED = IS_MOBILE ? 6.5 : 9; // 手机端最大速度降低
const ACCEL = IS_MOBILE ? 0.8 : 1.5; // 加速度
const FRICTION = 0.8; // 摩擦力 (越小越滑，越大停得越快)

function createLevel(lvl) {
    blocks=[]; enemies=[]; items=[]; clouds=[];
    const types=['grass','dark','sky']; 
    const biome = BIOMES[types[(lvl-1)%3]]; // 确保关卡主题循环
    wrapper.style.backgroundColor = biome.bg; 
    document.getElementById('level-val').innerText = "1-" + lvl;

    const gy = canvas.height - 100;
    let x = 0; 
    finishLine = (50 + lvl * 20) * 50; // 稍微缩短关卡长度，适合手机快节奏

    // 起始安全区
    for(let i=0;i<10;i++){ blocks.push({x:x,y:gy,w:50,h:50,type:'ground',c:biome.ground}); x+=50; }

    while(x < finishLine) {
        // 坑的逻辑：手机端坑不能太大
        if(Math.random() < 0.15 && lvl > 0) {
            x += 100 + Math.random() * 40; // 坑宽 100-140
        } else {
            let len = 2 + Math.floor(Math.random()*5);
            for(let k=0; k<len; k++) {
                blocks.push({x:x,y:gy,w:50,h:50,type:'ground',c:biome.ground});
                // 生成怪物
                if(Math.random() < 0.2) {
                    let mType = biome.monsters[Math.floor(Math.random()*biome.monsters.length)];
                    let my = gy - 40;
                    if(mType === 'bird' || mType === 'bat') my -= 120;
                    enemies.push({x:x, y:my, w:40, h:40, dx:-2, dy:0, type:mType, dead:false, startX:x, startY:my});
                }
                x+=50;
            }
        }
    }
    // 终点
    for(let i=0;i<10;i++){ blocks.push({x:x,y:gy,w:50,h:50,type:'ground',c:biome.ground}); x+=50; }
    blocks.push({x:finishLine+200, y:gy-50, w:60, h:50, type:'pipe', c:'#00DD00'});
    blocks.push({x:finishLine+200, y:gy-100, w:60, h:50, type:'pipe_top', c:'#00DD00'});

    player.x=100; player.y=gy-200; player.dx=0; player.dy=0; player.dead=false; camX=0; player.enteringPipe=false;
}

function update() {
    if(player.dead) return;
    frames++;
    
    // --- 物理引擎优化 ---
    // 1. 水平移动 (带惯性)
    if(input.right) player.dx += ACCEL;
    else if(input.left) player.dx -= ACCEL;
    else player.dx *= FRICTION; // 没按键时减速

    // 限制最大速度
    if(player.dx > MAX_SPEED) player.dx = MAX_SPEED;
    if(player.dx < -MAX_SPEED) player.dx = -MAX_SPEED;
    if(Math.abs(player.dx) < 0.1) player.dx = 0; // 止微动

    if(player.dx > 0) player.facingRight = true;
    if(player.dx < 0) player.facingRight = false;

    // 2. 跳跃 (三段跳)
    if(input.jump) {
        if(player.grounded) {
            player.dy = -15; player.grounded=false; player.jumpCount=1; playSound('jump');
        } else if(player.jumpCount < 3) {
            player.dy = -12; player.jumpCount++; playSound('jump');
            // 三段跳特效
            if(player.jumpCount === 2) createParticle(player.x, player.y+player.h, '#FF0');
            if(player.jumpCount === 3) createParticle(player.x, player.y+player.h, '#F00');
        }
        input.jump = false; // 防止长按连跳
    }

    player.dy += 0.8; // 重力
    player.x += player.dx;
    player.y += player.dy;

    // 摄像机跟随 (平滑)
    let targetCamX = player.x - canvas.width * 0.3;
    if (targetCamX < 0) targetCamX = 0;
    camX += (targetCamX - camX) * 0.1;

    // 掉落检测
    if(player.y > canvas.height + 100) die();

    // 碰撞检测
    player.grounded = false;
    blocks.forEach(b => {
        if(checkRectCollide(player, b)) {
            // 管道检测
            if (b.type === 'pipe_top' && player.dy > 0 && Math.abs((player.x+player.w/2) - (b.x+b.w/2)) < 20) {
                 winLevel(); return;
            }
            // 地面碰撞
            if (player.dy > 0 && player.y + player.h - player.dy <= b.y + 10) {
                player.y = b.y - player.h; player.dy = 0; player.grounded = true; player.jumpCount = 0;
            } else if (player.dy < 0 && player.y - player.dy >= b.y + b.h - 10) {
                player.y = b.y + b.h; player.dy = 0; // 顶头
            } else if (player.dx > 0) {
                player.x = b.x - player.w; player.dx = 0; // 右侧撞墙
            } else if (player.dx < 0) {
                player.x = b.x + b.w; player.dx = 0; // 左侧撞墙
            }
        }
    });

    drawGame();
    loopId = requestAnimationFrame(update);
}

function checkRectCollide(r1, r2) {
    return r1.x < r2.x + r2.w && r1.x + r1.w > r2.x &&
           r1.y < r2.y + r2.h && r1.y + r1.h > r2.y;
}

function drawGame() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // 绘制方块
    blocks.forEach(b => {
        if(b.x - camX > -100 && b.x - camX < canvas.width) {
            ctx.fillStyle = b.c;
            ctx.fillRect(b.x - camX, b.y, b.w, b.h);
            ctx.strokeStyle = "rgba(0,0,0,0.2)";
            ctx.lineWidth = 2;
            ctx.strokeRect(b.x - camX, b.y, b.w, b.h);
        }
    });

    // 绘制玩家
    const px = player.x - camX;
    if(px > -50 && px < canvas.width + 50) {
        ctx.fillStyle = "#ff0000";
        ctx.fillRect(px, player.y, player.w, player.h);
        // 眼睛
        ctx.fillStyle = "white";
        ctx.fillRect(player.facingRight ? px+25 : px+5, player.y+10, 10, 10);
        // 粒子效果
        if(player.jumpCount > 1) {
             ctx.fillStyle = player.jumpCount === 2 ? "yellow" : "orange";
             ctx.fillRect(px + 10, player.y + player.h, 20, 10);
        }
    }
}

function createParticle(x, y, color) {
    // 简化版粒子，为了性能暂时不做复杂对象池
}

function winLevel() {
    if(player.enteringPipe) return;
    player.enteringPipe = true;
    player.dy = 1;
    // 简单的下钻动画
    let count = 0;
    const pipeAnim = setInterval(() => {
        player.y += 2; count++;
        drawGame();
        if(count > 50) {
            clearInterval(pipeAnim);
            state.level++;
            retryLevel();
        }
    }, 16);
}

function die() {
    if(player.dead) return;
    player.dead = true;
    cancelAnimationFrame(loopId);
    playMusic('gameover');
    document.getElementById('overlay').style.display = 'flex';
    document.getElementById('title-text').innerText = "GAME OVER";
    document.getElementById('start-btn-group').style.display = 'none';
    document.getElementById('retry-btn-group').style.display = 'flex';
}

// --- 控制绑定 ---
window.tryStartGame = function() {
    state.score = 0; state.level = 1; 
    resizeCanvas(); // 确保开始时尺寸正确
    document.getElementById('overlay').style.display = 'none';
    playMusic('bgm', state.level);
    createLevel(state.level);
    update();
}
window.retryLevel = function() {
    document.getElementById('overlay').style.display = 'none';
    playMusic('bgm', state.level);
    createLevel(state.level);
    if(loopId) cancelAnimationFrame(loopId);
    update();
}

// 键盘
window.addEventListener('keydown', e => {
    if(e.code === 'ArrowRight') input.right = true;
    if(e.code === 'ArrowLeft') input.left = true;
    if(e.code === 'Space' || e.code === 'ArrowUp') {
        if(!e.repeat) input.jump = true;
    }
});
window.addEventListener('keyup', e => {
    if(e.code === 'ArrowRight') input.right = false;
    if(e.code === 'ArrowLeft') input.left = false;
    if(e.code === 'Space' || e.code === 'ArrowUp') input.jump = false;
});

// 触摸 (修复版)
const bindTouch = (id, key) => {
    const el = document.getElementById(id);
    el.addEventListener('touchstart', (e) => { 
        e.preventDefault(); 
        input[key] = true; 
        el.classList.add('active'); // 视觉反馈
    }, {passive: false});
    el.addEventListener('touchend', (e) => { 
        e.preventDefault(); 
        if(key !== 'jump') input[key] = false; // 跳跃只触发一次逻辑在 update 里处理
        el.classList.remove('active');
    }, {passive: false});
};
bindTouch('btn-left', 'left');
bindTouch('btn-right', 'right');
bindTouch('btn-jump', 'jump');

</script>
</body>
</html>
"""

game_html = game_template.replace("__PLAYLIST_DATA__", playlist_json).replace("__GAMEOVER_DATA__", game_over_b64)
st.markdown("### 🍄 Super AI Kart: V19.0 (Mobile Remaster)")
components.html(game_html, height=600, scrolling=False)
