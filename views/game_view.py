# Основной игровой экран
import arcade
import math
import subprocess
import sys
import os
import time
from typing import List
from enum import Enum
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from player import Player as PlayerSprite
from camera import CAMERA_LERP
from level import get_level_config
from enemy import Enemy
from bullet import Bullet


class GameState(Enum):
    PLAYING = 1
    PAUSED = 2
    GAME_OVER_WIN = 3
    GAME_OVER_LOSE = 4


class TileType(Enum):
    EMPTY = 0
    SOLID = 1
    PLATFORM = 2
    SPIKE = 3
    EXIT = 4


# Константы
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
SCREEN_TITLE = "Побег из лаборатории"

# Физика
GRAVITY = 1.7
MAX_FALL_SPEED = 40
JUMP_POWER = 24

TILE_SIZE = 35
HUD_HEIGHT = 60


class GamePlayer:
    def __init__(self, x: float, y: float):
        self.sprite = PlayerSprite()
        self.sprite.center_x = x
        self.sprite.center_y = y

        self.sprite_list = arcade.SpriteList()
        self.sprite_list.append(self.sprite)

        self.score = 0
        self.is_on_ground = False
        self.hit_spike = False

    @property
    def x(self):
        return self.sprite.center_x - self.sprite.width // 2

    @property
    def y(self):
        return self.sprite.center_y - self.sprite.height // 2

    @property
    def width(self):
        return self.sprite.width

    @property
    def height(self):
        return self.sprite.height

    # @property — геттер атрибута moving_left
    @property
    def moving_left(self):
        return self.sprite.move_left

    # @<имя>.setter — сеттер атрибута moving_left
    @moving_left.setter
    def moving_left(self, value):
        self.sprite.move_left = value

    @property
    def moving_right(self):
        return self.sprite.move_right

    @moving_right.setter
    def moving_right(self, value):
        self.sprite.move_right = value

    def update(self, delta_time, level_tiles: List[List[int]]):
        self.sprite.change_y -= GRAVITY
        self.sprite.change_y = max(self.sprite.change_y, -MAX_FALL_SPEED)

        self.sprite.update(delta_time)

        self.sprite.center_x += self.sprite.change_x
        self.sprite.center_y += self.sprite.change_y

        self.is_on_ground = False
        self.hit_spike = False
        self._check_collisions(level_tiles)

    def _check_collisions(self, level_tiles: List[List[int]]):
        if not level_tiles:
            return

        grid_height = len(level_tiles)
        grid_width = len(level_tiles[0]) if grid_height > 0 else 0

        for row in range(grid_height):
            for col in range(grid_width):
                tile_type = level_tiles[row][col]
                tile_x = col * TILE_SIZE
                tile_y = (grid_height - 1 - row) * TILE_SIZE

                # AABB проверка пересечения
                if (self.x < tile_x + TILE_SIZE and
                        self.x + self.width > tile_x and
                        self.y < tile_y + TILE_SIZE and
                        self.y + self.height > tile_y):

                    if tile_type == TileType.SPIKE.value:
                        self.hit_spike = True
                        return

                    if tile_type in [TileType.SOLID.value, TileType.PLATFORM.value]:
                        overlap_left = (self.x + self.width) - tile_x
                        overlap_right = (tile_x + TILE_SIZE) - self.x
                        overlap_top = (self.y + self.height) - tile_y
                        overlap_bottom = (tile_y + TILE_SIZE) - self.y

                        min_overlap = min(overlap_left, overlap_right, overlap_top, overlap_bottom)

                        if min_overlap == overlap_bottom:
                            self.sprite.center_y = tile_y + TILE_SIZE + self.height // 2
                            self.sprite.change_y = 0
                            self.is_on_ground = True
                        elif min_overlap == overlap_top:
                            self.sprite.center_y = tile_y - self.height // 2
                            self.sprite.change_y = 0
                        elif min_overlap == overlap_left:
                            self.sprite.center_x = tile_x - self.width // 2
                        else:
                            self.sprite.center_x = tile_x + TILE_SIZE + self.width // 2

    def jump(self):
        if self.is_on_ground:
            self.sprite.change_y = JUMP_POWER
            self.is_on_ground = False

    def draw(self):
        self.sprite_list.draw()


