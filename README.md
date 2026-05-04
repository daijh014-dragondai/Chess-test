# JJ象棋AI悬浮助手

华为Mate60专用 - JJ象棋智能辅助工具

## 功能特性

- **自动识别落子**：截取屏幕，自动识别对手的走法
- **AI大师级分析**：基于ChessDB数据库，提供专业走法建议
- **动画提示**：以动画形式展示建议的落子位置
- **全局分析**：记录双方所有走法，提供更精准的全局建议
- **悬浮窗模式**：半透明悬浮窗，不遮挡游戏画面

## 安装说明

### Windows/Mac/Linux 桌面版

```bash
# 1. 进入项目目录
cd chess-test

# 2. 安装依赖
pip install -r requirements.txt

# 3. 运行
python main.py
```

### 华为鸿蒙 APK 版本

APK打包需要使用Linux环境，推荐使用WSL2或虚拟机。

#### 方法一：使用WSL2 (推荐)

```bash
# 1. 安装WSL2 Ubuntu
wsl --install -d Ubuntu

# 2. 进入项目目录并运行打包脚本
cd d:/chess-test
bash build_apk.sh
```

#### 方法二：使用Docker

```bash
# 1. 安装Docker (Windows/Mac)

# 2. 构建APK
docker run --rm \
  -v ${PWD}:/app \
  -v ~/.buildozer:/home/user/.buildozer \
  ghcr.io/kivy/buildozer:latest \
  android debug
```

# 3. APK生成在 bin/ 目录下

## 使用方法

1. **启动应用**：打开JJ象棋游戏
2. **选择颜色**：在悬浮窗中选择您执棋的颜色（红方/黑方）
3. **对手走棋**：对手落子后，点击"对方落子"按钮
4. **获取建议**：点击"AI分析"获取大师级走法建议
5. **动画提示**：建议以动画形式高亮显示在悬浮窗中
6. **落子**：按照动画提示在JJ象棋中落子

## 项目结构

```
chess-test/
├── main.py              # 主程序入口
├── src/
│   ├── chess_core.py    # 象棋引擎和ChessDB集成
│   ├── board_detector.py # 棋盘识别和落子检测
│   └── anim_hint.py     # 动画提示模块
├── assets/              # 资源文件
├── requirements.txt     # Python依赖
├── buildozer.spec       # APK打包配置
├── build_apk.sh         # Linux/WML打包脚本
└── build_apk.bat        # Windows打包脚本
```

## 技术说明

- 开发语言：Python 3.10+
- 界面框架：Kivy 2.3.1
- 图像识别：OpenCV + PIL
- 屏幕截取：mss
- AI数据源：ChessDB (chessdb.cn)
- 最低系统：Android 10 / HarmonyOS 3+

## 许可证

MIT License

## 常见问题

### Q: 打包APK失败怎么办？

A: 确保已安装WSL2或Docker。首次打包需要下载Android SDK/NDK，可能需要20-40分钟。

### Q: 程序运行时显示乱码？

A: 已修复。程序使用UTF-8编码，Windows上需要控制台支持UTF-8。

### Q: AI分析连接失败？

A: 检查网络连接。ChessDB API需要访问chessdb.cn服务器。