import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Super AI Kart: V30 Stable",
    page_icon="🍄",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 移除所有多余的UI装饰，确保性能
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
    
    canvas { display: block; width: 100%; height: 100%; }

    /* UI 保持简单，去除模糊特效以提升PC流畅度 */
    .hud { position: absolute; top: 20px; color: #fff; font-size: 24px; font-weight: bold; text-shadow: 2px 2px 0 #000; pointer-events: none; }
    #score-ui { left: 20px; }
    #world-ui { right: 20px; color: #FFD700; }

    /* 移动端按键 */
    #controls { display: none; position: absolute; bottom: 0; width: 100%; height: 100%; pointer-events: none; }
    .btn {
        position: absolute; bottom: 40px; width: 80px; height: 80px;
        background: rgba(255,255,255,0.2); border: 2px solid #fff;
        border-radius: 50%; pointer-events: auto; 
        display: flex; align-items: center; justify-content: center;
        color: white; font-size: 30px;
    }
    .btn:active { background: rgba(255,255,255,0.5); }
    #btn-L { left: 20px; }
    #btn-R { left: 120px; }
    #btn-J { right: 30px; width: 90px; height: 90px; background: rgba(255,50,50,0.3); }

    /* 菜单 */
    #menu {
        position: absolute; top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(0,0,0,0.85); z-index: 100;
        display: flex; flex-direction: column; align-items: center; justify-content: center;
    }
    .start-btn {
        padding: 20px 60px; font-size: 32px; background: #FF3D00; color: white;
        border: 4px solid #fff; cursor: pointer; border-radius: 8px; font-weight: bold;
    }
</style>
</head>
<body>

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
        <h1 style="color:#fff; margin-bottom:20px; text-shadow:4px 4px 0 #f00;">SUPER AI KART</h1>
        <p style="color:#ccc; margin-bottom:30px;">V30: Triple Jump & Fast Graphics</p>
        <button class="start-btn" onclick="startGame()">START GAME</button>
    </div>
</div>

<script>
// --- 核心变量 ---
const canvas = document.getElementById('c');
const ctx = canvas.getContext('2d', { alpha: false }); // 优化：关闭透明通道提升性能
const isMobile = /Android|iPhone|iPad|iPod/i.test(navigator.userAgent);

// 1. 物理分离 (保持你喜欢的设置)
// PC快，手机慢且稳
const PHYSICS = isMobile ? 
    { spd: 3.5, acc: 0.15, fric: 0.65, jump: -10, grav: 0.55 } : 
    { spd: 7.0, acc: 0.8, fric: 0.80, jump: -12, grav: 0.60 };

let running = false;
let frames = 0;
let score = 0;
let level = 0;
let audioCtx = null;
let bgmTimer = null;

// 实体
let player = { x:100, y:0, w:32, h:40, dx:0, dy:0, ground:false, jumps:0, dead:false, inPipe:false };
let input = { l:false, r:false, j:false, jLock:false };
let camX = 0;
let blocks = [];
let enemies = [];
let particles = [];
let goal = null;

const THEMES = [
    { bg: "#5C94FC", ground: "#C84C0C", brick: "#FFB74D", pipe: "#00E676" },
    { bg: "#F4C430", ground: "#E65100", brick: "#FFECB3", pipe: "#2E7D32" },
    { bg: "#212121", ground: "#5D4037", brick: "#8D6E63", pipe: "#66BB6A" }
];

// --- 2. BGM 修复 (最稳的 setInterval 方案) ---
function initAudio() {
    if(!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    if(audioCtx.state === 'suspended') audioCtx.resume();
    
    // 强制重启BGM循环
    if(bgmTimer) clearInterval(bgmTimer);
    playBGM();
    bgmTimer = setInterval(playBGM, 3200); 
}

function playTone(f, t, d, v=0.1) {
    if(!audioCtx || audioCtx.state === 'suspended') return;
    try {
        const o = audioCtx.createOscillator();
        const g = audioCtx.createGain();
        o.type = t; o.frequency.value = f;
        g.gain.setValueAtTime(v, audioCtx.currentTime);
        g.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + d);
        o.connect(g); g.connect(audioCtx.destination);
        o.start(); o.stop(audioCtx.currentTime + d);
    } catch(e) {}
}

function playBGM() {
    if(!running || player.dead) return;
    let base = 220 + (level*20);
    // 简单的节奏
    [0, 200, 400, 600, 800, 1000, 1200, 1400].forEach((d, i) => {
        setTimeout(() => {
            if(running) playTone((i%2==0)?base:base*1.5, 'triangle', 0.1, 0.05);
        }, d);
    });
}

