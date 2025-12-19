@echo off
chcp 65001 >nul
echo ========================================
echo    Git 配置验证脚本
echo ========================================
echo.

cd /d D:\my-ai-brain
if errorlevel 1 (
    echo [错误] 无法进入项目目录！
    pause
    exit /b 1
)

echo [1/4] 检查 Git 仓库状态...
git status
echo.

echo [2/4] 检查远程仓库配置...
git remote -v
echo.

echo [3/4] 检查最近的提交记录...
git log --oneline -5
echo.

echo [4/4] 检查当前分支...
git branch -a
echo.

echo ========================================
echo    验证完成
echo ========================================
echo.
echo 如果看到：
echo   - origin 指向你的 GitHub 仓库 ✅
echo   - 有提交记录 ✅
echo   - 当前在 master 分支 ✅
echo.
echo 说明配置正确！
echo.
pause













