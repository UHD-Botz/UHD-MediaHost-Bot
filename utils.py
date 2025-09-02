from aiohttp import web
import time
from config import Config

routes = web.RouteTableDef()

START_TIME = time.time()

@routes.get("/", allow_head=True)
async def root_route_handler(request):
    uptime = round(time.time() - START_TIME)
    return web.json_response({
        "status": "running",
        "bot": "UHD-MediaHost-Bot",
        "uptime_seconds": uptime,
        "admin": Config.ADMIN if Config.ADMIN else "Not Set"
    })


async def web_server():
    web_app = web.Application(client_max_size=30000000)
    web_app.add_routes(routes)
    return web_app
