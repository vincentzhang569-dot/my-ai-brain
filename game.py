import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Super AI Kart: V28 Final Fix",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 强制全屏 + 隐藏边框
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
    body { background: #000; overflow: hidden; font-family: 'Courier New', monospace; }

    #game-container { position: absolute; top: 0; left: 0; width: 100%; height: 100%; }
    canvas { display: block; width: 100%; height: 100%; }

    /* UI */
    .hud { position: absolute; top: 20px; color: #fff; font-size: 24px; font-weight: bold; text-shadow: 2px 2px 0 #000; z-index: 10; pointer-events: none; }
    #score-ui { left: 20px; }
    #world-ui { right: 20px; color: #FFD700; }

    /* 移动端按键 */
    #controls { display: none; position: absolute; bottom: 0; width: 100%; height: 100%; pointer-events: none; z-index: 20; }
    .btn {
        position: absolute; bottom: 30px; width: 80px; height: 80px;
        background: rgba(255,255,255,0.2); border: 2px solid rgba(255,255,255,0.6);
        border-radius: 50%; pointer-events: auto; backdrop-filter: blur(5px);
        display: flex; align-items: center; justify-content: center;
        color: white; font-size: 30px;
    }
    .btn:active { background: rgba(255,255,255,0.4); transform: scale(0.95); }
    #btn-L { left: 20px; }
    #btn-R { left: 120px; }
    #btn-J { right: 30px; width: 90px; height: 90px; background: rgba(255,50,50,0.3); }

    /* 菜单 */
    #menu {
        position: absolute; top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(0,0,0,0.9); z-index: 100;
        display: flex; flex-direction: column; align-items: center; justify-content: center;
    }
    .start-btn {
        padding: 20px 60px; font-size: 32px; background: #FF3D00; color: white;
        border: 4px solid #fff; cursor: pointer; border-radius: 10px;
        box-shadow: 0 10px 0 #BF360C; font-weight: bold;
        transition: transform 0.1s;
    }
    .start-btn:active { transform: translateY(10px); box-shadow: 0 0 0; }
    
    #rotate-hint {
        display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        background: #111; color: #fff; z-index: 200;
        align-items: center; justify-content: center; text-align: center;
    }
</style>
</head>
<body>

<div id="rotate-hint"><h1>Please Rotate / 请横屏</h1></div>

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
        <h1 style="color:#fff; margin-bottom:10px; text-shadow:4px 4px 0 #f00;">SUPER AI KART</h1>
        <p style="color:#ccc; margin-bottom:30px;">V28: Physics Split & Monsters++</p>
        <button class="start-btn" onclick="startGame()">START GAME</button>
    </div>
</div>

<script>
// --- 核心变量 ---
const canvas = document.getElementById('c');
const ctx = canvas.getContext('2d');
const isMobile = /Android|iPhone|iPad|iPod/i.test(navigator.userAgent);

// --- 1. 物理参数分离 (PC快，手机慢) ---
const PHYSICS = isMobile ? 
    { spd: 3.5, acc: 0.3, fric: 0.85, jump: -10, grav: 0.55 } : // 手机: 稳
    { spd: 7.0, acc: 0.8, fric: 0.80, jump: -12, grav: 0.60 };  // PC: 快

// 游戏状态
let running = false;
let frames = 0;
let score = 0;
let level = 0;
let audioCtx = null;
let bgmInterval = null;

// 实体
let player = { x:100, y:0, w:32, h:40, dx:0, dy:0, ground:false, jumps:0, dead:false, inPipe:false };
let input = { l:false, r:false, j:false, jLock:false };
let camX = 0;
let blocks = [];
let enemies = [];
let particles = [];
let goal = null;

// 关卡风格
const THEMES = [
    { name: "PLAINS", bg: "#5C94FC", ground: "#C84C0C", brick: "#FFB74D" },
    { name: "DESERT", bg: "#F4C430", ground: "#E65100", brick: "#FFECB3" },
    { name: "CAVE",   bg: "#212121", ground: "#5D4037", brick: "#8D6E63" },
    { name: "SKY",    bg: "#B3E5FC", ground: "#ffffff", brick: "#E1F5FE" }
];