// --- 3. 关卡生成 ---
function initLevel(lvl) {
    blocks = []; enemies = []; particles = [];
    let t = THEMES[lvl % THEMES.length];
    
    blocks.push({x:-200, y:canvas.height-80, w:800, h:100, c: t.ground}); // 起点
    
    let x = 600;
    while(x < 3000 + lvl * 500) {
        if(Math.random() < 0.2) x += 150; // 沟壑
        
        let w = 400 + Math.random() * 400;
        blocks.push({x:x, y:canvas.height-80, w:w, h:100, c: t.ground});
        
        // 必定刷怪 (你之前的要求)
        if(w > 300) {
            let ex = x + 100 + Math.random()*(w-200);
            enemies.push({x:ex, y:canvas.height-120, w:36, h:36, dx:-1.5, type:lvl%3, dead:false});
        }
        
        // 砖块
        if(Math.random() < 0.6) {
            blocks.push({x:x+50, y:canvas.height-220, w:100, h:30, c: t.brick});
        }
        x += w;
    }
    
    // 终点
    blocks.push({x:x, y:canvas.height-80, w:500, h:100, c: t.ground});
    goal = { x: x + 200, y: canvas.height - 180, w: 70, h: 100, cx: x+235 };
    
    player.x = 100; player.y = 0; player.dx=0; player.dy=0;
    player.inPipe = false; player.dead = false;
    camX = 0;
}

