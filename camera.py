# Камера и её поведение

import arcade

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PLAYER_SPEED = 5
GRAVITY = 0.5
CAMERA_LERP = 0.1  # Скорость следования камеры (чем меньше, тем плавнее)


class Camera(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, "Camera")

        # Создаем камеры
        self.world_camera = arcade.camera.Camera2D()  # Камера для игрового мира
        self.gui_camera = arcade.camera.Camera2D()  # Камера для интерфейса

    def on_update(self, delta_time):
        # Перемещаем камеру за игроком
        self.pan_camera_to_player()

    def pan_camera_to_player(self):
        # Плавное перемещение камеры
        current_x, current_y = self.world_camera.position
        # отставшая камера + (переместившееся? x/y - отставшая) * плавность
        # н-р: 104 + (125 - 104) = 125 = перемещению игрока
        new_x = current_x + (target_x - current_x) * CAMERA_LERP
        new_y = current_y + (target_y - current_y) * CAMERA_LERP

        # Устанавливаем новую позицию камеры
        self.world_camera.position = (new_x, new_y)

    def on_draw(self):
        self.clear()

        # 1) Рисуем игровой мир с помощью камеры
        self.world_camera.use()
        # добавляем shake
        # 2) Рисуем GUI с помощью GUI-камеры
        self.gui_camera.use()
