import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Super AI Kart: V47.3 Smart Fix",
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
    #coin-ui { left: 20px; top: 60px; color: #FFD700; background: rgba(0,0,0,0.3); padding: 5px 10px; border-radius: 10px; display: flex; align-items: center; }
    #world-ui { right: 20px; color: #FFD700; background: rgba(0,0,0,0.3); padding: 5px 10px; border-radius: 10px; }
    #hp-ui { top: 100px; left: 20px; color: #FF5252; font-size: 18px; }
    
    #boss-ui { 
        position: absolute; top: 80px; left: 50%; transform: translateX(-50%); 
        width: 300px; padding: 5px; background: rgba(0,0,0,0.6); border-radius: 15px; display: none; border: 2px solid #fff;
    }
    #boss-name { color: #fff; text-align: center; font-size: 16px; margin-bottom: 4px; text-transform: uppercase; text-shadow: 1px 1px 0 #000; font-weight: 900; }
    #boss-bar-bg { width: 100%; height: 16px; background: #333; border-radius: 8px; overflow: hidden; border: 1px solid #777; }
    #boss-hp { width: 100%; height: 100%; background: linear-gradient(90deg, #FF9800, #D50000); transition: width 0.2s; }

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
    #btn-F { right: 130px; width: 60px; height: 60px; background: rgba(255,165,0,0.3); font-size: 24px; border-color: #FFD700; display:none; }

    #menu {
        position: absolute; top: 0; left: 0; width: 100%; height: 100%;
        background: linear-gradient(135deg, rgba(20,0,20,0.95), rgba(60,0,0,0.95)); z-index: 100;
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
    <div id="coin-ui" class="hud">🪙 0</div>
    <div id="world-ui" class="hud">WORLD 1-1</div>
    <div id="hp-ui" class="hud">HP: 1</div>
    
    <div id="boss-ui">
        <div id="boss-name">BOSS</div>
        <div id="boss-bar-bg"><div id="boss-hp"></div></div>
    </div>
    
    <div id="controls">
        <div class="btn" id="btn-L">◀</div>
        <div class="btn" id="btn-R">▶</div>
        <div class="btn" id="btn-F">🔥</div>
        <div class="btn" id="btn-J">🚀</div>
    </div>

    <div id="menu">
        <h1 id="menu-title">SUPER AI KART</h1>
        <p id="menu-sub">V47.3: AI FIX & BOUNDARY</p>
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
let coinCount = 0; 
let level = 0;
let audioCtx = null;
let bgmTimer = null;
let shake = 0;

let player = { 
    x:100, y:0, w:32, h:40, dx:0, dy:0, 
    ground:false, jumps:0, dead:false, inPipe:false, 
    hp: 1, hasFire: false,
    kart:false, timer:0, invul:0, facing:1 
};

let input = { l:false, r:false, j:false, jLock:false, f:false, fLock:false };
let camX = 0;
let blocks = [];
let enemies = [];
let particles = [];
let items = []; 
let projectiles = []; 
let p_bullets = [];   
let goal = null;
let boss = null; 
let floatText = []; 

// Visuals & Biomes
const BIOMES = [
    { name: "PLAINS", bg: "#64B5F6", ground: "#5D4037", top: "#81C784", brick: "#FFB74D", pipe: "#43A047" },
    { name: "DESERT", bg: "#FFCC80", ground: "#E65100", top: "#FFAB91", brick: "#FFE0B2", pipe: "#2E7D32" },
    { name: "CAVE",   bg: "#263238", ground: "#3E2723", top: "#4E342E", brick: "#8D6E63", pipe: "#546E7A" },
    { name: "SKY",    bg: "#E1F5FE", ground: "#0288D1", top: "#FFFFFF", brick: "#B3E5FC", pipe: "#01579B" }
];

