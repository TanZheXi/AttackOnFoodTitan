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
        self.font = pg.font.SysFont(None, 24)
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


# ----- Guide System -----
class GuideSystem:
    def __init__(self, x, y, width, height):
        self.rect = pg.Rect(x, y, width, height)
        self.font_title = pg.font.SysFont(None, 28, bold=True)
        self.font_text = pg.font.SysFont(None, 18)
        self.font_small = pg.font.SysFont(None, 16)
        self.visible = False
        
        # Guide content (can be expanded in future updates)
        self.guide_lines = [
            "=== GAME GUIDE ===",
            "",
            "[CONTROLS]",
            "Click on Monster - Deal damage",
            "G Key - Gain a test item (Mythic Pan)",
            "E Key - Equip weapon",
            "U Key - Unequip weapon",
            "C Key - Craft Golden Spatula",
            "",
            "[SHOP]",
            "Click Shop button to open shop",
            "Hover over items to see details",
            "Click item to purchase",
            "",
            "[INVENTORY]",
            "Click Inv button to open inventory",
            "Hover over items to see description",
            "Scroll mouse wheel to scroll",
            "",
            "[AFK SYSTEM]",
            "Earn $1 per hour while offline",
            "Max AFK earnings: $100",
            "",
            "[GEAR SYSTEM]",
            "Equip gear to increase damage",
            "Higher rarity = higher multiplier",
            "Craft items using scraps"
        ]

    def toggle(self):
        """Toggle the guide panel"""
        self.visible = not self.visible

    def draw(self, screen):
        if not self.visible:
            return
        
        # Draw semi-transparent background
        overlay = pg.Surface((self.rect.width, self.rect.height))
        overlay.set_alpha(230)
        overlay.fill((30, 30, 40))
        screen.blit(overlay, (self.rect.x, self.rect.y))
        
        # Draw border
        pg.draw.rect(screen, (200, 200, 200), self.rect, 2)
        
        # Draw title bar
        title_bar = pg.Rect(self.rect.x, self.rect.y, self.rect.width, 35)
        pg.draw.rect(screen, (255, 220, 100), title_bar)
        
        # Title text
        title_text = self.font_title.render("GUIDE", True, (30, 30, 40))
        title_rect = title_text.get_rect(center=(self.rect.centerx, self.rect.y + 18))
        screen.blit(title_text, title_rect)
        
        # Close button (X)
        close_rect = pg.Rect(self.rect.x + self.rect.width - 30, self.rect.y + 5, 25, 25)
        pg.draw.rect(screen, (80, 80, 100), close_rect)
        pg.draw.rect(screen, (200, 200, 200), close_rect, 1)
        close_text = self.font_text.render("X", True, (255, 255, 255))
        close_text_rect = close_text.get_rect(center=close_rect.center)
        screen.blit(close_text, close_text_rect)
        
        # Draw guide content (scrollable)
        y_offset = self.rect.y + 45
        scroll_offset = getattr(self, 'scroll_offset', 0)
        
        for i, line in enumerate(self.guide_lines):
            if i < scroll_offset:
                continue
            if y_offset > self.rect.y + self.rect.height - 20:
                break
            
            if line.startswith("==="):
                text = self.font_text.render(line, True, (255, 220, 100))
            elif line == "":
                y_offset += 10
                continue
            else:
                text = self.font_small.render(line, True, (200, 200, 220))
            
            screen.blit(text, (self.rect.x + 15, y_offset))
            y_offset += 22
        
        # Scroll hint
        if len(self.guide_lines) > 20:
            scroll_text = self.font_small.render("Scroll to see more", True, (150, 150, 170))
            scroll_rect = scroll_text.get_rect(center=(self.rect.centerx, self.rect.y + self.rect.height - 15))
            screen.blit(scroll_text, scroll_rect)

    def handle_event(self, event):
        if not self.visible:
            return False
        
        # Handle close button click
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            close_rect = pg.Rect(self.rect.x + self.rect.width - 30, self.rect.y + 5, 25, 25)
            if close_rect.collidepoint(event.pos):
                self.visible = False
                return True
        
        # Handle mouse wheel scrolling
        elif event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 4:  # Scroll up
                self.scroll_offset = max(0, getattr(self, 'scroll_offset', 0) - 1)
            elif event.button == 5:  # Scroll down
                max_scroll = max(0, len(self.guide_lines) - 18)
                self.scroll_offset = min(max_scroll, getattr(self, 'scroll_offset', 0) + 1)
        
        return False


