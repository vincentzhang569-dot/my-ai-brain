import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Super AI Kart: V39 Visuals & Bosses",
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
    body { background: #000; overflow: hidden; font-family: 'Segoe UI', sans-serif; }
    canvas { display: block; width: 100%; height: 100%; }

    .hud { position: absolute; top: 20px; color: #fff; font-size: 20px; font-weight: 800; text-shadow: 2px 2px 0 #000; pointer-events: none; letter-spacing: 1px; }
    #score-ui { left: 20px; background: rgba(0,0,0,0.3); padding: 5px 10px; border-radius: 10px; }
    #world-ui { right: 20px; color: #FFD700; background: rgba(0,0,0,0.3); padding: 5px 10px; border-radius: 10px; }
    
    #boss-ui { 
        position: absolute; top: 80px; left: 50%; transform: translateX(-50%); 
        width: 300px; padding: 5px; background: rgba(0,0,0,0.5); border-radius: 15px; display: none; 
    }
    #boss-name { color: #fff; text-align: center; font-size: 14px; margin-bottom: 4px; text-transform: uppercase; text-shadow: 1px 1px 0 #000; }
    #boss-bar-bg { width: 100%; height: 12px; background: #555; border-radius: 6px; overflow: hidden; }
    #boss-hp { width: 100%; height: 100%; background: linear-gradient(90deg, #ff4444, #cc0000); transition: width 0.2s; }

    #controls { display: none; position: absolute; bottom: 0; width: 100%; height: 100%; pointer-events: none; }
    .btn {
        position: absolute; bottom: 30px; width: 70px; height: 70px;
        background: rgba(255,255,255,0.15); border: 2px solid rgba(255,255,255,0.5);
        border-radius: 50%; pointer-events: auto; backdrop-filter: blur(4px);
        display: flex; align-items: center; justify-content: center;
        color: white; font-size: 24px; box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    }
    .btn:active { background: rgba(255,255,255,0.4); transform: scale(0.95); }
    #btn-L { left: 20px; }
    #btn-R { left: 110px; }
    #btn-J { right: 30px; width: 80px; height: 80px; background: rgba(255,50,50,0.3); font-size: 30px; }

    #menu {
        position: absolute; top: 0; left: 0; width: 100%; height: 100%;
        background: linear-gradient(135deg, rgba(20,0,20,0.95), rgba(0,0,40,0.95)); z-index: 100;
        display: flex; flex-direction: column; align-items: center; justify-content: center;
    }
    .btn-container { display: flex; gap: 20px; margin-top: 30px; }
    .start-btn {
        padding: 15px 50px; font-size: 24px; background: linear-gradient(to bottom, #FF5722, #D84315); color: white;
        border: none; cursor: pointer; border-radius: 30px; font-weight: bold;
        box-shadow: 0 5px 15px rgba(255,87,34,0.4); transition: transform 0.1s;
    }
    .start-btn:active { transform: scale(0.95); }
    #menu h1 { 
        color:#fff; margin-bottom:5px; font-size: 56px; 
        text-shadow: 0 0 20px rgba(255,255,255,0.5), 4px 4px 0 #D84315; 
        font-family: 'Arial Black', sans-serif; letter-spacing: -2px;
    }
    #menu p { color:#aaa; font-size: 18px; letter-spacing: 2px; text-transform: uppercase; }
</style>
</head>
<body>

<div id="game-container">
    <canvas id="c"></canvas>
    <div id="score-ui" class="hud">SCORE: 0</div>
    <div id="world-ui" class="hud">WORLD 1-1</div>
    
    <div id="boss-ui">
        <div id="boss-name">BOSS</div>
        <div id="boss-bar-bg"><div id="boss-hp"></div></div>
    </div>
    
    <div id="controls">
        <div class="btn" id="btn-L">◀</div>
        <div class="btn" id="btn-R">▶</div>
        <div class="btn" id="btn-J">🚀</div>
    </div>

    <div id="menu">
        <h1 id="menu-title">SUPER AI KART</h1>
        <p id="menu-sub">V39: 3D Visuals & Boss Roster</p>
        <div class="btn-container">
            <button id="btn-retry" class="start-btn" onclick="retryLevel()" style="display:none; background: #4CAF50;">RETRY</button>
            <button id="btn-start" class="start-btn" onclick="resetGame()">PLAY</button>
        </div>
    </div>
