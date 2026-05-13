import pygame as pg

pg.init()
pg.font.init()

class CategoryButton:
    def __init__(self, rect, text, category_id):
        self.rect = rect
        self.text = text
        self.category_id = category_id
        self.is_selected = False
        self.font = pg.font.SysFont(None, 14)

    def draw(self, screen):
        color = (100, 100, 150) if self.is_selected else (60, 60, 80)
        pg.draw.rect(screen, color, self.rect)
        pg.draw.rect(screen, (200, 200, 200), self.rect, 1)
        text_surf = self.font.render(self.text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)


class InventorySystem:
    def __init__(self, x, y, width, height):
        self.rect = pg.Rect(x, y, width, height)
        self.font_small = pg.font.SysFont(None, 14)
        self.font_medium = pg.font.SysFont(None, 18)
        self.font_large = pg.font.SysFont(None, 22)
        
        # All items in inventory, stored as tuples of (name, category)
        self.all_items = []
        self.current_category = 0
        self.category_map = {
            0: "weapon",
            1: "equipment",
            2: "scraps"
        }
        
        self.scroll_offset = 0
        self.item_height = 28
        
        self.desc_panel_rect = None
        self.hovered_index = -1
        self.selected_item = None
        
        # Category buttons
        self.category_buttons = []
        self._init_category_buttons()

    def _init_category_buttons(self):
        btn_width = 80
        btn_height = 25
        spacing = 8
        total_width = btn_width * 3 + spacing * 2
        start_x = self.rect.centerx - total_width // 2
        y = self.rect.y + 8
        
        categories = ["Weapon", "Equipment", "Scraps"]
        for i, cat in enumerate(categories):
            btn_rect = pg.Rect(start_x + i * (btn_width + spacing), y, btn_width, btn_height)
            btn = CategoryButton(btn_rect, cat, i)
            btn.is_selected = (i == self.current_category)
            self.category_buttons.append(btn)

    def set_category(self, category_index):
        self.current_category = category_index
        self.scroll_offset = 0
        for btn in self.category_buttons:
            btn.is_selected = (btn.category_id == self.current_category)

    def add_item(self, item_name):
        category = self._get_item_category(item_name)
        self.all_items.append((item_name, category))
        print(f"[INVENTORY] Added: {item_name}")

    def _get_item_category(self, item_name):
        weapon_items = ["Rusty Spatula", "Golden Spatula", "Chef's Wok", "Mythic Pan", "OP WEAPON"]
        equipment_items = ["Master Chef Hat", "Titanium Apron", "Roasted Garlic Aroma", "Speed Boots", "Magic Ring"]
        scrap_items = ["Scrap Pack S", "Scrap Pack M", "Scrap Pack L", "Scrap Pack XL", "Scrap Pack XXL"]
        pet_items = ["Baby Slime", "Fire Spirit", "Fairy", "Dragon Whelp", "Phoenix"]
        
        if item_name in weapon_items:
            return "weapon"
        elif item_name in equipment_items:
            return "equipment"
        elif item_name in scrap_items:
            return "scraps"
        elif item_name in pet_items:
            return "pet"
        else:
            return "equipment"

    def get_filtered_items(self):
        category = self.category_map.get(self.current_category, "weapon")
        return [(name, cat) for name, cat in self.all_items if cat == category]

    def restore_inventory(self, inventory_items):
        self.all_items = []
        for item_name in inventory_items:
            category = self._get_item_category(item_name)
            self.all_items.append((item_name, category))

    def get_inventory_state(self):
        return [name for name, cat in self.all_items]

    def reset_inventory(self):
        self.all_items = []
        print(f"[INVENTORY] Inventory cleared on prestige.")

    def set_desc_panel_rect(self, rect):
        self.desc_panel_rect = rect

    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            # Process category button clicks
            for btn in self.category_buttons:
                if btn.rect.collidepoint(event.pos):
                    self.set_category(btn.category_id)
                    return
            
            # Scroll inventory with mouse wheel
            if event.button == 4:
                self.scroll_offset = max(0, self.scroll_offset - 1)
            elif event.button == 5:
                items = self.get_filtered_items()
                max_scroll = max(0, len(items) - 10)
                self.scroll_offset = min(max_scroll, self.scroll_offset + 1)
        
        elif event.type == pg.MOUSEMOTION:
            self.hovered_index = -1
            self.selected_item = None
            mouse_pos = event.pos
            
            y_offset = self.rect.y + 45
            items = self.get_filtered_items()
            visible_items = items[self.scroll_offset:self.scroll_offset + 10]
            
            for idx, (item_name, cat) in enumerate(visible_items):
                item_rect = pg.Rect(self.rect.x + 10, y_offset, self.rect.width - 20, self.item_height)
                if item_rect.collidepoint(mouse_pos):
                    self.hovered_index = self.scroll_offset + idx
                    self.selected_item = item_name
                    break
                y_offset += self.item_height + 3

    def draw(self, screen):
        pg.draw.rect(screen, (45, 45, 55), self.rect)
        pg.draw.rect(screen, (150, 150, 170), self.rect, 2)

        for btn in self.category_buttons:
            btn.draw(screen)

        items = self.get_filtered_items()
        list_width = self.rect.width - 20

        if not items:
            empty_font = pg.font.SysFont(None, 18)
            empty_text = empty_font.render("Empty", True, (120, 120, 140))
            left_area_center_x = self.rect.x + list_width // 2
            left_area_center_y = self.rect.y + self.rect.height // 2
            empty_rect = empty_text.get_rect(center=(left_area_center_x, left_area_center_y))
            screen.blit(empty_text, empty_rect)
        else:
            y_offset = self.rect.y + 45
            visible_items = items[self.scroll_offset:self.scroll_offset + 10]

            for idx, (item_name, cat) in enumerate(visible_items):
                actual_index = self.scroll_offset + idx
                item_rect = pg.Rect(self.rect.x + 10, y_offset, list_width - 20, self.item_height)
                
                if actual_index == self.hovered_index:
                    color = (80, 80, 100)
                    pg.draw.rect(screen, (200, 200, 150), item_rect, 1)
                else:
                    color = (55, 55, 70) if idx % 2 == 0 else (60, 60, 80)
                    pg.draw.rect(screen, (90, 90, 110), item_rect, 1)
                
                pg.draw.rect(screen, color, item_rect)
                
                icon_rect = pg.Rect(item_rect.x + 5, item_rect.y + 4, 20, 20)
                pg.draw.rect(screen, (100, 100, 130), icon_rect)
                pg.draw.rect(screen, (150, 150, 170), icon_rect, 1)
                
                item_text = self.font_small.render(item_name, True, (230, 230, 250))
                screen.blit(item_text, (item_rect.x + 32, item_rect.y + 6))

                y_offset += self.item_height + 3

            # Scrollbar
            if len(items) > 10:
                scroll_bg = pg.Rect(self.rect.x + self.rect.width - 25, self.rect.y + 45, 15, 80)
                pg.draw.rect(screen, (40, 40, 50), scroll_bg)
                pg.draw.rect(screen, (100, 100, 120), scroll_bg, 1)
                
                scroll_ratio = self.scroll_offset / (len(items) - 10) if len(items) > 10 else 0
                scroll_bar_y = scroll_bg.y + int(scroll_ratio * (scroll_bg.height - 15))
                scroll_bar = pg.Rect(scroll_bg.x + 2, scroll_bar_y, 11, 15)
                pg.draw.rect(screen, (180, 180, 200), scroll_bar)
                pg.draw.rect(screen, (220, 220, 240), scroll_bar, 1)

        # ========== Description box ==========
        if self.desc_panel_rect:
            desc_x = self.desc_panel_rect.x
            desc_y = self.desc_panel_rect.y
            desc_w = self.desc_panel_rect.width
            desc_h = self.desc_panel_rect.height
            
            pg.draw.rect(screen, (50, 50, 65), (desc_x, desc_y, desc_w, desc_h))
            pg.draw.rect(screen, (130, 130, 150), (desc_x, desc_y, desc_w, desc_h), 2)
            
            top_bar = pg.Rect(desc_x, desc_y, desc_w, 5)
            pg.draw.rect(screen, (255, 220, 100), top_bar)
            
            y = desc_y + 12
            title_desc = self.font_medium.render("ITEM DESCRIPTION", True, (255, 220, 100))
            title_rect = title_desc.get_rect(center=(desc_x + desc_w // 2, y))
            screen.blit(title_desc, title_rect)
            y += 30
            
            if self.selected_item and self.hovered_index != -1:
                name_text = self.font_medium.render(self.selected_item, True, (255, 255, 200))
                screen.blit(name_text, (desc_x + 12, y))
                y += 25
                
                # Get item description and wrap text
                description = self._get_item_description(self.selected_item)
                desc_lines = self._wrap_text(description, self.font_small, desc_w - 24)
                for line in desc_lines:
                    desc_text = self.font_small.render(line, True, (180, 180, 200))
                    screen.blit(desc_text, (desc_x + 12, y))
                    y += 18
            else:
                hint_text1 = self.font_small.render("Hover over an item", True, (150, 150, 170))
                hint_rect1 = hint_text1.get_rect(center=(desc_x + desc_w // 2, y + 15))
                screen.blit(hint_text1, hint_rect1)
                
                hint_text2 = self.font_small.render("to see details", True, (150, 150, 170))
                hint_rect2 = hint_text2.get_rect(center=(desc_x + desc_w // 2, y + 35))
                screen.blit(hint_text2, hint_rect2)
        # ===================================================

    def _get_item_description(self, item_name):
        descriptions = {
            "Rusty Spatula": "An old spatula. Better than nothing.",
            "Golden Spatula": "A legendary cooking tool. Flip anything!",
            "Chef's Wok": "A master chef's wok. Perfect for stir-frying.",
            "Mythic Pan": "A pan of legendary power. Sizzles with energy.",
            "OP WEAPON": "Overpowered weapon! Use with care.",
            "Master Chef Hat": "Increases cooking skill. Look professional!",
            "Titanium Apron": "Heavy-duty protection. Stain resistant.",
            "Roasted Garlic Aroma": "Smells amazing! Distracts enemies.",
            "Speed Boots": "Increases movement speed. Very comfortable.",
            "Magic Ring": "Boosts all stats. Glows with power.",
            "Baby Slime": "A jiggly baby slime that loves to bounce.",
            "Fire Spirit": "A blazing spirit that burns enemies.",
            "Fairy": "A magical fairy that heals wounds.",
            "Dragon Whelp": "A baby dragon learning to fly.",
            "Phoenix": "A majestic bird that rises from ashes.",
            "Scrap Pack S": "Small pack of crafting scraps.",
            "Scrap Pack M": "Medium pack of crafting scraps.",
            "Scrap Pack L": "Large pack of crafting scraps.",
            "Scrap Pack XL": "Extra large pack of crafting scraps.",
            "Scrap Pack XXL": "Massive pack of crafting scraps."
        }
        return descriptions.get(item_name, f"A {item_name} in your collection.")

    def _wrap_text(self, text, font, max_width):
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