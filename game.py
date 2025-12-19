import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Super AI Kart: V34 Control Fix",
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
    #power-ui { top: 60px; left: 20px; color: #00E676; font-size: 20px; display: none; }

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
    /* 按钮容器 */
    .btn-container { display: flex; gap: 20px; margin-top: 20px; }
    
    .start-btn {
        padding: 15px 40px; font-size: 24px; background: #FF3D00; color: white;
        border: 4px solid #fff; cursor: pointer; border-radius: 8px; font-weight: bold;
    }
    .retry-btn {
        background: #00E676; /* 绿色按钮用于重试 */
    }
    
    #menu h1 { color:#fff; margin-bottom:10px; text-shadow:4px 4px 0 #f00; font-size: 48px; }
    #menu p { color:#ccc; margin-bottom:20px; font-size: 18px; }
</style>
</head>
<body>

<div id="game-container">
    <canvas id="c"></canvas>
    <div id="score-ui" class="hud">SCORE: 0</div>
    <div id="power-ui" class="hud">MODE: NORMAL</div>
    <div id="world-ui" class="hud">WORLD 1-1</div>
    
    <div id="controls">
        <div class="btn" id="btn-L">◀</div>
        <div class="btn" id="btn-R">▶</div>
        <div class="btn" id="btn-J">🚀</div>
    </div>

    <div id="menu">
        <h1 id="menu-title">SUPER AI KART</h1>
        <p id="menu-sub">V34: Manual Kart & Retry</p>
        
        <div class="btn-container">
            <button id="btn-retry" class="start-btn retry-btn" onclick="retryLevel()" style="display:none;">TRY AGAIN</button>
            <button id="btn-start" class="start-btn" onclick="resetGame()">START GAME</button>
        </div>
    </div>
</div>

<script>
const canvas = document.getElementById('c');
const ctx = canvas.getContext('2d', { alpha: false });
const isMobile = /Android|iPhone|iPad|iPod/i.test(navigator.userAgent);

// 物理参数
const PHYSICS = isMobile ? 
    { spd: 2.2, acc: 0.1, fric: 0.60, jump: -11, grav: 0.55 } : 
    { spd: 7.0, acc: 0.8, fric: 0.80, jump: -12, grav: 0.60 };

let running = false;
let frames = 0;
let score = 0;
let level = 0;
let audioCtx = null;
let bgmTimer = null;

let player = { 
    x:100, y:0, w:32, h:40, dx:0, dy:0, 
    ground:false, jumps:0, dead:false, inPipe:false,
    big: false, kart: false, timer: 0 
};
let input = { l:false, r:false, j:false, jLock:false };
let camX = 0;
let blocks = [];
let enemies = [];
let particles = [];
let items = []; 
let goal = null;

const BIOMES = [
    { name: "PLAINS", bg: "#5C94FC", ground: "#C84C0C", brick: "#FFB74D", pipe: "#00E676", fricMod: 1.0 },
    { name: "DESERT", bg: "#F4C430", ground: "#E65100", brick: "#FFECB3", pipe: "#2E7D32", fricMod: 1.0 },
    { name: "CAVE",   bg: "#212121", ground: "#5D4037", brick: "#8D6E63", pipe: "#66BB6A", fricMod: 1.0 },
    { name: "SNOW",   bg: "#81D4FA", ground: "#E1F5FE", brick: "#B3E5FC", pipe: "#0288D1", fricMod: 0.2 }, 
    { name: "HILLS",  bg: "#C5E1A5", ground: "#33691E", brick: "#AED581", pipe: "#558B2F", fricMod: 1.0 }
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
    let base = player.kart ? 440 : (220 + (level*20));
    let speed = player.kart ? 100 : 200;
    [0, 1, 2, 3, 4, 5, 6, 7].forEach((i) => {
        setTimeout(() => { if(running) playTone((i%2==0)?base:base*1.5, 'triangle', 0.1, 0.05); }, i * speed);
    });
}

