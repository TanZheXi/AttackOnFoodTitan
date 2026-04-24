import pygame as pg
import random 

class Monster:  # Monster class
    def __init__(self, name, max_hp, color):
        self.name = name
        self.max_hp = max_hp
        self.hp = max_hp
        self.color = color
        self.rect = pg.Rect(300, 200, 200, 200)  # Monster position and size

    def take_damage(self, dmg):
        self.hp -= dmg
        if self.hp < 0:
            self.hp = 0

    def is_defeated(self):
        return self.hp <= 0

    def draw(self, surface):
        pg.draw.rect(surface, self.color, self.rect)
        # Draw HP bar
        hp_bar_width = int((self.hp / self.max_hp) * self.rect.width)
        pg.draw.rect(surface, (255, 0, 0), (self.rect.x, self.rect.y - 20, hp_bar_width, 10))
        # Draw monster name
        font = pg.font.SysFont(None, 30)
        text = font.render(f"{self.name} HP: {self.hp}/{self.max_hp}", True, (0, 0, 0))
        surface.blit(text, (self.rect.x, self.rect.y - 50))

class MonsterManager:
    def __init__(self):
        # Fixed names and colors for 10 food monsters
        self.food_monsters = [
            {"name": "Bread Monster", "color": (139, 69, 19)},       # Brown
            {"name": "Baguette Monster", "color": (222, 184, 135)},  # Tan
            {"name": "Croissant Titan", "color": (255, 215, 0)},     # Gold
            {"name": "Donut King", "color": (255, 105, 180)},        # Pink
            {"name": "Pizza Beast", "color": (255, 69, 0)},          # Red-Orange
            {"name": "Burger Giant", "color": (160, 82, 45)},        # Saddle Brown
            {"name": "Sushi Serpent", "color": (70, 130, 180)},      # Steel Blue
            {"name": "Taco Titan", "color": (255, 255, 0)},          # Yellow
            {"name": "Ice Cream Overlord", "color": (173, 216, 230)},# Light Blue
            {"name": "Cake Emperor", "color": (255, 182, 193)},      # Light Pink
        ]

        self.progression_index = 0  # drives HP arithmetic sequence
        self.current_monster = self.spawn_monster()

    def spawn_monster(self):
        # Arithmetic sequence: HP = 50 + (progression_index * 100)
        hp_value = 50 + (self.progression_index * 100)

        # Always pick a random monster from the list
        data = random.choice(self.food_monsters)
        name = data["name"]
        color = data["color"]

        return Monster(name, hp_value, color)

    def next_monster(self):
        # Always increment progression index (HP keeps growing)
        self.progression_index += 1
        self.current_monster = self.spawn_monster()

    def draw_counter(self, surface):
        # Counter cycles 1–10 regardless of progression index
        font = pg.font.SysFont(None, 40)
        counter_value = (self.progression_index % 10) + 1
        counter_text = font.render(f"Monster {counter_value}/10", True, (0, 0, 0))
        surface.blit(counter_text, (surface.get_width() - 200, 20))

# Damage per click
damage_per_click = 10