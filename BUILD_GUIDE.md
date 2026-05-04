# JJ象棋AI助手 - APK打包指南

## 方法一：使用GitHub Actions（推荐）

这是最简单的方法，无需配置本地环境。

### 步骤：
1. 将项目上传到GitHub仓库
2. 登录GitHub，进入你的仓库
3. 点击顶部的 "Actions" 标签
4. 点击 "Build Android APK" workflow
5. 点击 "Run workflow"
6. 等待约20-40分钟，构建完成后下载APK

### 下载APK：
- 构建完成后，在Actions页面点击最新的运行记录
- 向下滚动到 "Artifacts" 部分
- 下载 `jjchessai-apk` 文件

---

## 方法二：使用WSL2（Windows子系统）

### 前提条件：
- Windows 10/11 版本 2004+
- 已启用WSL2

### 步骤：

1. **安装Ubuntu发行版**
   ```bash
   wsl --install -d Ubuntu
   ```

2. **进入WSL并安装依赖**
   ```bash
   wsl -d Ubuntu
   
   # 更新系统
   sudo apt-get update && sudo apt-get upgrade -y
   
   # 安装依赖
   sudo apt-get install -y git wget unzip build-essential cmake swig python3-pip python3-venv
   
   # 创建虚拟环境
   python3 -m venv venv
   source venv/bin/activate
   
   # 安装buildozer
   pip install --upgrade pip
   pip install cython buildozer
   ```

3. **进入项目目录并构建**
   ```bash
   cd /mnt/d/chess-test
   buildozer android debug
   ```

4. **获取APK**
   ```bash
   ls bin/*.apk
   ```

---

## 方法三：使用Docker

### 前提条件：
- 已安装Docker Desktop

### 步骤：

1. **打开命令提示符**，进入项目目录
   ```bash
   cd d:\chess-test
   ```

2. **运行Docker构建**
   ```bash
   docker run --rm ^
     -v %cd%:/app ^
     -v %USERPROFILE%/.buildozer:/home/user/.buildozer ^
     ghcr.io/kivy/buildozer:latest ^
     android debug
   ```

3. **获取APK**
   - APK文件位于 `bin/` 目录下

---

## 方法四：使用Linux服务器/虚拟机

### 步骤：

1. **安装依赖**
   ```bash
   sudo apt-get update
   sudo apt-get install -y git wget unzip build-essential cmake swig python3-pip python3-venv
   ```

2. **创建虚拟环境**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install --upgrade pip
   pip install cython buildozer
   ```

3. **构建APK**
   ```bash
   cd /path/to/chess-test
   buildozer android debug
   ```

---

## 安装到华为Mate60

### 方法一：通过USB传输
1. 将手机连接电脑
2. 启用USB调试（设置 > 关于手机 > 连续点击版本号）
3. 将APK文件复制到手机存储
4. 在手机上找到APK文件并点击安装

### 方法二：通过邮件/云盘
1. 将APK上传到云盘或发送到邮箱
2. 在手机上下载APK文件
3. 点击APK文件安装（可能需要允许"未知来源"）

---

## 常见问题

### Q: 构建失败？
A: 确保网络畅通。首次构建需要下载大量依赖，可能需要多次尝试。

### Q: 手机安装失败？
A: 在手机设置中允许"未知来源"安装，或检查APK是否完整。

### Q: 应用无法运行？
A: 确保手机系统版本 >= Android 10，检查权限设置。

---

## 技术规格

| 项目 | 规格 |
|------|------|
| 目标架构 | arm64-v8a（华为Mate60支持） |
| 最低Android版本 | Android 10 (API 29) |
| 目标Android版本 | Android 13 (API 33) |
| NDK版本 | 25b |

---

## 文件结构

```
chess-test/
├── main.py              # 主程序
├── src/                 # 源码目录
├── assets/              # 资源文件
├── buildozer.spec       # 打包配置
└── bin/                 # 输出目录（APK生成位置）
    └── jjchessai-1.0.0-debug.apk
```