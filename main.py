from flask import Flask, render_template
from flask_socketio import SocketIO, emit, join_room
import random
import os
from collections import defaultdict

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mahjong-platform-key'
# 核心修复：锁定异步模式+兼容Werkzeug
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# ======================
# 平台配置（4个积分场次）
# ======================
ROOMS = {
    "1": {"name": "新手场", "cost": 100,  "max": 4},
    "2": {"name": "中级场", "cost": 500,  "max": 4},
    "3": {"name": "高手场", "cost": 2000, "max": 4},
    "4": {"name": "大师场", "cost": 10000,"max": 4},
}

# 用户积分数据（新用户自动送1000）
users = defaultdict(lambda: 1000)

# 房间全局状态（服务器统一管理，防作弊）
rooms = defaultdict(lambda: {
    "players": [],   # {sid, uid, name, hand}
    "deck": [],
    "discards": [],
    "current": 0,
    "started": False
})

# 完整麻将牌（136张）
TILES = []
for t in ["万", "条", "筒"]:
    for n in range(1,10):
        TILES.extend([f"{n}{t}"]*4)
for z in ["东", "南", "西", "北", "中", "发", "白"]:
    TILES.extend([z]*4)

# ======================
# 页面路由
# ======================
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/hall")
def hall():
    return render_template("hall.html", rooms=ROOMS)

@app.route("/room/<rid>")
def room(rid):
    if rid not in ROOMS:
        return "房间不存在"
    return render_template("game.html", rid=rid, room=ROOMS[rid])

# ======================
# Socket 实时通信逻辑
# ======================

# 登录/注册
@socketio.on("login")
def login(data):
    uid = data["uid"]
    emit("login_ok", {"uid": uid, "score": users[uid]})

# 进入房间（检查积分门槛）
@socketio.on("enter_room")
def enter_room(data):
    rid = data["rid"]
    uid = data["uid"]
    if rid not in ROOMS:
        return
    # 检查积分是否够入场
    cost = ROOMS[rid]["cost"]
    if users[uid] < cost:
        emit("err", {"msg": "积分不足，无法进入该场次"}, to=request.sid)
        return

    room = rooms[rid]
    # 去重，避免重复进入
    room["players"] = [p for p in room["players"] if p["uid"] != uid]
    # 检查房间是否满员
    if len(room["players"]) >= ROOMS[rid]["max"]:
        emit("err", {"msg": "房间已满"}, to=request.sid)
        return

    # 加入房间
    name = data.get("name", f"玩家{uid[:4]}")
    room["players"].append({
        "sid": request.sid,
        "uid": uid,
        "name": name,
        "hand": []
    })
    join_room(rid)
    # 广播房间更新
    emit("room_update", {
        "rid": rid,
        "players": [p["name"] for p in room["players"]],
        "count": len(room["players"])
    }, to=rid)

# 开始游戏
@socketio.on("start_game")
def start_game(rid):
    room = rooms[rid]
    if len(room["players"]) < 2:
        emit("err", {"msg": "至少2人才能开始"}, to=rid)
        return
    if room["started"]:
        return

    # 洗牌发牌
    deck = TILES.copy()
    random.shuffle(deck)
    room["deck"] = deck
    room["started"] = True
    room["current"] = 0

    # 发牌：庄家14张，其他13张
    for i, p in enumerate(room["players"]):
        cnt = 14 if i == 0 else 13
        p["hand"] = [deck.pop() for _ in range(cnt)]
        # 只把自己的手牌发给本人
        emit("your_hand", {"hand": p["hand"]}, to=p["sid"])

    # 广播游戏开始
    emit("game_start", {
        "current": room["players"][0]["name"]
    }, to=rid)

# 出牌逻辑
@socketio.on("discard")
def discard(data):
    rid = data["rid"]
    tile = data["tile"]
    sid = request.sid
    room = rooms[rid]
    if not room["started"]:
        return

    # 校验轮次：只有当前玩家能出牌
    idx = -1
    for i,p in enumerate(room["players"]):
        if p["sid"] == sid:
            idx = i
            break
    if idx != room["current"]:
        emit("err", {"msg": "还没轮到你出牌"}, to=sid)
        return

    # 从手牌中移除打出的牌
    p = room["players"][idx]
    if tile not in p["hand"]:
        return
    p["hand"].remove(tile)
    room["discards"].append({"name": p["name"], "tile": tile})

    # 轮到下家
    room["current"] = (room["current"] + 1) % len(room["players"])
    next_p = room["players"][room["current"]]

    # 给当前玩家摸一张牌
    if room["deck"]:
        new_tile = room["deck"].pop()
        p["hand"].append(new_tile)
        emit("your_hand", {"hand": p["hand"]}, to=sid)

    # 广播出牌信息给房间所有人
    emit("discarded", {
        "player": p["name"],
        "tile": tile,
        "next": next_p["name"],
        "discards": room["discards"][-12:]
    }, to=rid)

# 玩家断开连接
@socketio.on("disconnect")
def on_disconnect():
    for rid in rooms:
        r = rooms[rid]
        for i,p in enumerate(r["players"]):
            if p["sid"] == request.sid:
                r["players"].pop(i)
                emit("room_update", {"players": [x["name"] for x in r["players"]]}, to=rid)
                break

# ======================
# 核心修复：Werkzeug兼容
# ======================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    socketio.run(
        app,
        host="0.0.0.0",
        port=port,
        debug=False,
        allow_unsafe_werkzeug=True  # 彻底解决Werkzeug版本冲突！
    )
