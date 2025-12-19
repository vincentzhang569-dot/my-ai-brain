# 🐧 Linux 保姆级入门教程

## 📚 目录
1. [什么是 Linux？](#什么是-linux)
2. [如何开始学习？](#如何开始学习)
3. [最基础的 10 个指令](#最基础的-10-个指令)
4. [文件操作（核心技能）](#文件操作核心技能)
5. [日常使用场景](#日常使用场景)
6. [常见问题解决](#常见问题解决)

---

## 🤔 什么是 Linux？

**Linux** 是一个**操作系统**（就像 Windows、macOS），但它是：
- 🆓 **免费开源**（不用花钱）
- 💪 **稳定强大**（服务器首选）
- 🔧 **高度可定制**（想怎么改就怎么改）

**为什么学 Linux？**
- 💼 程序员必备技能
- 🚀 部署网站、服务器都用它
- 🎯 很多工具只在 Linux 上运行

---

## 💻 如何开始学习？

### 方法 1：Windows 上安装 WSL（推荐新手）

**WSL = Windows Subsystem for Linux**（在 Windows 里运行 Linux）

#### 安装步骤：
1. 打开 **PowerShell（管理员）**
2. 输入：
```powershell
wsl --install
```
3. 重启电脑
4. 打开 **Ubuntu**（会自动出现在开始菜单）

**完成！** ✅ 你现在有 Linux 了！

---

### 方法 2：使用在线终端（最简单）

访问这些网站，直接体验 Linux：
- **Replit**：https://replit.com/
- **JSLinux**：https://bellard.org/jslinux/
- **Webminal**：https://www.webminal.org/

---

### 方法 3：虚拟机（最真实）

1. 下载 **VirtualBox**（免费）
2. 下载 **Ubuntu** 镜像
3. 在虚拟机里安装

---

## ⭐ 最基础的 10 个指令

### 1️⃣ `pwd` - 我在哪里？
**作用**：显示当前所在的文件夹路径

```bash
pwd
```

**输出示例**：
```
/home/username
```

---

### 2️⃣ `ls` - 看看有什么文件
**作用**：列出当前文件夹里的所有文件和文件夹

```bash
ls              # 简单列表
ls -l           # 详细列表（显示权限、大小等）
ls -a           # 显示隐藏文件（以.开头的）
ls -la          # 详细列表 + 隐藏文件
```

**输出示例**：
```
app.py  README.md  folder1  folder2
```

---

### 3️⃣ `cd` - 进入文件夹
**作用**：切换目录（就像在 Windows 里双击文件夹）

```bash
cd folder1              # 进入 folder1 文件夹
cd ..                   # 返回上一级
cd ~                    # 回到用户主目录
cd /home/username        # 进入绝对路径
```

**常用组合**：
```bash
cd ~                    # 回到主目录
cd -                   # 回到上一个目录
```

---

### 4️⃣ `mkdir` - 创建文件夹
**作用**：新建一个文件夹

```bash
mkdir myproject         # 创建 myproject 文件夹
mkdir -p folder1/folder2  # 创建多层文件夹
```

---

### 5️⃣ `touch` - 创建文件
**作用**：创建一个空文件

```bash
touch test.txt          # 创建 test.txt 文件
touch file1.py file2.py  # 一次创建多个文件
```

---

### 6️⃣ `cat` - 查看文件内容
**作用**：显示文件的全部内容

```bash
cat README.md           # 查看 README.md 的内容
cat app.py              # 查看 app.py 的内容
```

**适合**：查看小文件（几行到几十行）

---

### 7️⃣ `nano` - 编辑文件（最简单）
**作用**：打开文本编辑器编辑文件

```bash
nano README.md          # 编辑 README.md
```

**操作**：
- 直接打字编辑
- `Ctrl + O` 保存
- `Ctrl + X` 退出

---

### 8️⃣ `cp` - 复制文件
**作用**：复制文件或文件夹

```bash
cp file1.txt file2.txt           # 复制文件
cp -r folder1 folder2            # 复制文件夹（-r 表示递归）
```

---

### 9️⃣ `mv` - 移动/重命名
**作用**：移动文件或重命名

```bash
mv file1.txt folder1/            # 移动文件到文件夹
mv oldname.txt newname.txt       # 重命名文件
```

---

### 🔟 `rm` - 删除文件（小心使用！）
**作用**：删除文件或文件夹

```bash
rm file.txt              # 删除文件
rm -r folder1            # 删除文件夹（-r 表示递归）
rm -rf folder1           # 强制删除（-f 表示强制，危险！）
```

**⚠️ 警告**：`rm -rf` 会永久删除，无法恢复！使用前要确认！

---

## 📁 文件操作（核心技能）

### 查看文件内容的不同方法

#### 1. `cat` - 查看全部内容
```bash
cat file.txt
```
**适合**：小文件（< 100 行）

---

#### 2. `less` - 分页查看（推荐）
```bash
less file.txt
```
**操作**：
- `空格` = 向下翻页
- `q` = 退出
- `/关键词` = 搜索

---

#### 3. `head` - 看前几行
```bash
head file.txt           # 看前 10 行
head -n 20 file.txt     # 看前 20 行
```

---

#### 4. `tail` - 看后几行
```bash
tail file.txt           # 看后 10 行
tail -n 20 file.txt     # 看后 20 行
tail -f log.txt         # 实时查看日志（-f 表示跟随）
```

---

### 查找文件

#### `find` - 查找文件
```bash
find . -name "*.py"           # 查找所有 .py 文件
find . -name "app.py"          # 查找 app.py
find /home -type f -name "*.txt"  # 在 /home 下找所有 .txt 文件
```

---

#### `grep` - 在文件里搜索内容
```bash
grep "关键词" file.txt         # 在文件里找关键词
grep -r "关键词" folder/       # 在文件夹里递归搜索
grep -i "关键词" file.txt      # 忽略大小写（-i）
```

---

## 🔄 日常使用场景

### 场景 1：查看项目文件

```bash
# 1. 进入项目文件夹
cd ~/myproject

# 2. 看看有什么文件
ls -la

# 3. 查看 README
cat README.md

# 4. 查看 Python 文件的前几行
head app.py
```

---

### 场景 2：编辑配置文件

```bash
# 1. 找到配置文件
find . -name "config.py"

# 2. 编辑它
nano config.py

# 3. 保存（Ctrl+O）并退出（Ctrl+X）

# 4. 查看修改后的内容
cat config.py
```

---

### 场景 3：管理日志文件

```bash
# 1. 查看日志最后 50 行
tail -n 50 app.log

# 2. 实时监控日志（新内容会自动显示）
tail -f app.log

# 3. 在日志里搜索错误
grep "ERROR" app.log
```

---

### 场景 4：备份文件

```bash
# 1. 创建备份文件夹
mkdir backup

# 2. 复制重要文件
cp app.py backup/app.py.backup
cp -r config/ backup/config_backup/

# 3. 查看备份
ls -la backup/
```

---

## 📋 完整指令清单

### 📂 文件和文件夹操作
```bash
pwd                  # 显示当前路径
ls                   # 列出文件
cd                   # 切换目录
mkdir                # 创建文件夹
touch                # 创建文件
cp                   # 复制
mv                   # 移动/重命名
rm                   # 删除
find                 # 查找文件
```

### 📄 查看和编辑
```bash
cat                 # 查看文件全部内容
less                # 分页查看
head                # 查看前几行
tail                # 查看后几行
nano                # 简单编辑器
grep                # 搜索内容
```

### 🔍 信息查看
```bash
whoami              # 当前用户名
uname -a            # 系统信息
df -h               # 磁盘使用情况
free -h             # 内存使用情况
ps aux              # 运行中的进程
top                 # 实时系统监控
```

### 🔧 权限管理
```bash
chmod +x file.py    # 给文件添加执行权限
chmod 755 file.py   # 设置权限（755 = 可读可写可执行）
sudo                # 以管理员身份运行
```

---

## 🎯 实际例子

### 例子 1：第一次使用 Linux

```bash
# 1. 看看我在哪里
pwd
# 输出：/home/username

# 2. 看看有什么文件
ls
# 输出：Desktop  Documents  Downloads

# 3. 进入 Documents 文件夹
cd Documents

# 4. 创建一个新文件夹
mkdir myproject

# 5. 进入新文件夹
cd myproject

# 6. 创建一个文件
touch README.md

# 7. 编辑文件
nano README.md
# 输入内容，Ctrl+O 保存，Ctrl+X 退出

# 8. 查看文件内容
cat README.md
```

---

### 例子 2：管理 Python 项目

```bash
# 1. 进入项目
cd ~/myproject

# 2. 查看所有 Python 文件
find . -name "*.py"

# 3. 查看 app.py 的内容
cat app.py

# 4. 搜索包含 "def" 的行
grep "def" app.py

# 5. 创建备份
mkdir backup
cp app.py backup/

# 6. 查看文件大小
ls -lh app.py
```

---

### 例子 3：查看系统信息

```bash
# 1. 我是谁？
whoami

# 2. 系统信息
uname -a

# 3. 磁盘使用情况
df -h

# 4. 内存使用情况
free -h

# 5. 当前运行的进程
ps aux | head -20
```

---

## ❓ 常见问题解决

### Q1: 提示 "Permission denied"（权限被拒绝）？
**原因**：没有权限执行这个操作
**解决**：
```bash
# 使用 sudo（需要管理员密码）
sudo command

# 或者修改文件权限
chmod +x file.py
```

---

### Q2: 找不到命令 "command not found"？
**原因**：这个命令没有安装
**解决**：
```bash
# Ubuntu/Debian 系统
sudo apt update
sudo apt install 软件名

# 例如安装 Python
sudo apt install python3
```

---

### Q3: 文件太多，屏幕刷屏了？
**解决**：
```bash
# 使用 less 分页查看
ls -la | less

# 或者只看前 20 个
ls -la | head -20
```

---

### Q4: 想撤销刚才的操作？
**说明**：Linux 命令行没有"撤销"功能！
**预防**：
- 重要操作前先备份
- 使用 `cp` 而不是 `mv`
- 删除前用 `ls` 确认

---

### Q5: 如何退出卡住的程序？
**解决**：
- `Ctrl + C` = 中断当前程序
- `Ctrl + Z` = 暂停程序（后台运行）
- `Ctrl + D` = 退出当前终端

---

### Q6: 忘记文件在哪里了？
**解决**：
```bash
# 从当前目录开始找
find . -name "filename"

# 从根目录开始找（需要时间）
find / -name "filename" 2>/dev/null

# 在最近访问的文件里找
locate filename
```

---

## 🎓 学习路径建议

### 第 1 周：熟悉基础
- ✅ 每天用 `pwd`、`ls`、`cd` 导航
- ✅ 练习 `mkdir`、`touch` 创建文件
- ✅ 用 `cat`、`nano` 查看和编辑文件
- ✅ 理解文件路径（绝对路径 vs 相对路径）

### 第 2 周：掌握文件操作
- ✅ 熟练使用 `cp`、`mv`、`rm`
- ✅ 学会用 `find` 查找文件
- ✅ 学会用 `grep` 搜索内容
- ✅ 理解文件权限

### 第 3 周：系统管理
- ✅ 查看系统信息（`df`、`free`、`ps`）
- ✅ 安装软件（`apt` 或 `yum`）
- ✅ 理解进程管理
- ✅ 学会查看日志

### 第 4 周：进阶技能
- ✅ 管道操作（`|`）
- ✅ 重定向（`>`、`>>`）
- ✅ 环境变量
- ✅ Shell 脚本基础

---

## 💡 最佳实践

### ✅ 好的习惯
1. **经常用 `pwd` 确认位置**：避免在错误的地方操作
2. **删除前先 `ls` 确认**：防止误删
3. **重要文件先备份**：`cp file.txt file.txt.backup`
4. **用 `less` 查看大文件**：不要用 `cat` 看大文件
5. **Tab 键自动补全**：输入文件名时按 Tab 自动补全

### ❌ 避免的错误
1. ❌ 在根目录 `/` 下执行 `rm -rf *`（会删除整个系统！）
2. ❌ 不确认就执行删除操作
3. ❌ 用 `cat` 查看超大文件（会卡死）
4. ❌ 忘记 `-r` 就删除文件夹
5. ❌ 在重要操作前不备份

---

## 🚀 快速参考卡片

```
┌─────────────────────────────────────┐
│  导航和查看（最常用）                  │
├─────────────────────────────────────┤
│  pwd          → 我在哪里？            │
│  ls           → 看看有什么           │
│  cd 文件夹     → 进入文件夹           │
│  cd ..        → 返回上一级           │
│  cd ~         → 回到主目录           │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│  文件操作（核心技能）                  │
├─────────────────────────────────────┤
│  mkdir 名字    → 创建文件夹           │
│  touch 名字    → 创建文件             │
│  cat 文件      → 查看文件             │
│  nano 文件     → 编辑文件             │
│  cp 源 目标    → 复制                 │
│  mv 源 目标    → 移动/重命名          │
│  rm 文件       → 删除（小心！）       │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│  查找和搜索                           │
├─────────────────────────────────────┤
│  find . -name "*.py"  → 找文件       │
│  grep "关键词" 文件    → 搜索内容      │
│  head -n 20 文件       → 看前20行     │
│  tail -n 20 文件       → 看后20行    │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│  紧急操作                             │
├─────────────────────────────────────┤
│  Ctrl + C     → 中断程序             │
│  Ctrl + D     → 退出终端             │
│  Ctrl + Z     → 暂停程序             │
│  Tab          → 自动补全文件名        │
└─────────────────────────────────────┘
```

---

## 🎯 实用技巧

### 技巧 1：Tab 键自动补全
输入文件名时，按 `Tab` 键可以自动补全：
```bash
cd Doc[TAB]     # 自动补全为 Documents
cat app[TAB]    # 自动补全为 app.py
```

---

### 技巧 2：使用历史命令
- `↑` 键 = 上一条命令
- `↓` 键 = 下一条命令
- `history` = 查看所有历史命令
- `!123` = 执行历史中第 123 条命令

---

### 技巧 3：管道操作 `|`
把前一个命令的输出传给后一个命令：
```bash
ls -la | grep ".py"        # 列出文件，然后筛选 .py 文件
cat file.txt | grep "error"  # 查看文件，然后搜索 error
ps aux | head -10          # 查看进程，只显示前 10 个
```

---

### 技巧 4：重定向 `>` 和 `>>`
```bash
ls > filelist.txt          # 把输出保存到文件（覆盖）
ls >> filelist.txt         # 把输出追加到文件（不覆盖）
cat file.txt > output.txt  # 把文件内容保存到另一个文件
```

---

## 📚 推荐学习资源

### 在线练习
- **Linux Journey**：https://linuxjourney.com/（交互式教程）
- **Linux Command**：https://linuxcommand.org/（命令行教程）
- **OverTheWire**：https://overthewire.org/wargames/（游戏化学习）

### 参考手册
- **TLDR Pages**：https://tldr.sh/（简化版命令手册）
- **Linux Manual**：`man 命令名`（在终端查看）

---

## 🎉 总结

**Linux 的核心就是：**
1. **导航**：`pwd`、`ls`、`cd` - 知道在哪，看到什么，去哪
2. **操作**：`mkdir`、`touch`、`cp`、`mv`、`rm` - 创建、复制、移动、删除
3. **查看**：`cat`、`less`、`head`、`tail` - 看文件内容
4. **搜索**：`find`、`grep` - 找文件和内容

**记住**：
- 💪 多练习，熟能生巧
- 📝 重要操作前先备份
- ⚠️ 删除操作要小心
- 🔍 不会就查手册：`man 命令名`

**开始你的 Linux 之旅吧！** 🚀












