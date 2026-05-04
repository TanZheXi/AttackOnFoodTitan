import pygame as pg
import random
import time

class Monster:
    def __init__(self, name, max_hp, color):
        self.name = name
        self.max_hp = max_hp
        self.hp = max_hp
        self.color = color
        self.rect = pg.Rect(300, 200, 200, 200)
        self.is_boss = False
        self.time_left = None  # for boss countdown display

    def take_damage(self, dmg):
        self.hp = max(self.hp - dmg, 0)

    def is_defeated(self):
        return self.hp <= 0

    def draw(self, surface):
     # Monster body
     pg.draw.rect(surface, self.color, self.rect)

     # HP bar background
     pg.draw.rect(surface, (100, 100, 100), (self.rect.x, self.rect.y - 20, self.rect.width, 10))

     # Current HP bar
     hp_bar_width = int((self.hp / self.max_hp) * self.rect.width) if self.max_hp > 0 else 0
     bar_color = (255, 215, 0) if self.is_boss else (255, 0, 0)
     pg.draw.rect(surface, bar_color, (self.rect.x, self.rect.y - 20, hp_bar_width, 10))

     # Monster text centered above HP bar
     font = pg.font.SysFont("Arial", 28, bold=self.is_boss)
     label = f"{self.name} HP: {self.hp}/{self.max_hp}"
     if self.is_boss:
        label = "[BOSS] " + label
     text = font.render(label, True, (0, 0, 0))
     text_x = self.rect.x + (self.rect.width - text.get_width()) // 2
     text_y = self.rect.y - 50
     surface.blit(text, (text_x, text_y))

     # ✅ Boss timer text + bar below HP bar
     if self.is_boss and self.time_left is not None:
        timer_font = pg.font.SysFont("Arial", 24, bold=True)
        color = (200, 0, 0) if self.time_left <= 5 else (0, 0, 0)
        timer_text = timer_font.render(f"Time Left: {self.time_left}s", True, color)

        # Position text centered below HP bar
        timer_x = self.rect.x + (self.rect.width - timer_text.get_width()) // 2
        timer_y = self.rect.y - 5
        surface.blit(timer_text, (timer_x, timer_y))

        # Draw timer bar to the left of the text
        total_time = 30
        bar_max_width = 100  # fixed width for full 30s
        bar_height = 10
        # shrink bar proportionally
        bar_width = int((self.time_left / total_time) * bar_max_width)

        bar_x = timer_x - bar_max_width - 10  # 10px gap to the left of text
        bar_y = timer_y + (timer_text.get_height() - bar_height) // 2

        # background (gray)
        pg.draw.rect(surface, (180, 180, 180), (bar_x, bar_y, bar_max_width, bar_height))
        # foreground (green → red as time decreases)
        fg_color = (0, 200, 0) if self.time_left > 10 else (200, 0, 0)
        pg.draw.rect(surface, fg_color, (bar_x, bar_y, bar_width, bar_height))


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
        self.base_hp = 50.0
        self.common_ratio = 1.05
        self.monster_order = random.sample(self.food_monsters, len(self.food_monsters))
        self.current_monster = self.spawn_monster()
        self.boss_start_time = None

    def spawn_monster(self):
        hp_value = int(self.base_hp * (self.common_ratio ** self.progression_index))
        is_boss = (self.progression_index + 1) % 10 == 0
        if is_boss:
            hp_value *= 2
            self.boss_start_time = time.time()
        else:
            self.boss_start_time = None

        data = self.monster_order[self.progression_index % len(self.monster_order)]
        monster = Monster(data["name"], hp_value, data["color"])
        monster.is_boss = is_boss
        return monster

    def next_monster(self):
        self.progression_index += 1
        if self.progression_index % 10 == 0:
            self.stage += 1
            self.monster_order = random.sample(self.food_monsters, len(self.food_monsters))
        self.current_monster = self.spawn_monster()

    def check_boss_timer(self):
        if self.current_monster.is_boss and self.boss_start_time:
            elapsed = time.time() - self.boss_start_time
            return elapsed > 30
        return False

    def reset_to_first_monster(self):
        self.progression_index = (self.stage - 1) * 10
        self.current_monster = self.spawn_monster()

    def get_boss_time_left(self):
        if self.current_monster.is_boss and self.boss_start_time:
            elapsed = time.time() - self.boss_start_time
            return max(0, 30 - int(elapsed))
        return None

    def draw_counter(self, surface):
     font = pg.font.SysFont(None, 40)
     counter_value = (self.progression_index % 10) + 1
     label = f"Monster {counter_value}/10"
     if getattr(self.current_monster, "is_boss", False):
      label += " (Boss!)"

     counter_text = font.render(label, True, (0, 0, 0))

     # Clamp position so text stays inside window
     text_width = counter_text.get_width()
     text_x = max(10, surface.get_width() - text_width - 10)  # 10px padding
     text_y = 20

     surface.blit(counter_text, (text_x, text_y))

    def draw_stage_counter(self, surface):
        font = pg.font.SysFont(None, 50, bold=True)
        stage_text = font.render(f"Stage {self.stage}", True, (0, 0, 0))
        stage_x = (surface.get_width() - stage_text.get_width()) // 2
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
damage_per_click = 50

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