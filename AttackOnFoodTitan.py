import pygame as pg
import time
from Click_Damage_Feature import Monster, MonsterManager, damage_per_click
import Button_System
import AFK_System
import Currency_System
import Gear_System

# General (Main loop) #

pg.init()
window = pg.display.set_mode((800,600)) 
pg.display.set_caption("Attack On Food Titan") 

# Load AFK rewards and saved game data
afk_earnings, saved_monster_data, saved_money = AFK_System.afk_system.load_and_calculate_afk_rewards()

# Reload saved money, then sum up with AFK rewards
if saved_money > 0:
    Currency_System.pocket_money = saved_money

# Load AFK rewards screen
if afk_earnings > 0:
    Currency_System.pocket_money += afk_earnings
    AFK_System.show_afk_rewards(window, afk_earnings)
    
# Initialize Monster
if saved_monster_data:
    current_monster = Monster(
        saved_monster_data["name"],
        saved_monster_data["max_hp"],
        tuple(saved_monster_data["color"])
    )
    current_monster.hp = saved_monster_data["hp"]
else:
    current_monster = Monster("Bread Monster", 50, (139,69,19))

IsRunning = True
last_auto_save = time.time()
auto_save_interval = 5  # Save the game every 5 seconds

# Initialize Monster Manager
monster_manager = MonsterManager()
current_monster = monster_manager.current_monster

while IsRunning:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            AFK_System.afk_system.save_game_data(
                Currency_System.pocket_money,
                current_monster.hp,
                current_monster.max_hp,
                current_monster.name,
                current_monster.color
            )
            IsRunning = False
            break
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_g:
                Gear_System.gain_gear("Golden Spatula") 
            elif event.key == pg.K_e:
                Gear_System.equip_gear("Golden Spatula")
            elif event.key == pg.K_u:
                Gear_System.unequip_gear("weapon")
        elif event.type == pg.MOUSEBUTTONDOWN:
            if current_monster.rect.collidepoint(event.pos):
                base_damage = damage_per_click 
                gear_bonus = Gear_System.total_bonus_damage 
                final_damage = base_damage + gear_bonus 
                current_monster.take_damage(final_damage)

                if current_monster.is_defeated():
                    Currency_System.update_economy(current_monster.max_hp, monster_manager.progression_index) 
                    monster_manager.next_monster()
                    current_monster = monster_manager.current_monster

        for button in Button_System.buttons:
            button.handle_event(event)

    # Auto save system
    current_time = time.time()
    if current_time - last_auto_save >= auto_save_interval:
        AFK_System.afk_system.save_game_data(
            Currency_System.pocket_money,
            current_monster.hp,
            current_monster.max_hp,
            current_monster.name,
            current_monster.color
        )
        AFK_System.afk_system.update_save_time()
        last_auto_save = current_time

    for button in Button_System.buttons:
        button.update()

    window.fill((227,227,227))
    current_monster.draw(window)
    monster_manager.draw_counter(window)
    Currency_System.draw_ui(window)
    AFK_System.draw_AFK_ui(window)

    for button in Button_System.buttons:
        button.draw(window)

    Button_System.panel_manager.draw(window)
    
    pg.display.update()

pg.quit()


'''
References list

#1. ABILITY TO CLICK TO DEAL DAMAGE (line 16 - line 40)
Source code: Copilot
Link: None

#2. Drawer system (Inside Button_System file, line 38 - line 77)
Source code: Deepseek
Link: None

Example:
# [Name of the code] (From line x to line x)
#Source code: (Creater of the sources - Platform)
#Link: the link to your reference sources

'''