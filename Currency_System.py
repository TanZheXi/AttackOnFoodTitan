import pygame as pg
import random 
import Equipment_System
import sys

pg.init()
pg.font.init()

_prestige_callbacks = []

def register_prestige_callback(callback):
    _prestige_callbacks.append(callback)

pocket_money = 1
current_stage = 1

ui_font = pg.font.SysFont(None, 48)
scrap_font = pg.font.SysFont(None, 36)

MIDDLE_CENTER_X = 575

# ========== BOOST STATE MANAGEMENT ==========
_boost_active = False

def set_boost_active(active):
    """Set up boost active state"""
    global _boost_active
    _boost_active = active

def is_boost_active():
    """Check if boost is active"""
    return _boost_active
# ============================================

# Load coin icon
try:
    raw_coin_image = pg.image.load("Icon/pocket_money.png")
    coin_icon = pg.transform.scale(raw_coin_image, (40, 40))
except Exception as e:
    print(f"[UI WARN] Could not load pocket_money.png: {e}")
    coin_icon = None

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
    """Update currency and return the amount earned"""
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
        
    if is_boost_active():
        money_earned = int(money_earned * 2)
        
    pocket_money += money_earned
    
    return money_earned

def format_money(amount):
    if amount < 1000:
        return f"{int(amount)}"

    suffixes = ["", "K", "M", "B", "T", "Qa", "Qi"]
    
    magnitude = 0
    temp_amount = float(amount)
    while temp_amount >= 1000 and magnitude < len(suffixes) - 1:
        magnitude += 1
        temp_amount /= 1000.0
    if temp_amount >= 1000 and magnitude == len(suffixes) - 1:
        return f"{float(amount):.2e}"
    return f"{temp_amount:.2f}{suffixes[magnitude]}"
        
