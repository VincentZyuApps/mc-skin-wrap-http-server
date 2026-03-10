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

# 获取头像
curl "http://${H}:${P}/mcjava/avatar/VincentZyu" -o avatar.png

# 获取皮肤
curl "http://${H}:${P}/mcjava/skin/VincentZyu" -o skin.png

# 获取服务器状态
curl "http://${H}:${P}/mcjava/server_status/mc.hypixel.net"

# FastAPI 自动生成的文档页
curl "http://${H}:${P}/docs"
```

### Bash
```bash
H="127.0.0.1"
P=58418

# 获取头像
curl "http://${H}:${P}/mcjava/avatar/VincentZyu" -o avatar.png

# 获取皮肤
curl "http://${H}:${P}/mcjava/skin/VincentZyu" -o skin.png

# 获取服务器状态
curl "http://${H}:${P}/mcjava/server_status/mc.hypixel.net"

# FastAPI 自动生成的文档页
curl "http://${H}:${P}/docs"
```

## nginx

```bash
sudo apt update
sudo apt install nginx certbot python3-certbot-nginx -y

sudo cat  /etc/nginx/sites-available/fastapi_skin_wrap
sudo nano /etc/nginx/sites-available/fastapi_skin_wrap

```


```nginx
server {
    listen 80;
    server_name vkvm.vincentzyu233.xyz;

    location /fastapi_skin_wrap/ {
        proxy_pass http://127.0.0.1:58418/;
        rewrite ^/fastapi_skin_wrap(/.*)$ $1 break;

        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # 解决 /fastapi_skin_wrap/docs 页面资源加载问题
        proxy_redirect off;
        proxy_set_header X-Script-Name /fastapi_skin_wrap;
    }
}

```


```bash
sudo ln -s /etc/nginx/sites-available/fastapi_skin_wrap /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

sudo certbot --nginx -d vkvm.vincentzyu233.xyz

```



- nginx command
```bash
sudo nginx -t
sudo systemctl reload nginx

sudo nginx -t	#检查配置文件是否有语法错误
sudo nginx -s reload	#平滑重载配置，推荐使用
sudo systemctl restart nginx	#重启 Nginx 服务（配置变动+崩溃恢复）
sudo systemctl start nginx	#启动 Nginx
sudo systemctl stop nginx	#停止 Nginx
sudo systemctl status nginx	#查看 Nginx 当前运行状态
```

## git
```bash
git reset --hard

# 拉取远程最新版本，强制覆盖本地（用远程 main 分支）
git fetch origin
git reset --hard origin/main
```