@echo off
chcp 65001 >nul
echo ========================================
echo    推送到 GitHub
echo ========================================
echo.
echo 请准备好你的个人访问令牌
echo.
echo 当提示输入时：
echo   用户名：vincentzhang569-dot
echo   密码：粘贴你的个人访问令牌（不是 GitHub 密码）
echo.
echo 按任意键开始推送...
pause >nul
echo.

cd /d D:\my-ai-brain
git push -u origin master

echo.
if errorlevel 1 (
    echo [错误] 推送失败，请检查：
    echo   1. 个人访问令牌是否正确
    echo   2. 网络连接是否正常
) else (
    echo [成功] 代码已推送到 GitHub！
    echo.
    echo 访问以下地址查看：
    echo https://github.com/vincentzhang569-dot/my-ai-brain
)
echo.
pause