// --- 游戏循环 ---
function update() {
    if(!running) return;
    frames++;

    // 钻管
    if(player.inPipe) {
        player.x += (goal.cx - player.x - player.w/2) * 0.2;
        player.y += 3;
        if(player.w > 0) player.w -= 0.5;
        if(player.y > canvas.height) { level++; initLevel(level); }
        draw();
        requestAnimationFrame(update);
        return;
    }

    // 物理
    if(input.r) player.dx += PHYSICS.acc;
    else if(input.l) player.dx -= PHYSICS.acc;
    else player.dx *= PHYSICS.fric;
    
    if(player.dx > PHYSICS.spd) player.dx = PHYSICS.spd;
    if(player.dx < -PHYSICS.spd) player.dx = -PHYSICS.spd;
    
    // --- 4. 三段跳逻辑修复 ---
    if(input.j && !input.jLock) {
        if(player.ground) {
            // 第一跳
            player.dy = PHYSICS.jump; 
            player.jumps = 1; 
            input.jLock = true;
            playTone(300, 'square', 0.1);
        } else if(player.jumps > 0 && player.jumps < 3) { 
            // 只要 jumps < 3 就能跳 (即 1->2, 2->3)
            player.dy = PHYSICS.jump * 0.9; 
            player.jumps++; 
            input.jLock = true;
            playTone(450 + player.jumps*100, 'square', 0.1);
            // 粒子
            for(let i=0; i<6; i++) particles.push({x:player.x+16, y:player.y+40, dx:(Math.random()-0.5)*5, dy:Math.random()*5, life:20, c:'#fff'});
        }
    }
    if(!input.j) input.jLock = false;

    player.dy += PHYSICS.grav;
    player.x += player.dx;
    player.y += player.dy;
    
    // 摄像机
    camX += (player.x - canvas.width*0.3 - camX) * 0.1;
    if(camX < 0) camX = 0;

    // 死亡
    if(player.y > canvas.height + 100) gameOver();

    // 碰撞检测
    player.ground = false;
    blocks.forEach(b => {
        if(colCheck(player, b)) {
            if(player.dy >= 0 && player.y + player.h - player.dy <= b.y + 20) {
                player.y = b.y - player.h; player.dy = 0; player.ground = true; player.jumps = 0;
            } else if(player.dy < 0 && player.y - player.dy >= b.y + b.h - 10) {
                player.y = b.y + b.h; player.dy = 0;
            } else if(player.dx > 0) { player.x = b.x - player.w; player.dx = 0; }
            else if(player.dx < 0) { player.x = b.x + b.w; player.dx = 0; }
        }
    });

    // 怪物碰撞
    enemies.forEach(e => {
        if(e.dead) return;
        e.x += e.dx;
        if(frames % 60 == 0 && Math.random() < 0.3) e.dx *= -1;
        
        if(colCheck(player, e)) {
            if(player.dy > 0 && player.y + player.h < e.y + e.h * 0.8) {
                e.dead = true; player.dy = -8; score += 200;
                playTone(600, 'noise', 0.1); // 踩死音效
                for(let i=0;i<8;i++) particles.push({x:e.x+18,y:e.y+18,dx:(Math.random()-0.5)*8,dy:(Math.random()-0.5)*8,life:20,c:['#E53935','#43A047','#5E35B1'][e.type]});
            } else {
                gameOver();
            }
        }
    });
    
    // 终点
    if(goal) {
        // 站上去触发
        if(colCheck(player, {x:goal.x+10, y:goal.y-5, w:goal.w-20, h:20}) && player.ground) {
             if(Math.abs(player.dx) < 1) {
                 player.inPipe = true;
                 playTone(100, 'sawtooth', 0.8);
             }
        }
        // 撞管壁
        if(colCheck(player, {x:goal.x, y:goal.y+10, w:goal.w, h:goal.h})) {
            if(player.dx > 0) player.x = goal.x - player.w;
        }
    }

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

// --- 5. 绘图优化 (使用 fillRect 代替复杂绘图以解决卡顿) ---
function draw() {
    let t = THEMES[level % THEMES.length];
    
    // 背景
    ctx.fillStyle = t.bg;
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // 砖块
    blocks.forEach(b => {
        if(b.x > camX+canvas.width || b.x+b.w < camX) return;
        ctx.fillStyle = b.c;
        ctx.fillRect(b.x-camX, b.y, b.w, b.h);
        ctx.fillStyle = "rgba(0,0,0,0.1)"; // 简单的阴影线条
        ctx.fillRect(b.x-camX, b.y+b.h-5, b.w, 5); 
    });

    // 终点
    if(goal) {
        let gx = goal.x - camX;
        ctx.fillStyle = t.pipe;
        ctx.fillRect(gx, goal.y, goal.w, goal.h); // 管身
        ctx.fillRect(gx-5, goal.y, goal.w+10, 30); // 管口
        ctx.fillStyle = "#fff"; ctx.font = "bold 16px monospace";
        ctx.fillText("GOAL", gx+15, goal.y+60);
    }

    // 怪物 (用简单的矩形拼出蘑菇样子，不使用 arc 避免卡顿)
    enemies.forEach(e => {
        if(e.dead || e.x > camX+canvas.width) return;
        let ex = e.x - camX;
        let c = ['#E53935', '#43A047', '#5E35B1'][e.type];
        
        // 蘑菇盖 (梯形效果)
        ctx.fillStyle = c;
        ctx.fillRect(ex, e.y+5, e.w, e.h-5); 
        ctx.fillRect(ex+5, e.y, e.w-10, 5); // 顶部凸起
        
        // 脸
        ctx.fillStyle = "#FFCCBC";
        ctx.fillRect(ex+5, e.y+15, e.w-10, 10);
        
        // 眼睛
        ctx.fillStyle = "#000";
        if(e.dx < 0) { ctx.fillRect(ex+8, e.y+18, 4, 4); ctx.fillRect(ex+20, e.y+18, 4, 4); }
        else { ctx.fillRect(ex+12, e.y+18, 4, 4); ctx.fillRect(ex+24, e.y+18, 4, 4); }
    });
    
    // 粒子
    particles.forEach((p, i) => {
        p.x += p.dx; p.y += p.dy; p.life--;
        ctx.fillStyle = p.c;
        ctx.fillRect(p.x-camX, p.y, 5, 5);
        if(p.life<=0) particles.splice(i, 1);
    });

    // 玩家 (拼图绘制：帽子+脸+身体，不使用图片)
    if(!player.dead) {
        let px = player.x - camX;
        let py = player.y;
        
        // 帽子
        ctx.fillStyle = "#D32F2F";
        ctx.fillRect(px, py, player.w, 12);
        ctx.fillRect(px-4, py+8, player.w+8, 4); // 帽檐
        
        // 脸
        ctx.fillStyle = "#FFCCBC";
        ctx.fillRect(px+4, py+12, player.w-8, 12);
        
        // 身体
        ctx.fillStyle = "#1976D2";
        ctx.fillRect(px+4, py+24, player.w-8, 14);
        
        // 腿 (简单的动画)
        ctx.fillStyle = "#3E2723";
        if(player.ground && Math.abs(player.dx) > 0.1) {
            let leg = Math.sin(frames*0.5)*6;
            ctx.fillRect(px+4+leg, py+38, 8, 4);
            ctx.fillRect(px+20-leg, py+38, 8, 4);
        } else {
            ctx.fillRect(px+4, py+38, 8, 4);
            ctx.fillRect(px+20, py+38, 8, 4);
        }
    }

    // UI
    document.getElementById('score-ui').innerText = "SCORE: " + score;
    document.getElementById('world-ui').innerText = "WORLD 1-" + (level+1);
}

// 启动
function startGame() {
    initAudio(); // 核心修复
    document.getElementById('menu').style.display = 'none';
    level = 0; score = 0;
    initLevel(0);
    running = true;
    update();
}

// 适配
function checkOrient() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    if(isMobile) document.getElementById('controls').style.display = 'block';
}
window.addEventListener('resize', checkOrient);
checkOrient();

// 触屏
if(isMobile) {
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
    if(e.key==='w'||e.key===' '||e.key==='ArrowUp') input.j=true;
});
window.addEventListener('keyup', e=>{
    if(e.key==='a'||e.key==='ArrowLeft') input.l=false;
    if(e.key==='d'||e.key==='ArrowRight') input.r=false;
    if(e.key==='w'||e.key===' '||e.key==='ArrowUp') input.j=false;
});

// 全局点击唤醒音频 (修复BGM消失问题)
document.addEventListener('click', function() {
    if(audioCtx && audioCtx.state === 'suspended') audioCtx.resume();
});

</script>
</body>
</html>
"""

st.components.v1.html(game_html, height=800)