function initLevel(lvl) {
    blocks = []; enemies = []; particles = []; items = [];
    let t = BIOMES[lvl % BIOMES.length];
    
    player.x = 100; player.y = 0; player.dx=0; player.dy=0;
    player.w = player.big ? 40 : 32; 
    player.h = player.big ? 56 : 40; 
    player.inPipe = false; player.dead = false;
    camX = 0;

    // 起点
    blocks.push({x:-200, y:canvas.height-80, w:800, h:100, c: t.ground, type:'ground'}); 
    
    let x = 600;
    let endX = 3000 + lvl * 600;
    
    while(x < endX) {
        let gap = 0;
        let groundY = canvas.height - 80;
        
        if(t.name === "DESERT") gap = Math.random() < 0.3 ? 150 : 0;
        else if(t.name === "HILLS") {
            gap = Math.random() < 0.2 ? 100 : 0;
            groundY -= Math.floor(Math.random() * 3) * 60; 
        } else if(t.name === "CAVE") {
            gap = Math.random() < 0.2 ? 80 : 0;
            blocks.push({x:x, y:0, w:400, h:80, c: t.ground, type:'ground'});
        } else {
            gap = Math.random() < 0.2 ? 120 : 0;
        }

        x += gap; 
        let w = 400 + Math.random() * 400;
        blocks.push({x:x, y:groundY, w:w, h:canvas.height-groundY+100, c: t.ground, type:'ground'});
        
        if(w > 300) {
            let ex = x + 100 + Math.random()*(w-200);
            let eType = Math.floor(Math.random() * 3); 
            enemies.push({x:ex, y:groundY-40, w:36, h:36, dx:-1.5, type:eType, dead:false});
        }
        
        if(Math.random() < 0.7) { 
            let bx = x + 50 + Math.random() * 100;
            let by = groundY - 140; 
            let content = null;
            let rng = Math.random();
            if(rng < 0.5) content = "coin";
            else if(rng < 0.6) content = "mushroom";
            else if(rng < 0.65) content = "kart";

            blocks.push({ x:bx, y:by, w:60, h:60, c: content?"#FFD700":t.brick, type:'brick', content:content, hit:false });
            blocks.push({x:bx+60, y:by, w:60, h:60, c: t.brick, type:'brick', content:null});
            blocks.push({x:bx-60, y:by, w:60, h:60, c: t.brick, type:'brick', content:null});
        }
        x += w;
    }
    
    blocks.push({x:x, y:canvas.height-80, w:500, h:100, c: t.ground, type:'ground'});
    goal = { x: x + 200, y: canvas.height - 150, w: 70, h: 150, cx: x+235 };
    blocks.push({ x: goal.x, y: goal.y, w: goal.w, h: goal.h, c: t.pipe, type:'pipe' });
}

function spawnItem(block) {
    if(!block.content) return;
    let type = 0;
    if(block.content === "coin") type = 0;
    if(block.content === "mushroom") type = 1;
    if(block.content === "kart") type = 2;

    items.push({ x: block.x + 15, y: block.y, w: 30, h: 30, type: type, dy: -5, targetY: block.y - 35 });
    playTone(500, 'square', 0.1);
    for(let i=0;i<5;i++) particles.push({x:block.x+30, y:block.y+60, dx:(Math.random()-0.5)*5, dy:Math.random()*5, life:15, c:"#FFD700"});

    block.content = null; block.c = "#6D4C41"; block.hit = true;
}

