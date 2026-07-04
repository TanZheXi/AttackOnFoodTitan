import pygame as pg
import pygame.gfxdraw
import time
import math
import os

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
    def __init__(self, x, y, radius, duration=20, cooldown_time=120, icon_name=None):
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
        
        # --- NEW: ICON LOADER ---
        self.icon_image = None
        if icon_name:
            try:
                icon_path = os.path.join(os.path.dirname(__file__), "Icon", f"{icon_name}.png")
                if os.path.exists(icon_path):
                    img = pg.image.load(icon_path).convert_alpha()
                    # Scale the icon perfectly to fit inside the circle
                    self.icon_image = pg.transform.scale(img, (radius * 2, radius * 2))
            except Exception as e:
                print(f"[ABILITY] Failed to load {icon_name}.png: {e}")

        # Add rect for collision detection
        self.rect = pg.Rect(x - radius, y - radius, radius * 2, radius * 2)

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
            
            # Add a small black shadow so text pops against the images
            shadow = self.font.render(text, True, (0, 0, 0))
            shadow_rect = shadow.get_rect(center=(self.x + 1, self.y + 1))
            surface.blit(shadow, shadow_rect)
            
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
        self.base_multiplier = 1.5
        self.upgrade_bonus = 0.0
        self.mana_cost = 20

    def set_upgrade_bonus(self, bonus, new_mana_cost=None):
        self.upgrade_bonus = bonus
        if new_mana_cost is not None:
            self.mana_cost = new_mana_cost

    def activate(self, mana_system=None):
        if mana_system and not mana_system.spend(self.mana_cost):
            print("[ABILITY] Not enough mana for Spicy Surge!")
            return
        super().activate()

    def get_multiplier(self):
        if self.active:
            return self.base_multiplier + self.upgrade_bonus
        return 1.0

    def draw(self, surface, mana_system=None):
        self.rect = pg.Rect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)

         # Grey if not enough mana
        if mana_system and mana_system.current_mana < self.mana_cost:
            color = (80, 80, 80)
        elif self.active:
            color = (255, 0, 0)
        elif self.cooldown:
            color = (100, 100, 100)
        else:
            # Fallback to standard colored circle if image is missing
            if self.active:
                color = (255, 0, 0)
            elif self.cooldown:
                color = (100, 100, 100)
            else:
                color = (200, 0, 0)
            if self.is_hovered():
                color = self.brighten(color)
            draw_smooth_circle(surface, self.x, self.y, self.radius, color)

        # --- 2. DRAW TEXT TIMER ---
        self.draw_timer(surface)

        # --- 3. DRAW SWEEP PROGRESS ARC ---
        if self.active:
            progress = (time.time() - self.start_time) / self.duration
            bar_color = lerp_color((173, 216, 230), (255, 0, 0), progress)
            self.draw_progress_arc(surface, progress, clockwise=True, color=bar_color)
        elif self.cooldown:
            progress = (time.time() - self.cooldown_start) / self.cooldown_time
            bar_color = lerp_color((255, 0, 0), (173, 216, 230), progress)
            self.draw_progress_arc(surface, progress, clockwise=False, color=bar_color)

        # Draw mana cost label below the button
        font = pg.font.SysFont(None, 18)
        txt = font.render(f"{self.mana_cost} MP", True, (0, 0, 0))
        txt_rect = txt.get_rect(center=(self.x, self.y + self.radius + 15))
        surface.blit(txt, txt_rect)

