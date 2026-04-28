import pygame as pg
import time
import random
import Click_Damage_Feature
from Click_Damage_Feature import Monster, MonsterManager, DamageText, damage_per_click, calculate_damage
import Button_System
import AFK_System
import Currency_System
import Gear_System

'''General'''
pg.init()
window = pg.display.set_mode((800,600)) 
pg.display.set_caption("Attack On Food Titan") 


# Load saved gear data
Gear_System.load_gear()

# Reload saved money, then sum up with AFK rewards
# Load AFK rewards and saved game data
afk_earnings, saved_monster_data, saved_money, saved_progression_index, saved_inventory, saved_shop_state = AFK_System.afk_system.load_and_calculate_afk_rewards()

# Load saved gear data
Gear_System.load_gear()

#   Reload saved money, then sum up with AFK rewards
# Reload saved money, then sum up with AFK rewards

if saved_money > 0:
    Currency_System.pocket_money = saved_money

if afk_earnings > 0:
    Currency_System.pocket_money += afk_earnings
    AFK_System.show_afk_rewards(window, afk_earnings)

# Initialize Monster Manager
monster_manager = Click_Damage_Feature.MonsterManager()

# if status of monster was saved, then load it
if saved_monster_data:
    # Restore waves of monster
    monster_manager.progression_index = saved_progression_index
    
    # Save monster's data
    current_monster = Click_Damage_Feature.Monster(
        saved_monster_data["name"],
        saved_monster_data["max_hp"],
        tuple(saved_monster_data["color"])
    )
    current_monster.hp = saved_monster_data["hp"]
    monster_manager.current_monster = current_monster
    
    print(f"[LOAD] Restored progress: {saved_progression_index}/10, Monster HP: {current_monster.hp}/{current_monster.max_hp}")
else:
    current_monster = monster_manager.current_monster

IsRunning = True
last_auto_save = time.time()
auto_save_interval = 5

# Set data that will be restore
Button_System.panel_manager.pending_inventory = saved_inventory if saved_inventory else []
Button_System.panel_manager.pending_shop_state = saved_shop_state if saved_shop_state else []
Button_System.panel_manager.pending_money = Currency_System.pocket_money

data_restored = False   # Shows data restore state

# NEW: list for damage popups
damage_texts = []

