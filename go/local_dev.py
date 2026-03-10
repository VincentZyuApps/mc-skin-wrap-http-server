#!/usr/bin/env python3
"""
本地开发辅助脚本
- 更新 dev.go.md 中的版本号和环境变量
- 解压当前架构的压缩包
- 输出 cd + 运行命令 + curl 测试命令 + 浏览器 URL

用法:
    python go/local_dev.py                          # 使用默认值
    python go/local_dev.py --host 0.0.0.0           # 指定 host
    python go/local_dev.py --port 8080              # 指定 port
    python go/local_dev.py --root-path /api         # 指定 root_path
    python go/local_dev.py --arch arm64             # 指定架构
"""

import os
import sys
import re
import platform
import subprocess
import shutil
import argparse

# ========== ANSI 颜色 ==========
class Color:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_MAGENTA = "\033[95m"

def log_info(msg):
    print(f"{Color.CYAN}ℹ️  [INFO]{Color.RESET} {msg}")

def log_ok(msg):
    print(f"{Color.BRIGHT_GREEN}✅ [OK]{Color.RESET} {msg}")

def log_doc(msg):
    print(f"{Color.BRIGHT_MAGENTA}📝 [DOC]{Color.RESET} {msg}")

def log_unzip(msg):
    print(f"{Color.YELLOW}📦 [UNZIP]{Color.RESET} {msg}")

def log_error(msg):
    print(f"{Color.RED}❌ [ERROR]{Color.RESET} {msg}")

# ========== 配置 ==========
APP_NAME = "mc-skin-wrap-go"
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST_DIR = os.path.join(PROJECT_ROOT, "dist")
SOURCE_DIR = "go"

# 默认值
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 60311
DEFAULT_ROOT_PATH = "/gin_skin_wrap"


def get_version_from_go() -> str:
    """从 main.go 提取版本号"""
    main_go = os.path.join(PROJECT_ROOT, SOURCE_DIR, "main.go")
    if not os.path.exists(main_go):
        return "0.0.1"
    try:
        with open(main_go, "r", encoding="utf-8") as f:
            for line in f:
                if 'const Version =' in line:
                    return line.split('"')[1]
    except Exception:
        pass
    return "0.0.1"


def get_current_platform() -> tuple[str, str]:
    """获取当前系统的 GOOS 和 GOARCH"""
    system = platform.system().lower()
    machine = platform.machine().lower()
    
    goos_map = {"windows": "windows", "linux": "linux", "darwin": "darwin"}
    goos = goos_map.get(system, system)
    
    goarch_map = {
        "x86_64": "amd64", "amd64": "amd64",
        "arm64": "arm64", "aarch64": "arm64"
    }
    goarch = goarch_map.get(machine, "amd64")
    
    return goos, goarch


