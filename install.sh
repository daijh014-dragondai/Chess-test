#!/bin/bash
# -*- coding: utf-8 -*-
# JJ象棋AI助手 - 依赖安装脚本 (Linux/Mac)

echo "========================================"
echo "   JJ象棋AI助手 - 依赖安装脚本"
echo "========================================"
echo ""

echo "正在安装Python依赖..."
echo ""

pip3 install kivy
pip3 install pillow
pip3 install opencv-python
pip3 install mss
pip3 install numpy
pip3 install requests

echo ""
echo "========================================"
echo "   依赖安装完成！"
echo "========================================"
echo ""
echo "现在可以运行主程序:"
echo "  python3 main.py"
echo ""
echo "或者运行测试:"
echo "  python3 test_app.py"
echo ""
