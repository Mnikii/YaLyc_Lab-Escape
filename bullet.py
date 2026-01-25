import arcade
import math


class Bullet(arcade.Sprite):
    def __init__(self, start_x, start_y, target_x, target_y, speed=800, damage=10):
        super().__init__()
        self.texture = arcade.load_texture(":resources:/images/space_shooter/laserBlue01.png")
        self.scale = 0.5
        self.start = (start_x, start_y)
        self.center_x = start_x
        self.center_y = start_y
        self.speed = speed
        self.damage = damage
        self.distance = 500

        # Направление
        x_diff = target_x - start_x
        y_diff = target_y - start_y
        angle = math.atan2(y_diff, x_diff)

        self.change_x = math.cos(angle) * speed
        self.change_y = math.sin(angle) * speed