</div>

<script>
const canvas = document.getElementById('c');
const ctx = canvas.getContext('2d', { alpha: false });
const isMobile = /Android|iPhone|iPad|iPod/i.test(navigator.userAgent);

// Physics & Game State
const PHYSICS = isMobile ? 
    { spd: 2.2, acc: 0.1, fric: 0.60, jump: -11, grav: 0.55 } : 
    { spd: 7.0, acc: 0.8, fric: 0.80, jump: -12, grav: 0.60 };

let running = false;
let frames = 0;
let score = 0;
let level = 0;
let audioCtx = null;
let bgmTimer = null;

let player = { x:100, y:0, w:32, h:40, dx:0, dy:0, ground:false, jumps:0, dead:false, inPipe:false, big:false, kart:false, timer:0, invul:0, facing:1 };
let input = { l:false, r:false, j:false, jLock:false };
let camX = 0;
let blocks = [];
let enemies = [];
let particles = [];
let items = []; 
let goal = null;
let boss = null; 

// Visuals & Biomes
const BIOMES = [
    { name: "PLAINS", bg: "#64B5F6", ground: "#5D4037", top: "#81C784", brick: "#FFB74D", pipe: "#43A047" },
    { name: "DESERT", bg: "#FFCC80", ground: "#E65100", top: "#FFAB91", brick: "#FFE0B2", pipe: "#2E7D32" },
    { name: "CAVE",   bg: "#263238", ground: "#3E2723", top: "#4E342E", brick: "#8D6E63", pipe: "#546E7A" },
    { name: "SKY",    bg: "#E1F5FE", ground: "#0288D1", top: "#FFFFFF", brick: "#B3E5FC", pipe: "#01579B" }
];

// Audio System
function initAudio() {
    if(!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    if(audioCtx.state === 'suspended') audioCtx.resume();
    if(bgmTimer) clearInterval(bgmTimer);
    playBGM();
    bgmTimer = setInterval(playBGM, 150); // Faster tick for melody sequencing
}

let melodyStep = 0;
function playTone(f, t, d, v=0.1) {
    if(!audioCtx || audioCtx.state === 'suspended') return;
    try {
        const o = audioCtx.createOscillator(); const g = audioCtx.createGain();
        o.type = t; o.frequency.value = f; g.gain.setValueAtTime(v, audioCtx.currentTime);
        g.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + d);
        o.connect(g); g.connect(audioCtx.destination); o.start(); o.stop(audioCtx.currentTime + d);
    } catch(e) {}
}

const MELODIES = {
    peace: [330,0,392,0,523,0,392,0,330,0,262,0],
    boss1: [110,110,0,105,105,0,100,100,0,95,95,0], // Heavy
    boss2: [880,0,440,0,880,0,440,0,830,0,415,0],   // Fast/Ninja
    boss3: [220,220,294,294,330,330,294,294],       // Epic
    kart:  [440,440,554,659,440,554,659,880]
};

function playBGM() {
    if(!running || player.dead) return;
    melodyStep++;
    
    // Choose track
    let track = MELODIES.peace;
    let wave = 'triangle';
    let tempo = 2; // mod 2 = slow
    
    if(boss && !boss.dead && boss.x < camX + canvas.width + 100) {
        if(boss.style === 0) { track = MELODIES.boss1; wave='sawtooth'; tempo=2; }
        else if(boss.style === 1) { track = MELODIES.boss2; wave='square'; tempo=1; }
        else { track = MELODIES.boss3; wave='sine'; tempo=2; }
    } else if(player.kart) {
        track = MELODIES.kart; wave='square'; tempo=1;
    }

    if(melodyStep % tempo === 0) {
        let note = track[(melodyStep/tempo) % track.length];
        if(note > 0) playTone(note, wave, 0.1, 0.05);
    }
}

