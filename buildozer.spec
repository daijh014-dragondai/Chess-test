[app]

title = JJ Chess AI
package.name = jjchessai
package.domain = com.chessai
version = 0.1.0

source.dir = .
source.include_exts = py,png,jpg,kv,atlas

requirements = python3,kivy==2.1.0,numpy,Pillow,requests
android.permissions = INTERNET,ACCESS_NETWORK_STATE
orientation = portrait
fullscreen = 0
mainfile = main.py

[buildozer]
log_level = 2
warn_on_root = 0

android.ndk = 25b
android.sdk = 24
android.api = 33
android.minapi = 24
android.archs = arm64-v8a

p4a.source_dir =
p4a.local_recipes =
p4a.bootstrap = sdl2
p4a.ndk_dir =
p4a.sdk_dir =
