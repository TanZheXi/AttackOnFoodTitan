import pygame as pg
import Equipment_System
import Currency_System

class CraftingSystem:
    def __init__(self, x, y, width, height):
        self.rect = pg.Rect(x, y, width, height)
        self.font_title = pg.font.SysFont(None, 48)
        self.font_med = pg.font.SysFont(None, 32)
        self.font_small = pg.font.SysFont(None, 24)

        try:
            self.click_sfx = pg.mixer.Sound("Sound_Effects/Click_sfx.wav")
        except:
            self.click_sfx = None
            print("[WARN] Crafting could not find the sound file!")
        
        self.upgrade_btn_rect = pg.Rect(self.rect.centerx - 180, self.rect.bottom - 90, 360, 100)
        
        # --- NEW: Left and Right Arrow Buttons ---
        arrow_w = 40 
        arrow_h = 40 
        
        # This pushes them 80 pixels away from the center 
        distance_from_center = 20
        
        # This puts them right under Weapon Title
        y_position = self.rect.y + 160

        # Buttons
        left_x = self.rect.centerx - distance_from_center - arrow_w
        self.left_btn = pg.Rect(left_x, y_position, arrow_w, arrow_h)
        
        right_x = self.rect.centerx + distance_from_center
        self.right_btn = pg.Rect(right_x, y_position, arrow_w, arrow_h)
        
        # Tracking the list of weapons
        self.owned_weapons = []
        self.current_index = 0

    def refresh_owned_weapons(self):
        """Finds all the weapons you currently own and loads their icons!"""
        db = Equipment_System.equipment_database
        self.owned_weapons = [name for name, data in db.items() if name != "Player_Data" and data.get("owned", False)]
        
        # Safety check just in case the list shrinks
        if self.current_index >= len(self.owned_weapons):
            self.current_index = max(0, len(self.owned_weapons) - 1)

        # --- NEW: WEAPON ICON CACHE ---
        # Create a dictionary to hold the images so we don't lag the game!
        if not hasattr(self, 'weapon_icons'):
            self.weapon_icons = {}
            
        for weapon_name in self.owned_weapons:
            # If we haven't loaded this specific weapon's picture yet:
            if weapon_name not in self.weapon_icons:
                try:
                    # Assumes your pictures are named exactly like the weapons! 
                    # Example: "Icon/Golden Spatula.png"
                    raw_img = pg.image.load(f"Icon/{weapon_name}.png").convert_alpha()
                    
                    # Scale it to a nice big 160x80 icon for the Forge
                    self.weapon_icons[weapon_name] = pg.transform.scale(raw_img, (360, 120))
                except FileNotFoundError:
                    # If the picture doesn't exist, store None so we can fallback to text
                    self.weapon_icons[weapon_name] = None

    def draw(self, screen):
        # Update the list every frame so it stays accurate
        self.refresh_owned_weapons()

        scraps = Equipment_System.crafting_scraps
        scrap_text = self.font_small.render(f"Scraps: {Currency_System.format_money(scraps)}", True, (200, 200, 200))
        screen.blit(scrap_text, (self.rect.right - scrap_text.get_width() - 20, self.rect.y + 20))

        # If they haven't bought anything yet!
        if not self.owned_weapons:
            warning = self.font_title.render("NO WEAPONS OWNED", True, (150, 150, 150))
            screen.blit(warning, warning.get_rect(center=(self.rect.centerx, self.rect.centery)))
            return

        # 1. Grab the weapon we are currently looking at!
        weapon_name = self.owned_weapons[self.current_index]
        item = Equipment_System.equipment_database.get(weapon_name, {})

        lvl = item.get("level", 1)
        mult = item.get("multiplier", 1.0)
        cost = item.get("scrap_value", 10) * lvl

       # Draw Weapon Title
        icon_surface = self.weapon_icons.get(weapon_name)
        
        if icon_surface:
            # If we successfully loaded a picture, draw it!
            icon_rect = icon_surface.get_rect(center=(self.rect.centerx - 10, self.rect.y + 100))
            screen.blit(icon_surface, icon_rect)
        else:
            # Fallback: If no picture is found, just draw the text name so the game doesn't break
            title_text = self.font_title.render(f"{weapon_name}", True, (255, 215, 0))
            screen.blit(title_text, title_text.get_rect(center=(self.rect.centerx - 30, self.rect.y + 140)))

        # --- FORMAT THE NUMBERS ---
        formatted_mult = Currency_System.format_money(mult)
        formatted_next_mult = Currency_System.format_money(mult + 0.5)
        # --------------------------

        # 1. Level Text
        lvl_text = self.font_med.render(f"Level: {lvl}", True, (200, 255, 200))
        screen.blit(lvl_text, lvl_text.get_rect(center=(self.rect.centerx, self.rect.centery - 30)))

        # 2. Current Multiplier Text (Using formatted number!)
        mult_text = self.font_med.render(f"Damage Multiplier: x{formatted_mult}", True, (100, 255, 100))
        screen.blit(mult_text, mult_text.get_rect(center=(self.rect.centerx, self.rect.centery + 5)))

        # 3. Next Level Preview Text (Using formatted number!)
        preview_text = self.font_small.render(f"Next Level Multiplier: x{formatted_next_mult}", True, (150, 150, 150))
        screen.blit(preview_text, preview_text.get_rect(center=(self.rect.centerx, self.rect.centery + 40)))
        
        # --------------------------------------------------------------

        # 2. Draw the Left/Right Arrows (Only if you own more than 1 weapon)
        if len(self.owned_weapons) > 1:
            pg.draw.rect(screen, (80, 80, 100), self.left_btn, border_radius=10)
            left_text = self.font_title.render("<", True, (255, 255, 255))
            screen.blit(left_text, left_text.get_rect(center=self.left_btn.center))

            pg.draw.rect(screen, (80, 80, 100), self.right_btn, border_radius=10)
            right_text = self.font_title.render(">", True, (255, 255, 255))
            screen.blit(right_text, right_text.get_rect(center=self.right_btn.center))

        # 3. Draw the Upgrade Button
        can_afford = scraps >= cost
        btn_color = (200, 150, 0) if can_afford else (100, 100, 100)
        
        if self.upgrade_btn_rect.collidepoint(pg.mouse.get_pos()) and can_afford:
            btn_color = (255, 200, 50)
            
        pg.draw.rect(screen, btn_color, self.upgrade_btn_rect)
        pg.draw.rect(screen, (255, 255, 255), self.upgrade_btn_rect, 2)
        
        btn_text = self.font_med.render(f"UPGRADE ({Currency_System.format_money(cost)} Scraps)", True, (255, 255, 255))
        screen.blit(btn_text, btn_text.get_rect(center=self.upgrade_btn_rect.center))

    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            if not self.owned_weapons: return
            try:
                from Button_System import GLOBAL_CLICK
            except ImportError:
                GLOBAL_CLICK = None
        
            if len(self.owned_weapons) > 1 and self.left_btn.collidepoint(event.pos):
                if GLOBAL_CLICK: GLOBAL_CLICK.play()
                self.current_index = (self.current_index - 1) % len(self.owned_weapons)

            elif len(self.owned_weapons) > 1 and self.right_btn.collidepoint(event.pos):
                if GLOBAL_CLICK: GLOBAL_CLICK.play()
                self.current_index = (self.current_index + 1) % len(self.owned_weapons)

            elif self.upgrade_btn_rect.collidepoint(event.pos):
                weapon_name = self.owned_weapons[self.current_index]
                if GLOBAL_CLICK: GLOBAL_CLICK.play()
                Equipment_System.upgrade_weapon_by_name(weapon_name)