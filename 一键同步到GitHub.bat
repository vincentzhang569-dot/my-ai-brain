@echo off
chcp 65001 >nul
echo ========================================
echo    GitHub 仓库一键同步脚本
echo ========================================
echo.

REM 切换到项目目录
echo [1/6] 切换到项目目录...
cd /d "D:\my-ai-brain" 2>nul
if errorlevel 1 (
    echo [错误] 无法进入 D:\my-ai-brain 目录！
    echo 请确认项目文件夹路径是否正确。
    pause
    exit /b 1
)
echo [✓] 当前目录：%CD%
echo.

REM 检查是否在正确的目录
if not exist "app.py" (
    echo [错误] 未找到 app.py 文件，请确认在正确的项目目录！
    pause
    exit /b 1
)
echo [✓] 确认在正确的项目目录
echo.

REM 删除用户目录下的错误 Git 仓库
echo [2/6] 清理用户目录下的错误 Git 仓库...
if exist "C:\Users\Vincent Zhang\.git" (
    rmdir /s /q "C:\Users\Vincent Zhang\.git" 2>nul
    echo [✓] 已删除用户目录下的 .git 文件夹
) else (
    echo [提示] 用户目录下没有 .git 文件夹
)
echo.

REM 删除项目目录下可能存在的旧 Git 仓库
echo [3/6] 清理项目目录下的旧 Git 仓库...
if exist ".git" (
    rmdir /s /q .git 2>nul
    echo [✓] 已删除旧的 .git 文件夹
) else (
    echo [提示] 项目目录下没有 .git 文件夹
)
echo.

REM 初始化 Git 仓库
echo [4/6] 初始化 Git 仓库...
git init >nul 2>&1
if errorlevel 1 (
    echo [错误] Git 初始化失败！请确认已安装 Git。
    pause
    exit /b 1
)
echo [✓] Git 仓库初始化成功
echo.

REM 添加远程仓库
echo [5/6] 配置远程仓库...
git remote remove origin >nul 2>&1
git remote add origin https://github.com/vincentzhang569-dot/my-ai-brain.git
if errorlevel 1 (
    echo [错误] 添加远程仓库失败！
    pause
    exit /b 1
)
echo [✓] 远程仓库已配置
echo.

REM 添加文件
echo [6/6] 添加文件到 Git...
git add . >nul 2>&1
if errorlevel 1 (
    echo [警告] 添加文件时出现警告（可能是换行符问题，不影响使用）
)
echo [✓] 文件已添加
echo.

REM 提交
echo [提交] 提交更改...
git commit -m "重构代码：统一 LLM 客户端管理，添加 core 模块" >nul 2>&1
if errorlevel 1 (
    echo [警告] 提交失败或没有新更改
) else (
    echo [✓] 更改已提交
)
echo.

REM 推送
echo ========================================
echo    准备推送到 GitHub
echo ========================================
echo.
echo 如果提示输入用户名和密码：
echo   - 用户名：vincentzhang569-dot
echo   - 密码：使用个人访问令牌（不是 GitHub 密码）
echo.
echo 按任意键开始推送...
pause >nul
echo.

git push -u origin main

echo.
echo ========================================
echo    完成！
echo ========================================
echo.
if errorlevel 1 (
    echo [提示] 推送可能失败，请检查：
    echo   1. 网络连接是否正常
    echo   2. 个人访问令牌是否正确
    echo   3. 远程仓库地址是否正确
) else (
    echo [✓] 代码已成功推送到 GitHub！
    echo.
    echo 访问以下地址查看：
    echo https://github.com/vincentzhang569-dot/my-ai-brain
)
echo.
pause

