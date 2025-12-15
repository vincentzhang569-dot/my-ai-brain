@echo off
chcp 65001 >nul
echo ========================================
echo    GitHub 自动推送脚本
echo ========================================
echo.
echo 仓库：my-ai-brain
echo 分支：main
echo 用户：vincentzhang569-dot
echo.

REM 切换到项目目录
cd /d "D:\my-ai-brain"
if errorlevel 1 (
    echo [错误] 无法进入项目目录！
    pause
    exit /b 1
)

REM 检查 Git 状态
echo [1/4] 检查文件变更...
git status --short
echo.

REM 添加所有更改
echo [2/4] 添加所有更改...
git add .
if errorlevel 1 (
    echo [错误] 添加文件失败！
    pause
    exit /b 1
)
echo [✓] 文件已添加
echo.

REM 提交更改（使用时间戳作为提交信息）
echo [3/4] 提交更改...
for /f "tokens=1-3 delims=/ " %%a in ('date /t') do set mydate=%%a-%%b-%%c
for /f "tokens=1-2 delims=: " %%a in ('time /t') do set mytime=%%a:%%b
git commit -m "自动提交 %mydate% %mytime%"
if errorlevel 1 (
    echo [提示] 没有新的更改需要提交
    echo.
    pause
    exit /b 0
)
echo [✓] 更改已提交
echo.

REM 推送到 GitHub
echo [4/4] 推送到 GitHub...
git push origin main
if errorlevel 1 (
    echo.
    echo [错误] 推送失败！可能的原因：
    echo   1. 网络连接问题
    echo   2. 需要输入 GitHub 凭据
    echo   3. 远程仓库有新的提交，需要先拉取
    echo.
    echo 尝试先拉取远程更改...
    git pull origin main --rebase
    if errorlevel 1 (
        echo [错误] 拉取失败，请手动解决冲突
        pause
        exit /b 1
    )
    echo 再次尝试推送...
    git push origin main
    if errorlevel 1 (
        echo [错误] 推送仍然失败，请检查网络和凭据
        pause
        exit /b 1
    )
)

echo.
echo ========================================
echo    ✓ 推送成功！
echo ========================================
echo.
echo 查看仓库：https://github.com/vincentzhang569-dot/my-ai-brain
echo.
pause
