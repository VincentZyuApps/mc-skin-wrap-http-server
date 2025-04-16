from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
import httpx

app = FastAPI()

# 允许跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 可以设置为特定域名, 比如 ["https://abc.domain.com"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# minotar.net 基础URL
MINOTAR_URL = "https://minotar.net"

# 获取皮肤
@app.get("/mcjava/skin/{name}")
async def get_skin(name: str):
    skin_url = f"{MINOTAR_URL}/skin/{name}"
    async with httpx.AsyncClient() as client:
        response = await client.get(skin_url)
        return RedirectResponse(url=response.url)

# 获取头像
@app.get("/mcjava/avatar/{name}")
async def get_avatar(name: str):
    avatar_url = f"{MINOTAR_URL}/avatar/{name}"
    async with httpx.AsyncClient() as client:
        response = await client.get(avatar_url)
        return RedirectResponse(url=response.url)
