# Don't Remove Credit @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot @Tech_VJ
# Ask Doubt on telegram @KingVJ01

"""
This module initializes the aiohttp web server
used for file streaming or API endpoints.
"""

from aiohttp import web
from .route import routes

async def web_server():
    # Max client request size = ~30 MB
    web_app = web.Application(client_max_size=30_000_000)
    web_app.add_routes(routes)
    return web_app
