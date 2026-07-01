
# TitanXBots
# File Path: plugins/__init__.py
from aiohttp import web
from .route import routes  # Safe relative import from route.py

async def web_server() -> web.Application:
    """
    Creates the web application context wrapper by pulling 
    route blueprints from the separate route.py file.
    """
    app = web.Application(client_max_size=30000000)
    app.add_routes(routes)
    return app
    
