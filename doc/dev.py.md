## python version
`3.12.5`

### cp config file
```
cd py
cp config.example.json config.json
```

### venv
```bash
python -m venv venv
./venv/Scripts/Activate #win

source ./venv/bin/activate #linux

pip install fastapi uvicorn requests
pip freeze > requirements.txt
pip install -r requirements.txt

# 启动（配置项在 py/config.json 中设置）
cd py
uvicorn main:app --reload   # 或者直接: python main.py --reload
python main.py              # 生产模式

```

### uv
```shell
uv venv --python 3.12

uv pip install fastapi uvicorn requests
uv pip freeze > requirements.txt
pip install -r requirements.txt

# 启动（配置项在 py/config.json 中设置，不需要再写一长串参数了）
cd py
uv run python main.py --reload   # 开发模式（热重载）
uv run python main.py            # 生产模式
```

## curl test

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

# FastAPI 自动生成的文档页
curl "http://${H}:${P}${R}/docs"

# 输出完整 URL (方便复制到浏览器/Postman)
Write-Host "`n===== URLs =====" -ForegroundColor Cyan
Write-Host "Avatar:"; Write-Host "http://${H}:${P}${R}/mcjava/avatar/VincentZyu"
Write-Host "Skin:"; Write-Host "http://${H}:${P}${R}/mcjava/skin/VincentZyu"
Write-Host "Status:"; Write-Host "http://${H}:${P}${R}/mcjava/server_status/mc.hypixel.net"
Write-Host "Docs:"; Write-Host "http://${H}:${P}${R}/docs"
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

# FastAPI 自动生成的文档页
curl "http://${H}:${P}${R}/docs"

# 输出完整 URL (方便复制到浏览器/Postman)
echo -e "\n===== URLs ====="
echo "Avatar:"; echo "http://${H}:${P}${R}/mcjava/avatar/VincentZyu"
echo "Skin:"; echo "http://${H}:${P}${R}/mcjava/skin/VincentZyu"
echo "Status:"; echo "http://${H}:${P}${R}/mcjava/server_status/mc.hypixel.net"
echo "Docs:"; echo "http://${H}:${P}${R}/docs"
```
