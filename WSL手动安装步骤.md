# 🔧 WSL 手动安装步骤（彻底解决 0x80d03805）

## 当前状态
你已经用管理员权限运行了，但还是报错 `0x80d03805`。

这个错误通常是因为 **Windows Update 服务** 或 **系统组件** 有问题。

---

## 🎯 解决方案（按顺序执行）

### 方法 1：使用修复脚本（推荐）

1. **找到** `彻底修复WSL.bat` 文件
2. **右键点击** → **"以管理员身份运行"**
3. 等待脚本执行完成（可能需要 5-10 分钟）
4. 脚本完成后，再次运行：
```powershell
wsl --install
```

---

### 方法 2：手动执行修复步骤

#### 步骤 1：停止 Windows Update 服务

在管理员 PowerShell 中执行：

```powershell
net stop wuauserv
net stop cryptSvc
net stop bits
net stop msiserver
net stop UsoSvc
```

#### 步骤 2：清理 Windows Update 缓存

```powershell
# 重命名缓存文件夹
Rename-Item -Path "$env:windir\SoftwareDistribution" -NewName "SoftwareDistribution.old" -Force
```

#### 步骤 3：重启服务

```powershell
net start msiserver
net start bits
net start cryptSvc
net start wuauserv
net start UsoSvc
```

#### 步骤 4：手动启用 Windows 功能

```powershell
# 启用 WSL
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart

# 启用虚拟机平台
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
```

#### 步骤 5：重启电脑

```powershell
shutdown /r /t 0
```

#### 步骤 6：重启后安装 WSL

重启后，以管理员身份打开 PowerShell：

```powershell
wsl --install
```

---

### 方法 3：通过控制面板启用功能

#### 步骤 1：打开 Windows 功能

1. 按 `Win + R`
2. 输入 `optionalfeatures`，回车
3. 等待列表加载完成

#### 步骤 2：启用功能

勾选以下选项：
- ✅ **适用于 Linux 的 Windows 子系统**
- ✅ **虚拟机平台**

#### 步骤 3：重启电脑

点击"确定"，系统会提示重启，选择"立即重启"

#### 步骤 4：重启后安装

重启后，以管理员身份打开 PowerShell：

```powershell
wsl --install
```

---

### 方法 4：使用 Microsoft Store 安装（最简单）

如果命令行安装一直失败，可以直接用 Microsoft Store：

#### 步骤 1：先启用 Windows 功能

1. 按 `Win + R`，输入 `optionalfeatures`
2. 勾选 **"适用于 Linux 的 Windows 子系统"**
3. 点击"确定"，重启电脑

#### 步骤 2：从 Microsoft Store 安装

1. 打开 **Microsoft Store**（在开始菜单搜索 "Microsoft Store"）
2. 搜索 **"Ubuntu"**
3. 点击 **"获取"** 或 **"安装"**
4. 等待安装完成

#### 步骤 3：设置 Ubuntu

1. 安装完成后，在开始菜单打开 **Ubuntu**
2. 等待初始化（可能需要几分钟）
3. 设置用户名和密码

**完成！** ✅ 这样就不需要 `wsl --install` 命令了。

---

### 方法 5：检查系统更新

有时候系统版本太旧也会导致问题：

#### 步骤 1：检查 Windows 版本

```powershell
winver
```

确保是：
- **Windows 10**：版本 2004 或更高（内部版本 19041+）
- **Windows 11**：所有版本都支持

#### 步骤 2：更新系统

1. 按 `Win + I` 打开设置
2. 进入 **"更新和安全"** → **"Windows 更新"**
3. 点击 **"检查更新"**
4. 安装所有可用更新
5. 重启电脑

#### 步骤 3：再次尝试安装

更新后，以管理员身份运行：

```powershell
wsl --install
```

---

## 🔍 如果所有方法都不行

### 最后的解决方案：完全重置

```powershell
# 1. 卸载现有的 WSL（如果有）
wsl --unregister Ubuntu
wsl --shutdown

# 2. 禁用功能
dism.exe /online /disable-feature /featurename:Microsoft-Windows-Subsystem-Linux /norestart
dism.exe /online /disable-feature /featurename:VirtualMachinePlatform /norestart

# 3. 重启电脑
shutdown /r /t 0

# 4. 重启后，重新启用功能
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart

# 5. 再次重启
shutdown /r /t 0

# 6. 重启后安装
wsl --install
```

---

## 📋 诊断命令

运行这些命令来检查问题：

```powershell
# 检查 WSL 状态
wsl --status

# 检查已安装的 Linux 发行版
wsl --list --verbose

# 检查 Windows 功能是否启用
dism.exe /online /get-featureinfo /featurename:Microsoft-Windows-Subsystem-Linux
dism.exe /online /get-featureinfo /featurename:VirtualMachinePlatform

# 检查 Windows Update 服务状态
Get-Service wuauserv
Get-Service bits
```

---

## 💡 推荐方案

**最简单的方法**：

1. ✅ 使用 **Microsoft Store** 直接安装 Ubuntu（不需要 `wsl --install`）
2. ✅ 只需要在控制面板启用"适用于 Linux 的 Windows 子系统"
3. ✅ 重启后从 Store 安装即可

这样避免了所有命令行安装的问题！

---

## ✅ 验证安装成功

安装完成后，验证：

```powershell
# 查看 WSL 版本
wsl --version

# 查看已安装的发行版
wsl --list --verbose

# 进入 Linux
wsl
```

如果成功进入 Linux 命令行，说明安装成功！🎉












