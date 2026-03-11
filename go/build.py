import os
import subprocess
import sys
import shutil
import argparse

# ========== ANSI 颜色 ==========
class Color:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    # 前景色
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    # 亮色
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"

def log_run(msg):
    print(f"{Color.CYAN}⚙️  [RUN]{Color.RESET} {msg}")

def log_build(msg):
    print(f"\n{Color.BRIGHT_BLUE}🔨 [BUILD]{Color.RESET} {Color.BOLD}{msg}{Color.RESET}")

def log_copy(msg):
    print(f"{Color.GREEN}📋 [COPY]{Color.RESET} {msg}")

def log_pack(msg):
    print(f"{Color.MAGENTA}📦 [PACK]{Color.RESET} {msg}")

def log_clear(msg):
    print(f"{Color.YELLOW}🧹 [CLEAR]{Color.RESET} {msg}")

def log_ok(msg):
    print(f"{Color.BRIGHT_GREEN}✅ [OK]{Color.RESET} {msg}")

def log_error(msg):
    print(f"{Color.BRIGHT_RED}❌ [ERROR]{Color.RESET} {msg}")

def log_info(msg):
    print(f"{Color.WHITE}ℹ️  [INFO]{Color.RESET} {msg}")

def log_skip(msg):
    print(f"{Color.YELLOW}⏭️  [SKIP]{Color.RESET} {msg}")

# 配置参数
APP_NAME = "mc-skin-wrap-go"
VERSION = "0.0.1" # 在 github action 中会通过 main.go 提取，这里本地默认
SOURCE_DIR = "go"
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # 项目根目录
DIST_DIR = os.path.join(PROJECT_ROOT, "dist")

# 构建目标配置 (GOOS, GOARCH, binary_name)
TARGETS = [
    ("windows", "amd64", f"{APP_NAME}.exe"),
    ("windows", "arm64", f"{APP_NAME}.exe"),
    ("linux",   "amd64", f"{APP_NAME}"),
    ("linux",   "arm64", f"{APP_NAME}"),
    ("darwin",  "amd64", f"{APP_NAME}"),
    ("darwin",  "arm64", f"{APP_NAME}"),
]

def run_command(cmd, env=None, cwd=None):
    """运行终端命令并处理错误"""
    log_run(' '.join(cmd))
    result = subprocess.run(cmd, env=env, cwd=cwd, shell=(sys.platform == "win32"))
    if result.returncode != 0:
        log_error(f"Command failed with exit code {result.returncode}")
        sys.exit(result.returncode)

def get_version_from_go():
    """从 main.go 提取版本号"""
    main_go = os.path.join(PROJECT_ROOT, SOURCE_DIR, "main.go")
    if not os.path.exists(main_go):
        return VERSION
    try:
        with open(main_go, "r", encoding="utf-8") as f:
            for line in f:
                if 'const Version =' in line:
                    return line.split('"')[1]
    except Exception:
        pass
    return VERSION

