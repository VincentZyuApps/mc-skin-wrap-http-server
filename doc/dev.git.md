
## git
### 强制远程覆盖本地捏 （生产环境用的
```bash
git reset --hard

# 拉取远程最新版本，强制覆盖本地（用远程 main 分支）
git fetch origin
git reset --hard origin/main
```