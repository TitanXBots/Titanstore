from aiohttp import web

async def web_server():
    app = web.Application()
    app.router.add('GET', '/', index)
    return app

async def index(request):
    return web.Response(text="🚀 Titan FileStore Bot is up and running successfully!")
    