// --- 2. 音频引擎 (强制BGM) ---
function initAudio() {
    if(!audioCtx) {
        audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    }
    if(audioCtx.state === 'suspended') {
        audioCtx.resume();
    }
    // 启动 BGM 循环
    if(bgmInterval) clearInterval(bgmInterval);
    playBGM();
    bgmInterval = setInterval(playBGM, 3200); // 循环播放
}

function playTone(freq, type, dur, vol=0.1) {
    if(!audioCtx) return;
    const osc = audioCtx.createOscillator();
    const gain = audioCtx.createGain();
    osc.type = type; osc.frequency.value = freq;
    gain.gain.setValueAtTime(vol, audioCtx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + dur);
    osc.connect(gain); gain.connect(audioCtx.destination);
    osc.start(); osc.stop(audioCtx.currentTime + dur);
}

function playBGM() {
    if(!running || player.dead) return;
    // 简单的低音循环
    let base = 220 + (level*20);
    let sequence = [0, 200, 400, 600, 800, 1000, 1200, 1400];
    sequence.forEach((delay, i) => {
        setTimeout(() => {
            if(!running) return;
            let f = (i%2==0) ? base : base * 1.5;
            playTone(f, 'triangle', 0.15, 0.03);
        }, delay);
    });
}

// --- 3. 关卡生成 (怪物加量) ---
function initLevel(lvl) {
    blocks = []; enemies = []; particles = [];
    let theme = THEMES[lvl % THEMES.length];
    
    // 起跑线
    blocks.push({x:-200, y:canvas.height-80, w:800, h:100, c: theme.ground});
    
    let x = 600;
    let endX = 3000 + lvl * 500;
    
    while(x < endX) {
        // 沟壑 (20% 概率)
        if(Math.random() < 0.2) x += 150;
        
        let w = 400 + Math.random() * 400;
        // 地面
        blocks.push({x:x, y:canvas.height-80, w:w, h:100, c: theme.ground});
        
        // --- 怪物生成 (高密度) ---
        // 只要这个平台够宽，就必定放怪物
        if(w > 300) {
            let enemyCount = 1 + Math.floor(Math.random() * 2); // 1~3个怪物
            for(let i=0; i<enemyCount; i++) {
                let ex = x + 100 + Math.random() * (w-200);
                enemies.push({
                    x: ex, y: canvas.height-120, w:36, h:36, 
                    dx: -1 - Math.random(), // 随机速度
                    type: Math.floor(Math.random()*3),
                    dead: false
                });
            }
        }
        
        // 砖块
        if(Math.random() < 0.6) {
            let by = canvas.height - 200 - Math.random()*50;
            blocks.push({x:x+50, y:by, w:100, h:30, c: theme.brick});
        }
        
        x += w;
    }
    
    // 终点管子
    // 管子底座
    blocks.push({x:x, y:canvas.height-80, w:500, h:100, c: theme.ground});
    // 管子实体
    goal = {
        x: x + 200,
        y: canvas.height - 180, // 管子顶部高度
        w: 70, 
        h: 100,
        cx: x + 200 + 35 // 中心点
    };
    
    player.x = 100; player.y = 0; player.dx=0; player.dy=0;
    player.inPipe = false; player.dead = false;
    camX = 0;
}

