import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Super AI Kart: V31 Fix",
    page_icon="🍄",
    layout="wide",
    initial_sidebar_state="collapsed"
)

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

    .hud { position: absolute; top: 20px; color: #fff; font-size: 24px; font-weight: bold; text-shadow: 2px 2px 0 #000; pointer-events: none; }
    #score-ui { left: 20px; }
    #world-ui { right: 20px; color: #FFD700; }

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
        <p style="color:#ccc; margin-bottom:30px;">V31: Pipe Fix & Slower Mobile</p>
        <button class="start-btn" onclick="startGame()">START GAME</button>
    </div>
</div>

<script>
const canvas = document.getElementById('c');
const ctx = canvas.getContext('2d', { alpha: false });
const isMobile = /Android|iPhone|iPad|iPod/i.test(navigator.userAgent);

// --- 1. 物理参数修正 (Mobile 究极减速) ---
const PHYSICS = isMobile ? 
    // 手机: 速度降到 2.2，加速度降到 0.1 (非常慢)，摩擦加大到 0.6 (秒停)
    { spd: 2.2, acc: 0.1, fric: 0.60, jump: -11, grav: 0.55 } : 
    // PC: 保持爽快
    { spd: 7.0, acc: 0.8, fric: 0.80, jump: -12, grav: 0.60 };

let running = false;
let frames = 0;
let score = 0;
let level = 0;
let audioCtx = null;
let bgmTimer = null;

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

function initAudio() {
    if(!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    if(audioCtx.state === 'suspended') audioCtx.resume();
    if(bgmTimer) clearInterval(bgmTimer);
    playBGM();
    bgmTimer = setInterval(playBGM, 3200); 
}

function playTone(f, t, d, v=0.1) {
    if(!audioCtx || audioCtx.state === 'suspended') return;
    try {
        const o = audioCtx.createOscillator(); const g = audioCtx.createGain();
        o.type = t; o.frequency.value = f; g.gain.setValueAtTime(v, audioCtx.currentTime);
        g.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + d);
        o.connect(g); g.connect(audioCtx.destination); o.start(); o.stop(audioCtx.currentTime + d);
    } catch(e) {}
}

function playBGM() {
    if(!running || player.dead) return;
    let base = 220 + (level*20);
    [0, 200, 400, 600, 800, 1000, 1200, 1400].forEach((d, i) => {
        setTimeout(() => { if(running) playTone((i%2==0)?base:base*1.5, 'triangle', 0.1, 0.05); }, d);
    });
}

function initLevel(lvl) {
    blocks = []; enemies = []; particles = [];
    let t = THEMES[lvl % THEMES.length];
    
    // 地板
    blocks.push({x:-200, y:canvas.height-80, w:800, h:100, c: t.ground});
    
    let x = 600;
    while(x < 3000 + lvl * 500) {
        if(Math.random() < 0.2) x += 150;
        let w = 400 + Math.random() * 400;
        blocks.push({x:x, y:canvas.height-80, w:w, h:100, c: t.ground});
        
        if(w > 300) {
            let ex = x + 100 + Math.random()*(w-200);
            enemies.push({x:ex, y:canvas.height-120, w:36, h:36, dx:-1.5, type:lvl%3, dead:false});
        }
        if(Math.random() < 0.6) {
            blocks.push({x:x+50, y:canvas.height-220, w:100, h:30, c: t.brick});
        }
        x += w;
    }
    
    // --- 2. 终点管子修复 ---
    // 之前的问题：管子太高(100px)，手机跳跃高度(90px)，导致卡死
    // 修复：管子高度降低，并且加入到 blocks 数组中作为实体碰撞
    
    // 终点地面
    blocks.push({x:x, y:canvas.height-80, w:500, h:100, c: t.ground});
    
    // 这里的 Goal 对象只负责画图和记录位置
    goal = { 
        x: x + 200, 
        y: canvas.height - 150, // 降低高度 (80 -> 150, 相对地面高70px，容易跳上去)
        w: 70, 
        h: 150, // 管身高度
        cx: x+235 
    };
    
    // 关键修复：把管子当作一个实体墙壁/平台加入 blocks，这样物理引擎就能自然处理站立
    blocks.push({
        x: goal.x, 
        y: goal.y, 
        w: goal.w, 
        h: goal.h, 
        c: t.pipe // 颜色
    });
    
    player.x = 100; player.y = 0; player.dx=0; player.dy=0;
    player.inPipe = false; player.dead = false;
    camX = 0;
}

function update() {
    if(!running) return;
    frames++;

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
    
    // 跳跃
    if(input.j && !input.jLock) {
        if(player.ground) {
            player.dy = PHYSICS.jump; player.jumps = 1; input.jLock = true;
            playTone(300, 'square', 0.1);
        } else if(player.jumps > 0 && player.jumps < 3) { 
            player.dy = PHYSICS.jump * 0.9; player.jumps++; input.jLock = true;
            playTone(450 + player.jumps*100, 'square', 0.1);
            for(let i=0; i<6; i++) particles.push({x:player.x+16, y:player.y+40, dx:(Math.random()-0.5)*5, dy:Math.random()*5, life:20, c:'#fff'});
        }
    }
    if(!input.j) input.jLock = false;

    player.dy += PHYSICS.grav;
    player.x += player.dx;
    player.y += player.dy;
    
    camX += (player.x - canvas.width*0.3 - camX) * 0.1;
    if(camX < 0) camX = 0;

    if(player.y > canvas.height + 100) gameOver();

    player.ground = false;
    blocks.forEach(b => {
        if(colCheck(player, b)) {
            // 碰撞修复：更宽松的顶部检测
            if(player.dy >= 0 && player.y + player.h - player.dy <= b.y + 25) {
                player.y = b.y - player.h; player.dy = 0; player.ground = true; player.jumps = 0;
            } else if(player.dy < 0 && player.y - player.dy >= b.y + b.h - 10) {
                player.y = b.y + b.h; player.dy = 0;
            } else if(player.dx > 0) { player.x = b.x - player.w; player.dx = 0; }
            else if(player.dx < 0) { player.x = b.x + b.w; player.dx = 0; }
        }
    });

    enemies.forEach(e => {
        if(e.dead) return;
        e.x += e.dx;
        if(frames % 60 == 0 && Math.random() < 0.3) e.dx *= -1;
        if(colCheck(player, e)) {
            if(player.dy > 0 && player.y + player.h < e.y + e.h * 0.8) {
                e.dead = true; player.dy = -8; score += 200;
                playTone(600, 'noise', 0.1);
                for(let i=0;i<8;i++) particles.push({x:e.x+18,y:e.y+18,dx:(Math.random()-0.5)*8,dy:(Math.random()-0.5)*8,life:20,c:['#E53935','#43A047','#5E35B1'][e.type]});
            } else {
                gameOver();
            }
        }
    });
    
    // 终点检测 (简化版)
    // 只要站在管子上 (player.y == goal.y - player.h) 就算赢
    if(goal && player.ground) {
        // 判断是否站在管子高度 (容差5px)
        if(Math.abs(player.y - (goal.y - player.h)) < 5 && player.x > goal.x && player.x < goal.x + goal.w) {
             if(Math.abs(player.dx) < 1) { // 稍微停一下
                 player.inPipe = true;
                 playTone(100, 'sawtooth', 0.8);
             }
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

function draw() {
    let t = THEMES[level % THEMES.length];
    ctx.fillStyle = t.bg;
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    blocks.forEach(b => {
        if(b.x > camX+canvas.width || b.x+b.w < camX) return;
        ctx.fillStyle = b.c;
        ctx.fillRect(b.x-camX, b.y, b.w, b.h);
        ctx.fillStyle = "rgba(0,0,0,0.1)"; 
        ctx.fillRect(b.x-camX, b.y+b.h-5, b.w, 5); 
    });

    // 单独画管口装饰 (管身已经作为 block 画了)
    if(goal) {
        let gx = goal.x - camX;
        ctx.fillStyle = t.pipe; 
        ctx.fillRect(gx-5, goal.y, goal.w+10, 30); // 只有这个管口是装饰
        ctx.fillStyle = "#fff"; ctx.font = "bold 16px monospace";
        ctx.fillText("GOAL", gx+15, goal.y+60);
    }

    enemies.forEach(e => {
        if(e.dead || e.x > camX+canvas.width) return;
        let ex = e.x - camX;
        let c = ['#E53935', '#43A047', '#5E35B1'][e.type];
        ctx.fillStyle = c;
        ctx.fillRect(ex, e.y+5, e.w, e.h-5); 
        ctx.fillRect(ex+5, e.y, e.w-10, 5);
        ctx.fillStyle = "#FFCCBC";
        ctx.fillRect(ex+5, e.y+15, e.w-10, 10);
        ctx.fillStyle = "#000";
        if(e.dx < 0) { ctx.fillRect(ex+8, e.y+18, 4, 4); ctx.fillRect(ex+20, e.y+18, 4, 4); }
        else { ctx.fillRect(ex+12, e.y+18, 4, 4); ctx.fillRect(ex+24, e.y+18, 4, 4); }
    });
    
    particles.forEach((p, i) => {
        p.x += p.dx; p.y += p.dy; p.life--;
        ctx.fillStyle = p.c;
        ctx.fillRect(p.x-camX, p.y, 5, 5);
        if(p.life<=0) particles.splice(i, 1);
    });

    if(!player.dead) {
        let px = player.x - camX;
        let py = player.y;
        ctx.fillStyle = "#D32F2F";
        ctx.fillRect(px, py, player.w, 12);
        ctx.fillRect(px-4, py+8, player.w+8, 4);
        ctx.fillStyle = "#FFCCBC";
        ctx.fillRect(px+4, py+12, player.w-8, 12);
        ctx.fillStyle = "#1976D2";
        ctx.fillRect(px+4, py+24, player.w-8, 14);
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

    document.getElementById('score-ui').innerText = "SCORE: " + score;
    document.getElementById('world-ui').innerText = "WORLD 1-" + (level+1);
}

function startGame() {
    initAudio();
    document.getElementById('menu').style.display = 'none';
    level = 0; score = 0;
    initLevel(0);
    running = true;
    update();
}

function checkOrient() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    if(isMobile) document.getElementById('controls').style.display = 'block';
}
window.addEventListener('resize', checkOrient);
checkOrient();

if(isMobile) {
    const b = (id, k) => {
        let el = document.getElementById(id);
        el.addEventListener('touchstart', e=>{e.preventDefault(); input[k]=true;});
        el.addEventListener('touchend', e=>{e.preventDefault(); input[k]=false;});
    };
    b('btn-L', 'l'); b('btn-R', 'r'); b('btn-J', 'j');
}

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
document.addEventListener('click', function() { if(audioCtx && audioCtx.state === 'suspended') audioCtx.resume(); });

</script>
</body>
</html>
"""

st.components.v1.html(game_html, height=800)
