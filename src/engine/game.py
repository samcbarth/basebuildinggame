from __future__ import annotations

import math
import random
import sys

import pygame

from ai.enemies import Enemy, spawn_enemy
from combat.projectiles import Projectile
from combat.weapons import fire_projectile, nearest_enemy
from engine.settings import (
    CELL_SIZE,
    COLORS,
    FPS,
    GRID_HEIGHT,
    GRID_WIDTH,
    INTERNAL_HEIGHT,
    INTERNAL_WIDTH,
    SCALE,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    STARTING_SCRAP,
    WAVE_INTERVAL,
)
from gameplay.buildings import BUILDING_SPECS, Building
from gameplay.units import Soldier, WorkerRoster
from ui.hud import Hud


class Game:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("Base Building Game - Prototype")
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.canvas = pygame.Surface((INTERNAL_WIDTH, INTERNAL_HEIGHT))
        self.clock = pygame.time.Clock()
        self.hud = Hud()

        self.scrap = float(STARTING_SCRAP)
        self.wave = 0
        self.wave_timer = WAVE_INTERVAL
        self.spawn_queue = 0
        self.spawn_tick = 0.0
        self.game_over = False

        self.economy_level = 0
        self.weapon_level = 0
        self.armor_level = 0
        self.selected_building: str | None = "mine"
        self.message = "Build before the first raid."
        self.message_color = "muted"
        self.message_timer = 5.0

        self.buildings: list[Building] = [Building.create("hq", 13, 8)]
        self.workers = WorkerRoster()
        self.soldiers: list[Soldier] = [
            Soldier(pygame.Vector2(INTERNAL_WIDTH / 2 - 18, INTERNAL_HEIGHT / 2 + 38)),
        ]
        self.enemies: list[Enemy] = []
        self.projectiles: list[Projectile] = []

    def run(self) -> None:
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            self.handle_events()
            if not self.game_over:
                self.update(dt)
            self.draw()

    def handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                self.handle_key(event.key)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.try_place_selected()
                elif event.button == 3:
                    self.selected_building = None

    def handle_key(self, key: int) -> None:
        if key == pygame.K_ESCAPE:
            pygame.quit()
            sys.exit()
        if self.game_over and key == pygame.K_RETURN:
            self.__init__()
            return
        if key == pygame.K_1:
            self.selected_building = "mine"
        elif key == pygame.K_2:
            self.selected_building = "turret"
        elif key == pygame.K_3:
            self.selected_building = "barracks"
        elif key == pygame.K_w:
            self.train_worker()
        elif key == pygame.K_s:
            self.train_soldier()
        elif key == pygame.K_u:
            self.buy_upgrade("economy")
        elif key == pygame.K_i:
            self.buy_upgrade("weapons")
        elif key == pygame.K_o:
            self.buy_upgrade("armor")
        elif key == pygame.K_r:
            self.repair_building()
        elif key == pygame.K_SPACE:
            self.start_wave()

    def update(self, dt: float) -> None:
        self.message_timer -= dt
        if self.message_timer <= 0:
            self.message = ""

        mine_count = sum(1 for building in self.buildings if building.spec.key == "mine")
        self.scrap += self.workers.income_per_second(self.economy_level, mine_count) * dt

        self.wave_timer -= dt
        if self.wave_timer <= 0 and self.spawn_queue <= 0:
            self.start_wave()

        self.spawn_enemies(dt)
        self.update_building_weapons(dt)
        self.update_soldiers(dt)
        self.update_projectiles(dt)
        self.update_enemies(dt)

        self.enemies = [enemy for enemy in self.enemies if enemy.alive]
        self.projectiles = [projectile for projectile in self.projectiles if projectile.alive]
        self.soldiers = [soldier for soldier in self.soldiers if soldier.alive]
        self.buildings = [building for building in self.buildings if building.alive or building.spec.key == "hq"]

        hq = self.hq
        if hq is None or hq.hp <= 0:
            self.game_over = True
            self.flash("HQ destroyed. Press Enter to restart.", "bad", 999)

    def start_wave(self) -> None:
        if self.spawn_queue > 0:
            return
        self.wave += 1
        self.spawn_queue = 4 + self.wave * 2
        self.spawn_tick = 0.0
        self.wave_timer = WAVE_INTERVAL + min(12, self.wave * 1.5)
        self.flash(f"Wave {self.wave} incoming.", "warning")

    def spawn_enemies(self, dt: float) -> None:
        if self.spawn_queue <= 0:
            return
        self.spawn_tick -= dt
        if self.spawn_tick <= 0:
            self.enemies.append(spawn_enemy(self.wave))
            self.spawn_queue -= 1
            self.spawn_tick = max(0.25, 0.85 - self.wave * 0.03)

    def update_building_weapons(self, dt: float) -> None:
        damage = 16 + self.weapon_level * 6
        fire_range = 70 + self.weapon_level * 10
        for building in self.buildings:
            if building.spec.key != "turret":
                continue
            building.cooldown -= dt
            target = nearest_enemy(building.center, self.enemies, fire_range)
            if target and building.cooldown <= 0:
                self.projectiles.append(fire_projectile(building.center, target, damage))
                building.cooldown = max(0.18, 0.62 - self.weapon_level * 0.08)

    def update_soldiers(self, dt: float) -> None:
        damage = 8 + self.weapon_level * 3
        fire_range = 58 + self.weapon_level * 8
        hq_center = self.hq.center if self.hq else pygame.Vector2(INTERNAL_WIDTH / 2, INTERNAL_HEIGHT / 2)

        for index, soldier in enumerate(self.soldiers):
            soldier.cooldown -= dt
            target = nearest_enemy(soldier.pos, self.enemies, fire_range)
            if target:
                if soldier.cooldown <= 0:
                    self.projectiles.append(fire_projectile(soldier.pos, target, damage, 130.0))
                    soldier.cooldown = max(0.24, 0.72 - self.weapon_level * 0.08)
            else:
                guard_offset = pygame.Vector2(math.cos(index) * 28, math.sin(index * 1.7) * 22)
                destination = hq_center + guard_offset
                delta = destination - soldier.pos
                if delta.length_squared() > 4:
                    soldier.pos += delta.normalize() * 24 * dt

    def update_projectiles(self, dt: float) -> None:
        for projectile in self.projectiles:
            projectile.update(dt)
            for enemy in self.enemies:
                if enemy.alive and projectile.pos.distance_to(enemy.pos) <= 5:
                    enemy.hp -= projectile.damage
                    projectile.ttl = 0
                    if enemy.hp <= 0:
                        self.scrap += 7 + self.wave
                    break

    def update_enemies(self, dt: float) -> None:
        for enemy in self.enemies:
            target = self.closest_building(enemy.pos)
            if target is None:
                continue
            enemy.attack_cooldown -= dt
            target_point = target.center
            distance = enemy.pos.distance_to(target_point)
            if distance > 10:
                direction = (target_point - enemy.pos).normalize()
                enemy.pos += direction * enemy.speed * dt
            elif enemy.attack_cooldown <= 0:
                target.hp -= enemy.damage
                enemy.attack_cooldown = 0.75

    def train_worker(self) -> None:
        cost = 25 + self.workers.count * 4
        if self.spend(cost):
            self.workers.count += 1
            self.flash("Worker trained. Income increased.", "good")

    def train_soldier(self) -> None:
        if not any(building.spec.key == "barracks" for building in self.buildings):
            self.flash("Build a barracks first.", "bad")
            return
        cost = 35 + len(self.soldiers) * 3
        if self.spend(cost):
            spawn = self.hq.center if self.hq else pygame.Vector2(INTERNAL_WIDTH / 2, INTERNAL_HEIGHT / 2)
            jitter = pygame.Vector2(random.randint(-22, 22), random.randint(22, 44))
            self.soldiers.append(Soldier(spawn + jitter))
            self.flash("Soldier deployed.", "good")

    def buy_upgrade(self, kind: str) -> None:
        levels = {
            "economy": self.economy_level,
            "weapons": self.weapon_level,
            "armor": self.armor_level,
        }
        current = levels[kind]
        if current >= 3:
            self.flash(f"{kind.title()} already maxed.", "muted")
            return
        cost = {"economy": 80, "weapons": 95, "armor": 75}[kind] + current * 55
        if not self.spend(cost):
            return
        if kind == "economy":
            self.economy_level += 1
        elif kind == "weapons":
            self.weapon_level += 1
        else:
            self.armor_level += 1
            for building in self.buildings:
                building.hp += 25
        self.flash(f"{kind.title()} upgraded to level {current + 1}.", "good")

    def repair_building(self) -> None:
        damaged = [
            building
            for building in self.buildings
            if building.hp < building.spec.max_hp + self.armor_bonus
        ]
        if not damaged:
            self.flash("Nothing needs repair.", "muted")
            return
        target = min(damaged, key=lambda building: building.hp / (building.spec.max_hp + self.armor_bonus))
        if self.spend(22):
            target.hp = min(target.spec.max_hp + self.armor_bonus, target.hp + 45)
            self.flash(f"Repaired {target.spec.name}.", "good")

    def try_place_selected(self) -> None:
        if self.selected_building is None or self.game_over:
            return
        grid_x, grid_y = self.mouse_grid()
        spec = BUILDING_SPECS[self.selected_building]
        if not self.can_place(spec.key, grid_x, grid_y):
            self.flash("Can't build there.", "bad")
            return
        if not self.spend(spec.cost):
            return
        self.buildings.append(Building.create(spec.key, grid_x, grid_y, self.armor_bonus))
        self.flash(f"{spec.name} built.", "good")

    def can_place(self, kind: str, grid_x: int, grid_y: int) -> bool:
        spec = BUILDING_SPECS[kind]
        if grid_y < 3:
            return False
        if grid_x < 0 or grid_y < 0 or grid_x + spec.width > GRID_WIDTH or grid_y + spec.height > GRID_HEIGHT:
            return False
        new_rect = pygame.Rect(grid_x, grid_y, spec.width, spec.height)
        for building in self.buildings:
            existing = pygame.Rect(building.grid_x, building.grid_y, building.spec.width, building.spec.height)
            if new_rect.colliderect(existing):
                return False
        return True

    def spend(self, amount: int) -> bool:
        if self.scrap < amount:
            self.flash(f"Need {amount} scrap.", "bad")
            return False
        self.scrap -= amount
        return True

    def closest_building(self, pos: pygame.Vector2) -> Building | None:
        alive = [building for building in self.buildings if building.alive]
        if not alive:
            return None
        return min(alive, key=lambda building: pos.distance_squared_to(building.center))

    @property
    def hq(self) -> Building | None:
        return next((building for building in self.buildings if building.spec.key == "hq"), None)

    @property
    def armor_bonus(self) -> int:
        return self.armor_level * 25

    def mouse_grid(self) -> tuple[int, int]:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        internal_x = int(mouse_x / SCALE)
        internal_y = int(mouse_y / SCALE)
        return internal_x // CELL_SIZE, internal_y // CELL_SIZE

    def flash(self, text: str, color: str = "text", duration: float = 2.2) -> None:
        self.message = text
        self.message_color = color
        self.message_timer = duration

    def draw(self) -> None:
        self.canvas.fill(COLORS["bg"])
        self.draw_grid()

        for building in self.buildings:
            building.draw(self.canvas, self.armor_bonus)
        for soldier in self.soldiers:
            soldier.draw(self.canvas)
        for enemy in self.enemies:
            enemy.draw(self.canvas)
        for projectile in self.projectiles:
            projectile.draw(self.canvas)

        self.draw_build_preview()
        self.hud.draw(self.canvas, self.hud_state())
        if self.game_over:
            self.draw_game_over()

        scaled = pygame.transform.scale(self.canvas, (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.screen.blit(scaled, (0, 0))
        pygame.display.flip()

    def draw_grid(self) -> None:
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                color = COLORS["grid_alt"] if (x + y) % 2 == 0 else COLORS["bg"]
                pygame.draw.rect(self.canvas, color, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
        for x in range(0, INTERNAL_WIDTH, CELL_SIZE):
            pygame.draw.line(self.canvas, COLORS["grid"], (x, 0), (x, INTERNAL_HEIGHT))
        for y in range(0, INTERNAL_HEIGHT, CELL_SIZE):
            pygame.draw.line(self.canvas, COLORS["grid"], (0, y), (INTERNAL_WIDTH, y))

    def draw_build_preview(self) -> None:
        if self.selected_building is None or self.game_over:
            return
        grid_x, grid_y = self.mouse_grid()
        spec = BUILDING_SPECS[self.selected_building]
        rect = pygame.Rect(
            grid_x * CELL_SIZE,
            grid_y * CELL_SIZE,
            spec.width * CELL_SIZE,
            spec.height * CELL_SIZE,
        )
        color = COLORS["ghost_ok"] if self.can_place(spec.key, grid_x, grid_y) and self.scrap >= spec.cost else COLORS["ghost_bad"]
        ghost = pygame.Surface(rect.size, pygame.SRCALPHA)
        ghost.fill((*color, 95))
        self.canvas.blit(ghost, rect.topleft)
        pygame.draw.rect(self.canvas, color, rect, 1)

    def draw_game_over(self) -> None:
        overlay = pygame.Surface((INTERNAL_WIDTH, INTERNAL_HEIGHT), pygame.SRCALPHA)
        overlay.fill((5, 6, 8, 175))
        self.canvas.blit(overlay, (0, 0))
        font = pygame.font.Font(None, 28)
        small = pygame.font.Font(None, 13)
        title = font.render("OUTPOST LOST", False, COLORS["bad"])
        prompt = small.render("Press Enter to rebuild from the ashes.", False, COLORS["text"])
        self.canvas.blit(title, title.get_rect(center=(INTERNAL_WIDTH // 2, INTERNAL_HEIGHT // 2 - 8)))
        self.canvas.blit(prompt, prompt.get_rect(center=(INTERNAL_WIDTH // 2, INTERNAL_HEIGHT // 2 + 18)))

    def hud_state(self) -> dict[str, object]:
        hq_hp = self.hq.hp if self.hq else 0
        return {
            "scrap": self.scrap,
            "wave": self.wave,
            "workers": self.workers.count,
            "soldiers": len(self.soldiers),
            "wave_timer": max(0, self.wave_timer),
            "hq_hp": hq_hp,
            "selected": self.selected_building,
            "message": self.message,
            "message_color": self.message_color,
        }
