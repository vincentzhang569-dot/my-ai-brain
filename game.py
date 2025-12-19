import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Super AI Kart: V32 Power-Up",
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
    <div id="power-ui" class="hud">MODE: NORMAL</div>
    <div id="world-ui" class="hud">WORLD 1-1</div>
    
    <div id="controls">
        <div class="btn" id="btn-L">◀</div>
        <div class="btn" id="btn-R">▶</div>
        <div class="btn" id="btn-J">🚀</div>
    </div>

    <div id="menu">
        <h1 style="color:#fff; margin-bottom:20px; text-shadow:4px 4px 0 #f00;">SUPER AI KART</h1>
        <p style="color:#ccc; margin-bottom:30px;">V32: Kart Rampage & Items</p>
        <button class="start-btn" onclick="startGame()">START GAME</button>
    </div>
</div>

<script>
const canvas = document.getElementById('c');
const ctx = canvas.getContext('2d', { alpha: false });
const isMobile = /Android|iPhone|iPad|iPod/i.test(navigator.userAgent);

// 物理参数：保持 V31 的手感，PC快，手机慢
const PHYSICS = isMobile ? 
    { spd: 2.2, acc: 0.1, fric: 0.60, jump: -11, grav: 0.55 } : 
    { spd: 7.0, acc: 0.8, fric: 0.80, jump: -12, grav: 0.60 };

let running = false;
let frames = 0;
let score = 0;
let level = 0;
let audioCtx = null;
let bgmTimer = null;

// 玩家状态新增：big(变大), kart(赛车模式), timer(变身时间)
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
let items = []; // 新增道具列表
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
    // 赛车模式 BGM 变快
    let base = player.kart ? 440 : (220 + (level*20));
    let speed = player.kart ? 100 : 200;
    
    [0, 1, 2, 3, 4, 5, 6, 7].forEach((i) => {
        setTimeout(() => { 
            if(running) playTone((i%2==0)?base:base*1.5, 'triangle', 0.1, 0.05); 
        }, i * speed);
    });
}

function initLevel(lvl) {
    blocks = []; enemies = []; particles = []; items = [];
    let t = THEMES[lvl % THEMES.length];
    
    // 1. 玩家重置 (修复“压扁”BUG的核心)
    player.x = 100; player.y = 0; player.dx=0; player.dy=0;
    // 强制恢复尺寸
    player.w = player.big ? 40 : 32; 
    player.h = player.big ? 56 : 40; 
    player.inPipe = false; player.dead = false;
    // 只有 kart 模式是有时限的，切关时如果不满就不继承了，或者你可以选择继承
    // 这里为了安全起见，切关保留 big，重置 kart (或者你喜欢保留也可以)
    // 让我们保留状态，更爽一点
    
    camX = 0;

    blocks.push({x:-200, y:canvas.height-80, w:800, h:100, c: t.ground}); // 起点
    
    let x = 600;
    while(x < 3000 + lvl * 500) {
        // 沟壑 (kart 模式不怕沟壑)
        if(Math.random() < 0.2) x += 150; 
        
        let w = 400 + Math.random() * 400;
        blocks.push({x:x, y:canvas.height-80, w:w, h:100, c: t.ground});
        
        // 怪物：现在每一关随机混合 3 种怪物
        if(w > 300) {
            let ex = x + 100 + Math.random()*(w-200);
            // 随机种类 0, 1, 2
            let eType = Math.floor(Math.random() * 3); 
            enemies.push({x:ex, y:canvas.height-120, w:36, h:36, dx:-1.5, type:eType, dead:false});
        }
        
        // 砖块与道具 (概率提高)
        if(Math.random() < 0.7) { // 提高生成率
            let bx = x+50;
            let bw = 100;
            let by = canvas.height-220;
            blocks.push({x:bx, y:by, w:bw, h:30, c: t.brick});
            
            // 砖块上方生成道具
            let rand = Math.random();
            if(rand < 0.5) {
                // 金币 (50%)
                items.push({x:bx+20, y:by-30, w:20, h:20, type:0, dy:0}); 
            } else if (rand < 0.6) {
                // 变大蘑菇 (10%)
                items.push({x:bx+60, y:by-35, w:30, h:30, type:1, dy:0});
            } else if (rand < 0.65) {
                // 赛车蘑菇 (5% 稀有)
                items.push({x:bx+60, y:by-35, w:30, h:30, type:2, dy:0});
            }
        }
        
        // 额外的跳跃平台
        if(Math.random() < 0.3) {
            blocks.push({x:x+200, y:canvas.height-320, w:80, h:30, c: t.brick});
        }
        
        x += w;
    }
    
    // 终点
    blocks.push({x:x, y:canvas.height-80, w:500, h:100, c: t.ground});
    goal = { x: x + 200, y: canvas.height - 150, w: 70, h: 150, cx: x+235 };
    blocks.push({ x: goal.x, y: goal.y, w: goal.w, h: goal.h, c: t.pipe });
}

