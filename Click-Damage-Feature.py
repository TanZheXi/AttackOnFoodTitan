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

'''General'''
pg.init()
window = pg.display.set_mode((800,600)) 
pg.display.set_caption("Attack On Food Titan") 
IsRunning = True

# Initialize Monster Manager
monster_manager = MonsterManager()

while IsRunning:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            IsRunning = False
            break
        elif event.type == pg.KEYDOWN:
            # Press 'G' to get the item (Goes to backpack)
            if event.key == pg.K_g:
                Gear_System.gain_gear("Golden Spatula") 
            # Press 'E' to wear the item 
            elif event.key == pg.K_e:
                Gear_System.equip_gear("Golden Spatula")
            # Press 'U' to unequip weapon
            elif event.key == pg.K_u:
                Gear_System.unequip_gear("weapon")
        elif event.type == pg.MOUSEBUTTONDOWN:
            if monster_manager.current_monster.rect.collidepoint(event.pos):
                
                # 1. base damage
                base_damage = damage_per_click 
                
                # 2. active gear buffs
                gear_bonus = Gear_System.total_bonus_damage 
                
                # 3. Final Damage Calculation
                final_damage = base_damage + gear_bonus 
                
                # 4. Deal the damage to the monster
                monster_manager.current_monster.take_damage(final_damage)
                
                # Print to terminal so you can prove it works
                print(f"Dealt {final_damage} damage (Base {base_damage} + Gear {gear_bonus})")
                if monster_manager.current_monster.is_defeated():
                    # Trigger your economy system
                    Currency_System.update_economy(monster_manager.current_monster.hp) 
                    
                    # Spawn next monster
                    monster_manager.next_monster()

    window.fill((227,227,227)) 
    monster_manager.current_monster.draw(window)
    monster_manager.draw_counter(window)  # Draw monster counter

    # 2. Trigger your separate UI file!
    Currency_System.draw_ui(window)
    
    pg.display.update()

pg.quit()