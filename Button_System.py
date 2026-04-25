import pygame as pg
from Shop_System import ShopSystem
from Inventory_System import InventorySystem

pg.init()
pg.font.init()  

# Global pocket money (暂时先把Pocket_money设置成global且数量为$300，以方便测试)
POCKET_MONEY = 300

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
        self.panel_rect = pg.Rect(100, 100, 800, 450)  # Setting for pannel width and height (稍微加宽以容纳商店右侧信息面板)
        self.panel_color = (50, 50, 50, 220)  # Setting a opaque color
        self.border_color = (200, 200, 200) # Setting for its border
        self.shop_system = None  # will be created when needed
        self.inventory_system = None  # will be created when needed
        self.global_pocket_money = POCKET_MONEY  # 全局Pocket_money
        
    def toggle_panel(self, button_name):
        """Shows status when pannel changed"""
        if self.active_panel == button_name:
            self.active_panel = None  # Turn off the pannel when clicked again
        else:
            self.active_panel = button_name  # Display other button name if the other button was clicked
    
    def handle_event(self, event):
        if self.active_panel == "Shop" and self.shop_system:
            self.global_pocket_money = self.shop_system.handle_event(
                event, self.global_pocket_money, self.add_to_inventory
            )
        elif self.active_panel == "Inventory" and self.inventory_system:
            self.inventory_system.handle_event(event)

    def add_to_inventory(self, item_name):
        """添加物品到背包（回调函数）"""
        if self.inventory_system is None:
            inv_x = self.panel_rect.x + 20
            inv_y = self.panel_rect.y + 20
            inv_width = self.panel_rect.width - 40
            inv_height = self.panel_rect.height - 40
            self.inventory_system = InventorySystem(inv_x, inv_y, inv_width, inv_height)
        self.inventory_system.add_item(item_name)

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
            if self.active_panel == "Shop":
                if self.shop_system is None:
                    shop_x = self.panel_rect.x + 20
                    shop_y = self.panel_rect.y + 20
                    shop_width = self.panel_rect.width - 40
                    shop_height = self.panel_rect.height - 40
                    self.shop_system = ShopSystem(shop_x, shop_y, shop_width, shop_height)
                self.shop_system.update()
                self.shop_system.draw(screen)
            elif self.active_panel == "Inventory":
                if self.inventory_system is None:
                    inv_x = self.panel_rect.x + 20
                    inv_y = self.panel_rect.y + 20
                    inv_width = self.panel_rect.width - 40
                    inv_height = self.panel_rect.height - 40
                    self.inventory_system = InventorySystem(inv_x, inv_y, inv_width, inv_height)
                self.inventory_system.draw(screen)
            else:
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
button_width = 110
button_height = 40
spacing = 8
total_width = button_width * 6 + spacing * 5
start_x = (800 - total_width) // 2
button_y = 540 

buttons = [
    Main_button(start_x + 0 * (button_width + spacing), button_y, button_width, button_height, "Upgrade", (80, 80, 100), (120, 120, 140), create_button_callback("Upgrade")),
    Main_button(start_x + 1 * (button_width + spacing), button_y, button_width, button_height, "Crafting", (80, 80, 100), (120, 120, 140), create_button_callback("Crafting")),
    Main_button(start_x + 2 * (button_width + spacing), button_y, button_width, button_height, "Raids", (80, 80, 100), (120, 120, 140), create_button_callback("Raids")),
    Main_button(start_x + 3 * (button_width + spacing), button_y, button_width, button_height, "Shop", (80, 80, 100), (120, 120, 140), create_button_callback("Shop")),
    Main_button(start_x + 4 * (button_width + spacing), button_y, button_width, button_height, "Prestige", (80, 80, 100), (120, 120, 140), create_button_callback("Prestige")),
    Main_button(start_x + 5 * (button_width + spacing), button_y, button_width, button_height, "Inventory", (80, 80, 100), (120, 120, 140), create_button_callback("Inventory")),  # Added a button for Inventory
]