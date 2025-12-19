import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Super AI Kart: V29 Art Restore",
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
    body { background: #000; overflow: hidden; font-family: 'Arial', sans-serif; }
    canvas { display: block; width: 100%; height: 100%; }

    /* UI文字 */
    .hud { position: absolute; top: 20px; color: #fff; font-size: 20px; font-weight: 900; text-shadow: 3px 3px 0 #000; z-index: 10; pointer-events: none; font-family: monospace; }
    #score-ui { left: 20px; }
    #world-ui { right: 20px; color: #FFD700; }

    /* 触屏按键 */
    #controls { display: none; position: absolute; bottom: 0; width: 100%; height: 100%; pointer-events: none; z-index: 20; }
    .btn {
        position: absolute; bottom: 30px; width: 85px; height: 85px;
        background: rgba(255,255,255,0.15); border: 3px solid rgba(255,255,255,0.7);
        border-radius: 50%; pointer-events: auto; backdrop-filter: blur(4px);
        display: flex; align-items: center; justify-content: center;
        color: white; font-size: 32px;
        transition: transform 0.1s;
    }
    .btn:active { background: rgba(255,255,255,0.4); transform: scale(0.9); }
    #btn-L { left: 20px; }
    #btn-R { left: 130px; }
    #btn-J { right: 30px; width: 95px; height: 95px; background: rgba(255,50,50,0.25); border-color: #ff8a80; }

    /* 菜单 */
    #menu {
        position: absolute; top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(0,0,0,0.92); z-index: 100;
        display: flex; flex-direction: column; align-items: center; justify-content: center;
    }
    .start-btn {
        padding: 15px 50px; font-size: 28px; background: #FF9800; color: white;
        border: 4px solid #FFF3E0; border-radius: 12px; cursor: pointer;
        box-shadow: 0 8px 0 #E65100; font-weight: bold; font-family: monospace;
        text-transform: uppercase;
    }
    .start-btn:active { transform: translateY(8px); box-shadow: 0 0 0; }
    
    /* 旋转提示 */
    #rotate-hint {
        display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        background: #000; color: #fff; z-index: 200;
        align-items: center; justify-content: center; text-align: center;
    }
</style>
</head>
<body>

<div id="rotate-hint">
    <div style="font-size:50px;">📱➡️</div>
    <h1>请旋转手机 / Rotate</h1>
</div>

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
        <h1 style="color:#fff; font-size: 40px; margin-bottom:10px; text-shadow:4px 4px 0 #D84315;">SUPER AI KART</h1>
        <h3 style="color:#FFCC80; margin-bottom:30px;">V29: Art Restore & Control Fix</h3>
        <button class="start-btn" onclick="startGame()">START GAME</button>
    </div>
</div>

<script>
const canvas = document.getElementById('c');
const ctx = canvas.getContext('2d');
const isMobile = /Android|iPhone|iPad|iPod/i.test(navigator.userAgent);

// --- 1. 物理参数 (针对性微调) ---
const PHYSICS = isMobile ? 
    // 手机: 极强摩擦(0.6)，极低加速度(0.15)，方便微操
    { spd: 3.0, acc: 0.15, fric: 0.60, jump: -10, grav: 0.6 } : 
    // PC: 恢复爽快感
    { spd: 7.5, acc: 0.80, fric: 0.82, jump: -13, grav: 0.65 };

let running = false;
let frames = 0;
let score = 0;
let level = 0;
let audioCtx = null;
let player = { x:100, y:0, w:32, h:44, dx:0, dy:0, ground:false, jumps:0, dead:false, inPipe:false };
let input = { l:false, r:false, j:false, jLock:false };
let camX = 0;
let blocks = [];
let enemies = [];
let particles = [];
let goal = null;

const THEMES = [
    { name: "PLAINS", bg: "#5C94FC", ground: "#C84C0C", brick: "#FFB74D", pipe:"#43A047" },
    { name: "DESERT", bg: "#F4C430", ground: "#E65100", brick: "#FFECB3", pipe:"#2E7D32" },
    { name: "CAVE",   bg: "#212121", ground: "#5D4037", brick: "#8D6E63", pipe:"#66BB6A" },
];

