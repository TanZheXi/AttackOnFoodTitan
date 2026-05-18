import pygame as pg
import pygame.gfxdraw
import time
import math

# =========================
# Helper: Smooth Circle
# =========================
def draw_smooth_circle(surface, x, y, radius, color):
    pygame.gfxdraw.filled_circle(surface, x, y, radius, color)
    pygame.gfxdraw.aacircle(surface, x, y, radius, (0, 0, 0))  # outline

# =========================
# Base Ability Template
# =========================
class AbilityBase:
    def __init__(self, x, y, radius, duration=20, cooldown_time=120):
        self.x = x
        self.y = y
        self.radius = radius
        self.active = False
        self.cooldown = False
        self.duration = duration
        self.cooldown_time = cooldown_time
        self.start_time = 0
        self.cooldown_start = 0
        self.font = pg.font.SysFont(None, 24)

    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            mouse_x, mouse_y = event.pos
            if not self.active and not self.cooldown:
                if (mouse_x - self.x) ** 2 + (mouse_y - self.y) ** 2 <= self.radius ** 2:
                    self.activate()

    def activate(self):
        self.active = True
        self.start_time = time.time()

    def update(self):
        current_time = time.time()
        if self.active and current_time - self.start_time >= self.duration:
            self.active = False
            self.cooldown = True
            self.cooldown_start = current_time
        elif self.cooldown and current_time - self.cooldown_start >= self.cooldown_time:
            self.cooldown = False

    def draw_timer(self, surface):
        text = ""
        if self.active:
            remaining = int(self.duration - (time.time() - self.start_time))
            text = f"{remaining}s"
        elif self.cooldown:
            remaining = int(self.cooldown_time - (time.time() - self.cooldown_start))
            text = f"CD {remaining}s"

        if text:
            txt_surface = self.font.render(text, True, (255, 255, 255))
            txt_rect = txt_surface.get_rect(center=(self.x, self.y))
            surface.blit(txt_surface, txt_rect)

    def draw_progress_arc(self, surface, progress, color):
        """Draw an arc around the circle showing progress (0.0–1.0)."""
        rect = pg.Rect(self.x - self.radius - 4, self.y - self.radius - 4,
                       (self.radius + 4) * 2, (self.radius + 4) * 2)
        start_angle = -math.pi / 2  # start at top
        end_angle = start_angle + (progress * 2 * math.pi)
        pg.draw.arc(surface, color, rect, start_angle, end_angle, 4)


# =========================
# Spicy Surge (Damage Boost)
# =========================
class SpicySurge(AbilityBase):
    def __init__(self, x, y, radius):
        super().__init__(x, y, radius)
        self.damage_multiplier = 1.5

    def get_multiplier(self):
        return self.damage_multiplier if self.active else 1.0

    def draw(self, surface):
        if self.active:
            color = (255, 0, 0)
        elif self.cooldown:
            color = (100, 100, 100)
        else:
            color = (200, 0, 0)

        draw_smooth_circle(surface, self.x, self.y, self.radius, color)
        self.draw_timer(surface)

        # Duration bar (green arc)
        if self.active:
            progress = (time.time() - self.start_time) / self.duration
            self.draw_progress_arc(surface, progress, (0, 255, 0))
        # Cooldown bar (red arc)
        elif self.cooldown:
            progress = (time.time() - self.cooldown_start) / self.cooldown_time
            self.draw_progress_arc(surface, progress, (255, 0, 0))


# =========================
# Crispy Precision (Crit Boost)
# =========================
class CrispyPrecision(AbilityBase):
    def __init__(self, x, y, radius):
        super().__init__(x, y, radius)
        self.extra_crit_chance = 0.15
        self.extra_crit_damage = 1.5

    def get_crit_bonus(self):
        if self.active:
            return self.extra_crit_chance, self.extra_crit_damage
        return 0.0, 1.0

    def draw(self, surface):
        if self.active:
            color = (0, 255, 0)
        elif self.cooldown:
            color = (100, 100, 100)
        else:
            color = (0, 200, 0)

        draw_smooth_circle(surface, self.x, self.y, self.radius, color)
        self.draw_timer(surface)

        # Duration bar (blue arc)
        if self.active:
            progress = (time.time() - self.start_time) / self.duration
            self.draw_progress_arc(surface, progress, (0, 0, 255))
        # Cooldown bar (yellow arc)
        elif self.cooldown:
            progress = (time.time() - self.cooldown_start) / self.cooldown_time
            self.draw_progress_arc(surface, progress, (255, 255, 0))