def update_dev_doc(version: str, host: str, port: int, root_path: str):
    """更新 doc/dev.go.md 中的版本号和环境变量"""
    doc_path = os.path.join(PROJECT_ROOT, "doc", "dev.go.md")
    
    if not os.path.exists(doc_path):
        log_error(f"dev.go.md not found: {doc_path}")
        return
    
    with open(doc_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    original = content
    
    # 1. 更新版本号
    pattern = r"mc-skin-wrap_[^\s_]+_((windows|linux|darwin)_(amd64|arm64))"
    content = re.sub(pattern, f"mc-skin-wrap_{version}_\\1", content)
    
    # 2. 更新 PowerShell 环境变量 ($H, $P, $R)
    content = re.sub(r'\$H\s*=\s*"[^"]*"', f'$H = "{host}"', content)
    content = re.sub(r'\$P\s*=\s*\d+', f'$P = {port}', content)
    content = re.sub(r'\$R\s*=\s*"[^"]*"', f'$R = "{root_path}"', content)
    
    # 3. 更新 Bash 环境变量 (H=, P=, R=)
    content = re.sub(r'^H="[^"]*"', f'H="{host}"', content, flags=re.MULTILINE)
    content = re.sub(r'^P=\d+', f'P={port}', content, flags=re.MULTILINE)
    content = re.sub(r'^R="[^"]*"', f'R="{root_path}"', content, flags=re.MULTILINE)
    
    if content != original:
        with open(doc_path, "w", encoding="utf-8") as f:
            f.write(content)
        log_doc(f"Updated dev.go.md")
    else:
        log_info("dev.go.md unchanged (values identical)")
    
    # 无论是否更新都显示当前配置
    log_info(f"  version:   {Color.BRIGHT_GREEN}{version}{Color.RESET}")
    log_info(f"  host:      {Color.YELLOW}{host}{Color.RESET}")
    log_info(f"  port:      {Color.YELLOW}{port}{Color.RESET}")
    log_info(f"  root_path: {Color.YELLOW}{root_path}{Color.RESET}")


def extract_archive(version: str, goos: str, goarch: str, clear: bool = False) -> str | None:
    """解压对应平台的压缩包，返回解压后的目录路径"""
    dir_name = f"mc-skin-wrap_{version}_{goos}_{goarch}"
    extract_path = os.path.join(DIST_DIR, dir_name)
    
    if os.path.exists(extract_path):
        if clear:
            log_info(f"Cleaning existing: {dir_name}")
            shutil.rmtree(extract_path)
        else:
            log_info(f"Using existing: {dir_name} (use --clear to re-extract)")
            return extract_path
    
    if goos == "windows":
        archive_path = os.path.join(DIST_DIR, f"{dir_name}.zip")
    else:
        archive_path = os.path.join(DIST_DIR, f"{dir_name}.tar.gz")
    
    if not os.path.exists(archive_path):
        log_error(f"Archive not found: {archive_path}")
        log_info("Please run build.py first")
        return None
    
    log_unzip(f"Extracting: {os.path.basename(archive_path)}")
    
    try:
        if goos == "windows":
            subprocess.run(["7z", "x", archive_path, f"-o{DIST_DIR}", "-y"],
                           check=True, capture_output=True)
        else:
            subprocess.run(["7z", "x", archive_path, f"-o{DIST_DIR}", "-y"],
                           check=True, capture_output=True)
            tar_path = archive_path.replace(".tar.gz", ".tar")
            subprocess.run(["7z", "x", tar_path, f"-o{DIST_DIR}", "-y"],
                           check=True, capture_output=True)
            os.remove(tar_path)
        
        log_ok(f"Extracted to: {extract_path}")
        return extract_path
    except subprocess.CalledProcessError as e:
        log_error(f"7z extraction failed: {e}")
        return None
    except FileNotFoundError:
        log_error("7z not found in PATH. Please install 7-Zip.")
        return None


def generate_commands(extract_path: str, goos: str, host: str, port: int, root_path: str):
    """生成各种命令并输出"""
    path_slash = extract_path.replace("\\", "/")
    binary = f"./{APP_NAME}.exe" if goos == "windows" else f"./{APP_NAME}"
    
    # ========== 运行命令 ==========
    print(f"\n{Color.BRIGHT_CYAN}{'='*60}{Color.RESET}")
    print(f"{Color.BOLD}📋 Run Commands{Color.RESET}")
    print(f"{Color.BRIGHT_CYAN}{'='*60}{Color.RESET}")
    
    print(f"\n{Color.YELLOW}# cd to directory:{Color.RESET}")
    print(f"cd {path_slash}")
    
    print(f"\n{Color.YELLOW}# run server:{Color.RESET}")
    print(f"{binary}")
    
    print(f"\n{Color.YELLOW}# one-liner:{Color.RESET}")
    if goos == "windows":
        print(f"cd {path_slash}; {binary}")
    else:
        print(f"cd {path_slash} && {binary}")
    
    # ========== curl 命令 ==========
    print(f"\n{Color.BRIGHT_CYAN}{'='*60}{Color.RESET}")
    print(f"{Color.BOLD}🔗 Curl Commands{Color.RESET}")
    print(f"{Color.BRIGHT_CYAN}{'='*60}{Color.RESET}")
    
    if goos == "windows":
        # PowerShell 语法
        print(f"\n{Color.YELLOW}# PowerShell:{Color.RESET}")
        print(f'$H = "{host}"')
        print(f'$P = {port}')
        print(f'$R = "{root_path}"')
        print()
        print(f'# Avatar')
        print(f'curl "http://${{H}}:${{P}}${{R}}/mcjava/avatar/VincentZyu" -o avatar.png')
        print(f'# Skin')
        print(f'curl "http://${{H}}:${{P}}${{R}}/mcjava/skin/VincentZyu" -o skin.png')
        print(f'# Server Status')
        print(f'curl "http://${{H}}:${{P}}${{R}}/mcjava/server_status/mc.hypixel.net"')
        print(f'# Swagger Docs')
        print(f'curl "http://${{H}}:${{P}}${{R}}/docs/"')
    else:
        # Bash 语法
        print(f"\n{Color.YELLOW}# Bash:{Color.RESET}")
        print(f'H="{host}"')
        print(f'P={port}')
        print(f'R="{root_path}"')
        print()
        print(f'# Avatar')
        print(f'curl "http://${{H}}:${{P}}${{R}}/mcjava/avatar/VincentZyu" -o avatar.png')
        print(f'# Skin')
        print(f'curl "http://${{H}}:${{P}}${{R}}/mcjava/skin/VincentZyu" -o skin.png')
        print(f'# Server Status')
        print(f'curl "http://${{H}}:${{P}}${{R}}/mcjava/server_status/mc.hypixel.net"')
        print(f'# Swagger Docs')
        print(f'curl "http://${{H}}:${{P}}${{R}}/docs/"')
    
    # ========== 浏览器 URL ==========
    print(f"\n{Color.BRIGHT_CYAN}{'='*60}{Color.RESET}")
    print(f"{Color.BOLD}🌐 Browser URLs{Color.RESET}")
    print(f"{Color.BRIGHT_CYAN}{'='*60}{Color.RESET}")
    
    if goos == "windows":
        # PowerShell 语法
        print(f"\n{Color.YELLOW}# PowerShell - 生成浏览器 URL:{Color.RESET}")
        print('echo "http://${H}:${P}${R}/mcjava/avatar/VincentZyu"      # Avatar')
        print('echo "http://${H}:${P}${R}/mcjava/skin/VincentZyu"        # Skin')
        print('echo "http://${H}:${P}${R}/mcjava/server_status/mc.hypixel.net"  # Server Status')
        print('echo "http://${H}:${P}${R}/docs/"                         # Swagger Docs')
    else:
        # Bash 语法
        print(f"\n{Color.YELLOW}# Bash - 生成浏览器 URL:{Color.RESET}")
        print('echo "http://${H}:${P}${R}/mcjava/avatar/VincentZyu"      # Avatar')
        print('echo "http://${H}:${P}${R}/mcjava/skin/VincentZyu"        # Skin')
        print('echo "http://${H}:${P}${R}/mcjava/server_status/mc.hypixel.net"  # Server Status')
        print('echo "http://${H}:${P}${R}/docs/"                         # Swagger Docs')
    
    print(f"\n{Color.BRIGHT_CYAN}{'='*60}{Color.RESET}\n")


def main():
    parser = argparse.ArgumentParser(description="Local development helper for mc-skin-wrap-go")
    parser.add_argument("--arch", help="Target architecture (amd64/arm64), default: current system")
    parser.add_argument("--os", help="Target OS (windows/linux/darwin), default: current system")
    parser.add_argument("--host", default=DEFAULT_HOST, help=f"Server host (default: {DEFAULT_HOST})")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help=f"Server port (default: {DEFAULT_PORT})")
    parser.add_argument("--root-path", default=DEFAULT_ROOT_PATH, help=f"Root path prefix (default: {DEFAULT_ROOT_PATH})")
    parser.add_argument("--clear", action="store_true", help="Clear existing extracted directory before extracting")
    args = parser.parse_args()
    
    version = get_version_from_go()
    current_goos, current_goarch = get_current_platform()
    goos = args.os or current_goos
    goarch = args.arch or current_goarch
    
    host = args.host
    port = args.port
    root_path = args.root_path
    
    print(f"\n{Color.BRIGHT_CYAN}{'='*60}{Color.RESET}")
    print(f"{Color.BOLD}🛠️  MC Skin Wrap Local Dev{Color.RESET}")
    print(f"{Color.BRIGHT_CYAN}{'='*60}{Color.RESET}")
    log_info(f"Version:   {Color.BRIGHT_GREEN}{version}{Color.RESET}")
    log_info(f"Platform:  {Color.YELLOW}{goos}/{goarch}{Color.RESET}")
    log_info(f"Host:      {Color.YELLOW}{host}{Color.RESET}")
    log_info(f"Port:      {Color.YELLOW}{port}{Color.RESET}")
    log_info(f"Root Path: {Color.YELLOW}{root_path}{Color.RESET}")
    
    # 1. 更新文档
    update_dev_doc(version, host, port, root_path)
    
    # 2. 解压压缩包
    extract_path = extract_archive(version, goos, goarch, clear=args.clear)
    if not extract_path:
        sys.exit(1)
    
    # 3. 生成命令
    generate_commands(extract_path, goos, host, port, root_path)


if __name__ == "__main__":
    main()
