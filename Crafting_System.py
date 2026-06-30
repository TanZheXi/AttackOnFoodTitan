import pygame as pg
import Equipment_System
import Currency_System
from Audio_System import GLOBAL_CLICK

class CraftingSystem:
    def __init__(self, x, y, width, height):
        self.rect = pg.Rect(x, y, width, height)
        self.font_title = pg.font.SysFont(None, 32)
        self.font_med = pg.font.SysFont(None, 22)
        self.font_small = pg.font.SysFont(None, 16)

# LOAD CRAFTING SOUND ---
        try:
            # Make sure you have a sound file named this in your folder!
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
        
        # --- NEW: Confirmation Tracker ---
        self.confirming_upgrade = False

    def refresh_owned_weapons(self):
        db = Equipment_System.equipment_database
        self.owned_weapons = [name for name, data in db.items() if name != "Player_Data" and data.get("owned", False)]
        
        if self.owned_weapons and self.selected_weapon is None:
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

        if not self.owned_weapons:
            warning = self.font_title.render("NO WEAPONS OWNED", True, (150, 150, 150))
            screen.blit(warning, warning.get_rect(center=self.rect.center))
            return

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

        if self.selected_weapon:
            item = Equipment_System.equipment_database.get(self.selected_weapon, {})
            lvl = item.get("level", 1)
            mult = item.get("multiplier", 1.0)
            cost = item.get("scrap_value", 10) * lvl
            
            icon_surface = self.weapon_icons.get(self.selected_weapon)
            if icon_surface:
                screen.blit(icon_surface, icon_surface.get_rect(center=self.weapon_box.center))
            else:
                fallback_txt = self.font_small.render("WEAPON", True, (150,150,150))
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

            # --- NEW: Confirm Button Rendering Logic ---
            can_afford = scraps >= cost
            
            if self.confirming_upgrade:
                # If they clicked it once, turn it RED and ask for confirmation
                btn_color = (200, 50, 50) if self.upgrade_btn_rect.collidepoint(pg.mouse.get_pos()) else (150, 50, 50)
                btn_lbl = self.font_med.render("CONFIRM?", True, (255, 255, 255))
            else:
                # Standard State
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
        screen.blit(grid_title, (self.grid_area.x + 10, self.grid_area.y + 10))

        card_size = 75
        spacing = 15
        cols = 4
        start_x = self.grid_area.x + 20
        start_y = self.grid_area.y + 35
        
        mouse_pos = pg.mouse.get_pos()
        
        for idx, weapon_name in enumerate(self.owned_weapons):
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

    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            # 1. Did they click a weapon in the backpack grid?
            for weapon_name, rect in self.grid_buttons.items():
                if rect.collidepoint(event.pos):
                    if GLOBAL_CLICK: GLOBAL_CLICK.play()
                    self.selected_weapon = weapon_name
                    # NEW: Cancel any pending upgrade confirmation if they switch items!
                    self.confirming_upgrade = False
                    return
# 2. Did they click the UPGRADE button?
            if self.selected_weapon and self.upgrade_btn_rect.collidepoint(event.pos):
                item = Equipment_System.equipment_database.get(self.selected_weapon, {})
                lvl = item.get("level", 1)
                cost = item.get("scrap_value", 10) * lvl
                
                if Equipment_System.crafting_scraps >= cost:
                    if GLOBAL_CLICK: GLOBAL_CLICK.play() # Standard click sound
                    
                    # --- Two-step confirmation logic ---
                    if not self.confirming_upgrade:
                        # First Click: Ask for confirmation
                        self.confirming_upgrade = True
                    else:
                        # Second Click: Actually consume the scraps and upgrade
                        Equipment_System.upgrade_weapon_by_name(self.selected_weapon)
                        self.confirming_upgrade = False
                        
                        # --- NEW: PLAY THE HEAVY CRAFTING SOUND HERE! ---
                        if self.craft_sound:
                            self.craft_sound.play()
                        # -------------------------------------------------
                return

            # 3. Saftey Net: If they click anywhere else in the forge, cancel the confirmation!
            self.confirming_upgrade = False