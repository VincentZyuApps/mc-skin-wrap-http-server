![mc-skin-wrap-http-server](https://socialify.git.ci/VincentZyuApps/mc-skin-wrap-http-server/image?custom_description=%F0%9F%8E%AE+Minecraft+Java%E7%89%88+%E7%9A%AE%E8%82%A4%2F%E5%A4%B4%E5%83%8F%2F%E6%9C%8D%E5%8A%A1%E5%99%A8%E7%8A%B6%E6%80%81+API+%E4%BB%A3%E7%90%86+%C2%B7+%F0%9F%87%A8%F0%9F%87%B3+%E5%A4%A7%E9%99%86%E5%8A%A0%E9%80%9F+%C2%B7+%0A%E6%8F%90%E4%BE%9B%F0%9F%92%99Go%2B%F0%9F%90%8DPy+%E5%8F%8C%E7%89%88%E6%9C%AC+%C2%B7+%F0%9F%93%A6+Win%2FLinux%2FmacOS&custom_language=Go&description=1&forks=1&issues=1&language=1&logo=https%3A%2F%2Favatars.githubusercontent.com%2Fu%2F250448479%3Fs%3D200%26v%3D4&name=1&owner=1&pattern=Signal&pulls=1&stargazers=1&theme=Auto)
# MC Skin Wrap

> 轻量级 HTTP 服务器，封装 Minecraft 皮肤/头像/服务器状态 API，适合自建代理服务。
>
> 🎯 **目标用户**: 大陆开发者 or Minecraft玩家 等。
> (因为海外用户可直接调用原始 API，无需本项目

[![GitHub](https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/VincentZyuApps/mc-skin-wrap-http-server)
[![Gitee](https://img.shields.io/badge/Gitee-C71D23?style=for-the-badge&logo=gitee&logoColor=white)](https://gitee.com/vincent-zyu/mc-skin-wrap-http-server)

[![Windows x64 | ARM64](https://img.shields.io/badge/Windows-x64_|_ARM64-0078D4?style=for-the-badge&logo=windows&logoColor=white)](https://github.com/VincentZyuApps/mc-skin-wrap-http-server/releases)
[![Linux x64 | ARM64](https://img.shields.io/badge/Linux-x64_|_ARM64-FCC624?style=for-the-badge&logo=linux&logoColor=black)](https://github.com/VincentZyuApps/mc-skin-wrap-http-server/releases)
[![macOS x64 | ARM64](https://img.shields.io/badge/macOS-x64_|_ARM64-000000?style=for-the-badge&logo=apple&logoColor=white)](https://github.com/VincentZyuApps/mc-skin-wrap-http-server/releases)

## 🚀 简介

**MC Skin Wrap** 是一个简单的 HTTP 服务器，封装了常用的 Minecraft 相关 API，提供统一接口：

- 🎭 **玩家头像** — 通过 [minotar.net](https://minotar.net)
- 🧥 **玩家皮肤** — 通过 [minotar.net](https://minotar.net)
- 📊 **Java 服务器状态** — 通过 [mcstatus.io](https://mcstatus.io)

## 💡 使用场景举例

把这个服务部署到阿美莉卡 or 其他海外地区的 VPS 上，然后让你的**前端网页**或**机器人插件**来调用——一个方便的代理，绕过墙或简化 API 访问。

> 💡 **国内也能用！** 本项目支持在 `config.json` 中配置代理，支持 `http` / `https` / `socks4` / `socks5` / `socks5h` 协议，在国内直接跑也没问题~

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

## 📖 开发文档

> 💡 **开发者/部署者**: 想了解如何构建、测试或调试？请查阅对应文档：

| 文档 | 说明 |
|------|------|
| [📘 Go 开发指南](doc/dev.go.md) | 构建、测试、Swagger 文档生成、**一键 curl 测试命令** |
| [📗 Python 开发指南](doc/dev.py.md) | 环境搭建、快速启动、**一键 curl 测试命令** |
| [📙 Git 操作指南](doc/dev.git.md) | 生产环境同步、常用命令 |
| [🚀 Go 生产部署指南](doc/prod.go.md) | 安装脚本、screen 后台、**Nginx 反代 + CORS 踩坑** |

### 🌐 在线体验

> 🎉 **懒得自己部署？** 直接用作者的公开接口试试吧~
>
> （2RMB/月的小鸡，上面没别的东西，被打了就打了，就当玩了 😂）
>
> ✨ 开源代码不够，还免费提供公开接口 —— 如此慷慨的作者，不来个 ⭐ Star 说不过去吧？

| 接口 | 在线地址 |
|------|---------|
| 🎭 玩家头像 | [https://us-hudiyun.vincentzyu233.cn/nginx_gin_skin/gin_skin_wrap/mcjava/avatar/VincentZyu](https://us-hudiyun.vincentzyu233.cn/nginx_gin_skin/gin_skin_wrap/mcjava/avatar/VincentZyu) |
| 🧥 玩家皮肤 | [https://us-hudiyun.vincentzyu233.cn/nginx_gin_skin/gin_skin_wrap/mcjava/skin/VincentZyu](https://us-hudiyun.vincentzyu233.cn/nginx_gin_skin/gin_skin_wrap/mcjava/skin/VincentZyu) |
| 📊 服务器状态 | [https://us-hudiyun.vincentzyu233.cn/nginx_gin_skin/gin_skin_wrap/mcjava/server_status/bc.vincentzyu233.cn](https://us-hudiyun.vincentzyu233.cn/nginx_gin_skin/gin_skin_wrap/mcjava/server_status/bc.vincentzyu233.cn) |
| 📚 Swagger 文档 | [https://us-hudiyun.vincentzyu233.cn/nginx_gin_skin/gin_skin_wrap/docs/index.html](https://us-hudiyun.vincentzyu233.cn/nginx_gin_skin/gin_skin_wrap/docs/index.html) |

## 📦 快速开始

### 🐧 Linux 一键部署（推荐）

在你的海外 Linux 服务器上执行：

```bash
# 直接安装最新版（GitHub）
curl -fsSL https://raw.githubusercontent.com/VincentZyuApps/mc-skin-wrap-http-server/main/doc/scripts/install.sh | bash

# 安装指定版本
MC_SKIN_WRAP_VERSION=v0.0.2-beta.5 bash -c "$(curl -fsSL https://raw.githubusercontent.com/VincentZyuApps/mc-skin-wrap-http-server/main/doc/scripts/install.sh)"
```

**🇨🇳 国内 Gitee 镜像（大陆用户推荐）：**

```bash
# 从 Gitee 安装
curl -fsSL https://gitee.com/vincent-zyu/mc-skin-wrap-http-server/raw/main/doc/scripts/install_gitee.sh | bash

# 安装指定版本
MC_SKIN_WRAP_VERSION=v0.0.2-beta.5 bash -c "$(curl -fsSL https://gitee.com/vincent-zyu/mc-skin-wrap-http-server/raw/main/doc/scripts/install_gitee.sh)"
```

脚本会自动检测系统架构 (x64/ARM64)，显示最近 10 个可用版本，交互式引导安装。

### Go 版本（推荐生产环境）

```bash
# 从 Releases 下载并解压，然后：
cd mc-skin-wrap_<version>_<os>_<arch>

# 按需编辑 config.json
./mc-skin-wrap-go        # Linux/macOS
./mc-skin-wrap-go.exe    # Windows
```

> 💡 **保持后台运行**: Linux/macOS 推荐使用 `screen` 或 `tmux` 挂在后台；Windows 保持 CMD / PowerShell 窗口开着即可。

### Python 版本（用于原型开发）

```bash
cd py

# 安装依赖，推荐使用uv:
uv venv --python 3.12
uv pip install -r requirements.txt

# 运行
uv run python main.py
```

## 🔗 API 端点

| 端点 | 描述 |
|------|------|
| `GET /mcjava/avatar/{name}` | 获取玩家头像 (PNG) |
| `GET /mcjava/skin/{name}` | 获取玩家皮肤 (PNG) |
| `GET /mcjava/server_status/{addr}` | 获取 Java 服务器状态 (JSON) |
| `GET /docs/` | Swagger UI (Go: gin-swagger, Python: FastAPI 自带) |

## ⚙️ 配置说明

编辑 `config.json`：

```json
{
  "host": "0.0.0.0",
  "port": 60311,
  "root_path": "/gin_skin_wrap",
  "cors_allow_origins": ["*"],
  "proxy_enabled": false,
  "proxy_protocol": "http",
  "proxy_host": "127.0.0.1",
  "proxy_port": 7890,
  "log_level": "info"
}
```

> 反向代理部署时，Nginx 需要额外透传 `X-Forwarded-Host`、`X-Forwarded-Proto`、`X-Forwarded-Prefix`，这样 Go 版 Swagger UI 的 `Try it out` 才会自动拼出正确的外部 URL。

## 📁 项目结构

```
mc-skin-wrap-http-server/
├── go/                 # 🦀 Go 版本 (生产环境推荐)
│   ├── main.go
│   ├── build.py        # 交叉编译脚本
│   ├── local_dev.py    # 本地开发辅助
│   └── config.example.json
├── py/                 # 🐍 Python 版本 (原型演示)
│   ├── main.py
│   └── config.example.json
├── doc/                # 📖 开发文档
│   ├── dev.go.md
│   ├── dev.py.md
│   └── dev.git.md
└── dist/               # 📦 构建产物
```

## 📜许可证

MIT License
