import pygame as pg
import random
import Equipment_System
import time
import Player_Upgrade_System

class Monster:
    def __init__(self, name, max_hp, color):
        self.name = name
        self.max_hp = float(max_hp)   # store as float
        self.hp = float(max_hp)
        self.color = color
        self.rect = pg.Rect(0, 0, 200, 200)

    def take_damage(self, dmg):
        # Accept float damage, clamp to zero
        self.hp = max(self.hp - float(dmg), 0.0)

    def is_defeated(self):
        return self.hp <= 0.0

    def draw(self, surface):
        pg.draw.rect(surface, self.color, self.rect)
        # Background bar
        pg.draw.rect(surface, (100, 100, 100), (self.rect.x, self.rect.y - 20, self.rect.width, 10))
        # Current HP bar
        hp_bar_width = int((self.hp / self.max_hp) * self.rect.width)
        pg.draw.rect(surface, (255, 0, 0), (self.rect.x, self.rect.y - 20, hp_bar_width, 10))
        # Text with decimals
        font = pg.font.SysFont(None, 30)
        text = font.render(f"{self.name} HP: {self.hp:.1f}/{self.max_hp:.1f}", True, (0, 0, 0))
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
    def __init__(self, damage, pos, is_critical=False):
        self.damage = float(damage)   # store as float
        self.x, self.y = float(pos[0]), float(pos[1])
        self.vy = -60.0
        self.alpha = 255
        self.lifetime_ms = 800
        self.start_ms = pg.time.get_ticks()
        self.color = (0, 0, 0) if not is_critical else (220, 40, 40)
        self.font = pg.font.SysFont(None, 28 if not is_critical else 36)
        self.is_critical = is_critical

    def update(self, dt_ms):
        # Limit maximum time step to avoid large jumps
        dt_ms = min(dt_ms, 50)
        
        elapsed = pg.time.get_ticks() - self.start_ms
        if elapsed >= self.lifetime_ms:
            return True
        
        # Gravity effect (negative gravity makes it slow down as it rises)
        gravity = -20.0
        self.vy += gravity * (dt_ms / 1000.0)
        self.y += self.vy * (dt_ms / 1000.0)
        
        # Fade out effect
        fade_start = self.lifetime_ms * 0.6
        if elapsed > fade_start:
            fade_ratio = (elapsed - fade_start) / (self.lifetime_ms - fade_start)
            self.alpha = max(0, int(255 * (1 - fade_ratio)))
        
        return False

    def draw(self, surface):
        # Format decimal display
        if self.is_critical:
            text_str = f"{self.damage:.2f}!"
        else:
            text_str = f"{self.damage:.1f}"

        txt_surf = self.font.render(text_str, True, self.color)
        txt_surf.set_alpha(self.alpha)
        rect = txt_surf.get_rect(center=(int(self.x), int(self.y)))
        surface.blit(txt_surf, rect)

    def is_alive(self):
        elapsed = pg.time.get_ticks() - self.start_ms
        return elapsed < self.lifetime_ms


# Damage System 
# Use Equipment_System.base_damage if available, otherwise fallback
damage_per_click = getattr(Equipment_System, "base_damage", 1)

# Base critical values
crit_chance = 0.05        # 5% default crit chance
crit_multiplier = 2.0     # critical hits deal 200% damage

def calculate_damage(base_damage=None, extra_chance=0.0, extra_multi=1.0):
    """
    Calculate final damage with critical hits.
    
    Parameters:
    - base_damage: optional base damage (if None, uses Equipment_System.base_damage)
    - extra_chance: additional critical chance from abilities (CrispyPrecision)
    - extra_multi: additional critical multiplier from abilities (CrispyPrecision)
    
    Returns:
    - final_damage (int): the calculated damage value
    - is_critical (bool): whether the hit was critical
    """
    # Get base damage
    if base_damage is None:
        damage = float(Equipment_System.base_damage)
    else:
        damage = float(base_damage)
    
    # Apply equipment multiplier
    damage *= float(Equipment_System.total_damage_multiplier)
    
    # Apply upgrade bonus from Player Upgrade System
    upgrade_level = getattr(Player_Upgrade_System, "level", 0)
    damage += upgrade_level
    if upgrade_level > 0 and upgrade_level % 50 == 0:
        damage *= 1.2
    
    # Calculate total critical chance and multiplier
    total_crit_chance = crit_chance + float(extra_chance)
    total_crit_multi = crit_multiplier * float(extra_multi)
    
    # Determine if hit is critical
    is_critical = random.random() < total_crit_chance
    if is_critical:
        damage *= total_crit_multi
    
    return int(damage), is_critical