// --- 音频 ---
function initAudio() {
    if(!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    if(audioCtx.state === 'suspended') audioCtx.resume();
}
function playTone(f, t, d) {
    if(!audioCtx) return;
    const o = audioCtx.createOscillator(); const g = audioCtx.createGain();
    o.type=t; o.frequency.value=f; g.gain.setValueAtTime(0.05, audioCtx.currentTime);
    g.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime+d);
    o.connect(g); g.connect(audioCtx.destination); o.start(); o.stop(audioCtx.currentTime+d);
}

// --- 关卡 ---
function initLevel(l) {
    blocks = []; enemies = []; particles = [];
    let t = THEMES[l%THEMES.length];
    
    // 地面
    blocks.push({x:-500, y:canvas.height-80, w:1000, h:200, c:t.ground});
    
    let x = 500;
    while(x < 3000 + l*500) {
        if(Math.random()<0.15) x += 160; // 沟壑
        let w = 200 + Math.random()*400;
        blocks.push({x:x, y:canvas.height-80, w:w, h:200, c:t.ground});
        
        // 装饰/砖块
        if(Math.random()<0.5) {
            let bh = 150 + Math.random()*100;
            blocks.push({x:x+50, y:canvas.height-bh, w:40, h:40, c:t.brick});
            if(w>300) blocks.push({x:x+100, y:canvas.height-bh, w:40, h:40, c:t.brick});
        }
        
        // 怪物 (高密度)
        if(w > 250) {
            enemies.push({x:x+w/2, y:canvas.height-120, w:32, h:32, dx:-1, type:l%3, dead:false});
        }
        x += w;
    }
    
    // 终点
    blocks.push({x:x, y:canvas.height-80, w:500, h:200, c:t.ground});
    goal = {x:x+200, y:canvas.height-180, w:70, h:100, cx:x+235};
    
    player.x = 100; player.y=0; player.dx=0; player.dy=0; player.dead=false; player.inPipe=false;
    camX = 0;
}

function update() {
    if(!running) return;
    frames++;
    
    if(player.inPipe) {
        player.x += (goal.cx - player.x - player.w/2)*0.1;
        player.y += 2;
        if(player.y > canvas.height) { level++; initLevel(level); }
    } else {
        // 物理
        if(input.r) player.dx += PHYSICS.acc;
        else if(input.l) player.dx -= PHYSICS.acc;
        else player.dx *= PHYSICS.fric; // 强摩擦
        
        // 极速限制
        if(player.dx > PHYSICS.spd) player.dx = PHYSICS.spd;
        if(player.dx < -PHYSICS.spd) player.dx = -PHYSICS.spd;
        
        // 跳跃
        if(input.j && !input.jLock) {
            if(player.ground) { player.dy = PHYSICS.jump; player.jumps=1; input.jLock=true; playTone(300,'square',0.1); }
            else if(player.jumps>0 && player.jumps<2) { player.dy = PHYSICS.jump*0.9; player.jumps++; input.jLock=true; playTone(450,'square',0.1); }
        }
        if(!input.j) input.jLock=false;
        
        player.dy += PHYSICS.grav;
        player.x += player.dx;
        player.y += player.dy;
        
        // 死亡判定
        if(player.y > canvas.height+200) gameOver();
        
        // 碰撞
        player.ground = false;
        blocks.forEach(b => {
            if(colCheck(player,b)) {
                let pBot = player.y+player.h;
                if(player.dy>=0 && pBot-player.dy <= b.y+15) {
                    player.y = b.y-player.h; player.dy=0; player.ground=true; player.jumps=0;
                } else if(player.dy<0 && player.y-player.dy >= b.y+b.h-15) {
                    player.y = b.y+b.h; player.dy=0;
                } else if(player.dx>0) { player.x = b.x-player.w; player.dx=0; }
                else if(player.dx<0) { player.x = b.x+b.w; player.dx=0; }
            }
        });
        
        // 终点
        if(goal && colCheck(player, {x:goal.x, y:goal.y-10, w:goal.w, h:10})) {
            if(player.ground && Math.abs(player.dx)<1) { player.inPipe=true; playTone(100,'sawtooth',0.5); }
        }
        else if(goal && colCheck(player, goal)) { // 撞管壁
           if(player.dx>0) player.x = goal.x-player.w;
        }

        // 怪物
        enemies.forEach(e => {
            if(e.dead) return;
            e.x += e.dx;
            if(frames%100==0) e.dx *= -1;
            if(colCheck(player, e)) {
                if(player.dy>0 && player.y+player.h < e.y+e.h*0.8) {
                    e.dead = true; player.dy = -8; score+=100; playTone(600,'sine',0.1);
                    for(let i=0;i<8;i++) particles.push({x:e.x+16,y:e.y+16,dx:(Math.random()-0.5)*8,dy:(Math.random()-0.5)*8,life:20,c:"#fff"});
                } else {
                    gameOver();
                }
            }
        });
    }

    // 摄像机平滑跟随 (防止PC端玩家消失)
    let targetCam = player.x - canvas.width * 0.3;
    if(targetCam < 0) targetCam = 0; 
    camX += (targetCam - camX) * 0.1;
    
    draw();
    requestAnimationFrame(update);
}

