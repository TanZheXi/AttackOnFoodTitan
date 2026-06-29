import pygame as pg
import Currency_System
import math

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


class CompanionSystem:
    def __init__(self, x, y, width, height, monster_rect):
        self.rect = pg.Rect(x, y, width, height)
        self.font_title = pg.font.SysFont(None, 32, bold=True)
        self.font_text = pg.font.SysFont(None, 20)

        names = ["Metal Spoon","Metal Fork","Chopstick","Spatula","Whisk",
                 "Can Opener","Tongs","Soup Ladle","Fruit Knife","Meat Cleaver"]

        base_costs = [100, 200, 300, 500, 800, 1200, 2000, 3000, 5000, 8000]
        base_damages = [5, 8, 12, 20, 30, 45, 60, 80, 100, 150]

        # Position circles around monster
        circle_positions = []
        cx, cy = monster_rect.center
        offset = 60
        for i in range(len(names)):
            angle = (2 * math.pi / len(names)) * i
            circle_positions.append((cx + int(offset * math.cos(angle)),
                                     cy + int(offset * math.sin(angle))))

        self.companions = [
            Companion(names[i], base_costs[i], base_damages[i], circle_positions[i])
            for i in range(len(names))
        ]
        self.button_rects = []

    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            for i, rect in enumerate(self.button_rects):
                if rect.collidepoint(event.pos):
                    self.companions[i].purchase_upgrade()

    def draw(self, screen):
        pg.draw.rect(screen, (40, 40, 60), self.rect)
        pg.draw.rect(screen, (200, 200, 200), self.rect, 2)

        title = self.font_title.render("Companion Upgrades", True, (255, 220, 100))
        screen.blit(title, (self.rect.x + 10, self.rect.y + 10))

        mouse_pos = pg.mouse.get_pos()
        y_offset = self.rect.y + 60
        box_height = 40
        spacing = 8
        self.button_rects = []

        for comp in self.companions:
            rect = pg.Rect(self.rect.x + 20, y_offset, self.rect.width - 40, box_height)
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

        # Draw circles beside monster
        for c in self.companions:
            c.draw_circle(screen)