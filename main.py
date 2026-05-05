#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JJ Chess AI Assistant - Main Program
Functions:
1. Select piece color (Red/Black)
2. Click "Opponent Moved" to auto-detect
3. Click "Get Hint" for AI animation
4. Click "I Moved" to record
5. Loop analysis

Author: JJChessAI Team
Version: 1.0.0
"""

import sys
import os
import io

# Force UTF-8 encoding for Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    
    # Set console encoding
    import subprocess
    subprocess.run(['chcp', '65001'], shell=True, capture_output=True)

# ==================== Kivy Configuration ====================
import kivy
kivy.require('2.3.0')

from kivy.config import Config
Config.set('graphics', 'width', '320')
Config.set('graphics', 'height', '500')
Config.set('graphics', 'resizable', False)

# Set default font to support Chinese (cross-platform)
import platform
font_paths = []
if platform.system() == 'Windows':
    font_paths = ['C:\\Windows\\Fonts\\simhei.ttf', 'C:\\Windows\\Fonts\\simsun.ttc']
else:
    # For Linux/Android, try system fonts or use default
    font_paths = ['/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc', '/usr/share/fonts/truetype/freefont/FreeSans.ttf']

# Find first available font
available_font = None
for font_path in font_paths:
    if os.path.exists(font_path):
        available_font = font_path
        break

if available_font:
    Config.set('kivy', 'default_font', ['CustomFont', available_font])
else:
    # Fallback to default Kivy font
    pass

import sys
import os
import threading
import time
import json
import base64
import urllib.request
import urllib.parse

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.checkbox import CheckBox
from kivy.uix.popup import Popup
from kivy.graphics import Color, Rectangle, Line, Ellipse, InstructionGroup
from kivy.graphics.texture import Texture
from kivy.clock import Clock
from kivy.properties import NumericProperty, StringProperty, BooleanProperty
from kivy.animation import Animation

# 导入自定义模块
from chess_core import ChessEngine, ChessDBAPI
from board_detector import BoardDetector
from anim_hint import AnimationHint

# ==================== 全局配置 ====================
APP_NAME = "JJ象棋AI助手"
APP_VERSION = "1.0.0"

# ==================== 颜色定义 ====================
COLOR_PRIMARY = (0.0, 0.94, 1.0, 1)      # 电光青 #00F0FF
COLOR_SECONDARY = (0.75, 0.0, 1.0, 1)   # 霓虹紫 #BF00FF
COLOR_BG_DARK = (0.04, 0.04, 0.06, 1)   # 深黑 #0A0A0F
COLOR_BG_CARD = (0.08, 0.08, 0.12, 1)   # 卡片背景
COLOR_TEXT = (0.9, 0.9, 0.95, 1)        # 文字色
COLOR_TEXT_DIM = (0.5, 0.5, 0.6, 1)     # 次要文字
COLOR_RED = (0.9, 0.2, 0.2, 1)           # 红色棋子
COLOR_BLACK = (0.15, 0.15, 0.15, 1)      # 黑色棋子
COLOR_HINT = (1.0, 0.85, 0.0, 1)        # 提示高亮 #FFD700

# ==================== 主界面类 ====================
class ChessAIWidget(BoxLayout):
    """象棋AI助手主界面"""
    
    # 玩家颜色：True=红方, False=黑方
    is_red_player = BooleanProperty(True)
    
    # 游戏状态
    game_started = BooleanProperty(False)
    last_detected_move = StringProperty("")
    ai_suggestion = StringProperty("")
    status_text = StringProperty("请先选择棋子颜色")
    move_history = StringProperty("")
    thinking = BooleanProperty(False)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 10
        self.spacing = 8
        
        # 初始化模块
        self.chess_engine = ChessEngine()
        self.board_detector = BoardDetector()
        self.anim_hint = None
        
        # 当前游戏状态
        self.current_player = 'red'  # 当前应该走的玩家
        self.move_list = []          # 所有走法记录
        self.detected_enemy_move = ""  # 检测到的对方走法
        self.pending_suggestion = None  # 待显示的AI建议
        
        # 创建界面
        self.create_header()
        self.create_color_select()
        self.create_action_buttons()
        self.create_status_area()
        self.create_history_area()
        
        # 启动检测线程
        self.detection_thread = None
        self.running = True
        
    def create_header(self):
        """创建标题栏"""
        header = BoxLayout(
            size_hint_y=0.08,
            padding=5
        )
        
        title = Label(
            text='[color=#00F0FF]♟[/color] JJ象棋AI',
            font_size='16sp',
            bold=True,
            markup=True,
            halign='center',
            valign='middle'
        )
        header.add_widget(title)
        self.add_widget(header)
        
        # 分隔线
        with header.canvas.after:
            Color(*COLOR_PRIMARY, a=0.3)
            Line(points=[10, 0, 270, 0], width=1)
        
    def create_color_select(self):
        """创建颜色选择区域"""
        self.color_box = BoxLayout(
            size_hint_y=0.12,
            padding=5,
            spacing=10
        )
        
        # RED button
        self.red_btn = Button(
            text='[color=#FF3333]红方[/color]',
            markup=True,
            background_color=(0.15, 0.08, 0.08, 1),
            border=[0, 0, 0, 0]
        )
        self.red_btn.bind(on_press=lambda x: self.select_color(True))
        self.color_box.add_widget(self.red_btn)

        # BLACK button
        self.black_btn = Button(
            text='[color=#666666]黑方[/color]',
            markup=True,
            background_color=(0.1, 0.1, 0.1, 1),
            border=[0, 0, 0, 0]
        )
        self.black_btn.bind(on_press=lambda x: self.select_color(False))
        self.color_box.add_widget(self.black_btn)
        
        self.add_widget(self.color_box)
        
    def select_color(self, is_red):
        """选择棋子颜色"""
        self.is_red_player = is_red
        self.chess_engine.reset()
        self.chess_engine.player_is_red = is_red

        # 更新按钮样式
        if is_red:
            self.red_btn.background_color = (0.9, 0.2, 0.2, 0.8)
            self.black_btn.background_color = (0.1, 0.1, 0.1, 1)
            self.current_player = 'black'
            self.status_text = "已选择红方。等待对方落子..."
        else:
            self.black_btn.background_color = (0.3, 0.3, 0.3, 0.8)
            self.red_btn.background_color = (0.15, 0.08, 0.08, 1)
            self.current_player = 'red'
            self.status_text = "已选择黑方。等待对方落子..."

        # 清空历史
        self.move_list = []
        self.move_history = ""
        self.last_detected_move = ""
        self.ai_suggestion = ""
        self.game_started = True
        
    def create_action_buttons(self):
        """创建操作按钮区域"""
        btn_box = BoxLayout(
            size_hint_y=0.22,
            padding=5,
            spacing=8
        )
        btn_box.orientation = 'vertical'
        
        # Row 1: Enemy moved + I moved
        row1 = BoxLayout(spacing=8)
        
        self.enemy_btn = Button(
            text='[color=#FFD700]对方落子[/color]',
            markup=True,
            background_color=(0.2, 0.18, 0.05, 1),
            border=[0, 0, 0, 0],
            font_size='11sp'
        )
        self.enemy_btn.bind(on_press=self.on_enemy_moved)
        row1.add_widget(self.enemy_btn)

        self.my_btn = Button(
            text='[color=#00FF88]我已落子[/color]',
            markup=True,
            background_color=(0.05, 0.18, 0.12, 1),
            border=[0, 0, 0, 0],
            font_size='11sp'
        )
        self.my_btn.bind(on_press=self.on_my_moved)
        row1.add_widget(self.my_btn)

        btn_box.add_widget(row1)

        # Row 2: Get hint + Clear
        row2 = BoxLayout(spacing=8)

        self.hint_btn = Button(
            text='[color=#00F0FF]AI分析[/color]',
            markup=True,
            background_color=(0.05, 0.15, 0.2, 1),
            border=[0, 0, 0, 0],
            font_size='12sp'
        )
        self.hint_btn.bind(on_press=self.get_ai_hint)
        row2.add_widget(self.hint_btn)

        self.clear_btn = Button(
            text='清空',
            background_color=(0.15, 0.1, 0.1, 1),
            border=[0, 0, 0, 0],
            font_size='12sp'
        )
        self.clear_btn.bind(on_press=self.clear_all)
        row2.add_widget(self.clear_btn)

        btn_box.add_widget(row2)

        # Row 3: Start detection + Stop detection
        row3 = BoxLayout(spacing=8)

        self.start_monitor_btn = Button(
            text='开始检测',
            background_color=(0.1, 0.15, 0.1, 1),
            border=[0, 0, 0, 0],
            font_size='11sp'
        )
        self.start_monitor_btn.bind(on_press=self.start_monitoring)
        row3.add_widget(self.start_monitor_btn)

        self.stop_monitor_btn = Button(
            text='停止检测',
            background_color=(0.15, 0.1, 0.1, 1),
            border=[0, 0, 0, 0],
            font_size='11sp'
        )
        self.stop_monitor_btn.bind(on_press=self.stop_monitoring)
        row3.add_widget(self.stop_monitor_btn)
        
        btn_box.add_widget(row3)
        
        self.add_widget(btn_box)
        
    def create_status_area(self):
        """创建状态显示区域"""
        # AI hint label
        self.hint_label = Label(
            text='[color=#00F0FF]等待AI分析...[/color]',
            markup=True,
            font_size='13sp',
            size_hint_y=0.10,
            text_size=(280, None),
            halign='center',
            valign='middle'
        )
        self.add_widget(self.hint_label)

        # Detected move
        self.detect_label = Label(
            text='检测结果: 无',
            font_size='11sp',
            color=COLOR_TEXT_DIM,
            size_hint_y=0.08,
            text_size=(260, None),
            halign='center',
            valign='middle'
        )
        self.add_widget(self.detect_label)

        # Status label
        self.status_label = Label(
            text=self.status_text,
            font_size='11sp',
            color=COLOR_TEXT_DIM,
            size_hint_y=0.06,
            text_size=(280, None),
            halign='center',
            valign='middle'
        )
        self.add_widget(self.status_label)

    def create_history_area(self):
        """创建历史记录区域"""
        # History header
        hist_header = Label(
            text='--- 走法记录 ---',
            font_size='11sp',
            color=COLOR_PRIMARY,
            size_hint_y=0.05
        )
        self.add_widget(hist_header)

        # History scroll view
        self.history_scroll = ScrollView(
            size_hint_y=0.2,
            do_scroll_x=True,
            do_scroll_y=True
        )

        self.history_label = Label(
            text='暂无记录',
            font_size='11sp',
            color=COLOR_TEXT_DIM,
            size_hint_x=1,
            text_size=(280, None),
            halign='left',
            valign='top'
        )
        self.history_scroll.add_widget(self.history_label)
        self.add_widget(self.history_scroll)
        
    def on_enemy_moved(self, instance):
        """对方落子"""
        if not self.game_started:
            self.status_text = "请先选择棋子颜色"
            return

        self.status_text = "正在检测对方走法..."
        self.enemy_btn.disabled = True

        # Detect in background thread
        threading.Thread(target=self._detect_enemy_move, daemon=True).start()
        
    def _detect_enemy_move(self):
        """Background detect enemy move"""
        try:
            # Call board detector
            detected = self.board_detector.detect_move(self.current_player)
            
            if detected:
                self.detected_enemy_move = detected
                self.last_detected_move = detected
                # Update UI
                Clock.schedule_once(lambda dt: self._on_detection_complete(detected), 0.1)
            else:
                Clock.schedule_once(lambda dt: self._on_detection_failed(), 0.1)
        except Exception as e:
            Clock.schedule_once(lambda dt: self._on_detection_error(str(e)), 0.1)
            
    def _on_detection_complete(self, move):
        """检测完成回调"""
        self.detect_label.text = f'检测到: {move}'
        self.detect_label.color = (0, 1, 0.5, 1)
        self.status_text = f"对方: {move}。点击「AI分析」"

        # Switch current player
        self.current_player = 'red' if self.current_player == 'black' else 'black'

        # Record move
        self.move_list.append(f"{'黑方' if self.current_player == 'black' else '红方'}: {move}")
        self._update_history()

        self.enemy_btn.disabled = False

    def _on_detection_failed(self):
        """检测失败回调"""
        self.detect_label.text = '未检测到走法'
        self.detect_label.color = (1, 0.5, 0, 1)
        self.status_text = "自动检测失败，请尝试手动输入"
        self.enemy_btn.disabled = False

    def _on_detection_error(self, error):
        """检测错误回调"""
        self.detect_label.text = f'错误: {error[:20]}'
        self.detect_label.color = (1, 0.2, 0.2, 1)
        self.status_text = "检测出错，请重试"
        self.enemy_btn.disabled = False

    def get_ai_hint(self, instance):
        """获取AI建议"""
        if not self.game_started:
            self.status_text = "请先选择棋子颜色"
            return

        # If no detected move, prompt user
        if not self.detected_enemy_move:
            self.status_text = "请先点击「对方落子」"
            return

        self.status_text = "正在分析..."
        self.hint_btn.disabled = True
        self.thinking = True

        # Show loading animation
        self.hint_label.text = '[color=#00F0FF]正在分析...[/color]'
        
        # Analyze in background thread
        threading.Thread(target=self._analyze_with_ai, daemon=True).start()
        
    def _analyze_with_ai(self):
        """后台AI分析"""
        try:
            # Get AI suggestion
            result = self.chess_engine.analyze_and_suggest(self.detected_enemy_move)

            if result:
                self.pending_suggestion = result
                Clock.schedule_once(lambda dt: self._show_suggestion(result), 0.1)
            else:
                Clock.schedule_once(lambda dt: self._show_error("AI分析失败"), 0.1)
        except Exception as e:
            Clock.schedule_once(lambda dt: self._show_error(f"错误: {str(e)[:30]}"), 0.1)

    def _show_suggestion(self, suggestion):
        """显示AI建议"""
        self.thinking = False
        self.hint_btn.disabled = False

        # Show suggestion text
        self.hint_label.text = f'[color=#FFD700]建议: {suggestion}[/color]'
        self.ai_suggestion = suggestion
        self.status_text = "按照提示落子"

        # Get start/end for animation
        start, end = self.chess_engine.parse_move(suggestion)
        if start and end:
            self._play_animation(start, end, suggestion)

    def _show_error(self, msg):
        """显示错误"""
        self.thinking = False
        self.hint_btn.disabled = False
        self.hint_label.text = f'[color=#FF4444]{msg}[/color]'
        self.status_text = msg

    def _play_animation(self, start, end, move_text):
        """播放走法提示动画"""
        try:
            # Create animation hint window
            self.anim_hint = AnimationHintWidget(
                start_pos=start,
                end_pos=end,
                move_text=move_text,
                is_red_piece=(not self.is_red_player)
            )
            self.anim_hint.open()
        except Exception as e:
            print(f"动画失败: {e}")

    def on_my_moved(self, instance):
        """我已落子"""
        if not self.game_started:
            self.status_text = "请先选择棋子颜色"
            return

        # Record my move
        my_color = '红方' if self.is_red_player else '黑方'
        self.status_text = f"{my_color}已落子。等待对方..."

        # Switch current player
        self.current_player = 'red' if self.current_player == 'black' else 'black'

        # Clear detection state for next round
        self.detected_enemy_move = ""
        self.last_detected_move = ""
        self.hint_label.text = '[color=#00F0FF]等待AI分析...[/color]'
        self.detect_label.text = '检测结果: 无'
        self.detect_label.color = COLOR_TEXT_DIM

    def clear_all(self, instance):
        """清除所有记录"""
        self.chess_engine.reset()
        self.move_list = []
        self.move_history = ""
        self.detected_enemy_move = ""
        self.last_detected_move = ""
        self.ai_suggestion = ""
        self.current_player = 'red' if not self.is_red_player else 'black'
        self.game_started = False

        self.history_label.text = '暂无记录'
        self.hint_label.text = '[color=#00F0FF]等待AI分析...[/color]'
        self.detect_label.text = '检测结果: 无'
        self.status_text = "已清空，请重新开始"
        self.detect_label.color = COLOR_TEXT_DIM

    def _update_history(self):
        """更新历史记录"""
        if self.move_list:
            self.history_label.text = '\n'.join(self.move_list)
        else:
            self.history_label.text = '暂无记录'

    def start_monitoring(self, instance):
        """开始自动检测"""
        if not self.game_started:
            self.status_text = "请先选择棋子颜色"
            return

        self.status_text = "正在启动检测..."
        self.start_monitor_btn.text = "检测中..."
        self.start_monitor_btn.disabled = True

        # Start monitoring thread
        if self.detection_thread is None or not self.detection_thread.is_alive():
            self.running = True
            self.detection_thread = threading.Thread(target=self._auto_monitor, daemon=True)
            self.detection_thread.start()

    def stop_monitoring(self, instance):
        """停止自动检测"""
        self.running = False
        self.start_monitor_btn.text = "开始检测"
        self.start_monitor_btn.disabled = False
        self.status_text = "已停止检测"
    def _auto_monitor(self):
        """自动检测循环"""
        while self.running:
            try:
                # Periodically check for new moves
                detected = self.board_detector.detect_move(self.current_player)
                if detected and detected != self.last_detected_move:
                    Clock.schedule_once(lambda dt: self._on_detection_complete(detected), 0.1)
                    # Wait for user to process
                    time.sleep(2)
            except:
                pass
            time.sleep(0.5)  # Check every 0.5s

    def on_stop(self):
        """应用停止"""
        self.running = False


class AnimationHintWidget(Popup):
    """动画提示窗口 - 全屏覆盖"""

    def __init__(self, start_pos, end_pos, move_text, is_red_piece, **kwargs):
        super().__init__(**kwargs)
        self.auto_dismiss = False
        self.size_hint = (1, 1)
        self.background_color = (0, 0, 0, 0.3)
        self.title = ''

        # Save position info
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.move_text = move_text
        self.is_red_piece = is_red_piece

        # Create content
        content = BoxLayout(orientation='vertical', padding=20)

        # Hint text
        hint_label = Label(
            text=f'[color=#FFD700]建议走法[/color]\n[color=#00F0FF]{move_text}[/color]',
            markup=True,
            font_size='24sp',
            bold=True,
            size_hint_y=0.3
        )
        content.add_widget(hint_label)

        # Board display
        board = ChessBoardWidget(
            start_pos=start_pos,
            end_pos=end_pos,
            is_red_piece=is_red_piece,
            size_hint_y=0.5
        )
        content.add_widget(board)

        # Confirm button
        confirm_btn = Button(
            text='我已落子 - 关闭',
            size_hint_y=0.2,
            background_color=(0.1, 0.2, 0.15, 1)
        )
        confirm_btn.bind(on_press=self.dismiss)
        content.add_widget(confirm_btn)

        self.content = content

        # Start animation
        Clock.schedule_once(lambda dt: self._start_animation(), 0.1)

    def _start_animation(self):
        """启动动画效果"""
        # Blink animation
        anim = Animation(opacity=0.3, duration=0.5) + Animation(opacity=1, duration=0.5)
        anim.repeat = True
        anim.start(self)


class ChessBoardWidget(BoxLayout):
    """Simplified board display - for animation hint"""
    
    def __init__(self, start_pos, end_pos, is_red_piece, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 10
        self.start_pos = start_pos
        self.end_pos = end_pos
        
        # Canvas
        with self.canvas:
            # Background
            Color(0.15, 0.12, 0.08, 1)
            Rectangle(pos=self.pos, size=self.size)
            
            # Board grid
            Color(0.25, 0.2, 0.15, 1)
            for i in range(10):
                for j in range(9):
                    x = self.x + 10 + j * 30
                    y = self.y + 10 + i * 30
                    Line(rectangle=(x, y, 28, 28), width=0.5)
        
        # Start position marker
        with self.canvas.after:
            Color(1, 0.85, 0, 0.8)  # Gold highlight
            Ellipse(
                pos=(self.x + 10 + start_pos[1] * 30 + 5, 
                     self.y + 10 + (9 - start_pos[0]) * 30 + 5),
                size=(18, 18)
            )
            
    def on_size(self, *args):
        """Redraw on size change"""
        self.canvas.clear()
        with self.canvas:
            Color(0.15, 0.12, 0.08, 1)
            Rectangle(pos=self.pos, size=self.size)


class ChessAIApp(App):
    """Chess AI Assistant App"""
    
    def build(self):
        # Set window properties
        self.title = APP_NAME
        self.icon = 'icon.png' if os.path.exists('icon.png') else None
        
        # Create main UI
        root = ChessAIWidget()
        
        # Set background color
        with root.canvas.before:
            Color(*COLOR_BG_DARK)
            Rectangle(pos=root.pos, size=root.size)
            
        root.bind(pos=self._update_bg, size=self._update_bg)
        
        return root
        
    def _update_bg(self, widget, value):
        """Update background"""
        widget.canvas.before.clear()
        with widget.canvas.before:
            Color(*COLOR_BG_DARK)
            Rectangle(pos=widget.pos, size=widget.size)
            
    def on_stop(self):
        """App exit"""
        if hasattr(self, 'root'):
            self.root.on_stop()


# ==================== Main Entry ====================
if __name__ == '__main__':
    print(f"""
╔══════════════════════════════════════╗
║       Chess AI Assistant v{APP_VERSION}       ║
╠══════════════════════════════════════╣
║  Instructions:                        ║
║  1. Select your piece color           ║
║  2. After enemy moves, tap ENEMY     ║
║  3. Tap GET HINT for AI suggestion   ║
║  4. Follow animation to move         ║
║  5. Tap I MOVED to continue          ║
║                                      ║
║  Tip: Enable START MONITOR for auto   ║
╚══════════════════════════════════════╝
    """)
    ChessAIApp().run()