// --- 游戏循环 ---
function update() {
    if(!running) return;
    frames++;

    // --- 4. 钻管逻辑 (特效修复) ---
    if(player.inPipe) {
        // 自动移向中心
        player.x += (goal.cx - player.x - player.w/2) * 0.2;
        // 下潜
        player.y += 2;
        // 变小
        if(player.w > 0) player.w -= 0.5;
        
        playTone(100 - player.y/5, 'sawtooth', 0.1); // 钻管音效

        if(player.y > canvas.height) {
            level++;
            initLevel(level);
        }
        draw();
        requestAnimationFrame(update);
        return;
    }

    // --- 物理更新 ---
    if(input.r) player.dx += PHYSICS.acc;
    else if(input.l) player.dx -= PHYSICS.acc;
    else player.dx *= PHYSICS.fric;
    
    if(player.dx > PHYSICS.spd) player.dx = PHYSICS.spd;
    if(player.dx < -PHYSICS.spd) player.dx = -PHYSICS.spd;
    
    // 跳跃
    if(input.j && !input.jLock) {
        if(player.ground) {
            player.dy = PHYSICS.jump; player.jumps = 1; input.jLock = true;
            playTone(300, 'square', 0.1);
        } else if(player.jumps > 0 && player.jumps < 2) { // 二段跳
            player.dy = PHYSICS.jump * 0.9; player.jumps++; input.jLock = true;
            playTone(500, 'square', 0.1);
            // 粒子
            for(let i=0; i<5; i++) particles.push({x:player.x+16, y:player.y+40, dx:(Math.random()-0.5)*5, dy:Math.random()*5, life:20});
        }
    }
    if(!input.j) input.jLock = false;

    player.dy += PHYSICS.grav;
    player.x += player.dx;
    player.y += player.dy;
    
    // 摄像机
    camX += (player.x - canvas.width*0.3 - camX) * 0.1;
    
    // 死亡
    if(player.y > canvas.height + 100) gameOver();

    // 碰撞
    player.ground = false;
    
    // 地面检测
    blocks.forEach(b => {
        if(colCheck(player, b)) {
            let pBot = player.y + player.h;
            // 踩地
            if(player.dy >= 0 && pBot - player.dy <= b.y + 20) {
                player.y = b.y - player.h; player.dy = 0; player.ground = true; player.jumps = 0;
            }
            // 撞头
            else if(player.dy < 0 && player.y - player.dy >= b.y + b.h - 10) {
                player.y = b.y + b.h; player.dy = 0;
            }
            // 侧撞
            else if(player.dx > 0) { player.x = b.x - player.w; player.dx = 0; }
            else if(player.dx < 0) { player.x = b.x + b.w; player.dx = 0; }
        }
    });

    // 终点碰撞 (修复版)
    if(goal) {
        // 检测是否站在管子上
        if(player.x + player.w > goal.x && player.x < goal.x + goal.w) {
            if(Math.abs((player.y + player.h) - goal.y) < 5 && player.dy >= 0) {
                player.y = goal.y - player.h;
                player.ground = true;
                player.dy = 0;
                player.jumps = 0;
                
                // 触发过关 (只要站上去等一会儿)
                if(Math.abs(player.dx) < 0.5) {
                    player.inPipe = true;
                    playTone(600, 'sine', 0.5); // 成功音
                }
            }
        }
        // 管身阻挡
        if(colCheck(player, {x:goal.x, y:goal.y+10, w:goal.w, h:goal.h})) {
            if(player.dx > 0) player.x = goal.x - player.w;
        }
    }

    // 怪物逻辑
    enemies.forEach(e => {
        if(e.dead) return;
        e.x += e.dx;
        if(frames % 60 === 0 && Math.random() < 0.2) e.dx *= -1; // 随机转向
        
        if(colCheck(player, e)) {
            // 踩死
            if(player.dy > 0 && player.y + player.h < e.y + e.h * 0.7) {
                e.dead = true; player.dy = -8; score += 200;
                playTone(800, 'sawtooth', 0.1);
            } else {
                gameOver();
            }
        }
    });

    draw();
    requestAnimationFrame(update);
}

function colCheck(a, b) {
    return a.x < b.x + b.w && a.x + a.w > b.x && a.y < b.y + b.h && a.y + a.h > b.y;
}

function gameOver() {
    running = false;
    document.getElementById('menu').style.display = 'flex';
    document.querySelector('#menu h1').innerText = "GAME OVER";
}

