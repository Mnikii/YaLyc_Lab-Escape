# Логика игрового персонажа
import arcade


class Player(arcade.Sprite):
    def __init__(self):
        super().__init__()
        self.scale = 1.0
        self.speed_x = 5
        self.speed_y = 10
        self.health = 100

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
        self.is_walking = False

        self.face_direction = 0

        #  self.on_ground = True

        self.move_left, self.move_right, self.wants_to_jump = False, False, False

    def on_key_press(self, key, modifiers):
        if key in (arcade.key.A, arcade.key.LEFT):
            self.move_left = True
            self.is_walking = True
            self.face_direction = 1

        if key in (arcade.key.D, arcade.key.RIGHT):
            self.move_right = True
            self.is_walking = True
            self.face_direction = 0

        if key in (arcade.key.W, arcade.key.UP, arcade.key.SPACE):
            self.wants_to_jump = True

    def on_key_release(self, key, modifiers):
        if key in (arcade.key.A, arcade.key.LEFT):
            self.move_left = False
            self.is_walking = False

        if key in (arcade.key.D, arcade.key.RIGHT):
            self.move_right = False
            self.is_walking = False

        if key in (arcade.key.W, arcade.key.UP, arcade.key.SPACE):
            self.wants_to_jump = False

    def update_animation(self, delta_time):
        if self.is_walking:
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
            if self.face_direction == 0:
                self.texture = self.idle_texture
            else:
                self.texture = self.idle_texture.flip_horizontally()

    def update(self, delta_time):
        self.change_x = 0
        if self.move_left:
            self.change_x = -self.speed_x
        if self.move_right:
            self.change_x = self.speed_x
#  Гравитация в main
        if self.wants_to_jump:
            self.change_y = self.speed_y
            #  потом self.on_ground добавить


        self.update_animation(delta_time)

        self.center_x += self.change_x
        self.center_y += self.change_y