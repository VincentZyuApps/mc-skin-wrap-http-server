#!/usr/bin/env bash
# ============================================================
# mc-skin-wrap-http-server 一键部署脚本
# 
# 用法:
#   curl -fsSL https://raw.githubusercontent.com/VincentZyuApps/mc-skin-wrap-http-server/main/doc/scripts/install.sh | bash
#
# 指定版本安装:
#   MC_SKIN_WRAP_VERSION=v0.0.2-beta.4+20260311 bash -c "$(curl -fsSL https://raw.githubusercontent.com/VincentZyuApps/mc-skin-wrap-http-server/main/doc/scripts/install.sh)"
#
# 国内加速 (通过 GitHub Proxy):
#   curl -fsSL https://ghfast.top/https://raw.githubusercontent.com/VincentZyuApps/mc-skin-wrap-http-server/main/doc/scripts/install.sh | bash
#
# 支持的系统: Linux (Debian, Ubuntu, Arch, Alpine, Fedora, CentOS, etc.)
# 支持的架构: x86_64 (amd64), aarch64 (arm64)
# ============================================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# 打印函数
info()    { echo -e "${BLUE}[INFO]${NC} $1"; }
success() { echo -e "${GREEN}[✓]${NC} $1"; }
warn()    { echo -e "${YELLOW}[!]${NC} $1"; }
error()   { echo -e "${RED}[✗]${NC} $1"; exit 1; }

# 欢迎信息 (ASCII Art)
echo -e "${CYAN}"
cat << 'EOF'
    __  _________    _____ __ __ _____   __    _       ______  ___    ____ 
   /  |/  / ____/   / ___// //_//  _/ | / /   | |     / / __ \/   |  / __ \
  / /|_/ / /  ______\__ \/ ,<   / //  |/ /____| | /| / / /_/ / /| | / /_/ /
 / /  / / /__/_____/__/ / /| |_/ // /|  /_____/ |/ |/ / _, _/ ___ |/ ____/ 
/_/  /_/\____/    /____/_/ |_/___/_/ |_/      |__/|__/_/ |_/_/  |_/_/      

   __________        ___________   __
  / ____/ __ \      / ____/  _/ | / /
 / / __/ / / /_____/ / __ / //  |/ / 
/ /_/ / /_/ /_____/ /_/ // // /|  /  
\____/\____/      \____/___/_/ |_/   
EOF
echo -e "${NC}"
echo -e "${GREEN}    一键部署脚本 | Minecraft 皮肤/头像/服务器状态 API 代理${NC}"
echo ""

# ============================================================
# 检测系统和架构
# ============================================================

OS=$(uname -s | tr '[:upper:]' '[:lower:]')
ARCH=$(uname -m)

# 只支持 Linux
if [ "$OS" != "linux" ]; then
    error "此脚本仅支持 Linux 系统，检测到: $OS"
fi

# 架构映射
case "$ARCH" in
    x86_64|amd64)
        ARCH_NAME="amd64"
        ;;
    aarch64|arm64)
        ARCH_NAME="arm64"
        ;;
    *)
        error "不支持的架构: $ARCH (仅支持 x86_64/amd64, aarch64/arm64)"
        ;;
esac

info "检测到系统: ${CYAN}${OS} ${ARCH}${NC} → 将下载 ${CYAN}linux_${ARCH_NAME}${NC} 版本"

# ============================================================
# 获取版本列表
# ============================================================

REPO="VincentZyuApps/mc-skin-wrap-http-server"
RELEASES_API="https://api.github.com/repos/${REPO}/releases"

info "正在获取版本列表..."

# 获取所有 releases
if command -v curl &> /dev/null; then
    FETCH_CMD="curl -fsSL"
elif command -v wget &> /dev/null; then
    FETCH_CMD="wget -qO-"
else
    error "需要 curl 或 wget，请先安装"
fi

ALL_RELEASES=$($FETCH_CMD "$RELEASES_API" 2>/dev/null) || error "无法获取 Release 列表，请检查网络连接"

