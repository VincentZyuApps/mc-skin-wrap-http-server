# 阿里云部署 — Nginx 反代 + Let's Encrypt HTTPS

## 环境信息

| 项目 | 值 |
|------|-----|
| 域名 | `www.example.com` (A 解析 → 服务器公网 IP) |
| Go 服务 | `mc-skin-wrap-go` 监听 `0.0.0.0:12345`，root_path=`/gin_skin_wrap` |
| Nginx location 前缀 | `/nginx_gin_skin/` |
| 最终 URL | `https://www.example.com/nginx_gin_skin/gin_skin_wrap/mcjava/skin/Vincentzyu` |

---

## 最终架构

```
用户浏览器
  │
  │  HTTPS :443
  ▼
Nginx (反代)
  location /nginx_gin_skin/ {
      proxy_pass http://127.0.0.1:12345/;    ← 末尾 / 去掉前缀
  }
  │
  │  HTTP :12345 (回环)
  ▼
mc-skin-wrap-go (监听 0.0.0.0:12345)
```

请求路径拆解：

```
浏览器:  https://www.example.com/nginx_gin_skin/gin_skin_wrap/mcjava/avatar/VincentZyu
                                               ^^^^^^^^^^^^^^^^ ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                                               Nginx 吃掉       转发给 Go

Nginx → Go: http://127.0.0.1:12345/gin_skin_wrap/mcjava/avatar/VincentZyu
                                    ^^^^^^^^^^^^^^ Go 的 root_path 匹配 → 处理请求
```

---

## 步骤 1：安装 Nginx

```bash
apt update && apt install -y nginx
systemctl enable --now nginx
nginx -v   # 验证
```

## 步骤 2：申请 SSL 证书（Let's Encrypt）

```bash
apt install -y certbot python3-certbot-nginx

# 交互式申请，会自动修改 nginx 配置
certbot --nginx -d www.example.com
```

成功后证书路径：
- `/etc/letsencrypt/live/www.example.com/fullchain.pem`
- `/etc/letsencrypt/live/www.example.com/privkey.pem`

验证自动续期：

```bash
certbot renew --dry-run
# 没报错就不用管了
```

## 步骤 3：创建 Nginx 配置

```bash
nano /etc/nginx/sites-available/mc-skin-wrap
```

写入（端口 12345，域名 `www.example.com`）：

```nginx
# ============================================================
# mc-skin-wrap-go Nginx 反向代理配置
# ============================================================

server {
    listen 80;
    server_name www.example.com;

    location /nginx_gin_skin/ {
        proxy_pass http://127.0.0.1:12345/;
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
    server_name www.example.com;

    ssl_certificate     /etc/letsencrypt/live/www.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/www.example.com/privkey.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    location /nginx_gin_skin/ {
        proxy_pass http://127.0.0.1:12345/;
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

### ⚠️ 关键点

```nginx
proxy_pass http://127.0.0.1:12345/;   # ← 末尾必须有 /
```

| proxy_pass 写法 | 请求 `/nginx_gin_skin/gin_skin_wrap/xxx` | 转发到 |
|---|---|---|
| `http://127.0.0.1:12345/` ✅ | 去掉 `/nginx_gin_skin` | `/gin_skin_wrap/xxx` |
| `http://127.0.0.1:12345` ❌ | 保留完整路径 | `/nginx_gin_skin/gin_skin_wrap/xxx` → 404 |

三个必须透传的 header：

```nginx
proxy_set_header X-Forwarded-Host   $host;           # 原始域名
proxy_set_header X-Forwarded-Proto  $scheme;          # http/https
proxy_set_header X-Forwarded-Prefix /nginx_gin_skin;  # location 前缀（Swagger 用）
```

## 步骤 4：启用配置

```bash
ln -s /etc/nginx/sites-available/mc-skin-wrap /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default          # 删除默认配置避免冲突
nginx -t && systemctl reload nginx
```

## 步骤 5：验证

```bash
# Go 直连
curl http://127.0.0.1:12345/gin_skin_wrap/mcjava/avatar/VincentZyu -o /dev/null -w "HTTP %{http_code}\n"
# 期望: HTTP 200

# Nginx HTTP
curl http://127.0.0.1/nginx_gin_skin/gin_skin_wrap/mcjava/avatar/VincentZyu -o /dev/null -w "HTTP %{http_code}\n"
# 期望: HTTP 200

# Nginx HTTPS
curl https://www.example.com/nginx_gin_skin/gin_skin_wrap/mcjava/avatar/VincentZyu -o /dev/null -w "HTTP %{http_code}\n"
# 期望: HTTP 200
```

## 验证全端点

```bash
DOMAIN="www.example.com"
BASE="/nginx_gin_skin/gin_skin_wrap"

curl "https://${DOMAIN}${BASE}/mcjava/avatar/VincentZyu"  -o avatar.png && echo "✅ avatar"
curl "https://${DOMAIN}${BASE}/mcjava/skin/VincentZyu"    -o skin.png   && echo "✅ skin"
curl "https://${DOMAIN}${BASE}/mcjava/server_status/mc.hypixel.net" && echo "✅ server_status"
```

## 常用 Nginx 速查

```bash
nginx -t                              # 测试配置语法
systemctl reload nginx                # 重载配置
systemctl restart nginx               # 重启
tail -20 /var/log/nginx/error.log     # 看错误日志
```

## 最终访问地址