def build(goos, goarch, binary_name, version):
    """执行单个目标的编译和打包"""
    dir_name = f"mc-skin-wrap_{version}_{goos}_{goarch}"
    build_path = os.path.join(DIST_DIR, dir_name)
    
    # 1. 创建打包目录
    if os.path.exists(build_path):
        shutil.rmtree(build_path)
    os.makedirs(build_path)

    # 2. 编译
    log_build(f"Target: {goos}/{goarch}")
    env = os.environ.copy()
    env["GOOS"] = goos
    env["GOARCH"] = goarch
    env["CGO_ENABLED"] = "0"
    
    # 【优化】设置 GOPROXY 国内源，解决下载依赖卡顿问题
    if "GOPROXY" not in env:
        env["GOPROXY"] = "https://goproxy.cn,direct"
    
    # 尝试自动读取 WSL/系统 代理变量 (如果 python 运行环境有的话就会自动继承 os.environ)
    # 也可以手动指定，例如:
    # env["HTTP_PROXY"] = "http://192.168.31.233:7890"
    # env["HTTPS_PROXY"] = "http://192.168.31.233:7890"

    ldflags = "-s -w" # 压缩体积，去除符号表
    output_file = os.path.abspath(os.path.join(build_path, binary_name))
    
    # 【修复】在 go 目录下执行编译，以确保能正确读取 go.mod
    go_src_dir = os.path.join(PROJECT_ROOT, SOURCE_DIR)
    run_command(["go", "build", "-ldflags", ldflags, "-o", output_file, "main.go"], env=env, cwd=go_src_dir)

    # 3. 复制配置文件 (从 go/ 目录下的模板)
    example_config = os.path.join(PROJECT_ROOT, SOURCE_DIR, "config.example.json")
    if os.path.exists(example_config):
        shutil.copy(example_config, os.path.join(build_path, "config.example.json"))
        shutil.copy(example_config, os.path.join(build_path, "config.json"))
        log_copy("Added config.example.json + config.json")

    # 3.5 复制 favicon
    favicon_src = os.path.join(PROJECT_ROOT, "assets", "favicon.ico")
    if os.path.exists(favicon_src):
        shutil.copy(favicon_src, os.path.join(build_path, "favicon.ico"))
        log_copy("Added favicon.ico")

    # 4. 压缩
    archive_base = os.path.join(DIST_DIR, dir_name)
    if goos == "windows":
        shutil.make_archive(archive_base, 'zip', DIST_DIR, dir_name)
        log_pack(f"Created {archive_base}.zip")
    else:
        shutil.make_archive(archive_base, 'gztar', DIST_DIR, dir_name)
        log_pack(f"Created {archive_base}.tar.gz")

    # 5. 清理临时目录
    shutil.rmtree(build_path)

def main():
    parser = argparse.ArgumentParser(description="Multi-platform Go builder for mc-skin-wrap")
    parser.add_argument("--os", help="Target OS (windows/linux/darwin)")
    parser.add_argument("--arch", help="Target Architecture (amd64/arm64)")
    parser.add_argument("--clear", action="store_true", help="Clear dist folder before building (for local debug)")
    args = parser.parse_args()

    version = get_version_from_go()
    
    # 打印 banner
    print(f"\n{Color.BRIGHT_CYAN}{'='*50}{Color.RESET}")
    print(f"{Color.BOLD}🚀 MC Skin Wrap Go Builder{Color.RESET}")
    print(f"{Color.BRIGHT_CYAN}{'='*50}{Color.RESET}")
    log_info(f"Version: {Color.BRIGHT_GREEN}{version}{Color.RESET}")
    log_info(f"Output:  {Color.YELLOW}{DIST_DIR}{Color.RESET}")

    # 本地调试用：清空 dist 目录
    if args.clear and os.path.exists(DIST_DIR):
        log_clear(f"Removing {DIST_DIR}...")
        shutil.rmtree(DIST_DIR)

    if not os.path.exists(DIST_DIR):
        os.makedirs(DIST_DIR)

    # 如果指定了特定平台
    if args.os and args.arch:
        binary = f"{APP_NAME}.exe" if args.os == "windows" else APP_NAME
        build(args.os, args.arch, binary, version)
        log_ok(f"Build completed for {args.os}/{args.arch}")
    else:
        # 构建所有
        total = len(TARGETS)
        for i, (goos, goarch, binary) in enumerate(TARGETS, 1):
            log_info(f"Progress: [{i}/{total}]")
            build(goos, goarch, binary, version)
        
        print(f"\n{Color.BRIGHT_GREEN}{'='*50}{Color.RESET}")
        log_ok(f"All {total} targets built successfully! 🎉")
        print(f"{Color.BRIGHT_GREEN}{'='*50}{Color.RESET}\n")


if __name__ == "__main__":
    main()
