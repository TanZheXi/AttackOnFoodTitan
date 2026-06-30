import pygame as pg
import Currency_System
import os
from Audio_System import GLOBAL_CLICK

pg.init()
pg.font.init()

class ShopItem:
    def __init__(self, name, price, rarity, description, icon_color, category):
        self.name = name
        self.price = price
        self.rarity = rarity
        self.description = description
        self.icon_color = icon_color
        self.category = category
        self.sold_out = False

    def get_rarity_color(self):
        rarity_colors = {
            "Common": (200, 200, 200),
            "Uncommon": (100, 255, 100),
            "Rare": (100, 150, 255),
            "Epic": (170, 100, 255),
            "Legendary": (255, 150, 50),
            "Mythic": (255, 100, 100)
        }
        return rarity_colors.get(self.rarity, (200, 200, 200))


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
        
        if hasattr(self, 'icon_image') and self.icon_image:
            # Draw centered icon
            icon_rect = self.icon_image.get_rect(center=self.rect.center)
            screen.blit(self.icon_image, icon_rect)
        else:
            text_surf = self.font.render(self.text, True, (255, 255, 255))
            text_rect = text_surf.get_rect(center=self.rect.center)
            screen.blit(text_surf, text_rect)


class ShopSystem:
    def __init__(self, x, y, width, height):
        self.rect = pg.Rect(x, y, width, height)
        self.font_small = pg.font.SysFont(None, 14)
        self.font_medium = pg.font.SysFont(None, 20)
        self.font_large = pg.font.SysFont(None, 24)

        self.icon_cache = {}
        
        # All goods
        self.all_items = [
            # Weapon Shop (0)
            ShopItem("Rusty Spatula", 100, "Common", "An old spatula. Better than nothing.", (150, 150, 150), "weapon"),
            ShopItem("Golden Spatula", 500, "Rare", "A legendary cooking tool. Flip anything!", (255, 215, 0), "weapon"),
            ShopItem("Chef's Wok", 2000, "Epic", "Master chef's wok. Perfect for stir-frying.", (200, 150, 50), "weapon"),
            ShopItem("Mythic Pan", 10000, "Mythic", "A pan of legendary power. Sizzles with energy.", (255, 100, 100), "weapon"),
            ShopItem("OP WEAPON", 999999, "Mythic", "Overpowered weapon! Use with care.", (255, 50, 50), "weapon"),
            # Equipment Shop (1)
            ShopItem("Master Chef Hat", 1500, "Rare", "Increases cooking skill. Look professional!", (200, 180, 100), "equipment"),
            ShopItem("Titanium Apron", 4000, "Epic", "Heavy-duty protection. Stain resistant.", (150, 150, 200), "equipment"),
            ShopItem("Roasted Garlic Aroma", 5000, "Epic", "Smells amazing! Distracts enemies.", (200, 150, 100), "equipment"),
            ShopItem("Speed Boots", 2000, "Rare", "Increases movement speed. Very comfortable.", (100, 150, 200), "equipment"),
            ShopItem("Magic Ring", 8000, "Legendary", "Boosts all stats. Glows with power.", (255, 200, 100), "equipment"),
            # Pet Shop (2)
            ShopItem("Baby Slime", 500, "Common", "A cute slime pet. Jiggly and friendly.", (100, 200, 100), "pet"),
            ShopItem("Fire Spirit", 2000, "Epic", "Burns enemies with passion. Handle with care.", (255, 100, 50), "pet"),
            ShopItem("Fairy", 5000, "Epic", "Heals owner over time. Very rare indeed.", (200, 150, 255), "pet"),
            ShopItem("Dragon Whelp", 15000, "Legendary", "A baby dragon. Breathes tiny flames.", (255, 100, 100), "pet"),
            ShopItem("Phoenix", 30000, "Mythic", "Rises from ashes. Immortal companion.", (255, 100, 50), "pet"),
            # Scraps Shop (3)
            ShopItem("Scrap Pack S", 100, "Common", "Contains 10 scraps. For basic crafting.", (200, 200, 200), "scraps"),
            ShopItem("Scrap Pack M", 500, "Uncommon", "Contains 50 scraps. Better value!", (200, 200, 150), "scraps"),
            ShopItem("Scrap Pack L", 2000, "Rare", "Contains 250 scraps. Great deal!", (200, 200, 100), "scraps"),
            ShopItem("Scrap Pack XL", 8000, "Epic", "Contains 1000 scraps. Massive pile!", (200, 180, 80), "scraps"),
            ShopItem("Scrap Pack XXL", 30000, "Legendary", "Contains 5000 scraps. Mountain of scraps!", (200, 150, 50), "scraps"),
        ]

        self.category_map = {
            0: "weapon",
            1: "equipment", 
            2: "pet",
            3: "scraps"
        }
        
        self.current_category = 0
        self.items = []
        self.update_items_by_category()

        self.selected_item = None
        self.hovered_index = -1
        self.buy_messages = []
        self.message_timer = 0

        self.category_buttons = []
        self._init_category_buttons()

        # ========== Grid Settings ==========
        self.grid_cols = 5
        self.cell_spacing = 6
        available_width = self.rect.width - 20
        total_spacing = self.cell_spacing * (self.grid_cols - 1)
        self.cell_size = (available_width - total_spacing) // self.grid_cols
        
        self.grid_start_x = self.rect.x + 10
        self.grid_start_y = self.rect.y + 48
        # ===================================

        self.desc_panel_rect = None

    def _init_category_buttons(self):
        btn_width = 75
        btn_height = 28
        spacing = 8
        total_width = btn_width * 4 + spacing * 3
        start_x = self.rect.centerx - total_width // 2
        y = self.rect.y + 8
        
        categories = ["Weapon", "Equipment", "Pet", "Scraps"]
        icon_names = ["Weapon", "Equipment", "Pet", "Scraps"]
        
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
        self.update_items_by_category()
        for btn in self.category_buttons:
            btn.is_selected = (btn.category_id == self.current_category)

    def update_items_by_category(self):
        category = self.category_map.get(self.current_category, "weapon")
        self.items = [item for item in self.all_items if item.category == category]

    def set_desc_panel_rect(self, rect):
        self.desc_panel_rect = rect

    def restore_shop_state(self, shop_state):
        if not shop_state:
            return
        for saved_item in shop_state:
            saved_name = saved_item.get("name")
            saved_sold_out = saved_item.get("sold_out", False)
            for item in self.all_items:
                if item.name == saved_name:
                    item.sold_out = saved_sold_out
                    break
        self.update_items_by_category()

    def get_shop_state(self):
        return [{"name": item.name, "sold_out": item.sold_out} for item in self.all_items]

    def reset_shop(self):
        for item in self.all_items:
            item.sold_out = False
        self.update_items_by_category()
        print(f"[SHOP] Shop restocked on prestige.")

    def update(self):
        if self.message_timer > 0:
            self.message_timer -= 1
        else:
            self.buy_messages = []

    def handle_event(self, event, add_to_inventory_callback):
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            for btn in self.category_buttons:
                if btn.rect.collidepoint(event.pos):
                    if GLOBAL_CLICK: GLOBAL_CLICK.play()
                    self.set_category(btn.category_id)
                    return

        if event.type == pg.MOUSEMOTION:
            self.hovered_index = -1
            mouse_pos = event.pos
            rows = (len(self.items) + self.grid_cols - 1) // self.grid_cols
            for i in range(rows):
                for j in range(self.grid_cols):
                    idx = i * self.grid_cols + j
                    if idx >= len(self.items):
                        continue
                    cell_x = self.grid_start_x + j * (self.cell_size + self.cell_spacing)
                    cell_y = self.grid_start_y + i * (self.cell_size + self.cell_spacing)
                    cell_rect = pg.Rect(cell_x, cell_y, self.cell_size, self.cell_size)
                    if cell_rect.collidepoint(mouse_pos):
                        self.hovered_index = idx
                        self.selected_item = self.items[idx]
                        break

        # Logics for buying items
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            rows = (len(self.items) + self.grid_cols - 1) // self.grid_cols
            for i in range(rows):
                for j in range(self.grid_cols):
                    idx = i * self.grid_cols + j
                    if idx >= len(self.items):
                        continue
                    cell_x = self.grid_start_x + j * (self.cell_size + self.cell_spacing)
                    cell_y = self.grid_start_y + i * (self.cell_size + self.cell_spacing)
                    cell_rect = pg.Rect(cell_x, cell_y, self.cell_size, self.cell_size)
                    if cell_rect.collidepoint(event.pos):
                        if GLOBAL_CLICK:
                            GLOBAL_CLICK.play()
                        item = self.items[idx]
                        if not item.sold_out:
                            if Currency_System.pocket_money >= item.price:
                                add_to_inventory_callback(item.name)
                                Currency_System.pocket_money -= item.price
                                item.sold_out = True
                                self.buy_messages.append(f"Bought {item.name}!")
                                self.message_timer = 120
                            else:
                                self.buy_messages.append(f"Need ${item.price}!")
                                self.message_timer = 120
                        break
            
    def _get_item_icon(self, item_name, target_size):
        """Loads, cleans, and scales the item icon, then caches it."""
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
                    
                # Scale properly so it fits without getting squashed
                scale = min(target_size / img.get_width(), target_size / img.get_height())
                new_w, new_h = int(img.get_width() * scale), int(img.get_height() * scale)
                img = pg.transform.scale(img, (new_w, new_h))
                
                self.icon_cache[item_name] = img
                return img
            except Exception as e:
                pass
                
        self.icon_cache[item_name] = None
        return None

    def draw(self, screen):
        pg.draw.rect(screen, (45, 45, 55), self.rect)
        pg.draw.rect(screen, (150, 150, 170), self.rect, 2)

        # Draw category buttons
        for btn in self.category_buttons:
            btn.draw(screen)

        # Draw items in grid
        rows = (len(self.items) + self.grid_cols - 1) // self.grid_cols
        for i in range(rows):
            for j in range(self.grid_cols):
                idx = i * self.grid_cols + j
                if idx >= len(self.items):
                    continue
                item = self.items[idx]
                cell_x = self.grid_start_x + j * (self.cell_size + self.cell_spacing)
                cell_y = self.grid_start_y + i * (self.cell_size + self.cell_spacing)
                cell_rect = pg.Rect(cell_x, cell_y, self.cell_size, self.cell_size)

                if item.sold_out:
                    color = (60, 60, 70)
                elif self.hovered_index == idx:
                    color = (80, 80, 100)
                else:
                    color = item.icon_color

                pg.draw.rect(screen, color, cell_rect)
                pg.draw.rect(screen, (200, 200, 220), cell_rect, 2)

                if item.sold_out:
                    text = self.font_small.render("SOLD OUT", True, (150, 150, 150))
                    text_rect = text.get_rect(center=cell_rect.center)
                    screen.blit(text, text_rect)
                else:
                    # --- NEW DRAW LOGIC STARTS HERE ---
                    target_icon_size = self.cell_size - 24 # Leaves room for price text
                    icon = self._get_item_icon(item.name, target_icon_size)
                    
                    if icon:
                        # Draw Image
                        icon_rect = icon.get_rect(center=(cell_rect.centerx, cell_rect.centery - 8))
                        screen.blit(icon, icon_rect)
                    else:
                        # Fallback text if the PNG is missing
                        name_display = item.name[:8] + ".." if len(item.name) > 9 else item.name
                        text = self.font_small.render(name_display, True, (255, 255, 255))
                        text_rect = text.get_rect(center=(cell_rect.centerx, cell_rect.centery - 10))
                        screen.blit(text, text_rect)

                    if item.price >= 10000:
                        price_display = f"{item.price//1000}k"
                    else:
                        price_display = str(item.price)
                        
                    price_text = self.font_small.render(f"${price_display}", True, (255, 220, 100))
                    # Lowered from +12 to +20 to prevent overlap with the image
                    price_rect = price_text.get_rect(center=(cell_rect.centerx, cell_rect.centery + 20)) 
                    screen.blit(price_text, price_rect)
                    # --- NEW DRAW LOGIC ENDS HERE ---

        if self.buy_messages and self.message_timer > 0:
            msg = self.buy_messages[-1]
            msg_surface = self.font_medium.render(msg, True, (255, 255, 150))
            msg_rect = msg_surface.get_rect(center=(self.rect.centerx, self.rect.y + self.rect.height - 15))
            screen.blit(msg_surface, msg_rect)
        
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
                name_text = self.font_medium.render(self.selected_item.name, True, (255, 255, 200))
                screen.blit(name_text, (desc_x + 12, y))
                y += 25
                
                price_text = self.font_small.render(f"Price: ${self.selected_item.price}", True, (255, 220, 100))
                screen.blit(price_text, (desc_x + 12, y))
                y += 20
                
                rarity_color = self.selected_item.get_rarity_color()
                rarity_text = self.font_small.render(f"Rarity: {self.selected_item.rarity}", True, rarity_color)
                screen.blit(rarity_text, (desc_x + 12, y))
                y += 20
                
                pg.draw.line(screen, (100, 100, 120), (desc_x + 12, y), (desc_x + desc_w - 12, y), 1)
                y += 10
                
                desc_lines = self.wrap_text(self.selected_item.description, self.font_small, desc_w - 24)
                for line in desc_lines:
                    desc_text = self.font_small.render(line, True, (180, 180, 200))
                    screen.blit(desc_text, (desc_x + 12, y))
                    y += 16
            else:
                hint_text1 = self.font_small.render("Hover over an item", True, (150, 150, 170))
                hint_rect1 = hint_text1.get_rect(center=(desc_x + desc_w // 2, y + 15))
                screen.blit(hint_text1, hint_rect1)
                
                hint_text2 = self.font_small.render("to see details", True, (150, 150, 170))
                hint_rect2 = hint_text2.get_rect(center=(desc_x + desc_w // 2, y + 35))
                screen.blit(hint_text2, hint_rect2)

    def wrap_text(self, text, font, max_width):
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