import pygame as pg

pg.init()
pg.font.init()

class InventorySystem:
    def __init__(self, x, y, width, height):
        self.rect = pg.Rect(x, y, width, height)
        self.font_small = pg.font.SysFont(None, 16)
        self.font_medium = pg.font.SysFont(None, 20)
        self.font_large = pg.font.SysFont(None, 24)
        self.items = []  # List of item names
        self.scroll_offset = 0
        self.item_height = 28
        
        # Description panel rectangle (set by Button_System)
        self.desc_panel_rect = None
        
        # hover effect setting
        self.hovered_index = -1
        self.selected_item = None

    def set_desc_panel_rect(self, rect):
        """Set the position and size of the description panel"""
        self.desc_panel_rect = rect

    def add_item(self, item_name):
        """Adding items into inventory"""
        self.items.append(item_name)
        print(f"[INVENTORY] Added: {item_name}. Total items: {len(self.items)}")
    
    def restore_inventory(self, inventory_items):
        """Restore inventory from saved data"""
        self.items = inventory_items.copy() if inventory_items else []
        print(f"[INVENTORY] Restored {len(self.items)} items: {self.items}")

    def get_inventory_state(self):
        """Get current inventory for saving"""
        return self.items.copy()

    def handle_event(self, event):
        """Scrolling and hovering event setting"""
        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 4:  # Scroll up
                self.scroll_offset = max(0, self.scroll_offset - 1)
            elif event.button == 5:  # Scroll down
                max_scroll = max(0, len(self.items) - 10)
                self.scroll_offset = min(max_scroll, self.scroll_offset + 1)
        
        elif event.type == pg.MOUSEMOTION:
            self.hovered_index = -1
            self.selected_item = None
            mouse_pos = event.pos
            
            # Check if player hover above an item
            y_offset = self.rect.y + 40
            visible_items = self.items[self.scroll_offset:self.scroll_offset + 10]
            
            for idx, item_name in enumerate(visible_items):
                item_rect = pg.Rect(self.rect.x + 10, y_offset, self.rect.width - 20, self.item_height)
                if item_rect.collidepoint(mouse_pos):
                    self.hovered_index = self.scroll_offset + idx
                    self.selected_item = item_name
                    break
                y_offset += self.item_height + 3

    def draw(self, screen):
        # Draw inventory UI
        pg.draw.rect(screen, (45, 45, 55), self.rect)
        pg.draw.rect(screen, (150, 150, 170), self.rect, 2)

        # Title
        title = self.font_large.render("INVENTORY", True, (255, 220, 100))
        title_rect = title.get_rect(center=(self.rect.centerx, self.rect.y + 20))
        screen.blit(title, title_rect)

        # Box for showing item
        list_width = self.rect.width - 20

        # Show item owned by player
        if not self.items:
            # Empty means that smaller the text and place it middle
            empty_font = pg.font.SysFont(None, 18)
            empty_text = empty_font.render("Empty", True, (120, 120, 140))
            left_area_center_x = self.rect.x + list_width // 2
            left_area_center_y = self.rect.y + self.rect.height // 2
            empty_rect = empty_text.get_rect(center=(left_area_center_x, left_area_center_y))
            screen.blit(empty_text, empty_rect)
            
            # Decoration rectangle
            box_rect = pg.Rect(self.rect.x + 10, self.rect.y + 45, list_width - 20, self.rect.height - 65)
            pg.draw.rect(screen, (60, 60, 75), box_rect, 1)
        else:
            # Draw item list if item exist
            y_offset = self.rect.y + 45
            visible_items = self.items[self.scroll_offset:self.scroll_offset + 10]

            for idx, item_name in enumerate(visible_items):
                actual_index = self.scroll_offset + idx
                item_rect = pg.Rect(self.rect.x + 10, y_offset, list_width - 20, self.item_height)
                
                # Change color when hover above it
                if actual_index == self.hovered_index:
                    color = (80, 80, 100)
                    pg.draw.rect(screen, (200, 200, 150), item_rect, 1)
                else:
                    color = (55, 55, 70) if idx % 2 == 0 else (60, 60, 80)
                    pg.draw.rect(screen, (90, 90, 110), item_rect, 1)
                
                pg.draw.rect(screen, color, item_rect)
                
                # Item UI box
                icon_rect = pg.Rect(item_rect.x + 5, item_rect.y + 4, 20, 20)
                pg.draw.rect(screen, (100, 100, 130), icon_rect)
                pg.draw.rect(screen, (150, 150, 170), icon_rect, 1)
                
                # Item name
                item_text = self.font_small.render(item_name, True, (230, 230, 250))
                screen.blit(item_text, (item_rect.x + 32, item_rect.y + 6))

                y_offset += self.item_height + 3

            # Scroll indicator
            if len(self.items) > 10:
                scroll_bg = pg.Rect(self.rect.x + self.rect.width - 25, self.rect.y + 45, 15, 80)
                pg.draw.rect(screen, (40, 40, 50), scroll_bg)
                pg.draw.rect(screen, (100, 100, 120), scroll_bg, 1)
                
                scroll_ratio = self.scroll_offset / (len(self.items) - 10) if len(self.items) > 10 else 0
                scroll_bar_y = scroll_bg.y + int(scroll_ratio * (scroll_bg.height - 15))
                scroll_bar = pg.Rect(scroll_bg.x + 2, scroll_bar_y, 11, 15)
                pg.draw.rect(screen, (180, 180, 200), scroll_bar)
                pg.draw.rect(screen, (220, 220, 240), scroll_bar, 1)

        # ========== Draw Description Panel ==========
        if self.desc_panel_rect and self.selected_item and self.hovered_index != -1:
            desc_x = self.desc_panel_rect.x
            desc_y = self.desc_panel_rect.y
            desc_w = self.desc_panel_rect.width
            desc_h = self.desc_panel_rect.height
            
            pg.draw.rect(screen, (50, 50, 65), (desc_x, desc_y, desc_w, desc_h))
            pg.draw.rect(screen, (130, 130, 150), (desc_x, desc_y, desc_w, desc_h), 2)
            
            top_bar = pg.Rect(desc_x, desc_y, desc_w, 5)
            pg.draw.rect(screen, (255, 220, 100), top_bar)
            
            y_offset = desc_y + 15
            
            name_text = self.font_medium.render(self.selected_item, True, (255, 255, 200))
            name_rect = name_text.get_rect(center=(desc_x + desc_w // 2, y_offset))
            screen.blit(name_text, name_rect)
            y_offset += 35
            
            pg.draw.line(screen, (100, 100, 120), (desc_x + 10, y_offset), (desc_x + desc_w - 10, y_offset), 1)
            y_offset += 15
            
            desc_label = self.font_small.render("~ Description ~", True, (200, 180, 120))
            screen.blit(desc_label, (desc_x + 12, y_offset))
            y_offset += 20
            
            description = self.get_item_description(self.selected_item)
            desc_lines = self.wrap_text(description, self.font_small, desc_w - 25)
            for line in desc_lines:
                desc_text = self.font_small.render(line, True, (200, 200, 220))
                screen.blit(desc_text, (desc_x + 12, y_offset))
                y_offset += 18
        
        elif self.desc_panel_rect:
            desc_x = self.desc_panel_rect.x
            desc_y = self.desc_panel_rect.y
            desc_w = self.desc_panel_rect.width
            desc_h = self.desc_panel_rect.height
            
            pg.draw.rect(screen, (50, 50, 65), (desc_x, desc_y, desc_w, desc_h))
            pg.draw.rect(screen, (130, 130, 150), (desc_x, desc_y, desc_w, desc_h), 2)
            
            top_bar = pg.Rect(desc_x, desc_y, desc_w, 5)
            pg.draw.rect(screen, (255, 220, 100), top_bar)
            
            info_text = self.font_medium.render("Item Info", True, (255, 220, 100))
            info_rect = info_text.get_rect(center=(desc_x + desc_w // 2, desc_y + 40))
            screen.blit(info_text, info_rect)
            
            hint_text = self.font_small.render("Hover over an item", True, (180, 180, 200))
            hint_rect = hint_text.get_rect(center=(desc_x + desc_w // 2, desc_y + 80))
            screen.blit(hint_text, hint_rect)
            
            hint_text2 = self.font_small.render("to see description", True, (180, 180, 200))
            hint_rect2 = hint_text2.get_rect(center=(desc_x + desc_w // 2, desc_y + 105))
            screen.blit(hint_text2, hint_rect2)
    
    def get_item_description(self, item_name):
        """Show description according to each item"""
        descriptions = {
            "Apple": "A crisp red apple. Keeps the doctor away!",
            "Banana": "A yellow banana. Great source of potassium.",
            "Carrot": "A crunchy carrot. Good for your eyesight.",
            "Wok": "A versatile cooking tool. Also works as a shield.",
            "Fork": "A three-pronged weapon. For dining and fighting.",
            "Spon": "A hybrid spoon-fork. Very confusing to enemies.",
            "Ur dad belt": "Your father's favorite weapon. +50 respect.",
            "Ur sister's pen": "Borrowed without permission. Use carefully.",
            "Ur mom credit card": "Unlimited spending power. Use wisely!",
            "Golden Spatula": "A legendary cooking tool. Flip anything!",
            "Mythic Pan": "A pan of legendary power. Sizzles with energy.",
            "Rusty Spatula": "An old spatula. Better than nothing.",
            "Chef's Wok": "A master chef's wok. Perfect for stir-frying enemies.",
            "Master Chef Hat": "Increases cooking skill. Look professional!",
            "Titanium Apron": "Heavy-duty protection. Stain resistant.",
            "Roasted Garlic Aroma": "Smells amazing. Distracts enemies."
        }
        
        if item_name in descriptions:
            return descriptions[item_name]
        else:
            return f"A mysterious item called '{item_name}'."
    
    def wrap_text(self, text, font, max_width):
        """Text wrapping function"""
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