// --- Init & Gen ---
function initLevel(lvl) {
    blocks = []; enemies = []; particles = []; items = []; boss = null;
    let t = BIOMES[lvl % BIOMES.length];
    
    player.x = 100; player.y = 0; player.dx=0; player.dy=0;
    player.w = player.big ? 40 : 32; player.h = player.big ? 56 : 40; 
    player.inPipe = false; player.dead = false; player.invul = 0;
    camX = 0;
    document.getElementById('boss-ui').style.display = 'none';

    let groundY = canvas.height - 80;
    blocks.push({x:-200, y:groundY, w:800, h:100, c: t.ground, type:'ground'}); 
    
    let x = 600;
    let endX = 3500 + lvl * 800;
    
    while(x < endX) {
        let rng = Math.random();
        
        // Random Coin Arrays
        if(Math.random() < 0.25) {
            let cy = groundY - 120 - Math.random()*80;
            for(let k=0; k<4; k++) items.push({ x: x + k*35, y: cy + Math.sin(k)*20, w:30, h:30, type:0, dy:0, dx:0, state:'static' });
        }

        if(rng < 0.4) { // Flat + Enemies
            let w = 400 + Math.random() * 400;
            blocks.push({x:x, y:groundY, w:w, h:200, c: t.ground, type:'ground'});
            if(Math.random() < 0.7) spawnEnemy(x + w/2, groundY-40, (Math.random()<0.3)?'jumper':'walker');
            createBricks(x + 100, groundY - 140, t);
            x += w;
        } 
        else if(rng < 0.6) { // Pits + Flyers
            let gap = 140 + Math.random() * 60;
            spawnEnemy(x + gap/2, groundY - 150 - Math.random()*100, 'flyer');
            x += gap; 
        }
        else if(rng < 0.8) { // Platforms
            let steps = 3 + Math.floor(Math.random()*3);
            let platW = 150;
            for(let i=0; i<steps; i++) {
                blocks.push({x:x, y:groundY - i*40, w:60, h:200, c: t.brick, type:'ground'});
                x += 60;
            }
            blocks.push({x:x, y:groundY - (steps-1)*40, w:platW, h:200, c: t.ground, type:'ground'});
            createBricks(x+platW/2-30, groundY - (steps-1)*40 - 140, t);
            x += platW;
            if(Math.random() < 0.5) x += 80;
        }
        else { // Pipes + Drillers
            let w = 300;
            blocks.push({x:x, y:groundY, w:w, h:200, c: t.ground, type:'ground'});
            let ph = 60 + Math.random()*60;
            let px = x + 100;
            blocks.push({x:px, y:groundY-ph, w:60, h:ph, c: t.pipe, type:'pipe'});
            spawnEnemy(px+10, groundY-ph, 'drill'); // Changed from 'plant' to 'drill'
            x += w;
        }
    }
    
    // BOSS ARENA & GENERATION
    blocks.push({x:x, y:groundY, w:1000, h:100, c: t.ground, type:'ground'});
    
    // Choose Boss Style
    let bossStyle = lvl % 3; // 0: Titan, 1: Ninja, 2: Gold
    let bossProps = {
        0: { name: "IRON TITAN", color: "#D32F2F", w:90, h:90, hp:3, spd:2 },
        1: { name: "SHADOW NINJA", color: "#7B1FA2", w:60, h:60, hp:3, spd:6 },
        2: { name: "GOLD KING", color: "#FFD700", w:120, h:120, hp:5, spd:1.5 }
    }[bossStyle];

    boss = {
        x: x + 600, y: groundY - bossProps.h, w: bossProps.w, h: bossProps.h, 
        dx: -bossProps.spd, dy: 0, hp: bossProps.hp, maxHp: bossProps.hp,
        iframes: 0, dead: false, style: bossStyle, name: bossProps.name,
        baseSpd: bossProps.spd, timer: 0
    };
    
    x += 1000;
    goal = { x: x + 50, y: groundY-150, w: 70, h: 150, cx: x+85 };
    blocks.push({ x: goal.x, y: goal.y, w: goal.w, h: goal.h, c: t.pipe, type:'pipe' });
    blocks.push({x:x, y:groundY, w:300, h:100, c: t.ground, type:'ground'});
}

function createBricks(bx, by, t) {
    let rng = Math.random();
    let content = null;
    if(rng < 0.6) content = "coin";
    else if(rng < 0.8) content = "mushroom";
    else if(rng < 0.9) content = "kart";
    
    blocks.push({ x:bx, y:by, w:60, h:60, c: t.brick, type:'brick', content:content, hit:false });
    blocks.push({x:bx+60, y:by, w:60, h:60, c: t.brick, type:'brick', content:null});
    blocks.push({x:bx-60, y:by, w:60, h:60, c: t.brick, type:'brick', content:null});
}

