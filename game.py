import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Super AI Kart: V38 Boss & Loot",
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
    #boss-ui { 
        position: absolute; top: 100px; left: 50%; transform: translateX(-50%); 
        width: 300px; height: 20px; border: 2px solid #fff; display: none; 
    }
    #boss-hp { width: 100%; height: 100%; background: #D32F2F; transition: width 0.2s; }

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
    .btn-container { display: flex; gap: 20px; margin-top: 20px; }
    .start-btn {
        padding: 15px 40px; font-size: 24px; background: #FF3D00; color: white;
        border: 4px solid #fff; cursor: pointer; border-radius: 8px; font-weight: bold;
    }
    .retry-btn { background: #00E676; }
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
    <div id="boss-ui"><div id="boss-hp"></div></div>
    
    <div id="controls">
        <div class="btn" id="btn-L">◀</div>
        <div class="btn" id="btn-R">▶</div>
        <div class="btn" id="btn-J">🚀</div>
    </div>

    <div id="menu">
        <h1 id="menu-title">SUPER AI KART</h1>
        <p id="menu-sub">V38: BOSS BATTLE & LOOT</p>
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
    big: false, kart: false, timer: 0, invul: 0 
};
let input = { l:false, r:false, j:false, jLock:false };
let camX = 0;
let blocks = [];
let enemies = [];
let particles = [];
let items = []; 
let goal = null;
let boss = null; // BOSS对象

const BIOMES = [
    { name: "PLAINS", bg: "#5C94FC", ground: "#C84C0C", brick: "#FFB74D", pipe: "#00E676" },
    { name: "DESERT", bg: "#FFE0B2", ground: "#EF6C00", brick: "#FFCC80", pipe: "#2E7D32" },
    { name: "CAVE",   bg: "#212121", ground: "#5D4037", brick: "#8D6E63", pipe: "#66BB6A" },
    { name: "SNOW",   bg: "#81D4FA", ground: "#E1F5FE", brick: "#B3E5FC", pipe: "#0288D1" }, 
    { name: "HILLS",  bg: "#C5E1A5", ground: "#33691E", brick: "#AED581", pipe: "#558B2F" }
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
    // 如果Boss存活且在屏幕内，播放Boss战音乐
    if(boss && !boss.dead && boss.x < camX + canvas.width + 100) {
        let notes = [110, 110, 123, 110, 98, 87, 82, 110]; // 紧张的低音
        notes.forEach((freq, i) => { 
            setTimeout(() => { if(running) playTone(freq, 'sawtooth', 0.2, 0.1); }, i * 150); 
        });
        return;
    }

    let t = BIOMES[level % BIOMES.length];
    let notes = []; let wave = 'triangle'; let speed = 200;

    if (player.kart) {
        notes = [440, 440, 554, 659, 440, 554, 659, 880]; wave = 'sawtooth'; speed = 100;
    } else {
        switch(t.name) {
            case "PLAINS": notes = [262, 330, 392, 523, 392, 330, 262, 196]; wave = 'triangle'; break;
            case "DESERT": notes = [294, 311, 370, 294, 311, 370, 494, 294]; wave = 'sawtooth'; break;
            case "CAVE": notes = [110, 110, 0, 147, 110, 0, 131, 0]; wave = 'square'; speed=400; break;
            case "SNOW": notes = [523, 0, 659, 0, 784, 0, 1047, 0]; wave = 'sine'; break;
            case "HILLS": notes = [349, 349, 392, 392, 440, 440, 349, 0]; wave = 'square'; break;
        }
    }
    notes.forEach((freq, i) => { if(freq > 0) setTimeout(() => { if(running) playTone(freq, wave, 0.1, 0.05); }, i * speed); });
}

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
        let segmentType = Math.random();
        
        // --- 增加金币生成逻辑 ---
        if(Math.random() < 0.3) {
            // 空中生成一排金币
            let coinsY = groundY - 100 - Math.random()*100;
            for(let k=0; k<5; k++) {
                items.push({ x: x + k*40, y: coinsY, w:30, h:30, type:0, dy:0, dx:0, state:'static' });
            }
        }

        if(segmentType < 0.4) {
            let w = 400 + Math.random() * 400;
            blocks.push({x:x, y:groundY, w:w, h:200, c: t.ground, type:'ground'});
            if(Math.random() < 0.6) spawnEnemy(x + w/2, groundY-40, (Math.random()<0.3)?'jumper':'walker');
            
            // --- 疯狂增加砖块 ---
            if(Math.random() < 0.9) createBricks(x + 100, groundY - 140, t); // 概率由 0.7 提至 0.9
            x += w;
        } 
        else if(segmentType < 0.6) {
            let gap = 150 + Math.random() * 80;
            spawnEnemy(x + gap/2, groundY - 150 - Math.random()*100, 'flyer');
            // 坑上面悬浮金币
            items.push({ x: x + gap/2, y: groundY-150, w:30, h:30, type:0, dy:0, dx:0, state:'static' });
            x += gap; 
        }
        else if(segmentType < 0.8) {
            let steps = 3 + Math.floor(Math.random()*3);
            let platW = 150;
            for(let i=0; i<steps; i++) {
                blocks.push({x:x, y:groundY - i*40, w:60, h:200, c: t.brick, type:'ground'});
                x += 60;
            }
            blocks.push({x:x, y:groundY - (steps-1)*40, w:platW, h:200, c: t.ground, type:'ground'});
            if(Math.random()<0.5) spawnEnemy(x+platW/2, groundY - (steps-1)*40 - 40, 'walker');
            // 平台上有奖励
            createBricks(x+platW/2-30, groundY - (steps-1)*40 - 140, t);
            x += platW;
            if(Math.random() < 0.5) x += 100;
        }
        else {
            let w = 300;
            blocks.push({x:x, y:groundY, w:w, h:200, c: t.ground, type:'ground'});
            let ph = 60 + Math.random()*60;
            let px = x + 100;
            blocks.push({x:px, y:groundY-ph, w:60, h:ph, c: t.pipe, type:'pipe'});
            spawnEnemy(px+10, groundY-ph, 'plant');
            x += w;
        }
    }
    
    // --- BOSS ARENA ---
    // 生成一个宽阔的平台作为BOSS战场所
    blocks.push({x:x, y:groundY, w:1000, h:100, c: t.ground, type:'ground'});
    
    // 初始化BOSS
    boss = {
        x: x + 600, y: groundY - 80, w: 80, h: 80, 
        dx: -3, dy: 0, hp: 3, maxHp: 3,
        iframes: 0, dead: false, color: "#D32F2F", type: 'boss'
    };
    
    x += 1000;
    goal = { x: x + 50, y: groundY-150, w: 70, h: 150, cx: x+85 };
    blocks.push({ x: goal.x, y: goal.y, w: goal.w, h: goal.h, c: t.pipe, type:'pipe' });
    blocks.push({x:x, y:groundY, w:300, h:100, c: t.ground, type:'ground'});
}

