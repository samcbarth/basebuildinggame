from __future__ import annotations

import pygame

from ai.enemies import Enemy
from combat.projectiles import Projectile


def nearest_enemy(origin: pygame.Vector2, enemies: list[Enemy], max_range: float) -> Enemy | None:
    best: Enemy | None = None
    best_distance = max_range
    for enemy in enemies:
        if not enemy.alive:
            continue
        distance = origin.distance_to(enemy.pos)
        if distance <= best_distance:
            best = enemy
            best_distance = distance
    return best


def fire_projectile(origin: pygame.Vector2, target: Enemy, damage: float, speed: float = 150.0) -> Projectile:
    direction = target.pos - origin
    if direction.length_squared() == 0:
        direction = pygame.Vector2(1, 0)
    else:
        direction = direction.normalize()
    return Projectile(pos=pygame.Vector2(origin), velocity=direction * speed, damage=damage)
