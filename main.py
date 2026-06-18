import socketio
from aiohttp import web
from datetime import datetime

sio = socketio.AsyncServer(
    async_mode='aiohttp',
    cors_allowed_origins='*'
)

app = web.Application()
sio.attach(app)

# HTTP страница
async def index(request):
    return web.Response(text="Socket.IO server works!")

app.router.add_get('/', index)

# Список присоединившихся
connected_users = set()
active_users = []

# Непрослушиваемые сервером события
lost_queries = {}

# Счетчик для каждого пользователя
score = {}

# Старт сервера
if len(active_users) == 0:
    print("Сервер пуст")

# Начало сессии
start = 0


# Обработчик события подключения
@sio.event
async def connect(sid, environ):
    print(sid, "connected")
    await sio.emit("message", skip_sid=sid, data={"content": "Пользователь пришел"})
    await sio.emit("message", to=sid, data={"content": "Добро пожаловать на сервер!"})
    connected_users.add(sid)
    score[sid] = 0
    active_users.append(sid)
    global start
    start = datetime.now()
    print(f"Клиент {sid} подключился!")
    if len(active_users) == 1:
        print("Пользователь один")
    if len(active_users) > 1:
        print("Команда в сборе")
    print(active_users)


# Приветствие на событие message
@sio.event
async def message(sid, data=None):
    await sio.emit("message", {"data": "Welcome to the server"}, to=sid)
    await sio.emit("message", {"online": len(active_users)}, to=sid)
    print(sid, "Welcome to the server")
    print(sid, len(active_users))


@sio.event
async def get_users_online(sid, data=None):
    online_count = len(connected_users)
    await sio.emit("users", {"online": online_count}, to=sid)
    print(online_count)


@sio.event
async def chat_message(sid, data):
    print('message', data)
    await sio.emit('reply', data)


@sio.event
async def disconnect(sid):
    print('disconnect', sid)
    connected_users.discard(sid)
    active_users.remove(sid)

    print(f"Клиент {sid} отключился!")
    if len(active_users) == 1:
        print("Пользователь один")
    if len(active_users) == 0:
        print("Сервер пуст")
    print(active_users)
    
    """Время сессии клиента"""
    global start
    print(f"Клиент {sid} отключился, время сессии: {datetime.now() - start}")


@sio.event
async def increase(sid, data=None):
    score[sid] = score.get(sid, 0) + 1
    await sio.emit("score", {"score": score[sid]}, to=sid)


@sio.event
async def decrease(sid, data=None):
    score[sid] = score.get(sid, 0) - 1
    await sio.emit("score", {"score": score[sid]}, to=sid)


@sio.event
async def get_score(sid, data=None):
    current_score = score.get(sid, 0)
    await sio.emit("score", {"score": current_score}, to=sid)
    print("Score", current_score)


@sio.event
async def count_queries(sid, data=None):
    total_lost = sum(lost_queries.values())
    await sio.emit("queries", {"lost": total_lost}, to=sid)
    print("Lost queries:", total_lost)


@sio.on('*')
async def catch_all(event, sid, data):
   # await sio.emit("error", {"message": f"No handler for event {event}"})    # Error вынуждает отключится
    # увеличиваем счётчик для этого события
    lost_queries[event] = lost_queries.get(event, 0) + 1
    print(f"Lost query: {event}")


if __name__ == '__main__':
    web.run_app(app, port=8000)
    
# http://127.0.0.1:8000/