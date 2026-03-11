from fastapi import FastAPI, HTTPException, APIRouter, Request
from fastapi.responses import Response, JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
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


# ========== ANSI 颜色 ==========
class C:
    """ANSI escape codes for colored terminal output."""
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    DIM     = "\033[2m"
    # 前景色
    RED     = "\033[31m"
    GREEN   = "\033[32m"
    YELLOW  = "\033[33m"
    BLUE    = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN    = "\033[36m"
    WHITE   = "\033[37m"
    GRAY    = "\033[90m"
    # 亮色
    BRIGHT_RED     = "\033[91m"
    BRIGHT_GREEN   = "\033[92m"
    BRIGHT_YELLOW  = "\033[93m"
    BRIGHT_BLUE    = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN    = "\033[96m"


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


class ColoredFormatter(logging.Formatter):
    """自定义日志格式化器，为不同级别添加颜色。"""

    LEVEL_COLORS = {
        TRACE:            C.DIM + C.CYAN,
        logging.DEBUG:    C.CYAN,
        logging.INFO:     C.GREEN,
        logging.WARNING:  C.YELLOW,
        logging.ERROR:    C.RED,
        logging.CRITICAL: C.BRIGHT_RED + C.BOLD,
    }

    def format(self, record: logging.LogRecord) -> str:
        color = self.LEVEL_COLORS.get(record.levelno, C.WHITE)
        ts = self.formatTime(record, self.datefmt)
        level = record.levelname
        msg = record.getMessage()
        return f"{C.GRAY}{ts}{C.RESET} {color}[{level}]{C.RESET} {msg}"


# 配置根 logger
_handler = logging.StreamHandler()
_handler.setFormatter(ColoredFormatter(datefmt="%Y-%m-%d %H:%M:%S"))
logging.root.handlers.clear()
logging.root.addHandler(_handler)
logging.root.setLevel(_level)

logger = logging.getLogger("mc-skin-wrap")
logger.setLevel(_level)

logger.info(f"日志级别: {C.BOLD}{_cfg_level.upper()}{C.RESET}")

# ========== 代理 ==========
proxies: dict | None = None
if config.get("proxy_enabled", False):
    proxy_url = (
        f"{config['proxy_protocol']}://{config['proxy_host']}:{config['proxy_port']}"
    )
    proxies = {"http": proxy_url, "https": proxy_url}
    logger.info(f"🔗 代理已启用: {C.BRIGHT_CYAN}{proxy_url}{C.RESET}")
else:
    logger.info(f"🔗 代理未启用")


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

# 路径归一化：去掉末尾的 /
if root_path and root_path != "/":
    root_path = root_path.rstrip("/")
if not root_path:
    root_path = ""

# 自定义 OpenAPI URL (包含 prefix)
openapi_url = f"{root_path}/openapi.json" if root_path else "/openapi.json"

# 为了完全控制 docs 的 favicon，我们禁用默认 docs，手动挂载
app = FastAPI(
    docs_url=None,       # 禁用默认 docs
    redoc_url=None,      # 禁用默认 redoc
    openapi_url=openapi_url,
)

# 允许跨域请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境建议改为指定域名，如 ["https://abc.domain.com"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ========== 请求日志中间件 ==========
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    elapsed = (time.perf_counter() - start) * 1000

    status = response.status_code
    method = request.method
    path = request.url.path
    client = request.client.host if request.client else "?"

    # 根据状态码上色
    if status < 300:
        sc = f"{C.GREEN}{status}{C.RESET}"
    elif status < 400:
        sc = f"{C.CYAN}{status}{C.RESET}"
    elif status < 500:
        sc = f"{C.YELLOW}{status}{C.RESET}"
    else:
        sc = f"{C.RED}{status}{C.RESET}"

    # 耗时上色
    if elapsed < 100:
        tc = f"{C.GREEN}{elapsed:>8.2f}ms{C.RESET}"
    elif elapsed < 500:
        tc = f"{C.YELLOW}{elapsed:>8.2f}ms{C.RESET}"
    else:
        tc = f"{C.RED}{elapsed:>8.2f}ms{C.RESET}"

    logger.info(
        f"{sc} | {tc} | {C.GRAY}{client:>15}{C.RESET} | "
        f"{C.BRIGHT_CYAN}{method:<7}{C.RESET} {C.WHITE}\"{path}\"{C.RESET}"
    )
    return response


router = APIRouter(prefix=root_path)

# ========== Favicon 处理 ==========
_favicon_cfg = config.get("favicon_path", "")
_favicon_abs_path = ""

logger.debug(f"Favicon 配置值: favicon_path={C.BOLD}'{_favicon_cfg}'{C.RESET}")

