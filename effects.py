# Визуальные эффекты и частицы
import random

import arcade
from arcade.particles import FadeParticle, Emitter, EmitBurst, EmitMaintainCount, EmitInterval


class Effects:
    def __init__(self):
        self.confetti_tex = [
            arcade.make_soft_circle_texture(8, arcade.color.PASTEL_YELLOW),
            arcade.make_soft_circle_texture(8, arcade.color.PEACH),
            arcade.make_soft_circle_texture(8, arcade.color.BABY_BLUE),
            arcade.make_soft_circle_texture(8, arcade.color.ELECTRIC_CRIMSON),
        ]

        self.smoke_tex = [
            arcade.make_soft_circle_texture(8, arcade.color.DARK_GRAY),
            arcade.make_soft_circle_texture(8, arcade.color.GRAY),
            arcade.make_soft_circle_texture(8, arcade.color.LIGHT_GRAY),
            arcade.make_soft_circle_texture(8, arcade.color.WHITE)
        ]

        self.explosion_tex = [
            arcade.make_soft_circle_texture(30, arcade.color.YELLOW),
            arcade.make_soft_circle_texture(30, arcade.color.ORANGE),
            arcade.make_soft_circle_texture(30, arcade.color.RED),
            arcade.make_soft_circle_texture(30, arcade.color.DARK_RED)
        ]

        self.puff_tex = arcade.make_soft_circle_texture(12, arcade.color.WHITE, 255, 50)

    def smoke_mutator(self, p):
        p.scale_x *= 1.02
        p.scale_y *= 1.02
        p.alpha = max(0, p.alpha - 2)

    def gravity_drag(self, p):
        p.change_y += -0.03
        p.change_x *= 0.92
        p.change_y *= 0.92

    def make_confetti(self, x, y, count=80):
        return Emitter(
            center_xy=(x, y),
            emit_controller=EmitBurst(count),
            particle_factory=lambda e: FadeParticle(
                filename_or_texture=random.choice(self.confetti_tex),
                change_xy=arcade.math.rand_in_circle((0.0, 0.0), 9.0),
                lifetime=random.uniform(0.5, 1.1),
                start_alpha=255,
                end_alpha=0,
                scale=random.uniform(0.35, 0.6),
                mutation_callback=self.gravity_drag,
            ),
        )

    def make_explosion(self,x, y, count=20):
        return Emitter(
            center_xy=(x, y),
            emit_controller=EmitBurst(count),
            particle_factory=lambda e: FadeParticle(
                filename_or_texture=random.choice(self.explosion_tex),
                change_xy=arcade.math.rand_in_circle((0.0, 0.0), 9.0),
                lifetime=random.uniform(0.5, 1.1),
                start_alpha=255,
                end_alpha=0,
                scale=random.uniform(0.35, 0.6),
                mutation_callback=self.gravity_drag,
            ),
        )

    def make_trail(self, attached_sprite, maintain=60):
        texture = arcade.make_soft_circle_texture(8, arcade.color.DARK_GRAY)
        emit = Emitter(
            center_xy=(attached_sprite.center_x, attached_sprite.center_y),
            emit_controller=EmitMaintainCount(maintain),
            particle_factory=lambda e: FadeParticle(
                filename_or_texture=texture,
                change_xy=arcade.math.rand_in_circle((0.0, 0.0), 1.6),
                lifetime=random.uniform(0.35, 0.6),
                start_alpha=220,
                end_alpha=0,
                scale=random.uniform(0.25, 0.4),
            ),
        )
        emit._attached = attached_sprite
        return emit

    def make_smoke(self, x, y):
        return Emitter(
            center_xy=(x, y),
            emit_controller=EmitBurst(12),
            particle_factory=lambda e: FadeParticle(
                filename_or_texture=random.choice(self.smoke_tex),
                change_xy=arcade.math.rand_in_circle((0.0, 0.0), 0.6),
                lifetime=random.uniform(1.5, 2.5),
                start_alpha=200,
                end_alpha=0,
                scale=random.uniform(0.6, 0.9),
                mutation_callback=self.smoke_mutator,
            ),
        )

    def make_fountain(self, x, y):
        return Emitter(
            center_xy=(x, y),
            emit_controller=EmitInterval(0.02),
            particle_factory=lambda e: FadeParticle(
                filename_or_texture=self.puff_tex,
                change_xy=(random.uniform(-0.8, 0.8), random.uniform(4.0, 6.0)),
                lifetime=random.uniform(0.8, 1.6),
                start_alpha=240, end_alpha=0,
                scale=random.uniform(0.4, 0.8),
                mutation_callback=self.gravity_drag,
            ),
        )