# 提取所有版本号
ALL_VERSIONS=$(echo "$ALL_RELEASES" | grep -oP '"tag_name":\s*"\K[^"]+')
VERSION_COUNT=$(echo "$ALL_VERSIONS" | wc -l)

if [ -z "$ALL_VERSIONS" ]; then
    error "没有找到任何 Release 版本"
fi

# 显示最近的版本列表（最多10个）
echo ""
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BOLD}📋 可用版本列表${NC}"

if [ "$VERSION_COUNT" -le 10 ]; then
    echo -e "   （共 ${VERSION_COUNT} 个版本）"
else
    echo -e "   （显示最新 10 个，共 ${VERSION_COUNT} 个版本）"
fi
echo ""

# 显示版本列表（最多10个）
DISPLAY_VERSIONS=$(echo "$ALL_VERSIONS" | head -10)
IDX=1
LATEST_VERSION=$(echo "$ALL_VERSIONS" | head -1)

while IFS= read -r ver; do
    if [ "$ver" = "$LATEST_VERSION" ]; then
        echo -e "   ${GREEN}[$IDX]${NC} $ver ${GREEN}(latest)${NC}"
    else
        echo -e "   ${CYAN}[$IDX]${NC} $ver"
    fi
    IDX=$((IDX + 1))
done <<< "$DISPLAY_VERSIONS"

echo ""

# ============================================================
# 确定要安装的版本
# ============================================================

# 检查是否通过环境变量指定了版本
if [ -n "$MC_SKIN_WRAP_VERSION" ]; then
    VERSION="$MC_SKIN_WRAP_VERSION"
    info "使用环境变量指定的版本: ${CYAN}${VERSION}${NC}"
    
    # 验证版本是否存在
    if ! echo "$ALL_VERSIONS" | grep -q "^${VERSION}$"; then
        error "指定的版本 ${VERSION} 不存在！请检查版本号"
    fi
else
    # 默认使用最新版本
    VERSION="$LATEST_VERSION"
    success "将安装最新版本: ${GREEN}${VERSION}${NC}"
fi

# ============================================================
# 获取下载链接
# ============================================================

# 构建文件名（去掉 v 前缀）
PLAIN_VER="${VERSION#v}"
FILENAME="mc-skin-wrap_${PLAIN_VER}_linux_${ARCH_NAME}.tar.gz"

# 获取指定版本的 release 信息
RELEASE_API="https://api.github.com/repos/${REPO}/releases/tags/${VERSION}"
RELEASE_JSON=$($FETCH_CMD "$RELEASE_API" 2>/dev/null) || error "无法获取版本 ${VERSION} 的信息"

DOWNLOAD_URL=$(echo "$RELEASE_JSON" | grep -oP '"browser_download_url":\s*"\K[^"]+' | grep "$FILENAME" | head -1)

if [ -z "$DOWNLOAD_URL" ]; then
    error "找不到适合当前系统的下载文件: $FILENAME"
fi

info "下载文件: ${CYAN}$FILENAME${NC}"

# ============================================================
# 选择下载目录
# ============================================================

DEFAULT_DIR=$(pwd)

echo ""
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
info "当前目录: ${CYAN}${DEFAULT_DIR}${NC}"
echo -n -e "${BLUE}[?]${NC} 是否下载到当前目录? [Y/n]: "
read -r CONFIRM_DIR

CONFIRM_DIR=${CONFIRM_DIR:-Y}

if [[ "$CONFIRM_DIR" =~ ^[Nn]$ ]]; then
    echo -n -e "${BLUE}[?]${NC} 请输入自定义绝对路径: "
    read -r CUSTOM_DIR
    
    if [ -z "$CUSTOM_DIR" ]; then
        error "路径不能为空"
    fi
    
    # 创建目录（如果不存在）
    if [ ! -d "$CUSTOM_DIR" ]; then
        mkdir -p "$CUSTOM_DIR" || error "无法创建目录: $CUSTOM_DIR"
        success "已创建目录: $CUSTOM_DIR"
    fi
    
    INSTALL_DIR="$CUSTOM_DIR"
