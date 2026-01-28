from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components
import base64
import os
import glob
import json

st.set_page_config(page_title="Super AI Kart: Physics + Level Enhanced", page_icon="🍄", layout="wide", initial_sidebar_state="collapsed")

st.markdown(
    """
    <style>
        #MainMenu, header, footer {visibility: hidden;}
        .block-container { padding: 0 !important; margin: 0 !important; max-width: 100% !important; }
        iframe { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; border: none; z-index: 9999; }
    </style>
    """,
    unsafe_allow_html=True,
)

src_path = Path("d:/my-ai-brain/game.py")
content = src_path.read_text(encoding="utf-8")

def get_audio_data(folder_path="mp3"):
    playlist = []
    game_over_data = ""
    level1_data = ""
    if not os.path.exists(folder_path):
        return "[]", "", ""
    all_files = glob.glob(os.path.join(folder_path, "*.mp3"))
    for file_path in all_files:
        filename = os.path.basename(file_path).lower()
        try:
            with open(file_path, "rb") as f:
                b64 = base64.b64encode(f.read()).decode()
                if "game_over.mp3" == filename:
                    game_over_data = b64
                elif "bgm.mp3" == filename:
                    level1_data = b64
                    playlist.append(b64)
                else:
                    playlist.append(b64)
        except:
            pass
    return json.dumps(playlist), game_over_data, level1_data

playlist_json, game_over_b64, level1_b64 = get_audio_data("mp3")

base_html = ""
start_idx = content.find('game_template = """')
if start_idx != -1:
    start_idx += len('game_template = """')
    end_idx = content.find('"""', start_idx)
    base_template = content[start_idx:end_idx]
    base_html = (
        base_template.replace("__PLAYLIST_DATA__", playlist_json)
        .replace("__GAMEOVER_DATA__", game_over_b64)
        .replace("__LEVEL1_DATA__", level1_b64)
    )
else:
    start_idx = content.find('game_html = """')
    if start_idx != -1:
        start_idx += len('game_html = """')
        end_idx = content.find('"""', start_idx)
        base_html = content[start_idx:end_idx]

# AI Configuration (Tunable Constants)
ai_constants = {
    "chaseRange": 450,
    "surroundRange": 550,
    "slamRange": 180,
    "slamCooldown": 100,
    "patrolSpeed": 1.6,
    "chaseSpeedBase": 1.8,
    "chaseSpeedMax": 2.5
}
ai_const_json = json.dumps(ai_constants)

