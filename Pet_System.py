import pygame as pg

pg.init()
pg.font.init()

class Pet:
    def __init__(self, name, rarity, attack_damage, color):
        self.name = name
        self.rarity = rarity
        self.attack_damage = attack_damage
        self.color = color
        self.equipped = False

    def get_rarity_color(self):
        rarity_colors = {
            "common": (200, 200, 200),
            "uncommon": (100, 255, 100),
            "rare": (100, 150, 255),
            "mystic": (170, 100, 255),
            "legendary": (255, 150, 50)
        }
        return rarity_colors.get(self.rarity.lower(), (200, 200, 200))


class PetSystem:
    def __init__(self):
        self.pets = [
            Pet("Pet1", "common", 1, (180, 180, 220)),
            Pet("Pet2", "uncommon", 2, (220, 120, 120)),
            Pet("Pet3", "rare", 3, (150, 150, 200)),
            Pet("Pet4", "mystic", 4, (200, 130, 250)),
            Pet("Pet5", "legendary", 5, (255, 150, 50)),
        ]
        self.max_equip = 3
        self.message = ""
        self.message_timer = 0
        self.buttons_rect = {}

    def get_equipped_pets(self):
        return [pet for pet in self.pets if pet.equipped]

    def get_equipped_count(self):
        return len(self.get_equipped_pets())

    def get_total_damage(self):
        return sum(pet.attack_damage for pet in self.get_equipped_pets())

    def toggle_equip(self, pet_index):
        if pet_index < 0 or pet_index >= len(self.pets):
            return
        pet = self.pets[pet_index]
        if pet.equipped:
            pet.equipped = False
            self.message = f"{pet.name} unequipped."
            self.message_timer = 120
        else:
            if self.get_equipped_count() >= self.max_equip:
                self.message = f"You can ONLY equip {self.max_equip} pets."
                self.message_timer = 120
            else:
                pet.equipped = True
                self.message = f"{pet.name} equipped!"
                self.message_timer = 120

    def update(self):
        if self.message_timer > 0:
            self.message_timer -= 1
        else:
            self.message = ""

    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            for pet_name, rect in self.buttons_rect.items():
                if rect.collidepoint(event.pos):
                    for idx, pet in enumerate(self.pets):
                        if pet.name == pet_name:
                            self.toggle_equip(idx)
                            return True
        return False

    def draw(self, screen, panel_rect, desc_panel_rect):
        if not panel_rect:
            return

        font_title = pg.font.SysFont(None, 28, bold=True)
        font_small = pg.font.SysFont(None, 16)

        # 标题区域
        title_bg_rect = pg.Rect(panel_rect.x + 10, panel_rect.y + 10, panel_rect.width - 20, 40)
        pg.draw.rect(screen, (25, 25, 35), title_bg_rect)
        pg.draw.rect(screen, (255, 220, 100), title_bg_rect, 2)
        
        title = font_title.render("PET INVENTORY", True, (255, 220, 100))
        title_rect = title.get_rect(center=(panel_rect.centerx, panel_rect.y + 30))
        screen.blit(title, title_rect)

        # 背景板
        bg_rect = pg.Rect(panel_rect.x + 10, panel_rect.y + 55, panel_rect.width - 20, panel_rect.height - 64)
        pg.draw.rect(screen, (35, 35, 45), bg_rect)
        pg.draw.rect(screen, (80, 80, 100), bg_rect, 1)

        rarity_order = ["common", "uncommon", "rare", "mystic", "legendary"]
        y_offset = panel_rect.y + 70
        item_height = 50

        self.buttons_rect.clear()

        for rarity in rarity_order:
            pets_in_rarity = [p for p in self.pets if p.rarity.lower() == rarity]
            if not pets_in_rarity:
                continue

            rarity_color = pets_in_rarity[0].get_rarity_color()
            rarity_text = font_small.render(rarity.upper(), True, rarity_color)
            screen.blit(rarity_text, (panel_rect.x + 25, y_offset))
            y_offset += 22

            for pet in pets_in_rarity:
                color = (55, 55, 70) if ((y_offset // item_height) % 2 == 0) else (60, 60, 80)
                item_rect = pg.Rect(panel_rect.x + 25, y_offset, panel_rect.width - 50, item_height - 5)
                pg.draw.rect(screen, color, item_rect)
                pg.draw.rect(screen, (90, 90, 110), item_rect, 1)

                name_text = font_small.render(pet.name, True, (255, 255, 255))
                screen.blit(name_text, (item_rect.x + 10, item_rect.y + 10))

                dmg_text = font_small.render(f"DMG: {pet.attack_damage}", True, (200, 200, 200))
                screen.blit(dmg_text, (item_rect.x + 100, item_rect.y + 10))

                status = "EQUIPPED" if pet.equipped else "NOT EQUIPPED"
                status_color = (100, 200, 100) if pet.equipped else (150, 150, 150)
                status_text = font_small.render(status, True, status_color)
                screen.blit(status_text, (item_rect.x + 180, item_rect.y + 10))

                btn_rect = pg.Rect(item_rect.right - 60, item_rect.y + 8, 50, 25)
                mouse_pos = pg.mouse.get_pos()
                btn_color = (70, 130, 70) if btn_rect.collidepoint(mouse_pos) else (50, 100, 50)
                pg.draw.rect(screen, btn_color, btn_rect)
                pg.draw.rect(screen, (150, 200, 150), btn_rect, 1)
                btn_text = font_small.render("EQUIP" if not pet.equipped else "UNEQUIP", True, (255, 255, 255))
                btn_text_rect = btn_text.get_rect(center=btn_rect.center)
                screen.blit(btn_text, btn_text_rect)
                self.buttons_rect[pet.name] = btn_rect

                y_offset += item_height
            y_offset += 10

        # 消息显示
        if self.message and self.message_timer > 0:
            msg_font = pg.font.SysFont(None, 20)
            msg_surface = msg_font.render(self.message, True, (255, 255, 150))
            msg_rect = msg_surface.get_rect(center=(panel_rect.centerx, panel_rect.bottom - 20))
            screen.blit(msg_surface, msg_rect)

        # 描述栏
        if desc_panel_rect:
            font_desc = pg.font.SysFont(None, 18)
            font_desc_small = pg.font.SysFont(None, 16)
            
            pg.draw.rect(screen, (50, 50, 65), desc_panel_rect)
            pg.draw.rect(screen, (130, 130, 150), desc_panel_rect, 2)
            
            top_bar = pg.Rect(desc_panel_rect.x, desc_panel_rect.y, desc_panel_rect.width, 5)
            pg.draw.rect(screen, (255, 220, 100), top_bar)
            
            y = desc_panel_rect.y + 15
            title_desc = font_desc.render("YOUR PETS", True, (255, 220, 100))
            title_rect = title_desc.get_rect(center=(desc_panel_rect.centerx, y))
            screen.blit(title_desc, title_rect)
            y += 30
            
            equipped = self.get_equipped_pets()
            if equipped:
                for pet in equipped:
                    pet_name_text = font_desc_small.render(f"• {pet.name} (DMG: {pet.attack_damage})", True, (200, 200, 220))
                    screen.blit(pet_name_text, (desc_panel_rect.x + 15, y))
                    y += 22
            else:
                text = font_desc_small.render("No pet equipped.", True, (150, 150, 150))
                text_rect = text.get_rect(center=(desc_panel_rect.centerx, y + 10))
                screen.blit(text, text_rect)

    def get_save_data(self):
        return [{"name": p.name, "equipped": p.equipped} for p in self.pets]

    def restore_save_data(self, data):
        if not data:
            return
        for saved in data:
            for pet in self.pets:
                if pet.name == saved.get("name"):
                    pet.equipped = saved.get("equipped", False)
                    break