import pygame as pg
import time
import Click_Damage_Feature
import Button_System
import AFK_System
import Currency_System
import Gear_System


''' Tan Zhe Xi '''
## TZX_1. MINIGAME SYSTEM



## TZX_2. GEAR & DATA DESIGN



## TZX_3. ABILITY TO CLICK TO DEAL DAMAGE
#(Handled by Click_Damage_Feature.py)

## TZX_4. ADJUSTING STATS ACCORDING TO PRESTIGE LEVELS




''' Eng Kai Hin '''
## EKH_1. BUTTON INTERACTION SYSTEM
# (Handled by Button_System.py, which contains button and drawer system)

## EKH_2. AFK SYSTEM
# (Handled by AFK_System.py, which contains AFK system and data saving system)

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

# Load AFK rewards and saved game data
afk_earnings, saved_monster_data, saved_money = AFK_System.afk_system.load_and_calculate_afk_rewards()

#Reload saved money, then sum up with AFK rewards
if saved_money > 0:
    Currency_System.pocket_money = saved_money

# Load AFK rewards screen
if afk_earnings > 0:
    Currency_System.pocket_money += afk_earnings
    AFK_System.show_afk_rewards(window, afk_earnings)
    
current_monster = None

# if status of monster was saved, then load it
if saved_monster_data:
    current_monster = Click_Damage_Feature.Monster(
        saved_monster_data["name"],
        saved_monster_data["max_hp"],
        tuple(saved_monster_data["color"])
    )
    current_monster.hp = saved_monster_data["hp"]
else:
    current_monster = Click_Damage_Feature.Monster("Bread Monster", 50, (139,69,19))

IsRunning = True
# Timer for AFK system
last_auto_save = time.time()
auto_save_interval = 5  # Save the game every 5 second

# Initialize Monster Manager
monster_manager = Click_Damage_Feature.MonsterManager()
current_monster = monster_manager.current_monster

while IsRunning:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            # Save game data before exit it
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
                base_damage = Click_Damage_Feature.damage_per_click 
                
                # 2. active gear buffs
                gear_bonus = Gear_System.total_bonus_damage 
                
                # 3. Final Damage Calculation
                final_damage = base_damage + gear_bonus 
                
                # 4. Deal the damage to the monster
                current_monster.take_damage(final_damage)
                
                # Print to terminal so you can prove it works
                #print(f"Dealt {final_damage} damage (Base {base_damage} + Gear {gear_bonus})")
                if current_monster.is_defeated():
                    # Trigger your economy system
                    Currency_System.update_economy(current_monster.hp, monster_manager.progression_index) 
                    
                    # Spawn next monster
                    monster_manager.next_monster()

                    current_monster = monster_manager.current_monster

        for button in Button_System.buttons:
            button.handle_event(event)

# Auto save system for AFK
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

    window.fill((227,227,227)) # Adjust the window color from here by editing its RGB code
    current_monster.draw(window)
    monster_manager.draw_counter(window)  # Draw monster counter
    Currency_System.draw_ui(window) # CLS_2. Trigger your separate UI file!
    AFK_System.draw_AFK_ui(window)

    for button in Button_System.buttons:
        button.draw(window)

    #Draw button if actived
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