while IsRunning:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            inventory_state, shop_state = Button_System.panel_manager.get_save_data()
            AFK_System.afk_system.save_game_data(
                pocket_money=Currency_System.pocket_money,
                monster_hp=current_monster.hp,
                monster_max_hp=current_monster.max_hp,
                monster_name=current_monster.name,
                monster_color=current_monster.color,
                progression_index=monster_manager.progression_index,
                inventory_items=inventory_state,
                shop_items_state=shop_state
            )
            IsRunning = False
            break
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_g:

                Gear_System.gain_gear("Mythic Pan") 
            # Press 'E' to wear the item 
            elif event.key == pg.K_e:
                Gear_System.equip_gear("Mythic Pan")
            # Press 'U' to unequip weapon
            elif event.key == pg.K_u:
                Gear_System.unequip_gear("weapon")
            # Press 'C' to craft the item (Consumes scraps) - Placeholder for crafting system
            elif event.key == pg.K_c:
                Gear_System.craft_item("Golden Spatula")
        elif event.type == pg.MOUSEBUTTONDOWN:
            if current_monster.rect.collidepoint(event.pos):
                
                # --- MERGED DAMAGE CALCULATION ---
                # 1. Base damage
                base_damage = Click_Damage_Feature.damage_per_click 
                
                # 2. Tap Titans Multiplier (From your branch)
                gear_multi = Gear_System.total_damage_multiplier
                
                # 3. Main branch's new critical hit logic
                # (We pass '0' for the old additive bonus since you multiply now!)
                calculated_base, is_critical = calculate_damage(base_damage, 0)
                
                # 4. Final TT2 Multiplier Calculation
                final_damage = int(calculated_base * gear_multi)
                
                # Apply damage
                current_monster.take_damage(final_damage)

                # Spawn floating damage text
                popup_x = current_monster.rect.x + random.randint(20, current_monster.rect.width - 40)
                popup_y = current_monster.rect.y + random.randint(20, current_monster.rect.height - 40)
                damage_texts.append(DamageText(str(final_damage), (popup_x, popup_y), is_critical=is_critical))

                
                if current_monster.is_defeated():
                    # Trigger your economy system
                    Currency_System.update_economy(current_monster.hp, monster_manager.progression_index)
                    
                    # Spawn next monster
                    monster_manager.next_monster()
                    current_monster = monster_manager.current_monster

        Button_System.panel_manager.handle_event(event)
        for button in Button_System.buttons:
            button.handle_event(event)

    # Load Inventory or Shop data when activated
    if not data_restored and (Button_System.panel_manager.active_panel == "Shop" or Button_System.panel_manager.active_panel == "Inventory"):
        Button_System.panel_manager.load_saved_data(
            Currency_System.pocket_money,
            saved_inventory,
            saved_shop_state
        )
        data_restored = True

    # Sync currency
    Button_System.panel_manager.global_pocket_money = Currency_System.pocket_money

    # Auto save system for AFK
    current_time = time.time()
    if current_time - last_auto_save >= auto_save_interval:
        inventory_state, shop_state = Button_System.panel_manager.get_save_data()
        AFK_System.afk_system.save_game_data(
            pocket_money=Currency_System.pocket_money,
            monster_hp=current_monster.hp,
            monster_max_hp=current_monster.max_hp,
            monster_name=current_monster.name,
            monster_color=current_monster.color,
            progression_index=monster_manager.progression_index,
            inventory_items=inventory_state,
            shop_items_state=shop_state
        )
        AFK_System.afk_system.update_save_time()

        # Gear system auto save
        Gear_System.save_gear()

        last_auto_save = current_time

    for button in Button_System.buttons:
        button.update()

    # Update damage texts
    for dt in damage_texts[:]:
        dt.update()
        if not dt.is_alive():
            damage_texts.remove(dt)

    # Draw everything
    window.fill((227,227,227))
    current_monster.draw(window)
    monster_manager.draw_counter(window)        # Monster counter (top-right)
    monster_manager.draw_stage_counter(window)  # Stage counter (top-middle)
    Currency_System.draw_ui(window)
    AFK_System.draw_AFK_ui(window)

    # Draw damage texts
    for dt in damage_texts:
        dt.draw(window)

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

#2. Drawer system (Inside Button_System.py, line 38 - line 77)
Source code: Deepseek
Link: None

#3. Shop system's UI system (Inside Shop_System.py, line 92 - line 251)
Source code: Deepseek
Link: None

#3. Code for fixing bug (Inside AFK_System.py, line 22 - line 31)
Source code: Deepseek
Link: None

#3. Code for decorational circle (Inside Inventory_System.py, line 130 - line 131, and line 176 - line 177)
Source code: Deepseek
Link: None

Example:
# [Name of the code] (From line x to line x)
#Source code: (Creater of the sources - Platform)
#Link: the link to your reference sources

'''

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
# (Handled by AFK_System.py, which contains AFK system and data saving system that save player's data)
## EKH_3. SHOP SYSTEM
# (Handled by Shop_System.py and Inventory_System, One for buying item one for storing item)
## EKH_4. CLEAR WHEN PRESTIGE SYSTEM

''' Chen Lik Shen '''
## CLS_1. GAME UI & SOUND EFFECT
# (Handled by Currency_System.py)
## CLS_2. GAIN & LOST OF GEAR & CURRENCY SYSTEM
# (Handled by Currency_System.py)
## CLS_3. CRAFTING SYSTEM
## CLS_4. SYSTEM TO ADD NEW GEAR, CHARACTER, AND RECIPES ACCORDING TO EACH PRESTIGE LEVELS