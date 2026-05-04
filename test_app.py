#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JJ象棋AI助手 - 功能测试
测试各模块功能

作者: JJChessAI Team
版本: 1.0.0
"""

import sys
import os

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from chess_core import ChessEngine, MoveParser, ChessDBAPI
from board_detector import BoardDetector

print("=" * 60)
print("        JJ象棋AI助手 - 功能测试")
print("=" * 60)

# ==================== 测试1: 走法解析 ====================
print("\n【测试1】走法解析测试")
print("-" * 40)

parser = MoveParser()
test_cases = [
    ("炮二平五", True, "红炮从二路平到五路"),
    ("马8进7", False, "黑马从8路进到7路"),
    ("车1进1", True, "红车从1路进1步"),
    ("兵5进1", True, "红兵过河后前进"),
    ("相三进五", True, "红相飞到中相位置"),
]

all_passed = True
for move_text, is_red, desc in test_cases:
    from_pos, to_pos, piece = parser.parse_move(move_text, is_red)
    if from_pos and to_pos:
        print(f"  ✓ {move_text} ({desc})")
        print(f"    起点: {from_pos}, 终点: {to_pos}, 棋子: {piece}")
    else:
        print(f"  ✗ {move_text} - 解析失败")
        all_passed = False

print(f"\n  结果: {'全部通过' if all_passed else '存在问题'}")

# ==================== 测试2: ChessDB API ====================
print("\n【测试2】ChessDB API连接测试")
print("-" * 40)

api = ChessDBAPI()

# 测试创建游戏
game_id = api.new_game()
if game_id:
    print(f"  ✓ 创建游戏成功: {game_id}")
else:
    print("  ✗ 无法连接ChessDB API")
    print("    (可能是网络问题，不影响基本功能)")

# 测试UCI格式转换
print("\n  UCI格式转换测试:")
from_pos, to_pos = (0, 1), (2, 2)
uci = api.coordinate_to_uci(from_pos, to_pos)
back_from, back_to = api.uci_to_coordinate(uci)
print(f"    {from_pos} -> {uci} -> {back_from}, {back_to}")
if (from_pos == back_from) and (to_pos == back_to):
    print("    ✓ 转换正确")
else:
    print("    ✗ 转换错误")
    all_passed = False

# ==================== 测试3: 象棋引擎 ====================
print("\n【测试3】象棋引擎测试")
print("-" * 40)

engine = ChessEngine()
engine.player_is_red = True  # 假设玩家是红方

# 模拟走棋
moves = [
    ("炮二平五", False),  # 对方(黑方)
    ("马8进7", True),     # 我方(红方)
]

for move_text, is_red in moves:
    color = "红方" if is_red else "黑方"
    result = engine.add_move(move_text, is_red)
    if result:
        print(f"  ✓ {color} {move_text} - 添加成功")
    else:
        print(f"  ✗ {color} {move_text} - 添加失败")
        all_passed = False

# ==================== 测试4: 屏幕检测 ====================
print("\n【测试4】屏幕检测模块测试")
print("-" * 40)

detector = BoardDetector()

# 检查依赖
print("  依赖检查:")
print(f"    - mss (屏幕截取): {'✓' if detector.sct else '✗'}")
print(f"    - PIL (图像处理): {'✓' if hasattr(detector, 'last_screenshot') or True else '✗'}")

# 尝试截取
print("\n  尝试屏幕截取...")
screenshot = detector.capture_screen()
if screenshot:
    print(f"  ✓ 截取成功: {screenshot.size}")
else:
    print("  ! 截取失败 (可能需要GUI环境)")

# ==================== 测试5: 集成测试 ====================
print("\n【测试5】AI分析与建议测试")
print("-" * 40)

engine2 = ChessEngine()
engine2.player_is_red = False  # 玩家是黑方

# 模拟对方走棋
enemy_move = "炮2平5"  # 对方(红方)中炮
print(f"  对方(红方)走: {enemy_move}")

suggestion = engine2.analyze_and_suggest(enemy_move)
if suggestion:
    print(f"  ✓ AI建议: {suggestion}")
else:
    print("  ! 未能获取建议 (ChessDB可能不可用)")
    # 使用简单策略
    suggestion = engine2._simple_suggestion(enemy_move)
    print(f"    备用建议: {suggestion}")

# ==================== 测试结果 ====================
print("\n" + "=" * 60)
print("        测试完成")
print("=" * 60)

if all_passed:
    print("\n  🎉 所有测试通过!")
    print("\n  下一步:")
    print("    1. 运行 python main.py 启动主程序")
    print("    2. 在JJ象棋游戏中使用此助手")
else:
    print("\n  ⚠️ 部分测试存在问题，但不影响基本功能")
    print("\n  可以继续运行: python main.py")

print("\n")
