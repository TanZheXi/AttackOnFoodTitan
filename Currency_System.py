import pygame as pg
import random 
import Gear_System

pg.init()
pg.font.init()

# Callbacks for prestige
_prestige_callbacks = []

def register_prestige_callback(callback):
    _prestige_callbacks.append(callback)

# Variables for CLS_1
pocket_money = 0
current_stage = 1

# Setup for CLS_2
ui_font = pg.font.SysFont(None, 48)
scrap_font = pg.font.SysFont(None, 36)

MIDDLE_CENTER_X = 575

def spend_money(amount):
    global pocket_money
    if pocket_money >= amount:
        pocket_money -= amount
        print(f"Purchase successful! Remaining money: ${pocket_money}")
        return True
    else:
        print(f"Not enough money! You need ${amount - pocket_money} more.")
    return False

def update_economy(monster_hp, progression_index):
    global pocket_money
    
    current_stage = (progression_index // 10) + 1
    
    tier = current_stage // 10
    
    if tier == 0:
        target_drop = 5
    elif tier == 1:
        target_drop = 20
    elif tier == 2:
        target_drop = 75
    elif tier == 3:
        target_drop = 250
    elif tier == 4:
        target_drop = 800
    else:
        target_drop = 800 * (2 ** (tier - 4)) 
        
    variance = max(1, int(target_drop * 0.20)) 
    min_drop = target_drop - variance
    max_drop = target_drop + variance
    final_base_drop = random.randint(min_drop, max_drop)
        
    is_boss = (progression_index % 10 == 9)
    if is_boss:
        money_earned = final_base_drop * 5
    else:
        money_earned = final_base_drop
        
    pocket_money += money_earned

def format_money(amount):
    if amount >= 1_000_000_000_000:
        return f"${amount / 1_000_000_000_000:.2f}Trillion"
    elif amount >= 1_000_000_000:
        return f"${amount / 1_000_000_000:.2f}Billion"
    elif amount >= 1_000_000:
        return f"${amount / 1_000_000:.2f}Million"
    elif amount >= 1_000:
        return f"${amount / 1_000:.2f}Thousand"
    else:
        return f"${int(amount)}"
        
def draw_ui(window):
    global michelin_stars
    
    money_text = ui_font.render(f"Pocket Money: {format_money(pocket_money)}", True, (34, 139, 34))
    money_rect = money_text.get_rect(center=(MIDDLE_CENTER_X, 160))
    window.blit(money_text, money_rect)

    if michelin_stars > 0:
        multiplier_display = get_prestige_multiplier()
        stars_text = scrap_font.render(f"Michelin Stars: {michelin_stars} (x{multiplier_display:.1f} DMG)", True, (255, 215, 0))
        stars_rect = stars_text.get_rect(center=(MIDDLE_CENTER_X, 200))
        window.blit(stars_text, stars_rect)

# Prestige System
michelin_stars = 0 
prestige_count = 0

def get_advanced_start(current_stage):
    return max(1, current_stage // 2)

def get_prestige_multiplier():
    return 1.0 + (michelin_stars * 0.10)

def calculate_prestige_rewards(current_stage):
    if current_stage < 10:
        return 0
    return 1 + ((current_stage - 10) // 5)

def trigger_prestige(monster_manager):
    global pocket_money, michelin_stars, prestige_count
    
    stars_to_gain = calculate_prestige_rewards(monster_manager.stage)
    
    if stars_to_gain > 0:
        for callback in _prestige_callbacks:
            callback()
        
        michelin_stars += stars_to_gain
        prestige_count += 1
        pocket_money = 0
        
        monster_manager.stage = get_advanced_start(monster_manager.stage)
        monster_manager.progression_index = (monster_manager.stage - 1) * 10
        monster_manager.current_monster = monster_manager.spawn_monster()
        
        return True
    return False