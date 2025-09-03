from fastapi import FastAPI, HTTPException
from fastapi.responses import Response, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import requests

app = FastAPI()

# 允许跨域请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境建议改为指定域名，如 ["https://abc.domain.com"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 获取头像（方形头像）
@app.get("/mcjava/avatar/{name}")
def get_avatar(name: str):
    """
    通过玩家名获取 Minecraft Java 版头像
    """
    url = f"https://minotar.net/avatar/{name}"
    try:
        r = requests.get(url)
        # 检查响应状态码，确保请求成功
        r.raise_for_status()
        return Response(content=r.content, media_type="image/png")
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch avatar: {e}")

# 获取皮肤（原始皮肤图）
@app.get("/mcjava/skin/{name}")
def get_skin(name: str):
    """
    通过玩家名获取 Minecraft Java 版皮肤
    """
    url = f"https://minotar.net/skin/{name}"
    try:
        r = requests.get(url)
        # 检查响应状态码，确保请求成功
        r.raise_for_status()
        return Response(content=r.content, media_type="image/png")
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch skin: {e}")

# 获取服务器状态
@app.get("/mcjava/server_status/{addr}")
def get_server_status(addr: str):
    """
    通过服务器地址获取 Minecraft Java 版服务器状态
    """
    # 构造 mcstatus.io 的 API URL
    url = f"https://api.mcstatus.io/v2/status/java/{addr}"
    
    try:
        # 发送 GET 请求到 mcstatus.io API
        r = requests.get(url)
        # 检查响应状态码，如果请求失败则抛出异常
        r.raise_for_status()
        
        # 将 mcstatus.io 返回的 JSON 数据直接作为响应返回
        return JSONResponse(content=r.json())
    except requests.exceptions.RequestException as e:
        # 捕获请求异常，并返回一个带有适当HTTP状态码的错误响应
        # 502 Bad Gateway 适合用于转发请求失败的场景
        raise HTTPException(status_code=502, detail=f"Failed to fetch server status from external API: {e}")
    
# 获取 CS:GO 库存（Steam）
@app.get("/cs/inv/{steamid}")
def get_cs_inventory(steamid: str):
    """
    通过 SteamID 获取 CS:GO 库存原始数据
    """
    url = f"https://steamcommunity.com/inventory/{steamid}/730/2?l=schinese"
    try:
        r = requests.get(url)
        r.raise_for_status()
        return JSONResponse(content=r.json())
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Failed to fetch CS:GO inventory: {e}")

# 获取 CS:GO 玩家信息（Steam）
@app.get("/cs/player/{steamid}")
def get_cs_player(steamid: str):
    """
    通过 SteamID 获取玩家信息
    """
    try:
        # 读取 API Key
        with open("steam_api_key.txt", "r", encoding="utf-8") as f:
            api_key = f.read().strip()

        url = (
            f"https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/"
            f"?key={api_key}&steamids={steamid}"
        )

        r = requests.get(url)
        r.raise_for_status()
        return JSONResponse(content=r.json())
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="steam_api_key.txt not found")
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Failed to fetch player info: {e}")

# 获取图片代理
@app.get("/image_proxy")
def image_proxy(url: str):
    """
    通过代理获取图片，解决跨域或图片不稳定问题
    """
    try:
        # 发送 GET 请求到目标 URL
        r = requests.get(url, stream=True)
        # 检查响应状态码
        r.raise_for_status()

        # 获取图片的 Content-Type
        content_type = r.headers.get("Content-Type")

        # 返回图片的二进制内容，并指定 Content-Type
        return Response(content=r.content, media_type=content_type)
    except requests.exceptions.RequestException as e:
        # 捕获请求异常并返回 502 Bad Gateway 错误
        raise HTTPException(status_code=502, detail=f"Failed to proxy image from external URL: {e}")
