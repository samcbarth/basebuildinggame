from __future__ import annotations

import pygame

from engine.settings import COLORS, INTERNAL_HEIGHT, INTERNAL_WIDTH


class Hud:
    def __init__(self) -> None:
        self.font = pygame.font.Font(None, 12)
        self.small_font = pygame.font.Font(None, 10)

    def draw_text(self, surface: pygame.Surface, text: str, pos: tuple[int, int], color: str = "text") -> None:
        rendered = self.font.render(text, False, COLORS[color])
        surface.blit(rendered, pos)

    def draw_small(self, surface: pygame.Surface, text: str, pos: tuple[int, int], color: str = "muted") -> None:
        rendered = self.small_font.render(text, False, COLORS[color])
        surface.blit(rendered, pos)

    def draw(self, surface: pygame.Surface, state: dict[str, object]) -> None:
        panel = pygame.Rect(0, 0, INTERNAL_WIDTH, 38)
        pygame.draw.rect(surface, COLORS["panel"], panel)
        pygame.draw.line(surface, COLORS["panel_edge"], (0, panel.bottom), (INTERNAL_WIDTH, panel.bottom))

        self.draw_text(surface, f"SCRAP {int(state['scrap'])}", (5, 5), "scrap")
        self.draw_text(surface, f"WAVE {state['wave']}", (72, 5), "warning")
        self.draw_text(surface, f"WORKERS {state['workers']}", (124, 5))
        self.draw_text(surface, f"SOLDIERS {state['soldiers']}", (190, 5))
        self.draw_text(surface, f"NEXT {int(state['wave_timer'])}s", (268, 5), "muted")
        self.draw_text(surface, f"BASE {int(state['hq_hp'])}", (330, 5), "good" if state["hq_hp"] > 80 else "bad")

        selected = state["selected"] or "none"
        self.draw_small(surface, f"Build: {selected} | 1 mine 2 turret 3 barracks | W worker S soldier | U/I/O upgrades | R repair | Space wave", (5, 22))

        if state["message"]:
            message_width = self.font.size(str(state["message"]))[0] + 8
            msg_rect = pygame.Rect(INTERNAL_WIDTH - message_width - 4, INTERNAL_HEIGHT - 18, message_width, 14)
            pygame.draw.rect(surface, COLORS["panel"], msg_rect)
            pygame.draw.rect(surface, COLORS["panel_edge"], msg_rect, 1)
            self.draw_text(surface, str(state["message"]), (msg_rect.x + 4, msg_rect.y + 3), str(state["message_color"]))
