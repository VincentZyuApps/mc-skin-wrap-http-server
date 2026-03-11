#!/usr/bin/env bash
# ============================================================
# mc-skin-wrap-http-server 一键部署脚本 (Gitee 镜像)
# 
# 适用于中国大陆用户，解决 GitHub 下载慢的问题
#
# 用法:
#   curl -fsSL https://gitee.com/vincent-zyu/mc-skin-wrap-http-server/raw/main/doc/scripts/install_gitee.sh | bash
#
# 指定版本安装:
#   MC_SKIN_WRAP_VERSION=v0.0.2-beta.4+20260311 bash -c "$(curl -fsSL https://gitee.com/vincent-zyu/mc-skin-wrap-http-server/raw/main/doc/scripts/install_gitee.sh)"
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
info()    { echo -e "${BLUE}[信息]${NC} $1"; }
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
echo -e "${GREEN}    一键部署脚本 (Gitee 镜像) | Minecraft 皮肤/头像/服务器状态 API 代理${NC}"
echo -e "${YELLOW}    🇨🇳 专为国内用户优化，从 Gitee 下载${NC}"
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
# 检查是否通过管道执行
# ============================================================

# 如果是 curl | bash 方式，stdin (fd 0) 是脚本内容，不能动它！
# 我们在 fd 3 上打开终端，所有 read 从 fd 3 读取用户输入。
if [ ! -t 0 ] && [ -e /dev/tty ]; then
    exec 3</dev/tty
else
    exec 3<&0
fi

# ============================================================
# 获取版本列表
# ============================================================

OWNER="vincent-zyu"
REPO="mc-skin-wrap-http-server"
RELEASES_API="https://gitee.com/api/v5/repos/${OWNER}/${REPO}/releases"

info "正在从 Gitee 获取版本列表..."

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
VERSION_COUNT=$(echo "$ALL_VERSIONS" | grep -c . || echo "0")

if [ -z "$ALL_VERSIONS" ] || [ "$VERSION_COUNT" -eq 0 ]; then
    error "没有找到任何 Release 版本，请稍后再试或访问 https://gitee.com/${OWNER}/${REPO}/releases"
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
        echo -e "   ${GREEN}[$IDX]${NC} $ver ${GREEN}(最新)${NC}"
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
# 构建下载链接
# ============================================================

# 构建文件名（去掉 v 前缀）
PLAIN_VER="${VERSION#v}"
FILENAME="mc-skin-wrap_${PLAIN_VER}_linux_${ARCH_NAME}.tar.gz"

# Gitee 下载链接需要对 + 号进行 URL 编码 (%2B)
ENCODED_VER=$(echo "$VERSION" | sed 's/+/%2B/g')
ENCODED_FILENAME=$(echo "$FILENAME" | sed 's/+/%2B/g')

DOWNLOAD_URL="https://gitee.com/${OWNER}/${REPO}/releases/download/${ENCODED_VER}/${ENCODED_FILENAME}"

info "下载文件: ${CYAN}$FILENAME${NC}"

# ============================================================
# 选择下载目录
# ============================================================

DEFAULT_DIR=$(pwd)

echo ""
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
info "当前目录: ${CYAN}${DEFAULT_DIR}${NC}"
echo -n -e "${BLUE}[?]${NC} 是否下载到当前目录? [Y/n]: "
read -r CONFIRM_DIR <&3

CONFIRM_DIR=${CONFIRM_DIR:-Y}

if [[ "$CONFIRM_DIR" =~ ^[Nn]$ ]]; then
    echo -n -e "${BLUE}[?]${NC} 请输入自定义绝对路径: "
    read -r CUSTOM_DIR <&3
    
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
info "正在从 Gitee 下载 ${CYAN}${FILENAME}${NC}..."

if command -v curl &> /dev/null; then
    curl -fSL --progress-bar -o "$FILENAME" "$DOWNLOAD_URL" || error "下载失败，请检查网络或版本号"
