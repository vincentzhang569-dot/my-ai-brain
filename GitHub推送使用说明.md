# GitHub 自动推送配置说明

## 📋 配置信息

- **GitHub 用户名**: vincentzhang569-dot
- **邮箱**: vincentzhang569@gmail.com
- **仓库地址**: https://github.com/vincentzhang569-dot/my-ai-brain
- **分支**: main

## 🚀 使用方法

### 方法一：一键自动推送（推荐）

直接双击运行 `自动推送GitHub.bat`，脚本会自动完成：
1. 检查文件变更
2. 添加所有更改
3. 提交更改（自动生成时间戳提交信息）
4. 推送到 GitHub

### 方法二：首次配置

如果是第一次使用，先运行 `配置Git自动推送.bat` 完成初始配置。

### 方法三：手动命令

```bash
git add .
git commit -m "你的提交信息"
git push origin main
```

## 🔑 GitHub 凭据配置

### 如果推送时提示输入密码

GitHub 已经不支持使用账户密码推送，需要使用 **Personal Access Token**：

1. 访问 https://github.com/settings/tokens
2. 点击 "Generate new token" → "Generate new token (classic)"
3. 设置 Token 名称（如：my-ai-brain-token）
4. 勾选权限：
   - ✅ repo（完整仓库访问权限）
5. 点击 "Generate token"
6. **复制生成的 Token**（只显示一次！）

### 保存凭据（避免每次输入）

推送时输入：
- 用户名：`vincentzhang569-dot`
- 密码：**粘贴你的 Personal Access Token**

Git 会自动保存凭据（已配置 `credential.helper=store`）。

## 📝 常见问题

### 1. 推送失败：需要先拉取

```bash
git pull origin main --rebase
git push origin main
```

### 2. 查看当前配置

```bash
git config --list
git remote -v
```

### 3. 查看提交历史

```bash
git log --oneline
```

### 4. 撤销最后一次提交（保留更改）

```bash
git reset --soft HEAD~1
```

## 🎯 快速参考

| 操作 | 命令 |
|------|------|
| 查看状态 | `git status` |
| 添加文件 | `git add .` |
| 提交更改 | `git commit -m "信息"` |
| 推送代码 | `git push origin main` |
| 拉取代码 | `git pull origin main` |
| 查看远程仓库 | `git remote -v` |

## 🔗 相关链接

- 仓库地址：https://github.com/vincentzhang569-dot/my-ai-brain
- Token 管理：https://github.com/settings/tokens
- Git 文档：https://git-scm.com/doc
