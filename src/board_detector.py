#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
棋盘识别与落子检测模块
功能：
1. 截取屏幕指定区域
2. 识别棋盘和棋子位置
3. 检测对方落子

作者: JJChessAI Team
版本: 1.0.0
"""

import os
import sys
import time
import json
import base64
import urllib.request
import urllib.parse
import urllib.error
import numpy as np
from io import BytesIO

# 尝试导入可选依赖
try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    print("[警告] OpenCV未安装，自动检测功能将受限")

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("[警告] PIL未安装，自动检测功能将受限")

try:
    import mss
    MSS_AVAILABLE = True
except ImportError:
    MSS_AVAILABLE = False
    print("[警告] mss未安装，屏幕截取功能将受限")


# ==================== 棋盘常量 ====================
# 中国象棋棋盘配置
BOARD_CONFIG = {
    'rows': 10,           # 10行
    'cols': 9,            # 9列
    'cell_width': 50,     # 格子宽度(像素)
    'cell_height': 50,    # 格子高度(像素)
    'offset_x': 0,        # 棋盘左上角X偏移
    'offset_y': 0,       # 棋盘左上角Y偏移
}

# 棋子定义
PIECE_NAMES = {
    'r': '车', 'n': '马', 'b': '相', 'a': '仕', 'k': '帅', 'c': '炮', 'p': '兵',
    'R': '車', 'N': '馬', 'B': '象', 'A': '士', 'K': '將', 'C': '砲', 'P': '卒'
}

# 棋子颜色范围 (HSV)
RED_PIECE_RANGE = {
    'lower': np.array([0, 100, 100]),
    'upper': np.array([10, 255, 255])
}

BLACK_PIECE_RANGE = {
    'lower': np.array([0, 0, 0]),
    'upper': np.array([180, 255, 100])
}


# ==================== 棋盘检测器类 ====================
class BoardDetector:
    """棋盘检测器"""
    
    def __init__(self):
        """初始化检测器"""
        self.config = BOARD_CONFIG.copy()
        self.sct = None
        self.last_screenshot = None
        self.last_move_detected = ""
        self.move_history = []  # 移动历史
        self.board_state = {}    # 棋盘状态
        self.last_state = {}     # 上一次状态
        
        # 初始化屏幕截取
        if MSS_AVAILABLE:
            self.sct = mss.mss()
            
        # 默认截取区域（需要根据实际JJ象棋窗口调整）
        self.capture_region = {
            'left': 100,
            'top': 100,
            'width': 500,
            'height': 600
        }
        
    def set_capture_region(self, left, top, width, height):
        """设置截取区域"""
        self.capture_region = {
            'left': left,
            'top': top,
            'width': width,
            'height': height
        }
        print(f"[棋盘检测] 截取区域: {self.capture_region}")
        
    def capture_screen(self):
        """截取屏幕"""
        if not MSS_AVAILABLE:
            return None
            
        try:
            screenshot = self.sct.grab(self.capture_region)
            self.last_screenshot = screenshot
            return screenshot
        except Exception as e:
            print(f"[错误] 截取屏幕失败: {e}")
            return None
            
    def detect_move(self, current_player='black'):
        """
        检测对方落子
        
        参数:
            current_player: 当前应该落子的玩家 ('red' 或 'black')
            
        返回:
            检测到的走法字符串，如 "炮二平五" 或 None
        """
        if not MSS_AVAILABLE or not PIL_AVAILABLE:
            print("[提示] 自动检测需要安装 mss 和 PIL 库")
            return None
            
        try:
            # 截取屏幕
            screenshot = self.capture_screen()
            if screenshot is None:
                return None
                
            # 转换为PIL Image
            img = Image.frombytes('RGB', screenshot.size, screenshot.rgb)
            img_array = np.array(img)
            
            # 检测是否有新落子
            pieces = self._detect_pieces(img_array)
            
            if pieces:
                # 对比上一状态，找出变化的棋子
                moved_piece = self._detect_moved_piece(pieces)
                
                if moved_piece:
                    from_pos, to_pos, piece_type = moved_piece
                    
                    # 转换坐标为走法描述
                    move_text = self._convert_to_move_text(
                        from_pos, to_pos, piece_type, 
                        current_player
                    )
                    
                    if move_text and move_text != self.last_move_detected:
                        self.last_move_detected = move_text
                        self.move_history.append({
                            'player': current_player,
                            'from': from_pos,
                            'to': to_pos,
                            'piece': piece_type,
                            'move_text': move_text,
                            'timestamp': time.time()
                        })
                        return move_text
                        
            return None
            
        except Exception as e:
            print(f"[错误] 检测落子失败: {e}")
            return None
            
    def _detect_pieces(self, img_array):
        """
        检测棋盘上的棋子
        
        参数:
            img_array: numpy数组格式的图片
            
        返回:
            检测到的棋子列表 [(行, 列, 颜色, 类型), ...]
        """
        if not CV2_AVAILABLE:
            return self._detect_pieces_simple(img_array)
            
        pieces = []
        
        # 转换到HSV颜色空间
        hsv = cv2.cvtColor(img_array, cv2.COLOR_RGB2HSV)
        
        # 检测红色棋子
        mask_red = cv2.inRange(hsv, RED_PIECE_RANGE['lower'], RED_PIECE_RANGE['upper'])
        
        # 检测黑色棋子
        mask_black = cv2.inRange(hsv, BLACK_PIECE_RANGE['lower'], BLACK_PIECE_RANGE['upper'])
        
        # 找圆形（棋子）
        circles = cv2.HoughCircles(
            mask_red + mask_black,
            cv2.HOUGH_GRADIENT,
            dp=1,
            minDist=30,
            param1=50,
            param2=30,
            minRadius=15,
            maxRadius=30
        )
        
        if circles is not None:
            for circle in circles[0]:
                x, y, r = circle
                col = int((x - self.config['offset_x']) / self.config['cell_width'])
                row = int((y - self.config['offset_y']) / self.config['cell_height'])
                
                if 0 <= row < 10 and 0 <= col < 9:
                    color = 'red' if mask_red[int(y), int(x)] > 0 else 'black'
                    pieces.append((row, col, color, 'unknown'))
                    
        return pieces
        
    def _detect_pieces_simple(self, img_array):
        """
        简单棋子检测（不使用OpenCV）
        """
        pieces = []
        
        # 基于颜色直方图简单检测
        # 实际使用时建议配置棋盘位置
        
        return pieces
        
    def _detect_moved_piece(self, current_pieces):
        """
        检测移动的棋子
        
        参数:
            current_pieces: 当前检测到的棋子列表
            
        返回:
            (起点, 终点, 棋子类型) 或 None
        """
        if not self.last_state:
            # 首次检测，保存当前状态
            self.last_state = {(p[0], p[1]): p for p in current_pieces}
            return None
            
        # 找出新出现的棋子或消失的棋子
        current_set = {(p[0], p[1]) for p in current_pieces}
        last_set = set(self.last_state.keys())
        
        # 新出现的棋子位置
        new_positions = current_set - last_set
        
        # 消失的棋子位置
        old_positions = last_set - current_set
        
        if len(new_positions) == 1 and len(old_positions) == 1:
            # 这是一次移动
            to_pos = list(new_positions)[0]
            from_pos = list(old_positions)[0]
            
            # 获取棋子颜色
            piece_color = None
            for p in current_pieces:
                if (p[0], p[1]) == to_pos:
                    piece_color = p[2]
                    break
                    
            # 更新状态
            self.last_state = {(p[0], p[1]): p for p in current_pieces}
            
            return (from_pos, to_pos, piece_color)
            
        elif len(new_positions) == 1 and len(old_positions) == 0:
            # 可能是首次检测
            self.last_state = {(p[0], p[1]): p for p in current_pieces}
            
        return None
        
    def _convert_to_move_text(self, from_pos, to_pos, piece_color, player):
        """
        将坐标转换为中国象棋走法描述
        
        参数:
            from_pos: 起点 (行, 列)
            to_pos: 终点 (行, 列)
            piece_color: 棋子颜色 'red' 或 'black'
            player: 当前玩家
            
        返回:
            走法描述字符串，如 "炮二平五"
        """
        row, col = from_pos
        to_row, to_col = to_pos
        
        # 行列转换 (行0-9对应1-10，列0-8对应1-9)
        # 棋盘坐标：红方在下，黑方在上
        if piece_color == player:
            # 是当前玩家的棋子，可能是被吃掉了
            return None
            
        # 确定棋子类型（需要根据实际识别，这里用简化逻辑）
        piece_type = self._identify_piece_type(from_pos, to_pos, piece_color)
        
        if piece_type is None:
            piece_type = '未知'
            
        # 列编号（红方视角）
        cols = '一二三四五六七八九'
        
        # 确定方向（红方从下往上，黑方从上往下）
        if player == 'red':
            # 红方视角：数字从右往左
            from_col_text = cols[8 - col]
            to_col_text = cols[8 - to_col]
        else:
            # 黑方视角
            from_col_text = cols[col]
            to_col_text = cols[to_col]
            
        # 判断是进、退、平
        row_diff = to_row - row
        
        if piece_type in ['车', '馬', '車', '馬']:
            # 车马按方向描述
            if row_diff > 0:
                direction = '进'
                num = to_row - row if player == 'red' else row - to_row
            elif row_diff < 0:
                direction = '退'
                num = row - to_row if player == 'red' else to_row - row
            else:
                direction = '平'
                num = to_col_text
        elif piece_type in ['炮', '砲']:
            if row_diff > 0:
                direction = '进'
                num = to_row - row if player == 'red' else row - to_row
            elif row_diff < 0:
                direction = '退'
                num = row - to_row if player == 'red' else to_row - row
            else:
                direction = '平'
                num = to_col_text
        elif piece_type in ['兵', '卒']:
            if player == 'red':
                if row > 4:  # 过河前
                    direction = '进'
                    num = row - to_row
                else:
                    if row_diff > 0:
                        direction = '进'
                    else:
                        direction = '平'
                    num = cols[8 - to_col]
            else:
                if row < 5:  # 过河前
                    direction = '进'
                    num = to_row - row
                else:
                    if row_diff < 0:
                        direction = '进'
                    else:
                        direction = '平'
                    num = cols[to_col]
        else:
            # 将帅仕相
            if row_diff > 0:
                direction = '进'
                num = abs(row_diff)
            elif row_diff < 0:
                direction = '退'
                num = abs(row_diff)
            else:
                direction = '平'
                num = to_col_text
                
        return f"{piece_type}{from_col_text}{direction}{num}"
        
    def _identify_piece_type(self, from_pos, to_pos, piece_color):
        """
        识别棋子类型（简化版）
        实际需要OCR或模板匹配
        
        返回:
            棋子类型名称
        """
        row, col = from_pos
        
        # 简化逻辑：根据位置判断基本类型
        # 实际情况需要更复杂的图像识别
        
        # 默认返回
        return None
        
    def reset(self):
        """重置检测器状态"""
        self.last_state = {}
        self.last_move_detected = ""
        self.move_history = []
        self.board_state = {}
        
    def calibrate(self, screenshot):
        """
        校准棋盘位置
        通过用户点击四个角来校准
        """
        # 这是一个简化版本
        # 实际需要用户提供四个角点坐标
        pass
        
    def save_config(self, config_path='board_config.json'):
        """保存配置"""
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump({
                'capture_region': self.capture_region,
                'board_config': self.config
            }, f, indent=2, ensure_ascii=False)
            
    def load_config(self, config_path='board_config.json'):
        """加载配置"""
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.capture_region = data.get('capture_region', self.capture_region)
                self.config = data.get('board_config', self.config)


# ==================== 测试代码 ====================
if __name__ == '__main__':
    print("=" * 50)
    print("棋盘检测器测试")
    print("=" * 50)
    
    detector = BoardDetector()
    
    print("\n1. 测试屏幕截取...")
    screenshot = detector.capture_screen()
    if screenshot:
        print("   [OK] 屏幕截取成功")
    else:
        print("   [X] 屏幕截取失败")
        
    print("\n2. 检测功能可用性:")
    print(f"   - mss: {'✓' if MSS_AVAILABLE else '✗'}")
    print(f"   - PIL: {'✓' if PIL_AVAILABLE else '✗'}")
    print(f"   - OpenCV: {'✓' if CV2_AVAILABLE else '✗'}")
    
    if MSS_AVAILABLE and PIL_AVAILABLE:
        print("\n3. 尝试检测落子...")
        move = detector.detect_move('black')
        if move:
            print(f"   检测到: {move}")
        else:
            print("   未检测到变化")
            
    print("\n" + "=" * 50)
