[app]

title = JJ象棋AI助手
package.name = jjchessai
package.domain = com.chessai

# 应用版本
version = 1.0.0

# 源码目录
source.dir = .

# 依赖 - 使用更兼容的版本
requirements = python3,kivy==2.3.0,mss,numpy,opencv-python-headless,Pillow,requests

# 权限 - 添加悬浮窗和网络权限
android.permissions = SYSTEM_ALERT_WINDOW,INTERNET,ACCESS_NETWORK_STATE

# 屏幕方向
orientation = portrait

# 全屏
fullscreen = 0

# 主入口
mainfile = main.py

# 构建模式
buildozer.spec_mode = False

# Android设置
android.add_assets = assets/
android.add_jars = None
android.add_libs = None
android.add_resources = None

# 签名配置（调试模式不需要签名）
# android.signing.keyalias = mykey
# android.signing.keystore = my.keystore

[buildozer]

# 日志级别
log_level = 2

# 错误停止
warn_on_root = 0

# Android API级别
android.minapi = 24
android.api = 33
android.ndk = 25b
android.ndk_api = 24

# 架构 - 支持arm64-v8a（华为Mate60使用）
android.archs = arm64-v8a

# 允许重复构建
allow_dir_creation = 1

# p4a设置
p4a.source_dir = 
p4a.local_recipes = 
p4a.bootstrap = sdl2
p4a.ndk_dir = 
p4a.sdk_dir = 
