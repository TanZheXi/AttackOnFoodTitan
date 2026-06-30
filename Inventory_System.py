import pygame as pg
import Equipment_System
import os
from Audio_System import GLOBAL_CLICK

pg.init()
pg.font.init()

class CategoryButton:
    def __init__(self, rect, text, category_id):
        self.rect = rect
        self.text = text
        self.category_id = category_id
        self.is_selected = False
        self.font = pg.font.SysFont(None, 14)
        self.icon_image = None

    def draw(self, screen):
        color = (100, 100, 150) if self.is_selected else (60, 60, 80)
        pg.draw.rect(screen, color, self.rect)
        pg.draw.rect(screen, (200, 200, 200), self.rect, 1)
        
        if self.icon_image:
            # Draw
            icon_rect = self.icon_image.get_rect(center=self.rect.center)
            screen.blit(self.icon_image, icon_rect)
        else:
            # Use original text button if can't load its image
            text_surf = self.font.render(self.text, True, (255, 255, 255))
            text_rect = text_surf.get_rect(center=self.rect.center)
            screen.blit(text_surf, text_rect)


class InventorySystem:
    def __init__(self, x, y, width, height):
        self.rect = pg.Rect(x, y, width, height)
        # Fonts - same size as Pet system
        self.font_small = pg.font.SysFont(None, 14)
        self.font_medium = pg.font.SysFont(None, 18)
        self.font_large = pg.font.SysFont(None, 24)
        
        # All items in inventory
        self.all_items = []
        self.current_category = 0
        self.category_map = {
            0: "weapon",
            1: "equipment",
            2: "scraps"
        }
        
        # Add a cache so icons only load once!
        self.icon_cache = {}
        
        self.scroll_offset = 0
        self.item_width = 190
        self.item_height = 80
        self.equip_buttons = {}
        
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
        icon_names = ["Weapon", "Equipment", "Scraps"]
        
        for i, (cat, icon_name) in enumerate(zip(categories, icon_names)):
            btn_rect = pg.Rect(start_x + i * (btn_width + spacing), y, btn_width, btn_height)
            btn = CategoryButton(btn_rect, cat, i)
            btn.is_selected = (i == self.current_category)
            
            # Load icon
            icon_folder = os.path.join(os.path.dirname(__file__), "Icon")
            icon_path = os.path.join(icon_folder, f"{icon_name}.png")
            try:
                if os.path.exists(icon_path):
                    original = pg.image.load(icon_path).convert_alpha()
                    
                    # Remove white background
                    for _x in range(original.get_width()):
                        for _y in range(original.get_height()):
                            r, g, b, a = original.get_at((_x, _y))
                            if r > 240 and g > 240 and b > 240:
                                original.set_at((_x, _y), (0, 0, 0, 0))
                    
                    # --- MAGIC CROP: Snips away the empty transparent space! ---
                    bounding_rect = original.get_bounding_rect()
                    if bounding_rect.width > 0 and bounding_rect.height > 0:
                        original = original.subsurface(bounding_rect)
                    
                    target_w = btn_width - 10
                    target_h = btn_height - 6
                    original_w = original.get_width()
                    original_h = original.get_height()
                    
                    # Scale properly so it fits without getting squashed
                    scale = min(target_w / original_w, target_h / original_h)
                    new_w = int(original_w * scale)
                    new_h = int(original_h * scale)
                    
                    btn.icon_image = pg.transform.scale(original, (new_w, new_h))
            except Exception as e:
                pass
            
            self.category_buttons.append(btn)

    def set_category(self, category_index):
        self.current_category = category_index
        self.scroll_offset = 0
        for btn in self.category_buttons:
            btn.is_selected = (btn.category_id == self.current_category)

    def add_item(self, item_name):
        category = self._get_item_category(item_name)
        existing = [name for name, cat in self.all_items if name == item_name]
        if not existing:
            self.all_items.append((item_name, category))
            print(f"[INVENTORY] Added: {item_name}")
        else:
            print(f"[INVENTORY] {item_name} already in inventory")

    def _get_item_category(self, item_name):
        weapon_items = ["Rusty Spatula", "Golden Spatula", "Chef's Wok", "Mythic Pan", "OP WEAPON", "Beginner Wok"]
        equipment_items = ["Master Chef Hat", "Titanium Apron", "Roasted Garlic Aroma", "Speed Boots", "Magic Ring", "Beginner Apron"]
        scrap_items = ["Scrap Pack S", "Scrap Pack M", "Scrap Pack L", "Scrap Pack XL", "Scrap Pack XXL"]
        pet_items = ["Baby Slime", "Beginner Assistant Fairy", "Fire Spirit", "Fairy", "Dragon Whelp", "Phoenix"]
        
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
        
    def _get_item_icon(self, item_name):
        if item_name in self.icon_cache:
            return self.icon_cache[item_name]
            
        icon_path = os.path.join(os.path.dirname(__file__), "Icon", f"{item_name}.png")
        if os.path.exists(icon_path):
            try:
                img = pg.image.load(icon_path).convert_alpha()
                
                # Remove white background
                for _x in range(img.get_width()):
                    for _y in range(img.get_height()):
                        r, g, b, a = img.get_at((_x, _y))
                        if r > 240 and g > 240 and b > 240:
                            img.set_at((_x, _y), (0, 0, 0, 0))
                
                bounding_rect = img.get_bounding_rect()
                if bounding_rect.width > 0 and bounding_rect.height > 0:
                    img = img.subsurface(bounding_rect)
                    
                target_size = 50 # Size of the icon on the card
                scale = min(target_size / img.get_width(), target_size / img.get_height())
                new_w, new_h = int(img.get_width() * scale), int(img.get_height() * scale)
                img = pg.transform.scale(img, (new_w, new_h))
                
                self.icon_cache[item_name] = img
                return img
            except Exception as e:
                pass
                
        self.icon_cache[item_name] = None
        return None

    def get_filtered_items(self):
        category = self.category_map.get(self.current_category, "weapon")
        
        # --- THE MASTER FIX ---
        # Ignore the corrupted auto-save list. 
        # Read directly from the Equipment JSON database every single frame!
        actual_items = []
        for item_name, data in Equipment_System.equipment_database.items():
            # If the database says you own it, force it onto the screen.
            if item_name != "Player_Data" and data.get("owned", False) == True:
                cat = self._get_item_category(item_name)
                if cat == category:
                    actual_items.append((item_name, cat))
                    
        return actual_items

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
        
        # Handle equip/unequip button clicks
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            for key, rect in self.equip_buttons.items():
                if rect.collidepoint(event.pos):
                    # Extract item name correctly
                    if key.startswith("unequip_"):
                        item_name = key[8:]  # Remove "unequip_" prefix
                    elif key.startswith("equip_"):
                        item_name = key[6:]  # Remove "equip_" prefix
                    else:
                        continue
                    
                    if GLOBAL_CLICK:
                        GLOBAL_CLICK.play()
                    if key.startswith("unequip_"):
                        if item_name in Equipment_System.equipment_database:
                            slot = Equipment_System.equipment_database[item_name]["slot"]
                            Equipment_System.unequip_equipment(slot)
                    elif key.startswith("equip_"):
                        Equipment_System.equip_equipment(item_name)
                    return
        
        # 1. Left Mouse Button (Clicking the Category Tabs)
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            for btn in self.category_buttons:
                if btn.rect.collidepoint(event.pos):

                    if GLOBAL_CLICK: GLOBAL_CLICK.play() # <--- PLAY SOUND!

                    self.set_category(btn.category_id)
                    return
        
        # 2. Scroll inventory with mouse wheel (Buttons 4 and 5)
        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 4:
                self.scroll_offset = max(0, self.scroll_offset - 1)
            elif event.button == 5:
                items = self.get_filtered_items()
                max_scroll = max(0, len(items) - 4)
                self.scroll_offset = min(max_scroll, self.scroll_offset + 1)
        
        # Handle mouse hover for item selection
        elif event.type == pg.MOUSEMOTION:
            self.hovered_index = -1
            self.selected_item = None
            mouse_pos = event.pos
            
            # Card positions
            cards_per_row = 2
            card_width = self.item_width
            card_height = self.item_height
            card_spacing_x = 12
            card_spacing_y = 10
            
            # SHIFTED LEFT: Changed from 18 to 8
            start_x = self.rect.x + 8 
            start_y = self.rect.y + 65
            
            items = self.get_filtered_items()
            visible_items = items[self.scroll_offset:self.scroll_offset + 6]
            
            for idx, (item_name, cat) in enumerate(visible_items):
                row = idx // cards_per_row
                col = idx % cards_per_row
                x = start_x + col * (card_width + card_spacing_x)
                y = start_y + row * (card_height + card_spacing_y)
                item_rect = pg.Rect(x, y, card_width, card_height)
                if item_rect.collidepoint(mouse_pos):
                    self.hovered_index = self.scroll_offset + idx
                    self.selected_item = item_name
                    break

    def draw(self, screen):

        for item_name, item_data in Equipment_System.equipment_database.items():
            if item_name != "Player_Data" and item_data.get("owned", False):
                # If we own it, but it's missing from the UI list, add it back!
                if not any(name == item_name for name, cat in self.all_items):
                    self.add_item(item_name)
        
        # Panel background
        pg.draw.rect(screen, (45, 45, 55), self.rect)
        pg.draw.rect(screen, (150, 150, 170), self.rect, 2)

        # Draw category buttons
        for btn in self.category_buttons:
            btn.draw(screen)

        items = self.get_filtered_items()
        self.equip_buttons.clear()

        # Card dimensions
        card_width = self.item_width
        card_height = self.item_height
        cards_per_row = 2
        card_spacing_x = 12
        card_spacing_y = 10
        
        # SHIFTED LEFT: Changed from 18 to 8
        start_x = self.rect.x + 8 
        start_y = self.rect.y + 65

        if not items:
            empty_font = pg.font.SysFont(None, 18)
            empty_text = empty_font.render("Empty", True, (120, 120, 140))
            left_area_center_x = self.rect.x + self.rect.width // 2
            left_area_center_y = self.rect.y + self.rect.height // 2
            empty_rect = empty_text.get_rect(center=(left_area_center_x, left_area_center_y))
            screen.blit(empty_text, empty_rect)
        else:
            visible_items = items[self.scroll_offset:self.scroll_offset + 6]

            for idx, (item_name, cat) in enumerate(visible_items):
                actual_index = self.scroll_offset + idx
                row = idx // cards_per_row
                col = idx % cards_per_row
                x = start_x + col * (card_width + card_spacing_x)
                y = start_y + row * (card_height + card_spacing_y)
                item_rect = pg.Rect(x, y, card_width, card_height)
                
                # Check if item is equippable and equipped
                is_equippable = item_name in Equipment_System.equipment_database
                is_equipped = False
                if is_equippable:
                    for slot, equipped_item in Equipment_System.equipped_slots.items():
                        if equipped_item == item_name:
                            is_equipped = True
                            break
                
                # Card background color
                if is_equipped:
                    color = (70, 100, 70)
                else:
                    color = (55, 55, 70) if row % 2 == 0 else (60, 60, 80)
                
                pg.draw.rect(screen, color, item_rect)
                
                # Yellow border when hovered
                if self.hovered_index == actual_index:
                    pg.draw.rect(screen, (255, 220, 100), item_rect, 2)
                else:
                    pg.draw.rect(screen, (90, 90, 110), item_rect, 1)
                
                # Item name (top-left)
                if self.hovered_index == actual_index:
                    pg.draw.rect(screen, (255, 220, 100), item_rect, 2)
                else:
                    pg.draw.rect(screen, (90, 90, 110), item_rect, 1)
                
                # --- DRAW ICON INSTEAD OF TEXT ---
                icon = self._get_item_icon(item_name)
                if icon:
                    # Place the icon perfectly centered in the left area of the card
                    icon_rect = icon.get_rect(center=(item_rect.x + 40, item_rect.centery - 5))
                    screen.blit(icon, icon_rect)
                else:
                    # Fallback just in case the PNG is missing
                    name_display = item_name[:10] + ".." if len(item_name) > 10 else item_name
                    name_text = self.font_medium.render(name_display, True, (255, 255, 200))
                    screen.blit(name_text, (item_rect.x + 8, item_rect.y + 8))
                
                # Status text (bottom-left)
                if is_equippable:
                    if is_equipped:
                        status_text = self.font_small.render("Equipped", True, (100, 255, 100))
                    else:
                        status_text = self.font_small.render("Not Equipped", True, (200, 200, 200))
                    screen.blit(status_text, (item_rect.x + 8, item_rect.y + 58))
                else:
                    cat_text = self.font_small.render(f"[{cat.upper()}]", True, (150, 150, 150))
                    screen.blit(cat_text, (item_rect.x + 8, item_rect.y + 58))
                
                # Equip/Unequip button (bottom-right)
                if is_equippable:
                    btn_rect = pg.Rect(item_rect.right - 55, item_rect.bottom - 25, 50, 20)
                    mouse_pos = pg.mouse.get_pos()
                    
                    if is_equipped:
                        btn_color = (130, 70, 70) if btn_rect.collidepoint(mouse_pos) else (100, 50, 50)
                        btn_text = "UNEQUIP"
                        self.equip_buttons[f"unequip_{item_name}"] = btn_rect
                    else:
                        btn_color = (70, 100, 130) if btn_rect.collidepoint(mouse_pos) else (50, 70, 100)
                        btn_text = "EQUIP"
                        self.equip_buttons[f"equip_{item_name}"] = btn_rect
                    
                    pg.draw.rect(screen, btn_color, btn_rect)
                    pg.draw.rect(screen, (200, 200, 200), btn_rect, 1)
                    btn_render = self.font_small.render(btn_text, True, (255, 255, 255))
                    btn_render_rect = btn_render.get_rect(center=btn_rect.center)
                    screen.blit(btn_render, btn_render_rect)

            # Scrollbar
            if len(items) > 6:
                scroll_bg = pg.Rect(self.rect.x + self.rect.width - 20, self.rect.y + 45, 10, 100)
                pg.draw.rect(screen, (40, 40, 50), scroll_bg)
                pg.draw.rect(screen, (100, 100, 120), scroll_bg, 1)
                
                scroll_ratio = self.scroll_offset / (len(items) - 6) if len(items) > 6 else 0
                scroll_bar_height = max(20, scroll_bg.height * 0.3)
                scroll_bar_y = scroll_bg.y + int(scroll_ratio * (scroll_bg.height - scroll_bar_height))
                scroll_bar = pg.Rect(scroll_bg.x, scroll_bar_y, scroll_bg.width, scroll_bar_height)
                pg.draw.rect(screen, (180, 180, 200), scroll_bar)
                pg.draw.rect(screen, (220, 220, 240), scroll_bar, 1)

        # Description box
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
                # 1. Item Name
                name_text = self.font_large.render(self.selected_item, True, (255, 255, 200))
                screen.blit(name_text, (desc_x + 12, y))
                y += 28
                
                # 2. Get Live Stats from Equipment Database
                item_data = Equipment_System.equipment_database.get(self.selected_item, {})
                level = item_data.get("level", 1)
                multiplier = item_data.get("multiplier", 1.0)
                rarity = item_data.get("rarity", "Common")
                
                # Render Stats Line
                stats_str = f"Level: {level}  |  Rarity: {rarity}  |  Damage Multiplier: x{multiplier:.2f}"
                stats_text = self.font_small.render(stats_str, True, (100, 255, 100))
                screen.blit(stats_text, (desc_x + 12, y))
                y += 22
                
                # Draw a clean divider line
                pg.draw.line(screen, (100, 100, 120), (desc_x + 12, y), (desc_x + desc_w - 12, y), 1)
                y += 10
                
                # 3. Description
                description = self._get_item_description(self.selected_item)
                desc_lines = self._wrap_text(description, self.font_small, desc_w - 24)
                for line in desc_lines:
                    desc_text = self.font_small.render(line, True, (180, 180, 200))
                    screen.blit(desc_text, (desc_x + 12, y))
                    y += 18

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