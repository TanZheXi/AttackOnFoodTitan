import pygame as pg
from Shop_System import ShopSystem
from Inventory_System import InventorySystem
import Currency_System

pg.init()
pg.font.init()  

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
        panel_width = 650
        panel_height = 450
        panel_x = (screen_width - panel_width) // 2
        panel_y = (screen_height - panel_height) // 2
        self.panel_rect = pg.Rect(panel_x, panel_y, panel_width, panel_height)  # Setting for pannel width and height
        self.panel_color = (50, 50, 50, 220)  # Setting a opaque color
        self.border_color = (200, 200, 200) # Setting for its border
        self.shop_system = None  # will be created when needed
        self.inventory_system = None  # will be created when needed
        self.global_pocket_money = Currency_System.pocket_money
        self.shop_state_loaded = False  # Prevent from repeat loading
        
        # Store data to be recovered
        self.pending_inventory = []
        self.pending_shop_state = []
        self.pending_money = None

    def load_saved_data(self, pocket_money, inventory_items, shop_state):
        """Load saved data into systems (stores pending data if systems not yet created)"""
        self.global_pocket_money = pocket_money
        
        # Store data to be recovered
        self.pending_inventory = inventory_items if inventory_items else []
        self.pending_shop_state = shop_state if shop_state else []
        self.pending_money = pocket_money
        
        # Load if inventory was activated
        if self.inventory_system and self.pending_inventory:
            self.inventory_system.restore_inventory(self.pending_inventory)
            print(f"[LOAD] Inventory restored immediately: {len(self.pending_inventory)} items")
        
        # Load if shop was activated
        if self.shop_system and self.pending_shop_state:
            self.shop_system.restore_shop_state(self.pending_shop_state)
            print(f"[LOAD] Shop state restored immediately: {len(self.pending_shop_state)} items")
        
        print(f"[LOAD] Data loaded: Money={pocket_money}, Pending Inventory={len(self.pending_inventory)} items")

    def get_save_data(self):
        """Get current data for saving"""
        inventory_items = []
        if self.inventory_system:
            inventory_items = self.inventory_system.get_inventory_state()
        
        shop_state = []
        if self.shop_system:
            shop_state = self.shop_system.get_shop_state()
        
        return inventory_items, shop_state
        
    def toggle_panel(self, button_name):
        """Shows status when pannel changed"""
        if self.active_panel == button_name:
            self.active_panel = None  # Turn off the pannel when clicked again
        else:
            self.active_panel = button_name  # Display other button name if the other button was clicked
    
    def handle_event(self, event):
        if self.active_panel == "Shop" and self.shop_system:
            self.shop_system.handle_event(event, self.add_to_inventory)
            self.global_pocket_money = Currency_System.pocket_money
        elif self.active_panel == "Inventory" and self.inventory_system:
            self.inventory_system.handle_event(event)

    def add_to_inventory(self, item_name):
        """Adding item into inventory"""
        if self.inventory_system is None:
            inv_x = self.panel_rect.x + 15
            inv_y = self.panel_rect.y + 15
            inv_width = self.panel_rect.width - 30
            inv_height = self.panel_rect.height - 30
            self.inventory_system = InventorySystem(inv_x, inv_y, inv_width, inv_height)
            
            # Restore pending inventory data immediately after activated
            if self.pending_inventory:
                self.inventory_system.restore_inventory(self.pending_inventory)
                print(f"[RESTORE] Inventory restored on creation: {len(self.pending_inventory)} items")
            
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
                    shop_x = self.panel_rect.x + 15
                    shop_y = self.panel_rect.y + 15
                    shop_width = self.panel_rect.width - 30
                    shop_height = self.panel_rect.height - 30
                    self.shop_system = ShopSystem(shop_x, shop_y, shop_width, shop_height)
                    
                    # Restore pending shop data immediately after activated
                    if self.pending_shop_state:
                        self.shop_system.restore_shop_state(self.pending_shop_state)
                        print(f"[RESTORE] Shop state restored on creation: {len(self.pending_shop_state)} items")
                    
                self.shop_system.update()
                self.shop_system.draw(screen)
            elif self.active_panel == "Inventory":
                if self.inventory_system is None:
                    inv_x = self.panel_rect.x + 15
                    inv_y = self.panel_rect.y + 15
                    inv_width = self.panel_rect.width - 30
                    inv_height = self.panel_rect.height - 30
                    self.inventory_system = InventorySystem(inv_x, inv_y, inv_width, inv_height)
                    
                    # Restore pending inventory data immediately after activated
                    if self.pending_inventory:
                        self.inventory_system.restore_inventory(self.pending_inventory)
                        print(f"[RESTORE] Inventory restored on creation: {len(self.pending_inventory)} items")
                    
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
button_width = 130
button_height = 40
spacing = 10
total_width = button_width * 5 + spacing * 4
start_x = (800 - total_width) // 2
button_y = 550 

buttons = [
    Main_button(start_x + 0 * (button_width + spacing), button_y, button_width, button_height, "Upgrade", (80, 80, 100), (120, 120, 140), create_button_callback("Upgrade")),
    Main_button(start_x + 1 * (button_width + spacing), button_y, button_width, button_height, "Crafting", (80, 80, 100), (120, 120, 140), create_button_callback("Crafting")),
    Main_button(start_x + 2 * (button_width + spacing), button_y, button_width, button_height, "Raids", (80, 80, 100), (120, 120, 140), create_button_callback("Raids")),
    Main_button(start_x + 3 * (button_width + spacing), button_y, button_width, button_height, "Shop", (80, 80, 100), (120, 120, 140), create_button_callback("Shop")),
    Main_button(start_x + 4 * (button_width + spacing), button_y, button_width, button_height, "Prestige", (80, 80, 100), (120, 120, 140), create_button_callback("Prestige")),
    Main_button(740, 50, 40, 40, "Inv", (80, 80, 100), (120, 120, 140), create_button_callback("Inventory")),  # Added a button for Inventory
]