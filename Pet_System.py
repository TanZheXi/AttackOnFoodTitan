import pygame as pg
from Audio_System import GLOBAL_CLICK
import os

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
            Pet("Beginner Assistant Fairy", "common", 2, (200, 200, 255), price=0),
            # Epic
            Pet("Fairy", "epic", 4, (200, 150, 255), price=5000),
            Pet("Fire Spirit", "epic", 4, (200, 150, 255), price=2000),
            # Legendary
            Pet("Dragon Whelp", "legendary", 5, (100, 200, 255), price=15000),
            # Mythic
            Pet("Phoenix", "mythic", 10, (255, 100, 50), price=30000),
        ]
        
        self.max_equip = 3
        self.message = ""
        self.message_timer = 0
        self.buttons_rect = {}
        
        self.hovered_index = -1
        self.selected_pet = None
        
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
        
        self.scroll_offset = 0
        self.max_scroll = max(0, len(self.categories) - 4)
        
        self.pet_scroll_offset = 0
        self.icon_cache = {}
        
        self.pets = []
        self.update_pets_by_category()
        
        self.panel_rect = None
        self.desc_panel_rect = None
        
        self.guide_callback = None

    def update_pets_by_category(self):
        category = self.category_map.get(self.current_category, "common")
        self.pets = [pet for pet in self.all_pets if pet.owned and pet.rarity == category]
        print(f"[PET] Updated pets: {len(self.pets)} in category {category}")

    def refresh_display(self):
        self.update_pets_by_category()

    def set_category(self, category_index):
        self.current_category = category_index
        self.pet_scroll_offset = 0
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
                
                if self.guide_callback:
                    self.guide_callback()

    def update(self):
        if self.message_timer > 0:
            self.message_timer -= 1
        else:
            self.message = ""

    def handle_event(self, event):
        if self.panel_rect is None:
            return
        
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            
            if hasattr(self, 'category_buttons') and self.category_buttons:
                for btn_info in self.category_buttons:
                    if btn_info["rect"].collidepoint(event.pos):
                        if GLOBAL_CLICK: GLOBAL_CLICK.play()
                        self.set_category(btn_info["category_id"])
                        return
            
            if hasattr(self, 'arrow_left_rect') and self.arrow_left_rect.collidepoint(event.pos):
                if GLOBAL_CLICK: GLOBAL_CLICK.play()
                self.scroll_categories("left")
                return
            if hasattr(self, 'arrow_right_rect') and self.arrow_right_rect.collidepoint(event.pos):
                if GLOBAL_CLICK: GLOBAL_CLICK.play()
                self.scroll_categories("right")
                return
            
            for key, rect in self.buttons_rect.items():
                if rect.collidepoint(event.pos):
                    if GLOBAL_CLICK: GLOBAL_CLICK.play()
                    
                    if key.startswith("equip_"):
                        idx = int(key.split("_")[1])
                        self.toggle_equip(idx)
                    return
        
        # Handle Mouse Wheel Scrolling
        elif event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 4:
                self.pet_scroll_offset = max(0, self.pet_scroll_offset - 1)
            elif event.button == 5:
                max_scroll = max(0, len(self.pets) - 6)
                self.pet_scroll_offset = min(max_scroll, self.pet_scroll_offset + 1)
        
        elif event.type == pg.MOUSEMOTION:
            self.hovered_index = -1
            self.selected_pet = None
            mouse_pos = event.pos
            
            if not self.pets or self.panel_rect is None:
                return
            
            item_width = 390
            item_height = 55
            start_x = self.panel_rect.x + 18
            start_y = self.panel_rect.y + 95
            spacing_y = 6
            
            visible_items = self.pets[self.pet_scroll_offset:self.pet_scroll_offset + 6]
            
            for idx, pet in enumerate(visible_items):
                actual_index = self.pet_scroll_offset + idx
                y = start_y + idx * (item_height + spacing_y)
                item_rect = pg.Rect(start_x, y, item_width, item_height)
                if item_rect.collidepoint(mouse_pos):
                    self.hovered_index = actual_index
                    self.selected_pet = pet
                    break

    def reset_on_prestige(self):
       # Reset all pets on prestige
       for pet in self.all_pets:
           pet.equipped = False

       # Keep ownership (so player doesn't lose pets)
       self.message = "All pets unequipped due to prestige!"
       self.message_timer = 120
       print(f"[PET] All pets unequipped on prestige.")

    def restore_save_data(self, data):
        if not data:
            print("[PET] No save data, starting fresh.")
            return
        
        if not isinstance(data, list):
            print("[PET] Invalid save data format, resetting.")
            return
        
        for pet in self.all_pets:
            pet.owned = False
            pet.equipped = False
        
        for saved in data:
            for pet in self.all_pets:
                if pet.name == saved.get("name"):
                    pet.owned = saved.get("owned", False)
                    pet.equipped = saved.get("equipped", False)
                    if pet.equipped:
                        print(f"[PET] Restored equipped pet: {pet.name}")
                    break
        
        equipped_pets = self.get_equipped_pets()
        if len(equipped_pets) > self.max_equip:
            print(f"[PET] Too many equipped pets ({len(equipped_pets)})! Resetting equipped status.")
            for pet in self.all_pets:
                pet.equipped = False
        
        self.update_pets_by_category()
        owned_count = len([p for p in self.all_pets if p.owned])
        equipped_count = len(self.get_equipped_pets())
        print(f"[PET] Restored {owned_count} owned pets, {equipped_count} equipped pets from save data")

    def get_save_data(self):
        return [{"name": p.name, "owned": p.owned, "equipped": p.equipped} for p in self.all_pets]

    def _get_pet_description(self, pet_name):
        descriptions = {
            "Baby Slime": "A jiggly baby slime that loves to bounce.",
            "Beginner Assistant Fairy": "A helpful fairy that boosts your cooking skills.",
            "Fire Spirit": "A blazing spirit that burns enemies.",
            "Fairy": "A magical fairy that heals wounds.",
            "Dragon Whelp": "A baby dragon learning to fly.",
            "Phoenix": "A majestic bird that rises from ashes.",
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

    def _get_item_icon(self, item_name):
        if item_name in self.icon_cache:
            return self.icon_cache[item_name]
            
        icon_path = os.path.join(os.path.dirname(__file__), "Icon", f"{item_name}.png")
        if os.path.exists(icon_path):
            try:
                img = pg.image.load(icon_path).convert_alpha()
                bounding_rect = img.get_bounding_rect()
                if bounding_rect.width > 0 and bounding_rect.height > 0:
                    img = img.subsurface(bounding_rect)
                    
                target_size = 40
                scale = min(target_size / img.get_width(), target_size / img.get_height())
                new_w, new_h = int(img.get_width() * scale), int(img.get_height() * scale)
                img = pg.transform.scale(img, (new_w, new_h))
                
                self.icon_cache[item_name] = img
                return img
            except Exception as e:
                pass
                
        self.icon_cache[item_name] = None
        return None
    
    def draw(self, screen, panel_rect, desc_panel_rect):
        if not panel_rect:
            return
        
        self.panel_rect = panel_rect
        self.desc_panel_rect = desc_panel_rect
        
        font_small = pg.font.SysFont(None, 14)
        font_medium = pg.font.SysFont(None, 18)
        
        # Black background with border
        bg_rect = pg.Rect(panel_rect.x + 10, panel_rect.y + 50, panel_rect.width - 20, panel_rect.height - 60)
        pg.draw.rect(screen, (45, 45, 55), bg_rect)
        pg.draw.rect(screen, (150, 150, 170), bg_rect, 2)
        
        # Category buttons
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
        
        # Pet list (List View)
        item_width = 390
        item_height = 55
        spacing_y = 6
        
        start_x = panel_rect.x + 18
        start_y = panel_rect.y + 95
        
        self.buttons_rect.clear()
        
        if not self.pets:
            empty_text = font_medium.render("Empty", True, (150, 150, 150))
            empty_rect = empty_text.get_rect(center=(panel_rect.centerx, panel_rect.centery + 20))
            screen.blit(empty_text, empty_rect)
        else:
            visible_items = self.pets[self.pet_scroll_offset:self.pet_scroll_offset + 6]
            
            for idx, pet in enumerate(visible_items):
                actual_index = self.pet_scroll_offset + idx
                y = start_y + idx * (item_height + spacing_y)
                item_rect = pg.Rect(start_x, y, item_width, item_height)
                
                if pet.equipped:
                    color = (70, 100, 70)
                else:
                    color = (55, 55, 70) if idx % 2 == 0 else (60, 60, 80)
                
                pg.draw.rect(screen, color, item_rect)
                
                if self.hovered_index == actual_index:
                    pg.draw.rect(screen, (255, 220, 100), item_rect, 2)
                else:
                    pg.draw.rect(screen, (90, 90, 110), item_rect, 1)
                
                # --- 1. ICON (Far Left) ---
                icon = self._get_item_icon(pet.name)
                if icon:
                    icon_rect = icon.get_rect(center=(item_rect.x + 30, item_rect.centery))
                    screen.blit(icon, icon_rect)
                else:
                    # Fallback circle if icon is missing
                    pg.draw.circle(screen, pet.color, (item_rect.x + 30, item_rect.centery), 15)
                
                # --- 2. PET NAME & RARITY (Middle Left, Upper) ---
                name_display = pet.name[:20] + ".." if len(pet.name) > 20 else pet.name
                name_text = font_medium.render(name_display, True, (255, 255, 200))
                screen.blit(name_text, (item_rect.x + 65, item_rect.centery - 14))
                
                # --- 3. STATUS & DMG (Middle Left, Lower) ---
                if pet.equipped:
                    status_text = font_small.render(f"EQUIPPED  |  DMG: {pet.attack_damage}", True, (100, 255, 100))
                else:
                    status_text = font_small.render(f"DMG: {pet.attack_damage}", True, (200, 200, 220))
                screen.blit(status_text, (item_rect.x + 65, item_rect.centery + 4))
                
                # --- 4. BUTTON (Far Right) ---
                btn_width = 70
                btn_height = 26
                btn_rect = pg.Rect(item_rect.right - btn_width - 15, item_rect.centery - btn_height // 2, btn_width, btn_height)
                mouse_pos = pg.mouse.get_pos()
                
                if pet.equipped:
                    btn_color = (130, 70, 70) if btn_rect.collidepoint(mouse_pos) else (100, 50, 50)
                    btn_text = "UNEQUIP"
                else:
                    btn_color = (70, 100, 130) if btn_rect.collidepoint(mouse_pos) else (50, 70, 100)
                    btn_text = "EQUIP"
                
                pg.draw.rect(screen, btn_color, btn_rect)
                pg.draw.rect(screen, (200, 200, 200), btn_rect, 1)
                btn_render = font_small.render(btn_text, True, (255, 255, 255))
                btn_render_rect = btn_render.get_rect(center=btn_rect.center)
                screen.blit(btn_render, btn_render_rect)
                self.buttons_rect[f"equip_{actual_index}"] = btn_rect
                
            # Scrollbar
            if len(self.pets) > 6:
                scroll_bg = pg.Rect(panel_rect.x + panel_rect.width - 15, start_y, 8, 6 * (item_height + spacing_y) - spacing_y)
                pg.draw.rect(screen, (40, 40, 50), scroll_bg)
                pg.draw.rect(screen, (100, 100, 120), scroll_bg, 1)
                
                max_scroll = max(0, len(self.pets) - 6)
                if max_scroll > 0:
                    scroll_ratio = self.pet_scroll_offset / max_scroll
                    scroll_bar_height = max(20, scroll_bg.height * 0.3)
                    scroll_bar_y = scroll_bg.y + int(scroll_ratio * (scroll_bg.height - scroll_bar_height))
                    scroll_bar = pg.Rect(scroll_bg.x, scroll_bar_y, scroll_bg.width, scroll_bar_height)
                    pg.draw.rect(screen, (180, 180, 200), scroll_bar)
                    pg.draw.rect(screen, (220, 220, 240), scroll_bar, 1)
        
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