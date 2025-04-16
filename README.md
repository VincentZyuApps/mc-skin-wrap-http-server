## python version
`3.12.5`

```bash
python -m venv venv

./venv/Scripts/Activate

source ./venv/bin/activate

pip install fastapi uvicorn requests
pip freeze > requirements.txt
pip install -r requirements.txt

uvicorn main:app --reload --host 0.0.0.0 --port 8418
```


## nginx

```bash


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