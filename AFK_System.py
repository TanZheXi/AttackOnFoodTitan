import pygame as pg
import json
import os
import time

pg.init()
pg.font.init()  

class AFKSystem:
    def __init__(self, save_file="afk_save.json"):
        self.save_file = save_file
        self.last_save_time = time.time()
        self.afk_income_rate = 1 / 3600  # Gain 1 currency per every hour
        self.max_afk_earnings = 100      # Setting $100 as limit for AFK earns
        
    def save_game_data(self, pocket_money, monster_hp, monster_max_hp, monster_name, monster_color, progression_index, inventory_items=None, shop_items_state=None):
        """Save full game data including inventory and shop states"""
        # Prepare shop items state (which items are sold out)
        shop_state = []
        if shop_items_state:
            for item in shop_items_state:
                if isinstance(item, dict):
                    shop_state.append({
                        "name": item.get("name", "Unknown"),
                        "sold_out": item.get("sold_out", False)
                    })
                else:
                    shop_state.append({
                        "name": item.name,
                        "sold_out": item.sold_out
                    })

        save_data = {
            "pocket_money": pocket_money,
            "last_time": self.last_save_time,
            "monster": {
                "name": monster_name,
                "hp": monster_hp,
                "max_hp": monster_max_hp,
                "color": monster_color
            },
            "progression_index": progression_index,
            "inventory": inventory_items if inventory_items else [],
            "shop_items": shop_state
        }
        try:
            with open(self.save_file, 'w') as f:
                json.dump(save_data, f)
            print(f"[SAVE] Game saved. Money: {pocket_money}, Progress: {progression_index}, Items: {len(inventory_items) if inventory_items else 0}")
        except Exception as e:
            print(f"Save failed: {e}")
    
    def load_and_calculate_afk_rewards(self):
        """Load saved data and calculate AFK rewards"""
        if not os.path.exists(self.save_file):
            return 0, None, 0, 1, [], []
        
        try:
            with open(self.save_file, 'r') as f:
                save_data = json.load(f)
            
            last_time = save_data.get("last_time", time.time())
            saved_money = save_data.get("pocket_money", 0)
            current_time = time.time()
            time_diff = current_time - last_time
            
            raw_earnings = int(time_diff * self.afk_income_rate)
            afk_earnings = min(raw_earnings, self.max_afk_earnings)
            
            monster_data = save_data.get("monster", None)
            progression_index = save_data.get("progression_index", 1)
            inventory = save_data.get("inventory", [])
            shop_state = save_data.get("shop_items", [])
            
            return afk_earnings, monster_data, saved_money, progression_index, inventory, shop_state
            
        except Exception as e:
            print(f"Loading failed: {e}")
            return 0, None, 0, 1, [], []
    
    def update_save_time(self):
        """Update last save time"""
        self.last_save_time = time.time()

# Initial AFK system
afk_system = AFKSystem()

def draw_AFK_ui(window):
    # Show AFK stats
    small_font = pg.font.SysFont(None, 24)
    afk_text_line_1 = small_font.render("*Your mom paid you $1/h since you didn't destroy her taste buds,", True, (100, 100, 100))
    afk_text_line_2 = small_font.render(" but she won't paid you when you reached $100 since you are lazy.", True, (100, 100, 100))
    window.blit(afk_text_line_1, (10, 5))
    window.blit(afk_text_line_2, (10, 25))

def show_afk_rewards(window, afk_earnings):
    """AFK rewards screen"""
    if afk_earnings > 0:
        overlay = pg.Surface((800, 600))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        window.blit(overlay, (0, 0))
        
        font_big = pg.font.SysFont(None, 48)
        font_small = pg.font.SysFont(None, 32)
        
        title_text = font_big.render("Welcome Back!", True, (255, 255, 0))
        reward_text = font_small.render(f"You earned ${afk_earnings} while away!", True, (0, 255, 0))

        if afk_earnings >= 100:
            limit_text = font_small.render("You've reached the $100 AFK limit", True, (255, 255, 0))
            limit_rect = limit_text.get_rect(center=(400, 320))
            window.blit(limit_text, limit_rect)

        continue_text = font_small.render("Click anywhere to continue", True, (255, 255, 255))
        continue_rect = continue_text.get_rect(center=(400, 360))
        
        title_rect = title_text.get_rect(center=(400, 200))
        reward_rect = reward_text.get_rect(center=(400, 280))
        
        window.blit(title_text, title_rect)
        window.blit(reward_text, reward_rect)
        window.blit(continue_text, continue_rect)
        
        pg.display.update()
        
        waiting = True
        while waiting:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    exit()
                elif event.type == pg.MOUSEBUTTONDOWN:
                    waiting = False