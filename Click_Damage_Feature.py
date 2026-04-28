import pygame as pg
import random

class Monster:
    def __init__(self, name, max_hp, color):
        self.name = name
        self.max_hp = max_hp
        self.hp = max_hp
        self.color = color
        self.rect = pg.Rect(300, 200, 200, 200)

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
        surface.blit(text, (self.rect.x, self.rect.y - 50))


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
        font = pg.font.SysFont(None, 40)
        counter_value = (self.progression_index % 10) + 1
        counter_text = font.render(f"Monster {counter_value}/10", True, (0, 0, 0))
        surface.blit(counter_text, (surface.get_width() - 200, 20))

    def draw_stage_counter(self, surface):
        font = pg.font.SysFont(None, 50, bold=True)
        stage_text = font.render(f"Stage {self.stage}", True, (0, 0, 0))
        surface_width = surface.get_width()
        stage_x = (surface_width - stage_text.get_width()) // 2
        surface.blit(stage_text, (stage_x, 20))


class DamageText:
    def __init__(self, text, pos, is_critical=False):
        self.text = text
        self.pos = list(pos)   # [x, y]
        self.is_critical = is_critical
        # Critical hits: red color, larger font, bold
        if is_critical:
            self.color = (255, 0, 0)
            self.font = pg.font.SysFont(None, 36, bold=True)  # larger font
        else:
            self.color = (0, 0, 0)
            self.font = pg.font.SysFont(None, 28)
        self.lifetime = 60     # frames (~1 second at 60fps)

    def update(self):
        self.pos[1] -= 1
        self.lifetime -= 1

    def draw(self, surface):
        alpha = max(0, int((self.lifetime / 60) * 255))
        render = self.font.render(self.text, True, self.color)
        render.set_alpha(alpha)
        surface.blit(render, self.pos)

    def is_alive(self):
        return self.lifetime > 0


# Damage System 
damage_per_click = 1

# Critical hit settings
crit_chance = 0.05       # 5% chance
crit_multiplier = 2.0    # double damage on crit

def calculate_damage(base_damage, gear_bonus=0):
    # Return (final_damage, is_critical) with crit chance applied. 
    final_damage = base_damage + gear_bonus
    is_critical = random.random() < crit_chance
    if is_critical:
        final_damage = int(final_damage * crit_multiplier)
    return final_damage, is_critical