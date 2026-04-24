import pygame as pg
import json
import os
import time
import Button_System
import Currency_System
import Gear_System


''' Tan Zhe Xi '''
## TZX_1. MINIGAME SYSTEM



## TZX_2. GEAR & DATA DESIGN



## TZX_3. ABILITY TO CLICK TO DEAL DAMAGE

class Monster: # Monster class
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
        pg.draw.rect(surface, (255,0,0), (self.rect.x, self.rect.y - 20, hp_bar_width, 10))
        # Draw monster name
        font = pg.font.SysFont(None, 30)
        text = font.render(f"{self.name} HP: {self.hp}/{self.max_hp}", True, (0,0,0))
        surface.blit(text, (self.rect.x, self.rect.y - 50))

# Initialize first monster
current_monster = Monster("Bread Monster", 50, (0,255,0))

# Damage per click
damage_per_click = 10

## TZX_4. ADJUSTING STATS ACCORDING TO PRESTIGE LEVELS




''' Eng Kai Hin '''
## EKH_1. BUTTON INTERACTION SYSTEM



## EKH_2. AFK SYSTEM



## EKH_3. SHOP SYSTEM



## EKH_4. CLEAR WHEN PRESTIGE SYSTEM




''' Chen Lik Shen '''
## CLS_1. GAME UI & SOUND EFFECT
# (Handled by Currency_System.py)

## CLS_2. GAIN & LOST OF GEAR & CURRENCY SYSTEM
# (Handled by Currency_System.py)
## CLS_3. CRAFTING SYSTEM



## CLS_4. SYSTEM TO ADD NEW GEAR, CHARACTER, AND RECIPES ACCORDING TO EACH PRESTIGE LEVELS




'''General'''
pg.init()
window = pg.display.set_mode((800,600)) 
pg.display.set_caption("Attack On Food Titan") 
IsRunning = True
# Timer for AFK system
last_auto_save = time.time()
auto_save_interval = 5  # Save the game every 5 second

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
            if current_monster.rect.collidepoint(event.pos):
                
                # 1. base damage
                base_damage = damage_per_click 
                
                # 2. active gear buffs
                gear_bonus = Gear_System.total_bonus_damage 
                
                # 3. Final Damage Calculation
                final_damage = base_damage + gear_bonus 
                
                # 4. Deal the damage to the monster
                current_monster.take_damage(final_damage)
                
                # Print to terminal so you can prove it works
                print(f"Dealt {final_damage} damage (Base {base_damage} + Gear {gear_bonus})")
                if current_monster.is_defeated():
                    # Trigger your economy system
                    Currency_System.update_economy(current_monster.hp) 
                    
                    # Spawn next monster
                    current_monster = Monster("Baguette Monster", 100, (0,0,255))

    window.fill((227,227,227)) 
    current_monster.draw(window)
    
    # 2. Trigger your separate UI file!
    Currency_System.draw_ui(window)
    
    pg.display.update()

pg.quit()



'''
References list

#1. ABILITY TO CLICK TO DEAL DAMAGE (line 16 - line 40)
Source code: Copilot
Link: None



Example:
# [Name of the code] (From line x to line x)
#Source code: (Creater of the sources - Platform)
#Link: the link to your reference sources

'''