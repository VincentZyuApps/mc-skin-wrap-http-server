from fastapi import FastAPI, HTTPException, APIRouter
from fastapi.responses import Response, JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import requests
import json
import sys
import os
import logging
import time
import uvicorn

BANNER = r"""
    __  _________    _____ __ __ _____   __    _       ______  ___    ____ 
   /  |/  / ____/   / ___// //_//  _/ | / /   | |     / / __ \/   |  / __ \
  / /|_/ / /  ______\__ \/ ,<   / //  |/ /____| | /| / / /_/ / /| | / /_/ /
 / /  / / /__/_____/__/ / /| |_/ // /|  /_____/ |/ |/ / _, _/ ___ |/ ____/ 
/_/  /_/\____/    /____/_/ |_/___/_/ |_/      |__/|__/_/ |_/_/  |_/_/      

    ______  __      _________   ______________    ____  ____
   / __ \ \/ /     / ____/   | / ___/_  __/   |  / __ \/  _/
  / /_/ /\  /_____/ /_  / /| | \__ \ / / / /| | / /_/ // /
 / ____/ / /_____/ __/ / ___ |___/ // / / ___ |/ ____// /
/_/     /_/     /_/   /_/  |_/____//_/ /_/  |_/_/   /___/
"""

def print_banner():
    print(BANNER)

# ========== 命令行参数 early exit ==========
if "--help" in sys.argv or "-h" in sys.argv:
    print(BANNER)
    print("用法: python main.py [选项]")
    print()
    print("选项:")
    print("  -c, --config <path>  配置文件路径 (默认: config.json)")
    print("  --reload             启用热重载 (uvicorn)")
    print("  -h, --help           显示此帮助信息")
    sys.exit(0)

# ========== 加载配置 ==========
def load_config() -> dict:
    config_path = "config.json"

    # 支持 -c / --config 两种写法
    for flag in ("-c", "--config"):
        if flag in sys.argv:
            try:
                config_path = sys.argv[sys.argv.index(flag) + 1]
            except IndexError:
                print(f"[ERROR] {flag} 参数后必须指定配置文件路径")
                sys.exit(1)
            break
    
    # 如果没通过参数指定，则尝试读取同目录下的 config.json
    if not os.path.isabs(config_path):
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), config_path)

    if not os.path.exists(config_path):
        print(f"[ERROR] 找不到配置文件: {config_path}")
        print(f"        请确保配置文件存在，或使用 -c 参数指定路径")
        sys.exit(1)
        
    print(f"[INFO] 加载配置文件: {config_path}")
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)

config = load_config()

# ========== 日志 ==========
# 自定义 TRACE 级别 (比 DEBUG=10 更低)
TRACE = 5
logging.addLevelName(TRACE, "TRACE")

LOG_LEVEL_MAP = {
    "trace":  TRACE,
    "debug":  logging.DEBUG,
    "info":   logging.INFO,
    "warn":   logging.WARNING,
    "error":  logging.ERROR,
    "silent": logging.CRITICAL + 10,  # 高于所有级别，静默
}

_cfg_level = config.get("log_level", "info").lower()
_level = LOG_LEVEL_MAP.get(_cfg_level, logging.INFO)

logging.basicConfig(
    level=_level,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("mc-skin-wrap")
logger.setLevel(_level)

logger.info(f"日志级别: {_cfg_level.upper()}")

# ========== 代理 ==========
proxies: dict | None = None
if config.get("proxy_enabled", False):
    proxy_url = (
        f"{config['proxy_protocol']}://{config['proxy_host']}:{config['proxy_port']}"
    )
    proxies = {"http": proxy_url, "https": proxy_url}
    logger.info(f"代理已启用: {proxy_url}")
else:
    logger.info("代理未启用")


def proxy_get(url: str, max_retries: int = 2, **kwargs) -> requests.Response:
    """统一的 GET 请求，自动带上代理配置。失败时自动重试，SSL 错误时尝试不走代理兜底。"""
    logger.log(TRACE, f"proxy_get() 开始请求: {url}")
    logger.debug(f"请求参数: proxies={proxies}, timeout=10, kwargs={kwargs}")

    last_exception: Exception | None = None

    for attempt in range(1, max_retries + 1):
        start = time.perf_counter()
        try:
            r = requests.get(url, proxies=proxies, timeout=10, **kwargs)
            elapsed = (time.perf_counter() - start) * 1000
            logger.debug(f"响应状态码: {r.status_code}, 耗时: {elapsed:.1f}ms, 大小: {len(r.content)} bytes")
            logger.log(TRACE, f"响应头: {dict(r.headers)}")
            return r
        except Exception as e:
            elapsed = (time.perf_counter() - start) * 1000
            logger.warning(f"请求失败 (第{attempt}/{max_retries}次): {url}, 耗时: {elapsed:.1f}ms, 异常: {type(e).__name__}: {e}")
            last_exception = e

    # 所有重试都失败了，如果开了代理，尝试不走代理兜底
    if proxies:
        logger.warning(f"代理请求全部失败，尝试直连兜底: {url}")
        start = time.perf_counter()
        try:
            r = requests.get(url, timeout=10, **kwargs)
            elapsed = (time.perf_counter() - start) * 1000
            logger.info(f"直连兜底成功: {r.status_code}, 耗时: {elapsed:.1f}ms, 大小: {len(r.content)} bytes")
            return r
        except Exception as e:
            elapsed = (time.perf_counter() - start) * 1000
            logger.error(f"直连兜底也失败: {url}, 耗时: {elapsed:.1f}ms, 异常: {type(e).__name__}: {e}")
            # 抛出原始代理错误，更有参考价值
            raise last_exception  # type: ignore

    logger.error(f"请求最终失败: {url}")
    raise last_exception  # type: ignore


# ========== 路由 ==========
# 使用 APIRouter 添加真实路由前缀
root_path = config.get("root_path", "")

# FastAPI 内置的 /docs 和 /redoc 也需要带前缀
app = FastAPI(
    docs_url=f"{root_path}/docs" if root_path else "/docs",
    redoc_url=f"{root_path}/redoc" if root_path else "/redoc",
    openapi_url=f"{root_path}/openapi.json" if root_path else "/openapi.json",
)

# 允许跨域请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境建议改为指定域名，如 ["https://abc.domain.com"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

router = APIRouter(prefix=root_path)

# Favicon
_favicon_path = config.get("favicon_path", "")
if _favicon_path:
    if not os.path.isabs(_favicon_path):
        _favicon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), _favicon_path)
    if os.path.exists(_favicon_path):
        @router.get("/favicon.ico", include_in_schema=False)
        def get_favicon():
            return FileResponse(_favicon_path, media_type="image/x-icon")
        logger.info(f"Favicon: {_favicon_path}")
    else:
        logger.warning(f"Favicon 文件未找到: {_favicon_path}")


