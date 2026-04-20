import pygame as pg
import json
import os
import time

pg.init()
pg.font.init()  

''' Tan Zhe Xi '''
## TZX_1. MINIGAME SYSTEM



## TZX_2. GEAR & DATA DESIGN



## TZX_3. ABILITY TO CLICK TO DEAL DAMAGE

class Monster: # Monster class
    def __init__(self, name, max_hp, color):
        self.name = name
        self.max_hp = max_hp
        self.hp = max_hp
        self.color = color
        self.rect = pg.Rect(300, 200, 200, 200)  # Monster position and size

    def take_damage(self, dmg):
        self.hp -= dmg
        if self.hp < 0:
            self.hp = 0

    def is_defeated(self):
        return self.hp <= 0

    def draw(self, surface):
        pg.draw.rect(surface, self.color, self.rect)
        # Draw HP bar
        hp_bar_width = int((self.hp / self.max_hp) * self.rect.width)
        pg.draw.rect(surface, (255,0,0), (self.rect.x, self.rect.y - 20, hp_bar_width, 10))
        # Draw monster name
        font = pg.font.SysFont(None, 30)
        text = font.render(f"{self.name} HP: {self.hp}/{self.max_hp}", True, (0,0,0))
        surface.blit(text, (self.rect.x, self.rect.y - 50))

# Initialize first monster
current_monster = Monster("Bread Monster", 50, (0,255,0))

# Damage per click
damage_per_click = 10

## TZX_4. ADJUSTING STATS ACCORDING TO PRESTIGE LEVELS