function update() {
    if(!running) return;
    frames++;

    if(player.kart) {
        player.timer--;
        if(player.timer <= 0) {
            player.kart = false;
            player.w = player.big ? 40 : 32;
            playTone(150, 'sawtooth', 0.5); 
        }
    }

    if(player.inPipe) {
        player.x += (goal.cx - player.x - player.w/2) * 0.2;
        player.y += 3;
        if(player.w > 0) player.w -= 0.5;
        if(player.y > canvas.height) { level++; initLevel(level); }
        draw();
        requestAnimationFrame(update);
        return;
    }

    let t = BIOMES[level % BIOMES.length];
    let friction = (isMobile ? 0.6 : 0.8);
    // 雪地特别滑
    if(t.name === "SNOW") friction = 0.96;

    // --- 1. 赛车操控修复 (Kart Control Fix) ---
    // 之前是 player.dx = 8 强制赋值，现在改为受控加速
    if(player.kart) {
        let kAcc = 1.5; // 赛车加速极快
        let kMax = 12.0; // 赛车极速更高
        
        if(input.r) player.dx += kAcc;
        else if(input.l) player.dx -= kAcc;
        else player.dx *= 0.9; // 赛车松油门减速也快
        
        // 限制极速
        if(player.dx > kMax) player.dx = kMax;
        if(player.dx < -kMax) player.dx = -kMax;
        
    } else {
        // 普通模式物理
        if(input.r) player.dx += PHYSICS.acc;
        else if(input.l) player.dx -= PHYSICS.acc;
        else player.dx *= friction; 
        
        if(player.dx > PHYSICS.spd) player.dx = PHYSICS.spd;
        if(player.dx < -PHYSICS.spd) player.dx = -PHYSICS.spd;
    }
    
    if(input.j && !input.jLock) {
        let maxJumps = player.kart ? 999 : 3;
        if(player.ground) {
            player.dy = PHYSICS.jump; player.jumps = 1; input.jLock = true;
            playTone(300, 'square', 0.1);
        } else if(player.jumps > 0 && player.jumps < maxJumps) { 
            player.dy = PHYSICS.jump * 0.9; player.jumps++; input.jLock = true;
            playTone(450 + player.jumps*100, 'square', 0.1);
        }
    }
    if(!input.j) input.jLock = false;

    player.dy += PHYSICS.grav;
    player.x += player.dx;
    player.y += player.dy;
    
    if(player.kart && player.y > canvas.height - 100) {
        player.y = canvas.height - 100; player.dy = 0; player.ground = true;
    }

    camX += (player.x - canvas.width*0.3 - camX) * 0.1;
    if(camX < 0) camX = 0;

    if(player.y > canvas.height + 100 && !player.kart) gameOver();

    player.ground = false;
    blocks.forEach(b => {
        if(colCheck(player, b)) {
            if(player.dy >= 0 && player.y + player.h - player.dy <= b.y + 25) {
                player.y = b.y - player.h; player.dy = 0; player.ground = true; player.jumps = 0;
            } else if(player.dy < 0 && player.y - player.dy >= b.y + b.h - 20) {
                player.y = b.y + b.h; player.dy = 0; spawnItem(b);
            } else if(player.dx > 0) { player.x = b.x - player.w; player.dx = 0; }
            else if(player.dx < 0) { player.x = b.x + b.w; player.dx = 0; }
        }
    });

    items.forEach((it, i) => {
        if(it.dy < 0 || it.y < it.targetY) {
            it.y += it.dy; if(it.dy < 0) it.dy += 0.5; if(it.y >= it.targetY && it.dy > 0) it.dy = 0;
        }
        if(colCheck(player, it)) {
            items.splice(i, 1); 
            if(it.type === 0) { score += 100; playTone(800, 'sine', 0.1); }
            else if(it.type === 1) { score += 500; player.big = true; player.w = 40; player.h = 56; playTone(200, 'square', 0.3); }
            else if(it.type === 2) { score += 1000; player.kart = true; player.timer = 600; player.w = 48; player.h = 24; playTone(100, 'sawtooth', 0.5); }
        }
    });

    enemies.forEach(e => {
        if(e.dead) return;
        e.x += e.dx;
        if(frames % 60 == 0 && Math.random() < 0.3) e.dx *= -1;
        
        if(colCheck(player, e)) {
            if(player.kart) {
                e.dead = true; score += 500; playTone(100, 'noise', 0.2);
                for(let i=0;i<10;i++) particles.push({x:e.x+18,y:e.y+18,dx:(Math.random()-0.5)*15,dy:(Math.random()-0.5)*15,life:30,c:'#fff'});
            }
            else if(player.dy > 0 && player.y + player.h < e.y + e.h * 0.8) {
                e.dead = true; player.dy = -8; score += 200; playTone(600, 'noise', 0.1);
            } 
            else {
                if(player.big) {
                    player.big = false; player.w = 32; player.h = 40; player.dy = -5; e.dx *= -1; playTone(150, 'sawtooth', 0.3);
                } else {
                    gameOver();
                }
            }
        }
    });
    
    if(goal && player.ground) {
        if(Math.abs(player.y - (goal.y - player.h)) < 10 && player.x > goal.x && player.x < goal.x + goal.w) {
             if(Math.abs(player.dx) < 2) { player.inPipe = true; playTone(100, 'sawtooth', 0.8); }
        }
    }

    draw();
    requestAnimationFrame(update);
}

