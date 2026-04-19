import pygame as pg

pg.init()
pg.font.init()  

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

'''General'''

window = pg.display.set_mode((800,600))
pg.display.set_caption("Attack On Food Titan")
IsRunning = True

while IsRunning:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            IsRunning = False
            break
        
        for button in buttons:
            button.handle_event(event)

    for button in buttons:
        button.update()

    window.fill((227,227,227))
    
    for button in buttons:
        button.draw(window)
    
    # Draw button if actived
    panel_manager.draw(window)
    
    pg.display.update()

pg.quit()