function spawnEnemy(x, y, type) {
    let e = { x:x, y:y, w:36, h:36, dx:-1.5, dy:0, dead:false, type:0, anchorY:y, timer:0, facing:-1 };
    if(type === 'flyer') { e.type = 1; e.dx = -2; e.w=40; e.h=30; }
    else if(type === 'drill') { e.type = 2; e.dx = 0; e.y += 30; e.anchorY = y; e.w=40; e.h=60; }
    else if(type === 'jumper') { e.type = 3; e.dx = -1.0; e.h=32; }
    enemies.push(e);
}

function spawnItem(block) {
    if(!block.content) return;
    let type = (block.content==="coin")?0:(block.content==="mushroom"?1:2);
    let isMoving = (type !== 0);
    items.push({ x: block.x+15, y: block.y, w:30, h:30, type:type, dy:-6, dx:isMoving?2:0, targetY:block.y-35, state:'spawning' });
    playTone(500, 'square', 0.1);
    block.content=null; block.hit=true;
}

function update() {
    if(!running) return;
    frames++;
    if(player.invul > 0) player.invul--;

    // Player Physics
    if(player.kart) {
        player.timer--;
        if(player.timer <= 0) { player.kart = false; player.w = player.big?40:32; playTone(150,'sawtooth',0.5); }
        if(input.r) player.dx += 1.5; else if(input.l) player.dx -= 1.5; else player.dx *= 0.9;
        if(player.dx > 12) player.dx = 12; if(player.dx < -12) player.dx = -12;
    } else {
        let t = BIOMES[level % BIOMES.length];
        let friction = isMobile ? 0.6 : 0.8;
        if(input.r) { player.dx += PHYSICS.acc; player.facing=1; } 
        else if(input.l) { player.dx -= PHYSICS.acc; player.facing=-1; } 
        else player.dx *= friction;
        if(player.dx > PHYSICS.spd) player.dx = PHYSICS.spd; if(player.dx < -PHYSICS.spd) player.dx = -PHYSICS.spd;
    }
    
    if(input.j && !input.jLock) {
        if(player.ground || (player.jumps > 0 && player.jumps < (player.kart?999:3))) { 
            player.dy = (player.ground ? PHYSICS.jump : PHYSICS.jump*0.9); 
            player.jumps++; input.jLock=true; playTone(330,'square',0.1); 
        }
    }
    if(!input.j) input.jLock = false;

    player.dy += PHYSICS.grav; player.x += player.dx; player.y += player.dy;
    if(player.kart && player.y > canvas.height-100) { player.y = canvas.height-100; player.dy=0; player.ground=true; }
    camX += (player.x - canvas.width*0.3 - camX) * 0.1; if(camX<0) camX=0;
    if(player.y > canvas.height+100 && !player.kart) gameOver();

    player.ground = false;
    blocks.forEach(b => {
        if(colCheck(player, b)) {
            if(player.dy >= 0 && player.y+player.h-player.dy <= b.y+25) { player.y = b.y-player.h; player.dy=0; player.ground=true; player.jumps=0; }
            else if(player.dy < 0 && player.y-player.dy >= b.y+b.h-20) { player.y = b.y+b.h; player.dy=0; spawnItem(b); }
            else if(player.dx > 0) { player.x = b.x-player.w; player.dx=0; }
            else if(player.dx < 0) { player.x = b.x+b.w; player.dx=0; }
        }
    });

    if(player.inPipe) {
        player.x += (goal.cx - player.x - player.w/2) * 0.2; player.y += 3; if(player.w>0)player.w-=0.5;
        if(player.y > canvas.height) { level++; initLevel(level); }
        draw(); requestAnimationFrame(update); return;
    }

    // BOSS LOGIC
    if(boss && !boss.dead) {
        if(boss.x < player.x + 800) {
            document.getElementById('boss-ui').style.display = 'block';
            document.getElementById('boss-name').innerText = boss.name;
            document.getElementById('boss-hp').style.width = (boss.hp / boss.maxHp * 100) + '%';
            document.getElementById('boss-hp').style.background = boss.style===1 ? "#7B1FA2" : (boss.style===2 ? "#FFD700" : "#ff4444");

            boss.timer++;
            boss.x += boss.dx; boss.dy += PHYSICS.grav; boss.y += boss.dy;
            if(boss.y > canvas.height - 180 - boss.h) { boss.y = canvas.height - 180 - boss.h; boss.dy = 0; }
            if(boss.x < camX) boss.dx = Math.abs(boss.dx);
            if(boss.x > goal.x - 100) boss.dx = -Math.abs(boss.dx);

            // Special Moves based on Style
            if(boss.style === 1) { // Ninja: Jump often
                if(boss.timer % 60 === 0) boss.dy = -15;
            } else { // Titan/Gold: Charge
                if(boss.timer % 120 === 0) { boss.dy = -10; boss.dx = (player.x < boss.x) ? -boss.baseSpd*2 : boss.baseSpd*2; }
            }
            if(boss.iframes > 0) boss.iframes--;

            if(colCheck(player, boss)) {
                if(player.kart) { boss.hp = 0; boss.dead = true; score += 5000; spawnExplosion(boss.x, boss.y); }
                else if(player.dy > 0 && player.y + player.h < boss.y + boss.h * 0.6) {
                    if(boss.iframes <= 0) {
                        boss.hp--; boss.iframes = 60; player.dy = -10; spawnExplosion(boss.x+boss.w/2, boss.y);
                        playTone(150, 'square', 0.3);
                        if(boss.hp <= 0) { boss.dead = true; score += 3000; playTone(50, 'noise', 0.8); }
                    }
                } else if(player.invul <= 0) {
                    if(player.big) { player.big=false; player.w=32; player.h=40; player.invul=60; playTone(100,'sawtooth',0.5); }
                    else gameOver();
                }
            }
        }
    } else { document.getElementById('boss-ui').style.display = 'none'; }

    // ITEMS & ENEMIES
    items.forEach((it, i) => {
        if(it.state!=='static') { it.dy+=0.5; it.x+=it.dx; it.y+=it.dy; }
        blocks.forEach(b => { if(colCheck(it, b) && it.state!=='static') { if(it.dy>0) { it.y=b.y-it.h; it.dy=0; } else it.dx*=-1; } });
        if(colCheck(player, it)) {
            items.splice(i,1); 
            if(it.type===0) score+=100; else if(it.type===1) { player.big=true; player.w=40; player.h=56; } else { player.kart=true; player.timer=600; player.w=48; player.h=24; }
            playTone(it.type===0?800:200, 'sine', 0.1);
        }
    });

    enemies.forEach(e => {
        if(e.dead) return;
        e.timer++;
        if(e.type === 1) { // Bat
             e.x += e.dx; e.y = e.anchorY + Math.sin(frames * 0.1) * 60; 
        } else if(e.type === 2) { // Drill
            let cycle = e.timer % 180;
            if(cycle < 90 && e.y > e.anchorY - e.h) e.y -= 2;
            if(cycle >= 90 && e.y < e.anchorY) e.y += 2;
        } else if(e.type === 3) { // Frog
            e.x += e.dx; e.dy += PHYSICS.grav; e.y += e.dy; 
            if(e.y >= e.anchorY) { e.y = e.anchorY; e.dy = 0; e.dx=0; }
            if(Math.random()<0.02 && e.dy===0) { e.dy=-10; e.dx = (player.x<e.x)?-2:2; }
        } else { // Walker
            e.x += e.dx; if(frames%60==0 && Math.random()<0.3) e.dx *= -1;
        }
        
        if(colCheck(player, e)) {
            if(player.kart) { e.dead=true; score+=500; spawnExplosion(e.x,e.y); }
            else if(e.type !== 2 && player.dy > 0 && player.y+player.h < e.y+e.h*0.8) { e.dead=true; player.dy=-8; score+=200; spawnExplosion(e.x,e.y); } 
            else { if(player.big) { player.big=false; player.invul=60; } else if(player.invul<=0) gameOver(); }
        }
    });

    if(goal && player.ground && Math.abs(player.y-(goal.y-player.h))<10 && player.x>goal.x && player.x<goal.x+goal.w) {
         if(Math.abs(player.dx)<2) player.inPipe=true; 
    }

    draw();
    requestAnimationFrame(update);
}

