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

src_path = Path(__file__).resolve().parent / "game.py"
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
    
    function hookInit(){
        // Level enhancement disabled - using original game levels
        return;
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

             if(!aiDebug) return;
            try{
                ctx.save();
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
        
        // Hardcoded AI config (removed level dependency)
        let C = window.__AI_CONSTANTS || {};
        let chaseRange = C.chaseRange || 420;
        let surroundRange = C.surroundRange || 520;
        let slamRange = C.slamRange || 160;
        let slamCooldown = C.slamCooldown || 120;
        
        let nearby = [];
        enemies.forEach(e=>{
            if(e.dead) return;
            if(!e.ai) e.ai = { state: "patrol", layer: "ground", patrolIndex: 0, wait: 0, slamCd: 0, role: 0, group: 0, slamPhase: "idle" };
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
            let chaseR = chaseRange;
            if(e.type === 3) chaseR = 250;
            if(e.type === 0) chaseR = 200; // Walker is less aggressive
            
            let inChase = dist < chaseR;
            let inSurround = dist < surroundRange && groups[e.ai.group] && groups[e.ai.group].members.length >= 2;
            if(e.ai.slamCd > 0) e.ai.slamCd--;
            if(e.ai.state === "slam"){
                if(e.ground && e.ai.slamPhase === "fall"){
                    e.ai.state = inChase ? "chase" : "patrol";
                    e.ai.slamPhase = "idle";
                    e.ai.slamCd = slamCooldown;
                } else if(e.dy > 0){
                    e.ai.slamPhase = "fall";
                }
            } else if(inChase && e.ai.slamCd === 0 && dist < slamRange && e.ground){
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
                // Simple patrol: move back and forth
                if(e.ai.wait > 0){ 
                    e.ai.wait--; 
                    e.dx = 0;
                } else {
                    let patrolSpd = C.patrolSpeed || 1.6;
                    if(e.type === 0) patrolSpd = 1.0; // Walker slower
                    e.dx = (e.ai.patrolIndex % 2 === 0 ? 1 : -1) * patrolSpd;
                    e.ai.wait = 24;
                    e.ai.patrolIndex++;
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
    setInterval(function(){ hookInit(); hookSpawn(); hookShoot(); hookDraw(); hookCore(); updateEnemyAI(); step(); }, 16);
})();
</script>
"""

enhanced_html = base_html + patch_js

components.html(enhanced_html, height=800)
