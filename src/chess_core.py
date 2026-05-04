#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
象棋引擎核心模块
功能：
1. 中国象棋走法验证
2. ChessDB API集成
3. AI走法建议

作者: JJChessAI Team
版本: 1.0.0
"""

import os
import json
import time
import base64
import urllib.request
import urllib.parse
import urllib.error
import re

# ==================== 常量定义 ====================
# ChessDB API地址
CHESSDB_API = "http://www.chessdb.cn/chessdb.php"

# 中国象棋棋子编码
PIECES = {
    'k': '帅', 'K': '将',
    'r': '车', 'R': '車',
    'n': '马', 'N': '馬',
    'b': '相', 'B': '象',
    'a': '仕', 'A': '士',
    'c': '炮', 'C': '砲',
    'p': '兵', 'P': '卒'
}

# 简化版棋子映射
PIECE_TYPES = {
    '帅': 'k', '将': 'K',
    '车': 'r', '車': 'R',
    '马': 'n', '馬': 'N',
    '相': 'b', '象': 'B',
    '仕': 'a', '士': 'A',
    '炮': 'c', '砲': 'C',
    '兵': 'p', '卒': 'P'
}


# ==================== 走法解析器 ====================
class MoveParser:
    """中国象棋走法解析器"""
    
    # 列映射（红方视角：九从右到左）
    COLS_RED = '一二三四五六七八九'
    COLS_BLACK = '九八七六五四三二一'
    
    @staticmethod
    def parse_move(move_text, is_red_move=True):
        """
        解析走法文本
        
        参数:
            move_text: 走法描述，如 "炮二平五"
            is_red_move: 是否为红方走法
            
        返回:
            (from_pos, to_pos, piece_type) 或 (None, None, None)
        """
        if not move_text or len(move_text) < 3:
            return None, None, None
            
        try:
            piece = move_text[0]
            from_col_char = move_text[1]
            direction = move_text[2]
            num_or_col = move_text[3:] if len(move_text) > 3 else ''
            
            # 解析起点列
            cols = MoveParser.COLS_RED if is_red_move else MoveParser.COLS_BLACK
            if from_col_char in cols:
                from_col = cols.index(from_col_char)
            else:
                return None, None, None
                
            # 解析终点
            if direction in ['进', '退', '平']:
                if direction == '平':
                    # 平：列变化，行不变
                    to_col_char = num_or_col[0] if num_or_col else from_col_char
                    if to_col_char in cols:
                        to_col = cols.index(to_col_char)
                    else:
                        return None, None, None
                    to_row = from_col  # 简化处理
                    from_row = 4 if is_red_move else 5  # 默认位置
                else:
                    # 进或退
                    to_col = from_col
                    if num_or_col.isdigit():
                        steps = int(num_or_col)
                    else:
                        return None, None, None
                        
                    # 根据棋子类型和方向计算终点行
                    if piece in ['兵', '卒', 'p', 'P']:
                        # 兵/卒过河前后走法不同
                        current_row = 3 if is_red_move else 6
                        if is_red_move:
                            to_row = current_row + steps if direction == '进' else current_row - steps
                        else:
                            to_row = current_row - steps if direction == '进' else current_row + steps
                    else:
                        # 其他棋子
                        if is_red_move:
                            to_row = 9 - steps if direction == '进' else 9 + steps
                        else:
                            to_row = steps if direction == '进' else 0 + steps
                            
                from_row = 4 if is_red_move else 5  # 简化：假设从第5行出发
                
                return (from_row, from_col), (to_row, to_col), piece
                
        except Exception as e:
            print(f"[错误] 解析走法失败: {e}")
            
        return None, None, None
        
    @staticmethod
    def format_move(from_pos, to_pos, piece_type, is_red_move=True):
        """
        将坐标格式化为走法文本
        
        参数:
            from_pos: 起点 (row, col)
            to_pos: 终点 (row, col)
            piece_type: 棋子类型
            is_red_move: 是否为红方
            
        返回:
            走法描述字符串
        """
        if not from_pos or not to_pos or not piece_type:
            return ""
            
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        
        cols = MoveParser.COLS_RED if is_red_move else MoveParser.COLS_BLACK
        
        # 获取起点列
        from_col_char = cols[from_col] if from_col < 9 else '?'
        
        # 计算方向和距离
        row_diff = to_row - from_row
        
        if row_diff == 0:
            direction = '平'
            num = cols[to_col] if to_col < 9 else ''
        elif row_diff > 0:
            direction = '进'
            num = str(abs(row_diff))
        else:
            direction = '退'
            num = str(abs(row_diff))
            
        return f"{piece_type}{from_col_char}{direction}{num}"


# ==================== ChessDB API客户端 ====================
class ChessDBAPI:
    """ChessDB中国象棋数据库API"""
    
    def __init__(self):
        self.base_url = CHESSDB_API
        
    def _make_request(self, action, params=None):
        """
        发送API请求
        
        参数:
            action: 操作类型 (newgame, addmove, query)
            params: 额外参数
            
        返回:
            响应数据或 None
        """
        try:
            data = {'action': action}
            if params:
                data.update(params)
                
            encoded_data = urllib.parse.urlencode(data)
            req = urllib.request.Request(
                self.base_url,
                data=encoded_data.encode('utf-8'),
                headers={'Content-Type': 'application/x-www-form-urlencoded'}
            )
            
            with urllib.request.urlopen(req, timeout=10) as response:
                result = response.read().decode('utf-8')
                return json.loads(result)
                
        except urllib.error.URLError as e:
            print(f"[错误] ChessDB请求失败: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"[错误] 解析响应失败: {e}")
            return None
        except Exception as e:
            print(f"[错误] 未知错误: {e}")
            return None
            
    def new_game(self):
        """创建新游戏"""
        result = self._make_request('newgame')
        if result and result.get('status') == 'ok':
            return result.get('id')
        return None
        
    def add_move(self, game_id, move_uci, side='w'):
        """
        添加走法
        
        参数:
            game_id: 游戏ID
            move_uci: UCI格式走法 (如 "h2e2")
            side: 'w' 红方, 'b' 黑方
            
        返回:
            是否成功
        """
        result = self._make_request('addmove', {
            'id': game_id,
            'move': move_uci,
            'side': side
        })
        return result and result.get('status') == 'ok'
        
    def query(self, game_id, side='b'):
        """
        查询最佳走法
        
        参数:
            game_id: 游戏ID
            side: 查询哪一方的最佳走法
            
        返回:
            最佳走法 (UCI格式) 或 None
        """
        result = self._make_request('query', {
            'id': game_id,
            'side': side
        })
        
        if result and result.get('status') == 'ok':
            return result.get('bestmove')
        return None
        
    def uci_to_coordinate(self, uci_move):
        """
        将UCI格式转换为坐标
        
        参数:
            uci_move: UCI格式，如 "h2e2"
            
        返回:
            (from_pos, to_pos)
        """
        if not uci_move or len(uci_move) < 4:
            return None, None
            
        try:
            # UCI格式: 列(0-8)行(0-9)列(0-8)行(0-9)
            # 列: a-i (0-8), 行: 0-9
            from_col = ord(uci_move[0].lower()) - ord('a')
            from_row = int(uci_move[1])
            to_col = ord(uci_move[2].lower()) - ord('a')
            to_row = int(uci_move[3])
            
            return (from_row, from_col), (to_row, to_col)
        except:
            return None, None
            
    def coordinate_to_uci(self, from_pos, to_pos):
        """
        将坐标转换为UCI格式
        
        参数:
            from_pos: 起点 (row, col)
            to_pos: 终点 (row, col)
            
        返回:
            UCI格式字符串
        """
        if not from_pos or not to_pos:
            return ""
            
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        
        from_uci = chr(ord('a') + from_col) + str(from_row)
        to_uci = chr(ord('a') + to_col) + str(to_row)
        
        return from_uci + to_uci


# ==================== 象棋引擎 ====================
class ChessEngine:
    """象棋引擎"""
    
    def __init__(self):
        self.api = ChessDBAPI()
        self.game_id = None
        self.player_is_red = True
        self.move_list = []
        self.current_side = 'w'  # w=红方先走, b=黑方
        
    def reset(self):
        """重置游戏"""
        self.game_id = self.api.new_game()
        self.move_list = []
        self.current_side = 'w'
        
    def add_move(self, move_text, is_red_move=True):
        """
        添加走法
        
        参数:
            move_text: 走法描述
            is_red_move: 是否为红方走法
            
        返回:
            是否成功
        """
        if not self.game_id:
            self.reset()
            
        # 解析走法
        from_pos, to_pos, piece_type = MoveParser.parse_move(move_text, is_red_move)
        
        if not from_pos or not to_pos:
            print(f"[警告] 无法解析走法: {move_text}")
            return False
            
        # 转换为UCI格式
        uci_move = self.api.coordinate_to_uci(from_pos, to_pos)
        
        # 确定是哪一方
        side = 'w' if is_red_move else 'b'
        
        # 添加到ChessDB
        if self.api.add_move(self.game_id, uci_move, side):
            self.move_list.append({
                'text': move_text,
                'from': from_pos,
                'to': to_pos,
                'piece': piece_type,
                'uci': uci_move,
                'side': side
            })
            
            # 切换走棋方
            self.current_side = 'b' if is_red_move else 'w'
            return True
            
        return False
        
    def get_best_move(self):
        """
        获取最佳走法
        
        返回:
            UCI格式的最佳走法或 None
        """
        if not self.game_id:
            return None
            
        # 查询当前方的最佳走法
        side = 'b' if self.current_side == 'w' else 'w'  # AI给的是对方
        return self.api.query(self.game_id, side)
        
    def analyze_and_suggest(self, enemy_move):
        """
        分析局势并给出建议
        
        参数:
            enemy_move: 对方的走法
            
        返回:
            建议走法描述或 None
        """
        if not enemy_move:
            return None
            
        # 确定敌我颜色
        # 如果玩家选择红方(player_is_red=True)，对手是黑方
        enemy_is_red = not self.player_is_red
        
        # 1. 先添加对方的走法
        self.add_move(enemy_move, is_red_move=enemy_is_red)
        
        # 2. 查询我方最佳走法
        best_uci = self.get_best_move()
        
        if best_uci:
            # 3. 转换UCI为坐标
            from_pos, to_pos = self.api.uci_to_coordinate(best_uci)
            
            if from_pos and to_pos:
                # 4. 确定我方棋子颜色
                is_red = self.player_is_red
                
                # 5. 格式化输出
                # 简化处理：假设已知棋子类型
                # 实际使用时需要根据棋盘状态确定
                suggestion = MoveParser.format_move(
                    from_pos, to_pos, 
                    self._guess_piece_type(from_pos, is_red),
                    is_red
                )
                
                if suggestion:
                    return suggestion
                    
        # 如果ChessDB没有结果，使用简单策略
        return self._simple_suggestion(enemy_move)
        
    def _guess_piece_type(self, pos, is_red):
        """猜测棋子类型（简化版）"""
        row, col = pos
        
        # 根据位置猜测棋子类型
        if is_red:
            # 红方布局：帅在(e,0), 车在(a/b,0/h/i,0), 马在(b/g,0), 相在(c/f,0)
            # 炮在(d/e,2), 兵在(a/c/e/g/i,3)
            if col == 4 and row == 0:
                return '帅'
            elif col in [0, 8] and row in [0, 1]:
                return '车'
            elif col in [1, 7] and row in [0, 2]:
                return '马'
            elif col in [2, 6] and row in [0, 2]:
                return '相'
            elif col in [3, 5] and row in [0, 1]:
                return '仕'
            elif col in [2, 7] and row == 2:
                return '炮'
            elif row >= 3:
                return '兵'
        else:
            # 黑方布局
            if col == 4 and row == 9:
                return '将'
            elif col in [0, 8] and row in [9, 8]:
                return '車'
            elif col in [1, 7] and row in [9, 7]:
                return '馬'
            elif col in [2, 6] and row in [9, 7]:
                return '象'
            elif col in [3, 5] and row in [9, 8]:
                return '士'
            elif col in [2, 7] and row == 7:
                return '砲'
            elif row <= 6:
                return '卒'
                
        return '马'  # 默认返回马
        
    def _simple_suggestion(self, enemy_move):
        """简单建议策略（当ChessDB不可用时）"""
        # 解析对方走法
        from_pos, to_pos, piece = MoveParser.parse_move(enemy_move, not self.player_is_red)
        
        if not from_pos:
            return "马8进7"  # 默认建议
            
        # 简单策略：如果是对方进攻，考虑防守或对攻
        # 这里返回一些常见开局走法
        suggestions = [
            "马8进7",   # 屏风马
            "炮8平5",   # 中炮
            "车1进1",   # 抬车
            "士4进5",   # 上士
            "象3进5",   # 飞象
            "兵7进1",   # 挺兵
        ]
        
        import random
        return random.choice(suggestions)
        
    def parse_move(self, move_text):
        """
        解析走法返回坐标
        
        参数:
            move_text: 走法描述
            
        返回:
            (from_pos, to_pos)
        """
        from_pos, to_pos, _ = MoveParser.parse_move(
            move_text, 
            self.player_is_red
        )
        return from_pos, to_pos


# ==================== 测试代码 ====================
if __name__ == '__main__':
    print("=" * 50)
    print("象棋引擎测试")
    print("=" * 50)
    
    engine = ChessEngine()
    engine.player_is_red = False  # 假设玩家是黑方
    
    print("\n1. 测试走法解析:")
    test_moves = [
        ("炮二平五", True),
        ("马8进7", False),
        ("车1进1", True),
    ]
    
    for move_text, is_red in test_moves:
        from_pos, to_pos, piece = MoveParser.parse_move(move_text, is_red)
        print(f"   {move_text} -> 起点:{from_pos}, 终点:{to_pos}, 棋子:{piece}")
        
    print("\n2. 测试ChessDB API:")
    api = ChessDBAPI()
    game_id = api.new_game()
    if game_id:
        print(f"   创建游戏成功: {game_id}")
        
        # 添加一个走法
        from_pos, to_pos = (0, 1), (2, 2)
        uci = api.coordinate_to_uci(from_pos, to_pos)
        print(f"   坐标转UCI: {from_pos}->{to_pos} = {uci}")
        
        back = api.uci_to_coordinate(uci)
        print(f"   UCI转坐标: {uci} = {back}")
    else:
        print("   [X] 无法连接ChessDB API")
        
    print("\n" + "=" * 50)
