## python version
`3.12.5`

```bash
python -m venv venv

./venv/Scripts/Activate #win

source ./venv/bin/activate #linux

pip install fastapi uvicorn requests
pip freeze > requirements.txt
pip install -r requirements.txt

uvicorn main:app --host 0.0.0.0 --port 8418 --root-path /fastapi_skin_wrap --reload
uvicorn main:app --host 0.0.0.0 --port 8418 --root-path /fastapi_skin_wrap

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
        proxy_pass http://127.0.0.1:8418/;
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