import pygame as pg
import Currency_System
import Equipment_System

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


class PlayerUpgradeSystem:
    def __init__(self, x, y, width, height):
        self.rect = pg.Rect(x, y, width, height)
        self.font_title = pg.font.SysFont(None, 32, bold=True)
        self.font_text = pg.font.SysFont(None, 20)
        self.font_small = pg.font.SysFont(None, 16)

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

        # Companion (placeholder for future updates)
        self.companion_level = 0
        self.companion_cost = 100

        # init base_damage
        if not hasattr(Equipment_System, "base_damage"):
            Equipment_System.base_damage = 1

        # ========== Kitchen Guide callback ==========
        self.upgrade_callback = None  # Set external callback function
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
        if self.current_category == 0:  # Player upgrade
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                # YOUR REAL BUTTON IS HERE:
                if self.button_rect and self.button_rect.collidepoint(event.pos):
                    
                    if GLOBAL_CLICK: GLOBAL_CLICK.play()
                    
                    self.purchase_upgrade()
                    
        elif self.current_category == 1:  # Companion upgrade
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                if self.button_rect and self.button_rect.collidepoint(event.pos):
                    
                    if GLOBAL_CLICK: GLOBAL_CLICK.play() 
                    
                    print("[COMPANION] Coming soon! Companion upgrade system is under development.")

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

            # ========== 通知 Kitchen Guide 升级完成 ==========
            if self.upgrade_callback:
                self.upgrade_callback()
            # =================================================

    def draw(self, screen):
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

    def _draw_player_upgrade(self, screen):
        cost = self.get_upgrade_cost()
        mouse_pos = pg.mouse.get_pos()

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

        # Draw button
        pg.draw.rect(screen, btn_color, self.button_rect)
        pg.draw.rect(screen, (200, 200, 200), self.button_rect, 2)

        # Text on button
        text = self.font_text.render(
            f"Upgrade Base Damage (Lv {self.level}) - Cost: {cost}", True, text_color
        )
        text_rect = text.get_rect(center=self.button_rect.center)
        screen.blit(text, text_rect)

        # Current damage display
        dmg_text = self.font_text.render(
            f"Current Base Damage: {Equipment_System.base_damage}", True, (200, 200, 220)
        )
        screen.blit(dmg_text, (self.rect.x + 20, self.rect.y + 170))

        # Growth ratio display
        ratio_text = self.font_small.render(
            f"Growth Ratio: {self.common_ratio:.2f} (Spike ×1.5 every 50)", True, (200, 200, 220)
        )
        screen.blit(ratio_text, (self.rect.x + 20, self.rect.y + 200))

    def _draw_companion_upgrade(self, screen): #For future updates for companion system
        mouse_pos = pg.mouse.get_pos()

        # Position the button (same area as player upgrade for consistency)
        self.button_rect = pg.Rect(self.rect.x + 20, self.rect.y + 100, self.rect.width - 40, 50)

        pg.draw.rect(screen, (200, 200, 200), self.button_rect, 2)

        # Button text
        text = self.font_text.render("Companion Upgrade - Coming Soon!", True, (255, 255, 255))
        text_rect = text.get_rect(center=self.button_rect.center)
        screen.blit(text, text_rect)