# Go 开发指南

## 📦 依赖准备

Go 版本要求: `>= 1.24`

```bash
# 进入 go 目录
cd go

# 初始化依赖 (如果需要)
go mod tidy
```

---

## 🏗️ 交叉编译 (Build All)

项目使用 `go/build.py` 统一管理构建，支持 Windows / Linux / macOS x AMD64 / ARM64。

### Windows PowerShell

```powershell
# 设置临时代理 (如果 go mod 下载慢)
$Env:HTTP_PROXY = "http://192.168.31.233:7890"
$Env:HTTPS_PROXY = "http://192.168.31.233:7890"

# 验证代理连通性
Invoke-WebRequest -Uri "https://www.google.com" -Method Head -UseBasicParsing

# 构建所有平台 (在项目根目录下运行)
python .\go\build.py

# 或者构建指定平台
python .\go\build.py --os windows --arch amd64

# 解压 (在项目根目录下运行)
7z x .\dist\mc-skin-wrap_0.0.2-beta.4+20260311_windows_amd64.zip -odist\
```

### WSL / Linux Bash

```bash
# 设置临时代理
export HTTP_PROXY="http://192.168.31.233:7890"
export HTTPS_PROXY="http://192.168.31.233:7890"

# 验证代理连通性
curl -I https://www.google.com

# 构建所有平台 (在项目根目录下运行)
python3 go/build.py

# 或者构建指定平台
python3 go/build.py --os linux --arch amd64

# 解压 (在项目根目录下运行)
7z x dist/mc-skin-wrap_0.0.2-beta.4+20260311_linux_amd64.tar.gz -odist/
7z x dist/mc-skin-wrap_0.0.2-beta.4+20260311_linux_amd64.tar -odist/ && rm dist/*.tar
```


## curl test

### PowerShell
```powershell
$H = "127.0.0.1"
$P = 60311
$R = "/gin_skin_wrap"  # root_path 前缀

# 获取头像
curl "http://${H}:${P}${R}/mcjava/avatar/VincentZyu" -o avatar.png

# 获取皮肤
curl "http://${H}:${P}${R}/mcjava/skin/VincentZyu" -o skin.png

# 获取服务器状态
curl "http://${H}:${P}${R}/mcjava/server_status/mc.hypixel.net"

# Swagger 文档页
curl "http://${H}:${P}${R}/docs/"

# 输出完整 URL (方便复制到浏览器/Postman)
Write-Host "`n===== URLs =====" -ForegroundColor Cyan
Write-Host "Avatar:"; Write-Host "http://${H}:${P}${R}/mcjava/avatar/VincentZyu"
Write-Host "Skin:"; Write-Host "http://${H}:${P}${R}/mcjava/skin/VincentZyu"
Write-Host "Status:"; Write-Host "http://${H}:${P}${R}/mcjava/server_status/mc.hypixel.net"
Write-Host "Docs:"; Write-Host "http://${H}:${P}${R}/docs/"
```

### Bash
```bash
H="127.0.0.1"
P=60311
R="/gin_skin_wrap"  # root_path 前缀

# 获取头像
curl "http://${H}:${P}${R}/mcjava/avatar/VincentZyu" -o avatar.png

# 获取皮肤
curl "http://${H}:${P}${R}/mcjava/skin/VincentZyu" -o skin.png

# 获取服务器状态
curl "http://${H}:${P}${R}/mcjava/server_status/mc.hypixel.net"

# Swagger 文档页
curl "http://${H}:${P}${R}/docs/"

# 输出完整 URL (方便复制到浏览器/Postman)
echo -e "\n===== URLs ====="
echo "Avatar:"; echo "http://${H}:${P}${R}/mcjava/avatar/VincentZyu"
echo "Skin:"; echo "http://${H}:${P}${R}/mcjava/skin/VincentZyu"
echo "Status:"; echo "http://${H}:${P}${R}/mcjava/server_status/mc.hypixel.net"
echo "Docs:"; echo "http://${H}:${P}${R}/docs/"
```

## local dev py script

本地开发辅助脚本，自动完成以下工作：
- 更新本文档中的版本号和环境变量 (`$H`, `$P`, `$R`)
- 解压当前架构的压缩包 (已存在则跳过，除非 `--clear`)
- 输出 cd + 运行命令 + curl 测试命令 + 浏览器 URL

```bash
python ./go/local_dev.py --help
python ./go/local_dev.py                    # 使用默认值
python ./go/local_dev.py --host 0.0.0.0     # 指定 host
python ./go/local_dev.py --port 8080        # 指定 port
python ./go/local_dev.py --root-path /api   # 指定 root_path
python ./go/local_dev.py --arch arm64       # 指定架构
python ./go/local_dev.py --clear            # 强制重新解压
```

---

## 🔧 Swagger 文档生成

API 文档使用 [swaggo/swag](https://github.com/swaggo/swag) 生成。

### 安装 swag

```bash
go install github.com/swaggo/swag/cmd/swag@latest
```

### 生成文档

> **注意**: `go install` 安装的二进制位置取决于环境变量：
> - 如果设置了 `GOBIN`，则在 `$GOBIN`
> - 否则在 `$GOPATH/bin`
> 
> 可以用 `go env GOBIN` 和 `go env GOPATH` 查看具体路径。

#### PowerShell
```powershell
cd go

# 优先使用 GOBIN，否则 fallback 到 GOPATH/bin
$gobin = $(go env GOBIN)
if (-not $gobin) { $gobin = "$(go env GOPATH)\bin" }
& "$gobin\swag.exe" init

# 或者一行搞定 (如果确定设置了 GOBIN)
& "$(go env GOBIN)\swag.exe" init
```

#### Bash
```bash
cd go

# 优先使用 GOBIN，否则 fallback 到 GOPATH/bin
gobin=$(go env GOBIN)
[ -z "$gobin" ] && gobin="$(go env GOPATH)/bin"
"$gobin/swag" init

# 或者一行搞定 (如果确定设置了 GOBIN)
"$(go env GOBIN)/swag" init
```