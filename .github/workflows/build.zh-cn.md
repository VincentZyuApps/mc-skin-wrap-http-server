# GitHub Actions 工作流指南

本仓库使用 GitHub Actions 进行持续集成和部署。当代码推送到 `main` 分支时，工作流会自动触发。

## 📋 概述

CI/CD 流水线完全由 **commit 信息中的关键词** 驱动。推送到 `main` 分支时，只需在 commit message 中包含对应关键词，GitHub Actions 会自动完成后续工作。

## 🔑 关键词

| Commit 信息中的关键词 | 构建 (多平台) | GitHub Release | Scoop / AUR / npm | PyPI | crates.io | 基准测试 (Benchmark) |
|----------------------|:---:|:---:|:---:|:---:|:---:|:---:|
| `build action` | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| `build release` | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| `build publish` | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| `publish from release` | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ |
| `pypi publish` | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ |
| `crates publish` | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ |
| `run benchmark` | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |

### 支持的构建平台
`build` 任务会为以下平台生成二进制文件：
- **Windows**: x64, ARM64
- **Linux**: x64, ARM64
- **macOS**: x64, ARM64 (Apple Silicon)

## 🛠️ 工作流结构

1.  **检查提交信息 (Check Commit Message)**:
    - 解析 commit message 以决定运行哪些任务。
    - 从 `go/main.go` 中提取版本号。
2.  **同步代码 (Sync Code)**:
    - 自动将代码同步到 Gitee 镜像仓库（如果配置了）。
3.  **构建 (Build)**:
    - 使用 Go 1.24+ 编译静态二进制文件 (`CGO_ENABLED=0`)。
    - 输出优化后的二进制文件（通过 `-ldflags "-s -w"` 去除符号表）。
4.  **发布 (Release)**:
    - 创建带有提取版本号标签的 GitHub Release。
    - 上传所有构建产物。
