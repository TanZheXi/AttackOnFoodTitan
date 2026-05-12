import pygame as pg
import Currency_System
import Gear_System

pg.init()
pg.font.init()

class PlayerUpgradeSystem:
    def __init__(self, x, y, width, height):
        self.rect = pg.Rect(x, y, width, height)
        self.font_title = pg.font.SysFont(None, 32, bold=True)
        self.font_text = pg.font.SysFont(None, 20)

        # Upgrade tracking
        self.level = 0
        self.base_cost = 20          # Start cost
        self.common_ratio = 1.05     # Normal growth ratio
        self.current_cost = self.base_cost

        # Button rect
        self.button_rect = pg.Rect(self.rect.x + 20, self.rect.y + 80, self.rect.width - 40, 50)

        # Initialize base damage in Gear_System if not present
        if not hasattr(Gear_System, "base_damage"):
            Gear_System.base_damage = 1

    def get_upgrade_cost(self):
        return int(self.current_cost)

    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            if self.button_rect.collidepoint(event.pos):
                self.purchase_upgrade()

    def purchase_upgrade(self):
        cost = self.get_upgrade_cost()
        if Currency_System.pocket_money >= cost:
            Currency_System.pocket_money -= cost
            self.level += 1

            # Apply effect: +1 base damage each upgrade
            Gear_System.base_damage += 1

            # Milestone: every 50 upgrades multiply damage and spike cost
            if self.level % 50 == 0:
                Gear_System.base_damage = int(Gear_System.base_damage * 1.2)
                self.current_cost = int(self.current_cost * 1.5)  # spike cost
            else:
                self.current_cost = self.current_cost * self.common_ratio  # normal growth

            print(f"[UPGRADE] Base Damage Lv {self.level} → {Gear_System.base_damage}, Next Cost: {self.get_upgrade_cost()}")

    def draw(self, screen):
        # Panel background
        pg.draw.rect(screen, (40, 40, 60), self.rect)
        pg.draw.rect(screen, (200, 200, 200), self.rect, 2)

        # Title
        title = self.font_title.render("Player Upgrade", True, (255, 220, 100))
        screen.blit(title, (self.rect.x + 10, self.rect.y + 10))

        # Determine button color based on affordability + hover
        cost = self.get_upgrade_cost()
        mouse_pos = pg.mouse.get_pos()

        if Currency_System.pocket_money >= cost:
            if self.button_rect.collidepoint(mouse_pos):
                btn_color = (0, 180, 180)   # Bright teal on hover
            else:
                btn_color = (0, 128, 128)   # Normal teal
            text_color = (255, 255, 255)
        else:
            if self.button_rect.collidepoint(mouse_pos):
                btn_color = (140, 140, 140) # Light grey on hover
            else:
                btn_color = (100, 100, 100) # Normal grey
            text_color = (180, 180, 180)

        # Draw button
        pg.draw.rect(screen, btn_color, self.button_rect)
        pg.draw.rect(screen, (200, 200, 200), self.button_rect, 2)

        # Button text
        text = self.font_text.render(
            f"Upgrade Base Damage (Lv {self.level}) - Cost: {cost}", True, text_color
        )
        text_rect = text.get_rect(center=self.button_rect.center)
        screen.blit(text, text_rect)

        # Current damage display
        dmg_text = self.font_text.render(
            f"Current Base Damage: {Gear_System.base_damage}", True, (200, 200, 220)
        )
        screen.blit(dmg_text, (self.rect.x + 20, self.rect.y + 150))

        # Current ratio display
        ratio_text = self.font_text.render(
            f"Growth Ratio: {self.common_ratio:.2f} (Spike ×1.5 every 50)", True, (200, 200, 220)
        )
        screen.blit(ratio_text, (self.rect.x + 20, self.rect.y + 180))