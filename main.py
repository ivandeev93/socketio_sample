import socketio
from aiohttp import web

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

# Обработчик события подключения
@sio.event
async def connect(sid, environ):
    print('connect', sid)
    connected_users.add(sid)


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


@sio.on('*')
async def catch_all(event, sid, data):
    await sio.emit("error", {"message": f"No handler for event {event}"})


if __name__ == '__main__':
    web.run_app(app, port=8000)
    
# http://127.0.0.1:8000/