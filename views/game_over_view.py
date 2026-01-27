# Экран завершения
import arcade
from arcade.gui import UIManager, UIFlatButton, UILabel, UIMessageBox
from arcade.gui.widgets.layout import UIAnchorLayout, UIBoxLayout

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from data.database import init_database, save_game_stats, get_last_game_stats, get_average_score

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600


class Game_Over_View(arcade.View):
    def __init__(self, result=True, score="0", timer="00:00", statistic="Игра завершена"):
        super().__init__()

        self.result = result
        self.timer = timer
        self.score = int(score) if isinstance(score, str) and score.isdigit() else int(score) if isinstance(score, int) else 0
        self.statistic = statistic
        self.enemies_killed = 0
        self.levels_completed = 3 if result else 0
        self.result_text = "ПОБЕДА" if self.result else "ПОРАЖЕНИЕ"

        self.manager = None

    def on_show_view(self):
        arcade.set_background_color((30, 30, 50, 255))

        self.manager = UIManager()
        self.manager.enable()

        self.anchor_layout = UIAnchorLayout()
        self.box_layout = UIBoxLayout(vertical=True, space_between=20)

        # Инициализация БД и сохранение статистики
        init_database()
        save_game_stats(
            self.result_text,
            self.timer,
            self.score,
            self.enemies_killed,
            self.levels_completed
        )

        self.setup_widgets()

        self.anchor_layout.add(self.box_layout)
        self.manager.add(self.anchor_layout)

    def on_hide_view(self):
        if self.manager:
            self.manager.disable()

    def setup_widgets(self):
        label = UILabel(
            text="ИГРА ОКОНЧЕНА",
            font_size=40,
            text_color=arcade.color.ELECTRIC_BLUE,
            width=300,
            align="center"
        )
        self.box_layout.add(label)

        if self.result:
            label_result = UILabel(
                text="🎉 Вы победили! 🎉",
                font_size=20,
                text_color=arcade.color.ANTI_FLASH_WHITE,
                width=300,
                align="center"
            )
        else:
            label_result = UILabel(
                text="Вы проиграли!",
                font_size=20,
                text_color=arcade.color.DEEP_SPACE_SPARKLE,
                width=300,
                align="center"
            )
        self.box_layout.add(label_result)

        static_button = UIFlatButton(text="📊 ПОЛНЫЙ ОТЧЕТ", width=200, height=50)
        static_button.on_click = self.show_statistics
        self.box_layout.add(static_button)

        leave_button = UIFlatButton(text="🚪 В МЕНЮ", width=200, height=50)
        leave_button.on_click = self.on_click_open
        self.box_layout.add(leave_button)

    def on_draw(self):
        self.clear()
        self.manager.draw()

    def on_click_open(self, event):
        from views.menu_view import MenuView
        self.window.show_view(MenuView())

    def show_statistics(self, event):
        game_data = get_last_game_stats()
        average_score = get_average_score()

        if game_data:
            game_id, result_db, game_time_db, score_db, enemies_killed_db, levels_completed_db = game_data
            score_db = int(score_db)

            if score_db != average_score:
                comparison = "больше" if score_db > average_score else "меньше"
                diff = abs(score_db - average_score)
                static_text = f"• Ваш счёт {comparison} среднего на {diff}\n"
            else:
                static_text = "• Ваш счёт равен среднему\n"

            stats_text = (
                f"СТАТИСТИКА ИГРЫ\n\n"
                f"• Результат: {result_db}\n"
                f"• Время игры: {game_time_db}\n"
                f"• Очки: {score_db}\n"
                f"• Убито врагов: {enemies_killed_db}\n"
                f"• Пройдено уровней: {levels_completed_db}\n"
                f"{static_text}"
                f"\n\nСпасибо за игру! 🎮"
            )
        else:
            stats_text = "Нет данных о статистике"

        stats_box = UIMessageBox(
            width=450,
            height=300,
            message_text=stats_text,
            buttons=("OK",),
        )
        self.manager.add(stats_box)

    def on_mouse_press(self, x, y, button, modifiers):
        pass