# ----- Pannel (Like a drawer system lah basically)-----
class PanelManager:
    def __init__(self, screen_width, screen_height):
        self.active_panel = None  # To set button's name
        
        # ========== Setting of right area panels ==========
        # Right side area：X from 850 to 1300，width = 450
        RIGHT_AREA_X = 850
        RIGHT_AREA_WIDTH = 450
        RIGHT_AREA_HEIGHT = screen_height
        
        # Main panel (long rectangle) - used for Shop/Inventory/Upgrade/Crafting/Raids/Prestige
        panel_width = RIGHT_AREA_WIDTH - 20
        panel_height = 500
        panel_x = RIGHT_AREA_X + 10
        panel_y = 60
        
        self.panel_rect = pg.Rect(panel_x, panel_y, panel_width, panel_height)
        self.panel_color = (50, 50, 50, 220)  # Setting a opaque color
        self.border_color = (200, 200, 200) # Setting for its border
        
        # Description panel (square) - used for showing item description when hovering in Shop/Inventory
        desc_panel_height = 150
        desc_panel_y = panel_y + panel_height + 10
        self.desc_panel_rect = pg.Rect(panel_x, desc_panel_y, panel_width, desc_panel_height)
        
        # Guide panel (overlays the right area)
        self.guide_system = GuideSystem(panel_x, panel_y, panel_width, panel_height + desc_panel_height + 10)
        # =======================================
        
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
    
    def toggle_guide(self):
        """Function to toggle guide panel, independent from other panels"""
        self.guide_system.toggle()
    
    def handle_event(self, event):
        # Mainly handle guide panel events first since it overlays other panels
        if self.guide_system.visible:
            self.guide_system.handle_event(event)
            return
        
        if self.active_panel == "Shop" and self.shop_system:
            self.shop_system.handle_event(event, self.add_to_inventory)
            self.global_pocket_money = Currency_System.pocket_money
        elif self.active_panel == "Inventory" and self.inventory_system:
            self.inventory_system.handle_event(event)

    def add_to_inventory(self, item_name):
        """Adding item into inventory"""
        if self.inventory_system is None:
            # Create inventory system if it doesn't exist when adding item for the first time
            inv_x = self.panel_rect.x + 10
            inv_y = self.panel_rect.y + 10
            inv_width = self.panel_rect.width - 20
            inv_height = self.panel_rect.height - 20
            self.inventory_system = InventorySystem(inv_x, inv_y, inv_width, inv_height)
            
            # Set position of description bar for InventorySystem
            self.inventory_system.set_desc_panel_rect(self.desc_panel_rect)
            
            # Restore pending inventory data immediately after activated
            if self.pending_inventory:
                self.inventory_system.restore_inventory(self.pending_inventory)
                print(f"[RESTORE] Inventory restored on creation: {len(self.pending_inventory)} items")
            
        self.inventory_system.add_item(item_name)

    def draw(self, screen):
        # If guide panel is visible, draw it first
        if self.guide_system.visible:
            self.guide_system.draw(screen)
            return
        
        # Draw regular panels
        if self.active_panel:
            # Draw main panel background (long rectangle)
            panel_surface = pg.Surface((self.panel_rect.width, self.panel_rect.height))
            panel_surface.set_alpha(self.panel_color[3])
            panel_surface.fill(self.panel_color[:3])
            screen.blit(panel_surface, (self.panel_rect.x, self.panel_rect.y))
            
            # Draw main panel border
            pg.draw.rect(screen, self.border_color, self.panel_rect, 3)
            
            # Draw description panel background (square)
            desc_surface = pg.Surface((self.desc_panel_rect.width, self.desc_panel_rect.height))
            desc_surface.set_alpha(self.panel_color[3])
            desc_surface.fill(self.panel_color[:3])
            screen.blit(desc_surface, (self.desc_panel_rect.x, self.desc_panel_rect.y))
            
            # Draw description panel border
            pg.draw.rect(screen, self.border_color, self.desc_panel_rect, 3)
            
            # Draw separator line
            pg.draw.line(screen, (100, 100, 100), 
                        (self.panel_rect.x, self.panel_rect.y + self.panel_rect.height),
                        (self.panel_rect.x + self.panel_rect.width, self.panel_rect.y + self.panel_rect.height), 2)
            
            # Display current panel title
            font = pg.font.SysFont(None, 36)
            title_text = font.render(f"{self.active_panel}", True, (255, 220, 100))
            title_rect = title_text.get_rect(center=(self.panel_rect.centerx, self.panel_rect.y + 25))
            screen.blit(title_text, title_rect)
            
            # Draw active panel content
            if self.active_panel == "Shop":
                if self.shop_system is None:
                    # Create shop panel
                    shop_x = self.panel_rect.x + 10
                    shop_y = self.panel_rect.y + 50
                    shop_width = self.panel_rect.width - 20
                    shop_height = self.panel_rect.height - 60
                    self.shop_system = ShopSystem(shop_x, shop_y, shop_width, shop_height)
                    
                    # Set position of description bar for ShopSystem
                    self.shop_system.set_desc_panel_rect(self.desc_panel_rect)
                    
                    # Restore pending shop data immediately after activated
                    if self.pending_shop_state:
                        self.shop_system.restore_shop_state(self.pending_shop_state)
                        print(f"[RESTORE] Shop state restored on creation: {len(self.pending_shop_state)} items")
                    
                self.shop_system.update()
                self.shop_system.draw(screen)
            elif self.active_panel == "Inventory":
                if self.inventory_system is None:
                    # Create inventory panel
                    inv_x = self.panel_rect.x + 10
                    inv_y = self.panel_rect.y + 50
                    inv_width = self.panel_rect.width - 20
                    inv_height = self.panel_rect.height - 60
                    self.inventory_system = InventorySystem(inv_x, inv_y, inv_width, inv_height)
                    
                    # Set position of description bar for InventorySystem
                    self.inventory_system.set_desc_panel_rect(self.desc_panel_rect)
                    
                    # Restore pending inventory data immediately after activated
                    if self.pending_inventory:
                        self.inventory_system.restore_inventory(self.pending_inventory)
                        print(f"[RESTORE] Inventory restored on creation: {len(self.pending_inventory)} items")
                    
                self.inventory_system.draw(screen)


