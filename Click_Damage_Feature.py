import pygame as pg
import random
import Gear_System

class Monster:
    def __init__(self, name, max_hp, color):
        self.name = name
        self.max_hp = max_hp
        self.hp = max_hp
        self.color = color
        self.rect = pg.Rect(0, 0, 200, 200)

    def take_damage(self, dmg):
        self.hp = max(self.hp - dmg, 0)

    def is_defeated(self):
        return self.hp <= 0

    def draw(self, surface):
        pg.draw.rect(surface, self.color, self.rect)
        # Background bar
        pg.draw.rect(surface, (100, 100, 100), (self.rect.x, self.rect.y - 20, self.rect.width, 10))
        # Current HP bar
        hp_bar_width = int((self.hp / self.max_hp) * self.rect.width)
        pg.draw.rect(surface, (255, 0, 0), (self.rect.x, self.rect.y - 20, hp_bar_width, 10))
        # Text
        font = pg.font.SysFont(None, 30)
        text = font.render(f"{self.name} HP: {self.hp}/{self.max_hp}", True, (0, 0, 0))
        text_rect = text.get_rect(center=(self.rect.centerx, self.rect.y - 35))
        surface.blit(text, text_rect)


class MonsterManager:
    def __init__(self):
        self.food_monsters = [
            {"name": "Bread Monster", "color": (139, 69, 19)},
            {"name": "Baguette Monster", "color": (222, 184, 135)},
            {"name": "Croissant Titan", "color": (255, 215, 0)},
            {"name": "Donut King", "color": (255, 105, 180)},
            {"name": "Pizza Beast", "color": (255, 69, 0)},
            {"name": "Burger Giant", "color": (160, 82, 45)},
            {"name": "Sushi Serpent", "color": (70, 130, 180)},
            {"name": "Taco Titan", "color": (255, 255, 0)},
            {"name": "Ice Cream Overlord", "color": (173, 216, 230)},
            {"name": "Cake Emperor", "color": (255, 182, 193)},
        ]
        self.progression_index = 0
        self.stage = 1
        self.current_monster = self.spawn_monster()

    def spawn_monster(self):
        hp_value = 50 + (self.progression_index * 100)
        data = random.choice(self.food_monsters)
        return Monster(data["name"], hp_value, data["color"])

    def next_monster(self):
        self.progression_index += 1
        if self.progression_index % 10 == 0:
            self.stage += 1
        self.current_monster = self.spawn_monster()

    def draw_counter(self, surface):
        font = pg.font.SysFont(None, 36)
        counter_value = (self.progression_index % 10) + 1
        counter_text = font.render(f"Monster {counter_value}/10", True, (0, 0, 0))
        #surface.blit(counter_text, (surface.get_width() - 200, 20))
        return counter_text

    def draw_stage_counter(self, surface):
        font = pg.font.SysFont(None, 48, bold=True)
        stage_text = font.render(f"Stage {self.stage}", True, (0, 0, 0))
        #surface_width = surface.get_width()
        #stage_x = (surface_width - stage_text.get_width()) // 2
        #surface.blit(stage_text, (stage_x, 20))
        return stage_text


class DamageText:
    def __init__(self, text, pos, is_critical=False):
        self.text = str(text)
        self.x, self.y = float(pos[0]), float(pos[1])
        self.vy = -80.0                      # pixels per second upward
        self.alpha = 255
        self.lifetime_ms = 900               # visible time in ms
        self.start_ms = pg.time.get_ticks()
        # Color: black for normal, red for critical
        self.color = (0, 0, 0) if not is_critical else (220, 40, 40)
        # Larger font for critical hits
        self.font = pg.font.SysFont(None, 28 if not is_critical else 36)
        self.is_critical = is_critical

    def update(self, dt_ms):
        """Update position and alpha. Return True if expired."""
        elapsed = pg.time.get_ticks() - self.start_ms
        if elapsed >= self.lifetime_ms:
            return True

        # Move upward using dt
        self.y += self.vy * (dt_ms / 1000.0)

        # Fade out in the last 30% of lifetime
        fade_start = self.lifetime_ms * 0.7
        if elapsed > fade_start:
            fade_ratio = (elapsed - fade_start) / (self.lifetime_ms - fade_start)
            self.alpha = max(0, int(255 * (1 - fade_ratio)))

        return False

    def draw(self, surface):
        txt_surf = self.font.render(self.text, True, self.color)
        txt_surf.set_alpha(self.alpha)
        rect = txt_surf.get_rect(center=(int(self.x), int(self.y)))
        surface.blit(txt_surf, rect)

    def is_alive(self):
        return self.lifetime > 0


# Damage System 
# Use Gear_System.base_damage if available, otherwise fallback
damage_per_click = getattr(Gear_System, "base_damage", 1)

# Base critical values
crit_chance = 0.05        # 5% default crit chance
crit_multiplier = 2.0     # critical hits deal 200% damage

def calculate_damage(base_damage, gear_bonus=0, extra_chance=0.0, extra_multi=1.0):
    '''
    Calculate final damage with critical hit logic.
    - base_damage: raw damage before multipliers
    - gear_bonus: extra flat damage from gear
    - extra_chance: additional crit chance from abilities
    - extra_multi: multiplier applied to crit damage from abilities
    Returns: (final_damage, is_critical)
    '''
    final_damage = base_damage + gear_bonus

    # Effective crit chance and multiplier
    effective_chance = crit_chance + extra_chance
    effective_multi = crit_multiplier * extra_multi

    # Critical check
    is_critical = random.random() < effective_chance
    if is_critical:
        final_damage = int(final_damage * effective_multi)

    return final_damage, is_critical