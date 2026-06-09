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

ui_font = pg.font.SysFont(None, 48)
scrap_font = pg.font.SysFont(None, 36)

MIDDLE_CENTER_X = 575

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
    """更新经济，返回获得的金额"""
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
    
    # 返回获得的金额，用于显示飘字提示
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
    """绘制UI，包括金钱、星星和金钱获得提示"""
    global michelin_stars
    
    # 获取 boost 状态（从 main.py 设置）
    is_boost_active = getattr(draw_ui, 'is_boost_active', lambda: False)()
    
    # 绘制金钱时，如果 boost 激活则添加特效
    if is_boost_active:
        # 闪烁效果：每0.5秒切换颜色
        flash = (pg.time.get_ticks() // 500) % 2
        if flash == 0:
            money_color = (255, 215, 0)  # 金色
        else:
            money_color = (255, 180, 50)  # 橙金色
        # 添加发光效果（绘制阴影）
        shadow_text = ui_font.render(f"{format_money(pocket_money)}", True, (255, 200, 0))
        shadow_rect = shadow_text.get_rect(center=(MIDDLE_CENTER_X + 2, 162))
        window.blit(shadow_text, shadow_rect)
    else:
        money_color = (34, 139, 34)  # 绿色
    
    money_text = ui_font.render(f"{format_money(pocket_money)}", True, money_color)
    
    if coin_icon:
        total_width = coin_icon.get_width() + 10 + money_text.get_width()
        start_x = MIDDLE_CENTER_X - (total_width // 2)
        coin_rect = coin_icon.get_rect(midleft=(start_x, 160))
        window.blit(coin_icon, coin_rect)
        money_rect = money_text.get_rect(midleft=(coin_rect.right + 10, 160))
        window.blit(money_text, money_rect)
    else:
        money_rect = money_text.get_rect(center=(MIDDLE_CENTER_X, 160))
        window.blit(money_text, money_rect)

    if michelin_stars > 0:
        multiplier_display = get_prestige_multiplier()
        stars_text = scrap_font.render(f"Michelin Stars: {michelin_stars} (x{multiplier_display:.1f} DMG)", True, (255, 215, 0))
        stars_rect = stars_text.get_rect(center=(MIDDLE_CENTER_X, 200))
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