function colCheck(a,b) { return a.x < b.x+b.w && a.x+a.w > b.x && a.y < b.y+b.h && a.y+a.h > b.y; }
function gameOver() { running=false; document.getElementById('menu').style.display='flex'; document.querySelector('#menu h1').innerText="GAME OVER"; }

// --- 2. 绘图 (美术复兴) ---
function draw() {
    let theme = THEMES[level % THEMES.length];
    ctx.fillStyle = theme.bg;
    ctx.fillRect(0,0,canvas.width,canvas.height); // 清屏
    
    // 砖块/地面
    blocks.forEach(b => {
        if(b.x > camX+canvas.width || b.x+b.w < camX) return;
        ctx.fillStyle = b.c;
        ctx.fillRect(b.x-camX, b.y, b.w, b.h);
        // 简单的砖块纹理
        ctx.lineWidth = 2; ctx.strokeStyle = "rgba(0,0,0,0.1)";
        ctx.strokeRect(b.x-camX, b.y, b.w, b.h);
    });

    // 终点
    if(goal) {
        let gx = goal.x - camX;
        ctx.fillStyle = theme.pipe;
        ctx.fillRect(gx, goal.y, goal.w, goal.h);
        ctx.fillRect(gx-5, goal.y, goal.w+10, 30); // 管口
        ctx.fillStyle = "#fff"; ctx.font="bold 16px Arial"; ctx.fillText("GOAL", gx+12, goal.y+70);
    }

    // 怪物 (画成蘑菇)
    enemies.forEach(e => {
        if(e.dead || e.x > camX+canvas.width) return;
        let ex = e.x - camX;
        
        // 蘑菇头 (半圆)
        ctx.fillStyle = ["#E53935", "#8E24AA", "#43A047"][e.type];
        ctx.beginPath();
        ctx.arc(ex+e.w/2, e.y+10, e.w/2, Math.PI, 0); // 上半圆
        ctx.fill();
        
        // 蘑菇柄
        ctx.fillStyle = "#FFCCBC";
        ctx.fillRect(ex+6, e.y+10, e.w-12, e.h-10);
        
        // 眼睛
        ctx.fillStyle = "#000";
        let eyeOff = (e.dx<0) ? -4 : 4;
        ctx.fillRect(ex+e.w/2-6+eyeOff, e.y+15, 4, 8);
        ctx.fillRect(ex+e.w/2+2+eyeOff, e.y+15, 4, 8);
        
        // 走路的小脚
        if(Math.floor(frames/10)%2==0) {
             ctx.fillStyle = "#000";
             ctx.fillRect(ex, e.y+e.h-5, 10, 5);
             ctx.fillRect(ex+e.w-10, e.y+e.h-5, 10, 5);
        }
    });

    // 粒子
    particles.forEach((p,i) => {
        p.x+=p.dx; p.y+=p.dy; p.life--;
        ctx.fillStyle = p.c; ctx.fillRect(p.x-camX, p.y, 6, 6);
        if(p.life<=0) particles.splice(i,1);
    });

    // 玩家 (画成立体小人)
    if(!player.dead) {
        let px = player.x - camX;
        let py = player.y;
        let w = player.w;
        let h = player.h;
        let facing = (player.dx > 0) ? 1 : (player.dx < 0 ? -1 : 1);
        
        // 1. 帽子 (Brown Hat)
        ctx.fillStyle = "#D84315";
        ctx.fillRect(px, py, w, 10); // 帽顶
        ctx.fillRect(px-(facing==1?0:4), py+8, w+4, 4); // 帽檐
        
        // 2. 脸 (Face)
        ctx.fillStyle = "#FFCCBC";
        ctx.fillRect(px+4, py+10, w-8, 12);
        // 眼睛/胡子
        ctx.fillStyle = "#000"; 
        if(facing==1) ctx.fillRect(px+w-10, py+14, 4, 4);
        else ctx.fillRect(px+6, py+14, 4, 4);
        
        // 3. 衣服 (Blue Overalls)
        ctx.fillStyle = "#1565C0";
        ctx.fillRect(px+2, py+22, w-4, 14);
        // 扣子
        ctx.fillStyle = "#FFD54F";
        ctx.fillRect(px+6, py+24, 4, 4);
        ctx.fillRect(px+w-10, py+24, 4, 4);
        
        // 4. 脚 (Shoes) - 跑步动画
        ctx.fillStyle = "#3E2723";
        let legOff = 0;
        if(Math.abs(player.dx)>0.1 && player.ground) legOff = Math.sin(frames*0.8)*6;
        
        // 左脚 & 右脚
        ctx.fillRect(px+4+legOff, py+h-8, 10, 8); 
        ctx.fillRect(px+w-14-legOff, py+h-8, 10, 8);
    }
    
    // UI HUD
    document.getElementById('score-ui').innerText = "SCORE: " + score;
    document.getElementById('world-ui').innerText = "WORLD 1-" + (level+1);
}

