import pygame as pg
from Shop_System import ShopSystem
from Inventory_System import InventorySystem
import Currency_System
from Pet_System import PetSystem
from Player_Upgrade_System import PlayerUpgradeSystem
import Equipment_System

# --- NEW: GLOBAL SOUND SYSTEM (CLS_1) ---
try:
    # We load it ONCE here at the top of the file
    GLOBAL_CLICK = pg.mixer.Sound("Sound_Effects/Click_sfx.wav")
    GLOBAL_CLICK.set_volume(0.3) # 50% volume
except Exception as e:
    GLOBAL_CLICK = None
    print(f"Warning: Could not load click sound: {e}")

pg.init()
pg.font.init()  

class Main_button:
    def __init__(self, x, y, width, height, text, color, hover_color, callback=None):
        self.rect = pg.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.callback = callback
        self.font = pg.font.SysFont(None, 16)
        self.is_hovered = False

    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                
                # 1. Play the global sound!
                if GLOBAL_CLICK:
                    GLOBAL_CLICK.play()
                
                # 2. Run the button's normal code
                if self.callback:
                    self.callback()
                return True
        return False

    def update(self):
        self.is_hovered = self.rect.collidepoint(pg.mouse.get_pos())

    def draw(self, screen):
        color = self.hover_color if self.is_hovered else self.color
        pg.draw.rect(screen, color, self.rect)
        pg.draw.rect(screen, (200, 200, 200), self.rect, 1)
        
        text_surf = self.font.render(self.text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)


