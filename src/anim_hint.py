#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
落子动画提示模块
功能：
1. 全屏半透明覆盖
2. 棋盘可视化
3. 起点终点高亮动画
4. 脉冲闪烁效果

作者: JJChessAI Team
版本: 1.0.0
"""

import os
import sys
import math
import time
from kivy.animation import Animation
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.graphics import Color, Rectangle, Ellipse, Line, InstructionGroup
from kivy.graphics.texture import Texture
from kivy.properties import NumericProperty, ListProperty
from kivy.clock import Clock
from kivy.core.window import Window


# ==================== 颜色定义 ====================
COLOR_GOLD = (1.0, 0.85, 0.0, 1.0)      # 金色高亮 #FFD700
COLOR_CYAN = (0.0, 0.94, 1.0, 1.0)      # 电光青 #00F0FF
COLOR_RED = (0.9, 0.2, 0.2, 1.0)        # 红色
COLOR_BLACK = (0.2, 0.2, 0.2, 1.0)      # 黑色
COLOR_BG = (0.0, 0.0, 0.0, 0.5)        # 半透明黑色
COLOR_BOARD = (0.85, 0.65, 0.4, 1.0)   # 木质棋盘


# ==================== 棋盘常量 ====================
BOARD_SIZE = 400  # 棋盘边长
CELL_SIZE = BOARD_SIZE // 9  # 格子大小
BOARD_OFFSET_X = 50  # 棋盘左边距
BOARD_OFFSET_Y = 50  # 棋盘下边距


# ==================== 动画提示窗口 ====================
class AnimationHint(Popup):
    """
    落子动画提示弹出窗口
    显示全屏半透明背景 + 棋盘 + 动画提示
    """
    
    def __init__(self, start_pos, end_pos, move_text, is_red_piece=True, **kwargs):
        """
        初始化
        
        参数:
            start_pos: 起点坐标 (row, col)
            end_pos: 终点坐标 (row, col)
            move_text: 走法描述
            is_red_piece: 是否是红方棋子
        """
        super().__init__(**kwargs)
        
        self.auto_dismiss = False
        self.size_hint = (1, 1)
        self.background_color = (0, 0, 0, 0.6)
        self.title = ''
        self.separator_height = 0
        
        # 位置信息
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.move_text = move_text
        self.is_red_piece = is_red_piece
        
        # 创建内容
        self._create_content()
        
        # 启动动画
        Clock.schedule_once(lambda dt: self._start_animation(), 0.1)
        
    def _create_content(self):
        """创建内容布局"""
        content = BoxLayout(
            orientation='vertical',
            padding=20,
            spacing=15
        )
        
        # 标题
        title_label = Label(
            text=f'[color=#FFD700]♟ AI建议走法[/color]',
            markup=True,
            font_size='20sp',
            bold=True,
            size_hint_y=0.1,
            halign='center'
        )
        content.add_widget(title_label)
        
        # 走法提示
        move_label = Label(
            text=f'[color=#00F0FF]{self.move_text}[/color]',
            markup=True,
            font_size='32sp',
            bold=True,
            size_hint_y=0.15,
            halign='center'
        )
        content.add_widget(move_label)
        
        # 棋盘显示区域
        board_container = BoxLayout(
            size_hint_y=0.55,
            padding=10
        )
        
        self.board_widget = ChessBoardAnimatedWidget(
            start_pos=self.start_pos,
            end_pos=self.end_pos,
            is_red_piece=self.is_red_piece
        )
        board_container.add_widget(self.board_widget)
        content.add_widget(board_container)
        
        # 说明文字
        hint_label = Label(
            text='红色圆点: 起点  →  绿色圆点: 终点',
            font_size='14sp',
            color=(0.7, 0.7, 0.7, 1),
            size_hint_y=0.08,
            halign='center'
        )
        content.add_widget(hint_label)
        
        # 确认按钮
        confirm_btn = Button(
            text='[color=#FFFFFF]我已落子，关闭提示[/color]',
            markup=True,
            font_size='16sp',
            size_hint_y=0.12,
            background_color=(0.1, 0.4, 0.3, 1),
            border=[0, 0, 0, 0]
        )
        confirm_btn.bind(on_press=self.dismiss)
        content.add_widget(confirm_btn)
        
        self.content = content
        
    def _start_animation(self):
        """启动动画"""
        # 获取棋盘widget开始动画
        if hasattr(self, 'board_widget'):
            self.board_widget.start_animation()


# ==================== 棋盘动画组件 ====================
class ChessBoardAnimatedWidget(Widget):
    """
    带动画的棋盘组件
    在棋盘上显示起点和终点的动画高亮
    """
    
    def __init__(self, start_pos, end_pos, is_red_piece=True, **kwargs):
        super().__init__(**kwargs)
        
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.is_red_piece = is_red_piece
        self.animation_running = False
        
        # 绑定大小变化
        self.bind(size=self._on_size_change, pos=self._on_size_change)
        
        # 创建棋盘
        self._draw_board()
        
    def _on_size_change(self, *args):
        """大小或位置改变时重绘"""
        self._draw_board()
        
    def _draw_board(self):
        """绘制棋盘"""
        self.canvas.clear()
        
        # 计算棋盘尺寸
        board_width = min(self.width, self.height) * 0.9
        board_height = board_width * (10/9)  # 10:9比例
        cell_size = board_width / 9
        
        offset_x = (self.width - board_width) / 2
        offset_y = (self.height - board_height) / 2
        
        with self.canvas:
            # 背景
            Color(0.2, 0.15, 0.1, 1)
            Rectangle(
                pos=(offset_x - 10, offset_y - 10),
                size=(board_width + 20, board_height + 20)
            )
            
            # 棋盘格子线
            Color(0.5, 0.35, 0.2, 1)
            for i in range(10):  # 10条横线
                y = offset_y + i * cell_size
                Line(
                    points=[offset_x, y, offset_x + board_width, y],
                    width=1
                )
                
            for j in range(9):  # 9条竖线
                x = offset_x + j * cell_size
                if j == 0 or j == 8:
                    # 边线
                    Line(
                        points=[x, offset_y, x, offset_y + board_height],
                        width=2
                    )
                else:
                    # 中间的线（不画过楚河汉界）
                    if i < 5:
                        Line(
                            points=[x, offset_y, x, offset_y + 4 * cell_size],
                            width=1
                        )
                    else:
                        Line(
                            points=[x, offset_y + 5 * cell_size, x, offset_y + board_height],
                            width=1
                        )
                        
            # 炮和兵的标记点
            Color(0.5, 0.35, 0.2, 1)
            for pos in [(2, 1), (2, 7), (7, 1), (7, 7)]:
                self._draw_dot(offset_x, offset_y, cell_size, pos)
                
            for pos in [(3, 0), (3, 2), (3, 4), (3, 6), (3, 8),
                        (6, 0), (6, 2), (6, 4), (6, 6), (6, 8)]:
                self._draw_dot(offset_x, offset_y, cell_size, pos)
                
    def _draw_dot(self, offset_x, offset_y, cell_size, pos):
        """画小圆点"""
        row, col = pos
        x = offset_x + col * cell_size
        y = offset_y + row * cell_size
        Ellipse(pos=(x-2, y-2), size=(4, 4))
        
    def start_animation(self):
        """开始动画"""
        if self.animation_running:
            return
        self.animation_running = True
        
        # 创建高亮组
        self.highlight_group = InstructionGroup()
        
        # 计算棋盘位置
        board_width = min(self.width, self.height) * 0.9
        cell_size = board_width / 9
        offset_x = (self.width - board_width) / 2
        offset_y = (self.height - board_height) / 2
        
        board_height = board_width * (10/9)
        
        # 绘制起点（红色脉冲）
        start_row, start_col = self.start_pos
        start_x = offset_x + start_col * cell_size
        start_y = offset_y + (9 - start_row) * cell_size  # 坐标系转换
        
        self._draw_pulse_circle(start_x, start_y, cell_size * 0.4, COLOR_RED)
        
        # 绘制终点（绿色脉冲）
        end_row, end_col = self.end_pos
        end_x = offset_x + end_col * cell_size
        end_y = offset_y + (9 - end_row) * cell_size
        
        self._draw_pulse_circle(end_x, end_y, cell_size * 0.4, (0.2, 0.9, 0.3, 1))
        
        # 添加到画布
        self.canvas.add(self.highlight_group)
        
        # 启动闪烁动画
        Clock.schedule_interval(self._animate, 0.5)
        
        # 5秒后自动停止
        Clock.schedule_once(lambda dt: self.stop_animation(), 5)
        
    def _draw_pulse_circle(self, x, y, radius, color):
        """绘制脉冲圆圈"""
        # 外圈
        Color(*color[:3], a=0.3)
        Ellipse(
            pos=(x - radius, y - radius),
            size=(radius * 2, radius * 2)
        )
        
        # 内圈
        Color(*color[:3], a=0.6)
        Ellipse(
            pos=(x - radius * 0.7, y - radius * 0.7),
            size=(radius * 1.4, radius * 1.4)
        )
        
        # 中心点
        Color(*color[:3], a=1.0)
        Ellipse(
            pos=(x - radius * 0.3, y - radius * 0.3),
            size=(radius * 0.6, radius * 0.6)
        )
        
    def _animate(self, dt):
        """动画回调 - 闪烁效果"""
        if not self.animation_running:
            return
            
        # 简单闪烁
        current_alpha = getattr(self, '_highlight_alpha', 1.0)
        new_alpha = 0.4 if current_alpha > 0.5 else 1.0
        self._highlight_alpha = new_alpha
        
    def stop_animation(self):
        """停止动画"""
        self.animation_running = False
        Clock.unschedule(self._animate)
        self.highlight_group = None


# ==================== 简化动画提示 ====================
class SimpleAnimationHint(Popup):
    """
    简化版动画提示
    适用于性能较差的设备
    """
    
    def __init__(self, start_pos, end_pos, move_text, is_red_piece=True, **kwargs):
        super().__init__(**kwargs)
        
        self.auto_dismiss = False
        self.size_hint = (0.8, 0.6)
        self.background_color = (0.05, 0.05, 0.08, 0.95)
        self.title = ''
        
        # 创建简洁内容
        content = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # 走法显示
        move_label = Label(
            text=f'[color=#FFD700]建议:[/color] [color=#00F0FF]{move_text}[/color]',
            markup=True,
            font_size='28sp',
            bold=True,
            size_hint_y=0.3
        )
        content.add_widget(move_label)
        
        # 位置信息
        info_label = Label(
            text=f'从 {self._format_pos(start_pos)} 移动到 {self._format_pos(end_pos)}',
            font_size='16sp',
            color=(0.7, 0.7, 0.7, 1),
            size_hint_y=0.3
        )
        content.add_widget(info_label)
        
        # 确认按钮
        confirm_btn = Button(
            text='我已落子',
            size_hint_y=0.2,
            background_color=(0.1, 0.3, 0.3, 1)
        )
        confirm_btn.bind(on_press=self.dismiss)
        content.add_widget(confirm_btn)
        
        self.content = content
        
        # 3秒后自动消失
        Clock.schedule_once(lambda dt: self.dismiss(), 3)
        
    def _format_pos(self, pos):
        """格式化位置"""
        if not pos:
            return "?"
        row, col = pos
        cols = '一二三四五六七八九'
        return f"{cols[col]}{row + 1}"


# ==================== 工具函数 ====================
def show_animation_hint(start_pos, end_pos, move_text, is_red_piece=True, use_simple=True):
    """
    显示动画提示的便捷函数
    
    参数:
        start_pos: 起点
        end_pos: 终点
        move_text: 走法描述
        is_red_piece: 是否为红方
        use_simple: 是否使用简化版本
    """
    if use_simple:
        hint = SimpleAnimationHint(
            start_pos=start_pos,
            end_pos=end_pos,
            move_text=move_text,
            is_red_piece=is_red_piece
        )
    else:
        hint = AnimationHint(
            start_pos=start_pos,
            end_pos=end_pos,
            move_text=move_text,
            is_red_piece=is_red_piece
        )
    hint.open()
    return hint


# ==================== 测试代码 ====================
if __name__ == '__main__':
    from kivy.app import App
    
    class TestApp(App):
        def build(self):
            # 测试动画
            hint = SimpleAnimationHint(
                start_pos=(0, 1),  # 马的起始位置
                end_pos=(2, 2),    # 马的目标位置
                move_text="马8进7",
                is_red_piece=False
            )
            hint.open()
            return Widget()
            
    TestApp().run()