// --- 启动 & 适配 ---
function startGame() {
    initAudio();
    document.getElementById('menu').style.display='none';
    level=0; score=0; initLevel(0);
    running=true;
    checkOrient();
    update();
}

function checkOrient() {
    // 仅针对手机竖屏进行阻断
    if(isMobile && window.innerHeight > window.innerWidth) {
        document.getElementById('rotate-hint').style.display = 'flex';
        running = false;
    } else {
        document.getElementById('rotate-hint').style.display = 'none';
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
        if(!running && frames>10 && !player.dead) running = true;
    }
}
window.addEventListener('resize', checkOrient);
setInterval(checkOrient, 1000);

if(isMobile) {
    document.getElementById('controls').style.display='block';
    const b = (id,k) => {
        let el = document.getElementById(id);
        el.addEventListener('touchstart',e=>{e.preventDefault(); input[k]=true;});
        el.addEventListener('touchend',e=>{e.preventDefault(); input[k]=false;});
    };
    b('btn-L','l'); b('btn-R','r'); b('btn-J','j');
}

window.addEventListener('keydown', e=>{
    if(e.key=='a'||e.key=='ArrowLeft') input.l=true;
    if(e.key=='d'||e.key=='ArrowRight') input.r=true;
    if(e.key=='w'||e.key==' ') input.j=true;
});
window.addEventListener('keyup', e=>{
    if(e.key=='a'||e.key=='ArrowLeft') input.l=false;
    if(e.key=='d'||e.key=='ArrowRight') input.r=false;
    if(e.key=='w'||e.key==' ') input.j=false;
});

</script>
</body>
</html>
"""

st.components.v1.html(game_html, height=800)
