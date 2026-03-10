# Python 开发指南

> 🐍 Python 版本适合**原型开发**和**概念验证**，生产环境推荐使用 Go 版本。

## 📦 环境要求

- Python: `>= 3.12`
- 依赖: FastAPI + Uvicorn + Requests

## 🚀 快速开始

### 1️⃣ 复制配置文件

```bash
cd py
cp config.example.json config.json
# 按需修改 config.json
```

### 2️⃣ 方式一: 传统 venv

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
./venv/Scripts/Activate     # Windows
source ./venv/bin/activate  # Linux/macOS

# 安装依赖
pip install -r requirements.txt

# 启动服务
python main.py              # 生产模式
python main.py --reload     # 开发模式 (热重载)
```

### 2️⃣ 方式二: uv (推荐 🚀)

[uv](https://docs.astral.sh/uv/) 是 Rust 写的超快 Python 包管理器。

```bash
# 创建虚拟环境
uv venv --python 3.12

# 安装依赖
uv pip install -r requirements.txt

# 启动服务
uv run python main.py              # 生产模式
uv run python main.py --reload     # 开发模式 (热重载)
```

---

## 🧪 curl 测试

### PowerShell

```powershell
$H = "127.0.0.1"
$P = 58418
$R = "/fastapi_skin_wrap"  # root_path 前缀

# 获取头像
curl "http://${H}:${P}${R}/mcjava/avatar/VincentZyu" -o avatar.png

# 获取皮肤
curl "http://${H}:${P}${R}/mcjava/skin/VincentZyu" -o skin.png

# 获取服务器状态
curl "http://${H}:${P}${R}/mcjava/server_status/mc.hypixel.net"

# FastAPI 自动生成的 Swagger 文档页
curl "http://${H}:${P}${R}/docs"
```

### Bash

```bash
H="127.0.0.1"
P=58418
R="/fastapi_skin_wrap"  # root_path 前缀

# 获取头像
curl "http://${H}:${P}${R}/mcjava/avatar/VincentZyu" -o avatar.png

# 获取皮肤
curl "http://${H}:${P}${R}/mcjava/skin/VincentZyu" -o skin.png

# 获取服务器状态
curl "http://${H}:${P}${R}/mcjava/server_status/mc.hypixel.net"

# FastAPI 自动生成的 Swagger 文档页
curl "http://${H}:${P}${R}/docs"
```

## 🌐 浏览器 URLs

> 💡 使用上面定义的环境变量 `$H`, `$P`, `$R` 拼接 URL

### PowerShell

```powershell
# 头像
echo "http://${H}:${P}${R}/mcjava/avatar/VincentZyu"

# 皮肤
echo "http://${H}:${P}${R}/mcjava/skin/VincentZyu"

# 服务器状态
echo "http://${H}:${P}${R}/mcjava/server_status/mc.hypixel.net"

# Swagger 文档 (FastAPI 自带)
echo "http://${H}:${P}${R}/docs"
```

### Bash

```bash
# 头像
echo "http://${H}:${P}${R}/mcjava/avatar/VincentZyu"

# 皮肤
echo "http://${H}:${P}${R}/mcjava/skin/VincentZyu"

# 服务器状态
echo "http://${H}:${P}${R}/mcjava/server_status/mc.hypixel.net"

# Swagger 文档 (FastAPI 自带)
echo "http://${H}:${P}${R}/docs"
```
