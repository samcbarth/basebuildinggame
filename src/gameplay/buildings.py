from __future__ import annotations

from dataclasses import dataclass

import pygame

from engine.settings import CELL_SIZE, COLORS, STARTING_CORE_HP


@dataclass(frozen=True)
class BuildingSpec:
    key: str
    name: str
    cost: int
    width: int
    height: int
    max_hp: int
    color_key: str
    description: str


BUILDING_SPECS: dict[str, BuildingSpec] = {
    "mine": BuildingSpec(
        key="mine",
        name="Mine",
        cost=40,
        width=2,
        height=2,
        max_hp=95,
        color_key="mine",
        description="Generates steady scrap.",
    ),
    "turret": BuildingSpec(
        key="turret",
        name="Turret",
        cost=55,
        width=1,
        height=1,
        max_hp=85,
        color_key="turret",
        description="Auto-fires at nearby enemies.",
    ),
    "barracks": BuildingSpec(
        key="barracks",
        name="Barracks",
        cost=85,
        width=3,
        height=2,
        max_hp=135,
        color_key="barracks",
        description="Unlocks soldier training.",
    ),
    "hq": BuildingSpec(
        key="hq",
        name="Core HQ",
        cost=0,
        width=3,
        height=3,
        max_hp=STARTING_CORE_HP,
        color_key="hq",
        description="Protect this. If it falls, the run ends.",
    ),
}


@dataclass
class Building:
    spec: BuildingSpec
    grid_x: int
    grid_y: int
    hp: float
    cooldown: float = 0.0

    @classmethod
    def create(cls, kind: str, grid_x: int, grid_y: int, armor_bonus: int = 0) -> "Building":
        spec = BUILDING_SPECS[kind]
        return cls(spec=spec, grid_x=grid_x, grid_y=grid_y, hp=spec.max_hp + armor_bonus)

    @property
    def max_hp(self) -> int:
        return self.spec.max_hp

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(
            self.grid_x * CELL_SIZE,
            self.grid_y * CELL_SIZE,
            self.spec.width * CELL_SIZE,
            self.spec.height * CELL_SIZE,
        )

    @property
    def center(self) -> pygame.Vector2:
        return pygame.Vector2(self.rect.center)

    @property
    def alive(self) -> bool:
        return self.hp > 0

    def draw(self, surface: pygame.Surface, armor_bonus: int = 0) -> None:
        rect = self.rect
        pygame.draw.rect(surface, COLORS[self.spec.color_key], rect)
        pygame.draw.rect(surface, (8, 10, 12), rect, 1)

        if self.spec.key == "turret":
            pygame.draw.circle(surface, (22, 31, 34), rect.center, 5)
            pygame.draw.line(surface, COLORS["projectile"], rect.center, (rect.centerx + 7, rect.centery), 2)
        elif self.spec.key == "mine":
            pygame.draw.rect(surface, (91, 72, 48), rect.inflate(-8, -8))
        elif self.spec.key == "barracks":
            pygame.draw.rect(surface, (55, 38, 69), rect.inflate(-10, -8))
        elif self.spec.key == "hq":
            pygame.draw.rect(surface, (35, 57, 90), rect.inflate(-8, -8))
            pygame.draw.rect(surface, COLORS["scrap"], rect.inflate(-24, -24))

        max_hp = self.spec.max_hp + armor_bonus
        hp_ratio = max(0.0, min(1.0, self.hp / max_hp))
        bar_width = rect.width
        bar_rect = pygame.Rect(rect.left, rect.top - 3, int(bar_width * hp_ratio), 2)
        pygame.draw.rect(surface, COLORS["bad"], (rect.left, rect.top - 3, bar_width, 2))
        pygame.draw.rect(surface, COLORS["good"], bar_rect)
