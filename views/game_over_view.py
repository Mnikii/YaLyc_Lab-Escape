# Экран завершения

import arcade
import random
from arcade.gui import UIManager, UIFlatButton, UITextureButton, UILabel, UIInputText, UITextArea, UISlider, UIDropdown, \
    UIMessageBox

from arcade.gui.widgets.layout import UIAnchorLayout, UIBoxLayout
import sqlite3

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600


class Game_Over_View(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, "ИГРА ОКОНЧЕНА🧪",
                         result, timer, score, enemies_killed, levels_completed)
        arcade.set_background_color((30, 30, 50))

        self.result = result  # True = победа, False = поражение
        self.timer = timer
        self.score = score
        self.enemies_killed = enemies_killed
        self.levels_completed = levels_completed
        self.result_text = "ПОБЕДА" if self.result else "ПОРАЖЕНИЕ"

        self.manager = UIManager()
        self.manager.enable()

        # UIAnchorLayout центрирует, UIBoxLayout располагает вертикально
        self.anchor_layout = UIAnchorLayout()
        self.box_layout = UIBoxLayout(vertical=True, space_between=20)

        self.setup_widgets()

        self.anchor_layout.add(self.box_layout)  # Box в anchor
        self.manager.add(self.anchor_layout)  # Всё в manager

        self.create_database()

    def create_database(self):
        # Подключение к базе данных (файл создается автоматически если не существует)
        conn = sqlite3.connect('game_statistics.db')
        cursor = conn.cursor()

        # INTEGER - целое число, PRIMARY KEY - Не может повторяться
        # AUTOINCREMENT - Не нужно вручную указывать ID. Первое: id=1, второе: id=2, и т.д.
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS game_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                result TEXT,
                game_time TEXT,
                score INTEGER,
                enemies_killed INTEGER,
                levels_completed INTEGER
            )
        ''')

        self.save_to_db(conn, cursor)

        conn.commit()
        conn.close()

    def save_to_db(self, conn, cursor):
        cursor.execute('''
                   INSERT INTO game_stats (result, game_time, score, enemies_killed, levels_completed)
                   VALUES (?, ?, ?, ?, ?)
               ''', (self.result_text, self.timer, self.score,
                     self.enemies_killed, self.levels_completed))

    def setup_widgets(self):
        label = UILabel(text="ИГРА ОКОНЧЕНА",
                        font_size=40,
                        text_color=arcade.color.ELECTRIC_BLUE,
                        width=300,
                        align="center")
        self.box_layout.add(label)

        # победа/проигрыш
        if self.result:
            label_result = UILabel(text="🎉 Вы победили! 🎉",
                                   font_size=20,
                                   text_color=arcade.color.ANTI_FLASH_WHITE,
                                   width=300,
                                   align="center")
            self.box_layout.add(label_result)


        else:
            label_result = UILabel(text="Вы проиграли!",
                                   font_size=20,
                                   text_color=arcade.color.DEEP_SPACE_SPARKLE,
                                   width=300,
                                   align="center")
            self.box_layout.add(label_result)
        # статистика
        static_button = UIFlatButton(text="ПОЛНЫЙ ОТЧЕТ", width=200, height=50,
                                     font_name=('Kenney Future', 'arial', 'calibri'), color=arcade.color.HOT_PINK)
        static_button.on_click = self.show_statistics
        self.box_layout.add(static_button)

        # вернуться в main
        leave_button = UIFlatButton(text="ВЫХОД", width=200, height=50,
                                    font_name=('Kenney Future', 'arial', 'calibri'), color=arcade.color.HOT_PINK)
        leave_button.on_click = self.on_click_open
        self.box_layout.add(leave_button)

    def on_update(self, dt):
        pass

    def on_draw(self):
        self.clear()
        self.manager.draw()  # Отрисовка всех UI-элементов

    def on_click_open(self, event):
        warning_box = UIMessageBox(
            width=300, height=200,
            message_text="Посморти статистику перед выходом!!\nХочешь продолжить?",
            buttons=("Да", "Нет")
        )
        self.manager.add(warning_box)
        if warning_box:
            pass  # вернуться на главный экран
        else:
            pass  # остаемся

    def show_statistics(self, event):
        conn = sqlite3.connect('game_statistics.db')
        cursor = conn.cursor()

        # выбираем максимальный id - id последнего игрока
        cursor.execute('''
                SELECT * FROM game_stats 
                WHERE id = (SELECT MAX(id) FROM game_stats)
            ''')
        game_data = cursor.fetchone()

        cursor.execute('SELECT AVG(score) FROM game_stats')
        average_score = int(cursor.fetchone()[0])
        conn.close()

        # Распаковываем данные из БД
        (game_id, result_db, game_time_db, score_db,
         enemies_killed_db, levels_completed_db) = game_data
        score_db = int(score_db)

        if score_db != average_score:
            comparison = "больше" if score_db > average_score else "меньше"
            static_text = f"• Ваша статистика {comparison} среденей на {average_score - score_db}\n"
        else:
            static_text = f"• Ваша статистика равна средней\n"

        # Создаем текст для отображения
        stats_text = (
            f"СТАТИСТИКА ИГРЫ (из БД)\n\n"
            f"• Результат: {result_db}\n"
            f"• Время игры: {game_time_db}\n"
            f"• Очки: {score_db}\n"
            f"• Убито врагов: {enemies_killed_db}\n"
            f"• Пройдено уровней: {levels_completed_db}\n"
            f"{static_text}"
            f"\n\n\nᓚ₍^..^₎ ♡ ₍^. .^₎Ⳋ\nСпасибо за игру!"
        )

        stats_box = UIMessageBox(
            width=450,
            height=300,
            message_text=stats_text,
            buttons=("OK",),
        )

        self.manager.add(stats_box)

    def on_mouse_press(self, x, y, button, modifiers):
        pass  # manager сам обрабатывает