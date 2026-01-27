import arcade


class Player(arcade.Sprite):
    def __init__(self):
        super().__init__()
        self.scale = 1.0
        self.speed_x = 10
        self.speed_y = 30
        self.health = 100

        # Движение
        self.change_x = 0
        self.change_y = 0

        # Прыжки
        self.jumps_available = 2
        self.is_jumping = False
        self.on_ground = True

        # Текстуры
        self.idle_texture = arcade.load_texture(
            ":resources:/images/animated_characters/male_person/malePerson_idle.png")
        self.texture = self.idle_texture

        self.jump_texture = arcade.load_texture(
            ":resources:/images/animated_characters/male_person/malePerson_jump.png")

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
        self.move_left = False
        self.move_right = False

    def on_key_press(self, key, modifiers):
        if key in (arcade.key.A, arcade.key.LEFT):
            self.move_left = True
            self.face_direction = 1

        if key in (arcade.key.D, arcade.key.RIGHT):
            self.move_right = True
            self.face_direction = 0

    def on_key_release(self, key, modifiers):
        if key in (arcade.key.A, arcade.key.LEFT):
            self.move_left = False

        if key in (arcade.key.D, arcade.key.RIGHT):
            self.move_right = False

    def update_animation(self, delta_time):
        walking = self.move_left or self.move_right

        if not self.on_ground:
            if self.face_direction == 0:
                self.texture = self.jump_texture
            else:
                self.texture = self.jump_texture.flip_horizontally()

        elif walking:
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
            if self.face_direction == 0:
                self.texture = self.idle_texture
            else:
                self.texture = self.idle_texture.flip_horizontally()

    def update(self, delta_time):
        # Управление движением
        self.change_x = 0
        if self.move_left:
            self.change_x = -self.speed_x
        if self.move_right:
            self.change_x = self.speed_x

        # Анимация
        self.update_animation(delta_time)

    def take_damage(self, dmg):
        self.health -= dmg
        return not self.check_if_alive()

    def check_if_alive(self):
        return self.health > 0

