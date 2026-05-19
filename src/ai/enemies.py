from __future__ import annotations

from dataclasses import dataclass
from random import choice, randint

import pygame

from engine.settings import COLORS, INTERNAL_HEIGHT, INTERNAL_WIDTH


@dataclass
class Enemy:
    pos: pygame.Vector2
    hp: float
    speed: float
    damage: float
    attack_cooldown: float = 0.0

    @property
    def alive(self) -> bool:
        return self.hp > 0

    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, COLORS["enemy"], (int(self.pos.x - 4), int(self.pos.y - 4), 8, 8))
        pygame.draw.rect(surface, (89, 28, 28), (int(self.pos.x - 2), int(self.pos.y - 6), 4, 3))


def spawn_enemy(wave: int) -> Enemy:
    side = choice(["top", "bottom", "left", "right"])
    if side == "top":
        pos = pygame.Vector2(randint(0, INTERNAL_WIDTH), -8)
    elif side == "bottom":
        pos = pygame.Vector2(randint(0, INTERNAL_WIDTH), INTERNAL_HEIGHT + 8)
    elif side == "left":
        pos = pygame.Vector2(-8, randint(0, INTERNAL_HEIGHT))
    else:
        pos = pygame.Vector2(INTERNAL_WIDTH + 8, randint(0, INTERNAL_HEIGHT))

    return Enemy(
        pos=pos,
        hp=32 + wave * 7,
        speed=14 + min(18, wave * 1.2),
        damage=7 + wave * 0.8,
    )
