import pygame as pg
import random 
import Gear_System

# Variables for CLS_1
pocket_money = 0
current_stage = 1

# Setup for CLS_2
pg.font.init()
ui_font = pg.font.SysFont(None, 48)
scrap_font= pg.font.SysFont(None, 36)

MIDDLE_CENTER_x = 575

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
    
    # 1. The Staircase Logic (Tiers)
    tier = current_stage // 10
    
    # We rename 'base_drop' to 'target_drop' because this is the average we want.
    if tier == 0:        # Stages 1 - 9
        target_drop = 5
    elif tier == 1:      # Stages 10 - 19
        target_drop = 20
    elif tier == 2:      # Stages 20 - 29
        target_drop = 75
    elif tier == 3:      # Stages 30 - 39
        target_drop = 250
    elif tier == 4:      # Stages 40 - 49
        target_drop = 800
    else:                # Stages 50 and beyond!
        target_drop = 800 * (2 ** (tier - 4)) 
        
    # 2. NEW: Add Random Logic (Variance)
    # We calculate a 20% variance. (e.g., 20% of 20 is 4).
    # We use max(1, ...) so even small numbers like 5 can still wiggle by at least 1.
    variance = max(1, int(target_drop * 0.20)) 
    
    min_drop = target_drop - variance
    max_drop = target_drop + variance
    
    # Pick a random number between the min and max!
    final_base_drop = random.randint(min_drop, max_drop)
        
    # 3. Apply Boss Bonus
    is_boss = (progression_index % 10 == 9)
    if is_boss:
        # The boss takes that random base drop and multiplies it by 5
        money_earned = final_base_drop * 5
    else:
        money_earned = final_base_drop
        
    # Add to wallet
    pocket_money += money_earned

def format_money(amount):
    """Foundation Level: Converts numbers into readable k, m, b, t."""
    
    # 1. Trillion (t)
    if amount >= 1_000_000_000_000:
        return f"${amount / 1_000_000_000_000:.2f}Trillion"
        
    # 2. Billion (b)
    elif amount >= 1_000_000_000:
        return f"${amount / 1_000_000_000:.2f}Billion"
        
    # 3. Million (m)
    elif amount >= 1_000_000:
        return f"${amount / 1_000_000:.2f}Million"
        
    # 4. Thousand (k)
    elif amount >= 1_000:
        return f"${amount / 1_000:.2f}Thousand"
        
    # 5. Under a thousand (Small numbers)
    else:
        # We use int() here because we don't need decimals for $5 or $500
        return f"${int(amount)}"
        

def draw_ui(window):
    """Logic for drawing the money and prestige stats on screen"""
    # 1. Draw Money
    money_text = ui_font.render(f"Pocket Money: {format_money(pocket_money)}", True, (34, 139, 34))
    money_rect = money_text.get_rect(center=(MIDDLE_CENTER_x, 160))
    window.blit(money_text, money_rect)

    # 2. Draw Michelin Stars & Multiplier (Only if they have prestiged)
    if michelin_stars > 0:
        multiplier_display = get_prestige_multiplier()
        stars_text = scrap_font.render(f"Michelin Stars: {michelin_stars} (x{multiplier_display:.1f} DMG)", True, (255, 215, 0))
        stars_rect = stars_text.get_rect(center=(MIDDLE_CENTER_x, 200))
        window.blit(stars_text, stars_rect)

"""For FUTURE USE: PRESTIGE/REBBIRTH SYSTEM & CURRENCY CONVERSION"""

"""Prestige System: Resets all gear and progress"""
# Variables for Prestige System
michelin_stars = 0 
prestige_count = 0

def calculate_prestige_rewards(current_stage):
    """Calculates Michelin Stars without actually giving them yet."""
    if current_stage < 10:
        return 0
    return 1 + ((current_stage - 10) // 5)

def get_advanced_start(current_stage):
    # Tap Titans Style: Always respawn at exactly 50% of the stage you reached!
    # Example: Prestige at Stage 50 -> Start next run at Stage 25
    # We use max(1, ...) to make sure they never drop below Stage 1
    return max(1, current_stage // 2)

def get_prestige_multiplier():
    """Calculates the permanent damage boost.
    Example: 1 Star = +10% Damage (1.1x multiplier)"""
    return 1.0 + (michelin_stars * 0.10)

def calculate_prestige_rewards(current_stage):
    """Calculates how many Michelin Stars the player earns based on their stage."""
    # Example: You need to beat stage 10 to prestige. 
    # You get 1 star for reaching it, and 1 extra star for every 5 stages after.
    if current_stage < 10:
        return 0
    return 1 + ((current_stage - 10) // 5)

def trigger_prestige(monster_manager):
    # Resets the run but keeps the gear
    global pocket_money, michelin_stars, prestige_count
    
    stars_to_gain = calculate_prestige_rewards(monster_manager.stage)
    
    if stars_to_gain > 0:
        michelin_stars += stars_to_gain
        prestige_count += 1
        pocket_money = 0  # Reset money to zero
        
        # Pass the current stage into our advanced start math!
        monster_manager.stage = get_advanced_start(monster_manager.stage)
        
        monster_manager.progression_index = (monster_manager.stage - 1) * 10
        monster_manager.current_monster = monster_manager.spawn_monster()
        
        return True
        
    return False