# =========================
# Crispy Precision (Crit Boost)
# =========================
class CrispyPrecision(AbilityBase):
    def __init__(self, x, y, radius):
        super().__init__(x, y, radius)
        self.base_crit_chance = 0.15
        self.base_crit_damage = 1.5
        self.upgrade_bonus_chance = 0.0
        self.upgrade_bonus_damage = 0.0
        self.mana_cost = 30

    def set_upgrade_bonus(self, bonus_chance, bonus_damage, new_mana_cost=None):
        self.upgrade_bonus_chance = bonus_chance
        self.upgrade_bonus_damage = bonus_damage
        if new_mana_cost is not None:
            self.mana_cost = new_mana_cost

    def activate(self, mana_system=None):
        if mana_system and not mana_system.spend(self.mana_cost):
            print("[ABILITY] Not enough mana for Crispy Precision!")
            return
        super().activate()

    def get_crit_bonus(self):
        if self.active:
            return (self.base_crit_chance + self.upgrade_bonus_chance,
                    self.base_crit_damage + self.upgrade_bonus_damage)
        return (0.0, 1.0)

    def draw(self, surface):
        # --- 1. DRAW BACKGROUND / ICON ---
        if self.icon_image:
            rect = self.icon_image.get_rect(center=(self.x, self.y))
            surface.blit(self.icon_image, rect)
            
            # Apply a dark tint if on cooldown, or a green tint if active
            if self.cooldown:
                overlay = pg.Surface((self.radius * 2, self.radius * 2), pg.SRCALPHA)
                pg.draw.circle(overlay, (0, 0, 0, 150), (self.radius, self.radius), self.radius)
                surface.blit(overlay, rect)
            elif self.active:
                overlay = pg.Surface((self.radius * 2, self.radius * 2), pg.SRCALPHA)
                pg.draw.circle(overlay, (50, 255, 50, 60), (self.radius, self.radius), self.radius)
                surface.blit(overlay, rect)
                
            # White highlight ring on hover
            if self.is_hovered() and not self.cooldown and not self.active:
                pygame.gfxdraw.aacircle(surface, self.x, self.y, self.radius, (255, 255, 255))
    def draw(self, surface, mana_system=None):
        self.rect = pg.Rect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)

        # Grey if not enough mana
        if mana_system and mana_system.current_mana < self.mana_cost:
            color = (80, 80, 80)
        elif self.active:
            color = (0, 255, 0)
        elif self.cooldown:
            color = (100, 100, 100)
        else:
            # Fallback to standard colored circle if image is missing
            if self.active:
                color = (0, 255, 0)
            elif self.cooldown:
                color = (100, 100, 100)
            else:
                color = (0, 200, 0)
            if self.is_hovered():
                color = self.brighten(color)
            draw_smooth_circle(surface, self.x, self.y, self.radius, color)

        # --- 2. DRAW TEXT TIMER ---
        self.draw_timer(surface)

        # --- 3. DRAW SWEEP PROGRESS ARC ---
        if self.active:
            progress = (time.time() - self.start_time) / self.duration
            bar_color = lerp_color((173, 216, 230), (255, 0, 0), progress)
            self.draw_progress_arc(surface, progress, clockwise=True, color=bar_color)
        elif self.cooldown:
            progress = (time.time() - self.cooldown_start) / self.cooldown_time
            bar_color = lerp_color((255, 0, 0), (173, 216, 230), progress)
            self.draw_progress_arc(surface, progress, clockwise=False, color=bar_color)

        # ✅ Draw mana cost label below the button
        font = pg.font.SysFont(None, 18)
        txt = font.render(f"{self.mana_cost} MP", True, (0, 0, 0))
        txt_rect = txt.get_rect(center=(self.x, self.y + self.radius + 15))
        surface.blit(txt, txt_rect)

# =================
# Mana Point System
# =================
class ManaSystem:
    def __init__(self, max_mana=100, regen_rate=0.2):
        self.max_mana = max_mana
        self.current_mana = max_mana
        self.regen_rate = regen_rate
        self.last_update = time.time()

    def update(self):
        now = time.time()
        elapsed = now - self.last_update
        self.last_update = now
        self.current_mana = min(self.max_mana, self.current_mana + elapsed * self.regen_rate)

    def spend(self, amount):
        if self.current_mana >= amount:
            self.current_mana -= amount
            return True
        return False

    def draw(self, surface, left_boundary_x, ability_y, ability_radius, width=120, height=16):
        x = left_boundary_x + 5
        y = ability_y - ability_radius - height - 10

        # Background
        pg.draw.rect(surface, (40, 40, 40), (x, y, width, height))
        # Filled portion (cyan)
        mana_ratio = self.current_mana / self.max_mana
        pg.draw.rect(surface, (0, 255, 255), (x, y, int(width * mana_ratio), height))
        # Border
        pg.draw.rect(surface, (200, 200, 200), (x, y, width, height), 2)

        # Text display: current/max
        font = pg.font.SysFont(None, 20)
        text_surface = font.render(f"{int(self.current_mana)}/{self.max_mana}", True, (0, 0, 0))
        text_rect = text_surface.get_rect(midleft=(x + width + 10, y + height // 2))
        surface.blit(text_surface, text_rect)