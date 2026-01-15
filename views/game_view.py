# Основной игровой экран
import arcade
import math
import subprocess
import sys
from typing import List, Tuple
from enum import Enum
from datetime import datetime

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
    MOVING_PLATFORM = 5


# Константы
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
SCREEN_TITLE = "Побег из лаборатории"

# Физика
GRAVITY = 0.5
MAX_FALL_SPEED = 20
JUMP_POWER = 15
MOVE_SPEED = 5

PLAYER_WIDTH = 32
PLAYER_HEIGHT = 48
TILE_SIZE = 32

HUD_HEIGHT = 60
GAME_AREA_HEIGHT = SCREEN_HEIGHT - HUD_HEIGHT


class Player:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT

        self.velocity_x = 0
        self.velocity_y = 0
        self.is_jumping = False
        self.is_on_ground = False

        self.score = 0

        self.moving_left = False
        self.moving_right = False

    def update(self, level_tiles: List[List[int]], moving_platforms: List['MovingPlatform']):
        self.velocity_y -= GRAVITY
        self.velocity_y = max(self.velocity_y, -MAX_FALL_SPEED)

        self.velocity_x = 0
        if self.moving_left:
            self.velocity_x = -MOVE_SPEED
        if self.moving_right:
            self.velocity_x = MOVE_SPEED

        self.x += self.velocity_x
        self.y += self.velocity_y

        self.is_on_ground = False
        self._check_collisions(level_tiles)
        self._check_moving_platform_collisions(moving_platforms)


    def _check_collisions(self, level_tiles: List[List[int]]):
        if not level_tiles:
            return

        grid_height = len(level_tiles)
        grid_width = len(level_tiles[0]) if grid_height > 0 else 0

        for row in range(grid_height):
            for col in range(grid_width):
                if level_tiles[row][col] in [TileType.SOLID.value, TileType.PLATFORM.value]:
                    tile_x = col * TILE_SIZE
                    tile_y = row * TILE_SIZE

                    if self._check_rect_collision(tile_x, tile_y, TILE_SIZE, TILE_SIZE):
                        # Разрешение столкновения
                        self._resolve_collision(tile_x, tile_y, TILE_SIZE, TILE_SIZE)

    def _check_moving_platform_collisions(self, moving_platforms: List):
        for platform in moving_platforms:
            if self._check_rect_collision(platform.x, platform.y, platform.width, platform.height):
                if self.velocity_y < 0 and self.y + self.height - platform.y > 0:
                    self.y = platform.y + platform.height
                    self.velocity_y = 0
                    self.is_on_ground = True

    def _check_rect_collision(self, rect_x: float, rect_y: float,
                             rect_width: float, rect_height: float) -> bool:
        return (self.x < rect_x + rect_width and
                self.x + self.width > rect_x and
                self.y < rect_y + rect_height and
                self.y + self.height > rect_y)

    def _resolve_collision(self, tile_x: float, tile_y: float,
                          tile_width: float, tile_height: float):
        overlap_left = (self.x + self.width) - tile_x
        overlap_right = (tile_x + tile_width) - self.x
        overlap_top = (self.y + self.height) - tile_y
        overlap_bottom = (tile_y + tile_height) - self.y

        min_overlap = min(overlap_left, overlap_right, overlap_top, overlap_bottom)

        if min_overlap == overlap_bottom:
            self.y = tile_y + tile_height
            self.velocity_y = 0
            self.is_on_ground = True
        elif min_overlap == overlap_top:
            self.y = tile_y - self.height
            self.velocity_y = 0
        elif min_overlap == overlap_left:
            self.x = tile_x - self.width
            self.velocity_x = 0
        else:
            self.x = tile_x + tile_width
            self.velocity_x = 0

    def jump(self):
        if self.is_on_ground:
            self.velocity_y = JUMP_POWER
            self.is_jumping = True
            self.is_on_ground = False

    def draw(self):
        # Игрока
        arcade.draw_lbwh_rectangle_filled(
            int(self.x),
            int(self.y),
            int(self.width),
            int(self.height),
            arcade.color.BLUE
        )

        eye_offset = 4 if not self.moving_left else -4
        arcade.draw_circle_filled(
            int(self.x + self.width // 2 + eye_offset),
            int(self.y + self.height - 10),
            3,
            arcade.color.WHITE
        )


class Particle:
    def __init__(self, x: float, y: float, velocity_x: float, velocity_y: float,
                 color: Tuple, lifetime: int = 30):
        self.x = x
        self.y = y
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
        self.color = color
        self.lifetime = lifetime
        self.max_lifetime = lifetime

    def update(self):
        self.x += self.velocity_x
        self.y += self.velocity_y
        self.velocity_y -= GRAVITY
        self.lifetime -= 1

    def draw(self):
        size = 4.0 * (self.lifetime / self.max_lifetime)
        arcade.draw_circle_filled(
            int(self.x), int(self.y), max(1, int(size)), arcade.color.WHITE)

    def is_alive(self) -> bool:
        return self.lifetime > 0


class GameView(arcade.View):
    def __init__(self, level: int = 1):
        super().__init__()

        self.bg_color = (32, 60, 80)

        self.game_state = GameState.PLAYING
        self.current_level = level
        self.start_time = datetime.now()

        self.player = None
        self.particles: List[Particle] = []

        self.level_tiles: List[List[int]] = []
        self.exit_rect = None

        # Камера
        self.camera_x = 0
        self.camera_y = 0
        self.camera_width = SCREEN_WIDTH
        self.camera_height = GAME_AREA_HEIGHT

        self._load_level(level)

    def _load_level(self, level: int):
        self.level_tiles = []

        if level == 1:
            self._create_laboratory_level()
        elif level == 2:
            self._create_dungeon_level()
        elif level == 3:
            self._create_exit_level()

    def _create_laboratory_level(self):
        # Первый уровень (лаборатория)
        # 0 - пусто, 1 - стена, 2 - платформа, 3 - ловушка, 4 - выход

        self.level_tiles = [
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 3, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 2, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 0, 0, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        ]

        # Начальная позиция игрока
        self.player = Player(100, 200)


        self.exit_rect = (1180, 100, 80, 80)

    def _create_dungeon_level(self):
        # 2 уровень (подземелье. потом апдейт графики)
        self.level_tiles = [
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 3, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 3, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        ]

        self.player = Player(100, 200)


        self.exit_rect = (1180, 100, 80, 80)

    def _create_exit_level(self):
        # Последний уровень
        self.level_tiles = [
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 3, 3, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 2, 2, 2, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 2, 2, 0, 0, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        ]

        self.player = Player(100, 200)


        self.exit_rect = (1180, 100, 80, 80)

    def on_draw(self):
        self.clear()

        self._draw_level()

        for particle in self.particles:
            particle.draw()

        if self.player:
            self.player.draw()

        # Отрисовка выхода
        if self.exit_rect:
            arcade.draw_lbwh_rectangle_filled(
                int(self.exit_rect[0]),
                int(self.exit_rect[1]),
                int(self.exit_rect[2]),
                int(self.exit_rect[3]),
                arcade.color.GOLD
            )
            arcade.draw_lbwh_rectangle_outline(
                int(self.exit_rect[0]),
                int(self.exit_rect[1]),
                int(self.exit_rect[2]),
                int(self.exit_rect[3]),
                arcade.color.YELLOW,
                3
            )

        self._draw_hud()

    def _draw_level(self):
        for row in range(len(self.level_tiles)):
            for col in range(len(self.level_tiles[row])):
                tile_type = self.level_tiles[row][col]
                x = col * TILE_SIZE
                y = row * TILE_SIZE

                if tile_type == TileType.SOLID.value:
                    arcade.draw_lbwh_rectangle_filled(
                        x, y,
                        TILE_SIZE, TILE_SIZE,
                        arcade.color.DARK_SLATE_GRAY
                    )
                elif tile_type == TileType.PLATFORM.value:
                    arcade.draw_lbwh_rectangle_filled(
                        x, y,
                        TILE_SIZE, TILE_SIZE,
                        arcade.color.SLATE_GRAY
                    )
                    arcade.draw_lbwh_rectangle_outline(
                        x, y,
                        TILE_SIZE, TILE_SIZE,
                        arcade.color.LIGHT_GRAY,
                        1
                    )

    def _draw_hud(self):
        arcade.draw_lbwh_rectangle_filled(
            0, SCREEN_HEIGHT - HUD_HEIGHT,
            SCREEN_WIDTH, HUD_HEIGHT,
            arcade.color.BLACK
        )

        # Очки
        arcade.draw_text(f"Очки: {self.player.score}", 400, SCREEN_HEIGHT - 40,
                        arcade.color.WHITE, 14)

        # Уровень
        arcade.draw_text(f"Уровень: {self.current_level}/3", 700, SCREEN_HEIGHT - 40,
                        arcade.color.WHITE, 14)

        # Время
        elapsed_time = (datetime.now() - self.start_time).total_seconds()
        minutes = int(elapsed_time // 60)
        seconds = int(elapsed_time % 60)
        arcade.draw_text(f"Время: {minutes:02d}:{seconds:02d}", 1000, SCREEN_HEIGHT - 40,
                        arcade.color.WHITE, 14)

    def on_update(self, delta_time: float):
        if self.game_state != GameState.PLAYING:
            return

        self.player.update(self.level_tiles, [])

        self.particles = [p for p in self.particles if p.is_alive()]
        for particle in self.particles:
            particle.update()

        if self.exit_rect:
            if (self.player.x < self.exit_rect[0] + self.exit_rect[2] and
                self.player.x + self.player.width > self.exit_rect[0] and
                self.player.y < self.exit_rect[1] + self.exit_rect[3] and
                self.player.y + self.player.height > self.exit_rect[1]):
                self._on_level_complete()

        self._update_camera()

    def _create_particles(self, x: float, y: float, color: Tuple, count: int = 10):
        for i in range(count):
            angle = (360 / count) * i
            speed = 3
            vx = math.cos(math.radians(angle)) * speed
            vy = math.sin(math.radians(angle)) * speed
            self.particles.append(Particle(x, y, vx, vy, color, 30))

    def _update_camera(self):
        # камера
        target_x = self.player.x + self.player.width // 2 - self.camera_width // 2
        target_y = self.player.y + self.player.height // 2 - self.camera_height // 2

        self.camera_x += (target_x - self.camera_x) * 0.1

        level_width = len(self.level_tiles[0]) * TILE_SIZE if self.level_tiles else 0
        level_height = len(self.level_tiles) * TILE_SIZE

        self.camera_x = max(0, min(self.camera_x, level_width - self.camera_width))
        self.camera_y = max(0, min(self.camera_y, level_height - self.camera_height))

    def _on_level_complete(self):
        self.player.score += 1000

        if self.current_level < 3:
            view = GameView(self.current_level + 1)
            self.window.show_view(view)
        else:
            self.game_state = GameState.GAME_OVER_WIN

            elapsed_time = (datetime.now() - self.start_time).total_seconds()
            minutes = int(elapsed_time // 60)
            seconds = int(elapsed_time % 60)
            timer_str = f"{minutes:02d}:{seconds:02d}"

            import os
            main_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "main.py")

            arcade.close_window()

            subprocess.Popen([
                sys.executable,
                main_path,
                "game_over",
                "True",  # result
                str(self.player.score),  # score
                timer_str,  # timer
                f"Пройдено уровней: {self.current_level}/3"  # statistic
            ])


    def on_key_press(self, key: int, modifiers: int):
        if key == arcade.key.D or key == arcade.key.RIGHT:
            self.player.moving_right = True
        elif key == arcade.key.A or key == arcade.key.LEFT:
            self.player.moving_left = True
        elif key == arcade.key.W or key == arcade.key.UP or key == arcade.key.SPACE:
            self.player.jump()
        elif key == arcade.key.ESCAPE:
            arcade.close_window()


    def on_key_release(self, key: int, modifiers: int):
        if key == arcade.key.D or key == arcade.key.RIGHT:
            self.player.moving_right = False
        elif key == arcade.key.A or key == arcade.key.LEFT:
            self.player.moving_left = False