| 接口 | URL |
|------|-----|
| 🎭 玩家头像 | `https://www.example.com/nginx_gin_skin/gin_skin_wrap/mcjava/avatar/{玩家名}` |
| 🧥 玩家皮肤 | `https://www.example.com/nginx_gin_skin/gin_skin_wrap/mcjava/skin/{玩家名}` |
| 📊 服务器状态 | `https://www.example.com/nginx_gin_skin/gin_skin_wrap/mcjava/server_status/{服务器地址}` |

---

# 套 EdgeOne CDN（可选）

> 源站 Nginx 配置好后，可以再套一层腾讯云 EdgeOne CDN 做加速和 HTTPS 托管。
>
> 💡 **此步骤可选** — 如果不需要 CDN 加速，以上 Nginx 配置已可直接使用。

## 环境信息

| 项目 | 值 |
|------|-----|
| EdgeOne 域名 | `eo.example.com`（CNAME → `eo.example.com.eo.dnse4.com`）|
| 源站域名 | `www.example.com`（源站 Nginx HTTPS :443） |
| 最终 URL | `https://eo.example.com/nginx_gin_skin/gin_skin_wrap/mcjava/skin/Vincentzyu` |

## 最终架构

```
用户浏览器
  │
  │  HTTPS :443 → EdgeOne CDN
  ▼
EdgeOne CDN (eo.example.com)
  │
  │  回源 HTTPS → www.example.com:443
  ▼
Nginx (源站, www.example.com)
  location /nginx_gin_skin/ {
      proxy_pass http://127.0.0.1:12345/;
  }
  │
  │  HTTP :12345
  ▼
mc-skin-wrap-go (127.0.0.1:12345)
```

## 步骤 1：在 EdgeOne 控制台添加域名

访问 EdgeOne 控制台 → 域名服务 → 添加域名：

| 配置项 | 值 |
|--------|-----|
| 域名 | `eo.example.com` |
| 源站类型 | IP/Domain name |
| 源站地址 | `www.example.com` |
| 回源协议 | **HTTPS**（强制回源走 443，避免 HTTP 请求走 80 多一次重定向） |
| 回源端口 | 443 |
| 回源 HOST | **Use origin domain name** → `www.example.com`（与 Nginx `server_name` 保持一致） |

提交后，EdgeOne 会分配 CNAME 记录，需要在 DNS 管理处添加：
```
eo.example.com  CNAME → eo.example.com.eo.dnse4.com.
```

## 步骤 2：申请 EdgeOne 免费 HTTPS 证书

EdgeOne 控制台 → 域名服务 → 选中 `eo.example.com` → 证书管理：

1. **配置方式**：选择 `Apply for a free certificate`
2. **验证方式**：选择 `Automatic verification`（自动验证）

> ⚠️ 为什么选自动验证？因为 CNAME 已经配好且生效了，EdgeOne 能自动完成域名验证并签发证书。

3. 点击确认/提交

等 1-5 分钟证书签发并部署。成功后，EdgeOne 会为 `eo.example.com` 自动签发 TrustAsia DV 证书。

## 步骤 3：验证

```bash
# 通过 EdgeOne CDN 访问（注意是 HTTPS，不带端口）
curl -v --connect-timeout 10 "https://eo.example.com/nginx_gin_skin/gin_skin_wrap/mcjava/avatar/Vincentzyu" 2>&1
```

期望输出关键信息：
- `SSL certificate verify ok`（证书验证通过）
- `subject: CN=eo.example.com`（证书域名匹配）
- `HTTP/2 200`（请求成功）
- `eo-cache-status: MISS`（首次未命中，后续请求会变 `HIT`）

## 配置要点总结

| 配置项 | 推荐值 | 说明 |
|--------|--------|------|
| 源站地址 | `www.example.com` | 源站 Nginx 域名，不是 IP |
| 回源协议 | **HTTPS** | 强制 HTTPS 回源，避免多一次 301 跳转 |
| 回源端口 | 443 | 对应源站 Nginx HTTPS 端口 |
| 回源 HOST | Use origin domain name → `www.example.com` | 与 Nginx `server_name` 保持一致 |
| 证书方式 | 申请免费证书 + 自动验证 | CNAME 已生效，可自动完成验证 |

## 最终访问地址（EdgeOne 线路）

| 接口 | URL |
|------|-----|
| 🎭 玩家头像 | `https://eo.example.com/nginx_gin_skin/gin_skin_wrap/mcjava/avatar/{玩家名}` |
| 🧥 玩家皮肤 | `https://eo.example.com/nginx_gin_skin/gin_skin_wrap/mcjava/skin/{玩家名}` |
| 📊 服务器状态 | `https://eo.example.com/nginx_gin_skin/gin_skin_wrap/mcjava/server_status/{服务器地址}` |

## 常见问题

### Q：浏览器访问 `https://eo.example.com/...` 返回 502

**原因：** EdgeOne 证书没配好，或者回源配置不对。先检查：
1. 证书是否已签发（控制台看证书状态）
2. curl 是否提示证书域名不匹配（`subjectAltName does not match`）
3. 回源 HOST 是否设置正确（应该用源站域名 `www.example.com`）

### Q：为什么源站配好了但直接访问 `eo.example.com:12345` 是 502？

EdgeOne CDN 节点只监听 80/443 端口，不接受其他端口的请求。必须走标准 HTTPS :443，且 URL 路径要带 `/nginx_gin_skin` 前缀。