patch_js = """
<script>
(function(){
    window.__AI_CONSTANTS = """ + ai_const_json + """;
    let prevGround = true;
    let baseMobile = 0.62;
    let baseDesktop = 0.68;
    let portalCooldown = 0;
    let prevHasFire = false;
    let aiDebug = false;
    let aiConfigCache = null;
    let lastPlayerPos = {x:0,y:0};
    let doubleJumpLocked = false;
    function enhanceLevel(lvl){
        if(typeof blocks === 'undefined') return;
        blocks.length = 0;
        enemies.length = 0;
        items.length = 0;
        projectiles.length = 0;
        window.__movingPlatforms = [];
        window.__springs = [];
        window.__portals = [];
        window.__hiddenBlocks = [];
        window.__tutorialHints = [];
        window.__exitRule = { requiresBoss: true };
        let groundY = canvas.height - 80;
        let t = BIOMES[lvl % BIOMES.length];
        let diff = Math.max(0, lvl);
        let enemyScale = 1 + diff * 0.3;
        let platformSpeed = 1 + diff * 0.15;
        blocks.push({x:-200, y:groundY, w:600, h:200, c:t.ground, type:'ground'});
        let cx = 400;

        function spawnLine(x, y, type, count, gap){
            for(let i=0;i<count;i++){
                spawnEnemy(x + i * gap, y, type);
            }
        }

        if(lvl === 0) {
            blocks.push({x:cx, y:groundY, w:1100, h:200, c:t.ground, type:'ground'});
            blocks.push({x:cx+200, y:groundY-140, w:60, h:100, c:t.brick, type:'ground'});
            blocks.push({x:cx+600, y:groundY-140, w:60, h:100, c:t.brick, type:'ground'});
            blocks.push({x:cx+260, y:groundY-160, w:340, h:40, c:t.brick, type:'ground'});
            createBricks(cx+420, groundY-120, t);
            spawnLine(cx+500, groundY-40, 'walker', Math.max(1, Math.round(enemyScale)), 140);
            blocks.push({x:cx+900, y:groundY-80, w:60, h:80, c:t.pipe, type:'pipe'});
            cx += 1100;

            blocks.push({x:cx, y:groundY, w:1200, h:200, c:t.ground, type:'ground'});
            blocks.push({x:cx+120, y:groundY-110, w:160, h:40, c:t.top, type:'ground'});
            blocks.push({x:cx+380, y:groundY-150, w:160, h:40, c:t.top, type:'ground'});
            blocks.push({x:cx+660, y:groundY-110, w:160, h:40, c:t.top, type:'ground'});
            window.__hiddenBlocks.push({x: cx+420, y: groundY-260, w:60, h:60, c:t.brick, content:"star", triggered:false});
            spawnLine(cx+260, groundY-40, 'jumper', Math.max(1, Math.round(enemyScale)), 200);
            spawnLine(cx+520, groundY-40, 'walker', Math.max(1, Math.round(enemyScale)), 180);
            cx += 1200;

            blocks.push({x:cx, y:groundY, w:1200, h:200, c:t.brick, type:'ground'});
            blocks.push({x:cx+100, y:groundY-50, w:60, h:50, c:t.brick, type:'ground'});
            blocks.push({x:cx+180, y:groundY-90, w:60, h:90, c:t.brick, type:'ground'});
            blocks.push({x:cx+260, y:groundY-140, w:200, h:140, c:t.brick, type:'ground'});
            cx += 1200;

            window.__tutorialHints.push({x:120, y:groundY-120, t:"方向键移动，空格跳跃", r:380, lvl:0});
            window.__tutorialHints.push({x:1100, y:groundY-240, t:"高处路线有隐藏奖励", r:420, lvl:0});
            window.__tutorialHints.push({x:cx-800, y:groundY-160, t:"击败BOSS后进入绿色出口", r:520, lvl:0});
        } else if(lvl === 1) {
            blocks.push({x:cx, y:groundY, w:1200, h:200, c:t.ground, type:'ground'});
            blocks.push({x:cx+120, y:groundY-80, w:60, h:80, c:t.pipe, type:'pipe'});
            blocks.push({x:cx+340, y:groundY-120, w:60, h:120, c:t.pipe, type:'pipe'});
            blocks.push({x:cx+560, y:groundY-160, w:60, h:160, c:t.pipe, type:'pipe'});
            blocks.push({x:cx+820, y:groundY-100, w:60, h:100, c:t.pipe, type:'pipe'});
            spawnLine(cx+380, groundY-40, 'walker', Math.max(2, Math.round(enemyScale)+1), 160);
            spawnEnemy(cx+680, groundY-40, 'drill');
            cx += 1200;

            let gapStart = cx;
            let gapWidth = 700;
            let mp1 = {x: gapStart, y: groundY-90, w:110, h:20, c:t.top, type:'ground', moving:{axis:'x', min: gapStart, max: gapStart+gapWidth-110, spd:2*platformSpeed, dir:1}};
            blocks.push(mp1);
            window.__movingPlatforms.push(mp1);
            let mp2 = {x: gapStart+320, y: groundY-50, w:110, h:20, c:t.top, type:'ground', moving:{axis:'y', min: groundY-160, max: groundY-40, spd:1.6*platformSpeed, dir:1}};
            blocks.push(mp2);
            window.__movingPlatforms.push(mp2);
            let mp3 = {x: gapStart+540, y: groundY-120, w:120, h:20, c:t.top, type:'ground', moving:{axis:'x', min: gapStart+420, max: gapStart+gapWidth-120, spd:2.4*platformSpeed, dir:-1}};
            blocks.push(mp3);
            window.__movingPlatforms.push(mp3);
            cx += gapWidth;

            blocks.push({x:cx, y:groundY, w:1200, h:200, c:t.ground, type:'ground'});
            blocks.push({x:cx+300, y:groundY-100, w:60, h:100, c:t.brick, type:'ground'});
            blocks.push({x:cx+900, y:groundY-100, w:60, h:100, c:t.brick, type:'ground'});
            spawnLine(cx+200, groundY-40, 'walker', Math.max(2, Math.round(enemyScale)+1), 180);
            spawnLine(cx+600, groundY-40, 'jumper', Math.max(1, Math.round(enemyScale)), 220);
            cx += 1200;

            window.__tutorialHints.push({x:200, y:groundY-120, t:"管道附近有敌人巡逻", r:380, lvl:1});
            window.__tutorialHints.push({x:cx-1500, y:groundY-220, t:"移动平台可选择上方路线", r:520, lvl:1});
            window.__tutorialHints.push({x:cx-700, y:groundY-160, t:"击败BOSS后进入绿色出口", r:520, lvl:1});
        } else {
            let variant = lvl % 3;
            if(variant === 0) {
                blocks.push({x:cx, y:groundY, w:900, h:200, c:t.ground, type:'ground'});
                blocks.push({x:cx+120, y:groundY-110, w:160, h:40, c:t.top, type:'ground'});
                blocks.push({x:cx+360, y:groundY-150, w:160, h:40, c:t.top, type:'ground'});
                blocks.push({x:cx+640, y:groundY-120, w:160, h:40, c:t.top, type:'ground'});
                spawnLine(cx+220, groundY-40, 'walker', Math.max(2, Math.round(enemyScale)+1), 160);
                spawnLine(cx+520, groundY-40, 'jumper', Math.max(1, Math.round(enemyScale)), 200);
                cx += 900;

                let gapStart = cx;
                let gapWidth = 800;
                let mp1 = {x: gapStart+80, y: groundY-100, w:120, h:20, c:t.top, type:'ground', moving:{axis:'x', min: gapStart+40, max: gapStart+gapWidth-160, spd:2.2*platformSpeed, dir:1}};
                blocks.push(mp1);
                window.__movingPlatforms.push(mp1);
                let mp2 = {x: gapStart+420, y: groundY-140, w:140, h:20, c:t.top, type:'ground', moving:{axis:'y', min: groundY-200, max: groundY-60, spd:1.8*platformSpeed, dir:1}};
                blocks.push(mp2);
                window.__movingPlatforms.push(mp2);
                cx += gapWidth;

                blocks.push({x:cx, y:groundY, w:1200, h:200, c:t.brick, type:'ground'});
                spawnLine(cx+240, groundY-40, 'flyer', Math.max(1, Math.round(enemyScale)-1), 240);
                cx += 1200;
                window.__tutorialHints.push({x:cx-1400, y:groundY-200, t:"移动平台速度更快", r:520, lvl:lvl});
            } else if(variant === 1) {
                blocks.push({x:cx, y:groundY, w:1100, h:200, c:t.ground, type:'ground'});
                blocks.push({x:cx+220, y:groundY-90, w:80, h:90, c:t.brick, type:'ground'});
                blocks.push({x:cx+520, y:groundY-120, w:80, h:120, c:t.brick, type:'ground'});
                blocks.push({x:cx+820, y:groundY-100, w:80, h:100, c:t.brick, type:'ground'});
                spawnLine(cx+300, groundY-40, 'walker', Math.max(2, Math.round(enemyScale)+1), 160);
                spawnLine(cx+640, groundY-40, 'drill', Math.max(1, Math.round(enemyScale)-1), 260);
                cx += 1100;

                blocks.push({x:cx, y:groundY-150, w:260, h:40, c:t.top, type:'ground'});
                blocks.push({x:cx+320, y:groundY-180, w:260, h:40, c:t.top, type:'ground'});
                blocks.push({x:cx+640, y:groundY-150, w:260, h:40, c:t.top, type:'ground'});
                blocks.push({x:cx, y:groundY, w:1200, h:200, c:t.ground, type:'ground'});
                spawnLine(cx+260, groundY-40, 'jumper', Math.max(2, Math.round(enemyScale)), 220);
                cx += 1200;
                window.__tutorialHints.push({x:cx-1100, y:groundY-260, t:"注意跳跃节奏", r:520, lvl:lvl});
            } else {
                blocks.push({x:cx, y:groundY, w:1000, h:200, c:t.ground, type:'ground'});
                blocks.push({x:cx+160, y:groundY-120, w:200, h:40, c:t.top, type:'ground'});
                blocks.push({x:cx+460, y:groundY-160, w:200, h:40, c:t.top, type:'ground'});
                blocks.push({x:cx+760, y:groundY-120, w:200, h:40, c:t.top, type:'ground'});
                spawnLine(cx+220, groundY-40, 'walker', Math.max(2, Math.round(enemyScale)+1), 160);
                spawnLine(cx+560, groundY-40, 'flyer', Math.max(1, Math.round(enemyScale)-1), 240);
                cx += 1000;

                let gapStart = cx;
                let gapWidth = 650;
                let mp1 = {x: gapStart+120, y: groundY-90, w:120, h:20, c:t.top, type:'ground', moving:{axis:'x', min: gapStart+80, max: gapStart+gapWidth-160, spd:2.6*platformSpeed, dir:1}};
                blocks.push(mp1);
                window.__movingPlatforms.push(mp1);
                cx += gapWidth;

                blocks.push({x:cx, y:groundY, w:1200, h:200, c:t.ground, type:'ground'});
                spawnLine(cx+220, groundY-40, 'jumper', Math.max(2, Math.round(enemyScale)), 200);
                cx += 1200;
                window.__tutorialHints.push({x:cx-1200, y:groundY-220, t:"平台速度加快", r:520, lvl:lvl});
            }
            window.__tutorialHints.push({x:cx-800, y:groundY-160, t:"击败BOSS后进入绿色出口", r:520, lvl:lvl});
        }

        // Common Boss Spawn
        let bossStyle = lvl % 3;
        let bossProps = {
            0: { name: "IRON TITAN", color: "#B71C1C", w:100, h:100, hp:10, spd:2 },
            1: { name: "SHADOW NINJA", color: "#4A148C", w:70, h:70, hp:8, spd:5 },
            2: { name: "GOLD KING", color: "#FFD700", w:110, h:110, hp:12, spd:2 }
        }[bossStyle];
        
        // Find Boss Arena Center (approx)
        let arenaEnd = cx; 
        let arenaStart = arenaEnd - 1200;

        window.boss = {
            x: arenaStart + 600, y: groundY - bossProps.h, w: bossProps.w, h: bossProps.h, 
            dx: 0, dy: 0, hp: bossProps.hp, maxHp: bossProps.hp,
            iframes: 0, dead: false, style: bossStyle, name: bossProps.name,
            color: bossProps.color,
            baseSpd: bossProps.spd, timer: 0, action: 'chase'
        };
        if(window.__bossBehavior && window.__bossBehavior.attach) window.__bossBehavior.attach(window.boss, lvl);
        
        window.goal = { x: arenaEnd + 50, y: groundY-150, w: 70, h: 150, cx: arenaEnd+85 };
        window.goal.__cx = window.goal.cx;
        blocks.push({ x: goal.x, y: goal.y, w: goal.w, h: goal.h, c: "#00C853", type:'pipe' });
        blocks.push({x:arenaEnd, y:groundY, w:300, h:200, c:t.ground, type:'ground'});
    }

    function getAIConfig(lvl){
        if(aiConfigCache) return aiConfigCache;
        let groundY = canvas.height - 80;
        let baseX = 600 + lvl * 400;
        let C = window.__AI_CONSTANTS || {};
        let fallback = {
            layers: [
                { name: "ground", speed: C.patrolSpeed||1.6, wait: 24, points: [
                    {x: baseX + 200, y: groundY - 40},
                    {x: baseX + 800, y: groundY - 40},
                    {x: baseX + 1400, y: groundY - 40}
                ]},
                { name: "high", speed: (C.patrolSpeed||1.6)*0.75, wait: 32, points: [
                    {x: baseX + 350, y: groundY - 240},
                    {x: baseX + 950, y: groundY - 300},
                    {x: baseX + 1550, y: groundY - 260}
                ]}
            ],
            chaseRange: C.chaseRange || 420,
            surroundRange: C.surroundRange || 520,
            slamRange: C.slamRange || 160,
            slamCooldown: C.slamCooldown || 120
        };
        try{
            if(window.__AI_CONFIG_JSON){
                aiConfigCache = JSON.parse(window.__AI_CONFIG_JSON);
                return aiConfigCache;
            }
            if(window.__AI_CONFIG){
                aiConfigCache = window.__AI_CONFIG;
                return aiConfigCache;
            }
        }catch(e){}
        aiConfigCache = fallback;
        return aiConfigCache;
    }
    function ensurePath(lvl){
        if(typeof blocks === 'undefined' || !Array.isArray(blocks)) return;
        let groundY = canvas.height - 80;
        let corridorTop = groundY - 160;
        let corridorBottom = groundY - 30;
        let startX = 120;
        let endX = goal ? goal.x : (startX + 3000);
        let gapWidth = 70;
        let additions = [];
        for(let sx = startX; sx < endX; sx += 220){
            let segmentBlocks = [];
            for(let i=0;i<blocks.length;i++){
                let b = blocks[i];
                if(b.type==='ground' || b.type==='pipe'){
                    let intersectsX = !(b.x + b.w < sx || b.x > sx + 200);
                    let coversCorridor = (b.y <= corridorTop && (b.y + b.h) >= corridorBottom);
                    if(intersectsX && coversCorridor){
                        segmentBlocks.push({idx:i, b:b});
                    }
                }
            }
            for(let s of segmentBlocks){
                let b = s.b;
                let gx = Math.max(b.x + gapWidth, Math.min(b.x + b.w - gapWidth, b.x + b.w/2));
                let leftW = gx - gapWidth/2 - b.x;
                let rightW = (b.x + b.w) - (gx + gapWidth/2);
                if(leftW < 20 && rightW < 20){
                    let newH = corridorTop - b.y - 10;
                    if(newH > 10) b.h = newH;
                    continue;
                }
                if(leftW >= 20 && rightW >= 20){
                    let rightBlock = {x: gx + gapWidth/2, y: b.y, w: rightW, h: b.h, c: b.c, type: b.type};
                    b.w = leftW;
                    additions.push(rightBlock);
                } else if(leftW >= 20){
                    b.w = leftW;
                } else if(rightW >= 20){
                    b.x = gx + gapWidth/2;
                    b.w = rightW;
                }
            }
        }
        for(let add of additions) blocks.push(add);
    }

    // --- NEW: Rules & Logic Injection ---
    window.createBricks = function(bx, by, t) {
        let rng = Math.random();
        let content = "coin";
        if(rng < 0.4) content = "coin";
        else if(rng < 0.55) content = "mushroom";
        else if(rng < 0.7) content = "flower";
        else if(rng < 0.8) content = "kart";
        else if(rng < 0.9) content = (Math.random()<0.5 ? "bigcoin" : "multicoin");
        else content = (Math.random()<0.5 ? "speed" : "trap");
        
        blocks.push({ x:bx, y:by, w:60, h:60, c: t.brick, type:'brick', content:content, hit:false, qBlock:true });
        blocks.push({x:bx+60, y:by, w:60, h:60, c: t.brick, type:'brick', content:null});
        blocks.push({x:bx-60, y:by, w:60, h:60, c: t.brick, type:'brick', content:null});
    };

    let origSpawnItem = window.spawnItem || function(){};
    window.spawnItem = function(block) {
        if(!block.content) return;
        if(block.content === "star") {
            items.push({ x: block.x+15, y: block.y-32, w:30, h:30, type: 4, dy:-8, dx:2, state:'spawning' });
            if(typeof window.AudioSystem !== 'undefined') window.AudioSystem.playSFX('powerup', block.x);
            else if(typeof playTone === 'function') playTone(1000, 'sine', 0.1);
            block.content = null; block.hit = true;
            return;
        }
        // Fix for original spawnItem issue if any
        if(typeof origSpawnItem === 'function') origSpawnItem(block);
    };

    window.__hiddenBlocks = [];
    function checkHiddenBlocks() {
        if(!window.__hiddenBlocks || !player) return;
        window.__hiddenBlocks.forEach((hb, i) => {
            if(hb.triggered) return;
            if(player.dy < 0 && 
               player.x + player.w > hb.x && player.x < hb.x + hb.w &&
               player.y >= hb.y + hb.h - 15 && player.y <= hb.y + hb.h + 25) {
                
                player.dy = 0; player.y = hb.y + hb.h; hb.triggered = true;
                
                blocks.push({x:hb.x, y:hb.y, w:hb.w, h:hb.h, c: hb.c, type:'brick', content:hb.content, hit:false});
                spawnItem(blocks[blocks.length-1]);
                window.__hiddenBlocks.splice(i, 1);
                
                if(typeof window.AudioSystem !== 'undefined') window.AudioSystem.playSFX('coin', player.x); 
            }
        });
    }

    function handleStar() {
        if(typeof items === 'undefined') return;
        items.forEach((it, i) => {
            if(it.type === 4) {
                 if(it.state !== 'static') {
                     it.dy += 0.5; it.x += it.dx; it.y += it.dy;
                     if(it.y > canvas.height - 100) { it.y = canvas.height - 100; it.dy = -12; } 
                     blocks.forEach(b => {
                        if(colCheck(it, b)) {
                            if(it.dy > 0 && it.y + it.h - it.dy <= b.y + 15) { it.y = b.y - it.h; it.dy = -12; }
                            else it.dx *= -1;
                        }
                     });
                 }
                 if(colCheck(player, it)) {
                     items.splice(i, 1);
                     player.invul = 600; 
                     player.hasStar = true;
                     score += 1000;
                     floatText.push({x:player.x, y:player.y-20, t:"STAR MODE!", life:60});
                     if(typeof window.AudioSystem !== 'undefined') window.AudioSystem.playBGM('climax');
                 }
            }
        });
        if(player.hasStar && player.invul > 0) {
            // No simple way to set colorOverride in original game without editing draw()
            // But we can draw a glow in hookDraw
        } else {
            player.hasStar = false;
        }
    }

    function hookInit(){
        if(typeof initLevel !== 'function' || initLevel.__enhanced) return;
        let baseInit = initLevel;
        initLevel = function(lvl){
            aiConfigCache = null;
            baseInit(lvl);
            try{ enhanceLevel(lvl); }catch(e){}
        };
        initLevel.__enhanced = true;
    }
    function hookSpawn(){
        if(window.__spawnHooked || typeof spawnEnemy !== 'function') return;
        let baseSpawn = spawnEnemy;
        window.spawnEnemy = function(x, y, type){
            baseSpawn(x, y, type);
            let e = enemies && enemies.length ? enemies[enemies.length-1] : null;
            if(e && !e.ai){
                e.ai = { state: "patrol", layer: (type==='flyer' ? "high" : "ground"), patrolIndex: 0, wait: 0, slamCd: 0, role: 0, group: 0, slamPhase: "idle" };
            }
        };
        window.__spawnHooked = true;
    }
    function hookCore(){
        if(window.__coreHooked || typeof update !== 'function') return;
        let baseUpdate = update;
        window.update = function(){
            let jBackup = (typeof input !== 'undefined') ? input.j : false;
            if(typeof player !== 'undefined' && typeof input !== 'undefined'){
                if(!player.ground && player.jumps >= 2 && !player.kart) input.j = false;
                if(player.ground) doubleJumpLocked = false;
            }
            if(typeof goal !== 'undefined' && goal && typeof boss !== 'undefined' && boss && !boss.dead){
                if(typeof goal.__cx === 'undefined') goal.__cx = goal.cx;
                goal.cx = goal.__cx + 99999;
                goal.__locked = true;
            } else if(typeof goal !== 'undefined' && goal && goal.__locked) {
                goal.cx = goal.__cx;
                goal.__locked = false;
            }
            let prevBossHp = (typeof boss !== 'undefined' && boss) ? boss.hp : null;
            let weakOpen = false;
            if(typeof boss !== 'undefined' && boss && !boss.dead){
                weakOpen = (boss.action === 'recover') || (boss.action === 'jump_attack' && boss.timer < 12);
                if(boss.__weakTimer && boss.__weakTimer > 0) weakOpen = true;
            }
            baseUpdate();
            if(typeof input !== 'undefined') input.j = jBackup;
            if(typeof boss !== 'undefined' && boss){
                let useBehavior = (typeof window.__bossBehavior !== 'undefined' && window.__bossBehavior && window.__bossBehavior.isActive && window.__bossBehavior.isActive());
                if(!boss.dead){
                    if(!useBehavior){
                        if(!boss.phase) boss.phase = 'normal';
                        if(boss.hp <= boss.maxHp/2 && boss.phase !== 'rage'){
                            boss.phase = 'rage';
                            boss.baseSpd = boss.baseSpd + 1.2;
                            floatText.push({x:boss.x, y:boss.y-20, t:"RAGE!", life:50});
                        }
                        if(boss.phase === 'rage' && frames % 90 === 0){
                            let count = 6;
                            for(let i=0;i<count;i++){
                                let ang = (Math.PI*2) * (i/count);
                                projectiles.push({x: boss.x+boss.w/2, y: boss.y+boss.h/2, w:18, h:18, dx: Math.cos(ang)*6, dy: Math.sin(ang)*4, type: boss.style, life:80});
                            }
                            boss.__weakTimer = 40;
                        }
                        if(boss.__weakTimer && boss.__weakTimer > 0) boss.__weakTimer--;
                        if(prevBossHp !== null && prevBossHp > boss.hp && !weakOpen){
                            boss.hp = prevBossHp;
                            boss.iframes = 0;
                        }
                    }
                } else if(!boss.__rewarded){
                    boss.__rewarded = true;
                    playTone(600, 'sine', 0.3);
                    floatText.push({x:boss.x, y:boss.y-30, t:"BOSS DOWN!", life:80});
                }
            }
        };
        let baseAddCoin = window.addCoin;
        window.addCoin = function(x, y, a){
            if(typeof CoinManager !== "undefined" && CoinManager.get){
                CoinManager.get().add(a || 1, x, y);
            } else if(typeof baseAddCoin === "function"){
                baseAddCoin(x, y, a);
            } else {
                window.coinCount = (window.coinCount||0) + (a||1);
                window.score = (window.score||0) + 100 * (a||1);
            }
            for(let k=0;k<5;k++) particles.push({x:x+10, y:y+10, dx:(Math.random()-0.5)*4, dy:-3-Math.random()*3, life:40, c:'#FFD700'});
            playTone(1050, 'square', 0.1); playTone(1300, 'sine', 0.1);
            floatText.push({x:x, y:y-20, t:"🪙", life:30});
        };
        window.__coreHooked = true;
    }
    function hookDraw(){
        if(window.__drawHooked || typeof draw !== 'function') return;
        let baseDraw = draw;
        window.draw = function(){
            baseDraw();
            if(typeof goal !== 'undefined' && goal && typeof ctx !== 'undefined'){
                ctx.save();
                let gx = goal.x - camX - 5;
                ctx.fillStyle = "#00C853";
                ctx.fillRect(gx, goal.y, goal.w + 10, 30);
                ctx.fillStyle = goal.__locked ? "#FFEB3B" : "#FFFFFF";
                ctx.font = "bold 14px Arial";
                ctx.fillText(goal.__locked ? "BOSS" : "EXIT", goal.x - camX + 8, goal.y + 55);
                ctx.restore();
            }
            if(window.__tutorialHints && typeof player !== 'undefined' && typeof ctx !== 'undefined'){
                window.__tutorialHints.forEach(h=>{
                    if(typeof level !== 'undefined' && h.lvl !== level) return;
                    if(Math.abs(player.x - h.x) > h.r) return;
                    ctx.save();
                    ctx.fillStyle = "rgba(0,0,0,0.6)";
                    ctx.fillRect(30, 40, 520, 50);
                    ctx.fillStyle = "#FFFFFF";
                    ctx.font = "16px Arial";
                    ctx.fillText(h.t, 50, 72);
                    ctx.restore();
                });
            }
            if(window.__hiddenBlocks && typeof ctx !== 'undefined') {
                ctx.save();
                window.__hiddenBlocks.forEach(b => {
                    if(b.x > camX - 100 && b.x < camX + canvas.width + 100) {
                        ctx.fillStyle = "rgba(255, 255, 255, 0.15)";
                        ctx.fillRect(b.x - camX, b.y, b.w, b.h);
                        ctx.strokeStyle = "rgba(255, 255, 255, 0.3)";
                        ctx.lineWidth = 2;
                        ctx.strokeRect(b.x - camX, b.y, b.w, b.h);
                    }
                });
                ctx.restore();
            }
            
            // Draw Star Effect
            if(player.hasStar && player.invul > 0 && typeof ctx !== 'undefined') {
                 ctx.save();
                 ctx.globalCompositeOperation = 'lighter';
                 ctx.fillStyle = `hsla(${frames*20}, 100%, 50%, 0.4)`;
                 ctx.beginPath();
                 ctx.arc(player.x - camX + player.w/2, player.y + player.h/2, 50, 0, Math.PI*2);
                 ctx.fill();
                 ctx.restore();
            }

            if(!aiDebug || !window.__patrolLayers || !window.__patrolLayers.length) return;
            try{
                ctx.save();
                ctx.strokeStyle = "rgba(255,255,255,0.35)";
                ctx.fillStyle = "rgba(255,255,255,0.8)";
                ctx.font = "bold 12px Arial";
                window.__patrolLayers.forEach(layer=>{
                    let pts = layer.points || [];
                    for(let i=0;i<pts.length;i++){
                        let p = pts[i];
                        let px = p.x - camX;
                        let py = p.y;
                        ctx.beginPath();
                        ctx.arc(px, py, 4, 0, Math.PI*2);
                        ctx.fill();
                        if(i<pts.length-1){
                            let np = pts[i+1];
                            ctx.beginPath();
                            ctx.moveTo(px, py);
                            ctx.lineTo(np.x - camX, np.y);
                            ctx.stroke();
                        }
                    }
                });
                enemies.forEach(e=>{
                    if(!e.ai) return;
                    let ex = e.x - camX + e.w/2;
                    let ey = e.y - 10;
                    ctx.fillStyle = "rgba(0,0,0,0.6)";
                    ctx.fillRect(ex-40, ey-14, 80, 16);
                    ctx.fillStyle = "#00E5FF";
                    ctx.textAlign = "center";
                    let stateText = e.ai.state.toUpperCase();
                    if(e.ai.stuckTimer > 15) stateText = "STUCK!";
                    ctx.fillText(stateText, ex, ey-2);
                    ctx.textAlign = "start";
                });
                ctx.restore();
            }catch(e){}
        };
        window.__drawHooked = true;
    }
    function updatePatrolLayers(lvl){
        let cfg = getAIConfig(lvl);
        window.__patrolLayers = (cfg.layers || []).map(l=>({
            name: l.name,
            speed: l.speed || 1.2,
            wait: l.wait || 30,
            points: (l.points || []).map(p=>({x:p.x, y:p.y}))
        }));
    }
    function assignGroups(nearby){
        let groups = [];
        nearby.forEach(e=>{
            let assigned = false;
            for(let g of groups){
                if(Math.abs(e.x - g.cx) < 220){
                    g.members.push(e);
                    g.cx = (g.cx + e.x) / 2;
                    assigned = true;
                    break;
                }
            }
            if(!assigned) groups.push({cx:e.x, members:[e]});
        });
        groups.forEach((g, gi)=>{
            g.members.forEach((e, idx)=>{
                e.ai.group = gi;
                e.ai.role = idx;
            });
        });
        return groups;
    }
    function updateEnemyAI(){
        if(!Array.isArray(enemies) || typeof player === 'undefined') return;
        let cfg = getAIConfig(level || 0);
        let C = window.__AI_CONSTANTS || {};
        if(!window.__patrolLayers) updatePatrolLayers(level || 0);
        let nearby = [];
        enemies.forEach(e=>{
            if(e.dead) return;
            if(!e.ai) e.ai = { state: "patrol", layer: (e.type===1 ? "high" : "ground"), patrolIndex: 0, wait: 0, slamCd: 0, role: 0, group: 0, slamPhase: "idle" };
            if(e.x > camX - 200 && e.x < camX + canvas.width + 200) nearby.push(e);
        });
        let groups = assignGroups(nearby);
        let px = player.x;
        let py = player.y;
        let playerSpeed = Math.abs(player.x - lastPlayerPos.x);
        lastPlayerPos = {x: player.x, y: player.y};
        nearby.forEach(e=>{
            // Stuck check
            if(e.ai.state !== 'slam' && Math.abs(e.dx) > 0.1){
                if(Math.abs(e.x - (e.ai.lastX || e.x)) < 0.5) e.ai.stuckTimer = (e.ai.stuckTimer||0) + 1;
                else e.ai.stuckTimer = 0;
            } else {
                e.ai.stuckTimer = 0;
            }
            e.ai.lastX = e.x;
            if(e.ai.stuckTimer > 20 && e.ground){
                e.dy = -11; 
                e.ai.stuckTimer = 0;
            }

            let dx = px - e.x;
            let dy = py - e.y;
            let dist = Math.sqrt(dx*dx + dy*dy);
            
            // Frog & Walker Nerf: Reduce range for Type 3 (Jumper) and Type 0 (Walker)
            let chaseR = cfg.chaseRange;
            if(e.type === 3) chaseR = 250;
            if(e.type === 0) chaseR = 200; // Walker is less aggressive
            
            let inChase = dist < chaseR;
            let inSurround = dist < cfg.surroundRange && groups[e.ai.group] && groups[e.ai.group].members.length >= 2;
            if(e.ai.slamCd > 0) e.ai.slamCd--;
            if(e.ai.state === "slam"){
                if(e.ground && e.ai.slamPhase === "fall"){
                    e.ai.state = inChase ? "chase" : "patrol";
                    e.ai.slamPhase = "idle";
                    e.ai.slamCd = cfg.slamCooldown;
                } else if(e.dy > 0){
                    e.ai.slamPhase = "fall";
                }
            } else if(inChase && e.ai.slamCd === 0 && dist < cfg.slamRange && e.ground){
                // Frog Nerf: Lower jump height and less aggression
                let jumpPwr = 14 + Math.min(6, playerSpeed);
                if(e.type === 3) jumpPwr = 9; 
                
                e.ai.state = "slam";
                e.ai.slamPhase = "air";
                e.dy = -jumpPwr;
                e.dx = (dx>0?1:-1) * (e.type === 3 ? 1.5 : 2.5);
            } else if(inSurround){
                e.ai.state = "surround";
            } else if(inChase){
                e.ai.state = "chase";
            } else {
                e.ai.state = "patrol";
            }
            if(e.ai.state === "patrol"){
                let layer = window.__patrolLayers.find(l=>l.name===e.ai.layer) || window.__patrolLayers[0];
                if(layer && layer.points.length){
                    if(e.ai.wait > 0){ e.ai.wait--; }
                    else {
                        let target = layer.points[e.ai.patrolIndex % layer.points.length];
                        let dir = target.x > e.x ? 1 : -1;
                        e.dx = dir * layer.speed;
                        if(Math.abs(target.x - e.x) < 20){
                            e.ai.wait = layer.wait;
                            e.ai.patrolIndex = (e.ai.patrolIndex + 1) % layer.points.length;
                        }
                    }
                }
            } else if(e.ai.state === "chase"){
                let dir = dx > 0 ? 1 : -1;
                let baseSpd = C.chaseSpeedBase || 1.6;
                let maxSpd = C.chaseSpeedMax || 2.5;
                
                // Walker Nerf
                if(e.type === 0) { baseSpd = 1.0; maxSpd = 1.4; }
                
                e.dx = dir * (baseSpd + Math.min(maxSpd - baseSpd, playerSpeed * 0.4));
            } else if(e.ai.state === "surround"){
                let g = groups[e.ai.group];
                let ring = 120 + (g ? g.members.length * 20 : 100);
                let offset = (e.ai.role % 2 === 0) ? ring : -ring;
                let targetX = px + offset;
                let dir = targetX > e.x ? 1 : -1;
                e.dx = dir * 2.0;
            }
            if(e.type === 1 && e.ai.state !== "patrol"){
                let dir = dx > 0 ? 1 : -1;
                e.dx = dir * 2.2;
            }
        });
    }
    function step(){
        try{
            if(typeof PHYSICS === 'undefined' || typeof player === 'undefined' || typeof input === 'undefined') return;
            let base = (typeof isMobile !== 'undefined' && isMobile) ? baseMobile : baseDesktop;
            let rise = base * 0.85;
            let fall = base * 1.35;
            let cut  = base * 1.55;
            let g = base;
            if(player.dy < 0){
                g = (input.j ? rise : cut);
            } else if(player.dy > 0){
                g = fall;
            } else {
                g = base;
            }
            PHYSICS.grav = g;
            if(!player.ground){
                player.dx *= 0.985;
            }
            if(prevGround === false && player.ground === true){
                player.dx *= 0.88;
                for(let k=0;k<6;k++){
                    particles.push({x: player.x + player.w/2, y: player.y + player.h, dx:(Math.random()-0.5)*6, dy:(Math.random()-0.5)*6, life:12, c:'#FFFFFF'});
                }
            }
            if(window.__movingPlatforms){
                window.__movingPlatforms.forEach(p=>{
                    if(!p.moving) return;
                    if(p.moving.axis==='x'){
                        p.x += p.moving.spd * p.moving.dir;
                        if(p.x < p.moving.min || p.x > p.moving.max) p.moving.dir *= -1;
                    } else {
                        p.y += p.moving.spd * p.moving.dir;
                        if(p.y < p.moving.min || p.y > p.moving.max) p.moving.dir *= -1;
                    }
                });
            }
            if(window.__springs){
                window.__springs.forEach(s=>{
                    if(colCheck(player, s) && player.dy >= 0 && player.y + player.h - player.dy <= s.y + 12){
                        player.dy = -14;
                        player.ground = false;
                        player.jumps = 1;
                        for(let k=0;k<8;k++){
                            particles.push({x: s.x + s.w/2, y: s.y, dx:(Math.random()-0.5)*8, dy:-Math.random()*6, life:14, c:'#B2FF59'});
                        }
                    }
                });
            }
            if(portalCooldown>0) portalCooldown--;
            if(window.__portals && portalCooldown===0){
                window.__portals.forEach(p=>{
                    if(colCheck(player, p.from) && player.ground && player.dy >= 0){
                        player.x = p.to.x;
                        player.y = p.to.y;
                        player.dx = 0;
                        player.dy = 0;
                        if(typeof camX !== 'undefined') camX = Math.max(0, player.x - canvas.width * 0.3);
                        portalCooldown = 40;
                    }
                });
            }
            if(player.hasFire && !prevHasFire){
                player.invul = Math.max(player.invul||0, 90);
                if(player.hp < 2) player.hp = 2;
                player.w = 40; player.h = 56;
                input.fLock = false;
            }
            prevHasFire = !!player.hasFire;
            prevGround = player.ground;
        }catch(e){}
    }
    function hookShoot(){
        if(typeof window.__shootHooked !== 'undefined') return;
        let orig = window.shootFireball;
        window.shootFireball = function(){
            try{
                if(typeof player === 'undefined' || !player.hasFire || player.kart || player.inPipe || player.dead) return;
                // Use global p_bullets directly (defined in game.py)
                if(typeof p_bullets === 'undefined') return;
                if(p_bullets.length > 30) return;
                
                let b = {
                    x: player.x + (player.facing>0 ? player.w : 0),
                    y: player.y + 10,
                    w: 12, h: 12,
                    dx: player.facing * 8,
                    dy: 0,
                    life: 60
                };
                p_bullets.push(b);
                if(typeof window.AudioSystem !== 'undefined') window.AudioSystem.playSFX('fireball', player.x);
                else if(typeof playTone === 'function') playTone(800, 'sawtooth', 0.05);
            }catch(e){
                console.error("Shoot error:", e);
            }
        };
        window.__shootHooked = true;
    }

    window.addEventListener('keydown', e=>{ if(e.key==='v'||e.key==='V') aiDebug = !aiDebug; });
    setInterval(function(){ hookInit(); hookSpawn(); hookShoot(); hookDraw(); hookCore(); updatePatrolLayers(level||0); updateEnemyAI(); step(); checkHiddenBlocks(); handleStar(); }, 16);
})();
</script>
"""

enhanced_html = base_html + patch_js

components.html(enhanced_html, height=800)
