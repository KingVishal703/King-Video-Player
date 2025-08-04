# Don't Remove Credit @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot @Tech_VJ
# Ask Doubt on telegram @KingVJ01

import re, math, logging, secrets, mimetypes
from datetime import datetime
from aiohttp import web
from aiohttp.http_exceptions import BadStatusLine

from info import STREAM_URL, MULTI_CLIENT
from plugins.start import decode, encode
from plugins.database import record_visit, get_count
from TechVJ.bot import multi_clients, work_loads
from TechVJ.server.exceptions import FIleNotFound, InvalidHash
from TechVJ import StartTime, __version__
from TechVJ.util.custom_dl import ByteStreamer
from TechVJ.util.time_format import get_readable_time
from TechVJ.util.render_template import render_page

routes = web.RouteTableDef()

# --- Static Homepage ---
html_content = """..."""  # Same as your animated welcome page (kept for brevity)

@routes.get("/", allow_head=True)
async def root_route_handler(request):
    return web.Response(text=html_content, content_type='text/html')


# --- Route to render video player page using encoded parts ---
@routes.get(r"/{path}/{user_path}/{second}/{third}", allow_head=True)
async def stream_page_handler(request: web.Request):
    try:
        path = request.match_info["path"]
        user_path = request.match_info["user_path"]
        sec = request.match_info["second"]
        th = request.match_info["third"]

        id = int(await decode(path))
        user_id = int(await decode(user_path))
        secid = int(await decode(sec))
        thid = int(await decode(th))

        page = await render_page(id, user_id, secid, thid)
        return web.Response(text=page, content_type='text/html')

    except Exception as e:
        logging.warning(f"Failed to render player page: {e}")
        return web.Response(text=html_content, content_type='text/html')


# --- Route for click-counter / visit tracking ---
@routes.post('/click-counter')
async def handle_click(request):
    try:
        data = await request.json()
        user_id = int(data.get('user_id'))
        today = datetime.now().strftime('%Y-%m-%d')

        user_agent = request.headers.get('User-Agent', '')
        is_chrome = "Chrome" in user_agent or "Google Inc" in user_agent

        if not is_chrome:
            return

        visited_cookie = request.cookies.get('visited')
        if visited_cookie == today:
            return

        response = web.Response(text="Hello, World!")
        response.set_cookie('visited', today, max_age=24*60*60)

        count = get_count(user_id)
        record_visit(user_id, (count + 1) if count else 1)

        return response

    except Exception as e:
        logging.warning(f"Click counter failed: {e}")
        return web.Response(status=400, text="Invalid Request")


# --- Route to resolve short link to stream ---
@routes.get('/{short_link}', allow_head=True)
async def resolve_short_link(request: web.Request):
    short_link = request.match_info["short_link"]
    try:
        original = await decode(short_link)
        if original:
            raise web.HTTPFound(f"{STREAM_URL}link?{original}")
    except Exception as e:
        logging.warning(f"Short link resolution failed: {e}")
    return web.Response(text=html_content, content_type='text/html')


# --- Redirect user to final stream path ---
@routes.get('/link', allow_head=True)
async def visits_redirect(request: web.Request):
    user = request.query.get('u')
    watch = request.query.get('w')
    second = request.query.get('s')
    third = request.query.get('t')

    data = await encode(watch)
    user_id = await encode(user)
    sec_id = await encode(second)
    th_id = await encode(third)

    link = f"{STREAM_URL}{data}/{user_id}/{sec_id}/{th_id}"
    raise web.HTTPFound(link)


# --- Actual video streaming handler ---
@routes.get(r"/dl/{path:\S+}", allow_head=True)
async def download_handler(request: web.Request):
    try:
        path = request.match_info["path"]
        match = re.search(r"^([a-zA-Z0-9_-]{6})(\d+)$", path)
        secure_hash = match.group(1) if match else request.rel_url.query.get("hash")
        id = int(match.group(2)) if match else int(re.search(r"(\d+)", path).group(1))

        return await media_streamer(request, id, secure_hash)

    except InvalidHash as e:
        raise web.HTTPForbidden(text=e.message)
    except FIleNotFound as e:
        raise web.HTTPNotFound(text=e.message)
    except (AttributeError, BadStatusLine, ConnectionResetError):
        return web.Response(status=500, text="Connection Error")
    except Exception as e:
        logging.critical(f"Unhandled exception: {e}")
        return web.Response(status=500, text=str(e))


# --- Cache & Stream logic ---
class_cache = {}

async def media_streamer(request: web.Request, id: int, secure_hash: str):
    range_header = request.headers.get("Range", None)

    index = min(work_loads, key=work_loads.get)
    client = multi_clients[index]

    if client not in class_cache:
        class_cache[client] = ByteStreamer(client)

    tg = class_cache[client]
    file_id = await tg.get_file_properties(id)
    file_size = file_id.file_size

    # Handle byte ranges
    if range_header:
        from_bytes, until_bytes = range_header.replace("bytes=", "").split("-")
        from_bytes = int(from_bytes)
        until_bytes = int(until_bytes) if until_bytes else file_size - 1
    else:
        from_bytes = request.http_range.start or 0
        until_bytes = (request.http_range.stop or file_size) - 1

    if (until_bytes > file_size) or (from_bytes < 0) or (until_bytes < from_bytes):
        return web.Response(
            status=416,
            body="416: Range not satisfiable",
            headers={"Content-Range": f"bytes */{file_size}"}
        )

    # Prepare chunks
    chunk_size = 1024 * 1024
    until_bytes = min(until_bytes, file_size - 1)
    offset = from_bytes - (from_bytes % chunk_size)
    first_cut = from_bytes - offset
    last_cut = until_bytes % chunk_size + 1
    part_count = math.ceil(until_bytes / chunk_size) - math.floor(offset / chunk_size)
    req_length = until_bytes - from_bytes + 1

    body = tg.yield_file(file_id, index, offset, first_cut, last_cut, part_count, chunk_size)

    # Prepare headers
    mime_type = file_id.mime_type or "application/octet-stream"
    file_name = file_id.file_name or f"{secrets.token_hex(2)}.unknown"
    if not file_name and mime_type:
        try:
            ext = mime_type.split('/')[1]
            file_name = f"{secrets.token_hex(2)}.{ext}"
        except IndexError:
            pass

    return web.Response(
        status=206 if range_header else 200,
        body=body,
        headers={
            "Content-Type": mime_type,
            "Content-Range": f"bytes {from_bytes}-{until_bytes}/{file_size}",
            "Content-Length": str(req_length),
            "Content-Disposition": f'attachment; filename="{file_name}"',
            "Accept-Ranges": "bytes",
        }
    )
