# Git 操作指南

## 🔄 强制同步远程 (生产环境更新用)

当服务器上的代码需要与远程仓库完全同步时：

```bash
# 丢弃本地所有修改
git reset --hard

# 拉取远程最新版本，强制覆盖本地
git fetch origin
git reset --hard origin/main
```

> ⚠️ **警告**: 此操作会丢弃所有本地修改，请确保重要更改已提交或备份！

## 📝 常用命令

```bash
# 查看状态
git status

# 查看改动统计
git diff HEAD --stat

# 添加所有文件并提交
git add -A
git commit -m "feat: your commit message"

# 推送到远程
git push origin main
```