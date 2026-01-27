# Стартовое меню
import arcade
from arcade.gui import UIManager, UIFlatButton, UILabel
from arcade.gui.widgets.layout import UIAnchorLayout, UIBoxLayout
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from views.game_view import GameView, SCREEN_WIDTH, SCREEN_HEIGHT


class MenuView(arcade.View):
    def __init__(self):
        super().__init__()

        self.manager = None
        self.setup_ui()

    def setup_ui(self):
        self.manager = UIManager()
        self.manager.enable()

        anchor_layout = UIAnchorLayout()
        box_layout = UIBoxLayout(vertical=True, space_between=30)

        title_label = UILabel(
            text="ПОБЕГ ИЗ ЛАБОРАТОРИИ",
            font_size=48,
            text_color=arcade.color.WHITE,
            width=600,
            align="center"
        )
        box_layout.add(title_label)

        subtitle_label = UILabel(
            text="Lab Escape",
            font_size=24,
            text_color=arcade.color.YELLOW,
            width=300,
            align="center"
        )
        box_layout.add(subtitle_label)

        spacer = UILabel(text="", width=100, height=50)
        box_layout.add(spacer)

        start_button = UIFlatButton(
            text="🎮 Начать игру",
            width=250,
            height=60
        )
        start_button.on_click = self.on_start_click
        box_layout.add(start_button)

        exit_button = UIFlatButton(
            text="🚪 Выход",
            width=250,
            height=60
        )
        exit_button.on_click = self.on_exit_click
        box_layout.add(exit_button)

        controls_label = UILabel(
            text="Управление: A/D или ←/→ - движение, Пробел - прыжок",
            font_size=14,
            text_color=arcade.color.LIGHT_GRAY,
            width=500,
            align="center"
        )
        box_layout.add(controls_label)

        anchor_layout.add(box_layout)
        self.manager.add(anchor_layout)

    def on_show_view(self):
        arcade.set_background_color(arcade.color.DARK_BLUE_GRAY)
        if self.manager:
            self.manager.enable()

    def on_hide_view(self):
        if self.manager:
            self.manager.disable()

    def on_draw(self):
        self.clear()

        arcade.draw_lbwh_rectangle_filled(
            0, 0, SCREEN_WIDTH, SCREEN_HEIGHT,
            arcade.color.DARK_BLUE_GRAY
        )

        self.manager.draw()

    def on_start_click(self, event=None):
        game_view = GameView(level=1)
        self.window.show_view(game_view)

    def on_exit_click(self, event=None):
        arcade.close_window()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ENTER or key == arcade.key.SPACE:
            self.on_start_click()
        elif key == arcade.key.ESCAPE:
            self.on_exit_click()