def draw_ui(window):
    global michelin_stars
    
    boost_active = is_boost_active()

    money_color = (34, 139, 34)
    
    money_str = f"{format_money(pocket_money)}"
    money_text_shadow = ui_font.render(money_str, True, (0, 0, 0))
    money_text = ui_font.render(money_str, True, money_color)
    
    if coin_icon:
        total_width = coin_icon.get_width() + 10 + money_text.get_width()
        start_x = MIDDLE_CENTER_X - (total_width // 2)
        coin_rect = coin_icon.get_rect(midleft=(start_x, 160))
        window.blit(coin_icon, coin_rect)
        
        shadow_rect = money_text_shadow.get_rect(midleft=(coin_rect.right + 10 + 2, 160 + 2))
        window.blit(money_text_shadow, shadow_rect)
        
        money_rect = money_text.get_rect(midleft=(coin_rect.right + 10, 160))
        window.blit(money_text, money_rect)
    else:
        shadow_rect = money_text_shadow.get_rect(center=(MIDDLE_CENTER_X + 2, 160 + 2))
        window.blit(money_text_shadow, shadow_rect)
        
        money_rect = money_text.get_rect(center=(MIDDLE_CENTER_X, 160))
        window.blit(money_text, money_rect)

michelin_stars = 0 
prestige_count = 0

def get_advanced_start(current_stage):
    return max(1, current_stage // 2)

def get_prestige_multiplier():
    return 1.0 + (michelin_stars * 0.10)

# ===== PRESTIGE REQUIREMENTS SYSTEM =====
def get_prestige_requirements():
    """
    Returns the stage requirement for each prestige level.
    Each prestige requires higher stage to unlock.
    """
    return {
        1: 10,    # First prestige: Stage 10
        2: 25,    # Second prestige: Stage 25
        3: 50,    # Third prestige: Stage 50
        4: 100,   # Fourth prestige: Stage 100
        5: 200,   # Fifth prestige: Stage 200
        6: 350,   # Sixth prestige: Stage 350
        7: 500,   # Seventh prestige: Stage 500
        8: 750,   # Eighth prestige: Stage 750
        9: 1000,  # Ninth prestige: Stage 1000
        10: 1500, # Tenth prestige: Stage 1500
    }

def get_next_prestige_requirement(current_stars):
   # Get the stage requirement for the next prestige.
   # Returns None if max prestige reached.
    requirements = get_prestige_requirements()
    next_level = current_stars + 1
    return requirements.get(next_level, None)

def calculate_stars_earned(current_stage, current_stars):
    # Calculate how many stars can be earned at current stage.
    # Returns (stars_to_earn, requirement_met)
    requirements = get_prestige_requirements()
    next_requirement = get_next_prestige_requirement(current_stars)
    
    if next_requirement is None:
        return 0, False  # Max prestige reached
    
    if current_stage >= next_requirement:
        return 1, True  # Can earn 1 star
    else:
        return 0, False

def calculate_prestige_rewards(current_stage):
    if current_stage < 10:
        return 0
    return 1 + ((current_stage - 10) // 5)

def trigger_prestige(monster_manager):
    # Execute prestige with increasing requirements.
    # Returns True if successful, False otherwise.
    global pocket_money, michelin_stars, prestige_count
    
    # Get current state
    current_stage = monster_manager.stage
    current_stars = michelin_stars
    
    # Check if can prestige
    next_requirement = get_next_prestige_requirement(current_stars)
    if next_requirement is None:
        print(f"[PRESTIGE] MAX PRESTIGE REACHED! You have {current_stars} stars!")
        return False
    
    if current_stage < next_requirement:
        print(f"[PRESTIGE] Need Stage {next_requirement} to prestige! (Current: Stage {current_stage})")
        return False
    
    # Calculate stars to earn (always 1 per prestige)
    stars_to_gain = 1
    
    # Execute prestige callbacks (reset systems)
    for callback in _prestige_callbacks:
        callback()
    
    # Apply prestige rewards
    michelin_stars += stars_to_gain
    prestige_count += 1
    
    # Reset everything to start
    pocket_money = 100  # Give some starting money (scales with stars)
    
    # Reset monster to Stage 1
    monster_manager.stage = 1
    monster_manager.progression_index = 0
    monster_manager.current_monster = monster_manager.spawn_monster()
    
    # Reset player upgrade system
    try:
        import Button_System
        if Button_System.panel_manager and Button_System.panel_manager.player_upgrade_system:
            upgrade_system = Button_System.panel_manager.player_upgrade_system
            upgrade_system.level = 0
            upgrade_system.current_cost = 20
            Equipment_System.base_damage = 1
            
            # Reset ability unlocks
            upgrade_system.spicy_unlocked = False
            upgrade_system.crispy_unlocked = False
            upgrade_system.spicy_level = 0
            upgrade_system.crispy_level = 0
            upgrade_system.spicy_damage_boost = 0.0
            upgrade_system.crispy_crit_damage = 0.0
            upgrade_system.crispy_crit_chance = 0.0
            
            # Reset mana system
            if hasattr(upgrade_system, 'mana_system'):
                upgrade_system.mana_system.current_mana = upgrade_system.mana_system.max_mana
    except Exception as e:
        print(f"[PRESTIGE] Error resetting upgrade system: {e}")
    
    # Reset pet system (unequip all pets)
    try:
        if Button_System.panel_manager and Button_System.panel_manager.pet_system:
            Button_System.panel_manager.pet_system.reset_on_prestige()
    except Exception as e:
        print(f"[PRESTIGE] Error resetting pet system: {e}")
    
    # Reset companions
    try:
        if Button_System.panel_manager and Button_System.panel_manager.player_upgrade_system:
            for comp in Button_System.panel_manager.player_upgrade_system.companions:
                comp.level = 0
                comp.current_cost = comp.base_cost
    except Exception as e:
        print(f"[PRESTIGE] Error resetting companions: {e}")
    
    # Print prestige info
    print(f"[PRESTIGE] ★ PRESTIGE COMPLETE! ★")
    print(f"[PRESTIGE] Earned {stars_to_gain} Michelin Star! Total: {michelin_stars}")
    next_req = get_next_prestige_requirement(michelin_stars)
    print(f"[PRESTIGE] Next Prestige Requirement: Stage {next_req if next_req else 'MAX REACHED'}")
    print(f"[PRESTIGE] Starting fresh from Stage 1 with ${pocket_money}")
    print(f"[PRESTIGE] Damage Multiplier: x{get_prestige_multiplier():.1f}")
    
    return True

def get_prestige_progress(current_stage, current_stars):
    # Get progress towards next prestige as a percentage.
    # Returns (progress_percentage, next_requirement)
    next_requirement = get_next_prestige_requirement(current_stars)
    if next_requirement is None:
        return 100, None  # Max prestige reached
    
    progress = min(100, (current_stage / next_requirement) * 100)
    return progress, next_requirement