import pygame as pg
import Currency_System
import Equipment_System
import math

try:
    GLOBAL_CLICK = pg.mixer.Sound("Sfx/click.wav")
    GLOBAL_CLICK.set_volume(0.5)
except Exception as e:
    GLOBAL_CLICK = None

pg.init()
pg.font.init()

class CategoryButton:
    def __init__(self, rect, text, category_id):
        self.rect = rect
        self.text = text
        self.category_id = category_id
        self.is_selected = False
        self.font = pg.font.SysFont(None, 18)

    def draw(self, screen):
        color = (100, 100, 150) if self.is_selected else (60, 60, 80)
        pg.draw.rect(screen, color, self.rect)
        pg.draw.rect(screen, (200, 200, 200), self.rect, 1)
        text_surf = self.font.render(self.text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

# =========================
# Companion Class
# =========================
class Companion:
    def __init__(self, name, base_cost, base_damage, circle_pos):
        self.name = name
        self.level = 0
        self.base_cost = base_cost
        self.base_damage = base_damage
        self.cost_growth = 1.07
        self.current_cost = base_cost
        self.circle_pos = circle_pos
        self.radius = 15

    def get_upgrade_cost(self):
        return int(self.current_cost)

    def get_damage(self):
        dmg = self.base_damage * self.level
        dmg *= 2 ** (self.level // 25)   # ×2 every 25 levels
        dmg *= 10 ** (self.level // 100) # ×10 every 100 levels
        return int(dmg)

    def purchase_upgrade(self):
        cost = self.get_upgrade_cost()
        if Currency_System.pocket_money >= cost:
            Currency_System.pocket_money -= cost
            self.level += 1
            self.current_cost = self.base_cost * (self.cost_growth ** self.level)
            print(f"[COMPANION] {self.name} Lv {self.level} → DMG {self.get_damage()}, Next Cost {self.get_upgrade_cost()}")

    def draw_circle(self, screen):
        if self.level > 0:
            pg.draw.circle(screen, (200, 200, 50), self.circle_pos, self.radius)
            font = pg.font.SysFont(None, 16)
            txt = font.render(self.name[0], True, (0, 0, 0))
            screen.blit(txt, txt.get_rect(center=self.circle_pos))

# =========================
# Player Upgrade System
# =========================            
class PlayerUpgradeSystem:
    def __init__(self, x, y, width, height):
        self.rect = pg.Rect(x, y, width, height)
        self.font_title = pg.font.SysFont(None, 32, bold=True)
        self.font_text = pg.font.SysFont(None, 20)
        self.font_small = pg.font.SysFont(None, 16)
        
        # Scrolling feature
        self.scroll_offset = 0
        
        # Category management
        self.current_category = 0  # 0: Player, 1: Companion
        self.category_buttons = []
        self._init_category_buttons()

        # Upgrade tracking (Player)
        self.level = 0
        self.base_cost = 20
        self.common_ratio = 1.05
        self.current_cost = self.base_cost

        self.button_rect = None
        
        self.spicy_ability = None
        self.crispy_ability = None

        # Spicy Surge upgrade tracking
        self.spicy_level = 0
        self.spicy_cost = 20000   # base cost 20k
        self.spicy_ratio = 1.30
        self.spicy_max_level = 30
        self.spicy_damage_boost = 0.0  # cumulative boost

        # Crispy Precision upgrade tracking
        self.crispy_level = 0
        self.crispy_cost = 150000  # base cost 150k
        self.crispy_ratio = 1.25
        self.crispy_max_level = 30
        self.crispy_crit_damage = 0.0
        self.crispy_crit_chance = 0.0

        # Critical Damage upgrade
        self.crit_dmg_level = 0
        self.crit_dmg_cost = 100
        self.crit_dmg_ratio = 1.02
        self.crit_dmg_max = 100
        self.crit_dmg_bonus = 0.0

        # Critical Chance upgrade
        self.crit_chance_level = 0
        self.crit_chance_cost = 250
        self.crit_chance_ratio = 1.02
        self.crit_chance_max = 100
        self.crit_chance_bonus = 0.0

        # Mana Capacity upgrade
        self.mana_cap_level = 0
        self.mana_cap_cost = 500
        self.mana_cap_ratio = 1.02
        self.mana_cap_max = 100
        self.mana_cap_bonus = 0

        # Mana Regen upgrade
        self.mana_regen_level = 0
        self.mana_regen_cost = 750
        self.mana_regen_ratio = 1.02
        self.mana_regen_max = 100
        self.mana_regen_bonus = 0.0

        # Companion 
        monster_rect = pg.Rect(600, 250, 200, 200)  # placeholder, pass actual monster rect
        names = ["Metal Spoon","Metal Fork","Chopstick","Spatula","Whisk",
         "Can Opener","Tongs","Soup Ladle","Fruit Knife","Meat Cleaver"]
        base_costs = [100, 200, 300, 500, 800, 1200, 2000, 3000, 5000, 8000]
        base_damages = [5, 8, 12, 20, 30, 45, 60, 80, 100, 150]

        circle_positions = []
        cx, cy = monster_rect.center
        offset = 60
        circle_positions = [
             (434, 516),  # 1 → Metal Spoon
             (375, 466),  # 2 → Metal Fork
             (337, 409),  # 3 → Chopstick
             (350, 342),  # 4 → Spatula
             (401, 291),  # 5 → Whisk
             (705, 512),  # 6 → Can Opener
             (743, 461),  # 7 → Tongs
             (769, 413),  # 8 → Soup Ladle
             (755, 343),  # 9 → Fruit Knife
             (718, 290) # 10 → Meat Cleaver
            ] 

        self.companions = [
            Companion(names[i], base_costs[i], base_damages[i], circle_positions[i])
            for i in range(len(names))
        ]

        # init base_damage
        if not hasattr(Equipment_System, "base_damage"):
            Equipment_System.base_damage = 1
    
    # Helper to clamp scroll (Limit the scroll length)
    def _clamp_scroll(self, total_height):
        # Ensure scroll_offset stays within valid bounds.
        visible_height = self.rect.height - 100  # leave space for title/buttons
        max_scroll = max(0, total_height - visible_height)
        self.scroll_offset = max(0, min(self.scroll_offset, max_scroll))

    # Add scrollbar in Player Upgrade Panel for easier navigation purposes
    def _draw_scrollbar(self, screen, total_height):
        # Draw a scrollbar on the right side of the panel.
        bar_area_height = self.rect.height - 20  # leave some padding
        bar_x = self.rect.right - 12             # scrollbar width = 8px + padding
        bar_y = self.rect.y + 10
        bar_width = 8

        # Background track
        pg.draw.rect(screen, (80, 80, 100), (bar_x, bar_y, bar_width, bar_area_height))
        pg.draw.rect(screen, (200, 200, 200), (bar_x, bar_y, bar_width, bar_area_height), 1)

        # Scroll thumb size (proportional to visible/total)
        visible_height = self.rect.height - 100
        if total_height <= visible_height:
            thumb_height = bar_area_height
        else:
            thumb_height = max(30, int(bar_area_height * (visible_height / total_height)))

        # Scroll thumb position (proportional to offset)
        max_scroll = max(1, total_height - visible_height)
        scroll_ratio = self.scroll_offset / max_scroll
        thumb_y = bar_y + int((bar_area_height - thumb_height) * scroll_ratio)

        # Thumb rectangle
        pg.draw.rect(screen, (180, 180, 220), (bar_x, thumb_y, bar_width, thumb_height))

    # Get Companion Damage
    def get_companion_damage(self, index):
        return self.companions[index].get_damage()
 
        # ========== Kitchen Guide callback ==========
        self.upgrade_callback = None  # 外部设置的回调函数
        # ===========================================

    def _init_category_buttons(self):
        btn_width = 100
        btn_height = 30
        spacing = 15
        total_width = btn_width * 2 + spacing
        start_x = self.rect.centerx - total_width // 2
        y = self.rect.y + 45
        
        categories = ["Player", "Companion"] # Can add future categories like "Weapon", "Armor" etc.
        for i, cat in enumerate(categories):
            btn_rect = pg.Rect(start_x + i * (btn_width + spacing), y, btn_width, btn_height)
            btn = CategoryButton(btn_rect, cat, i)
            btn.is_selected = (i == self.current_category)
            self.category_buttons.append(btn)

    def set_category(self, category_index):
        """Change the current category and update button states"""
        self.current_category = category_index
        for btn in self.category_buttons:
            btn.is_selected = (btn.category_id == self.current_category)

    def get_upgrade_cost(self):
        return int(self.current_cost)

    def handle_event(self, event):
        # Handle category switching
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
           for btn in self.category_buttons:
               if btn.rect.collidepoint(event.pos):
                  self.set_category(btn.category_id)
                  return  # stop further handling so category switches immediately
        
        # Update scroll_offset when scrolling
        elif event.type == pg.MOUSEBUTTONDOWN:
             if event.button == 4:   # scroll up
                self.scroll_offset -= 20
             elif event.button == 5: # scroll down
                self.scroll_offset += 20

        if self.current_category == 0:  # Player upgrade
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                # YOUR REAL BUTTON IS HERE:
                if self.button_rect and self.button_rect.collidepoint(event.pos):
                    
                    if GLOBAL_CLICK: GLOBAL_CLICK.play()
                    
                    self.purchase_upgrade()

                # Spicy Surge upgrade
                if hasattr(self, "spicy_rect") and self.spicy_rect.collidepoint(event.pos):
                   if self.level >= 50 and self.spicy_level < self.spicy_max_level:
                     if Currency_System.pocket_money >= self.spicy_cost:
                        Currency_System.pocket_money -= self.spicy_cost
                        self.spicy_level += 1
                        self.spicy_damage_boost += 0.15
                        self.spicy_cost = int(self.spicy_cost * self.spicy_ratio)

                        # ✅ Scale mana cost and push into ability
                        if self.spicy_ability:
                           new_mana_cost = int(self.spicy_ability.mana_cost * 1.3)
                           self.spicy_ability.set_upgrade_bonus(self.spicy_damage_boost, new_mana_cost)
                           print(f"[SPICY SURGE] Lv {self.spicy_level} → Damage Boost +{self.spicy_damage_boost:.2f}, Mana Cost {self.spicy_ability.mana_cost}, Next Cost: {self.spicy_cost}")
        
                # Crispy Precision upgrade
                if hasattr(self, "crispy_rect") and self.crispy_rect.collidepoint(event.pos):
                   if self.level >= 125 and self.crispy_level < self.crispy_max_level:
                      if Currency_System.pocket_money >= self.crispy_cost:
                         Currency_System.pocket_money -= self.crispy_cost
                         self.crispy_level += 1
                         self.crispy_crit_damage += 0.25
                         self.crispy_crit_chance += 0.01
                         self.crispy_cost = int(self.crispy_cost * self.crispy_ratio)

                         # ✅ Scale mana cost and push into ability
                         if self.crispy_ability:
                            new_mana_cost = int(self.crispy_ability.mana_cost * 1.3)
                            self.crispy_ability.set_upgrade_bonus(self.crispy_crit_chance, self.crispy_crit_damage, new_mana_cost)
                            print(f"[CRISPY PRECISION] Lv {self.crispy_level} → Crit +{self.crispy_crit_chance:.2f}, Damage +{self.crispy_crit_damage:.2f}, Mana Cost {self.crispy_ability.mana_cost}, Next Cost: {self.crispy_cost}")
                
                # Critical Damage upgrade
                if hasattr(self, "crit_dmg_rect") and self.crit_dmg_rect.collidepoint(event.pos):
                   if self.level >= 50 and self.crit_dmg_level < self.crit_dmg_max:
                      if Currency_System.pocket_money >= self.crit_dmg_cost:
                         Currency_System.pocket_money -= self.crit_dmg_cost
                         self.crit_dmg_level += 1
                         self.crit_dmg_bonus += 0.01  # +1% per upgrade
                         self.crit_dmg_cost = int(self.crit_dmg_cost * self.crit_dmg_ratio)
                         print(f"[CRIT DMG] Lv {self.crit_dmg_level} → +{self.crit_dmg_bonus*100:.1f}% Crit Damage, Next Cost: {self.crit_dmg_cost}")

                # Critical Chance upgrade
                if hasattr(self, "crit_chance_rect") and self.crit_chance_rect.collidepoint(event.pos):
                   if self.level >= 75 and self.crit_chance_level < self.crit_chance_max:
                      if Currency_System.pocket_money >= self.crit_chance_cost:
                         Currency_System.pocket_money -= self.crit_chance_cost
                         self.crit_chance_level += 1
                         self.crit_chance_bonus += 0.001  # +0.1% per upgrade
                         self.crit_chance_cost = int(self.crit_chance_cost * self.crit_chance_ratio)
                         print(f"[CRIT CHANCE] Lv {self.crit_chance_level} → +{self.crit_chance_bonus*100:.2f}% Crit Chance, Next Cost: {self.crit_chance_cost}")

                # Mana Capacity upgrade
                if hasattr(self, "mana_cap_rect") and self.mana_cap_rect.collidepoint(event.pos):
                   if self.level >= 100 and self.mana_cap_level < self.mana_cap_max:
                      if Currency_System.pocket_money >= self.mana_cap_cost:
                         Currency_System.pocket_money -= self.mana_cap_cost
                         self.mana_cap_level += 1
                         self.mana_cap_bonus += 1  # +1 per upgrade
                         self.mana_cap_cost = int(self.mana_cap_cost * self.mana_cap_ratio)
                         if self.spicy_ability and hasattr(self.spicy_ability, "mana_system"):
                            self.spicy_ability.mana_system.max_mana += 1
                            print(f"[MANA CAP] Lv {self.mana_cap_level} → +{self.mana_cap_bonus} Max Mana, Next Cost: {self.mana_cap_cost}")

                # Mana Regen upgrade
                if hasattr(self, "mana_regen_rect") and self.mana_regen_rect.collidepoint(event.pos):
                   if self.level >= 150 and self.mana_regen_level < self.mana_regen_max:
                      if Currency_System.pocket_money >= self.mana_regen_cost:
                         Currency_System.pocket_money -= self.mana_regen_cost
                         self.mana_regen_level += 1
                         self.mana_regen_bonus += 0.1  # +0.1/s per upgrade
                         self.mana_regen_cost = int(self.mana_regen_cost * self.mana_regen_ratio)
                         if self.spicy_ability and hasattr(self.spicy_ability, "mana_system"):
                            self.spicy_ability.mana_system.regen_rate += 0.1
                            print(f"[MANA REGEN] Lv {self.mana_regen_level} → +{self.mana_regen_bonus:.1f}/s Regen, Next Cost: {self.mana_regen_cost}")
  
        elif self.current_category == 1:  # Companion upgrade
             if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                for i, comp in enumerate(self.companions):
                    rect = getattr(self, f"companion_rect_{i}", None)
                    if rect and rect.collidepoint(event.pos):
                       comp.purchase_upgrade()
                       
    # Purchase Upgrade Function                  
    def purchase_upgrade(self):
        cost = self.get_upgrade_cost()
        if Currency_System.pocket_money >= cost:
            Currency_System.pocket_money -= cost
            self.level += 1

            # Apply effect: +1 base damage each upgrade
            Equipment_System.base_damage += 1

            # Milestone: every 50 upgrades multiply damage and spike cost
            if self.level % 50 == 0:
                Equipment_System.base_damage = int(Equipment_System.base_damage * 1.2)
                self.current_cost = int(self.current_cost * 1.5)
            else:
                self.current_cost = self.current_cost * self.common_ratio

            print(f"[UPGRADE] Base Damage Lv {self.level} → {Equipment_System.base_damage}, Next Cost: {self.get_upgrade_cost()}")

            # ==========  Kitchen Guide  ==========
            if self.upgrade_callback:
                self.upgrade_callback()
            # =================================================

    def draw(self, screen):
        clip_rect = self.rect
        screen.set_clip(clip_rect)

        # Panel background
        pg.draw.rect(screen, (40, 40, 60), self.rect)
        pg.draw.rect(screen, (200, 200, 200), self.rect, 2)

        # Draw category buttons
        for btn in self.category_buttons:
            btn.draw(screen)

        # Show diffent content based on category
        if self.current_category == 0:
            self._draw_player_upgrade(screen)
        else:
            self._draw_companion_upgrade(screen)

        screen.set_clip(None)

    def _draw_upgrade_box(self, screen, rect, mouse_pos,
                          unlock_level, current_level, max_level, cost, label):
        if self.level < unlock_level:
            pg.draw.rect(screen, (0, 0, 0), rect)
            txt = self.font_text.render(f"Reach Player Level {unlock_level} to Unlock", True, (255, 255, 255))
            screen.blit(txt, txt.get_rect(center=rect.center))
        elif current_level >= max_level:
            pg.draw.rect(screen, (60, 60, 60), rect)
            txt = self.font_text.render("Max Upgrade Level", True, (255, 255, 255))
            screen.blit(txt, txt.get_rect(center=rect.center))
        else:
            color = (100, 100, 200) if not rect.collidepoint(mouse_pos) else (140, 140, 240)
            pg.draw.rect(screen, color, rect)
            pg.draw.rect(screen, (200, 200, 200), rect, 2)
            txt = self.font_text.render(f"{label} Lv {current_level} - Cost: {cost}", True, (255, 255, 255))
            screen.blit(txt, txt.get_rect(center=rect.center))

    def _draw_player_upgrade(self, screen):
        surface = pg.Surface((self.rect.width, self.rect.height))
        surface.fill((40, 40, 60))
        cost = self.get_upgrade_cost()
        mouse_pos = pg.mouse.get_pos()

        # --- Start vertical offset for upgrades ---
        y_offset = self.rect.y + 100 - self.scroll_offset
        box_height = 50
        spacing = 10

        # Calculate total height of all upgrade boxes
        total_height = (7 * box_height) + (7 * spacing) + 40  # +40 for the title line
        self._clamp_scroll(total_height)

        # Button position
        self.button_rect = pg.Rect(self.rect.x + 20, self.rect.y + 100, self.rect.width - 40, 50)

        # Confirm button color based on affordability and hover state
        if Currency_System.pocket_money >= cost:
            if self.button_rect.collidepoint(mouse_pos):
                btn_color = (0, 180, 180)
            else:
                btn_color = (0, 128, 128)
            text_color = (255, 255, 255)
        else:
            if self.button_rect.collidepoint(mouse_pos):
                btn_color = (140, 140, 140)
            else:
                btn_color = (100, 100, 100)
            text_color = (180, 180, 180)

        # Category: Player Stats Upgrade
        category_text = self.font_title.render("Player Stats Upgrade", True, (255, 220, 100))
        surface.blit(category_text, category_text.get_rect(center=(self.rect.width // 2, y_offset)))
        y_offset += 40

        # Base Damage Upgrade box (scrollable)
        self.button_rect = pg.Rect(self.rect.x + 20, y_offset, self.rect.width - 40, box_height)
        y_offset += box_height + spacing

        if Currency_System.pocket_money >= cost:
            btn_color = (0, 180, 180) if self.button_rect.collidepoint(mouse_pos) else (0, 128, 128)
            text_color = (255, 255, 255)
        else:
            btn_color = (140, 140, 140) if self.button_rect.collidepoint(mouse_pos) else (100, 100, 100)
            text_color = (180, 180, 180)

        pg.draw.rect(screen, btn_color, self.button_rect)
        pg.draw.rect(screen, (200, 200, 200), self.button_rect, 2)
        text = self.font_text.render(
            f"Upgrade Base Damage (Lv {self.level}) - Cost: {cost}", True, text_color
        )
        screen.blit(text, text.get_rect(center=self.button_rect.center))
 
        # Critical Damage upgrade box
        self.crit_dmg_rect = pg.Rect(self.rect.x + 20, y_offset, self.rect.width - 40, box_height)
        self._draw_upgrade_box(screen, self.crit_dmg_rect, mouse_pos,
                               unlock_level=50, current_level=self.crit_dmg_level,
                               max_level=self.crit_dmg_max, cost=self.crit_dmg_cost,
                               label="Critical Damage")
        y_offset += box_height + spacing

        # Critical Chance upgrade box
        self.crit_chance_rect = pg.Rect(self.rect.x + 20, y_offset, self.rect.width - 40, box_height)
        self._draw_upgrade_box(screen, self.crit_chance_rect, mouse_pos,
                               unlock_level=75, current_level=self.crit_chance_level,
                               max_level=self.crit_chance_max, cost=self.crit_chance_cost,
                               label="Critical Chance")
        y_offset += box_height + spacing

        # Mana Capacity upgrade box
        self.mana_cap_rect = pg.Rect(self.rect.x + 20, y_offset, self.rect.width - 40, box_height)
        self._draw_upgrade_box(screen, self.mana_cap_rect, mouse_pos,
                               unlock_level=100, current_level=self.mana_cap_level,
                               max_level=self.mana_cap_max, cost=self.mana_cap_cost,
                               label="Mana Capacity")
        y_offset += box_height + spacing

        # Mana Regen upgrade box
        self.mana_regen_rect = pg.Rect(self.rect.x + 20, y_offset, self.rect.width - 40, box_height)
        self._draw_upgrade_box(screen, self.mana_regen_rect, mouse_pos,
                               unlock_level=150, current_level=self.mana_regen_level,
                               max_level=self.mana_regen_max, cost=self.mana_regen_cost,
                               label="Mana Regen")
        y_offset += box_height + spacing

        # Spicy Surge upgrade box
        self.spicy_rect = pg.Rect(self.rect.x + 20, y_offset, self.rect.width - 40, box_height)
        self._draw_upgrade_box(screen, self.spicy_rect, mouse_pos,
                               unlock_level=200, current_level=self.spicy_level,
                               max_level=self.spicy_max_level, cost=self.spicy_cost,
                               label="Spicy Surge")
        y_offset += box_height + spacing

        # Crispy Precision upgrade box
        self.crispy_rect = pg.Rect(self.rect.x + 20, y_offset, self.rect.width - 40, box_height)
        self._draw_upgrade_box(screen, self.crispy_rect, mouse_pos,
                               unlock_level=250, current_level=self.crispy_level,
                               max_level=self.crispy_max_level, cost=self.crispy_cost,
                               label="Crispy Precision")

        # Draw scrollbar
        self._draw_scrollbar(screen, total_height)

    # Companion Upgrade Box
    def _draw_companion_upgrade(self, screen):
        mouse_pos = pg.mouse.get_pos()
        y_offset = self.rect.y + 100 - self.scroll_offset
        box_height = 40
        spacing = 8

        # Calculate total height of all companion boxes
        total_height = len(self.companions) * (box_height + spacing)
        self._clamp_scroll(total_height)

        self.button_rects = []
        for i, comp in enumerate(self.companions):
            rect = pg.Rect(self.rect.x + 20, y_offset, self.rect.width - 40, box_height)
            setattr(self, f"companion_rect_{i}", rect)
            self.button_rects.append(rect)

            cost = comp.get_upgrade_cost()
            level = comp.level
            dmg = comp.get_damage()

            if Currency_System.pocket_money >= cost:
                color = (0, 180, 180) if rect.collidepoint(mouse_pos) else (0, 128, 128)
                text_color = (255, 255, 255)
            else:
                color = (140, 140, 140) if rect.collidepoint(mouse_pos) else (100, 100, 100)
                text_color = (180, 180, 180)

            pg.draw.rect(screen, color, rect)
            pg.draw.rect(screen, (200, 200, 200), rect, 2)

            text = self.font_text.render(
                f"{comp.name} Lv {level} → DMG {dmg} | Cost: {cost}", True, text_color
            )
            screen.blit(text, text.get_rect(center=rect.center))
  
            y_offset += box_height + spacing

        # Draw scrollbar
        self._draw_scrollbar(screen, total_height)

    # Always draw companions around the monster
    def draw_companions(self, screen):
        for comp in self.companions:
            comp.draw_circle(screen)