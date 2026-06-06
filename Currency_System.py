import pygame as pg
import random 
import Equipment_System

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

# --- NEW: LOAD AND SCALE THE COIN ICON ---
try:
    # Load the image

    raw_coin_image = pg.image.load("Icon/pocket_money.png")
    # Scale it down to a nice 40x40 pixel UI icon
    coin_icon = pg.transform.scale(raw_coin_image, (40, 40))
except Exception as e:
    print(f"[UI WARN] Could not load pocket_money.png: {e}")
    coin_icon = None
# -----------------------------------------

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
    # 1. Less than 1,000 stays normal
    if amount < 1000:
        return f"{int(amount)}"

    # You can add as many as you want here manually. It's super easy to read.
    suffixes = [
        "", "K", "M", "B", "T", "Qa", "Qi",   # The Classics     
    ]
    
    magnitude = 0
    temp_amount = float(amount)

    # 3. Keep dividing by 1000 as long as we haven't run out of suffixes in our list
    while temp_amount >= 1000 and magnitude < len(suffixes) - 1:
        magnitude += 1
        temp_amount /= 1000.0

    # We switch them to scientific notation so the game doesn't crash.
    if temp_amount >= 1000 and magnitude == len(suffixes) - 1:
        return f"{float(amount):.2e}"

    # 5. Return the formatted number
    return f"{temp_amount:.2f}{suffixes[magnitude]}"
        
def draw_ui(window):
    # 1. Render the text
    money_text = ui_font.render(f"{format_money(pocket_money)}", True, (34, 139, 34))
    
    # 2. Check if the image loaded successfully
    if coin_icon:
        # Calculate the total width of the icon + 10 pixels spacing + the text
        total_width = coin_icon.get_width() + 10 + money_text.get_width()
        
        # Figure out where to start drawing so the whole group is perfectly centered
        start_x = MIDDLE_CENTER_X - (total_width // 2)
        
        # Draw the coin on the left
        coin_rect = coin_icon.get_rect(midleft=(start_x, 160))
        window.blit(coin_icon, coin_rect)
        
        # Draw the text right next to it
        money_rect = money_text.get_rect(midleft=(coin_rect.right + 10, 160))
        window.blit(money_text, money_rect)
        
    else:
        # Fallback just in case the image goes missing
        money_rect = money_text.get_rect(center=(MIDDLE_CENTER_X, 160))
        window.blit(money_text, money_rect)


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