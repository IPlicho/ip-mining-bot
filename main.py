<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<title>欢乐游戏城</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{background:#121212;color:#fff;font-family:Arial}
.head{background:#1e1e1e;padding:18px 15px;display:flex;justify-content:space-between;align-items:center}
.logo{font-size:22px;font-weight:bold;color:#ffcc00}
.points{background:#367ff7;padding:6px 12px;border-radius:20px;font-size:14px}
.game-box{display:grid;grid-template-columns:1fr 1fr;gap:12px;padding:15px}
.game{background:#1e1e1e;border-radius:12px;padding:15px;text-align:center}
.game .icon{font-size:40px;margin-bottom:10px}
.game .name{font-size:16px;margin-bottom:5px}
.game .btn{background:#ffcc00;color:#000;padding:8px 12px;border-radius:8px;margin-top:8px;font-size:14px;font-weight:bold;border:none;width:100%}
.kefu{position:fixed;bottom:25px;right:25px;width:60px;height:60px;border-radius:50%;background:#ffcc00;color:#000;display:flex;align-items:center;justify-content:center;font-size:26px}
.modal{position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.8);display:none;justify-content:center;align-items:center}
.modal-body{background:#1e1e1e;width:90%;max-width:400px;padding:25px;border-radius:16px;text-align:center}
.close{margin-top:20px;background:#367ff7;color:#fff;padding:10px 20px;border-radius:8px;border:none}
.slot{display:flex;gap:10px;justify-content:center;margin:20px 0}
.reel{width:70px;height:70px;background:#000;border:2px solid #ffcc00;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:30px}
.spin{background:#ff3333;color:#fff;padding:12px 25px;border:none;border-radius:8px;font-size:16px;font-weight:bold}
</style>
</head>
<body>
<div class="head">
<div class="logo">🎮 欢乐游戏城</div>
<div class="points">积分: <span id="score">加载中...</span></div>
</div>
<div class="game-box">
<div class="game">
<div class="icon">🎰</div>
<div class="name">老虎机</div>
<button class="btn" onclick="openSlot()">开始游戏</button>
</div>
<div class="game">
<div class="icon">🎡</div>
<div class="name">幸运转盘</div>
<button class="btn" onclick="alert('即将开放')">开始游戏</button>
</div>
<div class="game">
<div class="icon">🃏</div>
<div class="name">翻牌抽奖</div>
<button class="btn" onclick="alert('即将开放')">开始游戏</button>
</div>
<div class="game">
<div class="icon">👤</div>
<div class="name">个人中心</div>
<button class="btn" onclick="alert('个人中心')">进入</button>
</div>
</div>
<div class="kefu" onclick="alert('联系客服：你的微信号')">💬</div>
<div class="modal" id="slotModal">
<div class="modal-body">
<h2>🎰 老虎机</h2>
<div class="slot">
<div class="reel" id="a">🍒</div>
<div class="reel" id="b">🍋</div>
<div class="reel" id="c">🍉</div>
</div>
<button class="spin" onclick="spin()">开始转动</button>
<div id="result" style="margin-top:15px;font-size:18px"></div>
<button class="close" onclick="closeSlot()">关闭</button>
</div>
</div>

<script>
// Supabase配置（后面你替换成自己的）
const SUPABASE_URL = "YOUR_SUPABASE_URL";
const SUPABASE_KEY = "YOUR_SUPABASE_ANON_KEY";
const USER_ID = "guest_001"; // 可扩展多用户，先固定一个

let score = 0;
const icons = ["🍒","🍋","🍉","7️⃣","⭐","🍇"];

// 初始化：从数据库加载积分
async function initScore() {
    try {
        const res = await fetch(`${SUPABASE_URL}/rest/v1/user_score?user_id=eq.${USER_ID}`, {
            headers: {
                "apikey": SUPABASE_KEY,
                "Authorization": `Bearer ${SUPABASE_KEY}`
            }
        });
        const data = await res.json();
        if (data.length > 0) {
            score = data[0].score;
        } else {
            // 新用户，初始化1000积分
            score = 1000;
            await fetch(`${SUPABASE_URL}/rest/v1/user_score`, {
                method: "POST",
                headers: {
                    "apikey": SUPABASE_KEY,
                    "Authorization": `Bearer ${SUPABASE_KEY}`,
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ user_id: USER_ID, score: 1000 })
            });
        }
        document.getElementById("score").innerText = score;
    } catch (e) {
        console.error("加载积分失败", e);
        document.getElementById("score").innerText = "1000";
        score = 1000;
    }
}

// 更新积分到数据库
async function updateScore() {
    await fetch(`${SUPABASE_URL}/rest/v1/user_score?user_id=eq.${USER_ID}`, {
        method: "PATCH",
        headers: {
            "apikey": SUPABASE_KEY,
            "Authorization": `Bearer ${SUPABASE_KEY}`,
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ score: score })
    });
    document.getElementById("score").innerText = score;
}

function openSlot(){document.getElementById("slotModal").style.display="flex"}
function closeSlot(){document.getElementById("slotModal").style.display="none"}

async function spin(){
if(score < 50){
alert("积分不足！");
return;
}
score -= 50;
await updateScore();
document.getElementById("result").innerText = "转动中...";

let a = icons[Math.floor(Math.random()*icons.length)];
let b = icons[Math.floor(Math.random()*icons.length)];
let c = icons[Math.floor(Math.random()*icons.length)];

document.getElementById("a").innerText = a;
document.getElementById("b").innerText = b;
document.getElementById("c").innerText = c;

if(a==b && b==c){
score += 500;
document.getElementById("result").innerText = "🎉 恭喜中奖！+500分";
}else{
document.getElementById("result").innerText = "谢谢参与";
}
await updateScore();
}

// 页面加载完成后初始化积分
window.onload = initScore;
</script>
</body>
</html>
