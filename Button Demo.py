import pygame as pg

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

class Button:
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

# ----- (add 5 button)-----

def button1_callback():
    print("1")

def button2_callback():
    print("2")

def button3_callback():
    print("3")

def button4_callback():
    print("4")

def button5_callback():
    print("5")

# middle
button_width = 130
button_height = 40
spacing = 10
start_x = (800 - (button_width * 5 + spacing * 4)) // 2
button_y = 550 

buttons = [
    Button(start_x + 0 * (button_width + spacing), button_y, button_width, button_height, "Upgrade", (100, 100, 100), (150, 150, 150), button1_callback),
    Button(start_x + 1 * (button_width + spacing), button_y, button_width, button_height, "Crafting", (100, 100, 100), (150, 150, 150), button2_callback),
    Button(start_x + 2 * (button_width + spacing), button_y, button_width, button_height, "Raids", (100, 100, 100), (150, 150, 150), button3_callback),
    Button(start_x + 3 * (button_width + spacing), button_y, button_width, button_height, "Shop", (100, 100, 100), (150, 150, 150), button4_callback),
    Button(start_x + 4 * (button_width + spacing), button_y, button_width, button_height, "Prestige", (100, 100, 100), (150, 150, 150), button5_callback),
]

## EKH_2. AFK SYSTEM



## EKH_3. SHOP SYSTEM



## EKH_4. CLEAR WHEN PRESTIGE SYSTEM




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

def draw_ui(window):
    """Logic for drawing the money on screen"""
    money_text = ui_font.render(f"Pocket Money: ${pocket_money}", True, (34, 139, 34))
    window.blit(money_text, (10, 10))

## CLS_3. CRAFTING SYSTEM



## CLS_4. SYSTEM TO ADD NEW GEAR, CHARACTER, AND RECIPES ACCORDING TO EACH PRESTIGE LEVELS




'''General'''

window = pg.display.set_mode((800,600)) # Adjust the window size from here by editing (x,y) value
pg.display.set_caption("Attack On Food Titan") # Rename the window by editing ("Name")
IsRunning = True
while IsRunning:
    for event in pg.event.get():
        if event.type == pg.QUIT:
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

    for button in buttons:
        button.update()

    window.fill((227,227,227)) # Adjust the window color from here by editing its RGB code
    current_monster.draw(window)
    draw_ui(window)
    
    for button in buttons:
        button.draw(window)
    
    pg.display.update()

pg.quit()





'''
References list

#1. ABILITY TO CLICK TO DEAL DAMAGE (line 17 - line 47)
Source code: Copilot
Link: None

#2. Button system (line 57 - line 116)
Source code: Deepseek
Link: None

Example:
# [Name of the code] (From line x to line x)
#Source code: (Creater of the sources - Platform)
#Link: the link to your reference sources

'''