# ----- Active PanelManager -----
panel_manager = PanelManager(1300, 750)

# ----- call out PanelManager function -----
def create_button_callback(button_name):
    def callback():
        panel_manager.toggle_panel(button_name)
    return callback

# Guide button callback is separate since it doesn't toggle with other panels
def guide_callback():
    panel_manager.toggle_guide()

# ========== Layout of buttons ==========
MIDDLE_AREA_X = 300
MIDDLE_WIDTH = 550
BUTTON_Y = 680

button_width = 90
button_height = 40
spacing = 8

total_buttons_width = button_width * 5 + spacing * 4
start_x = MIDDLE_AREA_X + (MIDDLE_WIDTH - total_buttons_width) // 2

buttons = [
    Main_button(start_x + 0 * (button_width + spacing), BUTTON_Y, button_width, button_height, "Upgrade", (80, 80, 100), (120, 120, 140), create_button_callback("Upgrade")),
    Main_button(start_x + 1 * (button_width + spacing), BUTTON_Y, button_width, button_height, "Crafting", (80, 80, 100), (120, 120, 140), create_button_callback("Crafting")),
    Main_button(start_x + 2 * (button_width + spacing), BUTTON_Y, button_width, button_height, "Raids", (80, 80, 100), (120, 120, 140), create_button_callback("Raids")),
    Main_button(start_x + 3 * (button_width + spacing), BUTTON_Y, button_width, button_height, "Shop", (80, 80, 100), (120, 120, 140), create_button_callback("Shop")),
    Main_button(start_x + 4 * (button_width + spacing), BUTTON_Y, button_width, button_height, "Prestige", (80, 80, 100), (120, 120, 140), create_button_callback("Prestige")),
]

# Inventory button
INV_BUTTON_X = 1240
INV_BUTTON_Y = 12
inventory_button = Main_button(INV_BUTTON_X, INV_BUTTON_Y, 40, 40, "Inv", (80, 80, 100), (120, 120, 140), create_button_callback("Inventory"))
buttons.append(inventory_button)

# Guide button
GUIDE_BUTTON_X = INV_BUTTON_X - 50  # 1240 - 50 = 1190
GUIDE_BUTTON_Y = 12
guide_button = Main_button(GUIDE_BUTTON_X, GUIDE_BUTTON_Y, 40, 40, "?", (80, 80, 100), (120, 120, 140), guide_callback)
buttons.append(guide_button)
# ===============================