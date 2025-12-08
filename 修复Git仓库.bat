@echo off
chcp 65001 >nul
echo ========================================
echo    修复 Git 仓库位置
echo ========================================
echo.

echo [1/4] 删除用户目录下的错误 Git 仓库...
if exist "C:\Users\Vincent Zhang\.git" (
    rmdir /s /q "C:\Users\Vincent Zhang\.git"
    echo [✓] 已删除用户目录下的 .git 文件夹
) else (
    echo [提示] 用户目录下没有 .git 文件夹
)
echo.

echo [2/4] 进入项目目录...
cd /d D:\my-ai-brain
if errorlevel 1 (
    echo [错误] 无法进入 D:\my-ai-brain 目录，请检查路径是否正确！
    pause
    exit /b 1
)
echo [✓] 当前目录：%CD%
echo.

echo [3/4] 删除项目目录下可能存在的旧 Git 仓库...
if exist ".git" (
    rmdir /s /q .git
    echo [✓] 已删除旧的 .git 文件夹
) else (
    echo [提示] 项目目录下没有 .git 文件夹
)
echo.

echo [4/4] 初始化新的 Git 仓库...
git init
if errorlevel 1 (
    echo [错误] Git 初始化失败！
    pause
    exit /b 1
)
echo [✓] Git 仓库初始化成功
echo.

echo ========================================
echo    下一步操作
echo ========================================
echo.
echo 请继续执行以下命令：
echo.
echo git remote add origin https://github.com/vincentzhang569-dot/my-ai-brain.git
echo git add .
echo git commit -m "重构代码：统一 LLM 客户端管理，添加 core 模块"
echo git push -u origin main
echo.
pause

