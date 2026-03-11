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
```

## 🌲 项目目录树

### 生成命令

```bash
# WSL / Linux / macOS
# 安装 tree (如果没有)
# Ubuntu/Debian: sudo apt install tree
# macOS: brew install tree

# 忽略 dist、.venv、__pycache__ 目录
tree -I "dist|.venv|__pycache__"
```

> 💡 **提示**: `tmp/` 目录包含敏感数据，已在 `.gitignore` 中忽略。`dist/` 为构建产物目录，同样不入库。
