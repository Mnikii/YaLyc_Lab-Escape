# Стартовое меню
import arcade
from arcade.gui import UIManager, UIFlatButton, UILabel, UIMessageBox
from arcade.gui.widgets.layout import UIAnchorLayout, UIBoxLayout
from game_view import GameView

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600


class menu_view(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, "LAB ESCAPE")
        arcade.set_background_color(arcade.color.LIGHT_SLATE_GRAY)

        self.manager = UIManager()
        self.manager.enable()

        self.anchor_layout = UIAnchorLayout()
        self.box_layout = UIBoxLayout(vertical=True, space_between=20)

        self.setup_widgets()

        self.anchor_layout.add(self.box_layout)  # Box в anchor
        self.manager.add(self.anchor_layout)  # Всё в manager

    def setup_widgets(self):
        label = UILabel(text="ПОБЕГ ИЗ ЛАБОРАТОРИИ",
                        font_size=40,
                        text_color=arcade.color.BLACK,
                        width=300,
                        align="center")
        self.box_layout.add(label)

        start_button = UIFlatButton(text="Начать игру", width=200, height=50, color=arcade.color.BLUE)
        start_button.on_click = self.start
        self.box_layout.add(start_button)


        leave_button = UIFlatButton(text="Выйти из игры", width=200, height=50, color=arcade.color.BLUE)
        leave_button.on_click = self.leave
        self.box_layout.add(leave_button)

    def on_draw(self):
        self.clear()
        self.manager.draw()

    def on_mouse_press(self, x, y, button, modifiers):
        pass

    def start(self, event=None):
        game_view = GameView()
        self.window.show_view(game_view)

    def leave(self, event=None):
        arcade.close_window()