# 🚀 Go 版生产环境部署指南

> 以作者的实际部署为例，从 GitHub Release 下载 → 安装脚本一键解压 → screen 后台运行 → Nginx 反代 + HTTPS。
>
> 最后还会讲一讲 **Swagger UI 在反代环境下的 CORS 跨域坑** 以及解决的关键点。

---

## 📋 前置条件

| 项目 | 要求 |
|------|------|
| 服务器 | Linux（Debian / Ubuntu / CentOS 等均可），x64 或 ARM64 |
| 域名 | 已解析到服务器 IP（如果需要 HTTPS） |
| Nginx | 用作反向代理（如果需要走域名 / HTTPS） |
| screen 或 tmux | 让 Go 进程在后台持续运行 |

以下示例中的域名以作者的公开接口 `us-hudiyun.vincentzyu233.cn` 为例，请替换成你自己的域名。

---

## 📐 最终架构概览

```
用户浏览器 / 小程序
    │
    │  HTTPS :443
    ▼
┌─────────────────────────┐
│  Nginx (反向代理)        │
│                         │
│  /nginx_gin_skin/*      │──► http://127.0.0.1:60311/*
│                         │
│  SSL: Let's Encrypt     │
└─────────────────────────┘
    │
    │  HTTP :60311 (本地回环)
    ▼
┌─────────────────────────┐
│  mc-skin-wrap-go        │
│  监听 0.0.0.0:60311     │
│  root_path: /gin_skin_wrap │
└─────────────────────────┘
```

请求路径拆解：

```
浏览器请求:
  https://<你的域名>/nginx_gin_skin/gin_skin_wrap/mcjava/avatar/VincentZyu
                     ^^^^^^^^^^^^^^^^ ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                     Nginx location   转发到 Go 服务的路径

Nginx 收到后:
  去掉 /nginx_gin_skin 前缀，转发到:
  http://127.0.0.1:60311/gin_skin_wrap/mcjava/avatar/VincentZyu

Go 服务收到:
  /gin_skin_wrap/mcjava/avatar/VincentZyu
  ^^^^^^^^^^^^^^ → root_path 匹配 → 处理请求
```

> 这里 `/nginx_gin_skin` 是 Nginx 的 location 前缀，`/gin_skin_wrap` 是 Go 服务自身的 `root_path`，两层前缀各管各的。

---

## 📦 第一步：下载安装

### 方式一：一键安装脚本（推荐）

```bash
# GitHub
curl -fsSL https://raw.githubusercontent.com/VincentZyuApps/mc-skin-wrap-http-server/main/doc/scripts/install.sh | bash

# Gitee 镜像（大陆服务器推荐）
curl -fsSL https://gitee.com/vincent-zyu/mc-skin-wrap-http-server/raw/main/doc/scripts/install_gitee.sh | bash
```

脚本会自动：
1. 检测系统架构（x64 / ARM64）
2. 列出最近 10 个可用版本，让你选择
3. 下载 `.tar.gz` 压缩包
4. 解压到当前目录
5. 询问是否删除压缩包

安装完成后，你会看到类似这样的目录：

```
mc-skin-wrap_<版本>_linux_amd64/
├── mc-skin-wrap-go        # 可执行文件
└── config.json            # 配置文件
```

> 💡 **指定版本安装**: `MC_SKIN_WRAP_VERSION=v0.0.2-beta.7 bash -c "$(curl -fsSL ...install.sh)"`

### 方式二：手动下载