function colCheck(a, b) {
    return a.x < b.x + b.w && a.x + a.w > b.x && a.y < b.y + b.h && a.y + a.h > b.y;
}

// --- 2. 游戏结束界面与重生逻辑 ---
function gameOver() {
    running = false;
    let menu = document.getElementById('menu');
    let title = document.getElementById('menu-title');
    let sub = document.getElementById('menu-sub');
    let retryBtn = document.getElementById('btn-retry');
    let startBtn = document.getElementById('btn-start');

    menu.style.display = 'flex';
    title.innerText = "GAME OVER";
    title.style.color = "#FF3D00";
    sub.innerText = "World " + (level+1) + " Score: " + score;
    
    // 显示重试按钮
    retryBtn.style.display = 'block';
    startBtn.innerText = "MAIN MENU";
}

function resetGame() {
    // 回到主菜单/从头开始
    initAudio();
    level = 0; score = 0;
    // 重置按钮状态
    document.getElementById('btn-retry').style.display = 'none';
    document.getElementById('btn-start').innerText = "START GAME";
    
    startGame();
}

function retryLevel() {
    // 重新开始当前关卡
    initAudio();
    // 玩家状态重置（变小）但保留关卡数
    startGame();
}

function startGame() {
    document.getElementById('menu').style.display = 'none';
    // 重置玩家核心状态
    player.big = false; player.kart = false; 
    initLevel(level); // 重新生成当前关卡
    running = true;
    update();
}

