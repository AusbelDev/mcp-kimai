from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import httpx, os

BRIDGE = os.environ.get("BRIDGE_URL", "http://127.0.0.1:11435")

app = FastAPI()
# Optional CORS (kept permissive; you can restrict origins later)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

# Serve static UI
app.mount("/static", StaticFiles(directory="/app/ui"), name="static")

@app.get("/", response_class=HTMLResponse)
async def root():
    return FileResponse("/app/ui/index.html")

# Proxy all /api/* to the bridge
@app.api_route("/api/{path:path}", methods=["GET","POST","PUT","PATCH","DELETE","OPTIONS"])
async def proxy(path: str, request: Request):
    url = f"{BRIDGE}/api/{path}"
    headers = dict(request.headers)
    # Drop host header so httpx sets it properly
    headers.pop("host", None)
    content = await request.body()

    async with httpx.AsyncClient(timeout=None) as client:
      resp = await client.request(
        request.method, url, headers=headers, content=content, params=dict(request.query_params)
      )
    return Response(content=resp.content, status_code=resp.status_code, headers=dict(resp.headers))