function update() {
    if(!running) return;
    frames++;

    // 状态计时器
    if(player.kart) {
        player.timer--;
        if(player.timer <= 0) {
            player.kart = false;
            player.w = player.big ? 40 : 32;
            playTone(150, 'sawtooth', 0.5); // 变回来音效
        }
    }

    // 钻管
    if(player.inPipe) {
        player.x += (goal.cx - player.x - player.w/2) * 0.2;
        player.y += 3;
        if(player.w > 0) player.w -= 0.5; // 注意：这里变小了，下一关必须重置！
        if(player.y > canvas.height) { level++; initLevel(level); }
        draw();
        requestAnimationFrame(update);
        return;
    }

    // 物理逻辑
    // 如果是赛车模式，强制最大速度
    if(player.kart) {
        player.dx = 8; // 极速
        if(input.l) player.dx = 4; // 可以减速但不能停
    } else {
        if(input.r) player.dx += PHYSICS.acc;
        else if(input.l) player.dx -= PHYSICS.acc;
        else player.dx *= PHYSICS.fric;
        
        if(player.dx > PHYSICS.spd) player.dx = PHYSICS.spd;
        if(player.dx < -PHYSICS.spd) player.dx = -PHYSICS.spd;
    }
    
    // 跳跃
    if(input.j && !input.jLock) {
        let maxJumps = 3;
        // 赛车模式可以在空中无限跳(像飞行一样) 或者 普通三段跳
        if(player.kart) maxJumps = 999; 

        if(player.ground) {
            player.dy = PHYSICS.jump; player.jumps = 1; input.jLock = true;
            playTone(300, 'square', 0.1);
        } else if(player.jumps > 0 && player.jumps < maxJumps) { 
            player.dy = PHYSICS.jump * 0.9; player.jumps++; input.jLock = true;
            playTone(450 + player.jumps*100, 'square', 0.1);
            for(let i=0; i<6; i++) particles.push({x:player.x+player.w/2, y:player.y+player.h, dx:(Math.random()-0.5)*5, dy:Math.random()*5, life:20, c:'#fff'});
        }
    }
    if(!input.j) input.jLock = false;

    player.dy += PHYSICS.grav;
    player.x += player.dx;
    player.y += player.dy;
    
    // --- 赛车模式：防掉落保护 (反重力) ---
    if(player.kart && player.y > canvas.height - 100) {
        player.y = canvas.height - 100;
        player.dy = 0;
        player.ground = true; // 允许在空气上起跳
        // 产生悬浮粒子
        if(frames%5==0) particles.push({x:player.x, y:player.y+40, dx:-5, dy:0, life:10, c:'#00E676'});
    }

    // 摄像机
    camX += (player.x - canvas.width*0.3 - camX) * 0.1;
    if(camX < 0) camX = 0;

    // 死亡 (非 Kart 模式才死)
    if(player.y > canvas.height + 100 && !player.kart) gameOver();

    // 地形碰撞
    player.ground = false;
    blocks.forEach(b => {
        if(colCheck(player, b)) {
            if(player.dy >= 0 && player.y + player.h - player.dy <= b.y + 25) {
                player.y = b.y - player.h; player.dy = 0; player.ground = true; player.jumps = 0;
            } else if(player.dy < 0 && player.y - player.dy >= b.y + b.h - 10) {
                player.y = b.y + b.h; player.dy = 0;
            } else if(player.dx > 0) { player.x = b.x - player.w; player.dx = 0; }
            else if(player.dx < 0) { player.x = b.x + b.w; player.dx = 0; }
        }
    });

    // 道具碰撞
    items.forEach((it, i) => {
        if(colCheck(player, it)) {
            items.splice(i, 1); // 吃掉
            if(it.type === 0) { // 金币
                score += 100;
                playTone(800, 'sine', 0.1);
            } else if(it.type === 1) { // 红蘑菇
                score += 500;
                player.big = true;
                player.w = 40; player.h = 56; // 变大
                playTone(200, 'square', 0.3);
                playTone(300, 'square', 0.3);
            } else if(it.type === 2) { // 赛车蘑菇
                score += 1000;
                player.kart = true;
                player.timer = 600; // 10秒爽快时间
                player.w = 48; player.h = 24; // 变成车的扁平形状
                playTone(100, 'sawtooth', 0.5);
            }
        }
    });

    // 怪物逻辑
    enemies.forEach(e => {
        if(e.dead) return;
        e.x += e.dx;
        if(frames % 60 == 0 && Math.random() < 0.3) e.dx *= -1;
        
        if(colCheck(player, e)) {
            // 赛车模式：直接撞死怪物
            if(player.kart) {
                e.dead = true; score += 500;
                playTone(100, 'noise', 0.2); // 撞击声
                for(let i=0;i<10;i++) particles.push({x:e.x+18,y:e.y+18,dx:(Math.random()-0.5)*15,dy:(Math.random()-0.5)*15,life:30,c:'#fff'});
            }
            // 普通踩死
            else if(player.dy > 0 && player.y + player.h < e.y + e.h * 0.8) {
                e.dead = true; player.dy = -8; score += 200;
                playTone(600, 'noise', 0.1);
                for(let i=0;i<8;i++) particles.push({x:e.x+18,y:e.y+18,dx:(Math.random()-0.5)*8,dy:(Math.random()-0.5)*8,life:20,c:['#E53935','#43A047','#5E35B1'][e.type]});
            } 
            // 玩家受伤
            else {
                if(player.big) {
                    player.big = false; // 变小
                    player.w = 32; player.h = 40;
                    player.dy = -5; // 弹开
                    e.dx *= -1;
                    playTone(150, 'sawtooth', 0.3);
                } else {
                    gameOver();
                }
            }
        }
    });
    
    // 终点检测
    if(goal && player.ground) {
        if(Math.abs(player.y - (goal.y - player.h)) < 10 && player.x > goal.x && player.x < goal.x + goal.w) {
             if(Math.abs(player.dx) < 2) {
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
    
    // 画方块
    blocks.forEach(b => {
        if(b.x > camX+canvas.width || b.x+b.w < camX) return;
        ctx.fillStyle = b.c;
        ctx.fillRect(b.x-camX, b.y, b.w, b.h);
        ctx.fillStyle = "rgba(0,0,0,0.1)"; 
        ctx.fillRect(b.x-camX, b.y+b.h-5, b.w, 5); 
    });

    // 画道具
    items.forEach(it => {
        if(it.x > camX+canvas.width || it.x+it.w < camX) return;
        let ix = it.x - camX;
        if(it.type === 0) { // 金币
            ctx.fillStyle = "#FFD700";
            ctx.beginPath(); ctx.arc(ix+10, it.y+10, 8, 0, Math.PI*2); ctx.fill();
            ctx.fillStyle = "#FFF"; ctx.fillText("$", ix+6, it.y+14);
        } else if(it.type === 1) { // 蘑菇
            ctx.fillStyle = "#E53935"; ctx.fillRect(ix, it.y, it.w, it.h);
            ctx.fillStyle = "#fff"; ctx.fillRect(ix+5, it.y+5, 5, 5);
        } else if(it.type === 2) { // 赛车
            ctx.fillStyle = "#2979FF"; ctx.fillRect(ix, it.y, it.w, it.h);
            ctx.fillStyle = "#fff"; ctx.fillText("K", ix+8, it.y+20);
        }
    });

    // 画终点装饰
    if(goal) {
        let gx = goal.x - camX;
        ctx.fillStyle = t.pipe; 
        ctx.fillRect(gx-5, goal.y, goal.w+10, 30); 
        ctx.fillStyle = "#fff"; ctx.font = "bold 16px monospace";
        ctx.fillText("GOAL", gx+15, goal.y+60);
    }

    // 画怪物
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
    
    // 画粒子
    particles.forEach((p, i) => {
        p.x += p.dx; p.y += p.dy; p.life--;
        ctx.fillStyle = p.c;
        ctx.fillRect(p.x-camX, p.y, 5, 5);
        if(p.life<=0) particles.splice(i, 1);
    });

    // 画玩家
    if(!player.dead) {
        let px = player.x - camX;
        let py = player.y;
        
        if(player.kart) {
            // 赛车形态
            ctx.fillStyle = frames%4<2 ? "#2979FF" : "#00E5FF"; // 闪烁效果
            ctx.fillRect(px, py+10, player.w, 14); // 车身
            ctx.fillStyle = "#000";
            ctx.fillRect(px+5, py+24, 10, 10); // 轮子
            ctx.fillRect(px+30, py+24, 10, 10);
            ctx.fillStyle = "#fff";
            ctx.fillRect(px+player.w-5, py+12, 5, 5); // 车灯
            
        } else {
            // 普通/变大形态
            // 如果是 Big 模式，颜色稍微深一点表示强壮
            let hatC = player.big ? "#C62828" : "#D32F2F";
            let suitC = player.big ? "#1565C0" : "#1976D2";

            ctx.fillStyle = hatC;
            ctx.fillRect(px, py, player.w, player.h*0.3); // 帽
            ctx.fillRect(px-4, py+player.h*0.2, player.w+8, player.h*0.1); // 檐
            
            ctx.fillStyle = "#FFCCBC";
            ctx.fillRect(px+4, py+player.h*0.3, player.w-8, player.h*0.3); // 脸
            
            ctx.fillStyle = suitC;
            ctx.fillRect(px+4, py+player.h*0.6, player.w-8, player.h*0.35); // 身
            
            ctx.fillStyle = "#3E2723";
            ctx.fillRect(px+4, py+player.h*0.9, 8, player.h*0.1); // 腿
            ctx.fillRect(px+player.w-12, py+player.h*0.9, 8, player.h*0.1);
        }
    }

    // UI 更新
    document.getElementById('score-ui').innerText = "SCORE: " + score;
    document.getElementById('world-ui').innerText = "WORLD 1-" + (level+1);
    let modeText = document.getElementById('power-ui');
    if(player.kart) {
        modeText.style.display = 'block';
        modeText.innerText = "KART MODE! " + Math.ceil(player.timer/60);
        modeText.style.color = "#00E676";
    } else {
        modeText.style.display = 'none';
    }
}

function startGame() {
    initAudio();
    document.getElementById('menu').style.display = 'none';
    level = 0; score = 0;
    // 重置玩家状态
    player.big = false; player.kart = false;
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