elif command -v wget &> /dev/null; then
    wget --show-progress -q -O "$FILENAME" "$DOWNLOAD_URL" || error "下载失败，请检查网络或版本号"
fi

success "下载完成: ${CYAN}${ARCHIVE_PATH}${NC}"

# ============================================================
# 解压文件
# ============================================================

echo ""
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -n -e "${BLUE}[?]${NC} 是否解压文件? [Y/n]: "
read -r CONFIRM_EXTRACT <&3

CONFIRM_EXTRACT=${CONFIRM_EXTRACT:-Y}

if [[ "$CONFIRM_EXTRACT" =~ ^[Yy]$ ]] || [ -z "$CONFIRM_EXTRACT" ]; then
    info "正在解压..."
    
    # 获取解压后的目录名（去掉 .tar.gz）
    EXTRACT_DIR="${FILENAME%.tar.gz}"
    
    # 解压
    tar -xzf "$FILENAME" || error "解压失败"
    
    success "解压完成"

    # 询问是否删除压缩包
    echo ""
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -n -e "${BLUE}[?]${NC} 是否删除压缩包? [Y/n]: "
    read -r CONFIRM_REMOVE <&3
    
    CONFIRM_REMOVE=${CONFIRM_REMOVE:-Y}
    
    if [[ "$CONFIRM_REMOVE" =~ ^[Yy]$ ]] || [ -z "$CONFIRM_REMOVE" ]; then
        rm "$FILENAME"
        success "已删除压缩包"
    fi
    
    # 查找二进制文件
    BINARY_PATH="${INSTALL_DIR}/${EXTRACT_DIR}/mc-skin-wrap-go"
    
    if [ -f "$BINARY_PATH" ]; then
        success "二进制文件: ${CYAN}${BINARY_PATH}${NC}"
        
        # 询问是否 cd 到目录
        echo ""
        echo -n -e "${BLUE}[?]${NC} 是否进入解压目录? [Y/n]: "
        read -r CONFIRM_CD <&3
        
        CONFIRM_CD=${CONFIRM_CD:-Y}
        
        if [[ "$CONFIRM_CD" =~ ^[Yy]$ ]] || [ -z "$CONFIRM_CD" ]; then
            cd "${INSTALL_DIR}/${EXTRACT_DIR}"
            echo ""
            echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
            success "已进入目录: $(pwd)"
            echo -e "[INFO] 你现在可以直接运行: ./mc-skin-wrap-go"
            echo ""
            # 尝试生成一个新的 shell 以保持在目录中
            if [ -n "$BASH" ]; then
                 exec "$BASH"
            elif [ -n "$ZSH_NAME" ]; then
                 exec "$ZSH_NAME"
            else
                 exec sh
            fi
        fi
    else
        warn "未找到二进制文件，请检查解压内容"
        ls -la "${INSTALL_DIR}/${EXTRACT_DIR}/"
    fi
else
    echo ""
    success "下载完成！文件保存在: ${CYAN}${ARCHIVE_PATH}${NC}"
    info "手动解压: tar -xzf ${FILENAME}"
fi

# ============================================================
# 完成
# ============================================================

echo ""
echo -e "${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║${NC}  ${GREEN}✓ 部署脚本执行完成${NC}"
echo -e "${CYAN}║${NC}"
echo -e "${CYAN}║${NC}  📦 版本:   ${VERSION}"
echo -e "${CYAN}║${NC}  📖 Gitee:  https://gitee.com/${OWNER}/${REPO}"
echo -e "${CYAN}║${NC}  📖 GitHub: https://github.com/VincentZyuApps/${REPO}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}   🌐 GitHub 安装脚本 (海外用户):${NC}"
echo -e "   curl -fsSL https://raw.githubusercontent.com/VincentZyuApps/${REPO}/main/doc/scripts/install.sh | bash"
echo ""
