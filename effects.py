# Визуальные эффекты и частицы
import random
import arcade
from arcade.particles import FadeParticle, Emitter, EmitBurst


class Effects:
    def __init__(self):
        self.confetti_tex = [
            arcade.make_soft_circle_texture(8, arcade.color.PASTEL_YELLOW),
            arcade.make_soft_circle_texture(8, arcade.color.PEACH),
            arcade.make_soft_circle_texture(8, arcade.color.BABY_BLUE),
            arcade.make_soft_circle_texture(8, arcade.color.ELECTRIC_CRIMSON),
        ]

        self.explosion_tex = [
            arcade.make_soft_circle_texture(30, arcade.color.YELLOW),
            arcade.make_soft_circle_texture(30, arcade.color.ORANGE),
            arcade.make_soft_circle_texture(30, arcade.color.RED),
            arcade.make_soft_circle_texture(30, arcade.color.DARK_RED)
        ]

    def make_confetti(self, x, y, count=80):
        return Emitter(
            center_xy=(x, y),
            emit_controller=EmitBurst(count),
            particle_factory=lambda e: FadeParticle(
                filename_or_texture=random.choice(self.confetti_tex),
                change_xy=arcade.math.rand_in_circle((0.0, 0.0), 9.0),
                lifetime=random.uniform(0.5, 1.1),
                start_alpha=255,
            )
        )

    def make_explosion(self, x, y, count=20):
        return Emitter(
            center_xy=(x, y),
            emit_controller=EmitBurst(count),
            particle_factory=lambda e: FadeParticle(
                filename_or_texture=random.choice(self.explosion_tex),
                change_xy=arcade.math.rand_in_circle((0.0, 0.0), 6.0),
                lifetime=random.uniform(0.3, 0.6),
                start_alpha=255,
            )
        )

