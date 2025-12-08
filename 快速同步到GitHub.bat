@echo off
chcp 65001 >nul
echo ========================================
echo    GitHub 仓库同步脚本
echo ========================================
echo.

REM 检查是否在正确的目录
if not exist "app.py" (
    echo [错误] 请确保在 D:\my-ai-brain 目录下运行此脚本！
    pause
    exit /b 1
)

echo [1/7] 检查 Git 是否安装...
git --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Git，请先安装：https://git-scm.com/download/win
    pause
    exit /b 1
)
echo [✓] Git 已安装
echo.

echo [2/7] 初始化 Git 仓库...
if exist ".git" (
    echo [提示] Git 仓库已存在，跳过初始化
) else (
    git init
    echo [✓] Git 仓库初始化完成
)
echo.

echo [3/7] 检查远程仓库配置...
git remote get-url origin >nul 2>&1
if errorlevel 1 (
    echo [提示] 添加远程仓库地址...
    git remote add origin https://github.com/vincentzhang569-dot/my-ai-brain.git
    echo [✓] 远程仓库已添加
) else (
    echo [提示] 远程仓库已存在，检查地址...
    git remote set-url origin https://github.com/vincentzhang569-dot/my-ai-brain.git
    echo [✓] 远程仓库地址已更新
)
echo.

echo [4/7] 拉取远程仓库内容（如果有）...
git pull origin main --allow-unrelated-histories 2>nul
if errorlevel 1 (
    echo [提示] 拉取失败，可能是第一次推送，继续...
)
echo.

echo [5/7] 添加所有文件到 Git...
git add .
echo [✓] 文件已添加
echo.

echo [6/7] 提交更改...
git commit -m "重构代码：统一 LLM 客户端管理，添加 core 模块" 2>nul
if errorlevel 1 (
    echo [提示] 没有新更改需要提交，或提交失败
) else (
    echo [✓] 更改已提交
)
echo.

echo [7/7] 推送到 GitHub...
echo [提示] 如果提示输入用户名和密码：
echo        - 用户名：你的 GitHub 用户名
echo        - 密码：使用个人访问令牌（不是 GitHub 密码）
echo.
git push -u origin main

echo.
echo ========================================
echo    完成！请检查上面的输出信息
echo ========================================
echo.
echo 如果推送成功，访问以下地址查看：
echo https://github.com/vincentzhang569-dot/my-ai-brain
echo.
pause