class GameView(arcade.View):
    def __init__(self, level: int = 1):
        super().__init__()

        self.game_state = GameState.PLAYING
        self.current_level = level
        self.start_time = datetime.now()

        self.player = None
        self.enemies = arcade.SpriteList()
        self.wall_list = arcade.SpriteList()
        self.bullet_list = arcade.SpriteList()
        self.player_damage_cooldown = 0.0
        self.player_damage_delay = 0.6

        self.world_camera = arcade.camera.Camera2D()
        self.gui_camera = arcade.camera.Camera2D()

        self.level_tiles: List[List[int]] = []
        self.level_name = ""

        self._load_level(level)

    def _load_level(self, level: int):
        config = get_level_config(level)

        self.level_tiles = config['tiles']
        self.level_name = config['name']

        player_x, player_y = config['player_pos']
        self.player = GamePlayer(player_x, player_y)

        self.wall_list = self._build_wall_list()
        self._spawn_enemies(config.get('enemy_count', 0))

    def _build_wall_list(self):
        wall_list = arcade.SpriteList()
        grid_height = len(self.level_tiles)

        for row in range(grid_height):
            for col in range(len(self.level_tiles[row])):
                tile_type = self.level_tiles[row][col]
                if tile_type in (TileType.SOLID.value, TileType.PLATFORM.value):
                    wall = arcade.SpriteSolidColor(TILE_SIZE, TILE_SIZE, arcade.color.TRANSPARENT_BLACK)
                    wall.center_x = col * TILE_SIZE + TILE_SIZE / 2
                    wall.center_y = (grid_height - 1 - row) * TILE_SIZE + TILE_SIZE / 2
                    wall_list.append(wall)

        return wall_list

    def _spawn_enemies(self, count: int):
        self.enemies = arcade.SpriteList()
        if count <= 0:
            return

        config = get_level_config(self.current_level)
        spawn_points = config.get('enemy_spawns', [])

        if spawn_points:
            for spawn_point in spawn_points[:count]:
                enemy = Enemy(self.player.sprite, self.wall_list, spawn_point=spawn_point)
                self.enemies.append(enemy)
            return

        for _ in range(count):
            enemy = Enemy(self.player.sprite, self.wall_list)
            self.enemies.append(enemy)

    def on_draw(self):
        self.clear()

        self.world_camera.use()
        self._draw_level()
        self.bullet_list.draw()
        if self.enemies:
            self.enemies.draw()
        if self.player:
            self.player.draw()

        self.gui_camera.use()
        self._draw_hud()

    def _draw_level(self):
        grid_height = len(self.level_tiles)

        for row in range(grid_height):
            for col in range(len(self.level_tiles[row])):
                tile_type = self.level_tiles[row][col]
                x = col * TILE_SIZE
                y = (grid_height - 1 - row) * TILE_SIZE

                if tile_type == TileType.SOLID.value:
                    arcade.draw_lbwh_rectangle_filled(x, y, TILE_SIZE, TILE_SIZE, (40, 40, 45))
                    arcade.draw_lbwh_rectangle_outline(x, y, TILE_SIZE, TILE_SIZE, (60, 60, 70), 2)
                elif tile_type == TileType.PLATFORM.value:
                    arcade.draw_lbwh_rectangle_filled(x, y + TILE_SIZE // 4, TILE_SIZE, TILE_SIZE // 2, (100, 110, 120))
                    arcade.draw_lbwh_rectangle_filled(x, y + TILE_SIZE - 4, TILE_SIZE, 4, (150, 160, 180))
                elif tile_type == TileType.SPIKE.value:
                    arcade.draw_triangle_filled(x, y, x + TILE_SIZE // 2, y + TILE_SIZE, x + TILE_SIZE, y, (200, 50, 50))
                elif tile_type == TileType.EXIT.value:
                    glow = 150 + int(100 * math.sin(time.time() * 3))
                    arcade.draw_lbwh_rectangle_filled(x, y, TILE_SIZE, TILE_SIZE, (0, 255, 100, glow))
                    arcade.draw_lbwh_rectangle_outline(x, y, TILE_SIZE, TILE_SIZE, arcade.color.WHITE, 2)

    def _draw_hud(self):
        arcade.draw_lbwh_rectangle_filled(0, SCREEN_HEIGHT - HUD_HEIGHT, SCREEN_WIDTH, HUD_HEIGHT, arcade.color.BLACK)

        arcade.draw_text(self.level_name, 100, SCREEN_HEIGHT - 40, arcade.color.YELLOW, 16, bold=True)
        arcade.draw_text(f"Очки: {self.player.score}", 450, SCREEN_HEIGHT - 40, arcade.color.WHITE, 14)
        arcade.draw_text(f"HP: {self.player.sprite.health}", 600, SCREEN_HEIGHT - 40, arcade.color.WHITE, 14)
        arcade.draw_text(f"Уровень: {self.current_level}/3", 780, SCREEN_HEIGHT - 40, arcade.color.WHITE, 14)

        elapsed = (datetime.now() - self.start_time).total_seconds()
        arcade.draw_text(f"Время: {int(elapsed // 60):02d}:{int(elapsed % 60):02d}", 1000, SCREEN_HEIGHT - 40, arcade.color.WHITE, 14)

    def on_update(self, delta_time: float):
        if self.game_state != GameState.PLAYING:
            return

        self.player.update(delta_time, self.level_tiles)

        for enemy in self.enemies:
            enemy.update(delta_time)

        self.bullet_list.update()

        # Попадание пуль по врагам
        for bullet in self.bullet_list:
            hit_enemies = arcade.check_for_collision_with_list(bullet, self.enemies)
            for enemy in hit_enemies:
                enemy.take_damage(bullet.damage)
                bullet.kill()
                self.player.score += 50
                break

        # Урон от врагов
        if self.player_damage_cooldown > 0:
            self.player_damage_cooldown -= delta_time
        if self.player_damage_cooldown <= 0:
            hits = arcade.check_for_collision_with_list(self.player.sprite, self.enemies)
            if hits:
                damage = max((getattr(e, "damage", 10) for e in hits), default=10)
                self.player.sprite.take_damage(damage)
                self.player_damage_cooldown = self.player_damage_delay

        # Проверки смерти/шипов/падения
        if self.player.sprite.health <= 0 or self.player.hit_spike or self.player.y < -100:
            self._restart_level()
            return

        # Проверка выхода
        if self._player_hits_exit_tile():
            self._on_level_complete()

        self._update_camera()

    def _restart_level(self):
        config = get_level_config(self.current_level)
        player_x, player_y = config['player_pos']
        self.player.sprite.center_x = player_x
        self.player.sprite.center_y = player_y
        self.player.sprite.change_x = 0
        self.player.sprite.change_y = 0
        self.player.sprite.health = 100
        self.player_damage_cooldown = 0.0
        self.player.hit_spike = False
        self.player.is_on_ground = False

        self.wall_list = self._build_wall_list()
        self._spawn_enemies(get_level_config(self.current_level).get('enemy_count', 0))

    def _update_camera(self):
        target_x = self.player.sprite.center_x
        target_y = self.player.sprite.center_y

        current_x, current_y = self.world_camera.position
        new_x = current_x + (target_x - current_x) * CAMERA_LERP
        new_y = current_y + (target_y - current_y) * CAMERA_LERP

        grid_width = len(self.level_tiles[0]) if self.level_tiles else 0
        grid_height = len(self.level_tiles) if self.level_tiles else 0
        level_width_px = grid_width * TILE_SIZE
        level_height_px = grid_height * TILE_SIZE

        half_w = SCREEN_WIDTH / 2
        half_h = SCREEN_HEIGHT / 2

        if level_width_px > SCREEN_WIDTH:
            new_x = max(half_w, min(new_x, level_width_px - half_w))
        else:
            new_x = half_w

        if level_height_px > SCREEN_HEIGHT:
            new_y = max(half_h, min(new_y, level_height_px - half_h))
        else:
            new_y = half_h

        self.world_camera.position = (new_x, new_y)

    def _on_level_complete(self):
        self.player.score += 1000

        if self.current_level < 3:
            self.window.show_view(GameView(self.current_level + 1))
        else:
            self.game_state = GameState.GAME_OVER_WIN

            elapsed = (datetime.now() - self.start_time).total_seconds()
            timer_str = f"{int(elapsed // 60):02d}:{int(elapsed % 60):02d}"

            main_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "main.py")
            arcade.close_window()
            subprocess.Popen([
                sys.executable, main_path, "game_over", "True",
                str(self.player.score), timer_str, f"Пройдено уровней: {self.current_level}/3"
            ])

    def on_key_press(self, key: int, modifiers: int):
        if key in (arcade.key.D, arcade.key.RIGHT):
            self.player.moving_right = True
        elif key in (arcade.key.A, arcade.key.LEFT):
            self.player.moving_left = True
        elif key in (arcade.key.W, arcade.key.UP, arcade.key.SPACE):
            self.player.jump()
        elif key == arcade.key.ESCAPE:
            from views.menu_view import MenuView
            self.window.show_view(MenuView())

    def on_key_release(self, key: int, modifiers: int):
        if key in (arcade.key.D, arcade.key.RIGHT):
            self.player.moving_right = False
        elif key in (arcade.key.A, arcade.key.LEFT):
            self.player.moving_left = False

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        if button == arcade.MOUSE_BUTTON_LEFT:
            world_x, world_y = self.world_camera.position
            target_x = world_x - SCREEN_WIDTH / 2 + x
            target_y = world_y - SCREEN_HEIGHT / 2 + y

            bullet = Bullet(
                start_x=self.player.sprite.center_x,
                start_y=self.player.sprite.center_y,
                target_x=target_x,
                target_y=target_y
            )
            self.bullet_list.append(bullet)

    def _player_hits_exit_tile(self) -> bool:
        grid_height = len(self.level_tiles)
        if grid_height == 0:
            return False

        player_left = self.player.x
        player_right = self.player.x + self.player.width
        player_bottom = self.player.y
        player_top = self.player.y + self.player.height

        for row in range(grid_height):
            for col in range(len(self.level_tiles[row])):
                if self.level_tiles[row][col] != TileType.EXIT.value:
                    continue
                tile_x = col * TILE_SIZE
                tile_y = (grid_height - 1 - row) * TILE_SIZE
                if (player_left < tile_x + TILE_SIZE and
                        player_right > tile_x and
                        player_bottom < tile_y + TILE_SIZE and
                        player_top > tile_y):
                    return True

        return False
