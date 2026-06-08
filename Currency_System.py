import pygame as pg
import random 
import Equipment_System

pg.init()
pg.font.init()

_prestige_callbacks = []

def register_prestige_callback(callback):
    _prestige_callbacks.append(callback)

pocket_money = 0
current_stage = 1
bottle_caps = 0

ui_font = pg.font.SysFont(None, 48)
scrap_font = pg.font.SysFont(None, 36)
bottle_font = pg.font.SysFont(None, 48)

MIDDLE_CENTER_X = 575

try:
    raw_coin_image = pg.image.load("Icon/pocket_money.png")
    coin_icon = pg.transform.scale(raw_coin_image, (40, 40))
except Exception as e:
    print(f"[UI WARN] Could not load pocket_money.png: {e}")
    coin_icon = None

def set_bottle_caps(amount):
    global bottle_caps
    bottle_caps = amount

def get_bottle_caps():
    return bottle_caps

def add_bottle_caps(amount):
    global bottle_caps
    bottle_caps += amount
    print(f"[CURRENCY] Added {amount} Bottle Caps. Total: {bottle_caps}")

def spend_money(amount):
    global pocket_money
    if pocket_money >= amount:
        pocket_money -= amount
        print(f"Purchase successful! Remaining money: ${pocket_money}")
        return True
    else:
        print(f"Not enough money! You need ${amount - pocket_money} more.")
    return False

def update_economy(monster_value, progression_index):
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
    if amount < 1000:
        return f"{int(amount)}"

    # You can add as many as you want here manually. It's super easy to read.
    suffixes = [
        "", "K", "M", "B", "T", "Qa", "Qi",   # The Classics     
    ]
    
    magnitude = 0
    temp_amount = float(amount)
    while temp_amount >= 1000 and magnitude < len(suffixes) - 1:
        magnitude += 1
        temp_amount /= 1000.0
    if temp_amount >= 1000 and magnitude == len(suffixes) - 1:
        return f"{float(amount):.2e}"

    # 5. Return the formatted number
    return f"{temp_amount:.2f}{suffixes[magnitude]}"
        
def draw_ui(window):
    global michelin_stars, bottle_caps
    money_text = ui_font.render(f"{format_money(pocket_money)}", True, (34, 139, 34))
    
    if coin_icon:
        total_width = coin_icon.get_width() + 10 + money_text.get_width()
        start_x = MIDDLE_CENTER_X - (total_width // 2)
        coin_rect = coin_icon.get_rect(midleft=(start_x, 160))
        window.blit(coin_icon, coin_rect)
        money_rect = money_text.get_rect(midleft=(coin_rect.right + 10, 160))
        window.blit(money_text, money_rect)
        
        caps_text = bottle_font.render(f"BC{bottle_caps}", True, (200, 180, 100))
        caps_rect = caps_text.get_rect(center=(MIDDLE_CENTER_X, 200))
        window.blit(caps_text, caps_rect)
    else:
        money_rect = money_text.get_rect(center=(MIDDLE_CENTER_X, 160))
        window.blit(money_text, money_rect)
        caps_text = bottle_font.render(f"BC{bottle_caps}", True, (200, 180, 100))
        caps_rect = caps_text.get_rect(center=(MIDDLE_CENTER_X, 200))
        window.blit(caps_text, caps_rect)

    if michelin_stars > 0:
        multiplier_display = get_prestige_multiplier()
        stars_text = scrap_font.render(f"Michelin Stars: {michelin_stars} (x{multiplier_display:.1f} DMG)", True, (255, 215, 0))
        stars_rect = stars_text.get_rect(center=(MIDDLE_CENTER_X, 235))
        window.blit(stars_text, stars_rect)

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