前往 [GitHub Releases](https://github.com/VincentZyuApps/mc-skin-wrap-http-server/releases) 页面，下载对应平台的压缩包，手动解压即可。

---

## ⚙️ 第二步：配置

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

常用字段说明：

| 字段 | 说明 | 生产环境建议 |
|------|------|-------------|
| `host` | 监听地址 | `0.0.0.0`（监听所有网卡） |
| `port` | 监听端口 | 默认 `60311`，按需修改 |
| `root_path` | 路径前缀 | 保持 `/gin_skin_wrap` 即可 |
| `cors_allow_origins` | CORS 允许的来源 | 生产环境建议改为明确域名（见下文 CORS 章节） |
| `proxy_enabled` | 是否为上游请求开代理 | 海外服务器设为 `false` |
| `log_level` | 日志级别 | 生产环境 `info` 或 `warn` |

---

## 🖥️ 第三步：用 screen 后台运行

```bash
# 安装 screen（如果没有）
apt install -y screen     # Debian/Ubuntu
# yum install -y screen   # CentOS/RHEL

# 创建一个名为 mc-skin-wrap 的 screen 会话
screen -S mc-skin-wrap

# 进入解压目录，启动服务
cd /你的安装路径/mc-skin-wrap_<版本>_linux_amd64
./mc-skin-wrap-go

# 看到 "Listening on 0.0.0.0:60311" 之类的日志就说明启动成功了
# 然后按 Ctrl+A, D 分离 screen 会话（服务继续在后台跑）
```

screen 常用速查：

```bash
screen -ls                      # 列出所有会话
screen -r mc-skin-wrap          # 重新连接
screen -S mc-skin-wrap -X quit  # 终止会话

# 在 screen 内:
# Ctrl+A, D    → 分离（detach），服务继续跑
# Ctrl+A, [    → 进入滚动模式，翻看历史日志
# q 或 Esc     → 退出滚动模式
```

> 💡 即使 SSH 断开，screen 里的进程也不会被杀掉。下次 SSH 连上后 `screen -r mc-skin-wrap` 就能回来。

先在本地验证一下服务是否正常：

```bash
curl http://127.0.0.1:60311/gin_skin_wrap/mcjava/avatar/VincentZyu -o /dev/null -w "%{http_code}\n"
# 期望: 200
```

---

## 🔒 第四步：配置 Nginx + HTTPS

如果你只需要通过 `http://<IP>:60311` 直连访问，可以跳过这一步。  
但如果需要 **域名 + HTTPS**（例如给 QQ 小程序调用），那就需要 Nginx 反向代理。

### 4.1 安装 Nginx

```bash
apt update && apt install -y nginx
systemctl enable --now nginx

# 验证
nginx -v
```

### 4.2 申请 SSL 证书（Let's Encrypt）

```bash
# 安装 certbot
apt install -y certbot python3-certbot-nginx

# 申请证书（交互式，会自动修改 nginx 配置）
certbot --nginx -d <你的域名>

# 或者只申请证书，不动 nginx 配置（手动党）
# certbot certonly --nginx -d <你的域名>
```

成功后记住证书路径：

```
/etc/letsencrypt/live/<你的域名>/fullchain.pem
/etc/letsencrypt/live/<你的域名>/privkey.pem
```

自动续期验证：

```bash
certbot renew --dry-run
# 没报错就说明自动续期没问题，以后不用管了
```

> ⚠️ **Cloudflare 用户注意**: 如果域名 DNS 托管在 Cloudflare，需要保持**灰色云 (DNS only)**，
> 否则 certbot 的 HTTP-01 验证会被 CF 拦截。如果需要开 CF 代理，要改用 DNS-01 验证方式。

### 4.3 创建 Nginx 配置文件

```bash
nano /etc/nginx/sites-available/mc-skin-wrap
```

写入：

```nginx
# ============================================================
# mc-skin-wrap-go Nginx 反向代理配置
# 
# 效果:
#   https://<你的域名>/nginx_gin_skin/gin_skin_wrap/mcjava/avatar/VincentZyu
#   → http://127.0.0.1:60311/gin_skin_wrap/mcjava/avatar/VincentZyu
# ============================================================

server {
    listen 80;
    server_name <你的域名>;

    location /nginx_gin_skin/ {
        proxy_pass http://127.0.0.1:60311/;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Prefix /nginx_gin_skin;

        proxy_connect_timeout 10s;
        proxy_read_timeout 30s;
        proxy_send_timeout 30s;
    }
}

server {
    listen 443 ssl;
    server_name <你的域名>;

    ssl_certificate     /etc/letsencrypt/live/<你的域名>/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/<你的域名>/privkey.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    location /nginx_gin_skin/ {
        proxy_pass http://127.0.0.1:60311/;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Prefix /nginx_gin_skin;

        proxy_connect_timeout 10s;
        proxy_read_timeout 30s;
        proxy_send_timeout 30s;
    }
}
```

### 4.4 ⚠️ 关键配置详解

```nginx
location /nginx_gin_skin/ {
    proxy_pass http://127.0.0.1:60311/;
    #                                 ^ 注意这个尾部斜杠！！！
}
```

| `proxy_pass` 写法 | 请求 `/nginx_gin_skin/gin_skin_wrap/xxx` | 实际转发到 |
|---|---|---|
| `http://127.0.0.1:60311/` ✅ | 去掉 `/nginx_gin_skin`，转发 `/gin_skin_wrap/xxx` |
| `http://127.0.0.1:60311` ❌ | 保留完整路径 `/nginx_gin_skin/gin_skin_wrap/xxx` |

我们要的是**去掉** Nginx 前缀，只把 Go 服务自己的路径转发过去，所以 **`proxy_pass` 末尾必须加 `/`**。

还有三个 **必须透传的 header**（下一节解释为什么）：

```nginx
proxy_set_header X-Forwarded-Host   $host;     # 原始域名
proxy_set_header X-Forwarded-Proto  $scheme;   # http 或 https
proxy_set_header X-Forwarded-Prefix /nginx_gin_skin;  # Nginx 的 location 前缀
```

### 4.5 启用配置

```bash
# 创建软链接
ln -s /etc/nginx/sites-available/mc-skin-wrap /etc/nginx/sites-enabled/

# 删除默认配置（可选，避免冲突）
rm -f /etc/nginx/sites-enabled/default

# 测试 + 重载
nginx -t && systemctl reload nginx
```

---

## 🔥 关键踩坑：Swagger UI 跨域 (CORS) 问题

> 这是本次部署遇到的**最大坑**，值得单独拿出来讲。

### 问题现象

Swagger UI 页面能正常打开（`https://<域名>/nginx_gin_skin/gin_skin_wrap/docs/index.html`），
但点击 **"Try it out"** 执行请求时，浏览器控制台报 CORS 错误，请求失败。

### 根因分析

问题**不是**简单的 CORS header 缺失——而是 **Swagger 发错了目标地址**：

1. Swagger UI 从 `/docs/index.html` 加载后，会请求 `swagger_doc.json` 获取 API 描述
2. 旧版的 `swagger_doc.json` 里写死了 `"host": "127.0.0.1:60311"`（Go 服务的本地地址）
3. 浏览器的 "Try it out" 就去请求了 `https://127.0.0.1:60311/...`
4. 这当然不通——于是浏览器报错，**表面上看起来像 CORS 错误**，但实际上是目标地址就不对

### 解决方案：三管齐下

**① Nginx 透传反代信息（上面配置里已经加了）**

```nginx
proxy_set_header X-Forwarded-Host   $host;            # 告诉 Go：外部域名是什么
proxy_set_header X-Forwarded-Proto  $scheme;           # 告诉 Go：外部用的是 http 还是 https
proxy_set_header X-Forwarded-Prefix /nginx_gin_skin;   # 告诉 Go：Nginx 加了什么前缀
```

**② Go 服务动态生成 Swagger 文档**

Go 服务收到请求后，会读取这三个 header，**动态修正** `swagger_doc.json` 里的关键字段：

| 字段 | 不经 Nginx（直连） | 经 Nginx 反代 |
|------|-------------------|--------------|
| `host` | `127.0.0.1:60311` | `<你的域名>` |
| `basePath` | `/gin_skin_wrap` | `/nginx_gin_skin/gin_skin_wrap` |
| `schemes` | `["http"]` | `["https"]` |

这样 Swagger UI 的 "Try it out" 就会自动拼出正确的外部 URL。

**③ Go 服务配了 CORS 响应头**

虽然根因是地址错误，但真正的跨域场景也需要 CORS header。Go 服务通过 `config.json` 中的 `cors_allow_origins` 字段控制：

```json
// 开发/测试：允许所有来源
"cors_allow_origins": ["*"]

// 生产环境：建议限定为你的域名
"cors_allow_origins": [
    "https://your-domain.example.com"
]
```

### 验证方法

部署完成后，用 curl 看一下 `swagger_doc.json` 的内容：

```bash
curl "https://<你的域名>/nginx_gin_skin/gin_skin_wrap/swagger_doc.json" 2>/dev/null | python3 -m json.tool | head -20
```

重点确认这三个字段：

- `"host"` → 应该是你的域名（**不是** `127.0.0.1`）
- `"basePath"` → 应该是 `/nginx_gin_skin/gin_skin_wrap`（**包含** Nginx 前缀）
- `"schemes"` → 应该包含 `"https"`

如果这三个值都对了，Swagger UI 的 "Try it out" 就能正常工作了。

---

## ✅ 第五步：验证部署

### 5.1 本机 curl 测试

```bash
# Go 直连
curl http://127.0.0.1:60311/gin_skin_wrap/mcjava/avatar/VincentZyu \
    -o /dev/null -w "HTTP %{http_code}\n"
# 期望: HTTP 200

# Nginx HTTP 反代
curl http://127.0.0.1/nginx_gin_skin/gin_skin_wrap/mcjava/avatar/VincentZyu \
    -o /dev/null -w "HTTP %{http_code}\n"
# 期望: HTTP 200

# Nginx HTTPS 反代
curl https://<你的域名>/nginx_gin_skin/gin_skin_wrap/mcjava/avatar/VincentZyu \
    -o /dev/null -w "HTTP %{http_code}\n"
# 期望: HTTP 200
```

### 5.2 全端点测试

```bash
DOMAIN="<你的域名>"
BASE="/nginx_gin_skin/gin_skin_wrap"

# 头像
curl "https://${DOMAIN}${BASE}/mcjava/avatar/VincentZyu" -o avatar.png && echo "✅ avatar"

# 皮肤
curl "https://${DOMAIN}${BASE}/mcjava/skin/VincentZyu" -o skin.png && echo "✅ skin"

# 服务器状态
curl "https://${DOMAIN}${BASE}/mcjava/server_status/mc.hypixel.net" && echo "✅ server_status"

# Swagger UI
curl "https://${DOMAIN}${BASE}/docs/index.html" -o /dev/null -w "HTTP %{http_code}\n"
# 期望: HTTP 200
```

### 5.3 浏览器测试

打开 Swagger UI 页面，点 "Try it out" → "Execute"，确认能正常返回结果：

```
https://<你的域名>/nginx_gin_skin/gin_skin_wrap/docs/index.html
```

---

## 🔄 更新版本

```bash
# 1. 回到 screen 会话，停掉旧服务
screen -r mc-skin-wrap
# Ctrl+C 停止

# 2. 用安装脚本下载新版本
cd /你的安装根目录
curl -fsSL https://raw.githubusercontent.com/VincentZyuApps/mc-skin-wrap-http-server/main/doc/scripts/install.sh | bash

# 3. 复制旧配置
cp mc-skin-wrap_<旧版本>_linux_amd64/config.json mc-skin-wrap_<新版本>_linux_amd64/

# 4. 启动新版本
cd mc-skin-wrap_<新版本>_linux_amd64
./mc-skin-wrap-go

# 5. Ctrl+A, D 分离 screen
```

> Nginx 不需要改动——它只转发到 `127.0.0.1:60311`，Go 服务换版本后端口不变。

---

## 🔍 常见问题

### `nginx -t` 报错

```bash
# 常见原因:
# 1. SSL 证书路径不对 → 检查 certbot 是否成功申请
# 2. 端口被占用 → lsof -i :80 / lsof -i :443
# 3. 配置文件语法错误 → 仔细检查花括号和分号
```

### HTTPS 访问返回 502 Bad Gateway

说明 Nginx 连不到后端 Go 服务：

```bash
# 检查 Go 是否在运行
curl http://127.0.0.1:60311/gin_skin_wrap/mcjava/avatar/VincentZyu -o /dev/null -w "%{http_code}\n"

# 如果不是 200，回去看 screen 日志
screen -r mc-skin-wrap

# 看 Nginx 错误日志
tail -20 /var/log/nginx/error.log
```

### certbot 申请证书失败

```bash
# 检查域名解析是否到位
nslookup <你的域名>

# 检查 80 端口可达
curl http://<你的域名>

# 检查 80 端口没被其他程序占用
lsof -i :80
```

### Swagger "Try it out" 还是报 CORS

```bash
# 1. 检查 swagger_doc.json 内容
curl "https://<你的域名>/nginx_gin_skin/gin_skin_wrap/swagger_doc.json" 2>/dev/null \
    | python3 -c "import sys,json; d=json.load(sys.stdin); print('host:', d.get('host')); print('basePath:', d.get('basePath')); print('schemes:', d.get('schemes'))"

# 如果 host 还是 127.0.0.1，说明 Nginx 没有透传 X-Forwarded-* header
# → 检查 nginx 配置里有没有 proxy_set_header X-Forwarded-Host / Proto / Prefix

# 2. 检查 Nginx 配置是否重载了
nginx -t && systemctl reload nginx
```

---

## 📌 访问方式汇总

| 方式 | URL 模式 | 适用场景 |
|------|---------|---------|
| HTTP 直连 | `http://<IP>:60311/gin_skin_wrap/...` | 服务器本地调试 |
| HTTP Nginx | `http://<域名>/nginx_gin_skin/gin_skin_wrap/...` | 无 HTTPS 需求 |
| **HTTPS Nginx** | `https://<域名>/nginx_gin_skin/gin_skin_wrap/...` | **QQ 小程序等正式环境** ✅ |