function createBricks(bx, by, t) {
    let rng = Math.random();
    let content = null;
    // --- 提高物品掉落率 ---
    if(rng < 0.5) content = "coin"; // 50% 金币
    else if(rng < 0.7) content = "mushroom"; // 20% 蘑菇
    else if(rng < 0.8) content = "kart"; // 10% 卡丁车
    
    blocks.push({ x:bx, y:by, w:60, h:60, c: content?"#FFD700":t.brick, type:'brick', content:content, hit:false });
    blocks.push({x:bx+60, y:by, w:60, h:60, c: t.brick, type:'brick', content:null});
    blocks.push({x:bx-60, y:by, w:60, h:60, c: t.brick, type:'brick', content:null});
}

function spawnEnemy(x, y, type) {
    let e = { x:x, y:y, w:36, h:36, dx:-1.5, dy:0, dead:false, type:0, anchorY:y, timer:0 };
    if(type === 'flyer') { e.type = 1; e.dx = -2; e.w=40; e.h=20; }
    else if(type === 'plant') { e.type = 2; e.dx = 0; e.y += 30; e.anchorY = y; e.w=40; e.h=40; }
    else if(type === 'jumper') { e.type = 3; e.dx = -1.0; }
    enemies.push(e);
}

function spawnItem(block) {
    if(!block.content) return;
    let type = (block.content==="coin")?0:(block.content==="mushroom"?1:2);
    let isMoving = (type !== 0);
    items.push({ x: block.x+15, y: block.y, w:30, h:30, type:type, dy:-6, dx:isMoving?2:0, targetY:block.y-35, state:'spawning' });
    playTone(500, 'square', 0.1);
    block.content=null; block.c="#6D4C41"; block.hit=true;
}

