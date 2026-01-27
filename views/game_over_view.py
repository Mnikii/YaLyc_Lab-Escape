# Экран завершения
import arcade
from arcade.gui import UIManager, UIFlatButton, UITextureButton, UILabel, UIMessageBox
from arcade.gui.widgets.layout import UIAnchorLayout, UIBoxLayout

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600


class Game_Over_View(arcade.View):
    def __init__(self, result=True, score="0", timer="00:00", statistic="Игра завершена"):
        super().__init__()
        self.result = result
        self.timer = timer
        self.score = score
        self.statistic = statistic

        self.manager = None

    def on_show_view(self):
        arcade.set_background_color((30, 30, 50, 255))

        self.manager = UIManager()
        self.manager.enable()

        self.anchor_layout = UIAnchorLayout()
        self.box_layout = UIBoxLayout(vertical=True, space_between=20)

        self.setup_widgets()

        self.anchor_layout.add(self.box_layout)
        self.manager.add(self.anchor_layout)

    def on_hide_view(self):
        if self.manager:
            self.manager.disable()

    def setup_widgets(self):
        label = UILabel(text="ИГРА ОКОНЧЕНА",
                        font_size=40,
                        text_color=arcade.color.ELECTRIC_BLUE, # также доступны: OLD_SILVER, DARK_BLUE PALE_TURQUOISE
                        width=300,
                        align="center")
        self.box_layout.add(label)

        # победа/проигрыш
        if self.result:
            label_result = UILabel(text="🎉 Вы победили! 🎉",
                                   font_size=20,
                                   text_color=arcade.color.ANTI_FLASH_WHITE, # PURPLE,STEEL_BLUE LIGHT_PINK
                                   width=300,
                                   align="center")
            self.box_layout.add(label_result)


        else:
            label_result = UILabel(text="Вы проиграли!",
                                   font_size=20,
                                   text_color=arcade.color.DEEP_SPACE_SPARKLE, #PURPLE
                                   width=300,
                                   align="center")
            self.box_layout.add(label_result)
        # статистика
        texture_normal = arcade.load_texture(":resources:/gui_basic_assets/button/red_normal.png")
        texture_hovered = arcade.load_texture(":resources:/gui_basic_assets/button/red_hover.png")
        texture_pressed = arcade.load_texture(":resources:/gui_basic_assets/button/red_press.png")

        static_button = UITextureButton(text="⏹️  ПОЛНЫЙ ОТЧЕТ", width=200, height=50, color=arcade.color.HOT_PINK,
                                        texture=texture_normal,
                                        texture_hovered=texture_hovered,
                                        texture_pressed=texture_pressed,
                                        scale=1.0)
        static_button.on_click = self.show_statistics
        self.box_layout.add(static_button)

        # вернуться в main
        leave_button = UIFlatButton(text="⚠️  АВАРИЙНЫЙ ВЫХОД", width=200, height=50,
                                    color=arcade.color.HOT_PINK)
        leave_button.on_click = self.on_click_open
        self.box_layout.add(leave_button)

    def on_draw(self):
        self.clear()
        self.manager.draw()

    def on_click_open(self, event):
        # Возвращаемся в главное меню
        from views.menu_view import MenuView
        menu = MenuView()
        self.window.show_view(menu)

    def show_statistics(self, event):
        stats_box = UIMessageBox(
            width=450,
            height=300,
            message_text= f"СТАТИСТИКА ИГРЫ\n\n•{self.statistic}\n\n•Время: {self.timer}\n•Очки: {self.score}\n• Убито врагов: 42\n"
                          f"• Пройдено уровней: 5\n"
                          f"• Общее время: 1ч 23м\n"
                          f"\n\n\nᓚ₍^..^₎ ♡ ₍^. .^₎Ⳋ\nСпасибо за игру!",
            buttons=("OK",),
        )

        self.manager.add(stats_box)

    def on_mouse_press(self, x, y, button, modifiers):
        pass  # manager сам обрабатывает