# 获取头像（方形头像）
@router.get("/mcjava/avatar/{name}")
def get_avatar(name: str):
    """
    通过玩家名获取 Minecraft Java 版头像
    """
    logger.info(f"[avatar] 请求头像: name={name}")
    url = f"https://minotar.net/avatar/{name}"
    try:
        r = proxy_get(url)
        r.raise_for_status()
        logger.info(f"[avatar] 成功获取头像: name={name}, size={len(r.content)} bytes")
        return Response(content=r.content, media_type="image/png")
    except requests.exceptions.RequestException as e:
        logger.error(f"[avatar] 获取头像失败: name={name}, error={e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch avatar: {e}")


# 获取皮肤（原始皮肤图）
@router.get("/mcjava/skin/{name}")
def get_skin(name: str):
    """
    通过玩家名获取 Minecraft Java 版皮肤
    """
    logger.info(f"[skin] 请求皮肤: name={name}")
    url = f"https://minotar.net/skin/{name}"
    try:
        r = proxy_get(url)
        r.raise_for_status()
        logger.info(f"[skin] 成功获取皮肤: name={name}, size={len(r.content)} bytes")
        return Response(content=r.content, media_type="image/png")
    except requests.exceptions.RequestException as e:
        logger.error(f"[skin] 获取皮肤失败: name={name}, error={e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch skin: {e}")


# 获取服务器状态
@router.get("/mcjava/server_status/{addr}")
def get_server_status(addr: str):
    """
    通过服务器地址获取 Minecraft Java 版服务器状态
    """
    # 构造 mcstatus.io 的 API URL
    logger.info(f"[server_status] 请求服务器状态: addr={addr}")
    url = f"https://api.mcstatus.io/v2/status/java/{addr}"
    
    try:
        r = proxy_get(url)
        r.raise_for_status()
        data = r.json()
        logger.info(f"[server_status] 成功获取状态: addr={addr}")
        logger.debug(f"[server_status] 响应数据: {json.dumps(data, ensure_ascii=False)[:500]}")
        return JSONResponse(content=data)
    except requests.exceptions.RequestException as e:
        logger.error(f"[server_status] 获取服务器状态失败: addr={addr}, error={e}")
        raise HTTPException(status_code=502, detail=f"Failed to fetch server status from external API: {e}")


# 注册路由到 app
app.include_router(router)


# ========== 启动入口 ==========
if __name__ == "__main__":
    print_banner()
    reload_flag = "--reload" in sys.argv

    # uvicorn 的日志级别映射
    uvicorn_log_level = _cfg_level if _cfg_level != "silent" else "critical"
    # uvicorn 不认识 trace，降为 debug
    if uvicorn_log_level == "trace":
        uvicorn_log_level = "debug"

    logger.info(f"host={config['host']} port={config['port']} root_path={config['root_path']} reload={reload_flag}")
    logger.debug(f"uvicorn log_level={uvicorn_log_level}")
    logger.log(TRACE, f"完整配置: {json.dumps({k: v for k, v in config.items() if not k.startswith('_')}, ensure_ascii=False)}")

    uvicorn.run(
        "main:app",
        host=config["host"],
        port=config["port"],
        root_path=config["root_path"],
        reload=reload_flag,
        log_level=uvicorn_log_level,
    )
