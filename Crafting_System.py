import pygame as pg
import Equipment_System
import Currency_System
from Audio_System import GLOBAL_CLICK
import os

class CategoryButton:
    def __init__(self, rect, text, category_id):
        self.rect = rect
        self.text = text
        self.category_id = category_id
        self.is_selected = False
        self.font = pg.font.SysFont(None, 14)
        self.icon_image = None

    def draw(self, screen):
        color = (100, 100, 150) if self.is_selected else (60, 60, 80)
        pg.draw.rect(screen, color, self.rect)
        pg.draw.rect(screen, (200, 200, 200), self.rect, 1)
        
        if self.icon_image:
            icon_rect = self.icon_image.get_rect(center=self.rect.center)
            screen.blit(self.icon_image, icon_rect)
        else:
            text_surf = self.font.render(self.text, True, (255, 255, 255))
            text_rect = text_surf.get_rect(center=self.rect.center)
            screen.blit(text_surf, text_rect)


class CraftingSystem:
    def __init__(self, x, y, width, height):
        self.rect = pg.Rect(x, y, width, height)
        self.font_title = pg.font.SysFont(None, 32)
        self.font_med = pg.font.SysFont(None, 22)
        self.font_small = pg.font.SysFont(None, 16)

        # LOAD CRAFTING SOUND ---
        try:
            self.craft_sound = pg.mixer.Sound("Sound_Effects/Upgrade_sfx.mp3") 
            self.craft_sound.set_volume(0.6)
        except Exception as e:
            self.craft_sound = None
            print(f"[WARN] Crafting sound not found: {e}")
        
        # --- LAYOUT SECTIONS ---
        self.forge_area = pg.Rect(self.rect.x + 10, self.rect.y + 50, self.rect.width - 20, 240)
        self.grid_area = pg.Rect(self.rect.x + 10, self.forge_area.bottom + 15, self.rect.width - 20, self.rect.height - 315)
        
        # --- FORGE BOXES ---
        self.box_size = 90
        self.weapon_box = pg.Rect(self.forge_area.centerx - 140, self.forge_area.y + 40, self.box_size, self.box_size)
        self.material_box = pg.Rect(self.forge_area.centerx + 50, self.forge_area.y + 40, self.box_size, self.box_size)
        
        self.upgrade_btn_rect = pg.Rect(self.forge_area.centerx - 100, self.forge_area.bottom - 55, 200, 40)
        
        self.owned_weapons = []
        self.selected_weapon = None
        self.weapon_icons = {}
        self.grid_buttons = {}
        
        self.scroll_offset = 0
        self.confirming_upgrade = False
        
        # --- FILTER TABS ---
        self.current_category = 0
        self.category_map = {
            0: "weapon",
            1: "equipment"
        }
        self.category_buttons = []
        self._init_category_buttons()

    def _init_category_buttons(self):
        btn_width = 80
        btn_height = 25
        spacing = 8
        total_width = btn_width * 2 + spacing
        
        # Position at the top right of the grid area
        start_x = self.grid_area.x + self.grid_area.width - total_width - 15
        y = self.grid_area.y + 8
        
        categories = ["Weapon", "Equipment"]
        icon_names = ["Weapon", "Equipment"]
        
        for i, (cat, icon_name) in enumerate(zip(categories, icon_names)):
            btn_rect = pg.Rect(start_x + i * (btn_width + spacing), y, btn_width, btn_height)
            btn = CategoryButton(btn_rect, cat, i)
            btn.is_selected = (i == self.current_category)
            
            icon_folder = os.path.join(os.path.dirname(__file__), "Icon")
            icon_path = os.path.join(icon_folder, f"{icon_name}.png")
            try:
                if os.path.exists(icon_path):
                    original = pg.image.load(icon_path).convert_alpha()
                    bounding_rect = original.get_bounding_rect()
                    if bounding_rect.width > 0 and bounding_rect.height > 0:
                        original = original.subsurface(bounding_rect)
                    
                    target_w = btn_width - 10
                    target_h = btn_height - 6
                    original_w = original.get_width()
                    original_h = original.get_height()
                    
                    scale = min(target_w / original_w, target_h / original_h)
                    new_w = int(original_w * scale)
                    new_h = int(original_h * scale)
                    
                    btn.icon_image = pg.transform.scale(original, (new_w, new_h))
            except Exception as e:
                pass
            
            self.category_buttons.append(btn)

    def _get_item_category(self, item_name):
        weapon_items = ["Rusty Spatula", "Golden Spatula", "Chef's Wok", "Mythic Pan", "OP WEAPON", "Beginner Wok"]
        equipment_items = ["Master Chef Hat", "Titanium Apron", "Roasted Garlic Aroma", "Speed Boots", "Magic Ring", "Beginner Apron"]
        
        if item_name in weapon_items:
            return "weapon"
        elif item_name in equipment_items:
            return "equipment"
        return "weapon"

    def set_category(self, category_index):
        self.current_category = category_index
        self.scroll_offset = 0
        self.selected_weapon = None
        self.confirming_upgrade = False
        for btn in self.category_buttons:
            btn.is_selected = (btn.category_id == self.current_category)
        self.refresh_owned_weapons()

    def refresh_owned_weapons(self):
        db = Equipment_System.equipment_database
        target_category = self.category_map.get(self.current_category, "weapon")
        
        # Only load owned items that match the current category filter
        self.owned_weapons = []
        for name, data in db.items():
            if name != "Player_Data" and data.get("owned", False):
                if self._get_item_category(name) == target_category:
                    self.owned_weapons.append(name)
        
        # Auto-select the first item if the list changed
        if self.owned_weapons and self.selected_weapon not in self.owned_weapons:
            self.selected_weapon = self.owned_weapons[0]

        for weapon_name in self.owned_weapons:
            if weapon_name not in self.weapon_icons:
                try:
                    raw_img = pg.image.load(f"Icon/{weapon_name}.png").convert_alpha()
                    self.weapon_icons[weapon_name] = pg.transform.scale(raw_img, (70, 70))
                except FileNotFoundError:
                    self.weapon_icons[weapon_name] = None

    def draw_arrow(self, screen, x, y):
        """Draws a cool pixel-art style arrow between the two boxes, pointing LEFT"""
        arrow_color = (255, 100, 100)
        points = [
            (x + 15, y - 8), (x - 5, y - 8),   
            (x - 5, y - 18),                   
            (x - 25, y),                       
            (x - 5, y + 18),                   
            (x - 5, y + 8), (x + 15, y + 8)    
        ]
        pg.draw.polygon(screen, arrow_color, points)
        pg.draw.polygon(screen, (150, 50, 50), points, 2)

    def draw(self, screen):
        self.refresh_owned_weapons()
        self.grid_buttons.clear()
        
        scraps = Equipment_System.crafting_scraps
        scrap_text = self.font_med.render(f"Total Scraps: {Currency_System.format_money(scraps)}", True, (200, 200, 200))
        screen.blit(scrap_text, (self.rect.x + 15, self.rect.y + 15))

        # 1. DRAW THE TOP FORGE AREA
        pg.draw.rect(screen, (55, 45, 45), self.forge_area, border_radius=8)
        pg.draw.rect(screen, (120, 80, 80), self.forge_area, 3, border_radius=8)
        
        forge_title = self.font_med.render("- UPGRADE PANEL -", True, (255, 200, 100))
        screen.blit(forge_title, forge_title.get_rect(center=(self.forge_area.centerx, self.forge_area.y + 20)))

        pg.draw.rect(screen, (35, 35, 40), self.weapon_box, border_radius=6)
        pg.draw.rect(screen, (100, 100, 120), self.weapon_box, 2, border_radius=6)
        
        pg.draw.rect(screen, (35, 35, 40), self.material_box, border_radius=6)
        pg.draw.rect(screen, (100, 100, 120), self.material_box, 2, border_radius=6)
        
        self.draw_arrow(screen, self.forge_area.centerx, self.forge_area.y + 85)

        if not self.owned_weapons:
            warning = self.font_title.render(f"NO {self.category_map[self.current_category].upper()}S OWNED", True, (150, 150, 150))
            screen.blit(warning, warning.get_rect(center=self.forge_area.center))
        elif self.selected_weapon:
            item = Equipment_System.equipment_database.get(self.selected_weapon, {})
            lvl = item.get("level", 1)
            mult = item.get("multiplier", 1.0)
            cost = item.get("scrap_value", 10) * lvl
            
            icon_surface = self.weapon_icons.get(self.selected_weapon)
            if icon_surface:
                screen.blit(icon_surface, icon_surface.get_rect(center=self.weapon_box.center))
            else:
                fallback_txt = self.font_small.render("ITEM", True, (150,150,150))
                screen.blit(fallback_txt, fallback_txt.get_rect(center=self.weapon_box.center))

            cost_txt1 = self.font_med.render(f"{Currency_System.format_money(cost)}", True, (255, 215, 0))
            cost_txt2 = self.font_small.render("Scraps", True, (200, 200, 200))
            screen.blit(cost_txt1, cost_txt1.get_rect(center=(self.material_box.centerx, self.material_box.centery - 10)))
            screen.blit(cost_txt2, cost_txt2.get_rect(center=(self.material_box.centerx, self.material_box.centery + 15)))

            stat_y = self.weapon_box.bottom + 15
            name_text = self.font_med.render(f"{self.selected_weapon} (Lv.{lvl})", True, (255, 255, 255))
            screen.blit(name_text, name_text.get_rect(center=(self.weapon_box.centerx, stat_y)))
            
            mult_text = self.font_small.render(f"DMG: x{Currency_System.format_money(mult)}", True, (100, 255, 100))
            screen.blit(mult_text, mult_text.get_rect(center=(self.weapon_box.centerx, stat_y + 18)))

            # --- Confirm Button Rendering Logic ---
            can_afford = scraps >= cost
            
            if self.confirming_upgrade:
                btn_color = (200, 50, 50) if self.upgrade_btn_rect.collidepoint(pg.mouse.get_pos()) else (150, 50, 50)
                btn_lbl = self.font_med.render("CONFIRM?", True, (255, 255, 255))
            else:
                btn_color = (200, 150, 0) if can_afford else (80, 80, 80)
                if self.upgrade_btn_rect.collidepoint(pg.mouse.get_pos()) and can_afford:
                    btn_color = (255, 200, 50)
                btn_lbl = self.font_med.render("UPGRADE", True, (255, 255, 255))
                
            pg.draw.rect(screen, btn_color, self.upgrade_btn_rect, border_radius=4)
            pg.draw.rect(screen, (255, 255, 255), self.upgrade_btn_rect, 1, border_radius=4)
            screen.blit(btn_lbl, btn_lbl.get_rect(center=self.upgrade_btn_rect.center))

        # 2. DRAW THE BOTTOM GRID AREA
        pg.draw.rect(screen, (40, 40, 50), self.grid_area, border_radius=8)
        pg.draw.rect(screen, (80, 80, 100), self.grid_area, 2, border_radius=8)
        
        grid_title = self.font_small.render("BACKPACK (Click to slot)", True, (150, 150, 170))
        screen.blit(grid_title, (self.grid_area.x + 10, self.grid_area.y + 14))

        for btn in self.category_buttons:
            btn.draw(screen)

        card_size = 75
        spacing = 15
        cols = 4
        start_x = self.grid_area.x + 20
        start_y = self.grid_area.y + 42
        
        mouse_pos = pg.mouse.get_pos()
        
        # Apply scrolling offsets
        start_index = self.scroll_offset * cols
        visible_items = self.owned_weapons[start_index : start_index + (cols * 2)]
        
        for idx, weapon_name in enumerate(visible_items):
            row = idx // cols
            col = idx % cols
            
            x = start_x + col * (card_size + spacing)
            y = start_y + row * (card_size + spacing)
            
            card_rect = pg.Rect(x, y, card_size, card_size)
            self.grid_buttons[weapon_name] = card_rect
            
            is_hovered = card_rect.collidepoint(mouse_pos)
            if weapon_name == self.selected_weapon:
                bg_color = (100, 150, 100) 
                border_color = (255, 255, 0)
            elif is_hovered:
                bg_color = (80, 80, 100)
                border_color = (200, 200, 255)
            else:
                bg_color = (55, 55, 70)
                border_color = (90, 90, 110)
                
            pg.draw.rect(screen, bg_color, card_rect, border_radius=6)
            pg.draw.rect(screen, border_color, card_rect, 2 if is_hovered else 1, border_radius=6)
            
            grid_icon = self.weapon_icons.get(weapon_name)
            if grid_icon:
                tiny_icon = pg.transform.scale(grid_icon, (50, 50))
                screen.blit(tiny_icon, tiny_icon.get_rect(center=card_rect.center))

        # Scrollbar (Shows up if there are more than 2 rows)
        if len(self.owned_weapons) > cols * 2:
            scroll_bg = pg.Rect(self.grid_area.right - 12, start_y, 8, card_size * 2 + spacing)
            pg.draw.rect(screen, (40, 40, 50), scroll_bg)
            pg.draw.rect(screen, (80, 80, 100), scroll_bg, 1)
            
            max_scroll = max(0, ((len(self.owned_weapons) - 1) // cols) - 1)
            if max_scroll > 0:
                scroll_ratio = self.scroll_offset / max_scroll
                scroll_bar_height = max(20, scroll_bg.height * 0.3)
                scroll_bar_y = scroll_bg.y + int(scroll_ratio * (scroll_bg.height - scroll_bar_height))
                scroll_bar = pg.Rect(scroll_bg.x, scroll_bar_y, scroll_bg.width, scroll_bar_height)
                pg.draw.rect(screen, (150, 150, 170), scroll_bar)
                pg.draw.rect(screen, (200, 200, 220), scroll_bar, 1)

    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1:
                # 1. Did they click a category tab?
                for btn in self.category_buttons:
                    if btn.rect.collidepoint(event.pos):
                        if GLOBAL_CLICK: GLOBAL_CLICK.play()
                        self.set_category(btn.category_id)
                        return

                # 2. Did they click an item in the backpack grid?
                for weapon_name, rect in self.grid_buttons.items():
                    if rect.collidepoint(event.pos):
                        if GLOBAL_CLICK: GLOBAL_CLICK.play()
                        self.selected_weapon = weapon_name
                        self.confirming_upgrade = False
                        return

                # 3. Did they click the UPGRADE button?
                if self.selected_weapon and self.upgrade_btn_rect.collidepoint(event.pos):
                    item = Equipment_System.equipment_database.get(self.selected_weapon, {})
                    lvl = item.get("level", 1)
                    cost = item.get("scrap_value", 10) * lvl
                    
                    if Equipment_System.crafting_scraps >= cost:
                        if GLOBAL_CLICK: GLOBAL_CLICK.play() 
                        
                        if not self.confirming_upgrade:
                            self.confirming_upgrade = True
                        else:
                            Equipment_System.upgrade_weapon_by_name(self.selected_weapon)
                            self.confirming_upgrade = False
                            
                            if self.craft_sound:
                                self.craft_sound.play()
                    return

                # 4. Saftey Net: If they click anywhere else in the forge, cancel the confirmation!
                self.confirming_upgrade = False

            # Scroll with mouse wheel
            elif event.button == 4:
                self.scroll_offset = max(0, self.scroll_offset - 1)
            elif event.button == 5:
                cols = 4
                max_scroll = max(0, ((len(self.owned_weapons) - 1) // cols) - 1)
                self.scroll_offset = min(max_scroll, self.scroll_offset + 1)