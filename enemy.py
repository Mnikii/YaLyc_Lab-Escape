# Логика врагов

import arcade
import random
import math
import time

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
MIN_DISTANCE_BETWEEN_ENEMIES = 30


class Enemy(arcade.Sprite):
    def __init__(self, player, wall_list):
        super().__init__()
        self.idle_texture = arcade.load_texture(":resources:images/animated_characters/zombie/zombie_idle.png")
        self.texture = self.idle_texture

        self.health = 100
        self.damage = 10
        self.speed = 2
        self.player = player
        self.score = 0
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
        self.stuck_max = 6  # сколько максимум враг не двигается
        self.stuck_check_interval = 1
        self.stuck_check_timer = 0
        self.is_stuck = False

        self.existing_enemy_positions = []

        self.spawn_enemy_without_overlap()

    def set_collision_lists(self, platform_list, wall_list=None):
        self.platform_list = platform_list
        self.wall_list = wall_list if wall_list else platform_list

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
        platform = random.choice(self.wall_list)
        spawn_x = platform.center_x
        spawn_y = platform.top + self.height / 2
        self.center_x = spawn_x
        self.center_y = spawn_y
        self.on_ground = True
        self.last_position_x = spawn_x
        self.last_position_y = spawn_y
        self.existing_enemy_positions.append((spawn_x, spawn_y))

    def check_if_stuck(self, delta_time):
        self.stuck_check_timer += delta_time

        if self.stuck_check_timer >= self.stuck_check_interval:
            self.stuck_check_timer = 0
            # Вычисляем, насколько далеко враг переместился
            distance_moved = math.sqrt(
                (self.center_x - self.last_position_x) ** 2 +
                (self.center_y - self.last_position_y) ** 2
            )

            if distance_moved < 10:  # Если враг переместился меньше чем на 10 пикселей
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

        if distance > 0 and distance < 400:
            if x_diff > 0:
                self.direction = 1
            else:
                self.direction = -1

        self.center_x += self.direction * self.speed

    walls_hit = arcade.check_for_collision_with_list(self, self.wall_list)
    if walls_hit:
        self.center_x = old_x
        self.center_y = old_y
        self.direction *= -1

    walls_x_collision = arcade.check_for_collision_with_list(self, self.wall_list)
    walls_y_collision = arcade.check_for_collision_with_list(self, self.wall_list)

    if walls_x_collision:
        self.center_x = old_x
        self.direction *= -1

    if walls_y_collision:
        self.center_y = old_y


def hit_player(self):
    if arcade.check_for_collision(self, self.player):
        if self.attack_cooldown_timer <= 0:
            self.player.take_damage(self.damage)
            self.attack_cooldown_timer = self.attack_cooldown_max
            return True
    return False


def take_damage(self, damage_amount):
    self.health -= damage_amount
    if self.health <= 0:
        # Удаляем позицию врага из списка при смерти
        for i, pos in enumerate(self.existing_enemy_positions):  # enumerate добавляет индексы
            # удаляет эту позицию из списка, чтобы новорожденный враг мог появиться на этом месте
            if abs(pos[0] - self.center_x) < 50 and abs(pos[1] - self.center_y) < 50:
                del self.existing_enemy_positions[i]
                break
        self.score += 100
        self.kill()
        return True
    return False


def update(self, delta_time):
    # Проверяем, не застрял ли враг
    self.check_if_stuck(delta_time)
    self.attack_cooldown_timer -= delta_time

    # Гравитация
    if not self.on_ground:
        self.change_y -= 0.5
        self.center_y += self.change_y
    else:
        self.change_y = 0

    # Проверяем землю
    self.check_ground_collision()

    # Обновляем движение и атаку
    self.follow_player(delta_time)
    self.hit_player()
