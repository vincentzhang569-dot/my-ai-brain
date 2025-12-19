import streamlit as st
import streamlit.components.v1 as components
import base64
import os
import glob
import json

# --- 1. 页面配置 ---
st.set_page_config(
    page_title="Super AI Kart: Infinite Sound",
    page_icon="🍄",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. 音频数据处理 (带容错) ---
def get_audio_data(folder_path="mp3"):
    playlist = []
    game_over_data = ""
    level1_data = ""
    # 即使文件夹不存在，也返回空，让前端JS去处理兜底逻辑
    if os.path.exists(folder_path):
        all_files = glob.glob(os.path.join(folder_path, "*.mp3"))
        for file_path in all_files:
            filename = os.path.basename(file_path).lower()
            try:
                with open(file_path, "rb") as f:
                    b64 = base64.b64encode(f.read()).decode()
                    if "game_over.mp3" == filename: game_over_data = b64
                    elif "bgm.mp3" == filename: level1_data = b64; playlist.append(b64)
                    else: playlist.append(b64)
            except: pass
    return json.dumps(playlist), game_over_data, level1_data

playlist_json, game_over_b64, level1_b64 = get_audio_data("mp3")

# --- 3. 游戏核心 (HTML/JS) ---
game_template = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<style>
    @import url('https://fonts.googleapis.com/css2?family=VT323&display=swap');
    body{margin:0;background-color:#0e1117;color:white;font-family:'VT323',monospace;overflow:hidden;height:100vh;display:flex;flex-direction:column;align-items:center;}
    #game-wrapper{position:relative;width:100%;height:100%;background-color:#333;overflow:hidden;}
    canvas{display:block;width:100%;height:100%;}
    .ui-text{position:absolute;color:white;text-shadow:3px 3px #000;z-index:10;pointer-events:none;font-size:32px;font-weight:bold;}
    #score-board{top:20px;left:20px;} #coin-board{top:20px;left:250px;color:#FFD700;} #level-board{top:20px;right:20px;color:#00FF00;}
    #overlay{position:absolute;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.85);display:flex;flex-direction:column;align-items:center;justify-content:center;z-index:20;}
    h1{font-size:90px;margin:0;color:#FF4500;text-shadow:6px 6px #000;letter-spacing:5px;}
    .btn-container{display:flex;gap:20px;margin-top:30px;}
    button.pixel-btn{background:#00AA00;border:4px solid #fff;color:white;font-family:'VT323';font-size:36px;padding:15px 40px;cursor:pointer;box-shadow:0 8px 0 #005500;text-transform:uppercase;}
    button.pixel-btn:active{transform:translateY(8px);box-shadow:none;}
    button.red-btn{background:#CC0000;box-shadow:0 8px 0 #660000;} button.blue-btn{background:#0066CC;box-shadow:0 8px 0 #003366;}
    #error-log { position: absolute; top: 0; left: 0; color: red; background: rgba(0,0,0,0.8); z-index: 100; font-size: 16px; display: none; padding: 10px; pointer-events: none;}
    #controls{position:absolute;bottom:30px;width:100%;display:flex;justify-content:space-between;padding:0 30px;box-sizing:border-box;z-index:15;pointer-events:none;}
    .ctrl-group{display:flex;gap:20px;pointer-events:auto;}
    .ctrl-btn{width:80px;height:80px;background:rgba(255,255,255,0.2);border:2px solid rgba(255,255,255,0.5);border-radius:15px;display:flex;align-items:center;justify-content:center;font-size:40px;color:white;user-select:none;}
    .btn-a{border-radius:50%;width:90px;height:90px;background:rgba(255,69,0,0.4);}
    @media(min-width:1024px){#controls{display:none;}}
</style>
</head>
<body>
<div id="game-wrapper">
    <div id="error-log"></div>
    <div id="score-board" class="ui-text">SCORE: <span id="score-val">0</span></div>
    <div id="coin-board" class="ui-text">💰 <span id="coin-val">0</span></div>
    <div id="level-board" class="ui-text">WORLD <span id="level-val">1-1</span></div>
    <div id="overlay">
        <h1 id="title-text">SUPER AI<br>KART</h1>
        <p id="sub-text" style="color:#aaa;font-size:24px;margin-top:10px;">[Space] Triple Jump | [Arrows] Move</p>
        <div id="start-btn-group" class="btn-container"><button class="pixel-btn" onclick="tryStartGame()">START GAME</button></div>
        <div id="retry-btn-group" class="btn-container" style="display:none;"><button class="pixel-btn blue-btn" onclick="retryLevel()">Retry Level</button><button class="pixel-btn red-btn" onclick="tryStartGame()">New Game</button></div>
    </div>
    <canvas id="gameCanvas"></canvas>
    <div id="controls"><div class="ctrl-group"><div class="ctrl-btn" id="btn-left">◀</div><div class="ctrl-btn" id="btn-right">▶</div></div><div class="ctrl-group"><div class="ctrl-btn btn-a" id="btn-jump">A</div></div></div>
</div>
<script>
window.onerror = function(msg, url, line) { document.getElementById('error-log').style.display = 'block'; document.getElementById('error-log').innerText = "Err: " + msg; return false; };
const canvas=document.getElementById('gameCanvas'), ctx=canvas.getContext('2d'), wrapper=document.getElementById('game-wrapper');
function resizeCanvas(){canvas.width=wrapper.clientWidth;canvas.height=wrapper.clientHeight;}
window.addEventListener('resize',resizeCanvas); resizeCanvas();

const bgmPlaylist=__PLAYLIST_DATA__, gameOverB64="__GAMEOVER_DATA__", level1B64="__LEVEL1_DATA__";
let audioCtx=null, currentSource=null;
let proceduralInterval = null; // 用于AI合成音乐的定时器

// --- 🎵 AI 音乐合成器 (当没有MP3时触发) ---
function startProceduralBGM() {
    if(proceduralInterval) clearInterval(proceduralInterval);
    if(!audioCtx) audioCtx=new(window.AudioContext||window.webkitAudioContext)();
    
    let tick = 0;
    const bassLine = [110, 110, 146.83, 146.83, 130.81, 130.81, 98, 98]; // A2, D3, C3, G2
    const melody = [440, 0, 523.25, 659.25, 587.33, 0, 440, 392]; // A4, C5, E5, D5...
    
    proceduralInterval = setInterval(() => {
        if(audioCtx.state === 'suspended') audioCtx.resume();
        const t = audioCtx.currentTime;
        
        // 1. Bass (贝斯)
        let bassNote = bassLine[Math.floor(tick/4) % bassLine.length];
        if (tick % 2 === 0) { // 每两拍响一次
            const o = audioCtx.createOscillator();
            const g = audioCtx.createGain();
            o.type = 'square'; // 8-bit 风格
            o.frequency.value = bassNote;
            g.gain.setValueAtTime(0.1, t);
            g.gain.exponentialRampToValueAtTime(0.01, t + 0.2);
            o.connect(g); g.connect(audioCtx.destination);
            o.start(t); o.stop(t + 0.2);
        }

        // 2. Melody (主旋律 - 随机一点)
        if (Math.random() > 0.3) {
            const o2 = audioCtx.createOscillator();
            const g2 = audioCtx.createGain();
            o2.type = 'triangle';
            // 简单的 C 大调五声音阶
            const scale = [523.25, 587.33, 659.25, 783.99, 880.00]; 
            let note = scale[Math.floor(Math.random() * scale.length)];
            // 偶尔升八度
            if(Math.random() > 0.8) note *= 2;
            
            o2.frequency.setValueAtTime(note, t);
            g2.gain.setValueAtTime(0.05, t);
            g2.gain.exponentialRampToValueAtTime(0.001, t + 0.15);
            o2.connect(g2); g2.connect(audioCtx.destination);
            o2.start(t); o2.stop(t + 0.15);
        }
        
        tick++;
    }, 150); // 速度 BPM
}

function stopMusic() {
    if(currentSource){try{currentSource.stop();}catch(e){}currentSource=null;}
    if(proceduralInterval) { clearInterval(proceduralInterval); proceduralInterval = null; }
}

async function playMusic(t,l){
    try {
        if(!audioCtx) audioCtx=new(window.AudioContext||window.webkitAudioContext)();
        if(audioCtx.state==='suspended') await audioCtx.resume();
        stopMusic();

        let b="",loop=true,vol=0.3;
        // 如果是 Game Over，还是尝试加载数据，如果没有数据则用合成音
        if(t==='gameover'){
            if (gameOverB64) { b=gameOverB64; loop=false; vol=0.5; }
            else { 
                // 简单的失败音效
                const o=audioCtx.createOscillator();const g=audioCtx.createGain();
                o.frequency.setValueAtTime(150, audioCtx.currentTime);
                o.frequency.linearRampToValueAtTime(50, audioCtx.currentTime+1);
                g.gain.setValueAtTime(0.2, audioCtx.currentTime);
                g.gain.linearRampToValueAtTime(0, audioCtx.currentTime+1);
                o.connect(g);g.connect(audioCtx.destination);o.start();o.stop(audioCtx.currentTime+1);
                return;
            }
        }
        else{
            if(l===1&&level1B64) b=level1B64;
            else if(bgmPlaylist.length>0) b=bgmPlaylist[Math.floor(Math.random()*bgmPlaylist.length)];
        }
        
        // --- 核心逻辑：如果有文件数据，播放文件；否则启动 AI 合成 ---
        if(!b || b === "[]" || b.length < 100) {
            console.log("No BGM data found, starting AI synthesizer...");
            startProceduralBGM();
            return;
        }

        const bin=window.atob(b),bytes=new Uint8Array(bin.length);
        for(let i=0;i<bin.length;i++)bytes[i]=bin.charCodeAt(i);
        const buf=await audioCtx.decodeAudioData(bytes.buffer);
        const src=audioCtx.createBufferSource();
        src.buffer=buf;src.loop=loop;const g=audioCtx.createGain();g.gain.value=vol;
        src.connect(g);g.connect(audioCtx.destination);src.start(0);currentSource=src;
    } catch(e){
        console.warn("Audio load failed, fallback to synth:", e);
        startProceduralBGM(); // 失败也回退到合成音
    }
}

function playSound(t){
    try {
        if(!audioCtx)return;
        const o=audioCtx.createOscillator(),g=audioCtx.createGain();
        o.connect(g);g.connect(audioCtx.destination);const n=audioCtx.currentTime;
        if(t==='jump'){
            let freq = 150 + (player.jumpCount * 100); 
            o.frequency.setValueAtTime(freq,n);o.frequency.linearRampToValueAtTime(freq+150,n+0.1);g.gain.setValueAtTime(0.1,n);g.gain.linearRampToValueAtTime(0,n+0.1);
        }
        else if(t==='coin'){o.frequency.setValueAtTime(1200,n);o.frequency.linearRampToValueAtTime(1800,n+0.1);g.gain.setValueAtTime(0.1,n);g.gain.linearRampToValueAtTime(0,n+0.15);}
        else if(t==='powerup'){o.type='triangle';o.frequency.setValueAtTime(300,n);o.frequency.linearRampToValueAtTime(600,n+0.3);g.gain.setValueAtTime(0.2,n);g.gain.linearRampToValueAtTime(0,n+0.3);}
        else if(t==='stomp'){o.type='square';o.frequency.setValueAtTime(100,n);o.frequency.linearRampToValueAtTime(50,n+0.1);g.gain.setValueAtTime(0.1,n);g.gain.linearRampToValueAtTime(0,n+0.1);}
        else if(t==='pipe'){o.type='sine';o.frequency.setValueAtTime(400,n);o.frequency.linearRampToValueAtTime(100,n+0.5);g.gain.setValueAtTime(0.3,n);g.gain.linearRampToValueAtTime(0,n+0.5);o.start(n);o.stop(n+0.5);return;}
        o.start(n);o.stop(n+0.2);
    } catch(e){}
}

const BIOMES={grass:{bg:'#5c94fc',ground:'#51D96C',monsters:['walker','slime','rabbit']}, dark:{bg:'#222',ground:'#555',monsters:['walker','bat','spiky']}, sky:{bg:'#87CEEB',ground:'#FFF',monsters:['bird','bat']}};
let state={level:1,score:0,coins:0}, frames=0, blocks=[], enemies=[], items=[], clouds=[], camX=0, finishLine=0, loopId=null, input={left:false,right:false,jump:false};
let player={x:100,y:200,w:40,h:56,dx:0,dy:0,grounded:false,jumpCount:0,dead:false,facingRight:true,enteringPipe:false, isBig:false, inKart:false, immune:0};

function drawPlayer(x,y,w,h,dir){
    if(player.enteringPipe) ctx.globalAlpha = 0.7;
    if(player.immune > 0 && Math.floor(frames/5)%2===0) ctx.globalAlpha = 0.5;

    if (player.inKart) {
        ctx.fillStyle = "#FF0000"; ctx.fillRect(x-5, y+h-20, w+10, 20);
        ctx.fillStyle = "black"; ctx.fillRect(x-2, y+h-5, 10, 10); ctx.fillRect(x+w-8, y+h-5, 10, 10);
        ctx.fillStyle = "#FFCC99"; ctx.fillRect(x+10, y+h-30, 20, 15);
        ctx.fillStyle = "#EE0000"; ctx.fillRect(x+10, y+h-35, 20, 5);
    } else {
        ctx.fillStyle="#EE0000";ctx.fillRect(x,y,w,h*0.25);
        ctx.fillRect(dir?x+5:x-5,y+h*0.2,w,h*0.1); 
        ctx.fillStyle="#FFCC99";ctx.fillRect(x+4,y+h*0.25,w-8,h*0.25);
        ctx.fillStyle="#EE0000";ctx.fillRect(x+4,y+h*0.5,w-8,h*0.25);
        ctx.fillStyle="#0000CC";ctx.fillRect(x+4,y+h*0.75,w-8,h*0.20);
        
        ctx.fillStyle="#5c3317";
        let legOffset = 0;
        if (Math.abs(player.dx) > 0.1 && player.grounded) { legOffset = Math.sin(frames * 0.4) * 8; }
        if (!player.grounded && player.jumpCount >= 2) {
            ctx.fillStyle = "#FFD700"; 
            ctx.fillRect(x+w/2-5, y+h, 10, Math.random()*10); 
            ctx.fillStyle="#5c3317"; 
        }
        ctx.fillRect(x + 4 + legOffset, y + h - 8, 12, 8); 
        ctx.fillRect(x + w - 16 - legOffset, y + h - 8, 12, 8);
    }
    ctx.globalAlpha = 1.0;
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
        ctx.fillStyle = 'black'; ctx.fillRect(x+5,y,2,40);
    }
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
        ctx.beginPath(); ctx.moveTo(x,y+10); ctx.lineTo(x-15,y-5); ctx.lineTo(x+10,y+15); ctx.fill();
        ctx.beginPath(); ctx.moveTo(x+w,y+10); ctx.lineTo(x+w+15,y-5); ctx.lineTo(x+w-10,y+15); ctx.fill();
    } else if (e.type === 'spiky') {
        ctx.fillStyle = '#006400'; ctx.fillRect(x,y+h-15,w,15);
        ctx.beginPath(); ctx.moveTo(x,y+h-15); ctx.lineTo(x+w/2,y); ctx.lineTo(x+w,y+h-15); ctx.fill();
    } else if (e.type === 'rabbit') {
        ctx.fillStyle = '#8B4513'; ctx.fillRect(x,y+10,w,h-10); ctx.fillRect(x,y,10,10); ctx.fillRect(x+w-10,y,10,10);
    } else if (e.type === 'bird') {
        ctx.fillStyle = '#FFD700'; ctx.beginPath(); ctx.arc(x+w/2,y+h/2,w/2,0,6.28); ctx.fill();
        ctx.fillStyle='white'; ctx.fillRect(dir?x+w-15:x+5,y+10,8,8);
    }
}

function createLevel(lvl) {
    blocks=[]; enemies=[]; items=[]; clouds=[]; player.enteringPipe=false; 
    if(player.dead) { player.isBig=false; player.inKart=false; player.w=40; player.h=56; }
    
    const types=['grass','dark','sky']; const b=BIOMES[types[(lvl-1)%3]];
    wrapper.style.backgroundColor=b.bg; document.getElementById('level-val').innerText="1-"+lvl;
    
    for(let i=0; i<10; i++) clouds.push({x: Math.random()*2000, y: Math.random()*200, w: 60+Math.random()*40, s: 0.2+Math.random()*0.3});

    const gy=canvas.height-100; let x=0; finishLine=(70+lvl*30)*50;
    
    for(let i=0;i<15;i++){blocks.push({x:x,y:gy,w:50,h:50,type:'ground',c:b.ground});x+=50;}
    
    while(x<finishLine){
        let r=Math.random();
        
        if(r < 0.20 && lvl > 0){ 
            x += 80 + Math.random()*40; 
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
                        if (Math.random() < 0.3) {
                             blocks.push({x: pX + p*50 + 20, y: platformH - 120, w: 50, h: 50, type: 'brick', c: '#8B4513'});
                        }
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

function update() {
    if(player.dead) return; 
    frames++; ctx.clearRect(0,0,canvas.width,canvas.height);

    ctx.fillStyle = "rgba(255,255,255,0.4)";
    clouds.forEach(c => {
        c.x -= c.s; 
        if(c.x < -100) c.x = canvas.width + Math.random()*500;
        ctx.beginPath(); ctx.arc(c.x, c.y, c.w, 0, Math.PI*2); ctx.fill();
        ctx.beginPath(); ctx.arc(c.x+c.w*0.5, c.y-20, c.w*0.8, 0, Math.PI*2); ctx.fill();
    });

    if (player.enteringPipe) {
        player.dy = 2; player.y += player.dy;
        let pipe = blocks.find(b => b.type === 'pipe_top' && Math.abs(b.x - player.x) < 100);
        if (pipe) player.x += (pipe.x + pipe.w/2 - player.w/2 - player.x) * 0.1;
        drawItemsAndEnemies(); drawPlayer(player.x - camX, player.y, player.w, player.h, player.facingRight); drawBlocks();
        if (player.y > canvas.height) { state.level++; retryLevel(); return; }
        loopId = requestAnimationFrame(update); return;
    }
    
    let speed = player.inKart ? 10 : 6;
    if(input.right){player.dx=speed;player.facingRight=true;}else if(input.left){player.dx=-speed;player.facingRight=false;}else player.dx=0;
    
    if(input.jump){
        if(player.grounded){
            player.dy=player.inKart?-18:-16;
            player.grounded=false;
            player.jumpCount=1;
            playSound('jump');
            input.jump=false;
        }
        else if(player.jumpCount < 3){ 
            player.dy=player.inKart?-16:-13; 
            player.jumpCount++;
            playSound('jump');
            input.jump=false;
        }
    }
    
    player.dy+=0.8; player.x+=player.dx; player.y+=player.dy;
    if (player.immune > 0) player.immune--;

    let tx=player.x-canvas.width*0.3;if(tx<0)tx=0;camX+=(tx-camX)*0.15;
    if(player.y>canvas.height+200)die();

    player.grounded=false;
    blocks.forEach(b=>{
        if(player.x<b.x+b.w&&player.x+player.w>b.x&&player.y<b.y+b.h&&player.y+player.h>b.y){
            if (b.type === 'pipe_top' && player.dy > 0 && player.y+player.h <= b.y+20 && Math.abs(player.x+player.w/2 - (b.x+b.w/2)) < 20) {
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
            else { player.x-=player.dx; } 
        }
    });

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
    drawPlayer(player.x-camX,player.y,player.w,player.h,player.facingRight);
    drawBlocks();
    
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
                 } else {
                    ctx.fillStyle = "rgba(0,0,0,0.2)"; ctx.fillRect(b.x-camX, b.y+20, b.w, 5);
                 }
                 ctx.strokeStyle='white'; ctx.lineWidth=2; ctx.strokeRect(b.x-camX,b.y,b.w,b.h);
            }
            if(b.type.includes('pipe')){ctx.strokeStyle='#005500';ctx.lineWidth=4;ctx.strokeRect(b.x-camX,b.y,b.w,b.h);
            if(b.type==='pipe_top'){ctx.fillStyle='#00AA00';ctx.fillRect(b.x-camX-5,b.y,b.w+10,20);}
            }
        }
    });
}

function die(){
    if(player.dead)return;
    player.dead=true;
    stopMusic();
    cancelAnimationFrame(loopId);
    playMusic('gameover');
    document.getElementById('title-text').innerHTML="GAME OVER";
    document.getElementById('overlay').style.display='flex';
    document.getElementById('start-btn-group').style.display='none';
    document.getElementById('retry-btn-group').style.display='flex';
}

window.tryStartGame = function() {
    try {
        resizeCanvas();
        state.score=0;state.coins=0;state.level=1;
        player.dead = false; 
        document.getElementById('overlay').style.display='none';
        playMusic('bgm',state.level);
        createLevel(state.level);
        if(loopId) cancelAnimationFrame(loopId);
        update();
    } catch(e) {
        alert("Startup Error: " + e.message);
    }
}
window.retryLevel=function(){
    try {
        document.getElementById('overlay').style.display='none';
        playMusic('bgm',state.level);
        createLevel(state.level);
        if(loopId) cancelAnimationFrame(loopId);
        update();
    } catch(e) {
         alert("Retry Error: " + e.message);
    }
}

window.addEventListener('keydown',e=>{if(e.code==='ArrowRight')input.right=true;if(e.code==='ArrowLeft')input.left=true;if((e.code==='Space'||e.code==='ArrowUp')&&!e.repeat)input.jump=true;});
window.addEventListener('keyup',e=>{if(e.code==='ArrowRight')input.right=false;if(e.code==='ArrowLeft')input.left=false;if(e.code==='Space'||e.code==='ArrowUp')input.jump=false;});
const at=(id,k)=>{const el=document.getElementById(id);el.addEventListener('touchstart',e=>{e.preventDefault();input[k]=true;});el.addEventListener('touchend',e=>{e.preventDefault();if(k!=='jump')input[k]=false;});};at('btn-left','left');at('btn-right','right');at('btn-jump','jump');
</script></body></html>
"""

game_html = game_template.replace("__PLAYLIST_DATA__", playlist_json).replace("__GAMEOVER_DATA__", game_over_b64).replace("__LEVEL1_DATA__", level1_b64)
st.markdown("### 🍄 Super AI Kart: Infinite Sound Edition")
components.html(game_html, height=600, scrolling=False)
