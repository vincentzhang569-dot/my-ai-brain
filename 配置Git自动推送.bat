@echo off
chcp 65001 >nul
echo ========================================
echo    配置 Git 自动推送到 GitHub
echo ========================================
echo.

cd /d "D:\my-ai-brain"

echo [1/5] 配置用户信息...
git config user.name "vincentzhang569-dot"
git config user.email "vincentzhang569@gmail.com"
echo [✓] 用户名：vincentzhang569-dot
echo [✓] 邮箱：vincentzhang569@gmail.com
echo.

echo [2/5] 配置远程仓库...
git remote remove origin 2>nul
git remote add origin https://github.com/vincentzhang569-dot/my-ai-brain.git
echo [✓] 远程仓库：https://github.com/vincentzhang569-dot/my-ai-brain.git
echo.

echo [3/5] 配置默认分支为 main...
git branch -M main 2>nul
echo [✓] 默认分支：main
echo.

echo [4/5] 配置推送策略...
git config push.default simple
git config pull.rebase false
echo [✓] 推送策略已配置
echo.

echo [5/5] 设置上游分支...
git push -u origin main 2>nul
if errorlevel 1 (
    echo [提示] 首次推送可能需要输入凭据
    echo.
    echo 如果提示输入密码，请使用 GitHub Personal Access Token
    echo 不要使用 GitHub 账户密码！
    echo.
    echo 获取 Token：https://github.com/settings/tokens
    echo.
) else (
    echo [✓] 上游分支已设置
)
echo.

echo ========================================
echo    配置完成！
echo ========================================
echo.
echo 现在你可以使用以下方式推送代码：
echo   1. 双击运行 "自动推送GitHub.bat"
echo   2. 或在命令行执行：git push
echo.
pause