function update() {
    if(!running) return;
    frames++;

    if(player.invul > 0) player.invul--;

    if(player.kart) {
        player.timer--;
        if(player.timer <= 0) { player.kart = false; player.w = player.big?40:32; playTone(150,'sawtooth',0.5); }
    }
    if(player.inPipe) {
        player.x += (goal.cx - player.x - player.w/2) * 0.2; player.y += 3; if(player.w>0)player.w-=0.5;
        if(player.y > canvas.height) { level++; initLevel(level); }
        draw(); requestAnimationFrame(update); return;
    }

    let t = BIOMES[level % BIOMES.length];
    let friction = (t.name === "SNOW") ? 0.96 : (isMobile ? 0.6 : 0.8);

    if(player.kart) {
        if(input.r) player.dx += 1.5; else if(input.l) player.dx -= 1.5; else player.dx *= 0.9;
        if(player.dx > 12) player.dx = 12; if(player.dx < -12) player.dx = -12;
    } else {
        if(input.r) player.dx += PHYSICS.acc; else if(input.l) player.dx -= PHYSICS.acc; else player.dx *= friction;
        if(player.dx > PHYSICS.spd) player.dx = PHYSICS.spd; if(player.dx < -PHYSICS.spd) player.dx = -PHYSICS.spd;
    }
    
    if(input.j && !input.jLock) {
        if(player.ground) { player.dy = PHYSICS.jump; player.jumps=1; input.jLock=true; playTone(330,'square',0.1); }
        else if(player.jumps > 0 && player.jumps < (player.kart?999:3)) { player.dy = PHYSICS.jump*0.9; player.jumps++; input.jLock=true; playTone(330,'square',0.1); }
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

    // --- BOSS LOGIC ---
    if(boss && !boss.dead) {
        // UI Update
        document.getElementById('boss-ui').style.display = 'block';
        document.getElementById('boss-hp').style.width = (boss.hp / boss.maxHp * 100) + '%';
        
        // Physics
        if(boss.x < player.x + 800) { // Activate when close
            boss.x += boss.dx;
            boss.dy += PHYSICS.grav;
            boss.y += boss.dy;
            
            // Patrol & Ground collision
            if(boss.y > canvas.height - 180) { boss.y = canvas.height - 180; boss.dy = 0; }
            
            // Simple AI
            if(boss.x < camX) boss.dx = Math.abs(boss.dx); // Keep in arena
            if(boss.x > goal.x - 100) boss.dx = -Math.abs(boss.dx);
            
            // Charge at player
            if(frames % 120 === 0) { 
                boss.dy = -10; // Jump
                boss.dx = (player.x < boss.x) ? -5 : 5; // Fast charge
            }
            
            if(boss.iframes > 0) boss.iframes--;

            // Collision with Player
            if(colCheck(player, boss)) {
                if(player.kart) {
                    boss.hp = 0; boss.dead = true; score += 5000;
                    spawnExplosion(boss.x + boss.w/2, boss.y + boss.h/2);
                    playTone(100, 'noise', 0.5);
                }
                else if(player.dy > 0 && player.y + player.h < boss.y + boss.h * 0.6) {
                    // Hit boss head
                    if(boss.iframes <= 0) {
                        boss.hp--;
                        boss.iframes = 60;
                        player.dy = -10; // Bounce
                        playTone(150, 'square', 0.3);
                        spawnExplosion(boss.x + boss.w/2, boss.y);
                        
                        if(boss.hp <= 0) {
                            boss.dead = true; score += 3000;
                            playTone(50, 'noise', 0.8);
                        } else {
                            // Enrage
                            boss.dx *= 1.5; 
                        }
                    }
                } else {
                    // Hurt player
                    if(player.invul <= 0) {
                        if(player.big) { 
                            player.big=false; player.w=32; player.h=40; 
                            player.invul = 60; playTone(100,'sawtooth',0.5); 
                        }
                        else gameOver();
                    }
                }
            }
        }
    } else {
         document.getElementById('boss-ui').style.display = 'none';
    }

    // Items
    items.forEach((it, i) => {
        if(it.type === 0) { 
            // Static coins or physics coins
            if(it.state !== 'static') { it.y += it.dy; if(it.dy<0) { it.y+=it.dy; it.dy+=0.5; } }
        }
        else {
            if(it.state==='spawning') { it.y+=it.dy; if(it.dy<0) it.dy+=0.5; if(it.dy>=0) it.state='moving'; }
            else {
                it.dy+=0.5; it.x+=it.dx; it.y+=it.dy;
                blocks.forEach(b => { if(colCheck(it, b)) { if(it.dy>0 && it.y<b.y+20) { it.y=b.y-it.h; it.dy=0; } else if(it.x<b.x+b.w && it.x+it.w>b.x) it.dx*=-1; } });
            }
        }
        if(colCheck(player, it)) {
            items.splice(i,1); 
            if(it.type===0) { score+=100; playTone(800,'sine',0.1); }
            else if(it.type===1) { player.big=true; player.w=40; player.h=56; playTone(200,'square',0.3); }
            else if(it.type===2) { player.kart=true; player.timer=600; player.w=48; player.h=24; playTone(100,'sawtooth',0.5); }
        }
    });

    // Enemies
    enemies.forEach(e => {
        if(e.dead) return;
        e.timer++;
        if(e.type === 1) { e.x += e.dx; e.y = e.anchorY + Math.sin(frames * 0.05) * 60; } 
        else if(e.type === 2) { let cycle = e.timer % 200; if(cycle < 100 && e.y > e.anchorY - 40) e.y -= 1; if(cycle >= 100 && e.y < e.anchorY) e.y += 1; }
        else if(e.type === 3) { e.x += e.dx; e.dy += PHYSICS.grav; e.y += e.dy; if(e.y >= e.anchorY) { e.y = e.anchorY; e.dy = 0; } if(Math.random() < 0.02 && e.dy === 0) e.dy = -10; }
        else { e.x += e.dx; if(frames%60==0 && Math.random()<0.3) e.dx *= -1; }

        if(colCheck(player, e)) {
            if(player.kart) { e.dead=true; score+=500; playTone(100,'noise',0.2); spawnExplosion(e.x,e.y); }
            else if(e.type !== 2 && player.dy > 0 && player.y+player.h < e.y+e.h*0.8) { e.dead=true; player.dy=-8; score+=200; playTone(600,'noise',0.1); spawnExplosion(e.x,e.y); } 
            else { if(player.big) { player.big=false; player.w=32; player.h=40; player.dy=-5; player.invul=60; playTone(150,'sawtooth',0.3); } else if(player.invul<=0) gameOver(); }
        }
    });
    
    // Pipe Entry
    if(goal && player.ground) {
        if(boss && !boss.dead) { /* Block exit if boss alive? No, let them run if they can! (Optional design, currently allowed) */ }
        if(Math.abs(player.y-(goal.y-player.h))<10 && player.x>goal.x && player.x<goal.x+goal.w) {
             if(Math.abs(player.dx)<2) { player.inPipe=true; playTone(100,'sawtooth',0.8); }
        }
    }

    draw();
    requestAnimationFrame(update);
}

function spawnExplosion(x, y) {
    for(let i=0;i<10;i++) particles.push({x:x,y:y,dx:(Math.random()-0.5)*10,dy:(Math.random()-0.5)*10,life:20,c:'#fff'});
}

function colCheck(a, b) { return a.x<b.x+b.w && a.x+a.w>b.x && a.y<b.y+b.h && a.y+a.h>b.y; }

function gameOver() {
    running = false;
    document.getElementById('menu').style.display='flex';
    document.getElementById('menu-title').innerText="GAME OVER";
    document.getElementById('boss-ui').style.display = 'none';
    document.getElementById('btn-retry').style.display='block';
    document.getElementById('btn-start').innerText="MAIN MENU";
}

function resetGame() { initAudio(); level=0; score=0; document.getElementById('btn-retry').style.display='none'; document.getElementById('btn-start').innerText="START GAME"; startGame(); }
function retryLevel() { initAudio(); startGame(); }
function startGame() { document.getElementById('menu').style.display='none'; player.big=false; player.kart=false; initLevel(level); running=true; update(); }

function draw() {
    let t = BIOMES[level % BIOMES.length];
    ctx.fillStyle = t.bg; ctx.fillRect(0,0,canvas.width,canvas.height);
    document.getElementById('world-ui').innerText = "WORLD 1-" + (level+1);

    blocks.forEach(b => {
        if(b.x > camX+canvas.width || b.x+b.w < camX) return;
        ctx.fillStyle = b.c; ctx.fillRect(b.x-camX, b.y, b.w, b.h);
        if(b.type==='brick' && b.content) { ctx.fillStyle="#000"; ctx.font="30px monospace"; ctx.fillText("?", b.x-camX+20, b.y+40); }
    });

    items.forEach(it => {
        if(it.x > camX+canvas.width) return;
        let ix = it.x-camX;
        if(it.type===0) { ctx.fillStyle="#FFD700"; ctx.beginPath(); ctx.arc(ix+15,it.y+15,12,0,6.28); ctx.fill(); ctx.fillStyle="#FFF"; ctx.fillText("$",ix+10,it.y+22); }
        else if(it.type===1) { ctx.fillStyle="#E53935"; ctx.fillRect(ix,it.y,it.w,it.h); }
        else if(it.type===2) { ctx.fillStyle="#2979FF"; ctx.fillRect(ix,it.y,it.w,it.h); }
    });

    if(goal) { ctx.fillStyle=t.pipe; ctx.fillRect(goal.x-camX-5, goal.y, goal.w+10, 30); ctx.fillStyle="#fff"; ctx.fillText("GOAL", goal.x-camX+15, goal.y+60); }

    // DRAW BOSS
    if(boss && !boss.dead) {
        let bx = boss.x - camX;
        if(boss.iframes % 4 < 2) {
            ctx.fillStyle = (boss.hp===1) ? "#D50000" : "#B71C1C"; // Low HP = Brighter Red
            ctx.fillRect(bx, boss.y, boss.w, boss.h);
            // Spikes
            ctx.fillStyle = "#fff"; 
            ctx.beginPath(); ctx.moveTo(bx, boss.y); ctx.lineTo(bx+20, boss.y-20); ctx.lineTo(bx+40, boss.y); ctx.fill();
            ctx.beginPath(); ctx.moveTo(bx+40, boss.y); ctx.lineTo(bx+60, boss.y-20); ctx.lineTo(bx+80, boss.y); ctx.fill();
            // Eyes
            ctx.fillStyle = "#000"; ctx.fillRect(bx+10, boss.y+30, 20, 10); ctx.fillRect(bx+50, boss.y+30, 20, 10);
            ctx.fillStyle = "#FF0"; ctx.fillRect(bx+15, boss.y+32, 5, 5); ctx.fillRect(bx+55, boss.y+32, 5, 5);
        }
    }

    enemies.forEach(e => {
        if(e.dead || e.x > camX+canvas.width) return;
        let ex = e.x - camX;
        if(e.type === 1) { ctx.fillStyle = "#7E57C2"; ctx.beginPath(); ctx.moveTo(ex, e.y); ctx.lineTo(ex+e.w/2, e.y+e.h); ctx.lineTo(ex+e.w, e.y); ctx.fill(); }
        else if(e.type === 2) { ctx.fillStyle = "#2E7D32"; ctx.fillRect(ex+10, e.y+20, 20, 20); ctx.fillStyle = "#D32F2F"; ctx.beginPath(); ctx.arc(ex+20, e.y+10, 15, 0, Math.PI*2); ctx.fill(); }
        else if(e.type === 3) { ctx.fillStyle = "#00BFA5"; ctx.fillRect(ex, e.y+10, e.w, e.h-10); }
        else { ctx.fillStyle = "#E53935"; ctx.fillRect(ex, e.y+5, e.w, e.h-5); ctx.fillStyle = "#FFCCBC"; ctx.fillRect(ex+5, e.y+15, e.w-10, 10); }
    });
    
    particles.forEach((p, i) => {
        p.x += p.dx; p.y += p.dy; p.life--;
        ctx.fillStyle = p.c; ctx.fillRect(p.x-camX, p.y, 5, 5);
        if(p.life<=0) particles.splice(i, 1);
    });

    if(!player.dead) {
        if(player.invul % 4 < 2) {
            let px = player.x-camX; let py = player.y;
            if(player.kart) {
                ctx.fillStyle=frames%4<2?"#2979FF":"#00E5FF"; ctx.fillRect(px,py+10,player.w,14);
                ctx.fillStyle="#000"; ctx.fillRect(px+5,py+24,10,10); ctx.fillRect(px+30,py+24,10,10);
            } else {
                let hatC=player.big?"#C62828":"#D32F2F"; let suitC=player.big?"#1565C0":"#1976D2";
                ctx.fillStyle=hatC; ctx.fillRect(px,py,player.w,player.h*0.3); ctx.fillRect(px-4,py+player.h*0.2,player.w+8,player.h*0.1);
                ctx.fillStyle="#FFCCBC"; ctx.fillRect(px+4,py+player.h*0.3,player.w-8,player.h*0.3);
                ctx.fillStyle=suitC; ctx.fillRect(px+4,py+player.h*0.6,player.w-8,player.h*0.35);
            }
        }
    }

    document.getElementById('score-ui').innerText="SCORE: "+score;
    let modeText=document.getElementById('power-ui');
    if(player.kart) { modeText.style.display='block'; modeText.innerText="KART MODE! "+Math.ceil(player.timer/60); }
    else modeText.style.display='none';
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
