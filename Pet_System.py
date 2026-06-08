import pygame as pg

try:
    GLOBAL_CLICK = pg.mixer.Sound("Sfx/click.wav")
    GLOBAL_CLICK.set_volume(0.5)
except Exception as e:
    GLOBAL_CLICK = None

pg.init()
pg.font.init()

class Pet:
    def __init__(self, name, rarity, attack_damage, color, price=0):
        self.name = name
        self.rarity = rarity.lower()
        self.attack_damage = attack_damage
        self.color = color
        self.price = price
        self.owned = False
        self.equipped = False

    def get_rarity_color(self):
        rarity_colors = {
            "common": (200, 200, 200),
            "uncommon": (100, 255, 100),
            "rare": (100, 150, 255),
            "epic": (170, 100, 255),
            "legendary": (255, 150, 50),
            "mythic": (255, 100, 100)
        }
        return rarity_colors.get(self.rarity, (200, 200, 200))


class PetSystem:
    def __init__(self):
        self.all_pets = [
            # Common (Pet Shop)
            Pet("Baby Slime", "common", 1, (100, 200, 100), price=100),
            Pet("Bat", "common", 1, (100, 100, 150), price=100),
            # Uncommon
            Pet("Wolf", "uncommon", 2, (150, 150, 200), price=300),
            Pet("Hawk", "uncommon", 2, (200, 180, 100), price=300),
            # Rare
            Pet("Tiger", "rare", 3, (200, 150, 50), price=800),
            Pet("Dragon", "rare", 3, (200, 100, 50), price=800),
            # Epic
            Pet("Fire Spirit", "epic", 4, (255, 100, 50), price=2000),
            Pet("Fairy", "epic", 4, (200, 150, 255), price=2000),
            # Legendary
            Pet("Dragon Whelp", "legendary", 5, (100, 200, 255), price=5000),
            Pet("Hydra", "legendary", 5, (100, 200, 255), price=5000),
            Pet("Cerberus", "legendary", 5, (255, 100, 100), price=5000),
            # Mythic
            Pet("Phoenix", "mythic", 10, (255, 100, 50), price=30000),
            Pet("Bahamut", "mythic", 10, (255, 215, 0), price=15000),
        ]
        
        self.max_equip = 3
        self.message = ""
        self.message_timer = 0
        self.buttons_rect = {}
        
        # Hover effects
        self.hovered_index = -1
        self.selected_pet = None
        
        # Categorization settings
        self.categories = ["Common", "Uncommon", "Rare", "Epic", "Legendary", "Mythic"]
        self.category_map = {
            0: "common",
            1: "uncommon", 
            2: "rare",
            3: "epic",
            4: "legendary",
            5: "mythic"
        }
        self.current_category = 0
        self.category_buttons = []
        
        # Scroll offset
        self.scroll_offset = 0
        self.max_scroll = max(0, len(self.categories) - 4)
        
        # Pets currently displayed (only owned ones)
        self.pets = []
        self.update_pets_by_category()
        
        self.panel_rect = None
        self.desc_panel_rect = None
        
        # ========== Kitchen Guide callback ==========
        self.guide_callback = None  # 外部设置的回调函数
        # ===========================================

    def update_pets_by_category(self):
        """Filter owned pets based on the current category"""
        category = self.category_map.get(self.current_category, "common")
        self.pets = [pet for pet in self.all_pets if pet.owned and pet.rarity == category]
        print(f"[PET] Updated pets: {len(self.pets)} in category {category}")

    def refresh_display(self):
        """Refresh the display list"""
        self.update_pets_by_category()

    def set_category(self, category_index):
        self.current_category = category_index
        self.update_pets_by_category()
        self.hovered_index = -1
        self.selected_pet = None

    def scroll_categories(self, direction):
        if direction == "left":
            self.scroll_offset = max(0, self.scroll_offset - 1)
        elif direction == "right":
            self.scroll_offset = min(self.max_scroll, self.scroll_offset + 1)

    def get_owned_pets(self):
        return [pet for pet in self.all_pets if pet.owned]

    def get_equipped_pets(self):
        return [pet for pet in self.all_pets if pet.equipped]

    def get_equipped_count(self):
        return len(self.get_equipped_pets())

    def get_total_damage(self):
        return sum(pet.attack_damage for pet in self.get_equipped_pets())

    def add_pet(self, pet_name):
        """Add a pet to the inventory by name. Returns True if added or already owned, False if not found."""
        print(f"[PET] add_pet called with: '{pet_name}'")
        
        for pet in self.all_pets:
            if pet.name == pet_name:
                if not pet.owned:
                    pet.owned = True
                    self.update_pets_by_category()
                    print(f"[PET] ✓ Added '{pet_name}' to pet inventory!")
                    return True
                else:
                    print(f"[PET] '{pet_name}' already owned!")
                    return True
        print(f"[PET] ✗ Pet '{pet_name}' not found in all_pets!")
        return False

    def toggle_equip(self, pet_index):
        if pet_index < 0 or pet_index >= len(self.pets):
            return
        pet = self.pets[pet_index]
        if not pet.owned:
            return
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
                
                # ========== 通知 Kitchen Guide 宠物已装备 ==========
                if self.guide_callback:
                    self.guide_callback()
                # =================================================

    def update(self):
        if self.message_timer > 0:
            self.message_timer -= 1
        else:
            self.message = ""

    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            
            # Detect left and right scroll arrows
            if hasattr(self, 'arrow_left_rect') and self.arrow_left_rect.collidepoint(event.pos):
                if GLOBAL_CLICK: GLOBAL_CLICK.play()
                self.scroll_categories("left")
                return
            if hasattr(self, 'arrow_right_rect') and self.arrow_right_rect.collidepoint(event.pos):
                if GLOBAL_CLICK: GLOBAL_CLICK.play()
                self.scroll_categories("right")
                return
            
            # Handle pet equip buttons
            for key, rect in self.buttons_rect.items():
                if rect.collidepoint(event.pos):
                    if GLOBAL_CLICK: GLOBAL_CLICK.play()
                    
                    if key.startswith("equip_"):
                        idx = int(key.split("_")[1])
                        self.toggle_equip(idx)
                    return
        
        elif event.type == pg.MOUSEMOTION:
            self.hovered_index = -1
            self.selected_pet = None
            mouse_pos = event.pos
            
            if not self.pets:
                return
            
            cols = 2
            item_width = (self.panel_rect.width - 45) // cols
            item_height = 80
            start_x = self.panel_rect.x + 18
            start_y = self.panel_rect.y + 95
            spacing_x = 12
            spacing_y = 10
            
            for idx, pet in enumerate(self.pets):
                row = idx // cols
                col = idx % cols
                x = start_x + col * (item_width + spacing_x)
                y = start_y + row * (item_height + spacing_y)
                item_rect = pg.Rect(x, y, item_width, item_height)
                if item_rect.collidepoint(mouse_pos):
                    self.hovered_index = idx
                    self.selected_pet = pet
                    break

    def reset_on_prestige(self):
        for pet in self.all_pets:
            pet.equipped = False
        self.message = "All pets unequipped due to prestige!"
        self.message_timer = 120
        print(f"[PET] All pets unequipped on prestige.")

    def restore_save_data(self, data):
        if not data:
            return
        for saved in data:
            for pet in self.all_pets:
                if pet.name == saved.get("name"):
                    pet.owned = saved.get("owned", False)
                    pet.equipped = saved.get("equipped", False)
                    break
        self.update_pets_by_category()
        print(f"[PET] Restored {len(data)} pets from save data")

    def get_save_data(self):
        return [{"name": p.name, "owned": p.owned, "equipped": p.equipped} for p in self.all_pets]

    def _get_pet_description(self, pet_name):
        descriptions = {
            "Baby Slime": "A jiggly baby slime that loves to bounce.",
            "Bat": "A swift bat that strikes from above.",
            "Wolf": "A loyal wolf that fights alongside you.",
            "Hawk": "A keen-eyed hawk that never misses.",
            "Tiger": "A fierce tiger with powerful claws.",
            "Dragon": "A small dragon that breathes fire.",
            "Phoenix": "A majestic bird that rises from ashes.",
            "Unicorn": "A magical unicorn that brings luck.",
            "Hydra": "A multi-headed beast of legend.",
            "Cerberus": "A three-headed guardian of the underworld.",
            "Bahamut": "The king of dragons, immensely powerful."
        }
        return descriptions.get(pet_name, "A mysterious pet with great potential.")

    def _wrap_text(self, text, max_width):
        font = pg.font.SysFont(None, 14)
        words = text.split(' ')
        lines = []
        current_line = []
        for word in words:
            test_line = ' '.join(current_line + [word])
            if font.size(test_line)[0] <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        if current_line:
            lines.append(' '.join(current_line))
        return lines if lines else [text]

    def draw(self, screen, panel_rect, desc_panel_rect):
        if not panel_rect:
            return
        
        self.panel_rect = panel_rect
        self.desc_panel_rect = desc_panel_rect
        
        font_small = pg.font.SysFont(None, 14)
        font_medium = pg.font.SysFont(None, 18)
        
        # ========== Black bolded background ==========
        bg_rect = pg.Rect(panel_rect.x + 10, panel_rect.y + 50, panel_rect.width - 20, panel_rect.height - 60)
        pg.draw.rect(screen, (45, 45, 55), bg_rect)
        pg.draw.rect(screen, (150, 150, 170), bg_rect, 2)
        
        # ========== Category button bar ==========
        btn_width = 70
        btn_height = 24
        btn_spacing = 6
        visible_buttons = 4
        btn_area_width = btn_width * visible_buttons + btn_spacing * (visible_buttons - 1)
        btn_area_start_x = panel_rect.centerx - btn_area_width // 2
        btn_y = panel_rect.y + 58
        
        self.category_buttons = []
        
        for i in range(visible_buttons):
            btn_idx = self.scroll_offset + i
            if btn_idx >= len(self.categories):
                break
            cat = self.categories[btn_idx]
            x = btn_area_start_x + i * (btn_width + btn_spacing)
            btn_rect = pg.Rect(x, btn_y, btn_width, btn_height)
            is_selected = (btn_idx == self.current_category)
            color = (100, 100, 150) if is_selected else (60, 60, 80)
            pg.draw.rect(screen, color, btn_rect)
            pg.draw.rect(screen, (200, 200, 200), btn_rect, 1)
            font = pg.font.SysFont(None, 12)
            text = font.render(cat, True, (255, 255, 255))
            text_rect = text.get_rect(center=btn_rect.center)
            screen.blit(text, text_rect)
            self.category_buttons.append({
                "rect": btn_rect,
                "text": cat,
                "category_id": btn_idx,
                "is_selected": is_selected
            })
        
        if len(self.categories) > visible_buttons:
            arrow_left_rect = pg.Rect(btn_area_start_x - 25, btn_y, 20, btn_height)
            pg.draw.rect(screen, (60, 60, 80), arrow_left_rect)
            pg.draw.rect(screen, (150, 150, 170), arrow_left_rect, 1)
            arrow_font = pg.font.SysFont(None, 16)
            arrow_text = arrow_font.render("<", True, (255, 255, 255))
            arrow_text_rect = arrow_text.get_rect(center=arrow_left_rect.center)
            screen.blit(arrow_text, arrow_text_rect)
            self.arrow_left_rect = arrow_left_rect
            
            arrow_right_rect = pg.Rect(btn_area_start_x + btn_area_width + 5, btn_y, 20, btn_height)
            pg.draw.rect(screen, (60, 60, 80), arrow_right_rect)
            pg.draw.rect(screen, (150, 150, 170), arrow_right_rect, 1)
            arrow_text = arrow_font.render(">", True, (255, 255, 255))
            arrow_text_rect = arrow_text.get_rect(center=arrow_right_rect.center)
            screen.blit(arrow_text, arrow_text_rect)
            self.arrow_right_rect = arrow_right_rect
        
        # ========== Pet list ==========
        cols = 2
        available_width = panel_rect.width - 40
        spacing_x = 12
        spacing_y = 10
        item_width = (available_width - spacing_x) // cols
        item_height = 80
        
        start_x = panel_rect.x + 18
        start_y = panel_rect.y + 95
        
        self.buttons_rect.clear()
        
        if not self.pets:
            empty_text = font_medium.render("Empty", True, (150, 150, 150))
            empty_rect = empty_text.get_rect(center=(panel_rect.centerx, panel_rect.centery + 20))
            screen.blit(empty_text, empty_rect)
        else:
            for idx, pet in enumerate(self.pets):
                row = idx // cols
                col = idx % cols
                x = start_x + col * (item_width + spacing_x)
                y = start_y + row * (item_height + spacing_y)
                item_rect = pg.Rect(x, y, item_width, item_height)
                
                if pet.equipped:
                    color = (70, 100, 70)
                else:
                    color = (55, 55, 70) if row % 2 == 0 else (60, 60, 80)
                
                pg.draw.rect(screen, color, item_rect)
                
                if self.hovered_index == idx:
                    pg.draw.rect(screen, (255, 220, 100), item_rect, 2)
                else:
                    pg.draw.rect(screen, (90, 90, 110), item_rect, 1)
                
                name_text = font_medium.render(pet.name, True, (255, 255, 200))
                screen.blit(name_text, (item_rect.x + 8, item_rect.y + 8))
                
                dmg_text = font_small.render(f"DMG: {pet.attack_damage}", True, (200, 200, 220))
                screen.blit(dmg_text, (item_rect.x + 8, item_rect.y + 35))
                
                if pet.equipped:
                    status_text = font_small.render("EQUIPPED", True, (100, 255, 100))
                    screen.blit(status_text, (item_rect.x + 8, item_rect.y + 58))
                    btn_text = "UNEQUIP"
                else:
                    status_text = font_small.render("NOT EQUIPPED", True, (150, 150, 150))
                    screen.blit(status_text, (item_rect.x + 8, item_rect.y + 58))
                    btn_text = "EQUIP"
                
                btn_rect = pg.Rect(item_rect.right - 55, item_rect.y + 50, 50, 25)
                mouse_pos = pg.mouse.get_pos()
                btn_color = (70, 100, 130) if btn_rect.collidepoint(mouse_pos) else (50, 70, 100)
                pg.draw.rect(screen, btn_color, btn_rect)
                pg.draw.rect(screen, (200, 200, 200), btn_rect, 1)
                btn_render = font_small.render(btn_text, True, (255, 255, 255))
                btn_render_rect = btn_render.get_rect(center=btn_rect.center)
                screen.blit(btn_render, btn_render_rect)
                self.buttons_rect[f"equip_{idx}"] = btn_rect
        
        if self.message and self.message_timer > 0:
            msg_font = pg.font.SysFont(None, 16)
            msg_surface = msg_font.render(self.message, True, (255, 255, 150))
            msg_rect = msg_surface.get_rect(center=(panel_rect.centerx, panel_rect.bottom - 15))
            screen.blit(msg_surface, msg_rect)
        
        # ========== Description panel ==========
        if desc_panel_rect:
            desc_x = desc_panel_rect.x
            desc_y = desc_panel_rect.y
            desc_w = desc_panel_rect.width
            desc_h = desc_panel_rect.height
            
            pg.draw.rect(screen, (50, 50, 65), (desc_x, desc_y, desc_w, desc_h))
            pg.draw.rect(screen, (130, 130, 150), (desc_x, desc_y, desc_w, desc_h), 2)
            
            top_bar = pg.Rect(desc_x, desc_y, desc_w, 5)
            pg.draw.rect(screen, (255, 220, 100), top_bar)
            
            y = desc_y + 12
            title_desc = font_medium.render("PET DESCRIPTION", True, (255, 220, 100))
            title_rect = title_desc.get_rect(center=(desc_x + desc_w // 2, y))
            screen.blit(title_desc, title_rect)
            y += 30
            
            if self.selected_pet and self.hovered_index != -1:
                name_text = font_medium.render(self.selected_pet.name, True, (255, 255, 200))
                screen.blit(name_text, (desc_x + 12, y))
                y += 25
                
                dmg_text = font_small.render(f"Attack Damage: {self.selected_pet.attack_damage}", True, (200, 200, 220))
                screen.blit(dmg_text, (desc_x + 12, y))
                y += 20
                
                rarity_color = self.selected_pet.get_rarity_color()
                rarity_text = font_small.render(f"Rarity: {self.selected_pet.rarity.capitalize()}", True, rarity_color)
                screen.blit(rarity_text, (desc_x + 12, y))
                y += 20
                
                desc_lines = self._wrap_text(self._get_pet_description(self.selected_pet.name), desc_w - 24)
                for line in desc_lines:
                    desc_text = font_small.render(line, True, (180, 180, 200))
                    screen.blit(desc_text, (desc_x + 12, y))
                    y += 18
            else:
                hint_text = font_small.render("Hover over a pet to see details", True, (150, 150, 170))
                hint_rect = hint_text.get_rect(center=(desc_x + desc_w // 2, y + 20))
                screen.blit(hint_text, hint_rect)