# GitHub Actions Workflow Guide

This repository uses GitHub Actions for continuous integration and deployment. The workflow is automatically triggered when you push code to the `main` branch.

## 📋 Overview

The CI/CD pipeline is driven entirely by **keywords in the commit message**. When you push to the `main` branch, simply include the corresponding keywords in your commit message, and GitHub Actions will automatically perform the subsequent work.

## 🔑 Keywords

| Keyword in Commit Message | Build (Multi-Platform) | GitHub Release | Scoop / AUR / npm | PyPI | crates.io | Benchmark |
|----------------------|:---:|:---:|:---:|:---:|:---:|:---:|
| `build action` | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| `build release` | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| `build publish` | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| `publish from release` | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ |
| `pypi publish` | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ |
| `crates publish` | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ |
| `run benchmark` | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |

### Supported Platforms
The `build` job generates binaries for the following platforms:
- **Windows**: x64, ARM64
- **Linux**: x64, ARM64
- **macOS**: x64, ARM64 (Apple Silicon)

## 🛠️ Workflow Structure

1.  **Check Commit Message**:
    - Parses the commit message to determine which jobs to run.
    - Extracts version number from `go/main.go`.
2.  **Sync Code**:
    - Automatically syncs code to Gitee mirror (if configured).
3.  **Build**:
    - Uses Go 1.24+ to compile static binaries (`CGO_ENABLED=0`).
    - Outputs optimized binaries (stripped symbols via `-ldflags "-s -w"`).
4.  **Release**:
    - Creates a GitHub Release with the extracted version tag.
    - Uploads all built artifacts.
