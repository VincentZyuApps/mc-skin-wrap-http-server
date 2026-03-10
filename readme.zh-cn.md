# MC Skin Wrap

> 轻量级 HTTP 服务器，封装 Minecraft 皮肤/头像/服务器状态 API，适合自建代理服务。

> **[📖 English](readme.md)**
> **[📖 简体中文](readme.zh-cn.md)**

[![GitHub](https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/VincentZyu233/mc-skin-wrap-http-server)
[![Gitee](https://img.shields.io/badge/Gitee-C71D23?style=for-the-badge&logo=gitee&logoColor=white)](https://gitee.com/vincent-zyu/mc-skin-wrap-http-server)

[![Windows x64 | ARM64](https://img.shields.io/badge/Windows-x64_|_ARM64-0078D4?style=for-the-badge&logo=windows&logoColor=white)](https://github.com/VincentZyu233/mc-skin-wrap-http-server/releases)
[![Linux x64 | ARM64](https://img.shields.io/badge/Linux-x64_|_ARM64-FCC624?style=for-the-badge&logo=linux&logoColor=black)](https://github.com/VincentZyu233/mc-skin-wrap-http-server/releases)
[![macOS x64 | ARM64](https://img.shields.io/badge/macOS-x64_|_ARM64-000000?style=for-the-badge&logo=apple&logoColor=white)](https://github.com/VincentZyu233/mc-skin-wrap-http-server/releases)

## 🚀 简介

**MC Skin Wrap** 是一个简单的 HTTP 服务器，封装了常用的 Minecraft 相关 API，提供统一接口：

- 🎭 **玩家头像** — 通过 [minotar.net](https://minotar.net)
- 🧥 **玩家皮肤** — 通过 [minotar.net](https://minotar.net)
- 📊 **Java 服务器状态** — 通过 [mcstatus.io](https://mcstatus.io)

## 💡 使用场景

把这个服务部署到阿美莉卡/海外服务器上，然后让你的**前端网页**或**机器人插件**来调用——一个方便的代理，绕过墙或简化 API 访问。

典型场景：
- 你有一个前端网站或 Koishi/Discord 机器人插件
- 你需要获取 MC 玩家头像/皮肤，或者查询 Java 服务器状态
- 直接调用 API 在你的网络环境下很慢或被墙
- → 把 MC Skin Wrap 部署到海外服务器，作为统一的 API 网关调用！

## ✨ 主要特性

- **双实现版本**
  - **Go 版**: 高性能、低内存占用、单二进制文件 — **推荐生产环境使用**。
  - **Python 版**: 易于修改和扩展 — 适合**原型开发和演示**。
- **跨平台**: Windows、Linux、macOS（x64 & ARM64）。
- **代理支持**: 可选 HTTP/SOCKS5 代理用于上游请求。
- **Swagger 文档**: 内置 API 文档（Go 版）。
- **可配置**: JSON 配置文件，支持 host、port、root path、代理等。

## 📦 快速开始

### Go 版本（推荐生产环境）

```bash
# 从 Releases 下载并解压，然后：
cd mc-skin-wrap_<version>_<os>_<arch>

# 按需编辑 config.json
./mc-skin-wrap-go        # Linux/macOS
./mc-skin-wrap-go.exe    # Windows
```

### Python 版本（用于原型开发）

```bash
cd py

# 安装依赖
pip install -r requirements.txt
# 或使用 uv：
uv venv && uv pip install -r requirements.txt

# 运行
python main.py
# 或: uv run python main.py
```

## 🔗 API 端点

| 端点 | 描述 |
|------|------|
| `GET /mcjava/avatar/{name}` | 获取玩家头像 (PNG) |
| `GET /mcjava/skin/{name}` | 获取玩家皮肤 (PNG) |
| `GET /mcjava/server_status/{addr}` | 获取 Java 服务器状态 (JSON) |
| `GET /docs/` | Swagger UI（仅 Go 版） |

## ⚙️ 配置说明

编辑 `config.json`：

```json
{
  "host": "0.0.0.0",
  "port": 60311,
  "root_path": "/gin_skin_wrap",
  "proxy_enabled": false,
  "proxy_protocol": "http",
  "proxy_host": "127.0.0.1",
  "proxy_port": 7890,
  "log_level": "info"
}
```

## 📜 许可证

MIT License
