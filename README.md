# MC Skin Wrap

> A lightweight HTTP server that wraps Minecraft skin/avatar/server status APIs, perfect for self-hosted proxy services.

> **[📖 English](readme.md)**
> **[📖 简体中文](readme.zh-cn.md)**

[![GitHub](https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/VincentZyu233/mc-skin-wrap-http-server)
[![Gitee](https://img.shields.io/badge/Gitee-C71D23?style=for-the-badge&logo=gitee&logoColor=white)](https://gitee.com/vincent-zyu/mc-skin-wrap-http-server)

[![Windows x64 | ARM64](https://img.shields.io/badge/Windows-x64_|_ARM64-0078D4?style=for-the-badge&logo=windows&logoColor=white)](https://github.com/VincentZyu233/mc-skin-wrap-http-server/releases)
[![Linux x64 | ARM64](https://img.shields.io/badge/Linux-x64_|_ARM64-FCC624?style=for-the-badge&logo=linux&logoColor=black)](https://github.com/VincentZyu233/mc-skin-wrap-http-server/releases)
[![macOS x64 | ARM64](https://img.shields.io/badge/macOS-x64_|_ARM64-000000?style=for-the-badge&logo=apple&logoColor=white)](https://github.com/VincentZyu233/mc-skin-wrap-http-server/releases)

## 🚀 Introduction

**MC Skin Wrap** is a simple HTTP server that wraps popular Minecraft-related APIs, providing unified endpoints for:

- 🎭 **Player Avatar** — via [minotar.net](https://minotar.net)
- 🧥 **Player Skin** — via [minotar.net](https://minotar.net)
- 📊 **Java Server Status** — via [mcstatus.io](https://mcstatus.io)

## 💡 Use Case

Deploy this server on a US/overseas VPS, then let your **frontend web apps** or **bot plugins** call it — a handy proxy to bypass GFW or simplify API access.

Example scenario:
- You have a frontend website or a Koishi/Discord bot plugin
- You need to fetch MC player avatars/skins or query Java server status
- Direct API calls are slow or blocked in your region
- → Deploy MC Skin Wrap on your overseas server, and call it as a unified API gateway!

## ✨ Features

- **Dual Implementations**
  - **Go Edition**: High-performance, low memory footprint, single binary — **recommended for production**.
  - **Python Edition**: Easy to hack and extend — great for **prototyping and demos**.
- **Cross-platform**: Windows, Linux, macOS (x64 & ARM64).
- **Proxy Support**: Optional HTTP/SOCKS5 proxy for upstream requests.
- **Swagger Docs**: Built-in API documentation (Go edition).
- **Configurable**: JSON config file for host, port, root path, proxy, etc.

## 📦 Quick Start

### Go Edition (Recommended for Production)

```bash
# Download from Releases, extract, then:
cd mc-skin-wrap_<version>_<os>_<arch>

# Edit config.json as needed
./mc-skin-wrap-go        # Linux/macOS
./mc-skin-wrap-go.exe    # Windows
```

### Python Edition (For Prototyping)

```bash
cd py

# Install dependencies
pip install -r requirements.txt
# Or use uv:
uv venv && uv pip install -r requirements.txt

# Run
python main.py
# Or: uv run python main.py
```

## 🔗 API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /mcjava/avatar/{name}` | Get player avatar (PNG) |
| `GET /mcjava/skin/{name}` | Get player skin (PNG) |
| `GET /mcjava/server_status/{addr}` | Get Java server status (JSON) |
| `GET /docs/` | Swagger UI (Go edition only) |

## ⚙️ Configuration

Edit `config.json`:

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

## 📜 License

MIT License