class ToolbarButton:
    """Toolbar button (smaller, for the top toolbar)"""
    def __init__(self, x, y, width, height, text, callback):
        self.rect = pg.Rect(x, y, width, height)
        self.text = text
        self.callback = callback
        self.font = pg.font.SysFont(None, 14)
        self.is_hovered = False

    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                if self.callback:
                    self.callback()
                return True
        return False

    def update(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def draw(self, screen):
        color = (100, 100, 120) if self.is_hovered else (60, 60, 80)
        pg.draw.rect(screen, color, self.rect)
        pg.draw.rect(screen, (200, 200, 200), self.rect, 1)
        text_surf = self.font.render(self.text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)


class GuideSystem:
    def __init__(self, x, y, width, height):
        self.rect = pg.Rect(x, y, width, height)
        self.font_title = pg.font.SysFont(None, 28, bold=True)
        self.font_text = pg.font.SysFont(None, 18)
        self.font_small = pg.font.SysFont(None, 16)
        self.visible = False
        
        self.guide_lines = [
            "=== GAME GUIDE ===",
            "",
            "[CONTROLS]",
            "Click on Monster - Deal damage",
            "G Key - Gain OP WEAPON (Test)",
            "E Key - Equip weapon (hover over item in Inv first)",
            "U Key - Unequip weapon",
            "C Key - Craft Golden Spatula",
            "N Key - Next Stage (Dev)",
            "P Key - Prestige (Dev)",
            "",
            "[SHOP]",
            "Click Shop button to open shop",
            "Use category tabs to filter items",
            "",
            "[INVENTORY]",
            "Click Inv button to open inventory",
            "Use category tabs to filter items",
            "HOVER over an item, then press E to equip!",
            "",
            "[PET SYSTEM]",
            "Click Pet button to manage pets",
            "Equip up to 3 pets",
            "",
            "[PRESTIGE]",
            "Reach Stage 10 to Prestige",
            "Earn Michelin Stars for permanent DMG boost",
            "",
            "[UPGRADE]",
            "Increase base damage permanently",
            "Cost increases with each upgrade"
        ]

    def toggle(self):
        self.visible = not self.visible

    def draw(self, screen):
        if not self.visible:
            return
        
        overlay = pg.Surface((self.rect.width, self.rect.height))
        overlay.set_alpha(230)
        overlay.fill((30, 30, 40))
        screen.blit(overlay, (self.rect.x, self.rect.y))
        
        pg.draw.rect(screen, (200, 200, 200), self.rect, 2)
        
        title_bar = pg.Rect(self.rect.x, self.rect.y, self.rect.width, 35)
        pg.draw.rect(screen, (255, 220, 100), title_bar)
        
        title_text = self.font_title.render("GUIDE", True, (30, 30, 40))
        title_rect = title_text.get_rect(center=(self.rect.centerx, self.rect.y + 18))
        screen.blit(title_text, title_rect)
        
        close_rect = pg.Rect(self.rect.x + self.rect.width - 30, self.rect.y + 5, 25, 25)
        pg.draw.rect(screen, (80, 80, 100), close_rect)
        pg.draw.rect(screen, (200, 200, 200), close_rect, 1)
        close_text = self.font_text.render("X", True, (255, 255, 255))
        close_text_rect = close_text.get_rect(center=close_rect.center)
        screen.blit(close_text, close_text_rect)
        
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
        
        if len(self.guide_lines) > 20:
            scroll_text = self.font_small.render("Scroll to see more", True, (150, 150, 170))
            scroll_rect = scroll_text.get_rect(center=(self.rect.centerx, self.rect.y + self.rect.height - 15))
            screen.blit(scroll_text, scroll_rect)

    def handle_event(self, event):
        if not self.visible:
            return False
        
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            close_rect = pg.Rect(self.rect.x + self.rect.width - 30, self.rect.y + 5, 25, 25)
            if close_rect.collidepoint(event.pos):
                self.visible = False
                return True
        
        elif event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 4:
                self.scroll_offset = max(0, getattr(self, 'scroll_offset', 0) - 1)
            elif event.button == 5:
                max_scroll = max(0, len(self.guide_lines) - 18)
                self.scroll_offset = min(max_scroll, getattr(self, 'scroll_offset', 0) + 1)
        
        return False
    
class PanelManager:
    def __init__(self, screen_width, screen_height):
        self.active_panel = None
        self.toolbar_buttons = []
        self.toolbar_offset = 0
        self.toolbar_dragging = False
        self.toolbar_drag_start_x = 0
        self.toolbar_drag_start_offset = 0
        
        self.player_upgrade_system = None

        try:
            raw_scrap = pg.image.load("Icon/Scrap.png").convert_alpha()
            self.scrap_icon = pg.transform.scale(raw_scrap, (32, 32)) # Nice large size
        except:
            self.scrap_icon = None

        # Load prestige sound effect
        try:
            self.prestige_sound = pg.mixer.Sound("Sound_Effects/prestige_sfx2.wav") 
            self.prestige_sound.set_volume(1.0)
        except FileNotFoundError:
            print("[AUDIO WARN] prestige_sfx2.wav not found. Running without sound.")
            self.prestige_sound = None

        RIGHT_AREA_X = 850
        RIGHT_AREA_WIDTH = 450
        RIGHT_AREA_HEIGHT = screen_height
        
        # Toolbar area (top of right area)
        toolbar_height = 45
        toolbar_y = 10
        self.toolbar_rect = pg.Rect(RIGHT_AREA_X + 5, toolbar_y, RIGHT_AREA_WIDTH - 10, toolbar_height)
        
        # Scrollbar area (above toolbar, for dragging)
        self.scrollbar_rect = pg.Rect(self.toolbar_rect.x, self.toolbar_rect.y - 8, self.toolbar_rect.width, 6)
        self.scrollbar_dragging = False
        
        # Panel size (smaller, located below toolbar)
        panel_width = RIGHT_AREA_WIDTH - 20
        panel_height = RIGHT_AREA_HEIGHT - toolbar_height - 60
        panel_x = RIGHT_AREA_X + 10
        panel_y = toolbar_y + toolbar_height + 10
        
        self.panel_rect = pg.Rect(panel_x, panel_y, panel_width, panel_height)
        self.panel_color = (50, 50, 50, 220)
        self.border_color = (200, 200, 200)
        
        # Description panel (inside main panel, at the bottom)
        desc_panel_height = 130
        desc_panel_y = panel_y + panel_height - desc_panel_height - 10
        self.desc_panel_rect = pg.Rect(panel_x + 10, desc_panel_y, panel_width - 20, desc_panel_height)
        
        self.guide_system = GuideSystem(panel_x, panel_y, panel_width, panel_height)
        
        self.shop_system = None
        self.inventory_system = None
        self.pet_system = None
        self.global_pocket_money = Currency_System.pocket_money
        
        self.current_shop_category = 0
        self.current_inv_category = 0
        
        self.pending_inventory = []
        self.pending_shop_state = []
        self.pending_pet_data = []
        self.pending_money = None

        self.current_stage = 1
        self.wants_to_prestige = False
        
        # Initialize toolbar buttons
        self._init_toolbar_buttons()

    def _init_toolbar_buttons(self):
        """Initialize toolbar buttons"""
        button_width = 65
        button_height = 32
        spacing = 5
        
        button_texts = ["Upgrade", "Crafting", "Raids", "Shop", "Prestige", "Inv", "Pet"]
        button_callbacks = [
            lambda: self.toggle_panel("Upgrade"),
            lambda: self.toggle_panel("Crafting"),
            lambda: self.toggle_panel("Raids"),
            lambda: self.toggle_panel("Shop"),
            lambda: self.toggle_panel("Prestige"),
            lambda: self.toggle_panel("Inventory"),
            lambda: self.toggle_panel("Pet")
        ]
        
        x = self.toolbar_rect.x + 5
        y = self.toolbar_rect.y + 7
        
        self.toolbar_buttons = []
        for text, callback in zip(button_texts, button_callbacks):
            btn = ToolbarButton(x, y, button_width, button_height, text, callback)
            self.toolbar_buttons.append(btn)
            x += button_width + spacing
        
        # Calculate total width and max scroll offset
        total_width = len(self.toolbar_buttons) * (button_width + spacing) - spacing
        self.max_toolbar_offset = max(0, total_width - (self.toolbar_rect.width - 10))

    def toggle_panel(self, button_name):
        if self.active_panel == button_name:
            self.active_panel = None
        else:
            self.active_panel = button_name
    
    def toggle_guide(self):
        self.guide_system.toggle()

    def handle_toolbar_event(self, event):
        """Handle toolbar mouse drag events (both scrollbar and toolbar area)"""
        # Handle scrollbar dragging (white semi-transparent bar above toolbar)
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            if self.scrollbar_rect.collidepoint(event.pos):
                self.scrollbar_dragging = True
                self.toolbar_drag_start_x = event.pos[0]
                self.toolbar_drag_start_offset = self.toolbar_offset
                return True
            
            if self.toolbar_rect.collidepoint(event.pos):
                # Check if a button was clicked
                for btn in self.toolbar_buttons:
                    btn_screen_rect = btn.rect.copy()
                    btn_screen_rect.x -= self.toolbar_offset
                    if btn_screen_rect.collidepoint(event.pos):
                        return False
                # Start dragging on blank area
                self.toolbar_dragging = True
                self.toolbar_drag_start_x = event.pos[0]
                self.toolbar_drag_start_offset = self.toolbar_offset
        
        elif event.type == pg.MOUSEBUTTONUP and event.button == 1:
            self.toolbar_dragging = False
            self.scrollbar_dragging = False
        
        elif event.type == pg.MOUSEMOTION and (self.toolbar_dragging or self.scrollbar_dragging):
            dx = event.pos[0] - self.toolbar_drag_start_x
            new_offset = self.toolbar_drag_start_offset - dx
            self.toolbar_offset = max(0, min(self.max_toolbar_offset, new_offset))
        
        return True

    def load_saved_data(self, pocket_money, inventory_items, shop_state, pet_data=None):
        self.global_pocket_money = pocket_money
        self.pending_inventory = inventory_items if inventory_items else []
        self.pending_shop_state = shop_state if shop_state else []
        self.pending_pet_data = pet_data if pet_data else []
        self.pending_money = pocket_money
        
        if self.inventory_system and self.pending_inventory:
            self.inventory_system.restore_inventory(self.pending_inventory)
        if self.shop_system and self.pending_shop_state:
            self.shop_system.restore_shop_state(self.pending_shop_state)
        if self.pet_system and self.pending_pet_data:
            self.pet_system.restore_save_data(self.pending_pet_data)

    def get_save_data(self):
        inventory_items = []
        if self.inventory_system:
            inventory_items = self.inventory_system.get_inventory_state()
        shop_state = []
        if self.shop_system:
            shop_state = self.shop_system.get_shop_state()
        pet_data = []
        if self.pet_system:
            pet_data = self.pet_system.get_save_data()
        return inventory_items, shop_state, pet_data

    def reset_all_on_prestige(self):
        if self.shop_system:
            self.shop_system.reset_shop()
        if self.inventory_system:
            self.inventory_system.reset_inventory()
        if self.pet_system:
            self.pet_system.reset_on_prestige()

    def handle_event(self, event):
        # Handle Guide panel first
        if self.guide_system.visible:
            self.guide_system.handle_event(event)
            return
        
        # Handle toolbar events (drag and button clicks)
        self.handle_toolbar_event(event)
        
        # Handle toolbar button clicks
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            for btn in self.toolbar_buttons:
                btn_screen_rect = btn.rect.copy()
                btn_screen_rect.x -= self.toolbar_offset
                if btn_screen_rect.collidepoint(event.pos):
                    
                    if GLOBAL_CLICK: GLOBAL_CLICK.play() # <--- PLAY SOUND FOR TOOLBAR!
                    
                    btn.callback()
                    return
        
        # Handle active panel events
        if self.active_panel == "Shop" and self.shop_system:
            self.shop_system.handle_event(event, self.add_to_inventory)
            self.global_pocket_money = Currency_System.pocket_money
        elif self.active_panel == "Inventory" and self.inventory_system:
            self.inventory_system.handle_event(event)
        elif self.active_panel == "Pet" and self.pet_system:
            self.pet_system.handle_event(event)
        elif self.active_panel == "Upgrade" and self.player_upgrade_system:
            self.player_upgrade_system.handle_event(event)
        elif self.active_panel == "Prestige":
            stars_to_gain = Currency_System.calculate_prestige_rewards(self.current_stage)
            
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                # 1. Did they click the button?
                if hasattr(self, 'prestige_btn_rect') and self.prestige_btn_rect.collidepoint(event.pos):
                    
                    # --- PLAY SOUND ONCE HERE! ---
                    if GLOBAL_CLICK: 
                        GLOBAL_CLICK.play()

                    # --- RUN THE PRESTIGE LOGIC ---
                    if stars_to_gain > 0:
                        if getattr(self, 'confirm_prestige', False) == False:
                            self.confirm_prestige = True  
                        else:
                            if Currency_System.trigger_prestige(self.monster_manager):
                                print("Prestige Successful!")
                                if hasattr(self, 'prestige_sound') and self.prestige_sound:
                                    self.prestige_sound.play()
                                self.active_panel = None
                                self.confirm_prestige = False
                
                # 2. Did they click anywhere ELSE on the screen?
                else:
                    self.confirm_prestige = False # Only cancel if they clicked away!
            return

    def add_to_inventory(self, item_name):
        if self.pet_system is None:
            self.pet_system = PetSystem()
            if self.pending_pet_data:
                self.pet_system.restore_save_data(self.pending_pet_data)
        
        if self.inventory_system is None:
            inv_x = self.panel_rect.x + 10
            inv_y = self.panel_rect.y + 50
            inv_width = self.panel_rect.width - 20
            inv_height = self.panel_rect.height - 80
            self.inventory_system = InventorySystem(inv_x, inv_y, inv_width, inv_height)
            self.inventory_system.set_desc_panel_rect(self.desc_panel_rect)
            self.inventory_system.set_category(self.current_inv_category)
            if self.pending_inventory:
                self.inventory_system.restore_inventory(self.pending_inventory)
        
        self.inventory_system.add_item(item_name)
        
        if self.pet_system:
            self.pet_system.add_pet(item_name)
        
        if item_name in Equipment_System.equipment_database:
            Equipment_System.gain_equipment(item_name)
            print(f"[SYNC] Equipment '{item_name}' added to Equipment_System")

    def get_selected_inventory_item(self):
        if self.inventory_system:
            return self.inventory_system.selected_item
        return None
    
    def draw_toolbar(self, screen):
        """Draw the scrollable toolbar with a white semi-transparent scrollbar above"""
        # Draw toolbar background
        pg.draw.rect(screen, (35, 35, 45), self.toolbar_rect)
        pg.draw.rect(screen, (100, 100, 120), self.toolbar_rect, 1)
        
        # Draw white semi-transparent scrollbar above toolbar
        scrollbar_surface = pg.Surface((self.scrollbar_rect.width, self.scrollbar_rect.height))
        scrollbar_surface.set_alpha(180)
        scrollbar_surface.fill((255, 255, 255))
        screen.blit(scrollbar_surface, (self.scrollbar_rect.x, self.scrollbar_rect.y))
        pg.draw.rect(screen, (180, 180, 200), self.scrollbar_rect, 1)
        
        # Calculate scroll indicator width based on visible area proportion
        total_width = len(self.toolbar_buttons) * (self.toolbar_buttons[0].rect.width + 5) - 5 if self.toolbar_buttons else 1
        visible_ratio = self.toolbar_rect.width / total_width if total_width > 0 else 1
        indicator_width = max(30, int(self.scrollbar_rect.width * visible_ratio))
        
        # Calculate scroll indicator position
        max_indicator_x = self.scrollbar_rect.x + self.scrollbar_rect.width - indicator_width
        indicator_x = self.scrollbar_rect.x + (self.toolbar_offset / self.max_toolbar_offset) * (self.scrollbar_rect.width - indicator_width) if self.max_toolbar_offset > 0 else self.scrollbar_rect.x
        indicator_x = max(self.scrollbar_rect.x, min(max_indicator_x, indicator_x))
        
        # Draw scroll indicator (darker bar showing current scroll position)
        indicator_rect = pg.Rect(indicator_x, self.scrollbar_rect.y, indicator_width, self.scrollbar_rect.height)
        pg.draw.rect(screen, (100, 100, 140), indicator_rect)
        pg.draw.rect(screen, (150, 150, 200), indicator_rect, 1)
        
        # Create clip region for buttons
        clip_rect = self.toolbar_rect.inflate(-4, -4)
        old_clip = screen.get_clip()
        screen.set_clip(clip_rect)
        
        # Draw buttons with offset
        for btn in self.toolbar_buttons:
            btn_screen_x = btn.rect.x - self.toolbar_offset
            temp_rect = btn.rect.copy()
            temp_rect.x = btn_screen_x
            
            # Only draw buttons visible in the clip region
            if temp_rect.x + temp_rect.width > clip_rect.x and temp_rect.x < clip_rect.x + clip_rect.width:
                original_x = btn.rect.x
                btn.rect.x = btn_screen_x
                btn.update(pg.mouse.get_pos())
                btn.draw(screen)
                btn.rect.x = original_x
        
        screen.set_clip(old_clip)
        
        # Draw edge shadows if scrollable
        if self.toolbar_offset > 0:
            left_shadow = pg.Surface((15, self.toolbar_rect.height))
            left_shadow.set_alpha(100)
            left_shadow.fill((0, 0, 0))
            screen.blit(left_shadow, (self.toolbar_rect.x, self.toolbar_rect.y))
        
        if self.toolbar_offset < self.max_toolbar_offset:
            right_shadow = pg.Surface((15, self.toolbar_rect.height))
            right_shadow.set_alpha(100)
            right_shadow.fill((0, 0, 0))
            screen.blit(right_shadow, (self.toolbar_rect.x + self.toolbar_rect.width - 15, self.toolbar_rect.y))

    def draw(self, screen):
        # Draw right area background
        right_area_rect = pg.Rect(850, 0, 450, 750)
        pg.draw.rect(screen, (45, 45, 55), right_area_rect)
        pg.draw.rect(screen, (150, 150, 170), right_area_rect, 2)
        
        # Draw scrollable toolbar
        self.draw_toolbar(screen)
        
        # If Guide panel is visible, draw it
        if self.guide_system.visible:
            self.guide_system.draw(screen)
            return
        
        # If no panel is active, show hint text
        if self.active_panel is None:
            font = pg.font.SysFont(None, 28)
            hint_text = font.render("Click a button to interact!", True, (200, 200, 220))
            hint_rect = hint_text.get_rect(center=(850 + 225, 375))
            screen.blit(hint_text, hint_rect)
            
            font_small = pg.font.SysFont(None, 20)
            hint_text2 = font_small.render("Upgrade | Crafting | Raids | Shop | Prestige | Inv | Pet", True, (150, 150, 170))
            hint_rect2 = hint_text2.get_rect(center=(850 + 225, 420))
            screen.blit(hint_text2, hint_rect2)
            return
        
        # Draw active panel
        if self.active_panel:
            # Draw main panel background
            panel_surface = pg.Surface((self.panel_rect.width, self.panel_rect.height))
            panel_surface.set_alpha(self.panel_color[3])
            panel_surface.fill(self.panel_color[:3])
            screen.blit(panel_surface, (self.panel_rect.x, self.panel_rect.y))
            pg.draw.rect(screen, self.border_color, self.panel_rect, 3)
            
            # Draw description panel background (except for Prestige)
            if self.active_panel != "Prestige":
                desc_surface = pg.Surface((self.desc_panel_rect.width, self.desc_panel_rect.height))
                desc_surface.set_alpha(self.panel_color[3])
                desc_surface.fill(self.panel_color[:3])
                screen.blit(desc_surface, (self.desc_panel_rect.x, self.desc_panel_rect.y))
                pg.draw.rect(screen, self.border_color, self.desc_panel_rect, 3)
            
            # Draw separator line
            pg.draw.line(screen, (100, 100, 100), 
                        (self.panel_rect.x, self.panel_rect.y + self.panel_rect.height),
                        (self.panel_rect.x + self.panel_rect.width, self.panel_rect.y + self.panel_rect.height), 2)
            
            # Draw main title
            font = pg.font.SysFont(None, 32)
            title_text = font.render(f"{self.active_panel}", True, (255, 220, 100))
            title_rect = title_text.get_rect(center=(self.panel_rect.centerx, self.panel_rect.y + 22))
            screen.blit(title_text, title_rect)
            
            # Draw specific panel content
            if self.active_panel == "Shop":
                if self.shop_system is None:
                    shop_x = self.panel_rect.x + 10
                    shop_y = self.panel_rect.y + 50
                    shop_width = self.panel_rect.width - 20
                    shop_height = self.panel_rect.height - 80
                    self.shop_system = ShopSystem(shop_x, shop_y, shop_width, shop_height)
                    self.shop_system.set_desc_panel_rect(self.desc_panel_rect)
                    self.shop_system.set_category(self.current_shop_category)
                    if self.pending_shop_state:
                        self.shop_system.restore_shop_state(self.pending_shop_state)
                self.shop_system.update()
                self.shop_system.draw(screen)
            elif self.active_panel == "Inventory":
                if self.inventory_system is None:
                    inv_x = self.panel_rect.x + 10
                    inv_y = self.panel_rect.y + 50
                    inv_width = self.panel_rect.width - 20
                    inv_height = self.panel_rect.height - 80
                    self.inventory_system = InventorySystem(inv_x, inv_y, inv_width, inv_height)
                    self.inventory_system.set_desc_panel_rect(self.desc_panel_rect)
                    self.inventory_system.set_category(self.current_inv_category)
                    if self.pending_inventory:
                        self.inventory_system.restore_inventory(self.pending_inventory)
                self.inventory_system.draw(screen)
            elif self.active_panel == "Pet":
                if self.pet_system is None:
                    self.pet_system = PetSystem()
                    if self.pending_pet_data:
                        self.pet_system.restore_save_data(self.pending_pet_data)
                self.pet_system.update()
                self.pet_system.draw(screen, self.panel_rect, self.desc_panel_rect)
            elif self.active_panel == "Prestige":
                self._draw_prestige_panel(screen)
            elif self.active_panel == "Upgrade":
                if self.player_upgrade_system is None:
                    upgrade_x = self.panel_rect.x + 10
                    upgrade_y = self.panel_rect.y + 50
                    upgrade_width = self.panel_rect.width - 20
                    upgrade_height = self.panel_rect.height - 80
                    self.player_upgrade_system = PlayerUpgradeSystem(upgrade_x, upgrade_y, upgrade_width, upgrade_height)
                self.player_upgrade_system.draw(screen)
                # ... (after your Inventory and Pet checks) ...
            

    def _draw_prestige_panel(self, screen):
        stars_to_gain = Currency_System.calculate_prestige_rewards(self.current_stage)
        new_start = Currency_System.get_advanced_start(self.current_stage)
        
        current_stars = Currency_System.michelin_stars
        current_mult = Currency_System.get_prestige_multiplier()
        
        pg.draw.rect(screen, (20, 20, 40), self.panel_rect)
        pg.draw.rect(screen, (0, 0, 0), self.panel_rect, 6) 
        pg.draw.rect(screen, (200, 200, 200), self.panel_rect.inflate(-12, -12), 4)

        try:
            badge_img = pg.image.load("Icon/Prestige_icon.png").convert_alpha()
            
            # Optional: Scale it if it's too big! Change (150, 150) to whatever fits.
            badge_img = pg.transform.scale(badge_img, (350, 450))
            
            # 2. Find the perfect center of your panel
            badge_rect = badge_img.get_rect(center=(self.panel_rect.centerx, self.panel_rect.centery + 30))
            
            # 3. Draw it!
            screen.blit(badge_img, badge_rect)
        except Exception as e:
            print(f"Could not load badge: {e}")
            
        font_title = pg.font.SysFont("courier", 36, bold=True)
        font_med = pg.font.SysFont("courier", 16, bold=True)
        font_small = pg.font.SysFont("courier", 16, bold=True)
        
        y_offset = self.panel_rect.y + 30
        
        title_text = font_title.render("- PRESTIGE -", False, (255, 255, 0))
        screen.blit(title_text, title_text.get_rect(center=(self.panel_rect.centerx, y_offset)))

        y_offset += 30
        warn_text = font_small.render("WARNING: MONEY RESETS. GEAR KEPT.", False, (255, 50, 50))
        screen.blit(warn_text, warn_text.get_rect(center=(self.panel_rect.centerx, y_offset)))
        
        y_offset += 22
        if current_stars > 0:
            buff_text = font_small.render(f"CURRENT BUFF: {current_stars} STARS (x{current_mult:.1f} DMG)", False, (255, 215, 0))
            screen.blit(buff_text, buff_text.get_rect(center=(self.panel_rect.centerx, y_offset)))
        
        y_offset += 22
        inner_screen_rect = pg.Rect(self.panel_rect.x + 30, y_offset, self.panel_rect.width - 60, 90)
        pg.draw.rect(screen, (10, 10, 20), inner_screen_rect) 
        pg.draw.rect(screen, (100, 255, 100), inner_screen_rect, 2) 
        
        gain_text = font_med.render(f"STARS TO GAIN: +{stars_to_gain}", False, (255, 255, 255))
        screen.blit(gain_text, gain_text.get_rect(center=(self.panel_rect.centerx, y_offset + 30)))
        
        start_text = font_med.render(f"NEXT START: LVL {new_start}", False, (100, 255, 255))
        screen.blit(start_text, start_text.get_rect(center=(self.panel_rect.centerx, y_offset + 55)))
        
        self.prestige_btn_rect = pg.Rect(self.panel_rect.centerx - 100, self.panel_rect.bottom - 75, 200, 50)
        
        if stars_to_gain > 0:
            btn_color = (200, 150, 0) if self.prestige_btn_rect.collidepoint(pg.mouse.get_pos()) else (150, 100, 0)
            btn_text = "CONFIRM PRESTIGE"
            if getattr(self, 'confirm_prestige', False):
                btn_text = "ARE YOU SURE?"
        else:
            btn_color = (100, 100, 100)
            btn_text = "REACH STAGE 10"
            
        pg.draw.rect(screen, btn_color, self.prestige_btn_rect)
        pg.draw.rect(screen, (255, 255, 255), self.prestige_btn_rect, 2)
        
        lbl = font_med.render(btn_text, True, (255, 255, 255))
        lbl_rect = lbl.get_rect(center=self.prestige_btn_rect.center)
        screen.blit(lbl, lbl_rect)


# ========== Panel Manager ==========
panel_manager = PanelManager(1300, 750)

# ========== Button callback ==========
def guide_callback():
    panel_manager.toggle_guide()

# ========== Button list (only Guide button in the middle area) ==========
buttons = []

GUIDE_BUTTON_X = 305
GUIDE_BUTTON_Y = 12
guide_button = Main_button(GUIDE_BUTTON_X, GUIDE_BUTTON_Y, 40, 40, "?", (80, 80, 100), (120, 120, 140), guide_callback)
buttons.append(guide_button)

# ========== Assign button list to panel_manager ==========
panel_manager.buttons = buttons