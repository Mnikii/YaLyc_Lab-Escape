# Камера и её поведение
# пока без shake и я не уверена стоит ли делать dead zone

import arcade

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PLAYER_SPEED = 5
GRAVITY = 0.5
CAMERA_LERP = 0.1  # Скорость следования камеры (чем меньше, тем плавнее)

class MyGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, "Camera")

        # Создаем камеры
        self.world_camera = arcade.camera.Camera2D()  # Камера для игрового мира
        self.gui_camera = arcade.camera.Camera2D()  # Камера для интерфейса

        # Опционально: тряска камеры (если нужно) аттаке врага
        self.camera_shake = arcade.camera.grips.ScreenShake2D(
            self.world_camera.view_data,  # Трястись будет только то, что попадает в объектив мировой камеры
            max_amplitude=15.0,
            acceleration_duration=0.1,
            falloff_time=0.5,
            shake_frequency=10.0,
        )

        # Спрайт игрока
        self.player = arcade.Sprite(
            ":resources:/images/animated_characters/female_adventurer/femaleAdventurer_idle.png",
            scale=0.5
        )
        self.player.center_x = 100
        self.player.center_y = 100
        self.player_spritelist = arcade.SpriteList()
        self.player_spritelist.append(self.player)

        # Загрузка тайловой карты
        self.tile_map = arcade.load_tilemap(
            ":resources:/tiled_maps/level_1.json",
            scaling=0.5
        )
        self.scene = arcade.Scene.from_tilemap(self.tile_map)

        # Физический движок
        self.physics_engine = arcade.PhysicsEngineSimple(
            self.player,
            self.scene["Platforms"]
        )

    def on_update(self, delta_time):
        self.player.change_y -= GRAVITY
        self.physics_engine.update()

        # Перемещаем камеру за игроком
        self.pan_camera_to_player()

    def pan_camera_to_player(self):
        target_x = self.player.center_x
        target_y = self.player.center_y

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

        # 1) Рисуем игровой мир с помощью мировой камеры
        self.world_camera.use()
        self.scene.draw()
        self.player_spritelist.draw()

        # Опционально: обновляем тряску камеры
        # self.camera_shake.update_camera()
        # self.camera_shake.readjust_camera()

        # 2) Рисуем GUI с помощью GUI-камеры
        self.gui_camera.use()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.UP or key == arcade.key.W:
            self.player.change_y = PLAYER_SPEED * 5
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.player.change_y = -PLAYER_SPEED
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.player.change_x = -PLAYER_SPEED
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.player.change_x = PLAYER_SPEED

    def on_key_release(self, key, modifiers):
        if key in [arcade.key.UP, arcade.key.DOWN, arcade.key.W, arcade.key.S]:
            self.player.change_y = 0
        if key in [arcade.key.LEFT, arcade.key.RIGHT, arcade.key.A, arcade.key.D]:
            self.player.change_x = 0