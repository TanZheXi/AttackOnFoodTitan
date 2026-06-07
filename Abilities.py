import pygame as pg
import pygame.gfxdraw
import time
import math

# =========================
# Helper: Smooth Circle
# =========================
def draw_smooth_circle(surface, x, y, radius, color):
    pygame.gfxdraw.filled_circle(surface, x, y, radius, color)
    pygame.gfxdraw.aacircle(surface, x, y, radius, (0, 0, 0))

# =========================
# Helper: Color Interpolation
# =========================
def lerp_color(color_start, color_end, t):
    """Linearly interpolate between two colors (0.0–1.0)."""
    t = max(0.0, min(1.0, t))
    r = int(color_start[0] + (color_end[0] - color_start[0]) * t)
    g = int(color_start[1] + (color_end[1] - color_start[1]) * t)
    b = int(color_start[2] + (color_end[2] - color_start[2]) * t)
    return (max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)))

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
        print(f"[ABILITY] Activated at {self.start_time}")

    def update(self):
        current_time = time.time()
        if self.active:
            elapsed = current_time - self.start_time
            if elapsed >= self.duration:
                self.active = False
                self.cooldown = True
                self.cooldown_start = current_time
                print(f"[ABILITY] Duration ended, entering cooldown at {current_time}")
        elif self.cooldown:
            elapsed = current_time - self.cooldown_start
            if elapsed >= self.cooldown_time:
                self.cooldown = False
                print(f"[ABILITY] Cooldown ended at {current_time}")

    def draw_timer(self, surface):
        text = ""
        current_time = time.time()
        if self.active:
            elapsed = current_time - self.start_time
            remaining = max(0, int(self.duration - elapsed))
            text = f"{remaining}s"
        elif self.cooldown:
            elapsed = current_time - self.cooldown_start
            remaining = max(0, int(self.cooldown_time - elapsed))
            text = f"CD {remaining}s"
        if text:
            txt_surface = self.font.render(text, True, (255, 255, 255))
            txt_rect = txt_surface.get_rect(center=(self.x, self.y))
            surface.blit(txt_surface, txt_rect)

    def is_hovered(self):
        mouse_x, mouse_y = pg.mouse.get_pos()
        return (mouse_x - self.x) ** 2 + (mouse_y - self.y) ** 2 <= self.radius ** 2

    def brighten(self, color, amount=50):
        r = min(color[0] + amount, 255)
        g = min(color[1] + amount, 255)
        b = min(color[2] + amount, 255)
        return (r, g, b)

    def draw_progress_arc(self, surface, progress, clockwise=True, color=(0, 0, 139)):
        if progress <= 0 or progress >= 1:
            return
        
        rect = pg.Rect(self.x - self.radius - 6, self.y - self.radius - 6,
                       (self.radius + 6) * 2, (self.radius + 6) * 2)
        start_angle = -math.pi / 2
        if clockwise:
            end_angle = start_angle + (progress * 2 * math.pi)
        else:
            end_angle = start_angle - (progress * 2 * math.pi)
        
        if isinstance(color, tuple) and len(color) == 3:
            safe_color = (max(0, min(255, color[0])), 
                         max(0, min(255, color[1])), 
                         max(0, min(255, color[2])))
        else:
            safe_color = (0, 0, 139)
        
        pg.draw.arc(surface, safe_color, rect, start_angle, end_angle, 5)


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

        if self.is_hovered():
            color = self.brighten(color)

        draw_smooth_circle(surface, self.x, self.y, self.radius, color)
        self.draw_timer(surface)

        if self.active:
            progress = (time.time() - self.start_time) / self.duration
            bar_color = lerp_color((173, 216, 230), (255, 0, 0), progress)
            self.draw_progress_arc(surface, progress, clockwise=True, color=bar_color)
        elif self.cooldown:
            progress = (time.time() - self.cooldown_start) / self.cooldown_time
            bar_color = lerp_color((255, 0, 0), (173, 216, 230), progress)
            self.draw_progress_arc(surface, progress, clockwise=False, color=bar_color)


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

        if self.is_hovered():
            color = self.brighten(color)

        draw_smooth_circle(surface, self.x, self.y, self.radius, color)
        self.draw_timer(surface)

        if self.active:
            progress = (time.time() - self.start_time) / self.duration
            bar_color = lerp_color((173, 216, 230), (255, 0, 0), progress)
            self.draw_progress_arc(surface, progress, clockwise=True, color=bar_color)
        elif self.cooldown:
            progress = (time.time() - self.cooldown_start) / self.cooldown_time
            bar_color = lerp_color((255, 0, 0), (173, 216, 230), progress)
            self.draw_progress_arc(surface, progress, clockwise=False, color=bar_color)