function spawnExplosion(x, y) { for(let i=0;i<8;i++) particles.push({x:x,y:y,dx:(Math.random()-0.5)*10,dy:(Math.random()-0.5)*10,life:15,c:'#fff'}); }
function colCheck(a, b) { return a.x<b.x+b.w && a.x+a.w>b.x && a.y<b.y+b.h && a.y+a.h>b.y; }
function gameOver() { running = false; document.getElementById('menu').style.display='flex'; document.getElementById('btn-retry').style.display='block'; }
function resetGame() { initAudio(); level=0; score=0; startGame(); }
function retryLevel() { initAudio(); startGame(); }
function startGame() { document.getElementById('menu').style.display='none'; player.big=false; player.kart=false; initLevel(level); running=true; update(); }

// --- ADVANCED DRAWING ---
function drawRect(x, y, w, h, c) { ctx.fillStyle=c; ctx.fillRect(x,y,w,h); }
function drawCircle(x, y, r, c) { ctx.beginPath(); ctx.arc(x,y,r,0,Math.PI*2); ctx.fillStyle=c; ctx.fill(); }
function drawEye(x, y, size, lookDir) {
    drawCircle(x, y, size, "#fff");
    drawCircle(x + lookDir*2, y, size/2, "#000");
}

function draw() {
    let t = BIOMES[level % BIOMES.length];
    ctx.fillStyle = t.bg; ctx.fillRect(0,0,canvas.width,canvas.height);
    document.getElementById('world-ui').innerText = "WORLD 1-" + (level+1);

    // Blocks with Top Layer
    blocks.forEach(b => {
        if(b.x > camX+canvas.width || b.x+b.w < camX) return;
        let bx = b.x-camX;
        ctx.fillStyle = b.c; ctx.fillRect(bx, b.y, b.w, b.h);
        if(b.type === 'ground') { ctx.fillStyle = t.top; ctx.fillRect(bx, b.y, b.w, 15); } // Grass top
        if(b.type === 'brick') { 
            ctx.fillStyle = "rgba(0,0,0,0.2)"; ctx.fillRect(bx+5, b.y+5, b.w-10, b.h-10); // Bevel
            if(b.content) { ctx.fillStyle="#FFD700"; ctx.fillText("?", bx+20, b.y+40); }
        }
        if(b.type === 'pipe') {
             ctx.fillStyle = "rgba(255,255,255,0.2)"; ctx.fillRect(bx+5, b.y, 10, b.h); // Highlight
             ctx.fillStyle = "#000"; ctx.strokeRect(bx, b.y, b.w, b.h);
        }
    });

    items.forEach(it => {
        if(it.x > camX+canvas.width) return;
        let ix = it.x-camX;
        if(it.type===0) { 
            // 3D Coin
            let rot = Math.abs(Math.sin(frames*0.1));
            ctx.fillStyle="#FFD700"; ctx.beginPath(); ctx.ellipse(ix+15,it.y+15, 12*rot, 12, 0, 0, 6.28); ctx.fill();
            ctx.fillStyle="#FFF"; ctx.fillText("$", ix+10, it.y+22);
        }
        else if(it.type===1) { // Mushroom
             drawCircle(ix+15, it.y+10, 15, "#D32F2F"); // Cap
             drawCircle(ix+8, it.y+8, 4, "#fff"); drawCircle(ix+22, it.y+8, 4, "#fff"); // Dots
             drawRect(ix+8, it.y+15, 14, 15, "#FFE0B2"); // Stem
        }
        else { ctx.fillStyle="#2979FF"; ctx.fillRect(ix,it.y,it.w,it.h); ctx.fillStyle="#FFF"; ctx.fillText("K", ix+10, it.y+20); }
    });

    if(goal) { ctx.fillStyle=t.pipe; ctx.fillRect(goal.x-camX-5, goal.y, goal.w+10, 30); ctx.fillStyle="#fff"; ctx.fillText("GOAL", goal.x-camX+15, goal.y+60); }

    // BOSS DRAWING
    if(boss && !boss.dead) {
        let bx = boss.x - camX;
        let shake = (boss.iframes>0)?(Math.random()*4-2):0;
        
        ctx.save();
        ctx.translate(bx + boss.w/2 + shake, boss.y + boss.h/2);
        
        if(boss.style === 0) { // TITAN (Red Square with Spikes)
            ctx.fillStyle = boss.color; ctx.fillRect(-boss.w/2, -boss.h/2, boss.w, boss.h);
            drawEye(-15, -10, 8, -1); drawEye(15, -10, 8, -1);
            // Spikes
            ctx.fillStyle = "#fff";
            ctx.beginPath(); ctx.moveTo(-boss.w/2, -boss.h/2); ctx.lineTo(-boss.w/2-10, -boss.h/2+20); ctx.lineTo(-boss.w/2, -boss.h/2+40); ctx.fill();
        } 
        else if (boss.style === 1) { // NINJA (Purple Circle)
            drawCircle(0, 0, boss.w/2, boss.color);
            // Bandana
            ctx.fillStyle = "#000"; ctx.fillRect(-boss.w/2, -10, boss.w, 15);
            ctx.fillStyle = "#fff"; ctx.fillRect(-15, -8, 10, 4); ctx.fillRect(5, -8, 10, 4); // Angry Eyes
        } 
        else { // GOLD KING (Big Crown)
            ctx.fillStyle = boss.color; ctx.fillRect(-boss.w/2, -boss.h/2, boss.w, boss.h);
            ctx.fillStyle = "#FFA000"; ctx.fillRect(-boss.w/2+10, -boss.h/2+10, boss.w-20, boss.h-20); // Inner detail
            drawEye(-30, 0, 12, -1); drawEye(30, 0, 12, -1);
            // Crown
            ctx.fillStyle = "#FFFF00"; 
            ctx.beginPath(); ctx.moveTo(-40,-boss.h/2); ctx.lineTo(-20,-boss.h/2-30); ctx.lineTo(0,-boss.h/2); ctx.lineTo(20,-boss.h/2-30); ctx.lineTo(40,-boss.h/2); ctx.fill();
        }
        ctx.restore();
    }

    // ENEMIES
    enemies.forEach(e => {
        if(e.dead || e.x > camX+canvas.width) return;
        let ex = e.x - camX;
        
        if(e.type === 1) { // Bat
            ctx.fillStyle = "#5E35B1"; drawCircle(ex+20, e.y+15, 12, "#5E35B1"); // Body
            drawEye(ex+16, e.y+12, 3, 0); drawEye(ex+24, e.y+12, 3, 0);
            // Wings
            let wingY = Math.sin(frames*0.5)*10;
            ctx.fillStyle = "#4527A0"; 
            ctx.beginPath(); ctx.moveTo(ex+10, e.y+15); ctx.lineTo(ex-10, e.y+5+wingY); ctx.lineTo(ex+10, e.y+25); ctx.fill();
            ctx.beginPath(); ctx.moveTo(ex+30, e.y+15); ctx.lineTo(ex+50, e.y+5+wingY); ctx.lineTo(ex+30, e.y+25); ctx.fill();
        }
        else if(e.type === 2) { // DRILL BOT (Replaces Cactus)
            ctx.save();
            ctx.translate(ex+20, e.y+30);
            let spin = Math.sin(frames*0.5)*5;
            ctx.fillStyle = "#B0BEC5"; // Silver
            ctx.beginPath(); ctx.moveTo(-15, 30); ctx.lineTo(0, -30); ctx.lineTo(15, 30); ctx.fill(); // Drill cone
            // Spiral lines
            ctx.strokeStyle = "#546E7A"; ctx.lineWidth=2;
            ctx.beginPath(); ctx.moveTo(-10, 20+spin); ctx.lineTo(5, -10+spin); ctx.stroke();
            ctx.beginPath(); ctx.moveTo(-5, 30+spin); ctx.lineTo(10, 0+spin); ctx.stroke();
            ctx.restore();
        }
        else if(e.type === 3) { // Frog
            ctx.fillStyle = "#43A047"; // Green
            drawCircle(ex+18, e.y+20, 14, "#43A047"); // Body
            drawEye(ex+12, e.y+10, 4, 0); drawEye(ex+24, e.y+10, 4, 0); // Eyes pop out
            // Legs
            ctx.strokeStyle = "#2E7D32"; ctx.lineWidth=4;
            ctx.beginPath(); ctx.moveTo(ex+5, e.y+25); ctx.lineTo(ex-5, e.y+32); ctx.stroke();
            ctx.beginPath(); ctx.moveTo(ex+31, e.y+25); ctx.lineTo(ex+41, e.y+32); ctx.stroke();
        }
        else { // Walker (Mushroom/Goom)
            ctx.fillStyle = "#D84315"; // Burnt Orange
            ctx.beginPath(); ctx.arc(ex+18, e.y+18, 16, Math.PI, 0); ctx.lineTo(ex+34, e.y+34); ctx.lineTo(ex+2, e.y+34); ctx.fill(); // Shape
            drawEye(ex+12, e.y+15, 4, e.dx>0?1:-1); drawEye(ex+24, e.y+15, 4, e.dx>0?1:-1);
            // Feet animation
            let walk = Math.sin(frames*0.2)*5;
            ctx.fillStyle = "#000"; 
            ctx.fillRect(ex+8+walk, e.y+32, 8, 6); ctx.fillRect(ex+20-walk, e.y+32, 8, 6);
        }
    });
    
    // Particles
    particles.forEach((p, i) => {
        p.x += p.dx; p.y += p.dy; p.life--;
        ctx.fillStyle = p.c; ctx.fillRect(p.x-camX, p.y, 5, 5);
        if(p.life<=0) particles.splice(i, 1);
    });

    // Player
    if(!player.dead && player.invul % 4 < 2) {
        let px = player.x-camX; let py = player.y;
        if(player.kart) {
             ctx.fillStyle="#FF1744"; ctx.fillRect(px,py+15,player.w,15); // Car Body
             drawCircle(px+10, py+30, 6, "#000"); drawCircle(px+player.w-10, py+30, 6, "#000"); // Wheels
             ctx.fillStyle="#FFEB3B"; ctx.fillRect(px+player.w-5, py+18, 5, 5); // Headlight
        } else {
             // 3D Player
             let dir = player.facing;
             ctx.fillStyle = "#b71c1c"; // Red Cap
             ctx.fillRect(px, py, player.w, 10); ctx.fillRect(dir>0?px+5:px-5, py+8, player.w, 4); // Brim
             ctx.fillStyle = "#FFCCBC"; // Face
             ctx.fillRect(px+5, py+10, player.w-10, 10);
             drawEye(dir>0?px+22:px+10, py+15, 3, dir); // Eye
             ctx.fillStyle = "#0D47A1"; // Blue Overalls
             ctx.fillRect(px+5, py+20, player.w-10, 15);
             // Arms/Legs
             ctx.fillStyle = "#b71c1c"; 
             let run = (Math.abs(player.dx)>0.1) ? Math.sin(frames*0.5)*5 : 0;
             ctx.fillRect(px+(dir>0?0:20)+run, py+22, 8, 8); // Arm
             ctx.fillStyle = "#000"; // Shoes
             ctx.fillRect(px+5-run, py+35, 10, 5); ctx.fillRect(px+18+run, py+35, 10, 5);
        }
    }

    document.getElementById('score-ui').innerText="SCORE: "+score;
}

