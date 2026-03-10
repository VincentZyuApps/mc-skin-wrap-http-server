#!/usr/bin/env python3
"""
本地开发辅助脚本 (Python 版)
- 输出 cd + 运行命令 + curl 测试命令 + 浏览器 URL

用法:
    python py/local_dev.py                          # 使用默认值
    python py/local_dev.py --host 0.0.0.0           # 指定 host
    python py/local_dev.py --port 8080              # 指定 port
    python py/local_dev.py --root-path /api         # 指定 root_path
"""

import os
import platform
import argparse

# ========== ANSI 颜色 ==========
class Color:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[31m"
    YELLOW = "\033[33m"
    CYAN = "\033[36m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_CYAN = "\033[96m"

def log_info(msg):
    print(f"{Color.CYAN}ℹ️  [INFO]{Color.RESET} {msg}")

# ========== 配置 ==========
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY_DIR = os.path.join(PROJECT_ROOT, "py")

# 默认值
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 58418
DEFAULT_ROOT_PATH = "/fastapi_skin_wrap"


def is_windows() -> bool:
    return platform.system().lower() == "windows"


def generate_commands(host: str, port: int, root_path: str):
    """生成各种命令并输出"""
    py_path = PY_DIR.replace("\\", "/")
    
    # ========== 运行命令 ==========
    print(f"\n{Color.BRIGHT_CYAN}{'='*60}{Color.RESET}")
    print(f"{Color.BOLD}📋 Run Commands{Color.RESET}")
    print(f"{Color.BRIGHT_CYAN}{'='*60}{Color.RESET}")
    
    print(f"\n{Color.YELLOW}# cd to directory:{Color.RESET}")
    print(f"cd {py_path}")
    
    print(f"\n{Color.YELLOW}# run server (production):{Color.RESET}")
    print("python main.py")
    
    print(f"\n{Color.YELLOW}# run server (dev with hot-reload):{Color.RESET}")
    print("python main.py --reload")
    
    print(f"\n{Color.YELLOW}# one-liner:{Color.RESET}")
    if is_windows():
        print(f"cd {py_path}; python main.py")
    else:
        print(f"cd {py_path} && python main.py")
    
    # ========== curl 命令 ==========
    print(f"\n{Color.BRIGHT_CYAN}{'='*60}{Color.RESET}")
    print(f"{Color.BOLD}🔗 Curl Commands{Color.RESET}")
    print(f"{Color.BRIGHT_CYAN}{'='*60}{Color.RESET}")
    
    if is_windows():
        # PowerShell 语法
        print(f"\n{Color.YELLOW}# PowerShell:{Color.RESET}")
        print(f'$H = "{host}"')
        print(f'$P = {port}')
        print(f'$R = "{root_path}"')
        print()
        print('# Avatar')
        print('curl "http://${H}:${P}${R}/mcjava/avatar/VincentZyu" -o avatar.png')
        print('# Skin')
        print('curl "http://${H}:${P}${R}/mcjava/skin/VincentZyu" -o skin.png')
        print('# Server Status')
        print('curl "http://${H}:${P}${R}/mcjava/server_status/mc.hypixel.net"')
        print('# Swagger Docs (FastAPI 自带)')
        print('curl "http://${H}:${P}${R}/docs"')
    else:
        # Bash 语法
        print(f"\n{Color.YELLOW}# Bash:{Color.RESET}")
        print(f'H="{host}"')
        print(f'P={port}')
        print(f'R="{root_path}"')
        print()
        print('# Avatar')
        print('curl "http://${H}:${P}${R}/mcjava/avatar/VincentZyu" -o avatar.png')
        print('# Skin')
        print('curl "http://${H}:${P}${R}/mcjava/skin/VincentZyu" -o skin.png')
        print('# Server Status')
        print('curl "http://${H}:${P}${R}/mcjava/server_status/mc.hypixel.net"')
        print('# Swagger Docs (FastAPI 自带)')
        print('curl "http://${H}:${P}${R}/docs"')
    
    # ========== 浏览器 URL ==========
    print(f"\n{Color.BRIGHT_CYAN}{'='*60}{Color.RESET}")
    print(f"{Color.BOLD}🌐 Browser URLs{Color.RESET}")
    print(f"{Color.BRIGHT_CYAN}{'='*60}{Color.RESET}")
    
    if is_windows():
        print(f"\n{Color.YELLOW}# PowerShell - 生成浏览器 URL:{Color.RESET}")
    else:
        print(f"\n{Color.YELLOW}# Bash - 生成浏览器 URL:{Color.RESET}")
    
    print('echo "http://${H}:${P}${R}/mcjava/avatar/VincentZyu"      # Avatar')
    print('echo "http://${H}:${P}${R}/mcjava/skin/VincentZyu"        # Skin')
    print('echo "http://${H}:${P}${R}/mcjava/server_status/mc.hypixel.net"  # Server Status')
    print('echo "http://${H}:${P}${R}/docs"                          # Swagger Docs')
    
    print(f"\n{Color.BRIGHT_CYAN}{'='*60}{Color.RESET}\n")


def main():
    parser = argparse.ArgumentParser(description="Local development helper for mc-skin-wrap Python version")
    parser.add_argument("--host", default=DEFAULT_HOST, help=f"Server host (default: {DEFAULT_HOST})")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help=f"Server port (default: {DEFAULT_PORT})")
    parser.add_argument("--root-path", default=DEFAULT_ROOT_PATH, help=f"Root path prefix (default: {DEFAULT_ROOT_PATH})")
    args = parser.parse_args()
    
    host = args.host
    port = args.port
    root_path = args.root_path
    
    print(f"\n{Color.BRIGHT_CYAN}{'='*60}{Color.RESET}")
    print(f"{Color.BOLD}🐍 MC Skin Wrap Local Dev (Python){Color.RESET}")
    print(f"{Color.BRIGHT_CYAN}{'='*60}{Color.RESET}")
    log_info(f"Host:      {Color.YELLOW}{host}{Color.RESET}")
    log_info(f"Port:      {Color.YELLOW}{port}{Color.RESET}")
    log_info(f"Root Path: {Color.YELLOW}{root_path}{Color.RESET}")
    
    generate_commands(host, port, root_path)


if __name__ == "__main__":
    main()
