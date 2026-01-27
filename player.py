import arcade
from bullet import Bullet


class Player(arcade.Sprite):
    def __init__(self):
        super().__init__()
        self.scale = 1.0
        self.speed_x = 7
        self.speed_y = 17
        self.health = 100

        # Движение
        self.change_x = 0
        self.change_y = 0

        # Прыжки
        self.jumps_available = 2
        self.is_jumping = False
        self.on_ground = True

        # Стрельба
        self.bullet_list = None
        self.shoot_cooldown = 0.3
        self.shoot_timer = 0
        self.target = None, None

        # Текстуры
        self.idle_texture = arcade.load_texture(
            ":resources:/images/animated_characters/male_person/malePerson_idle.png")
        self.texture = self.idle_texture

        self.walk_textures = []
        for i in range(0, 8):
            texture = arcade.load_texture(f":resources:/images/animated_characters/male_person/malePerson_walk{i}.png")
            self.walk_textures.append(texture)

        self.current_texture = 0
        self.texture_change_time = 0
        self.texture_change_delay = 0.1

        # Состояния
        self.is_walking = False
        self.face_direction = 0  # 0 - вправо, 1 - влево

        # Управление
        self.move_left, self.move_right, self.wants_to_jump = False, False, False
        self.wants_to_shoot = False

    def set_bullet_list(self, bullet_list):
        #  Передача списка пуль из main
        self.bullet_list = bullet_list

    # Движение на wasd/стрелками, меняем направление взгляда игрока если нужно
    def on_key_press(self, key, modifiers):
        if key in (arcade.key.A, arcade.key.LEFT):
            self.move_left = True
            self.face_direction = 1

        if key in (arcade.key.D, arcade.key.RIGHT):
            self.move_right = True
            self.face_direction = 0

        if key in (arcade.key.W, arcade.key.UP, arcade.key.SPACE):
            self.wants_to_jump = True

    def on_key_release(self, key, modifiers):
        if key in (arcade.key.A, arcade.key.LEFT):
            self.move_left = False

        if key in (arcade.key.D, arcade.key.RIGHT):
            self.move_right = False

        if key in (arcade.key.W, arcade.key.UP, arcade.key.SPACE):
            self.wants_to_jump = False

    # target хранит координаты клика мышкой, выстрел в последнюю точку куда кликнули
    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            self.wants_to_shoot = True
            self.target = x, y

    def on_mouse_release(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            self.wants_to_shoot = False

    # анимация, если игрок ходит текстура меняется каждую 0,1 секунды(texture_change_delay)
    def update_animation(self, delta_time):
        walking = self.move_left or self.move_right

        if walking:
            self.is_walking = True
            self.texture_change_time += delta_time
            if self.texture_change_time >= self.texture_change_delay:
                self.texture_change_time = 0
                self.current_texture += 1
                if self.current_texture >= len(self.walk_textures):
                    self.current_texture = 0

                if self.face_direction == 0:
                    self.texture = self.walk_textures[self.current_texture]
                else:
                    self.texture = self.walk_textures[self.current_texture].flip_horizontally()
        else:
            self.is_walking = False
            # 0 - право, 1 - лево, отзеркаливаем текстуру если игрок смотрит налево
            if self.face_direction == 0:
                self.texture = self.idle_texture
            else:
                self.texture = self.idle_texture.flip_horizontally()

    def on_land(self):  # Вызывается в main в момент приземления, обновляем кол-во доступных прыжков
        self.jumps_available = 2
        self.is_jumping = False
        self.on_ground = True

    def jump(self): # Прыжок только если есть доступные(можно совершить максимум двойной прыжок)
        if self.jumps_available > 0:
            self.change_y = self.speed_y
            self.jumps_available -= 1
            self.is_jumping = True
            self.on_ground = False
            self.wants_to_jump = False
            return True
        return False

    # Если можем выстрелить, есть цель и передан список пуль
    def shoot(self, target):
        x, y = target
        if x is not None and y is not None and self.bullet_list is not None:
            bullet = Bullet(
                start_x=self.center_x,
                start_y=self.center_y,
                target_x=x,
                target_y=y
            )
            self.bullet_list.append(bullet)

    def update(self, delta_time):
        # Управление движением
        self.change_x = 0
        if self.move_left:
            self.change_x = -self.speed_x
        if self.move_right:
            self.change_x = self.speed_x

        # Прыжок
        if self.wants_to_jump:
            self.jump()

        # Стрельба
        if self.shoot_timer > 0:  # обновление таймера перезаярдки
            self.shoot_timer -= delta_time

        # Выстрел только если прошла перезарядка(self.shoot_timer)
        if self.wants_to_shoot and self.shoot_timer <= 0:
            self.shoot(self.target)
            self.shoot_timer = self.shoot_cooldown
            self.wants_to_shoot = False

        # Обновление анимации
        self.update_animation(delta_time)

    def take_damage(self, dmg):
        self.health -= dmg

    # Проверка, жив ли игрок
    def check_if_alive(self):
        return self.health > 0