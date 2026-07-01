
# TitanXBots
from aiohttp import web

async def web_server():
    """
    Creates and returns the aiohttp Web Application instance.
    This seamlessly couples with the AppRunner lifecycle in bot.py.
    """
    app = web.Application()
    routes = web.RouteTableDef()

    @routes.get("/", allow_head=True)
    async def root_route_handler(request):
        return web.json_response({
            "status": "ok",
            "bot": "TitanXBots",
            "message": "Server is running smoothly"
        })

    # Register the route table routes into the web app context
    app.add_routes(routes)
    return app
    