function checkOrient() { canvas.width=window.innerWidth; canvas.height=window.innerHeight; if(isMobile)document.getElementById('controls').style.display='block'; }
window.addEventListener('resize', checkOrient); checkOrient();
if(isMobile) { const b=(id,k)=>{let el=document.getElementById(id); el.addEventListener('touchstart',e=>{e.preventDefault();input[k]=true;}); el.addEventListener('touchend',e=>{e.preventDefault();input[k]=false;});}; b('btn-L','l'); b('btn-R','r'); b('btn-J','j'); }
window.addEventListener('keydown',e=>{if(e.key==='a'||e.key==='ArrowLeft')input.l=true;if(e.key==='d'||e.key==='ArrowRight')input.r=true;if(e.key==='w'||e.key===' '||e.key==='ArrowUp')input.j=true;});
window.addEventListener('keyup',e=>{if(e.key==='a'||e.key==='ArrowLeft')input.l=false;if(e.key==='d'||e.key==='ArrowRight')input.r=false;if(e.key==='w'||e.key===' '||e.key==='ArrowUp')input.j=false;});
document.addEventListener('click', function() { if(audioCtx && audioCtx.state === 'suspended') audioCtx.resume(); });

</script>
</body>
</html>
"""

st.components.v1.html(game_html, height=800)
