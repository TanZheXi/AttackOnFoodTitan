import pygame as pg

pg.init()
pg.font.init()

class InventorySystem:
    def __init__(self, x, y, width, height):
        self.rect = pg.Rect(x, y, width, height)
        self.font_small = pg.font.SysFont(None, 18)
        self.font_medium = pg.font.SysFont(None, 22)
        self.font_large = pg.font.SysFont(None, 28)
        self.items = []  # List of item names
        self.scroll_offset = 0
        self.item_height = 30
        
        # hover effect setting
        self.hovered_index = -1
        self.selected_item = None

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
            y_offset = self.rect.y + 55
            visible_items = self.items[self.scroll_offset:self.scroll_offset + 10]
            
            for idx, item_name in enumerate(visible_items):
                item_rect = pg.Rect(self.rect.x + 15, y_offset, self.rect.width - 30, self.item_height)
                if item_rect.collidepoint(mouse_pos):
                    self.hovered_index = self.scroll_offset + idx
                    self.selected_item = item_name
                    break
                y_offset += self.item_height

    def draw(self, screen):
        # Draw inventory UI
        pg.draw.rect(screen, (45, 45, 55), self.rect)
        pg.draw.rect(screen, (150, 150, 170), self.rect, 2)

        # Title
        title = self.font_large.render("INVENTORY", True, (255, 220, 100))
        title_rect = title.get_rect(center=(self.rect.centerx, self.rect.y + 25))
        screen.blit(title, title_rect)

        # Description panel setting
        Description_panel_x = self.rect.x + int(self.rect.width * 0.58)
        Description_panel_y = self.rect.y + 55
        Description_panel_width = self.rect.width - int(self.rect.width * 0.58) - 15
        Description_panel_height = self.rect.height - 70

        # Draw description panel
        pg.draw.rect(screen, (50, 50, 65), (Description_panel_x, Description_panel_y, Description_panel_width, Description_panel_height))
        pg.draw.rect(screen, (130, 130, 150), (Description_panel_x, Description_panel_y, Description_panel_width, Description_panel_height), 2)
        
        # Add some lines for decoration
        top_bar = pg.Rect(Description_panel_x, Description_panel_y, Description_panel_width, 5)
        pg.draw.rect(screen, (255, 220, 100), top_bar)

        if self.selected_item and self.hovered_index != -1:
            # Shows description of item when hower on it
            y_offset_info = Description_panel_y + 20
            
            # Item name
            name_bg = pg.Rect(Description_panel_x + 10, y_offset_info, Description_panel_width - 20, 30)
            pg.draw.rect(screen, (65, 65, 85), name_bg)
            name_text = self.font_medium.render(self.selected_item, True, (255, 255, 200))
            name_rect = name_text.get_rect(center=(Description_panel_x + Description_panel_width // 2, y_offset_info + 15))
            screen.blit(name_text, name_rect)
            y_offset_info += 45
            
            # Lines that seperate between Info and ~ Description ~
            pg.draw.line(screen, (100, 100, 120), 
                        (Description_panel_x + 15, y_offset_info), 
                        (Description_panel_x + Description_panel_width - 15, y_offset_info), 1)
            y_offset_info += 15
            
            # Print description that used for decoration
            quote_label = self.font_small.render("~ Description ~", True, (200, 180, 120))
            screen.blit(quote_label, (Description_panel_x + 15, y_offset_info))
            y_offset_info += 22
            
            # Description
            description = self.get_item_description(self.selected_item)
            desc_lines = self.wrap_text(description, self.font_small, Description_panel_width - 25)
            for line in desc_lines:
                desc_text = self.font_small.render(line, True, (200, 200, 220))
                screen.blit(desc_text, (Description_panel_x + 15, y_offset_info))
                y_offset_info += 20
        else:
            # Shows when not hovering above anythings
            y_offset_info = Description_panel_y + 20
            
            # Text that will be print
            title_text = self.font_medium.render("Item Info", True, (255, 220, 100))
            title_rect = title_text.get_rect(center=(Description_panel_x + Description_panel_width // 2, y_offset_info + 10))
            screen.blit(title_text, title_rect)
            y_offset_info += 45
            
            # Lines that seperate the text, so look more cleaner
            pg.draw.line(screen, (100, 100, 120), 
                        (Description_panel_x + 15, y_offset_info), 
                        (Description_panel_x + Description_panel_width - 15, y_offset_info), 1)
            y_offset_info += 20
            
            # A dot design by Deepseek
            pg.draw.circle(screen, (200, 180, 120), (Description_panel_x + 20, y_offset_info + 8), 4)
            
            # Text that will be print between two seperate line
            hint_text = self.font_small.render("Hover to view item description", True, (180, 180, 200))
            screen.blit(hint_text, (Description_panel_x + 32, y_offset_info))
            y_offset_info += 22
            
            # Decorative line
            pg.draw.line(screen, (80, 80, 100), 
                        (Description_panel_x + 15, y_offset_info + 10), 
                        (Description_panel_x + Description_panel_width - 15, y_offset_info + 10), 1)

        # Box for showing item
        list_width = int(self.rect.width * 0.55)

        # Show item owned by player
        if not self.items:
            # Empty means that smaller the text and place it middle
            empty_font = pg.font.SysFont(None, 20)
            empty_text = empty_font.render("Empty", True, (120, 120, 140))
            # Left middle spaces：self.rect.x + 15 to self.rect.x + list_width
            left_area_center_x = self.rect.x + 15 + (list_width - 20) // 2
            left_area_center_y = self.rect.y + (self.rect.height // 2) + 15
            empty_rect = empty_text.get_rect(center=(left_area_center_x, left_area_center_y))
            screen.blit(empty_text, empty_rect)
            
            # Decoration rectangle
            box_rect = pg.Rect(self.rect.x + 15, self.rect.y + 55, list_width - 20, self.rect.height - 80)
            pg.draw.rect(screen, (60, 60, 75), box_rect, 1)
            return

        # Draw item list if item exist
        y_offset = self.rect.y + 55
        visible_items = self.items[self.scroll_offset:self.scroll_offset + 10]

        for idx, item_name in enumerate(visible_items):
            actual_index = self.scroll_offset + idx
            item_rect = pg.Rect(self.rect.x + 15, y_offset, list_width - 20, self.item_height)
            
            # Change color when hover above it
            if actual_index == self.hovered_index:
                color = (80, 80, 100)
            else:
                color = (55, 55, 70) if idx % 2 == 0 else (60, 60, 80)
            
            # Draw decorative circle
            pg.draw.rect(screen, color, item_rect)
            
            # Decoraation for right side
            if actual_index == self.hovered_index:
                pg.draw.rect(screen, (200, 200, 150), item_rect, 1)
            else:
                pg.draw.rect(screen, (90, 90, 110), item_rect, 1)
            
            # Item UI box
            icon_rect = pg.Rect(item_rect.x + 5, item_rect.y + 5, 20, 20)
            pg.draw.rect(screen, (100, 100, 130), icon_rect)
            pg.draw.rect(screen, (150, 150, 170), icon_rect, 1)
            
            # Item name
            item_text = self.font_small.render(item_name, True, (230, 230, 250))
            screen.blit(item_text, (item_rect.x + 32, item_rect.y + 7))

            y_offset += self.item_height + 3

        # Scroll indicator for future use
        if len(self.items) > 10:
            scroll_bg = pg.Rect(self.rect.x + self.rect.width - 35, self.rect.y + 55, 25, 100)
            pg.draw.rect(screen, (40, 40, 50), scroll_bg)
            pg.draw.rect(screen, (100, 100, 120), scroll_bg, 1)
            
            # Scroll bar design
            scroll_ratio = self.scroll_offset / (len(self.items) - 10) if len(self.items) > 10 else 0
            scroll_bar_y = scroll_bg.y + int(scroll_ratio * (scroll_bg.height - 20))
            scroll_bar = pg.Rect(scroll_bg.x + 3, scroll_bar_y, 19, 20)
            pg.draw.rect(screen, (180, 180, 200), scroll_bar)
            pg.draw.rect(screen, (220, 220, 240), scroll_bar, 1)
    
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