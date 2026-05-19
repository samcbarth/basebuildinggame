from __future__ import annotations

from dataclasses import dataclass

import pygame

from engine.settings import COLORS


@dataclass
class WorkerRoster:
    count: int = 2

    def income_per_second(self, economy_level: int, mine_count: int) -> float:
        worker_income = self.count * (0.8 + economy_level * 0.25)
        mine_income = mine_count * (1.5 + economy_level * 0.5)
        return worker_income + mine_income


@dataclass
class Soldier:
    pos: pygame.Vector2
    cooldown: float = 0.0
    hp: float = 45.0

    @property
    def alive(self) -> bool:
        return self.hp > 0

    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, COLORS["soldier"], (int(self.pos.x - 3), int(self.pos.y - 3), 6, 6))
        pygame.draw.rect(surface, (20, 34, 48), (int(self.pos.x - 1), int(self.pos.y - 5), 2, 3))