if _favicon_cfg:
    _favicon_resolved = _favicon_cfg
    if not os.path.isabs(_favicon_resolved):
        _favicon_resolved = os.path.join(os.path.dirname(os.path.abspath(__file__)), _favicon_resolved)
    
    logger.debug(f"Favicon 解析路径: {_favicon_resolved}")
    logger.debug(f"Favicon 文件存在: {os.path.exists(_favicon_resolved)}")
    
    if os.path.exists(_favicon_resolved):
        _favicon_abs_path = _favicon_resolved
        _fav_size = os.path.getsize(_favicon_abs_path)
        
        # 1. 注册带 prefix 的 favicon (e.g. /fastapi_skin_wrap/favicon.ico)
        @router.get("/favicon.ico", include_in_schema=False)
        def get_prefix_favicon():
            logger.debug(f"🎨 Favicon 请求 (prefix): {root_path}/favicon.ico")
            return FileResponse(
                _favicon_abs_path,
                media_type="image/x-icon",
                headers={"Cache-Control": "public, max-age=86400"},
            )
        
        # 2. 如果 prefix 不为空，也注册一个根路径的 favicon (e.g. /favicon.ico)
        #    这样浏览器直接访问根或者通过 link rel 没带前缀时也能找到
        if root_path and root_path != "/":
            @app.get("/favicon.ico", include_in_schema=False)
            def get_root_favicon():
                logger.debug(f"🎨 Favicon 请求 (root): /favicon.ico")
                return FileResponse(
                    _favicon_abs_path,
                    media_type="image/x-icon",
                    headers={"Cache-Control": "public, max-age=86400"},
                )

        logger.info(
            f"🎨 Favicon 已注册: {C.BRIGHT_CYAN}{_favicon_abs_path}{C.RESET} "
            f"({C.BOLD}{_fav_size}{C.RESET} bytes)"
        )
        logger.info(f"   ├─ {C.GREEN}{root_path}/favicon.ico{C.RESET}")
        if root_path and root_path != "/":
            logger.info(f"   └─ {C.GREEN}/favicon.ico{C.RESET}")
    else:
        logger.warning(f"⚠️  Favicon 文件未找到: {C.YELLOW}{_favicon_resolved}{C.RESET}")
else:
    logger.warning(f"⚠️  Favicon 未配置 (config.json 中 favicon_path 为空或缺失)")

# ========== Swagger UI 路由 ==========
# 手动注册，以便指定自定义 favicon
docs_url_path = f"{root_path}/docs" if root_path else "/docs"

@app.get(docs_url_path, include_in_schema=False)
async def custom_swagger_ui_html():
    favicon_url = f"{root_path}/favicon.ico" if _favicon_abs_path else None
    logger.debug(f"📄 Swagger UI 请求, favicon_url={favicon_url}")
    return get_swagger_ui_html(
        openapi_url=openapi_url,
        title=app.title + " - Swagger UI",
        swagger_favicon_url=favicon_url,
    )

logger.info(f"📄 Swagger UI: {C.BRIGHT_CYAN}{docs_url_path}{C.RESET}")
logger.info(f"📄 OpenAPI JSON: {C.BRIGHT_CYAN}{openapi_url}{C.RESET}")



# 获取头像（方形头像）
@router.get("/mcjava/avatar/{name}")
def get_avatar(name: str):
    """
    通过玩家名获取 Minecraft Java 版头像
    """
    logger.info(f"🖼️  [avatar] 请求头像: name={C.BRIGHT_CYAN}{name}{C.RESET}")
    url = f"https://minotar.net/avatar/{name}"
    try:
        r = proxy_get(url)
        r.raise_for_status()
        logger.info(f"🖼️  [avatar] {C.GREEN}成功{C.RESET}: name={name}, size={C.BOLD}{len(r.content)}{C.RESET} bytes")
        return Response(content=r.content, media_type="image/png")
    except requests.exceptions.RequestException as e:
        logger.error(f"🖼️  [avatar] {C.RED}失败{C.RESET}: name={name}, error={e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch avatar: {e}")


# 获取皮肤（原始皮肤图）
@router.get("/mcjava/skin/{name}")
def get_skin(name: str):
    """
    通过玩家名获取 Minecraft Java 版皮肤
    """
    logger.info(f"👕 [skin] 请求皮肤: name={C.BRIGHT_CYAN}{name}{C.RESET}")
    url = f"https://minotar.net/skin/{name}"
    try:
        r = proxy_get(url)
        r.raise_for_status()
        logger.info(f"👕 [skin] {C.GREEN}成功{C.RESET}: name={name}, size={C.BOLD}{len(r.content)}{C.RESET} bytes")
        return Response(content=r.content, media_type="image/png")
    except requests.exceptions.RequestException as e:
        logger.error(f"👕 [skin] {C.RED}失败{C.RESET}: name={name}, error={e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch skin: {e}")


# 获取服务器状态
@router.get("/mcjava/server_status/{addr}")
def get_server_status(addr: str):
    """
    通过服务器地址获取 Minecraft Java 版服务器状态
    """
    logger.info(f"🌐 [server_status] 请求状态: addr={C.BRIGHT_CYAN}{addr}{C.RESET}")
    url = f"https://api.mcstatus.io/v2/status/java/{addr}"
    
    try:
        r = proxy_get(url)
        r.raise_for_status()
        data = r.json()
        logger.info(f"🌐 [server_status] {C.GREEN}成功{C.RESET}: addr={addr}")
        logger.debug(f"🌐 [server_status] 响应数据: {json.dumps(data, ensure_ascii=False)[:500]}")
        return JSONResponse(content=data)
    except requests.exceptions.RequestException as e:
        logger.error(f"🌐 [server_status] {C.RED}失败{C.RESET}: addr={addr}, error={e}")
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

    logger.info(
        f"🚀 启动参数: host={C.BRIGHT_CYAN}{config['host']}{C.RESET} "
        f"port={C.BRIGHT_CYAN}{config['port']}{C.RESET} "
        f"root_path={C.BRIGHT_CYAN}{config['root_path']}{C.RESET} "
        f"reload={C.BRIGHT_CYAN}{reload_flag}{C.RESET}"
    )
    logger.debug(f"uvicorn log_level={uvicorn_log_level}")
    logger.log(TRACE, f"完整配置: {json.dumps({k: v for k, v in config.items() if not k.startswith('_')}, ensure_ascii=False)}")

    # 注意：我们去掉了 root_path 传参给 uvicorn，因为我们自己在 APIRouter 和 url 中手动处理了 prefix
    # 这样避免 uvicorn 的自动路径剥离与我们手动前缀冲突
    uvicorn.run(
        "main:app",
        host=config["host"],
        port=config["port"],
        # root_path 由应用层自行管理，不传给 uvicorn
        reload=reload_flag,
        log_level=uvicorn_log_level,
    )
