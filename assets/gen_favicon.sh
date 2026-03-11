#!/usr/bin/env bash
# 从 VincentZyu.Minecraft.png 生成 favicon.ico
# 用法: bash gen_favicon.sh
# 依赖: imagemagick (apt install -y imagemagick)

set -e

SRC="VincentZyu.Minecraft.png"
OUT="favicon.ico"

cd "$(dirname "$0")"

if [ ! -f "$SRC" ]; then
    echo "❌ 找不到 $SRC"
    exit 1
fi

if ! command -v convert &>/dev/null; then
    echo "📦 正在安装 imagemagick ..."
    sudo apt update && sudo apt install -y imagemagick
fi

echo "🔧 生成 favicon.ico (16x16, 32x32, 48x48) ..."
convert "$SRC" \
    \( -clone 0 -resize 16x16 \) \
    \( -clone 0 -resize 32x32 \) \
    \( -clone 0 -resize 48x48 \) \
    -delete 0 \
    "$OUT"

echo "✅ 已生成 $OUT ($(stat -c%s "$OUT") bytes)"