''' Eng Kai Hin '''
## EKH_1. BUTTON INTERACTION SYSTEM
class Main_button:
    def __init__(self, x, y, width, height, text, color, hover_color, callback=None):
        self.rect = pg.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.callback = callback
        self.font = pg.font.SysFont(None, 36)
        self.is_hovered = False

    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                if self.callback:
                    self.callback()
                return True
        return False

    def update(self):
        self.is_hovered = self.rect.collidepoint(pg.mouse.get_pos())

    def draw(self, screen):
        color = self.hover_color if self.is_hovered else self.color
        pg.draw.rect(screen, color, self.rect)
        pg.draw.rect(screen, (200, 200, 200), self.rect, 2)
        
        text_surf = self.font.render(self.text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

# ----- Pannel (Like a drawer system lah basically)-----
class PanelManager:
    def __init__(self, screen_width, screen_height):
        self.active_panel = None  # To set button's name
        self.panel_rect = pg.Rect(100, 100, 600, 400)  # Setting for pannel width and height
        self.panel_color = (50, 50, 50, 200)  # Setting a opaque color
        self.border_color = (200, 200, 200) # Setting for its border
        
    def toggle_panel(self, button_name):
        """Shows status when pannel changed"""
        if self.active_panel == button_name:
            self.active_panel = None  # Turn off the pannel when clicked again
        else:
            self.active_panel = button_name  # Display other button name if the other button was clicked
            
    def draw(self, screen):
        """Draw the clicked pannel"""
        if self.active_panel:
            # Creat a temporary surface to deal with transparancy
            panel_surface = pg.Surface((self.panel_rect.width, self.panel_rect.height))
            panel_surface.set_alpha(self.panel_color[3])  # Set transparency（200 = opaque）
            panel_surface.fill(self.panel_color[:3])  # Fill in color
            screen.blit(panel_surface, (self.panel_rect.x, self.panel_rect.y))
            
            # Draw border
            pg.draw.rect(screen, self.border_color, self.panel_rect, 3)
            
            # Display the button name on the pannel (It will add its function in the future)
            font = pg.font.SysFont(None, 48)
            text = font.render(f"{self.active_panel} Panel", True, (255, 255, 255))
            text_rect = text.get_rect(center=self.panel_rect.center)
            screen.blit(text, text_rect)

# ----- Active PanelManager -----
panel_manager = PanelManager(800, 600)

# ----- call out PanelManager function -----
def create_button_callback(button_name):
    def callback():
        panel_manager.toggle_panel(button_name)
    return callback

# middle
button_width = 130
button_height = 40
spacing = 10
start_x = (800 - (button_width * 5 + spacing * 4)) // 2
button_y = 550 

buttons = [
    Main_button(start_x + 0 * (button_width + spacing), button_y, button_width, button_height, "Upgrade", (100, 100, 100), (150, 150, 150), create_button_callback("Upgrade")),
    Main_button(start_x + 1 * (button_width + spacing), button_y, button_width, button_height, "Crafting", (100, 100, 100), (150, 150, 150), create_button_callback("Crafting")),
    Main_button(start_x + 2 * (button_width + spacing), button_y, button_width, button_height, "Raids", (100, 100, 100), (150, 150, 150), create_button_callback("Raids")),
    Main_button(start_x + 3 * (button_width + spacing), button_y, button_width, button_height, "Shop", (100, 100, 100), (150, 150, 150), create_button_callback("Shop")),
    Main_button(start_x + 4 * (button_width + spacing), button_y, button_width, button_height, "Prestige", (100, 100, 100), (150, 150, 150), create_button_callback("Prestige")),
]

## EKH_2. AFK SYSTEM

class AFKSystem:
    def __init__(self, save_file="afk_save.json"):
        self.save_file = save_file
        self.last_save_time = time.time()
        self.afk_income_rate = 1  # Gain 1 currency per a second
        
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
            
            
            # Calculate currency obtain after leaving the game
            afk_earnings = int(time_diff * self.afk_income_rate)
            
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
    afk_text = small_font.render("Your mom paid you $1 every second since you didn't destroy her taste buds", True, (100, 100, 100))
    window.blit(afk_text, (10, 50))

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
        continue_text = font_small.render("Click anywhere to continue", True, (255, 255, 255))
        
        title_rect = title_text.get_rect(center=(400, 200))
        reward_rect = reward_text.get_rect(center=(400, 280))
        continue_rect = continue_text.get_rect(center=(400, 360))
        
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

## EKH_3. SHOP SYSTEM



## EKH_4. CLEAN WHEN PRESTIGE SYSTEM




''' Chen Lik Shen '''
## CLS_1. GAME UI & SOUND EFFECT

# Setup for CLS_1
ui_font = pg.font.SysFont(None, 48)

## CLS_2. GAIN & LOST OF GEAR & CURRENCY SYSTEM

# Variables for CLS_2
pocket_money = 0

def update_economy(monster):
    global pocket_money
    if monster.is_defeated():
        pocket_money += 50
        return True # Signal that titan died
    return False



## CLS_3. CRAFTING SYSTEM



## CLS_4. SYSTEM TO ADD NEW GEAR, CHARACTER, AND RECIPES ACCORDING TO EACH PRESTIGE LEVELS




'''General'''

window = pg.display.set_mode((800,600)) # Adjust the window size from here by editing (x,y) value
pg.display.set_caption("Attack On Food Titan") # Rename the window by editing ("Name")

# Load AFK rewards and saved game data
afk_earnings, saved_monster_data, saved_money = afk_system.load_and_calculate_afk_rewards()

#Reload saved money, then sum up with AFK rewards
if saved_money > 0:
    pocket_money = saved_money

# Load AFK rewards screen
if afk_earnings > 0:
    pocket_money += afk_earnings
    show_afk_rewards(window, afk_earnings)
    
    # if status of monster was saved, then load it
    if saved_monster_data:
        current_monster = Monster(
            saved_monster_data["name"],
            saved_monster_data["max_hp"],
            tuple(saved_monster_data["color"])
        )
        current_monster.hp = saved_monster_data["hp"]

IsRunning = True
# Timer for AFK system
last_auto_save = time.time()
auto_save_interval = 5  # Save the game every 5 second

while IsRunning:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            # Save game data before exit it
            afk_system.save_game_data(
                pocket_money,
                current_monster.hp,
                current_monster.max_hp,
                current_monster.name,
                current_monster.color
            )
            IsRunning = False
            break
        elif event.type == pg.MOUSEBUTTONDOWN:
            if current_monster.rect.collidepoint(event.pos):
                current_monster.take_damage(damage_per_click)
                if current_monster.is_defeated():
                    update_economy(current_monster)
                    current_monster = Monster("Baguette Monster", 100, (0,0,255)) # Spawn new monster with higher HP
        
        for button in buttons:
            button.handle_event(event)

    # Auto save system for AFK
    current_time = time.time()
    if current_time - last_auto_save >= auto_save_interval:
        afk_system.save_game_data(
            pocket_money,
            current_monster.hp,
            current_monster.max_hp,
            current_monster.name,
            current_monster.color
        )
        afk_system.update_save_time()
        last_auto_save = current_time

    for button in buttons:
        button.update()

    window.fill((227,227,227)) # Adjust the window color from here by editing its RGB code
    current_monster.draw(window)
    draw_ui(window)
    
    for button in buttons:
        button.draw(window)

    #Draw button if actived
    panel_manager.draw(window)
    
    pg.display.update()

pg.quit()