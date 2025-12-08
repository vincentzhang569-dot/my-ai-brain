@echo off
chcp 65001 >nul
title WSL 彻底修复工具
color 0A

echo ========================================
echo    WSL 彻底修复工具 (管理员版)
echo ========================================
echo.

:: 检查管理员权限
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [错误] 需要管理员权限！
    echo 请右键点击此文件，选择"以管理员身份运行"
    pause
    exit /b 1
)

echo [✓] 管理员权限确认
echo.

echo [步骤 1/6] 停止相关服务...
net stop wuauserv >nul 2>&1
net stop cryptSvc >nul 2>&1
net stop bits >nul 2>&1
net stop msiserver >nul 2>&1
net stop UsoSvc >nul 2>&1
timeout /t 2 /nobreak >nul
echo [✓] 服务已停止
echo.

echo [步骤 2/6] 清理 Windows Update 缓存...
if exist "%windir%\SoftwareDistribution" (
    ren "%windir%\SoftwareDistribution" "SoftwareDistribution.old"
    echo [✓] 缓存已清理
) else (
    echo [!] 缓存文件夹不存在，跳过
)
echo.

echo [步骤 3/6] 重新启动 Windows Update 服务...
net start msiserver >nul 2>&1
net start bits >nul 2>&1
net start cryptSvc >nul 2>&1
net start wuauserv >nul 2>&1
net start UsoSvc >nul 2>&1
timeout /t 3 /nobreak >nul
echo [✓] 服务已重启
echo.

echo [步骤 4/6] 启用 Windows 功能（这可能需要几分钟）...
echo 正在启用"适用于 Linux 的 Windows 子系统"...
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart /quiet
if %errorLevel% equ 0 (
    echo [✓] WSL 功能已启用
) else (
    echo [!] WSL 功能启用可能有问题，继续尝试...
)
echo.

echo 正在启用"虚拟机平台"...
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart /quiet
if %errorLevel% equ 0 (
    echo [✓] 虚拟机平台已启用
) else (
    echo [!] 虚拟机平台启用可能有问题，继续尝试...
)
echo.

echo [步骤 5/6] 检查 WSL 状态...
wsl --status
echo.

echo [步骤 6/6] 尝试安装 WSL...
echo 这可能需要几分钟，请耐心等待...
echo.
wsl --install
echo.

echo ========================================
echo    修复完成！
echo ========================================
echo.
echo 如果还有错误，请尝试：
echo 1. 重启电脑后再运行 wsl --install
echo 2. 检查网络连接
echo 3. 运行 Windows Update 更新系统
echo.
pause

