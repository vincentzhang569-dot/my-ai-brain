import streamlit as st
import streamlit.components.v1 as components

# --- 1. 页面配置 ---
st.set_page_config(
    page_title="Super AI Kart: V25 Native",
    page_icon="🍄",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 清除所有边距，让 iframe 彻底全屏
st.markdown("""
    <style>
        #MainMenu, header, footer {visibility: hidden;}
        .block-container { padding: 0 !important; margin: 0 !important; max-width: 100% !important; }
        iframe { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; border: none; z-index: 9999; }
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
    * { margin: 0; padding: 0; box-sizing: border-box; -webkit-tap-highlight-color: transparent; }
    body { background: #000; overflow: hidden; font-family: monospace; }

    /* 游戏层 */
    #game-container {
        position: absolute; top: 0; left: 0; width: 100%; height: 100%;
        background: #5c94fc; display: none; /* 默认隐藏，JS控制显示 */
    }
    canvas { display: block; width: 100%; height: 100%; }

    /* 提示层：竖屏时显示 */
    #orientation-lock {
        position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        background: #222; color: #fff; z-index: 10000;
        display: flex; flex-direction: column; align-items: center; justify-content: center;
        text-align: center;
    }
    .rotate-icon { font-size: 60px; margin-bottom: 20px; animation: spin 2s infinite; }
    @keyframes spin { 0% { transform: rotate(0deg); } 25% { transform: rotate(-90deg); } 100% { transform: rotate(-90deg); } }

    /* UI */
    .hud { position: absolute; top: 20px; color: white; font-weight: bold; font-size: 24px; text-shadow: 2px 2px 0 #000; pointer-events: none; z-index: 10;}
    #score { left: 20px; }
    #coins { left: 50%; transform: translateX(-50%); color: gold; }

    /* 移动端按键 */
    #controls {
        display: none; position: absolute; bottom: 0; width: 100%; height: 100%;
        pointer-events: none; z-index: 20;
    }
    .btn {
        position: absolute; bottom: 30px; width: 80px; height: 80px;
        background: rgba(255,255,255,0.15); border: 2px solid rgba(255,255,255,0.4);
        border-radius: 50%; pointer-events: auto;
        display: flex; align-items: center; justify-content: center;
        color: white; font-size: 30px;
    }
    .btn:active { background: rgba(255,255,255,0.4); transform: scale(0.9); }
    #btn-L { left: 30px; }
    #btn-R { left: 130px; }
    #btn-J { right: 40px; width: 90px; height: 90px; background: rgba(255,50,50,0.2); }

    /* 开始菜单 */
    #menu {
        position: absolute; top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(0,0,0,0.8); z-index: 100;
        display: flex; flex-direction: column; align-items: center; justify-content: center;
    }
    button.start-btn {
        padding: 15px 40px; font-size: 24px; background: #00C853; color: white;
        border: 3px solid white; cursor: pointer; border-radius: 8px;
    }
</style>
</head>
<body>

<div id="orientation-lock">
    <div class="rotate-icon">📱</div>
    <h2>请旋转手机</h2>
    <p>Please Rotate Device</p>
</div>

<div id="game-container">
    <canvas id="c"></canvas>
    <div id="score" class="hud">SCORE: 0</div>
    <div id="coins" class="hud">🪙 0</div>
    
    <div id="controls">
        <div class="btn" id="btn-L">◀</div>
        <div class="btn" id="btn-R">▶</div>
        <div class="btn" id="btn-J">🚀</div>
    </div>

    <div id="menu">
        <h1 style="color:#ff9800; font-size:40px; margin-bottom:20px; text-shadow:2px 2px #000;">SUPER AI KART<br>V25.0</h1>
        <p style="color:#ddd; margin-bottom:30px;">Rocket Boots & Dual Feet Restored</p>
        <button class="start-btn" onclick="startGame()">START GAME</button>
    </div>
</div>

<script>
const canvas = document.getElementById('c');
const ctx = canvas.getContext('2d');
let isMobile = /Android|iPhone|iPad/i.test(navigator.userAgent);
let running = false;
let audioCtx = null;

// --- 适配逻辑 (Native) ---
function checkOrientation() {
    // 如果是手机且处于竖屏 (高 > 宽)
    if (isMobile && window.innerHeight > window.innerWidth) {
        document.getElementById('orientation-lock').style.display = 'flex';
        document.getElementById('game-container').style.display = 'none';
        if(running) running = false; // 暂停
    } else {
        document.getElementById('orientation-lock').style.display = 'none';
        document.getElementById('game-container').style.display = 'block';
        resize();
        if(!running && player.dead === false && frames > 0) {
            running = true; update(); // 恢复
        }
    }
}
function resize() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
}
window.addEventListener('resize', () => { setTimeout(checkOrientation, 100); });
setInterval(checkOrientation, 500); // 轮询检查

if (isMobile) {
    document.getElementById('controls').style.display = 'block';
}

// --- 音频 ---
const SFX = {
    jump: (n) => playTone(150 + n*50, 'square', 0.1),
    coin: () => playTone(1200, 'sine', 0.1),
    rocket: () => playTone(100, 'sawtooth', 0.2) // 火箭音效
};
function playTone(freq, type, dur) {
    if(!audioCtx) return;
    const t = audioCtx.currentTime;
    const osc = audioCtx.createOscillator();
    const g = audioCtx.createGain();
    osc.type = type; osc.frequency.setValueAtTime(freq, t);
    g.gain.setValueAtTime(0.1, t); g.gain.linearRampToValueAtTime(0, t+dur);
    osc.connect(g); g.connect(audioCtx.destination);
    osc.start(t); osc.stop(t+dur);
}

// --- 游戏实体 ---
let frames = 0;
let state = { score:0, coins:0 };
let input = { l:false, r:false, j:false, jLock:false };
let player = { x:100, y:0, w:36, h:50, dx:0, dy:0, ground:false, jumps:0, dead:false };
let particles = [];
let blocks = [];
let camX = 0;

// 粒子系统 (火箭特效)
class Particle {
    constructor(x, y, color) {
        this.x = x; this.y = y;
        this.vx = (Math.random()-0.5)*2;
        this.vy = 2 + Math.random()*2; // 向下喷射
        this.life = 1.0;
        this.color = color;
    }
    update() {
        this.x += this.vx; this.y += this.vy;
        this.life -= 0.05;
    }
    draw() {
        ctx.globalAlpha = this.life;
        ctx.fillStyle = this.color;
        ctx.fillRect(this.x, this.y, 4, 4);
        ctx.globalAlpha = 1.0;
    }
}

function initLevel() {
    blocks = []; particles = [];
    // 安全起步平台
    blocks.push({x:-100, y:canvas.height-80, w:800, h:100, c:'#66BB6A'});
    
    let x = 700;
    while(x < 6000) {
        let gap = Math.random()<0.2 ? 100 : 0;
        x += gap;
        blocks.push({x:x, y:canvas.height-80, w:200+Math.random()*300, h:100, c:'#66BB6A'});
        
        // 浮空砖块
        if(Math.random()<0.5) {
            blocks.push({x:x+50, y:canvas.height-200, w:80, h:40, c:'#8D6E63'});
        }
        x += 200;
    }
    player.x = 100; player.y = 0; player.dy = 0; player.dx = 0; camX = 0;
}

function update() {
    if(!running) return;
    frames++;
    
    // 物理
    if(input.r) player.dx += 0.8;
    else if(input.l) player.dx -= 0.8;
    else player.dx *= 0.7;
    
    if(player.dx > 6) player.dx = 6; if(player.dx < -6) player.dx = -6;
    
    // 跳跃 (三段跳 + 火箭特效)
    if(input.j && !input.jLock) {
        if(player.ground) {
            player.dy = -12; player.jumps = 1; input.jLock = true; SFX.jump(0);
        } else if(player.jumps > 0 && player.jumps < 3) {
            // 空中跳跃 -> 触发火箭
            player.dy = -10; player.jumps++; input.jLock = true; SFX.rocket();
            // 产生粒子
            for(let i=0; i<10; i++) {
                particles.push(new Particle(player.x + player.w/2, player.y + player.h, Math.random()>0.5 ? '#FF5722' : '#FFC107'));
            }
        }
    }
    if(!input.j) input.jLock = false;
    
    player.dy += 0.6;
    player.y += player.dy;
    player.x += player.dx;
    
    camX += (player.x - canvas.width*0.3 - camX) * 0.1;
    if(player.y > canvas.height + 100) resetGame();
    
    // 碰撞
    player.ground = false;
    blocks.forEach(b => {
        if(b.x > camX+canvas.width || b.x+b.w < camX) return;
        if(player.x < b.x+b.w && player.x+player.w > b.x && player.y < b.y+b.h && player.y+player.h > b.y) {
            if(player.dy > 0 && player.y+player.h-player.dy <= b.y+20) {
                player.y = b.y-player.h; player.dy=0; player.ground=true; player.jumps=0;
            } else if (player.dy < 0 && player.y-player.dy >= b.y+b.h-20) {
                player.y = b.y+b.h; player.dy=0;
            } else if(player.dx > 0) { player.x = b.x-player.w; player.dx=0; }
            else if(player.dx < 0) { player.x = b.x+b.w; player.dx=0; }
        }
    });

    // 粒子更新
    particles = particles.filter(p => p.life > 0);
    particles.forEach(p => p.update());

    draw();
    requestAnimationFrame(update);
}

function draw() {
    ctx.clearRect(0,0,canvas.width,canvas.height);
    
    // 砖块
    blocks.forEach(b => {
        if(b.x > camX+canvas.width || b.x+b.w < camX) return;
        ctx.fillStyle = b.c; ctx.fillRect(b.x-camX, b.y, b.w, b.h);
        ctx.fillStyle = '#4CAF50'; ctx.fillRect(b.x-camX, b.y, b.w, 15); // 草皮
    });
    
    // 粒子 (在玩家后面画)
    particles.forEach(p => {
        ctx.fillStyle = p.color;
        ctx.fillRect(p.x - camX, p.y, 4, 4);
    });
    
    // 玩家 (双脚 + 动画)
    let px = player.x - camX;
    let py = player.y;
    
    // 计算脚的摆动 (两只脚相位差 Math.PI)
    let legL = 0, legR = 0;
    if(player.ground && Math.abs(player.dx) > 0.5) {
        legL = Math.sin(frames * 0.5) * 8; // 左脚幅度
        legR = Math.sin(frames * 0.5 + Math.PI) * 8; // 右脚幅度 (反向)
    }
    
    // 左脚
    ctx.fillStyle = '#3E2723';
    ctx.fillRect(px + 8 + legL, py + player.h - 6, 10, 6);
    // 右脚
    ctx.fillStyle = '#3E2723';
    ctx.fillRect(px + player.w - 18 + legR, py + player.h - 6, 10, 6);
    
    // 身体
    ctx.fillStyle = '#F44336'; ctx.fillRect(px, py+15, player.w, 20);
    ctx.fillStyle = '#1565C0'; ctx.fillRect(px, py+35, player.w, 15); // 裤子
    ctx.fillStyle = '#FFCC80'; ctx.fillRect(px+4, py+8, 28, 18); // 脸
    ctx.fillStyle = '#8D6E63'; ctx.fillRect(px, py, player.w, 10); // 帽子
    
    document.getElementById('score').innerText = "SCORE: " + Math.floor(player.x/10);
}

function resetGame() {
    initLevel();
}

function startGame() {
    audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    document.getElementById('menu').style.display = 'none';
    running = true;
    checkOrientation(); // 立即检查方向
    initLevel();
    update();
}

// 输入绑定
const bind = (id, k) => {
    let btn = document.getElementById(id);
    btn.addEventListener('touchstart', (e)=>{e.preventDefault(); input[k]=true; btn.style.transform='scale(0.9)';});
    btn.addEventListener('touchend', (e)=>{e.preventDefault(); input[k]=false; btn.style.transform='scale(1)';});
};
if(isMobile) { bind('btn-L','l'); bind('btn-R','r'); bind('btn-J','j'); }

window.addEventListener('keydown', e=>{
    if(e.key==='a') input.l=true; if(e.key==='d') input.r=true; if(e.key==='w') input.j=true;
});
window.addEventListener('keyup', e=>{
    if(e.key==='a') input.l=false; if(e.key==='d') input.r=false; if(e.key==='w') input.j=false;
});

</script>
</body>
</html>
"""

st.components.v1.html(game_html, height=800)
