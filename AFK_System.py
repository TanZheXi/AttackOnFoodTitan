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
        self.max_afk_earnings = 100      #Setting $100 as limit for AFK earns
        
        
    def save_game_data(self, pocket_money, monster_hp, monster_max_hp, monster_name, monster_color):
        """Save game date to json file"""
        save_data = {
            "pocket_money": pocket_money,
            "last_time": self.last_save_time,
            "monster": {
                "name": monster_name,
                "hp": monster_hp,
                "max_hp": monster_max_hp,
                "color": monster_color
            }
        }
        try:
            with open(self.save_file, 'w') as f:
                json.dump(save_data, f)
        except Exception as e:
            print(f"Save failed: {e}")
    
    def load_and_calculate_afk_rewards(self):
        """Load saved data and calculate AFK rewards"""
        if not os.path.exists(self.save_file):
            return 0, None, 0 #Return the value of (AFK currency, monster stats, saved currency)
        
        try:
            with open(self.save_file, 'r') as f:
                save_data = json.load(f)
            
            last_time = save_data.get("last_time", time.time())
            saved_money = save_data.get("pocket_money", 0)
            current_time = time.time()
            time_diff = current_time - last_time
            
            
            # Calculate currency obtain after leaving the game (With $1 per hour, and a $100 limit for it)
            raw_earnings = int(time_diff * self.afk_income_rate)
            afk_earnings = min(raw_earnings, self.max_afk_earnings) #Setting the limitation
            
            # Get and load monster status
            monster_data = save_data.get("monster", None)
            
            return afk_earnings, monster_data, saved_money
            
        except Exception as e:
            print(f"Loading failed, please try again: {e}")
            return 0, None, 0
    
    def update_save_time(self):
        """Update last save time"""
        self.last_save_time = time.time()

# Initial AFK system
afk_system = AFKSystem()

def draw_ui(window):
    """Logic for drawing the money on screen"""
    money_text = ui_font.render(f"Pocket Money: ${pocket_money}", True, (34, 139, 34))
    window.blit(money_text, (10, 10))
    
    # Show AFk stats
    small_font = pg.font.SysFont(None, 24)
    afk_text_line_1 = small_font.render("*Your mom paid you $1 every hour since you didn't destroy her taste buds,", True, (100, 100, 100))
    afk_text_line_2 = small_font.render(" but she will won't paid you when you reached $100 since you are lazy.", True, (100, 100, 100))
    window.blit(afk_text_line_1, (10, 50))
    window.blit(afk_text_line_2, (10, 75))

def show_afk_rewards(window, afk_earnings):
    """AFK rewards screen"""
    if afk_earnings > 0:
        # Creat a surface
        overlay = pg.Surface((800, 600))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        window.blit(overlay, (0, 0))
        
        # Show AFK reward 
        font_big = pg.font.SysFont(None, 48)
        font_small = pg.font.SysFont(None, 32)
        
        title_text = font_big.render("Welcome Back!", True, (255, 255, 0))
        reward_text = font_small.render(f"You earned ${afk_earnings} while away!", True, (0, 255, 0))

        if afk_earnings >= 100:
            limit_text = font_small.render("You've reached the $100 AFK limit"), True, (255,255,0)
            limit_rect = limit_text.get_rect(center=(400, 320))
            window.blit(limit_text, limit_rect)
            continue_text = font_small.render("Click anywhere to continue", True, (255,255,255))
            continue_rect = continue_text.get_rect(center=(400, 360))
        else:
            continue_text = font_small.render("Click anywhere to continue", True, (255,255,255))
            continue_rect = continue_text.get_rect(center=(400, 360))
        
        title_rect = title_text.get_rect(center=(400, 200))
        reward_rect = reward_text.get_rect(center=(400, 280))
        
        window.blit(title_text, title_rect)
        window.blit(reward_text, reward_rect)
        window.blit(continue_text, continue_rect)
        
        pg.display.update()
        
        # Continue after player click the screen
        waiting = True
        while waiting:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    exit()
                elif event.type == pg.MOUSEBUTTONDOWN:
                    waiting = False