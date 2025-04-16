from fastapi import FastAPI
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
import requests

app = FastAPI()

# 允许跨域请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 或改成指定域名，如 ["https://abc.domain.com"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 获取头像（方形头像）
@app.get("/mcjava/avatar/{name}")
def get_avatar(name: str):
    url = f"https://minotar.net/avatar/{name}"
    r = requests.get(url)
    return Response(content=r.content, media_type="image/png")

# 获取皮肤（原始皮肤图）
@app.get("/mcjava/skin/{name}")
def get_skin(name: str):
    url = f"https://minotar.net/skin/{name}"
    r = requests.get(url)
    return Response(content=r.content, media_type="image/png")
