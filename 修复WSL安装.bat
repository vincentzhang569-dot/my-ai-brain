@echo off
chcp 65001 >nul
echo ========================================
echo    WSL 安装问题修复脚本
echo ========================================
echo.

echo [1/5] 检查管理员权限...
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ❌ 错误：需要管理员权限！
    echo.
    echo 请右键点击此文件，选择"以管理员身份运行"
    pause
    exit /b 1
)
echo ✅ 管理员权限确认
echo.

echo [2/5] 启动 Windows Update 服务...
net start wuauserv >nul 2>&1
net start cryptSvc >nul 2>&1
net start bits >nul 2>&1
net start msiserver >nul 2>&1
echo ✅ 服务已启动
echo.

echo [3/5] 重置 Windows Update 组件...
net stop wuauserv
net stop cryptSvc
net stop bits
net stop msiserver
timeout /t 2 /nobreak >nul
net start wuauserv
net start cryptSvc
net start bits
net start msiserver
echo ✅ 组件已重置
echo.

echo [4/5] 启用必要的 Windows 功能...
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
echo ✅ 功能已启用
echo.

echo [5/5] 尝试安装 WSL...
wsl --install
echo.

echo ========================================
echo    如果还有问题，请尝试：
echo    1. 重启电脑后再运行 wsl --install
echo    2. 检查网络连接
echo    3. 手动下载 WSL 更新包
echo ========================================
pause











