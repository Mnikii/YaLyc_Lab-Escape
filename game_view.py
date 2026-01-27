"""
Обертка для совместимости с menu_view.py
Перенаправляет импорт на views.game_view
"""

from views.game_view import *

# Явно экспортируем основные классы
from views.game_view import GameView, SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE

__all__ = ['GameView', 'SCREEN_WIDTH', 'SCREEN_HEIGHT', 'SCREEN_TITLE']