else
    INSTALL_DIR="$DEFAULT_DIR"
fi

info "下载目录: ${CYAN}${INSTALL_DIR}${NC}"

# ============================================================
# 下载文件
# ============================================================

cd "$INSTALL_DIR"
ARCHIVE_PATH="${INSTALL_DIR}/${FILENAME}"

echo ""
info "正在下载 ${FILENAME}..."

if command -v curl &> /dev/null; then
    curl -fSL --progress-bar -o "$FILENAME" "$DOWNLOAD_URL" || error "下载失败"
elif command -v wget &> /dev/null; then
    wget --show-progress -q -O "$FILENAME" "$DOWNLOAD_URL" || error "下载失败"
fi

success "下载完成: ${ARCHIVE_PATH}"

# ============================================================
# 解压文件
# ============================================================

echo ""
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -n -e "${BLUE}[?]${NC} 是否解压文件? [Y/n]: "
read -r CONFIRM_EXTRACT

CONFIRM_EXTRACT=${CONFIRM_EXTRACT:-Y}

if [[ "$CONFIRM_EXTRACT" =~ ^[Yy]$ ]] || [ -z "$CONFIRM_EXTRACT" ]; then
    info "正在解压..."
    
    # 获取解压后的目录名（去掉 .tar.gz）
    EXTRACT_DIR="${FILENAME%.tar.gz}"
    
    # 解压
    tar -xzf "$FILENAME" || error "解压失败"
    
    success "解压完成"
    
    # 查找二进制文件
    BINARY_PATH="${INSTALL_DIR}/${EXTRACT_DIR}/mc-skin-wrap-go"
    
    if [ -f "$BINARY_PATH" ]; then
        success "二进制文件: ${CYAN}${BINARY_PATH}${NC}"
        
        # 询问是否 cd 到目录
        echo ""
        echo -n -e "${BLUE}[?]${NC} 是否进入解压目录? [Y/n]: "
        read -r CONFIRM_CD
        
        CONFIRM_CD=${CONFIRM_CD:-Y}
        
        if [[ "$CONFIRM_CD" =~ ^[Yy]$ ]] || [ -z "$CONFIRM_CD" ]; then
            BINARY_DIR="${INSTALL_DIR}/${EXTRACT_DIR}"
            
            echo ""
            echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
            success "安装完成！"
            echo ""
            info "由于脚本在子 shell 中运行，请手动执行以下命令："
            echo ""
            echo -e "  ${GREEN}cd ${BINARY_DIR}${NC}"
            echo -e "  ${GREEN}./mc-skin-wrap-go${NC}"
            echo ""
            info "或者直接运行："
            echo ""
            echo -e "  ${GREEN}${BINARY_PATH}${NC}"
            echo ""
        fi
    else
        warn "未找到二进制文件，请检查解压内容"
        ls -la "${INSTALL_DIR}/${EXTRACT_DIR}/"
    fi
else
    echo ""
    success "下载完成！文件保存在: ${ARCHIVE_PATH}"
    info "手动解压: tar -xzf ${FILENAME}"
fi

# ============================================================
# 完成
# ============================================================

echo ""
echo -e "${CYAN}╔══════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║${NC}  ${GREEN}✓ 部署脚本执行完成${NC}                                           ${CYAN}║${NC}"
echo -e "${CYAN}║${NC}                                                                  ${CYAN}║${NC}"
echo -e "${CYAN}║${NC}  📦 版本: ${VERSION}                                     ${CYAN}║${NC}"
echo -e "${CYAN}║${NC}  📖 文档: https://github.com/${REPO}        ${CYAN}║${NC}"
echo -e "${CYAN}║${NC}  🐛 问题: https://github.com/${REPO}/issues ${CYAN}║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════════════════╝${NC}"
echo ""
