import pygame as pg
import os
from Audio_System import GLOBAL_CLICK
from Shop_System import ShopSystem
from Inventory_System import InventorySystem
import Currency_System
from Pet_System import PetSystem
from Player_Upgrade_System import PlayerUpgradeSystem
import Equipment_System
from Crafting_System import CraftingSystem
from KitchenGuide_System import KitchenGuideSystem
from Settings_System import SettingsSystem

pg.init()
pg.font.init()  

class Main_button:
    def __init__(self, x, y, width, height, text, color, hover_color, callback=None, icon_name=None):
        self.rect = pg.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.callback = callback
        self.font = pg.font.SysFont(None, 16)
        self.is_hovered = False
        self.icon_name = icon_name
        self.icon_image = None
        self.icon_loaded = False
    
    def load_icon(self):
        """Loading icon late a bit"""
        print(f"[DEBUG] load_icon called for: {self.icon_name}")
        
        if self.icon_loaded or not self.icon_name:
            print(f"[DEBUG] Skipping {self.icon_name}, icon_loaded={self.icon_loaded}")
            return
        
        icon_folder = os.path.join(os.path.dirname(__file__), "Icon")
        icon_path_png = os.path.join(icon_folder, f"{self.icon_name}.png")
        
        print(f"[DEBUG] Looking for: {icon_path_png}")
        print(f"[DEBUG] File exists: {os.path.exists(icon_path_png)}")
        
        try:
            if os.path.exists(icon_path_png):
                original = pg.image.load(icon_path_png).convert_alpha()
                
                # Remove white color background
                for x in range(original.get_width()):
                    for y in range(original.get_height()):
                        r, g, b, a = original.get_at((x, y))
                        if r > 240 and g > 240 and b > 240:
                            original.set_at((x, y), (0, 0, 0, 0))
                
                target_w = self.rect.width
                target_h = self.rect.height
                original_w = original.get_width()
                original_h = original.get_height()
                
                scale_w = target_w / original_w
                scale_h = target_h / original_h
                scale = max(scale_w, scale_h)
                
                new_w = int(original_w * scale)
                new_h = int(original_h * scale)
                
                self.icon_image = pg.transform.scale(original, (new_w, new_h))
                
                crop_x = (new_w - target_w) // 2
                crop_y = (new_h - target_h) // 2
                if crop_x > 0 or crop_y > 0:
                    self.icon_image = self.icon_image.subsurface((crop_x, crop_y, target_w, target_h))
                
                print(f"[BUTTON] Loaded icon: {self.icon_name}.png (scaled to {target_w}x{target_h})")
            else:
                print(f"[BUTTON] File not found: {icon_path_png}")
            self.icon_loaded = True
        except Exception as e:
            print(f"[BUTTON] Error loading {self.icon_name} - {e}")
            self.icon_loaded = True

    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                if GLOBAL_CLICK:
                    GLOBAL_CLICK.play()
                if self.callback:
                    self.callback()
                return True
        return False

    def update(self):
        self.is_hovered = self.rect.collidepoint(pg.mouse.get_pos())

    def draw(self, screen):
        # Try loading the image
        if not self.icon_loaded and self.icon_name:
            self.load_icon()
        
        if self.icon_image:
            # --- NEW: NO SCALING IN THE LOOP! ---
            if self.is_hovered:
                # We calculate the scaled image dynamically here only ONCE if missing, 
                # but a better approach is saving it. For quick inline fix without breaking init:
                if not hasattr(self, 'hover_image'):
                    scale = 1.1
                    new_w = int(self.rect.width * scale)
                    new_h = int(self.rect.height * scale)
                    self.hover_image = pg.transform.scale(self.icon_image, (new_w, new_h))
                
                draw_x = self.rect.centerx - self.hover_image.get_width() // 2
                draw_y = self.rect.centery - self.hover_image.get_height() // 2
                screen.blit(self.hover_image, (draw_x, draw_y))
            else:
                screen.blit(self.icon_image, self.rect)
        else:
            color = self.hover_color if self.is_hovered else self.color
            pg.draw.rect(screen, color, self.rect)
            pg.draw.rect(screen, (200, 200, 200), self.rect, 1)
            text_surf = self.font.render(self.text, True, (255, 255, 255))
            text_rect = text_surf.get_rect(center=self.rect.center)
            screen.blit(text_surf, text_rect)


