from __future__ import annotations

from dataclasses import dataclass

import pygame

from engine.settings import COLORS


@dataclass
class Projectile:
    pos: pygame.Vector2
    velocity: pygame.Vector2
    damage: float
    ttl: float = 1.2

    @property
    def alive(self) -> bool:
        return self.ttl > 0

    def update(self, dt: float) -> None:
        self.pos += self.velocity * dt
        self.ttl -= dt

    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.circle(surface, COLORS["projectile"], (int(self.pos.x), int(self.pos.y)), 2)