function draw() {
    let theme = THEMES[level % THEMES.length];
    
    // 背景
    ctx.fillStyle = theme.bg;
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // 砖块
    blocks.forEach(b => {
        if(b.x > camX+canvas.width || b.x+b.w < camX) return;
        ctx.fillStyle = b.c;
        ctx.fillRect(b.x-camX, b.y, b.w, b.h);
        ctx.lineWidth = 2; ctx.strokeStyle = "rgba(0,0,0,0.1)"; ctx.strokeRect(b.x-camX, b.y, b.w, b.h);
    });

    // 怪物
    enemies.forEach(e => {
        if(e.dead || e.x > camX+canvas.width || e.x+e.w < camX) return;
        let c = ['#E53935', '#43A047', '#5E35B1'][e.type];
        ctx.fillStyle = c;
        let jumpOff = Math.abs(Math.sin(frames*0.1)) * 5;
        ctx.fillRect(e.x-camX, e.y - jumpOff, e.w, e.h);
        // 眼睛
        ctx.fillStyle = "#fff";
        ctx.fillRect(e.x-camX + (e.dx<0?5:20), e.y - jumpOff + 10, 8, 8);
    });
    
    // 粒子
    particles.forEach((p, i) => {
        p.x += p.dx; p.y += p.dy; p.life--;
        ctx.fillStyle = `rgba(255,200,0,${p.life/20})`;
        ctx.fillRect(p.x-camX, p.y, 6, 6);
        if(p.life<=0) particles.splice(i, 1);
    });

    // 玩家 (如果在钻管，要画在管子后面？不，先画玩家，再画管子前盖)
    let px = player.x - camX;
    let py = player.y;
    
    if(!player.dead) {
        ctx.fillStyle = "#F44336"; // 红帽子
        ctx.fillRect(px, py, player.w, 10);
        ctx.fillStyle = "#FFCC80"; // 脸
        ctx.fillRect(px, py+10, player.w, 10);
        ctx.fillStyle = "#1565C0"; // 蓝衣服
        ctx.fillRect(px, py+20, player.w, player.h-20);
        
        // 跑动腿
        if(player.ground && Math.abs(player.dx)>0.1) {
            let leg = Math.sin(frames*0.5)*5;
            ctx.fillStyle="#000";
            ctx.fillRect(px+5+leg, py+player.h-5, 8, 5);
        }
    }

    // 终点管子 (分层绘制，实现钻入效果)
    if(goal) {
        let gx = goal.x - camX;
        // 1. 管子后壁 (略)
        // 2. 管子前盖 (遮挡玩家)
        ctx.fillStyle = "#2E7D32"; // 深绿
        ctx.fillRect(gx, goal.y, goal.w, goal.h); 
        ctx.fillStyle = "#4CAF50"; // 亮绿管口
        ctx.fillRect(gx-5, goal.y, goal.w+10, 30);
        
        // 文字
        ctx.fillStyle = "#fff"; ctx.font = "bold 20px Arial";
        ctx.fillText("GOAL", gx+10, goal.y+80);
    }

    // HUD
    document.getElementById('score-ui').innerText = `SCORE: ${score}`;
    document.getElementById('world-ui').innerText = `WORLD 1-${level+1}`;
}

// 启动
function startGame() {
    initAudio(); // 核心：用户交互触发音频
    document.getElementById('menu').style.display = 'none';
    level = 0; score = 0;
    initLevel(0);
    running = true;
    update();
}

// 适配
function checkOrient() {
    if(isMobile && window.innerHeight > window.innerWidth) {
        document.getElementById('rotate-hint').style.display = 'flex';
        running = false;
    } else {
        document.getElementById('rotate-hint').style.display = 'none';
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
        if(!running && frames > 0 && !player.dead) running = true;
    }
}
window.addEventListener('resize', checkOrient);
setInterval(checkOrient, 500);

// 触屏
if(isMobile) {
    document.getElementById('controls').style.display = 'block';
    const b = (id, k) => {
        let el = document.getElementById(id);
        el.addEventListener('touchstart', e=>{e.preventDefault(); input[k]=true;});
        el.addEventListener('touchend', e=>{e.preventDefault(); input[k]=false;});
    };
    b('btn-L', 'l'); b('btn-R', 'r'); b('btn-J', 'j');
}

// 键盘
window.addEventListener('keydown', e=>{
    if(e.key==='a'||e.key==='ArrowLeft') input.l=true;
    if(e.key==='d'||e.key==='ArrowRight') input.r=true;
    if(e.key==='w'||e.key===' ') input.j=true;
});
window.addEventListener('keyup', e=>{
    if(e.key==='a'||e.key==='ArrowLeft') input.l=false;
    if(e.key==='d'||e.key==='ArrowRight') input.r=false;
    if(e.key==='w'||e.key===' ') input.j=false;
});

</script>
</body>
</html>
"""

st.components.v1.html(game_html, height=800)