function draw() {
    let t = BIOMES[level % BIOMES.length];
    ctx.fillStyle = t.bg;
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    document.getElementById('world-ui').innerText = "WORLD 1-" + (level+1) + " (" + t.name + ")";

    blocks.forEach(b => {
        if(b.x > camX+canvas.width || b.x+b.w < camX) return;
        ctx.fillStyle = b.c;
        ctx.fillRect(b.x-camX, b.y, b.w, b.h);
        if(b.type === 'brick') {
            ctx.fillStyle = "rgba(0,0,0,0.2)"; ctx.fillRect(b.x-camX+5, b.y+5, b.w-10, b.h-10);
            if(b.content) { ctx.fillStyle = "#000"; ctx.font = "30px monospace"; ctx.fillText("?", b.x-camX+20, b.y+40); }
        } else if (b.type === 'ground') {
             ctx.fillStyle = "rgba(0,0,0,0.1)"; ctx.fillRect(b.x-camX, b.y, b.w, 10);
        }
    });

    items.forEach(it => {
        if(it.x > camX+canvas.width || it.x+it.w < camX) return;
        let ix = it.x - camX;
        if(it.type === 0) { 
            ctx.fillStyle = "#FFD700"; ctx.beginPath(); ctx.arc(ix+15, it.y+15, 12, 0, Math.PI*2); ctx.fill();
            ctx.fillStyle = "#FFF"; ctx.font="20px monospace"; ctx.fillText("$", ix+10, it.y+22);
        } else if(it.type === 1) { 
            ctx.fillStyle = "#E53935"; ctx.fillRect(ix, it.y, it.w, it.h);
            ctx.fillStyle = "#fff"; ctx.fillRect(ix+5, it.y+5, 8, 8);
        } else if(it.type === 2) { 
            ctx.fillStyle = "#2979FF"; ctx.fillRect(ix, it.y, it.w, it.h);
            ctx.fillStyle = "#fff"; ctx.fillText("K", ix+8, it.y+20);
        }
    });

    if(goal) {
        let gx = goal.x - camX;
        ctx.fillStyle = t.pipe; ctx.fillRect(gx-5, goal.y, goal.w+10, 30); 
        ctx.fillStyle = "#fff"; ctx.font = "bold 16px monospace"; ctx.fillText("GOAL", gx+15, goal.y+60);
    }

    enemies.forEach(e => {
        if(e.dead || e.x > camX+canvas.width) return;
        let ex = e.x - camX;
        let c = ['#E53935', '#43A047', '#5E35B1'][e.type];
        ctx.fillStyle = c;
        ctx.fillRect(ex, e.y+5, e.w, e.h-5); 
        ctx.fillStyle = "#FFCCBC"; ctx.fillRect(ex+5, e.y+15, e.w-10, 10);
        ctx.fillStyle = "#000";
        if(e.dx < 0) { ctx.fillRect(ex+8, e.y+18, 4, 4); ctx.fillRect(ex+20, e.y+18, 4, 4); }
        else { ctx.fillRect(ex+12, e.y+18, 4, 4); ctx.fillRect(ex+24, e.y+18, 4, 4); }
    });
    
    particles.forEach((p, i) => {
        p.x += p.dx; p.y += p.dy; p.life--;
        ctx.fillStyle = p.c; ctx.fillRect(p.x-camX, p.y, 5, 5);
        if(p.life<=0) particles.splice(i, 1);
    });

    if(!player.dead) {
        let px = player.x - camX; let py = player.y;
        if(player.kart) {
            ctx.fillStyle = frames%4<2 ? "#2979FF" : "#00E5FF"; ctx.fillRect(px, py+10, player.w, 14); 
            ctx.fillStyle = "#000"; ctx.fillRect(px+5, py+24, 10, 10); ctx.fillRect(px+30, py+24, 10, 10);
            ctx.fillStyle = "#fff"; ctx.fillRect(px+player.w-5, py+12, 5, 5);
        } else {
            let hatC = player.big ? "#C62828" : "#D32F2F"; let suitC = player.big ? "#1565C0" : "#1976D2";
            ctx.fillStyle = hatC; ctx.fillRect(px, py, player.w, player.h*0.3); ctx.fillRect(px-4, py+player.h*0.2, player.w+8, player.h*0.1); 
            ctx.fillStyle = "#FFCCBC"; ctx.fillRect(px+4, py+player.h*0.3, player.w-8, player.h*0.3); 
            ctx.fillStyle = suitC; ctx.fillRect(px+4, py+player.h*0.6, player.w-8, player.h*0.35); 
            ctx.fillStyle = "#3E2723"; ctx.fillRect(px+4, py+player.h*0.9, 8, player.h*0.1); ctx.fillRect(px+player.w-12, py+player.h*0.9, 8, player.h*0.1);
        }
    }

    document.getElementById('score-ui').innerText = "SCORE: " + score;
    let modeText = document.getElementById('power-ui');
    if(player.kart) {
        modeText.style.display = 'block'; modeText.innerText = "KART MODE! " + Math.ceil(player.timer/60);
    } else {
        modeText.style.display = 'none';
    }
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
