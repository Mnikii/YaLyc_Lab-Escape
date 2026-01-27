# Логика врагов
import arcade
import random
import math


class Enemy(arcade.Sprite):
    existing_enemy_positions = []

    def __init__(self, player, wall_list, spawn_point=None):
        super().__init__()
        self.idle_texture = arcade.load_texture(":resources:images/animated_characters/zombie/zombie_idle.png")
        self.texture = self.idle_texture

        self.health = 100
        self.damage = 10
        self.speed = 2
        self.player = player
        self.wall_list = wall_list

        self.attack_cooldown_max = 1.0
        self.attack_cooldown_timer = 0.0
        self.direction = random.choice([-1, 1])

        self.on_ground = False
        self.change_y = 0

        # Для отслеживания застревания
        self.last_position_x = 0
        self.last_position_y = 0
        self.stuck_timer = 0
        self.stuck_max = 6
        self.stuck_check_interval = 1
        self.stuck_check_timer = 0
        self.is_stuck = False

        if spawn_point is not None:
            self.center_x, self.center_y = spawn_point
            self.on_ground = True
            self.last_position_x = self.center_x
            self.last_position_y = self.center_y
            Enemy.existing_enemy_positions.append((self.center_x, self.center_y))
        elif wall_list and len(wall_list) > 0:
            self.spawn_enemy_without_overlap()

    def check_ground_collision(self):
        if not self.wall_list:
            self.on_ground = False
            return False

        feet_check = arcade.SpriteSolidColor(int(self.width), 10, arcade.color.TRANSPARENT_BLACK)
        feet_check.center_x = self.center_x
        feet_check.center_y = self.center_y - self.height / 2 - 2

        hit_list = arcade.check_for_collision_with_list(feet_check, self.wall_list)
        self.on_ground = len(hit_list) > 0
        return self.on_ground

    def spawn_enemy_without_overlap(self):
        if not self.wall_list or len(self.wall_list) == 0:
            return

        platform = random.choice(self.wall_list)
        spawn_x = platform.center_x
        spawn_y = platform.top + self.height / 2
        self.center_x = spawn_x
        self.center_y = spawn_y
        self.on_ground = True
        self.last_position_x = spawn_x
        self.last_position_y = spawn_y
        Enemy.existing_enemy_positions.append((spawn_x, spawn_y))

    def check_if_stuck(self, delta_time):
        self.stuck_check_timer += delta_time

        if self.stuck_check_timer >= self.stuck_check_interval:
            self.stuck_check_timer = 0
            distance_moved = math.sqrt(
                (self.center_x - self.last_position_x) ** 2 +
                (self.center_y - self.last_position_y) ** 2
            )

            if distance_moved < 10:
                self.stuck_timer += self.stuck_check_interval
            else:
                self.stuck_timer = 0
                self.is_stuck = False

            self.last_position_x = self.center_x
            self.last_position_y = self.center_y

            if self.stuck_timer >= self.stuck_max and not self.is_stuck:
                self.unstick_enemy()
                return True
        return False

    def unstick_enemy(self):
        move_direction = random.choice([-1, 1])
        self.center_x += move_direction * 67
        self.center_y += 25
        self.stuck_timer = 0
        self.is_stuck = True
        self.check_ground_collision()

    def follow_player(self, delta_time):
        self.check_ground_collision()
        if not self.on_ground:
            return

        x_diff = self.player.center_x - self.center_x
        y_diff = self.player.center_y - self.center_y
        distance = math.sqrt(x_diff ** 2 + y_diff ** 2)

        if 0 < distance < 400:
            self.direction = 1 if x_diff > 0 else -1

        old_x = self.center_x

        self.center_x += self.direction * self.speed

        if self.wall_list:
            walls_hit = arcade.check_for_collision_with_list(self, self.wall_list)
            if walls_hit:
                self.center_x = old_x
                self.direction *= -1

    def hit_player(self):
        if arcade.check_for_collision(self, self.player):
            if self.attack_cooldown_timer <= 0:
                if hasattr(self.player, 'take_damage'):
                    self.player.take_damage(self.damage)
                self.attack_cooldown_timer = self.attack_cooldown_max
                return True
        return False

    def take_damage(self, damage_amount):
        self.health -= damage_amount
        if self.health <= 0:
            for i, pos in enumerate(Enemy.existing_enemy_positions):
                if abs(pos[0] - self.center_x) < 50 and abs(pos[1] - self.center_y) < 50:
                    del Enemy.existing_enemy_positions[i]
                    break
            self.kill()
            return True
        return False

    def update(self, delta_time: float = 1/60):
        self.check_if_stuck(delta_time)
        self.attack_cooldown_timer -= delta_time

        if not self.on_ground:
            self.change_y -= 0.5
            self.center_y += self.change_y
        else:
            self.change_y = 0

        self.check_ground_collision()
        self.follow_player(delta_time)
        self.hit_player()