function initAudio() {
    if(!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    if(audioCtx.state === 'suspended') audioCtx.resume();
    if(bgmTimer) clearInterval(bgmTimer);
    playBGM();
    bgmTimer = setInterval(playBGM, 150);
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
    boss1: [110,110,0,105,105,0,100,100,0,95,95,0],
    boss2: [880,0,440,0,880,0,440,0,830,0,415,0],
    boss3: [220,220,294,294,330,330,294,294],
    kart:  [440,440,554,659,440,554,659,880]
};

function playBGM() {
    if(!running || player.dead) return;
    melodyStep++;
    let track = MELODIES.peace;
    let wave = 'triangle';
    let tempo = 2;
    
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

function addCoin(x, y, amount=1) {
    coinCount += amount;
    score += 100 * amount;
    if(coinCount >= 50) {
        coinCount -= 50;
        player.hp++; 
        if(player.hp >= 2) { player.w=40; player.h=56; }
        playTone(600, 'square', 0.3); playTone(800, 'square', 0.3);
        floatText.push({x:player.x, y:player.y-20, t:"+1 HP", life:60});
        for(let k=0;k<10;k++) particles.push({x:player.x+15,y:player.y+20,dx:(Math.random()-0.5)*10,dy:(Math.random()-0.5)*10,life:30,c:'#FFD700'});
    }
    playTone(1050, 'square', 0.1); 
    floatText.push({x:x, y:y-20, t:"+1 🪙", life:30});
}

// --- Init & Gen ---
function initLevel(lvl) {
    blocks = []; enemies = []; particles = []; items = []; projectiles = []; p_bullets = []; boss = null; floatText = [];
    let t = BIOMES[lvl % BIOMES.length];
    
    player.x = 100; player.y = 0; player.dx=0; player.dy=0;
    if (player.hp < 1) player.hp = 1;
    player.w = player.hp > 1 ? 40 : 32; 
    player.h = player.hp > 1 ? 56 : 40; 
    player.inPipe = false; player.dead = false; player.invul = 0;
    
    camX = 0;
    document.getElementById('boss-ui').style.display = 'none';

    let groundY = canvas.height - 80;
    blocks.push({x:-200, y:groundY, w:800, h:100, c: t.ground, type:'ground'}); 
    
    let x = 600;
    let endX = 3500 + lvl * 800;
    
    while(x < endX) {
        let rng = Math.random();
        
        if(Math.random() < 0.25) {
            let cy = groundY - 250 - Math.random()*80; 
            for(let k=0; k<4; k++) items.push({ x: x + k*35, y: cy + Math.sin(k)*20, w:30, h:30, type:0, dy:0, dx:0, state:'static' });
        }

        if(rng < 0.4) { 
            let w = 400 + Math.random() * 400;
            blocks.push({x:x, y:groundY, w:w, h:200, c: t.ground, type:'ground'});
            if(Math.random() < 0.7) spawnEnemy(x + w/2, groundY-40, (Math.random()<0.3)?'jumper':'walker');
            createBricks(x + 100, groundY - 140, t);
            x += w;
        } 
        else if(rng < 0.6) {
            let gap = 100 + Math.random() * 40;
            spawnEnemy(x + gap/2, groundY - 150 - Math.random()*100, 'flyer');
            x += gap; 
        }
        else if(rng < 0.8) {
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
        else {
            let w = 300;
            blocks.push({x:x, y:groundY, w:w, h:200, c: t.ground, type:'ground'});
            let ph = 60 + Math.random()*60;
            let px = x + 100;
            blocks.push({x:px, y:groundY-ph, w:60, h:ph, c: t.pipe, type:'pipe'});
            spawnEnemy(px+10, groundY-ph, 'drill'); 
            x += w;
        }
    }
    
    blocks.push({x:x, y:groundY, w:1000, h:100, c: t.ground, type:'ground'});
    
    let bossStyle = lvl % 3;
    let bossProps = {
        0: { name: "IRON TITAN", color: "#B71C1C", w:100, h:100, hp:10, spd:2 },
        1: { name: "SHADOW NINJA", color: "#4A148C", w:70, h:70, hp:8, spd:5 },
        2: { name: "GOLD KING", color: "#FFD700", w:110, h:110, hp:12, spd:2 }
    }[bossStyle];

    boss = {
        x: x + 600, y: groundY - bossProps.h, w: bossProps.w, h: bossProps.h, 
        dx: 0, dy: 0, hp: bossProps.hp, maxHp: bossProps.hp,
        iframes: 0, dead: false, style: bossStyle, name: bossProps.name,
        baseSpd: bossProps.spd, timer: 0, action: 'chase'
    };
    
    x += 1000;
    goal = { x: x + 50, y: groundY-150, w: 70, h: 150, cx: x+85 };
    blocks.push({ x: goal.x, y: goal.y, w: goal.w, h: goal.h, c: t.pipe, type:'pipe' });
    blocks.push({x:x, y:groundY, w:300, h:100, c: t.ground, type:'ground'});
}

function createBricks(bx, by, t) {
    let rng = Math.random();
    let content = null;
    if(rng < 0.5) content = "coin";
    else if(rng < 0.7) content = "mushroom"; 
    else if(rng < 0.85) content = "flower"; 
    else if(rng < 0.95) content = "kart";
    
    blocks.push({ x:bx, y:by, w:60, h:60, c: t.brick, type:'brick', content:content, hit:false });
    blocks.push({x:bx+60, y:by, w:60, h:60, c: t.brick, type:'brick', content:null});
    blocks.push({x:bx-60, y:by, w:60, h:60, c: t.brick, type:'brick', content:null});
}

function spawnEnemy(x, y, type) {
    let e = { x:x, y:y, w:36, h:36, dx:-1.5, dy:0, dead:false, type:0, anchorY:y, timer:0, facing:-1, ground:false };
    if(type === 'flyer') { e.type = 1; e.dx = -2; e.w=40; e.h=30; }
    else if(type === 'drill') { e.type = 2; e.dx = 0; e.y += 30; e.anchorY = y; e.w=40; e.h=60; }
    else if(type === 'jumper') { e.type = 3; e.dx = -1.0; e.h=32; }
    enemies.push(e);
}

function spawnItem(block) {
    if(!block.content) return;
    if(block.content === "coin") {
        addCoin(block.x + 30, block.y); 
        block.content=null; block.hit=true;
        return; 
    }
    let type = 1;
    if(block.content === "kart") type = 2;
    if(block.content === "flower") type = 3;

    let idX = 2; 
    items.push({ x: block.x+15, y: block.y-32, w:30, h:30, type:type, dy:-8, dx:idX, state:'spawning' });
    playTone(500, 'square', 0.1);
    block.content=null; block.hit=true;
}

function shootFireball() {
    if(!player.hasFire || player.kart || player.inPipe || player.dead) return;
    p_bullets.push({
        x: player.x + (player.facing>0 ? player.w : 0),
        y: player.y + 10,
        w: 12, h: 12,
        dx: player.facing * 8,
        dy: 0,
        life: 60
    });
    playTone(800, 'sawtooth', 0.05);
}

function update() {
    if(!running) return;
    frames++;
    if(shake>0) shake--;
    if(player.invul > 0) player.invul--;

    // Inputs & Logic
    if(player.hasFire) document.getElementById('btn-F').style.display = 'flex';
    else document.getElementById('btn-F').style.display = 'none';

    if(input.f && !input.fLock) {
        shootFireball();
        input.fLock = true;
    }
    if(!input.f) input.fLock = false;

    // Player Physics
    if(player.kart) {
        player.timer--;
        if(player.timer <= 0) { player.kart = false; player.w = player.hp>1?40:32; playTone(150,'sawtooth',0.5); }
        if(input.r) player.dx += 1.5; else if(input.l) player.dx -= 1.5; else player.dx *= 0.9;
        if(player.dx > 12) player.dx = 12; if(player.dx < -12) player.dx = -12;
    } else {
        let friction = isMobile ? 0.6 : 0.8;
        if(input.r) { player.dx += PHYSICS.acc; player.facing=1; } 
        else if(input.l) { player.dx -= PHYSICS.acc; player.facing=-1; } 
        else player.dx *= friction;
        if(player.dx > PHYSICS.spd) player.dx = PHYSICS.spd; if(player.dx < -PHYSICS.spd) player.dx = -PHYSICS.spd;
    }
    
    if(input.j && !input.jLock && !player.inPipe) {
        if(player.ground || (player.jumps > 0 && player.jumps < (player.kart?999:3))) { 
            player.dy = (player.ground ? PHYSICS.jump : PHYSICS.jump*0.9); 
            player.jumps++; input.jLock=true; playTone(330,'square',0.1); 
            if(player.jumps === 3) {
                 for(let k=0; k<12; k++) particles.push({x: player.x + player.w/2, y: player.y + player.h, dx: (Math.random()-0.5) * 12, dy: (Math.random() * 8) + 2, life: 20, c: '#00E676'});
                 playTone(600, 'square', 0.15); 
            }
        }
    }
    if(!input.j) input.jLock = false;

    player.dy += PHYSICS.grav; player.x += player.dx; player.y += player.dy;
    
    // --- FIX 1: LEFT SCREEN BOUNDARY ---
    // Prevent player from going behind the camera (causing sticky camera or lost vision)
    if(player.x < camX) { player.x = camX; player.dx = 0; }
    
    if(player.kart && player.y > canvas.height-100) { player.y = canvas.height-100; player.dy=0; player.ground=true; }
    
    // Camera Logic
    camX += (player.x - canvas.width*0.3 - camX) * 0.1; 
    if(camX<0) camX=0;
    
    if(player.y > canvas.height+100 && !player.kart && !player.inPipe) gameOver();

    player.ground = false;
    
    blocks.forEach(b => {
        if(player.inPipe) return; 
        if(colCheck(player, b)) {
            if(player.dy >= 0 && player.y+player.h-player.dy <= b.y+25) { player.y = b.y-player.h; player.dy=0; player.ground=true; player.jumps=0; }
            else if(player.dy < 0 && player.y-player.dy >= b.y+b.h-20) { player.y = b.y+b.h; player.dy=0; spawnItem(b); }
            else if(player.dx > 0) { player.x = b.x-player.w; player.dx=0; }
            else if(player.dx < 0) { player.x = b.x+b.w; player.dx=0; }
        }
    });

    if(player.inPipe) {
        player.x += (goal.cx - player.x - player.w/2) * 0.2; 
        player.y += 5; 
        if(player.w>0) player.w -= 0.5;
        if(player.y > canvas.height + 50) { level++; initLevel(level); }
        draw(); requestAnimationFrame(update); return;
    }

    if(goal && player.ground) {
        let dist = Math.abs(player.x + player.w/2 - goal.cx);
        if(Math.abs(player.y - (goal.y - player.h)) < 15 && dist < 30) {
             if(player.kart) {
                 player.kart = false;
                 player.w = player.hp > 1 ? 40 : 32;
                 player.h = player.hp > 1 ? 56 : 40;
                 player.y = goal.y - player.h;
             }
             if(Math.abs(player.dx) < 6) {
                 player.dx *= 0.5;
                 if (Math.abs(player.dx) < 1) {
                     player.inPipe=true; 
                     playTone(100, 'sawtooth', 0.5);
                 }
             }
        }
    }

    p_bullets.forEach((b, i) => {
        b.x += b.dx; b.life--;
        if(boss && !boss.dead && colCheck(b, boss)) {
             boss.hp -= 1; 
             b.life = 0; 
             spawnExplosion(b.x, b.y);
             playTone(200, 'noise', 0.2);
             boss.iframes = 5; 
        }
        enemies.forEach(e => {
            if(!e.dead && colCheck(b, e)) {
                e.dead = true; b.life = 0;
                spawnExplosion(e.x, e.y);
                score += 100;
                playTone(200, 'noise', 0.2);
            }
        });
        if(b.life <= 0) p_bullets.splice(i, 1);
    });

    if(boss && !boss.dead) {
        if(boss.x < player.x + 800) {
            document.getElementById('boss-ui').style.display = 'block';
            document.getElementById('boss-name').innerText = boss.name;
            document.getElementById('boss-hp').style.width = (boss.hp / boss.maxHp * 100) + '%';
            
            boss.timer++;
            let dist = player.x - boss.x;
            
            if(boss.action === 'chase') {
                if(dist > 0) boss.dx += 0.2; else boss.dx -= 0.2;
                if(boss.dx > boss.baseSpd) boss.dx = boss.baseSpd;
                if(boss.dx < -boss.baseSpd) boss.dx = -boss.baseSpd;
                if(boss.timer > 120 && Math.random() < 0.05) {
                    boss.action = (Math.random() < 0.5) ? 'jump_attack' : 'shoot';
                    boss.timer = 0;
                }
            } 
            else if(boss.action === 'shoot') {
                boss.dx *= 0.9;
                if(boss.timer === 30) {
                    let pdx = (player.x > boss.x) ? 6 : -6;
                    let ptype = boss.style; 
                    projectiles.push({x: boss.x+boss.w/2, y: boss.y+boss.h/2, w:20, h:20, dx:pdx, dy: (player.y - boss.y)*0.02, type: ptype, life:100});
                    playTone(600, 'sawtooth', 0.2);
                }
                if(boss.timer > 60) { boss.action='chase'; boss.timer=0; }
            }
            else if(boss.action === 'jump_attack') {
                if(boss.timer === 1) { boss.dy = -18; boss.dx = (dist>0?4:-4); playTone(150, 'square', 0.3); } 
                if(boss.timer > 10 && boss.y >= canvas.height - 180 - boss.h && boss.dy > 0) {
                    boss.dy = 0; boss.y = canvas.height - 180 - boss.h;
                    shake = 10; 
                    spawnExplosion(boss.x, boss.y+boss.h);
                    spawnExplosion(boss.x+boss.w, boss.y+boss.h);
                    playTone(100, 'noise', 0.5);
                    boss.action = 'recover'; boss.timer=0;
                }
            }
            else if(boss.action === 'recover') {
                boss.dx = 0;
                if(boss.timer > 60) { boss.action='chase'; boss.timer=0; }
            }

            boss.dy += PHYSICS.grav; boss.y += boss.dy;
            boss.x += boss.dx;
            if(boss.y > canvas.height - 180 - boss.h) { boss.y = canvas.height - 180 - boss.h; boss.dy = 0; }
            if(boss.x < camX) boss.x = camX;
            if(boss.x > goal.x - 100) boss.x = goal.x - 100;
            
            if(boss.iframes > 0) boss.iframes--;

            if(colCheck(player, boss)) {
                if(player.kart) { boss.hp -= 2; boss.iframes=30; spawnExplosion(boss.x+boss.w/2,boss.y); playTone(100,'noise',0.5); }
                else if(player.dy > 0 && player.y + player.h < boss.y + boss.h * 0.6) {
                    if(boss.iframes <= 0) {
                        boss.hp--; boss.iframes = 30; player.dy = -10; spawnExplosion(boss.x+boss.w/2, boss.y);
                        playTone(150, 'square', 0.3);
                    }
                } else if(player.invul <= 0) { takeDamage(); }

                if(boss.hp <= 0) { 
                    boss.dead = true; score += 5000; playTone(50, 'noise', 0.8);
                    for(let i=0; i<30; i++) {
                        items.push({
                             x: boss.x + boss.w/2, y: boss.y + boss.h/2,
                             w: 30, h: 30, type: 0, 
                             dx: (Math.random()-0.5) * 10, dy: -5 - Math.random()*8, state: 'moving'
                        });
                    }
                }
            }
        }
    } else { document.getElementById('boss-ui').style.display = 'none'; }
    
    projectiles.forEach((p, i) => {
        p.x += p.dx; p.y += p.dy; p.life--;
        if(colCheck(player, p)) {
            if(player.invul<=0) takeDamage();
            p.life = 0;
        }
        if(p.life <= 0) projectiles.splice(i, 1);
    });

    items.forEach((it, i) => {
        if(it.state!=='static') { 
            it.dy+=0.5; it.x+=it.dx; it.y+=it.dy;
            if(it.type === 0) { it.dx *= 0.95; }
            if(it.y > canvas.height) items.splice(i,1); 
        }
        blocks.forEach(b => { 
            if(colCheck(it, b) && it.state!=='static') { 
                if (it.dy < 0) return;
                if(it.dy>0 && it.y+it.h-it.dy <= b.y+15) { 
                    it.y=b.y-it.h; it.dy= -it.dy * 0.5; if(Math.abs(it.dy) < 1) it.dy=0;
                } else { it.dx*=-1; } 
            } 
        });
        if(it.y > canvas.height - 110) { it.y = canvas.height - 110; it.dy = -it.dy * 0.5; if(Math.abs(it.dy) < 1) it.dy=0; }
        if(colCheck(player, it)) {
            items.splice(i,1); 
            if(it.type===0) { addCoin(it.x, it.y); } 
            else if(it.type===1) { 
                player.hp++; 
                if(player.hp > 1) { player.w=40; player.h=56; } 
                score += 1000; playTone(200,'square',0.3); spawnExplosion(player.x, player.y); 
                floatText.push({x:player.x, y:player.y-20, t:"HP UP!", life:60});
            } 
            else if(it.type===2) { player.kart=true; player.timer=600; player.w=48; player.h=24; }
            else if(it.type===3) { 
                player.hasFire=true; 
                player.hp++;
                player.w=40; player.h=56; score+=1000; playTone(200,'square',0.3); 
                floatText.push({x:player.x, y:player.y-20, t:"FIRE!", life:60}); 
            }
        }
    });

    enemies.forEach(e => {
        if(e.dead) return;
        e.timer++;

        if(e.type === 0 || e.type === 3) { // Walker or Jumper
             e.dy += 0.5; 
             e.y += e.dy;
             e.x += e.dx;
             e.ground = false;

             blocks.forEach(b => {
                if(colCheck(e, b)) {
                    if(e.dy > 0 && e.y + e.h - e.dy <= b.y + 10) {
                        e.y = b.y - e.h; e.dy = 0; e.ground = true;
                    } 
                    else if (e.dy < 0 && e.y - e.dy >= b.y + b.h - 10) { 
                         e.y = b.y + b.h; e.dy = 0;
                    }
                    else {
                        e.dx *= -1; 
                        e.x += e.dx; 
                    }
                }
             });
             
             // --- FIX 2: SMART CLIFF DETECTION ---
             // If enemy is on ground, check if there is ground ahead. If not, turn back.
             if(e.ground && e.type === 0) {
                 let lookAhead = (e.dx > 0) ? (e.w/2 + 5) : (-e.w/2 - 5);
                 let cx = e.x + e.w/2 + lookAhead;
                 let cy = e.y + e.h + 5;
                 
                 let hasGround = false;
                 // Use a simple check against blocks
                 for(let bi=0; bi<blocks.length; bi++) {
                     let b = blocks[bi];
                     // Check point (cx, cy) vs block rect
                     if(cx >= b.x && cx <= b.x + b.w && cy >= b.y && cy <= b.y + b.h) {
                         hasGround = true; break;
                     }
                 }
                 
                 if(!hasGround) {
                     e.dx *= -1; // Turn around
                     e.x += e.dx * 2; // Bump back a bit
                 }
             }
             
             if(e.type === 3 && e.ground && Math.random() < 0.02) {
                 e.dy = -10; e.dx = (player.x < e.x) ? -2 : 2;
             }
             
             if(e.y > canvas.height + 100) e.dead = true; 
        } 
        else if(e.type === 1) { 
             e.x += e.dx; e.y = e.anchorY + Math.sin(frames * 0.1) * 60; 
        }
        else if(e.type === 2) { 
             let cycle = e.timer % 180; 
             if(cycle < 90 && e.y > e.anchorY - e.h) e.y -= 2; 
             if(cycle >= 90 && e.y < e.anchorY) e.y += 2; 
        }
        
        if(colCheck(player, e)) {
            if(player.kart) { e.dead=true; score+=500; spawnExplosion(e.x,e.y); addCoin(e.x, e.y); }
            else if(e.type !== 2 && player.dy > 0 && player.y+player.h < e.y+e.h*0.8) { e.dead=true; player.dy=-8; score+=200; spawnExplosion(e.x,e.y); addCoin(e.x, e.y); } 
            else { if(player.invul<=0) takeDamage(); }
        }
    });

    draw();
    requestAnimationFrame(update);
}

function takeDamage() {
    if(player.kart) { player.kart = false; player.invul = 60; return; }
    if(player.hasFire) { player.hasFire = false; player.invul = 60; playTone(150, 'sawtooth', 0.5); return; }
    if(player.hp > 1) {
        player.hp--; player.invul = 60; playTone(150, 'sawtooth', 0.5);
        if(player.hp === 1) { player.w=32; player.h=40; } 
    } else { gameOver(); }
}

function spawnExplosion(x, y) { for(let i=0;i<8;i++) particles.push({x:x,y:y,dx:(Math.random()-0.5)*10,dy:(Math.random()-0.5)*10,life:15,c:'#fff'}); }
function colCheck(a, b) { return a.x<b.x+b.w && a.x+a.w>b.x && a.y<b.y+b.h && a.y+a.h>b.y; }
function gameOver() { running = false; document.getElementById('menu').style.display='flex'; document.getElementById('btn-retry').style.display='block'; }
function resetGame() { initAudio(); level=0; score=0; coinCount=0; player.hp=1; player.hasFire=false; startGame(); }
function retryLevel() { initAudio(); player.hp=1; player.hasFire=false; startGame(); }
function startGame() { document.getElementById('menu').style.display='none'; player.kart=false; initLevel(level); running=true; update(); }

function drawRect(x, y, w, h, c) { ctx.fillStyle=c; ctx.fillRect(x,y,w,h); }
function drawCircle(x, y, r, c) { ctx.beginPath(); ctx.arc(x,y,r,0,Math.PI*2); ctx.fillStyle=c; ctx.fill(); }
function drawEye(x, y, size, lookDir) { drawCircle(x, y, size, "#fff"); drawCircle(x + lookDir*2, y, size/2, "#000"); }

function draw() {
    let t = BIOMES[level % BIOMES.length];
    let sx = (shake>0) ? (Math.random()*shake - shake/2) : 0;
    let sy = (shake>0) ? (Math.random()*shake - shake/2) : 0;
    
    ctx.save();
    ctx.translate(sx, sy);
    
    ctx.fillStyle = t.bg; ctx.fillRect(0,0,canvas.width,canvas.height);
    document.getElementById('world-ui').innerText = "WORLD 1-" + (level+1);
    
    let hpText = "HP: " + player.hp;
    if(player.hp >= 5) hpText += " (SSJ GOLD)";
    else if(player.hp === 4) hpText += " (SSJ RED)";
    else if(player.hp === 3) hpText += " (SSJ BLUE)";
    else if(player.hp === 2) hpText += " (BIG)";
    
    document.getElementById('hp-ui').innerText = hpText;
    document.getElementById('hp-ui').style.color = (player.hp>1) ? "#00E676" : "#FF5252";
    document.getElementById('coin-ui').innerText = "🪙 " + coinCount + " / 50";

    blocks.forEach(b => {
        if(b.x > camX+canvas.width || b.x+b.w < camX) return;
        let bx = b.x-camX;
        ctx.fillStyle = b.c; ctx.fillRect(bx, b.y, b.w, b.h);
        if(b.type === 'ground') { ctx.fillStyle = t.top; ctx.fillRect(bx, b.y, b.w, 15); }
        if(b.type === 'brick') { 
            ctx.fillStyle = "rgba(0,0,0,0.2)"; ctx.fillRect(bx+5, b.y+5, b.w-10, b.h-10);
            if(b.content) { ctx.fillStyle="#FFD700"; ctx.font = "900 32px 'Arial Black', sans-serif"; ctx.textAlign = "center"; ctx.fillText("?", bx+30, b.y+42); ctx.textAlign = "start"; }
        }
        if(b.type === 'pipe') { ctx.fillStyle = "rgba(255,255,255,0.2)"; ctx.fillRect(bx+5, b.y, 10, b.h); ctx.fillStyle = "#000"; ctx.strokeRect(bx, b.y, b.w, b.h); }
    });

    items.forEach(it => {
        if(it.x > camX+canvas.width) return;
        let ix = it.x-camX;
        if(it.type===0) { let rot = Math.abs(Math.sin(frames*0.1)); ctx.fillStyle="#FFD700"; ctx.beginPath(); ctx.ellipse(ix+15,it.y+15, 12*rot, 12, 0, 0, 6.28); ctx.fill(); ctx.fillStyle="#FFF"; ctx.fillText("$", ix+10, it.y+22); }
        else if(it.type===1) { ctx.fillStyle = "#FFE0B2"; ctx.fillRect(ix+10, it.y+15, 10, 15); ctx.fillStyle = "#D50000"; ctx.beginPath(); ctx.arc(ix+15, it.y+15, 15, Math.PI, 0); ctx.fill(); ctx.fillStyle = "#fff"; ctx.beginPath(); ctx.arc(ix+10, it.y+10, 3, 0, Math.PI*2); ctx.fill(); }
        else if(it.type===2) { ctx.fillStyle="#2979FF"; ctx.fillRect(ix,it.y,it.w,it.h); ctx.fillStyle="#FFF"; ctx.fillText("K", ix+10, it.y+20); }
        else if(it.type===3) { 
             ctx.fillStyle="#4CAF50"; ctx.fillRect(ix+12, it.y+20, 6, 10);
             ctx.fillStyle="#FF5722"; drawCircle(ix+15, it.y+10, 10, "#FF5722");
             ctx.fillStyle="#FFEB3B"; drawCircle(ix+15, it.y+10, 4, "#FFEB3B");
        }
    });
    
    p_bullets.forEach(b => {
        ctx.fillStyle = "#FF5722"; drawCircle(b.x-camX, b.y, 6, "#FF5722");
        ctx.fillStyle = "#FFEB3B"; drawCircle(b.x-camX, b.y, 3, "#FFEB3B");
    });

    projectiles.forEach(p => {
        let px = p.x - camX;
        ctx.fillStyle = (p.type==0)?"#D50000":((p.type==1)?"#AA00FF":"#FFD700");
        drawCircle(px, p.y, 10, ctx.fillStyle);
        ctx.fillStyle = "#fff"; drawCircle(px, p.y, 5, "#fff");
    });

    if(goal) { ctx.fillStyle=t.pipe; ctx.fillRect(goal.x-camX-5, goal.y, goal.w+10, 30); ctx.fillStyle="#fff"; ctx.fillText("GOAL", goal.x-camX+15, goal.y+60); }

    if(boss && !boss.dead) {
        let bx = boss.x - camX;
        let shakeB = (boss.iframes>0)?(Math.random()*4-2):0;
        ctx.save(); ctx.translate(bx + boss.w/2 + shakeB, boss.y + boss.h/2);
        
        if(boss.action === 'jump_attack' || boss.action === 'shoot') {
             ctx.beginPath(); ctx.arc(0,0, boss.w, 0, Math.PI*2);
             ctx.fillStyle = `rgba(255, 0, 0, ${Math.abs(Math.sin(frames*0.2)) * 0.5})`;
             ctx.fill();
        }

        if(boss.style === 0) { 
            ctx.fillStyle = boss.color; ctx.fillRect(-boss.w/2, -boss.h/2, boss.w, boss.h);
            ctx.fillStyle = "#555";
            ctx.beginPath(); ctx.moveTo(-boss.w/2, -boss.h/2); ctx.lineTo(-boss.w/2-10, -boss.h/2+20); ctx.lineTo(-boss.w/2, -boss.h/2+40); ctx.fill();
            ctx.beginPath(); ctx.moveTo(boss.w/2, -boss.h/2); ctx.lineTo(boss.w/2+10, -boss.h/2+20); ctx.lineTo(boss.w/2, -boss.h/2+40); ctx.fill();
            drawEye(-15, -10, 8, (player.x<boss.x)?-2:2); drawEye(15, -10, 8, (player.x<boss.x)?-2:2);
        } 
        else if (boss.style === 1) { 
            if(Math.abs(boss.dx) > 2) ctx.globalAlpha = 0.5;
            drawCircle(0, 0, boss.w/2, boss.color);
            ctx.globalAlpha = 1.0;
            ctx.fillStyle = "#D50000"; ctx.fillRect(-boss.w/2, -20, boss.w, 10);
            let tailY = Math.sin(frames*0.5)*10;
            ctx.beginPath(); ctx.moveTo(boss.w/2, -15); ctx.lineTo(boss.w/2+30, -15+tailY); ctx.lineTo(boss.w/2+30, -5+tailY); ctx.lineTo(boss.w/2, -5); ctx.fill();
            ctx.fillStyle = "#fff"; ctx.fillRect(-15, -8, 10, 4); ctx.fillRect(5, -8, 10, 4);
        } 
        else { 
            ctx.fillStyle = boss.color; ctx.fillRect(-boss.w/2, -boss.h/2, boss.w, boss.h);
            ctx.fillStyle = "#FFA000"; ctx.fillRect(-boss.w/2+10, -boss.h/2+10, boss.w-20, boss.h-20);
            ctx.fillStyle = "#FFAB00"; ctx.beginPath(); ctx.moveTo(-boss.w/2, -boss.h/2); ctx.lineTo(-boss.w/2, -boss.h/2-30); ctx.lineTo(-boss.w/4, -boss.h/2-10); ctx.lineTo(0, -boss.h/2-40); ctx.lineTo(boss.w/4, -boss.h/2-10); ctx.lineTo(boss.w/2, -boss.h/2-30); ctx.lineTo(boss.w/2, -boss.h/2); ctx.fill();
            drawEye(-30, 0, 12, (player.x<boss.x)?-2:2); drawEye(30, 0, 12, (player.x<boss.x)?-2:2);
        }
        ctx.restore();
    }

    enemies.forEach(e => {
        if(e.dead || e.x > camX+canvas.width) return;
        let ex = e.x - camX;
        if(e.type === 1) {
            ctx.fillStyle = "#5E35B1"; drawCircle(ex+20, e.y+15, 12, "#5E35B1");
            drawEye(ex+16, e.y+12, 3, 0); drawEye(ex+24, e.y+12, 3, 0);
            let wingY = Math.sin(frames*0.5)*10;
            ctx.fillStyle = "#4527A0"; ctx.beginPath(); ctx.moveTo(ex+10, e.y+15); ctx.lineTo(ex-10, e.y+5+wingY); ctx.lineTo(ex+10, e.y+25); ctx.fill(); ctx.beginPath(); ctx.moveTo(ex+30, e.y+15); ctx.lineTo(ex+50, e.y+5+wingY); ctx.lineTo(ex+30, e.y+25); ctx.fill();
        }
        else if(e.type === 2) {
            ctx.save(); ctx.translate(ex+20, e.y+30);
            let spin = Math.sin(frames*0.5)*5;
            ctx.fillStyle = "#B0BEC5"; ctx.beginPath(); ctx.moveTo(-15, 30); ctx.lineTo(0, -30); ctx.lineTo(15, 30); ctx.fill();
            ctx.strokeStyle = "#546E7A"; ctx.lineWidth=2; ctx.beginPath(); ctx.moveTo(-10, 20+spin); ctx.lineTo(5, -10+spin); ctx.stroke(); ctx.beginPath(); ctx.moveTo(-5, 30+spin); ctx.lineTo(10, 0+spin); ctx.stroke();
            ctx.restore();
        }
        else if(e.type === 3) {
            ctx.fillStyle = "#43A047"; drawCircle(ex+18, e.y+20, 14, "#43A047");
            drawEye(ex+12, e.y+10, 4, 0); drawEye(ex+24, e.y+10, 4, 0);
            ctx.strokeStyle = "#2E7D32"; ctx.lineWidth=4; ctx.beginPath(); ctx.moveTo(ex+5, e.y+25); ctx.lineTo(ex-5, e.y+32); ctx.stroke(); ctx.beginPath(); ctx.moveTo(ex+31, e.y+25); ctx.lineTo(ex+41, e.y+32); ctx.stroke();
        }
        else {
            ctx.fillStyle = "#D84315"; ctx.beginPath(); ctx.arc(ex+18, e.y+18, 16, Math.PI, 0); ctx.lineTo(ex+34, e.y+34); ctx.lineTo(ex+2, e.y+34); ctx.fill();
            drawEye(ex+12, e.y+15, 4, e.dx>0?1:-1); drawEye(ex+24, e.y+15, 4, e.dx>0?1:-1);
            let walk = Math.sin(frames*0.2)*5; ctx.fillStyle = "#000"; ctx.fillRect(ex+8+walk, e.y+32, 8, 6); ctx.fillRect(ex+20-walk, e.y+32, 8, 6);
        }
    });
    
    particles.forEach((p, i) => {
        p.x += p.dx; p.y += p.dy; p.life--;
        ctx.fillStyle = p.c; ctx.fillRect(p.x-camX, p.y, 5, 5);
        if(p.life<=0) particles.splice(i, 1);
    });
    
    floatText.forEach((f, i) => {
        f.y -= 1; f.life--;
        ctx.fillStyle = "#fff"; ctx.font = "bold 20px Arial"; ctx.fillText(f.t, f.x-camX, f.y);
        if(f.life<=0) floatText.splice(i, 1);
    });

    if(!player.dead && player.invul % 4 < 2) {
        let px = player.x-camX; let py = player.y;
        if(player.kart) {
             ctx.fillStyle="#FF1744"; ctx.fillRect(px,py+15,player.w,15);
             drawCircle(px+10, py+30, 6, "#000"); drawCircle(px+player.w-10, py+30, 6, "#000");
             ctx.fillStyle="#FFEB3B"; ctx.fillRect(px+player.w-5, py+18, 5, 5);
        } else {
             let dir = player.facing;
             
             let hatC = "#b71c1c"; 
             let suitC = "#0D47A1"; 
             
             if(player.hp === 2) {
                 hatC = "#b71c1c";
                 suitC = "#0D47A1";
             } else if(player.hp === 3) {
                 hatC = "#00B0FF";
                 suitC = "#F57C00";
             } else if(player.hp === 4) {
                 hatC = "#D50000";
                 suitC = "#F57C00";
             } else if(player.hp >= 5) {
                 hatC = "#FFD700";
                 suitC = "#F57C00";
             }

             ctx.fillStyle = hatC; ctx.fillRect(px, py, player.w, 10); ctx.fillRect(dir>0?px+5:px-5, py+8, player.w, 4);
             ctx.fillStyle = "#FFCCBC"; ctx.fillRect(px+5, py+10, player.w-10, 10);
             drawEye(dir>0?px+22:px+10, py+15, 3, dir);
             ctx.fillStyle = suitC; ctx.fillRect(px+5, py+20, player.w-10, 15);
             
             ctx.fillStyle = hatC; 
             let run = (Math.abs(player.dx)>0.1) ? Math.sin(frames*0.5)*5 : 0;
             ctx.fillRect(px+(dir>0?0:20)+run, py+22, 8, 8);
             
             ctx.fillStyle = "#000"; ctx.fillRect(px+5-run, py+35, 10, 5); ctx.fillRect(px+18+run, py+35, 10, 5);
        }
    }
    
    ctx.restore();
    document.getElementById('score-ui').innerText="SCORE: "+score;
}

function checkOrient() { canvas.width=window.innerWidth; canvas.height=window.innerHeight; if(isMobile)document.getElementById('controls').style.display='block'; }
window.addEventListener('resize', checkOrient); checkOrient();
if(isMobile) { 
    const b=(id,k)=>{let el=document.getElementById(id); el.addEventListener('touchstart',e=>{e.preventDefault();input[k]=true;}); el.addEventListener('touchend',e=>{e.preventDefault();input[k]=false;});}; 
    b('btn-L','l'); b('btn-R','r'); b('btn-J','j'); b('btn-F','f');
}
window.addEventListener('keydown',e=>{
    if(e.key==='a'||e.key==='ArrowLeft')input.l=true;
    if(e.key==='d'||e.key==='ArrowRight')input.r=true;
    if(e.key==='w'||e.key===' '||e.key==='ArrowUp')input.j=true;
    if(e.key==='f'||e.key==='Shift')input.f=true;
});
window.addEventListener('keyup',e=>{
    if(e.key==='a'||e.key==='ArrowLeft')input.l=false;
    if(e.key==='d'||e.key==='ArrowRight')input.r=false;
    if(e.key==='w'||e.key===' '||e.key==='ArrowUp')input.j=false;
    if(e.key==='f'||e.key==='Shift')input.f=false;
});
document.addEventListener('click', function() { if(audioCtx && audioCtx.state === 'suspended') audioCtx.resume(); });

</script>
</body>
</html>
"""

st.components.v1.html(game_html, height=800)
