from flask import Flask, render_template
from flask_socketio import SocketIO, emit, join_room
import random
from collections import defaultdict

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mahjong'
socketio = SocketIO(app, cors_allowed_origins="*")

# 四个场次：积分够了才能进
ROOMS = {
    "1": {"name":"新手场","cost":100},
    "2": {"name":"中级场","cost":500},
    "3": {"name":"高手场","cost":2000},
    "4": {"name":"大师场","cost":10000}
}

# 积分
users = defaultdict(int)

# 房间
rooms = defaultdict(lambda: {
    "players": [], "deck": [], "discards": [], "current":0, "started":False
})

# 麻将牌
TILES = []
for t in ["万","条","筒"]:
    for n in range(1,10):
        TILES += [f"{n}{t}"]*4
for z in ["东","南","西","北","中","发","白"]:
    TILES += [z]*4

# 页面
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/hall")
def hall():
    return render_template("hall.html", rooms=ROOMS)

@app.route("/room/<rid>")
def room(rid):
    return render_template("game.html", rid=rid, room=ROOMS[rid])

# 登录
@socketio.on("login")
def login(data):
    uid = data["uid"]
    if users[uid] == 0:
        users[uid] = 1000  # 新用户送1000积分
    emit("login_ok", {"score": users[uid]})

# 进入房间（检查积分）
@socketio.on("enter")
def enter(data):
    rid = data["rid"]
    uid = data["uid"]
    if users[uid] < ROOMS[rid]["cost"]:
        emit("err", "积分不够！")
        return
    room = rooms[rid]
    room["players"] = [p for p in room["players"] if p["uid"] != uid]
    room["players"].append({"uid":uid, "sid":request.sid})
    join_room(rid)
    emit("entered", {"count":len(room["players"])}, to=rid)

# 开始游戏
@socketio.on("start")
def start(rid):
    room = rooms[rid]
    if len(room["players"]) < 2:
        emit("err","至少2人开始")
        return
    deck = TILES.copy()
    random.shuffle(deck)
    room["deck"] = deck
    room["started"] = True
    for i,p in enumerate(room["players"]):
        hand = [deck.pop() for _ in range(14 if i==0 else 13)]
        emit("hand", hand, to=p["sid"])
    emit("started", to=rid)

# 出牌
@socketio.on("discard")
def discard(data):
    rid = data["rid"]
    tile = data["tile"]
    room = rooms[rid]
    room["discards"].append(tile)
    emit("show", {"tile":tile, "discards":room["discards"][-10:]}, to=rid)

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=8080)
