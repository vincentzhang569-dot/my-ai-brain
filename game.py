import streamlit as st
import streamlit.components.v1 as components
import base64
import os
import glob
import json

# --- 1. 页面配置 ---
st.set_page_config(
    page_title="Super AI Kart: Restoration",
    page_icon="🍄",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 隐藏多余UI，争取最大屏幕空间
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .block-container {padding-top: 0rem; padding-bottom: 0rem; padding-left: 0rem; padding-right: 0rem;}
    </style>
""", unsafe_allow_html=True)

# --- 2. 音频数据 (保持兼容) ---
def get_audio_data(folder_path="mp3"):
    playlist = []
    game_over_data = ""
    if os.path.exists(folder_path):
        all_files = glob.glob(os.path.join(folder_path, "*.mp3"))
        for file_path in all_files:
            filename = os.path.basename(file_path).lower()
            try:
                with open(file_path, "rb") as f:
                    b64 = base64.b64encode(f.read()).decode()
                    if "game_over.mp3" == filename: game_over_data = b64
                    else: playlist.append(b64)
            except: pass
    return json.dumps(playlist), game_over_data

playlist_json, game_over_b64 = get_audio_data("mp3")

# --- 3. 游戏核心 (V18内容 + V19音乐 + V20横屏) ---
game_template = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
<style>
    @import url('https://fonts.googleapis.com/css2?family=VT323&display=swap');
    
    body {
        margin: 0; background-color: #000; color: white;
        font-family: 'VT323', monospace;
        overflow: hidden; height: 100vh; width: 100vw;
        display: flex; align-items: center; justify-content: center;
        touch-action: none; -webkit-touch-callout: none; user-select: none;
    }

    /* 游戏容器 */
    #game-container {
        position: relative;
        width: 100%; height: 100%;
        display: flex; justify-content: center; align-items: center;
    }

    #game-wrapper {
        position: relative;
        width: 100%; height: 100%;
        background-color: #333; overflow: hidden;
        transition: all 0.5s ease; /* 旋转动画 */
    }

    /* 🔄 强制横屏模式 CSS */
    .force-landscape {
        width: 100vh !important;
        height: 100vw !important;
        transform: rotate(90deg);
        /* 旋转中心点需要微调，确保居中 */
        position: absolute;
        top: 50%; left: 50%;
        margin-left: -50vh; /* height的一半 */
        margin-top: -50vw;  /* width的一半 */
    }

    canvas { display: block; width: 100%; height: 100%; image-rendering: pixelated; }

    .ui-text { position: absolute; color: white; text-shadow: 2px 2px #000; z-index: 10; pointer-events: none; font-size: clamp(20px, 5vw, 32px); font-weight: bold; }
    #score-board { top: 10px; left: 10px; } 
    #coin-board { top: 10px; left: 50%; transform: translateX(-50%); color: #FFD700; } 
    #level-board { top: 10px; right: 10px; color: #00FF00; }

    #rotate-btn {
        position: absolute; top: 50px; left: 10px; z-index: 50;
        background: rgba(0,0,0,0.5); color: white; border: 1px solid white;
        padding: 5px 10px; font-family: 'VT323'; cursor: pointer; font-size: 16px;
        pointer-events: auto;
    }

    #overlay {
        position: absolute; top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(0,0,0,0.85);
        display: flex; flex-direction: column; align-items: center; justify-content: center; z-index: 20;
    }
    h1 { font-size: clamp(40px, 10vw, 90px); margin: 0; color: #FF4500; text-shadow: 4px 4px #000; letter-spacing: 5px; text-align: center; }
    
    .btn-container { display: flex; gap: 20px; margin-top: 20px; }
    button.pixel-btn {
        background: #00AA00; border: 4px solid #fff; color: white;
        font-family: 'VT323'; font-size: clamp(20px, 6vw, 36px);
        padding: 10px 30px; cursor: pointer; box-shadow: 0 6px 0 #005500; text-transform: uppercase;
    }
    button.pixel-btn:active { transform: translateY(6px); box-shadow: none; }
    button.red-btn { background: #CC0000; box-shadow: 0 6px 0 #660000; }
    button.blue-btn { background: #0066CC; box-shadow: 0 6px 0 #003366; }

    #controls {
        position: absolute; bottom: 20px; width: 100%; height: 120px;
        display: flex; justify-content: space-between; padding: 0 40px; box-sizing: border-box;
        z-index: 30; pointer-events: none;
    }
    .ctrl-group { display: flex; gap: 20px; pointer-events: auto; align-items: center; }
    .ctrl-btn {
        width: 80px; height: 80px;
        background: rgba(255, 255, 255, 0.15); border: 2px solid rgba(255, 255, 255, 0.4);
        border-radius: 12px; display: flex; align-items: center; justify-content: center;
        font-size: 30px; color: white; backdrop-filter: blur(4px); touch-action: none;
    }
    .ctrl-btn:active, .ctrl-btn.active { background: rgba(255, 255, 255, 0.4); transform: scale(0.95); }
    .btn-a { border-radius: 50%; width: 90px; height: 90px; background: rgba(255, 69, 0, 0.3); }
    .btn-a:active, .btn-a.active { background: rgba(255, 69, 0, 0.6); }

    @media (min-width: 1024px) { #controls, #rotate-btn { display: none; } }
</style>
</head>
<body>

<div id="game-container">
    <div id="game-wrapper">
        <div id="rotate-btn" onclick="toggleLandscape()">🔄 强制横屏</div>
        
        <div id="score-board" class="ui-text">SCORE: <span id="score-val">0</span></div>
        <div id="coin-board" class="ui-text">💰 <span id="coin-val">0</span></div>
        <div id="level-board" class="ui-text">WORLD <span id="level-val">1-1</span></div>
        
        <div id="overlay">
            <h1 id="title-text">SUPER AI<br>KART</h1>
            <p id="sub-text" style="color:#aaa;font-size:18px;margin-top:10px;">Music by AI 🎵</p>
            <div id="start-btn-group" class="btn-container"><button class="pixel-btn" onclick="tryStartGame()">START</button></div>
            <div id="retry-btn-group" class="btn-container" style="display:none;">
                <button class="pixel-btn blue-btn" onclick="retryLevel()">Retry</button>
                <button class="pixel-btn red-btn" onclick="tryStartGame()">Reset</button>
            </div>
        </div>
        
        <canvas id="gameCanvas"></canvas>
        
        <div id="controls">
            <div class="ctrl-group">
                <div class="ctrl-btn" id="btn-left">◀</div>
                <div class="ctrl-btn" id="btn-right">▶</div>
            </div>
            <div class="ctrl-group">
                <div class="ctrl-btn btn-a" id="btn-jump">A</div>
            </div>
        </div>
    </div>
</div>

<script>
const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');
const wrapper = document.getElementById('game-wrapper');

// --- 🔄 横屏切换逻辑 ---
let isLandscape = false;
function toggleLandscape() {
    isLandscape = !isLandscape;
    if (isLandscape) {
        wrapper.classList.add('force-landscape');
    } else {
        wrapper.classList.remove('force-landscape');
    }
    // 延迟一点等待CSS动画，然后重绘
    setTimeout(resizeCanvas, 600);
}

function resizeCanvas() {
    // 无论是否旋转，都获取wrapper当前显示的像素尺寸
    const rect = wrapper.getBoundingClientRect();
    // 当 transform 生效时，rect 可能会很奇怪，直接取 offsetWidth/Height
    // 如果旋转了，width 和 height 在视觉上是反的，但 canvas 内部坐标系跟随 DOM 元素
    if (isLandscape) {
        // 强制设置分辨率匹配
        canvas.width = wrapper.offsetHeight; 
        canvas.height = wrapper.offsetWidth;
    } else {
        canvas.width = wrapper.clientWidth;
        canvas.height = wrapper.clientHeight;
    }
    if(!player.dead) drawGame();
}
window.addEventListener('resize', resizeCanvas);
setTimeout(resizeCanvas, 100);

// --- 🎵 AI 音乐 (V19 逻辑) ---
const MUSIC_THEMES = [
    { type: 'grass', bass: 'square', lead: 'triangle', scale: [261.6, 293.6, 329.6, 392.0, 440.0, 523.2], bpm: 150 },
    { type: 'dark', bass: 'sawtooth', lead: 'square', scale: [130.8, 146.8, 155.5, 196.0, 207.6, 261.6], bpm: 120 },
    { type: 'sky', bass: 'sine', lead: 'sawtooth', scale: [349.2, 440.0, 523.2, 587.3, 659.2, 698.4], bpm: 180 }
];
let audioCtx = null, musicInterval = null;

function startProceduralBGM(levelIndex) {
    if(musicInterval) clearInterval(musicInterval);
    if(!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    const theme = MUSIC_THEMES[(levelIndex - 1) % MUSIC_THEMES.length];
    const beatTime = 60 / theme.bpm; 
    let tick = 0;

    musicInterval = setInterval(() => {
        if(audioCtx.state === 'suspended') audioCtx.resume();
        const t = audioCtx.currentTime;
        if (tick % 2 === 0) {
            const osc = audioCtx.createOscillator(); const g = audioCtx.createGain();
            osc.type = theme.bass;
            const bassNote = (Math.random() > 0.5 ? theme.scale[0] : theme.scale[3]) / 2; 
            osc.frequency.setValueAtTime(bassNote, t);
            g.gain.setValueAtTime(0.1, t); g.gain.exponentialRampToValueAtTime(0.01, t + 0.3);
            osc.connect(g); g.connect(audioCtx.destination); osc.start(t); osc.stop(t + 0.3);
        }
        if (Math.random() > 0.2) {
            const osc = audioCtx.createOscillator(); const g = audioCtx.createGain();
            osc.type = theme.lead;
            let noteFreq = theme.scale[Math.floor(Math.random() * theme.scale.length)];
            if (Math.random() > 0.8) noteFreq *= 2;
            osc.frequency.setValueAtTime(noteFreq, t);
            g.gain.setValueAtTime(0.05, t); g.gain.exponentialRampToValueAtTime(0.001, t + 0.2);
            osc.connect(g); g.connect(audioCtx.destination); osc.start(t); osc.stop(t + 0.2);
        }
        tick++;
    }, beatTime * 1000);
}
function stopMusic() { if (musicInterval) { clearInterval(musicInterval); musicInterval = null; } }
function playMusic(type, level) {
    if (type === 'gameover') {
        stopMusic();
        if(!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        const t = audioCtx.currentTime;
        const o=audioCtx.createOscillator(); const g=audioCtx.createGain();
        o.type='sawtooth'; o.frequency.setValueAtTime(100, t); o.frequency.linearRampToValueAtTime(30, t+1);
        g.gain.setValueAtTime(0.2, t); g.gain.linearRampToValueAtTime(0, t+1);
        o.connect(g); g.connect(audioCtx.destination); o.start(t); o.stop(t+1);
    } else { startProceduralBGM(level); }
}
function playSound(type) {
    if(!audioCtx) return;
    const t = audioCtx.currentTime;
    const o = audioCtx.createOscillator(); const g = audioCtx.createGain();
    o.connect(g); g.connect(audioCtx.destination);
    if (type === 'jump') { o.type='square'; o.frequency.setValueAtTime(150+(player.jumpCount*100), t); o.frequency.linearRampToValueAtTime(300, t+0.1); g.gain.setValueAtTime(0.1, t); g.gain.linearRampToValueAtTime(0, t+0.1); }
    else if (type === 'coin') { o.type='sine'; o.frequency.setValueAtTime(1200, t); o.frequency.linearRampToValueAtTime(1600, t+0.1); g.gain.setValueAtTime(0.1, t); g.gain.linearRampToValueAtTime(0, t+0.2); }
    else if (type === 'powerup') { o.type='triangle'; o.frequency.setValueAtTime(300, t); o.frequency.linearRampToValueAtTime(600, t+0.3); g.gain.setValueAtTime(0.2, t); g.gain.linearRampToValueAtTime(0, t+0.3); }
    else if (type === 'stomp') { o.type='noise'; o.frequency.setValueAtTime(100,t); o.frequency.linearRampToValueAtTime(0,t+0.1); g.gain.setValueAtTime(0.1,t); g.gain.linearRampToValueAtTime(0,t+0.1); }
    o.start(t); o.stop(t+0.3);
}

// --- 🎮 游戏核心 (V18 内容回归) ---
const BIOMES={grass:{bg:'#5c94fc',ground:'#51D96C',monsters:['walker','slime','rabbit']}, dark:{bg:'#222',ground:'#555',monsters:['walker','bat','spiky']}, sky:{bg:'#87CEEB',ground:'#FFF',monsters:['bird','bat']}};
let state={level:1,score:0,coins:0}, frames=0, blocks=[], enemies=[], items=[], clouds=[], camX=0, finishLine=0, loopId=null;
let input={left:false,right:false,jump:false};
let player={x:100,y:200,w:40,h:56,dx:0,dy:0,grounded:false,jumpCount:0,dead:false,facingRight:true,enteringPipe:false, isBig:false, inKart:false, immune:0};

// V19 移动端手感参数
const IS_MOBILE = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
const MAX_SPEED = IS_MOBILE ? 7 : 9; 
const ACCEL = IS_MOBILE ? 0.9 : 1.5; 
const FRICTION = 0.85;

function createLevel(lvl) {
    blocks=[]; enemies=[]; items=[]; clouds=[]; player.enteringPipe=false;
    // 重置玩家状态，但不重置分数
    if(player.dead) { player.isBig=false; player.inKart=false; player.w=40; player.h=56; }

    const types=['grass','dark','sky']; const b=BIOMES[types[(lvl-1)%3]];
    wrapper.style.backgroundColor=b.bg; document.getElementById('level-val').innerText="1-"+lvl;
    
    for(let i=0; i<10; i++) clouds.push({x: Math.random()*2000, y: Math.random()*200, w: 60+Math.random()*40, s: 0.2+Math.random()*0.3});

    const gy=canvas.height-100; let x=0; finishLine=(70+lvl*30)*50;
    
    for(let i=0;i<15;i++){blocks.push({x:x,y:gy,w:50,h:50,type:'ground',c:b.ground});x+=50;}
    
    // --- 恢复 V18 的复杂地图生成逻辑 ---
    while(x<finishLine){
        if(Math.random() < 0.15 && lvl > 0){ 
            x += 80 + Math.random()*40; // 坑
        } 
        else {
            let len = 2 + Math.floor(Math.random()*4);
            for(let k=0; k<len; k++){
                blocks.push({x:x,y:gy,w:50,h:50,type:'ground',c:b.ground});
                if(Math.random()<0.3){ 
                    let mType = b.monsters[Math.floor(Math.random()*b.monsters.length)];
                    let my = gy-40; let mg = 0.7;
                    if(mType==='bat'||mType==='bird'){my-=150; mg=0;}
                    enemies.push({x:x,y:my,w:40,h:40,dx:-2,dy:0,g:mg,startX:x,startY:my,type:mType,dead:false}); 
                }
                x+=50;
            }
            // 平台与箱子
            if(Math.random() < 0.6) {
                let platformH = gy - 130; 
                let pX = x - (len*50) + 20; 
                for(let p=0; p<3; p++) {
                    if (Math.random() > 0.5) { 
                        let isBox = Math.random() < 0.3;
                        let type = isBox ? 'box' : 'brick';
                        let color = isBox ? '#FFD700' : '#8B4513';
                        let loot = 'coin';
                        if(isBox) {
                             if(Math.random()<0.3) loot = 'mushroom'; 
                             if(Math.random()<0.05) loot = 'kart';
                        }
                        blocks.push({x: pX + p*50, y: platformH, w: 50, h: 50, type: type, c: color, loot: loot, active: true});
                    }
                }
            }
        }
    }
    for(let i=0;i<10;i++){blocks.push({x:x,y:gy,w:50,h:50,type:'ground',c:b.ground});x+=50;}
    blocks.push({x:finishLine+200,y:gy-50,w:60,h:50,type:'pipe',c:'#00DD00'});
    blocks.push({x:finishLine+200,y:gy-100,w:60,h:50,type:'pipe_top',c:'#00DD00'});
    
    player.x=100; player.y=gy-200; player.dx=0; player.dy=0; player.dead=false; player.jumpCount=0; camX=0;
}

// --- 恢复 V18 的绘制函数 ---
function drawPlayer(x,y,w,h,dir){
    if(player.enteringPipe) ctx.globalAlpha = 0.7;
    if(player.immune > 0 && Math.floor(frames/5)%2===0) ctx.globalAlpha = 0.5;

    if (player.inKart) {
        ctx.fillStyle = "#FF0000"; ctx.fillRect(x-5, y+h-20, w+10, 20);
        ctx.fillStyle = "black"; ctx.fillRect(x-2, y+h-5, 10, 10); ctx.fillRect(x+w-8, y+h-5, 10, 10);
        ctx.fillStyle = "#FFCC99"; ctx.fillRect(x+10, y+h-30, 20, 15); // 头
    } else {
        // 小人绘制
        ctx.fillStyle="#EE0000";ctx.fillRect(x,y,w,h*0.25); // 帽
        ctx.fillRect(dir?x+5:x-5,y+h*0.2,w,h*0.1); 
        ctx.fillStyle="#FFCC99";ctx.fillRect(x+4,y+h*0.25,w-8,h*0.25); // 脸
        ctx.fillStyle="#EE0000";ctx.fillRect(x+4,y+h*0.5,w-8,h*0.25); // 衣
        ctx.fillStyle="#0000CC";ctx.fillRect(x+4,y+h*0.75,w-8,h*0.20); // 裤
        ctx.fillStyle="#5c3317";
        let legOffset = (Math.abs(player.dx)>0.1 && player.grounded) ? Math.sin(frames*0.5)*5 : 0;
        ctx.fillRect(x+4+legOffset,y+h-5,10,5); ctx.fillRect(x+w-14-legOffset,y+h-5,10,5);
    }
    ctx.globalAlpha = 1.0;
}

function drawEnemy(e) {
    let x=e.x-camX, y=e.y, w=e.w, h=e.h, dir=e.dx>0;
    if (y === undefined || isNaN(y)) return; 
    if (e.type === 'walker') {
        ctx.fillStyle = '#8B0000'; ctx.fillRect(x,y+h/2,w,h/2);
        ctx.fillStyle = '#D2691E'; ctx.fillRect(x-2,y,w+4,h/2+2);
        ctx.fillStyle='white'; ctx.fillRect(dir?x+w-10:x+2,y+5,8,8);
    } else if (e.type === 'slime') {
        ctx.fillStyle = '#32CD32'; ctx.beginPath(); ctx.moveTo(x,y+h); ctx.quadraticCurveTo(x+w/2,y-10,x+w,y+h); ctx.fill();
        ctx.fillStyle='black'; ctx.fillRect(dir?x+w-15:x+5,y+h-15,5,5);
    } else if (e.type === 'bat') {
        ctx.fillStyle = '#4B0082'; ctx.fillRect(x+10,y+10,w-20,h-20);
        ctx.beginPath(); ctx.moveTo(x,y+10); ctx.lineTo(x-15,y-5); ctx.lineTo(x+10,y+15); ctx.fill(); // 翅膀
        ctx.beginPath(); ctx.moveTo(x+w,y+10); ctx.lineTo(x+w+15,y-5); ctx.lineTo(x+w-10,y+15); ctx.fill();
    } else if (e.type === 'spiky') {
        ctx.fillStyle = '#006400'; ctx.fillRect(x,y+h-15,w,15);
        ctx.beginPath(); ctx.moveTo(x,y+h-15); ctx.lineTo(x+w/2,y); ctx.lineTo(x+w,y+h-15); ctx.fill();
    } else if (e.type === 'bird') {
        ctx.fillStyle = '#FFD700'; ctx.beginPath(); ctx.arc(x+w/2,y+h/2,w/2,0,6.28); ctx.fill();
        ctx.fillStyle='white'; ctx.fillRect(dir?x+w-15:x+5,y+10,8,8);
    }
}

function drawItem(i) {
    let x = i.x - camX, y = i.y;
    if (i.type === 'coin') {
        ctx.fillStyle = '#FFD700'; ctx.beginPath(); ctx.arc(x+15, y+15, 12, 0, Math.PI*2); ctx.fill();
        ctx.fillStyle = '#FFEE00'; ctx.font="20px monospace"; ctx.fillText("$", x+10, y+22);
    } else if (i.type === 'mushroom') {
        ctx.fillStyle = 'red'; ctx.beginPath(); ctx.arc(x+20, y+20, 18, 0, Math.PI, true); ctx.fill();
        ctx.fillStyle = 'white'; ctx.fillRect(x+10, y+20, 20, 15);
    } else if (i.type === 'kart') {
        ctx.fillStyle = 'white'; ctx.fillRect(x+5,y+5,30,20);
        ctx.fillStyle = 'red'; ctx.fillRect(x+5,y+5,15,10); ctx.fillRect(x+20,y+15,15,10);
    }
}

// --- 核心更新循环 (V18逻辑 + V19物理) ---
function update() {
    if(player.dead) return; 
    frames++; ctx.clearRect(0,0,canvas.width,canvas.height);

    // 云朵背景
    ctx.fillStyle = "rgba(255,255,255,0.4)";
    clouds.forEach(c => {
        c.x -= c.s; if(c.x < -100) c.x = canvas.width + Math.random()*500;
        ctx.beginPath(); ctx.arc(c.x, c.y, c.w, 0, Math.PI*2); ctx.fill();
    });

    if (player.enteringPipe) {
        player.dy = 2; player.y += player.dy;
        if(player.y > canvas.height) { state.level++; retryLevel(); return; }
        // 绘制场景
        drawItemsAndEnemies(); drawBlocks(); drawPlayer(player.x - camX, player.y, player.w, player.h, player.facingRight);
        loopId = requestAnimationFrame(update); return;
    }

    // 物理移动 (V19 优化手感)
    let maxS = player.inKart ? MAX_SPEED + 3 : MAX_SPEED;
    if(input.right) player.dx += ACCEL;
    else if(input.left) player.dx -= ACCEL;
    else player.dx *= FRICTION;
    
    if(player.dx > maxS) player.dx = maxS; if(player.dx < -maxS) player.dx = -maxS;
    if(Math.abs(player.dx) < 0.1) player.dx = 0;

    if(player.dx > 0) player.facingRight = true; if(player.dx < 0) player.facingRight = false;

    if(input.jump) {
        if(player.grounded){
            player.dy=player.inKart?-18:-15; player.grounded=false; player.jumpCount=1; playSound('jump');
        } else if(player.jumpCount < 3){ 
            player.dy=player.inKart?-16:-12; player.jumpCount++; playSound('jump');
        }
        input.jump = false; 
    }
    
    player.dy+=0.8; player.x+=player.dx; player.y+=player.dy;
    if (player.immune > 0) player.immune--;

    let tx=player.x-canvas.width*0.3; if(tx<0)tx=0; camX+=(tx-camX)*0.15;
    if(player.y>canvas.height+200) die();

    // 碰撞检测
    player.grounded=false;
    blocks.forEach(b=>{
        if(player.x<b.x+b.w&&player.x+player.w>b.x&&player.y<b.y+b.h&&player.y+player.h>b.y){
            if (b.type === 'pipe_top' && player.dy > 0 && Math.abs(player.x+player.w/2 - (b.x+b.w/2)) < 20) {
                player.enteringPipe = true; playSound('pipe'); return;
            }
            if(player.dy>0&&player.y+player.h-player.dy<=b.y+20){
                player.y=b.y-player.h;player.dy=0;player.grounded=true;player.jumpCount=0;
            } 
            else if(player.dy<0 && player.y-player.dy >= b.y+b.h-20) {
                player.y = b.y+b.h; player.dy=0;
                if(b.type==='box' && b.active) {
                    b.active=false; b.c='#CD853F'; 
                    let itemType = b.loot;
                    if(itemType==='coin') { state.coins++; state.score+=50; playSound('coin'); } 
                    else { items.push({x:b.x+10, y:b.y-40, w:30, h:30, type:itemType, dx:2, dy:-5, ground:false}); playSound('powerup'); }
                }
            }
            else { player.x-=player.dx; player.dx=0; } 
        }
    });

    // 道具逻辑
    items.forEach((i, idx)=>{
        if(i.ground) return; 
        if(i.type !== 'coin') { 
            i.dy+=0.5; i.x+=i.dx; i.y+=i.dy;
            blocks.forEach(b=>{ if(i.x<b.x+b.w&&i.x+i.w>b.x&&i.y<b.y+b.h&&i.y+i.h>b.y && i.dy>0) { i.y=b.y-i.h; i.dy=0; } });
        }
        if(player.x<i.x+i.w && player.x+player.w>i.x && player.y<i.y+i.h && player.y+player.h>i.y) {
            items.splice(idx, 1);
            if(i.type==='coin'){ state.coins++; state.score+=50; playSound('coin'); }
            else if(i.type==='mushroom'){ player.isBig=true; player.w=50; player.h=70; state.score+=1000; playSound('powerup'); }
            else if(i.type==='kart'){ player.inKart=true; player.isBig=true; player.w=60; player.h=40; state.score+=2000; playSound('powerup'); }
        }
    });

    // 敌人逻辑
    enemies.forEach(e=>{
        if(!e.dead){
            if(e.type==='bat' && e.startY !== undefined) e.y = e.startY + Math.sin(frames*0.05)*50;
            else if(e.type==='rabbit' && e.g>0 && Math.random()<0.02 && e.y>e.startY) e.dy = -12;
            else if(e.type==='slime') e.dx = Math.sin(frames*0.02)*2;
            
            e.dy+=e.g; e.x+=e.dx; e.y+=e.dy;
            if(e.g>0) blocks.forEach(b=>{ if(e.x<b.x+b.w&&e.x+e.w>b.x&&e.y+e.h>=b.y&&e.y+e.h<=b.y+20){e.y=b.y-e.h;e.dy=0;} });
            if(Math.abs(e.x-e.startX)>200 && e.type!=='bird') e.dx*=-1;

            if(player.x<e.x+e.w&&player.x+player.w>e.x&&player.y<e.y+e.h&&player.y+player.h>e.y){
                if (e.type === 'spiky' && !player.inKart) { takeDamage(); } 
                else if(player.dy>0 && player.y+player.h < e.y+e.h*0.8){
                    e.dead=true;player.dy=-8;state.score+=100;playSound('stomp');player.jumpCount=1; 
                } else { takeDamage(); }
            }
        }
    });

    drawItemsAndEnemies();
    drawBlocks();
    drawPlayer(player.x-camX,player.y,player.w,player.h,player.facingRight);
    
    document.getElementById('score-val').innerText=state.score;
    document.getElementById('coin-val').innerText=state.coins;
    loopId=requestAnimationFrame(update);
}

function takeDamage() {
    if (player.immune > 0) return;
    if (player.inKart) { player.inKart = false; player.isBig = true; player.w=50; player.h=70; player.immune = 120; playSound('pipe'); } 
    else if (player.isBig) { player.isBig = false; player.w=40; player.h=56; player.immune = 120; playSound('pipe'); } 
    else { die(); }
}

function drawItemsAndEnemies() {
    items.forEach(i=>{if(i.x-camX>-100&&i.x-camX<canvas.width) drawItem(i);});
    enemies.forEach(e=>{if(!e.dead&&e.x-camX>-100&&e.x-camX<canvas.width) drawEnemy(e);});
}

function drawBlocks() {
    blocks.forEach(b=>{
        if(b.x-camX>-100&&b.x-camX<canvas.width){
            ctx.fillStyle=b.c; ctx.fillRect(b.x-camX,b.y,b.w,b.h);
            if(b.type==='box' || b.type==='brick') {
                 if (b.type==='box') {
                    ctx.fillStyle='black'; ctx.font="30px monospace"; ctx.fillText("?", b.x-camX+15, b.y+35);
                 } else { ctx.fillStyle = "rgba(0,0,0,0.2)"; ctx.fillRect(b.x-camX, b.y+20, b.w, 5); }
                 ctx.strokeStyle='white'; ctx.lineWidth=2; ctx.strokeRect(b.x-camX,b.y,b.w,b.h);
            }
            if(b.type.includes('pipe')){
                ctx.strokeStyle='#005500';ctx.lineWidth=4;ctx.strokeRect(b.x-camX,b.y,b.w,b.h);
                if(b.type==='pipe_top'){ctx.fillStyle='#00AA00';ctx.fillRect(b.x-camX-5,b.y,b.w+10,20);}
            }
        }
    });
}

function die(){
    if(player.dead)return;
    player.dead=true; stopMusic(); cancelAnimationFrame(loopId); playMusic('gameover');
    document.getElementById('overlay').style.display='flex';
    document.getElementById('title-text').innerHTML="GAME OVER";
    document.getElementById('start-btn-group').style.display='none';
    document.getElementById('retry-btn-group').style.display='flex';
}

// 启动与重试
window.tryStartGame = function() {
    resizeCanvas(); state.score=0;state.coins=0;state.level=1;
    player.dead = false; document.getElementById('overlay').style.display='none';
    playMusic('bgm',state.level); createLevel(state.level); update();
}
window.retryLevel=function(){
    document.getElementById('overlay').style.display='none';
    playMusic('bgm',state.level); createLevel(state.level);
    if(loopId) cancelAnimationFrame(loopId); update();
}

// 输入监听 (触摸+键盘)
window.addEventListener('keydown',e=>{if(e.code==='ArrowRight')input.right=true;if(e.code==='ArrowLeft')input.left=true;if((e.code==='Space'||e.code==='ArrowUp')&&!e.repeat)input.jump=true;});
window.addEventListener('keyup',e=>{if(e.code==='ArrowRight')input.right=false;if(e.code==='ArrowLeft')input.left=false;if(e.code==='Space'||e.code==='ArrowUp')input.jump=false;});
const bindTouch=(id,k)=>{const el=document.getElementById(id);el.addEventListener('touchstart',e=>{e.preventDefault();input[k]=true;el.classList.add('active');},{passive:false});el.addEventListener('touchend',e=>{e.preventDefault();if(k!=='jump')input[k]=false;el.classList.remove('active');},{passive:false});};
bindTouch('btn-left','left'); bindTouch('btn-right','right'); bindTouch('btn-jump','jump');

</script></body></html>
"""

game_html = game_template.replace("__PLAYLIST_DATA__", playlist_json).replace("__GAMEOVER_DATA__", game_over_b64)
st.markdown("### 🍄 Super AI Kart: V20.0 (The Restoration)")
components.html(game_html, height=600, scrolling=False)
