@echo off
chcp 65001 >nul
cd /d "D:\my-ai-brain"

echo 正在推送到 GitHub...
echo.

git -c core.pager=cat add .
git -c core.pager=cat commit -m "修复首页标题样式：硬核风格大字体+清晰颜色，新增自动推送脚本"
git -c core.pager=cat push origin main

if errorlevel 1 (
    echo.
    echo 推送失败，尝试先拉取...
    git -c core.pager=cat pull origin main --rebase
    git -c core.pager=cat push origin main
)

echo.
echo 完成！
pause