class ToolbarButton:
    def __init__(self, x, y, width, height, text, callback):
        self.rect = pg.Rect(x, y, width, height)
        self.text = text
        self.callback = callback
        self.font = pg.font.SysFont(None, 14)
        self.is_hovered = False

    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                if GLOBAL_CLICK:
                    GLOBAL_CLICK.play()
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


class VerticalScrollButton:
    def __init__(self, x, y, width, height, text, callback, icon_name=None):
        self.rect = pg.Rect(x, y, width, height)
        self.text = text
        self.callback = callback
        self.font = pg.font.SysFont(None, 14)
        self.is_hovered = False
        self.icon_name = icon_name
        self.icon_image = None
        self.icon_loaded = False
    
    def load_icon(self):
        """Loading icon late a bit"""
        print(f"[DEBUG] VScroll load_icon: {self.icon_name}")
        
        if self.icon_loaded or not self.icon_name:
            return
        
        icon_folder = os.path.join(os.path.dirname(__file__), "Icon")
        icon_path_png = os.path.join(icon_folder, f"{self.icon_name}.png")
        
        print(f"[DEBUG] VScroll looking for: {icon_path_png}")
        print(f"[DEBUG] VScroll exists: {os.path.exists(icon_path_png)}")
        
        try:
            if os.path.exists(icon_path_png):
                original = pg.image.load(icon_path_png).convert_alpha()
                
                #Remove white color background
                for x in range(original.get_width()):
                    for y in range(original.get_height()):
                        r, g, b, a = original.get_at((x, y))
                        if r > 240 and g > 240 and b > 240:
                            original.set_at((x, y), (0, 0, 0, 0))
                
                target_w = self.rect.width
                target_h = self.rect.height
                original_w = original.get_width()
                original_h = original.get_height()
                
                scale_w = target_w / original_w
                scale_h = target_h / original_h
                scale = max(scale_w, scale_h)
                
                new_w = int(original_w * scale)
                new_h = int(original_h * scale)
                
                self.icon_image = pg.transform.scale(original, (new_w, new_h))
                
                crop_x = (new_w - target_w) // 2
                crop_y = (new_h - target_h) // 2
                if crop_x > 0 or crop_y > 0:
                    self.icon_image = self.icon_image.subsurface((crop_x, crop_y, target_w, target_h))
                
                print(f"[BUTTON] Loaded icon: {self.icon_name}.png (scaled to {target_w}x{target_h})")
            self.icon_loaded = True
        except Exception as e:
            print(f"[BUTTON] Warning: Could not load {self.icon_name} - {e}")
            self.icon_loaded = True

    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                if GLOBAL_CLICK:
                    GLOBAL_CLICK.play()
                if self.callback:
                    self.callback()
                return True
        return False

    def update(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def draw(self, screen):
        #Try loading the image
        if not self.icon_loaded and self.icon_name:
            self.load_icon()
        
        if self.icon_image:
            # --- NEW: CACHE HOVER EFFECT ---
            if self.is_hovered:
                if not hasattr(self, 'hover_image'):
                    scale = 1.1
                    new_w = int(self.rect.width * scale)
                    new_h = int(self.rect.height * scale)
                    self.hover_image = pg.transform.scale(self.icon_image, (new_w, new_h))
                
                draw_x = self.rect.centerx - self.hover_image.get_width() // 2
                draw_y = self.rect.centery - self.hover_image.get_height() // 2
                screen.blit(self.hover_image, (draw_x, draw_y))
            else:
                screen.blit(self.icon_image, self.rect)
        else:
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
            "E Key - Equip weapon (Legacy)",
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
            "Click EQUIP button on item card to equip",
            "Click UNEQUIP button to remove",
            "",
            "[PET SYSTEM]",
            "Click Pet button to manage pets",
            "Equip up to 3 pets",
            "",
            "[KITCHEN GUIDE]",
            "Click G button to open kitchen guide",
            "Complete tasks to earn rewards",
            "Finish all to complete the guide",
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
                if GLOBAL_CLICK:
                    GLOBAL_CLICK.play()
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
        self.left_column_buttons = []
        self.right_column_buttons = []
        self.settings_system = None
        self.player_upgrade_system = None

        try:
            self.prestige_sound = pg.mixer.Sound("Sound_Effects/prestige_sfx2.wav") 
            self.prestige_sound.set_volume(1.0)
        except FileNotFoundError:
            print("[AUDIO WARN] prestige_sfx2.wav not found. Running without sound.")
            self.prestige_sound = None

        RIGHT_AREA_X = 850
        RIGHT_AREA_WIDTH = 450
        RIGHT_AREA_HEIGHT = screen_height
        
        panel_width = RIGHT_AREA_WIDTH - 20
        panel_height = RIGHT_AREA_HEIGHT - 20
        panel_x = RIGHT_AREA_X + 10
        panel_y = 10
        
        self.panel_rect = pg.Rect(panel_x, panel_y, panel_width, panel_height)
        self.panel_color = (50, 50, 50, 220)
        self.border_color = (200, 200, 200)
        
        desc_panel_height = 130
        desc_panel_y = panel_y + panel_height - desc_panel_height - 10
        self.desc_panel_rect = pg.Rect(panel_x + 10, desc_panel_y, panel_width - 20, desc_panel_height)
        
        self.guide_system = GuideSystem(panel_x, panel_y, panel_width, panel_height)
        
        self.shop_system = None
        self.inventory_system = None
        self.pet_system = None
        self.kitchen_guide_system = None
        self.global_pocket_money = Currency_System.pocket_money
        self.crafting_system = None
        
        self.current_shop_category = 0
        self.current_inv_category = 0
        
        self.pending_inventory = []
        self.pending_shop_state = []
        self.pending_pet_data = []
        self.pending_guide_data = {}
        self.pending_money = None

        self.current_stage = 1
        self.wants_to_prestige = False
        
        # ========== Middle Area Right Side Buttons (Single Column) ==========
        MIDDLE_RIGHT_BORDER = 850
        BUTTON_WIDTH = 40
        BUTTON_HEIGHT = 40
        SPACING = 8
        BUTTON_START_Y = 12

        BUTTON_AREA_X = MIDDLE_RIGHT_BORDER - BUTTON_WIDTH - 5  # 805

        # Add buttons in the order they should appear in the left column
        button_configs = [
            {"text": "U", "callback": lambda: self.toggle_panel("Upgrade"), "icon": "Upgrade"},
            {"text": "P", "callback": lambda: self.toggle_panel("Pet"), "icon": "Pet"},
            {"text": "C", "callback": lambda: self.toggle_panel("Crafting"), "icon": "Crafting"},
            {"text": "I", "callback": lambda: self.toggle_panel("Inventory"), "icon": "Inventory"},
            {"text": "S", "callback": lambda: self.toggle_panel("Shop"), "icon": "Shop"},
            {"text": "Pr", "callback": lambda: self.toggle_panel("Prestige"), "icon": "Prestige_icon"},
            {"text": "G", "callback": lambda: self.toggle_panel("Guide"), "icon": "KGuide"},
            {"text": "Set", "callback": lambda: self.toggle_panel("Settings"), "icon": "Settings"}
        ]

        self.left_column_buttons = []
        for i, config in enumerate(button_configs):
            y = BUTTON_START_Y + i * (BUTTON_HEIGHT + SPACING)
            btn = VerticalScrollButton(
                BUTTON_AREA_X, y, BUTTON_WIDTH, BUTTON_HEIGHT, 
                config["text"], config["callback"], 
                icon_name=config["icon"]
            )
            self.left_column_buttons.append(btn)

        # ========== Button column background board ==========
        button_count = len(button_configs)
        bg_padding = 10
        bg_width = BUTTON_WIDTH + bg_padding * 2
        bg_height = button_count * (BUTTON_HEIGHT + SPACING) + bg_padding * 2 - SPACING
        bg_x = BUTTON_AREA_X - bg_padding
        bg_y = BUTTON_START_Y - bg_padding

        self.button_bg_rect = pg.Rect(bg_x, bg_y, bg_width, bg_height)
        self.button_bg_color = (40, 40, 50)
        self.button_bg_border_color = (80, 80, 100)
        # ===================================================

        self.right_column_buttons = []

    def update_guide_button_visibility(self):
        """If the player has completed all guide tasks, hide the Guide button."""
        if self.kitchen_guide_system and self.kitchen_guide_system.guide_manager.check_all_completed():
            for btn in self.left_column_buttons:
                if btn.text == "G":
                    btn.rect.x = -100
                    break

    def handle_button_events(self, event):
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            for btn in self.left_column_buttons:
                if btn.rect.collidepoint(event.pos):
                    if GLOBAL_CLICK:
                        GLOBAL_CLICK.play()
                    btn.callback()
                    return True
            for btn in self.right_column_buttons:
                if btn.rect.collidepoint(event.pos):
                    if GLOBAL_CLICK:
                        GLOBAL_CLICK.play()
                    btn.callback()
                    return True
        return False

    def draw_buttons(self, screen):
        if hasattr(self, 'button_bg_rect'):
            pg.draw.rect(screen, self.button_bg_color, self.button_bg_rect)
            pg.draw.rect(screen, self.button_bg_border_color, self.button_bg_rect, 2)
        for btn in self.left_column_buttons:
            btn.update(pg.mouse.get_pos())
            btn.draw(screen)
        for btn in self.right_column_buttons:
            btn.update(pg.mouse.get_pos())
            btn.draw(screen)

    def toggle_panel(self, button_name):
        if self.active_panel == button_name:
            self.active_panel = None
        else:
            self.active_panel = button_name
    
    def toggle_guide(self):
        self.guide_system.toggle()

    def load_saved_data(self, pocket_money, inventory_items, shop_state, pet_data=None, guide_data=None):
        self.global_pocket_money = pocket_money
        self.pending_inventory = inventory_items if inventory_items else []
        self.pending_shop_state = shop_state if shop_state else []
        self.pending_pet_data = pet_data if pet_data else []
        self.pending_guide_data = guide_data if guide_data else {}
        self.pending_money = pocket_money
        
        if self.inventory_system and self.pending_inventory:
            self.inventory_system.restore_inventory(self.pending_inventory)
        if self.shop_system and self.pending_shop_state:
            self.shop_system.restore_shop_state(self.pending_shop_state)
        if self.pet_system and self.pending_pet_data:
            self.pet_system.restore_save_data(self.pending_pet_data)
            print(f"[BUTTON] Pet data restored: {len(self.pending_pet_data)} pets")

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
        guide_data = {}
        if self.kitchen_guide_system:
            guide_data = self.kitchen_guide_system.guide_manager.get_save_data()
        return inventory_items, shop_state, pet_data, guide_data

    def reset_all_on_prestige(self):
        if self.shop_system:
            self.shop_system.reset_shop()
        if self.inventory_system:
            self.inventory_system.reset_inventory()
        if self.pet_system:
            self.pet_system.reset_on_prestige()

    def handle_event(self, event):
        # If Guide panel is visible
        if self.guide_system.visible:
            self.guide_system.handle_event(event)
            
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                for btn in self.left_column_buttons:
                    if btn.rect.collidepoint(event.pos):
                        if GLOBAL_CLICK:
                            GLOBAL_CLICK.play()
                        self.guide_system.visible = False
                        btn.callback()
                        return
                for btn in self.right_column_buttons:
                    if btn.rect.collidepoint(event.pos):
                        if GLOBAL_CLICK:
                            GLOBAL_CLICK.play()
                        self.guide_system.visible = False
                        btn.callback()
                        return
                if hasattr(self, 'guide_button_rect') and self.guide_button_rect.collidepoint(event.pos):
                    if GLOBAL_CLICK:
                        GLOBAL_CLICK.play()
                    self.guide_system.visible = False
                    return
            return
        
        # Normal event handling when Guide is not visible
        self.handle_button_events(event)
        
        # Handle active panel events
        if self.active_panel == "Shop" and self.shop_system:
            self.shop_system.handle_event(event, self.add_to_inventory)
            self.global_pocket_money = Currency_System.pocket_money
        elif self.active_panel == "Crafting" and getattr(self, 'crafting_system', None):
            self.crafting_system.handle_event(event)
        elif self.active_panel == "Inventory" and self.inventory_system:
            self.inventory_system.handle_event(event)
        elif self.active_panel == "Pet" and self.pet_system:
            self.pet_system.handle_event(event)
        elif self.active_panel == "Upgrade" and self.player_upgrade_system:
            self.player_upgrade_system.handle_event(event)
        elif self.active_panel == "Guide" and self.kitchen_guide_system:
            self.kitchen_guide_system.handle_event(event)
        elif self.active_panel == "Prestige":
            stars_to_gain = Currency_System.calculate_prestige_rewards(self.current_stage)
            
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                if hasattr(self, 'prestige_btn_rect') and self.prestige_btn_rect.collidepoint(event.pos):
                    if GLOBAL_CLICK: 
                        GLOBAL_CLICK.play()
                    if stars_to_gain > 0:
                        if not getattr(self, 'confirm_prestige', False):
                            self.confirm_prestige = True  
                            print("[PRESTIGE] Click again to confirm prestige!")
                        else:
                            if Currency_System.trigger_prestige(self.monster_manager):
                                print("Prestige Successful!")
                                if hasattr(self, 'prestige_sound') and self.prestige_sound:
                                    self.prestige_sound.play()
                                self.active_panel = None
                                self.confirm_prestige = False
                else:
                    self.confirm_prestige = False
            return
        elif self.active_panel == "Settings" and self.settings_system:
            self.settings_system.handle_event(event, GLOBAL_CLICK)
        

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
    
    def draw(self, screen):
        # Update Kitchen Guide visibility of button
        self.update_guide_button_visibility()
        
        # ========== Make sure kitchen_guide_system exists ==========
        if self.kitchen_guide_system is None:
            self.kitchen_guide_system = KitchenGuideSystem(0, 0, 1, 1)
            if self.pending_guide_data:
                self.kitchen_guide_system.guide_manager.restore_save_data(self.pending_guide_data)
        # ======================================================================
        
        right_area_rect = pg.Rect(850, 0, 450, 750)
        pg.draw.rect(screen, (45, 45, 55), right_area_rect)
        pg.draw.rect(screen, (150, 150, 170), right_area_rect, 2)
        
        self.draw_buttons(screen)
        
        font = pg.font.SysFont(None, 20)
        guide_text = font.render("?", True, (255, 255, 255))
        guide_rect = pg.Rect(310, 12, 30, 30)
        pg.draw.rect(screen, (80, 80, 100), guide_rect)
        pg.draw.rect(screen, (200, 200, 200), guide_rect, 1)
        screen.blit(guide_text, guide_text.get_rect(center=guide_rect.center))
        self.guide_button_rect = guide_rect
        
        if self.guide_system.visible:
            self.guide_system.draw(screen)
            return
        
        if self.active_panel is None:
            font = pg.font.SysFont(None, 28)
            hint_text = font.render("Click a button to interact!", True, (200, 200, 220))
            hint_rect = hint_text.get_rect(center=(850 + 225, 375))
            screen.blit(hint_text, hint_rect)
            
            font_small = pg.font.SysFont(None, 20)
            hint_text2 = font_small.render("Panel will appear here", True, (150, 150, 170))
            hint_rect2 = hint_text2.get_rect(center=(850 + 225, 420))
            screen.blit(hint_text2, hint_rect2)
            return
        
        if self.active_panel:
            panel_surface = pg.Surface((self.panel_rect.width, self.panel_rect.height))
            panel_surface.set_alpha(self.panel_color[3])
            panel_surface.fill(self.panel_color[:3])
            screen.blit(panel_surface, (self.panel_rect.x, self.panel_rect.y))
            pg.draw.rect(screen, self.border_color, self.panel_rect, 3)
            
            if self.active_panel not in ["Prestige", "Crafting"]:
                desc_surface = pg.Surface((self.desc_panel_rect.width, self.desc_panel_rect.height))
                desc_surface.set_alpha(self.panel_color[3])
                desc_surface.fill(self.panel_color[:3])
                screen.blit(desc_surface, (self.desc_panel_rect.x, self.desc_panel_rect.y))
                pg.draw.rect(screen, self.border_color, self.desc_panel_rect, 3)
            
            pg.draw.line(screen, (100, 100, 100), 
                        (self.panel_rect.x, self.panel_rect.y + self.panel_rect.height),
                        (self.panel_rect.x + self.panel_rect.width, self.panel_rect.y + self.panel_rect.height), 2)
            
            # --- NEW UNIFIED HEADER STYLE ---
            font_title = pg.font.SysFont("courier", 36, bold=True)
            
            if self.active_panel == "Guide":
                title_str = "- KITCHEN GUIDE -"
            elif self.active_panel != "Prestige":
                # Automatically uppercase the panel name and add hyphens
                title_str = f"- {self.active_panel.upper()} -"
            
            # Only draw here if it's not Prestige (Prestige handles its own drawing)
            if self.active_panel != "Prestige":
                # Using the exact same yellow color (255, 255, 0) and Y-offset (+30) as the Prestige panel
                title_text = font_title.render(title_str, True, (255, 255, 0))
                title_rect = title_text.get_rect(center=(self.panel_rect.centerx, self.panel_rect.y + 30))
                screen.blit(title_text, title_rect)
            
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

            elif self.active_panel == "Crafting":
                if getattr(self, 'crafting_system', None) is None:
                    craft_x = self.panel_rect.x + 10
                    craft_y = self.panel_rect.y + 50
                    craft_width = self.panel_rect.width - 20
                    craft_height = self.panel_rect.height - 80
                    self.crafting_system = CraftingSystem(craft_x, craft_y, craft_width, craft_height)
                self.crafting_system.draw(screen)

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
                
            elif self.active_panel == "Guide":
                if self.kitchen_guide_system:
                    self.kitchen_guide_system.rect = pg.Rect(
                        self.panel_rect.x + 10,
                        self.panel_rect.y + 50,
                        self.panel_rect.width - 20,
                        self.panel_rect.height - 80
                    )
                    self.kitchen_guide_system.set_callbacks({
                        "add_to_inventory": self.add_to_inventory,
                        "gain_equipment": Equipment_System.gain_equipment,
                        "add_pet": lambda name: self.pet_system.add_pet(name) if self.pet_system else None
                    })
                else:
                    guide_x = self.panel_rect.x + 10
                    guide_y = self.panel_rect.y + 50
                    guide_width = self.panel_rect.width - 20
                    guide_height = self.panel_rect.height - 80
                    self.kitchen_guide_system = KitchenGuideSystem(guide_x, guide_y, guide_width, guide_height)
                    if self.pending_guide_data:
                        self.kitchen_guide_system.guide_manager.restore_save_data(self.pending_guide_data)
                    self.kitchen_guide_system.set_callbacks({
                        "add_to_inventory": self.add_to_inventory,
                        "gain_equipment": Equipment_System.gain_equipment,
                        "add_pet": lambda name: self.pet_system.add_pet(name) if self.pet_system else None
                    })
                self.kitchen_guide_system.update()
                self.kitchen_guide_system.draw(screen)

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

            elif self.active_panel == "Settings":
               if self.settings_system is None:
                   set_x = self.panel_rect.x + 10
                   set_y = self.panel_rect.y + 50
                   set_width = self.panel_rect.width - 20
                   set_height = self.panel_rect.height - 80
                   self.settings_system = SettingsSystem(set_x, set_y, set_width, set_height)
                   if hasattr(self, 'sync_sfx_callback'):
                        self.settings_system.update_external_sfx = self.sync_sfx_callback
                   self.settings_system.apply_volumes()
                
            
               self.settings_system.draw(screen)
                

    def _draw_prestige_panel(self, screen):
        stars_to_gain = Currency_System.calculate_prestige_rewards(self.current_stage)
        new_start = Currency_System.get_advanced_start(self.current_stage)
        
        current_stars = Currency_System.michelin_stars
        current_mult = Currency_System.get_prestige_multiplier()
    
        try:
            badge_img = pg.image.load("Icon/Prestige_icon.png").convert_alpha()
            badge_img = pg.transform.scale(badge_img, (350, 450))
            badge_rect = badge_img.get_rect(center=(self.panel_rect.centerx, self.panel_rect.centery + 30))
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


# ========== Global instance ==========
panel_manager = PanelManager(1300, 750)

# ========== Button callback for guide ==========
def guide_callback():
    panel_manager.toggle_guide()

# ========== Button list (only Guide button) ==========
buttons = []

GUIDE_BUTTON_X = 305
GUIDE_BUTTON_Y = 12
GUIDE_BUTTON_WIDTH = 40
GUIDE_BUTTON_HEIGHT = 40
guide_button = Main_button(GUIDE_BUTTON_X, GUIDE_BUTTON_Y, 30, 30, "?", (80, 80, 100), (120, 120, 140), guide_callback, icon_name="Guide")
buttons.append(guide_button)

# ========== Assign button list to panel_manager ==========
panel_manager.buttons = buttons