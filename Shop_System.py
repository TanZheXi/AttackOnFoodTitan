import pygame as pg
import Currency_System

pg.init()
pg.font.init()

class ShopItem:
    def __init__(self, name, price, rarity, description, icon_color):
        self.name = name
        self.price = price
        self.rarity = rarity
        self.description = description
        self.icon_color = icon_color
        self.sold_out = False

    def get_rarity_color(self):
        rarity_colors = {
            "Common": (200, 200, 200),
            "Uncommon": (100, 255, 100),
            "Rare": (100, 150, 255),
            "Epic": (170, 100, 255),
            "Legendary": (255, 150, 50)
        }
        return rarity_colors.get(self.rarity, (200, 200, 200))


class ShopSystem:
    def __init__(self, x, y, width, height):
        self.rect = pg.Rect(x, y, width, height)
        self.font_small = pg.font.SysFont(None, 14)
        self.font_medium = pg.font.SysFont(None, 18)
        self.font_large = pg.font.SysFont(None, 22)
        
        # Rectagle of Description Panel (Set by Button_System)
        self.desc_panel_rect = None

        # 9 items for 3x3 grid (Creating a 3x3 boxes storing goods that the Shop will sells)
        self.items = [
            ShopItem("Apple", 80, "Uncommon", "A crisp red apple. Keeps the doctor away!", (180, 180, 220)),
            ShopItem("Banana", 30, "Common", "A yellow banana. Great source of potassium.", (220, 120, 120)),
            ShopItem("Carrot", 120, "Rare", "A crunchy carrot. Good for your eyesight.", (150, 150, 200)),
            ShopItem("Ur dad belt", 200, "Epic", "Your father's favorite weapon. +50 respect.", (200, 130, 250)),
            ShopItem("Ur sister's pen", 45, "Common", "Borrowed without permission. Use carefully.", (160, 120, 80)),
            ShopItem("Ur mom credit card", 300, "Legendary", "Unlimited spending power. Use wisely!", (255, 100, 50)),
            ShopItem("Wok", 60, "Rare", "A versatile cooking tool. Also works as a shield.", (255, 215, 0)),
            ShopItem("Fork", 90, "Uncommon", "A three-pronged weapon. For dining and fighting.", (170, 170, 190)),
            ShopItem("Spon", 150, "Epic", "A hybrid spoon-fork. Very confusing to enemies.", (180, 100, 220)),
        ]

        self.selected_item = None
        self.hovered_index = -1
        self.buy_messages = []
        self.message_timer = 0

        # Grid settings (3x3 grid setting)
        self.grid_cols = 3
        self.grid_rows = 3
        self.cell_size = 65
        self.grid_start_x = self.rect.x + 10
        self.grid_start_y = self.rect.y + 40
        self.cell_spacing = 8

    def set_desc_panel_rect(self, rect):
        self.desc_panel_rect = rect

    def restore_shop_state(self, shop_state):
        """Restore which items were sold out from saved data"""
        if not shop_state:
            return
    
        for saved_item in shop_state:
            saved_name = saved_item.get("name")
            saved_sold_out = saved_item.get("sold_out", False)
            
            for item in self.items:
                if item.name == saved_name:
                    item.sold_out = saved_sold_out
                    break
        
        print(f"[SHOP] Restored shop state. Sold out items: {sum(1 for i in self.items if i.sold_out)}")

    def get_shop_state(self):
        """Get current shop state for saving"""
        shop_state = []
        for item in self.items:
            shop_state.append({
                "name": item.name,
                "sold_out": item.sold_out
            })
        return shop_state

    def update(self):
        if self.message_timer > 0:
            self.message_timer -= 1
        else:
            self.buy_messages = []

    def handle_event(self, event, add_to_inventory_callback):
        # Detect position of mouse hovered, then apply change of color to the button
        if event.type == pg.MOUSEMOTION:
            self.hovered_index = -1
            mouse_pos = event.pos
            for i in range(self.grid_rows):
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

        # Setting for buying goods
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            for i in range(self.grid_rows):
                for j in range(self.grid_cols):
                    idx = i * self.grid_cols + j
                    if idx >= len(self.items):
                        continue
                    cell_x = self.grid_start_x + j * (self.cell_size + self.cell_spacing)
                    cell_y = self.grid_start_y + i * (self.cell_size + self.cell_spacing)
                    cell_rect = pg.Rect(cell_x, cell_y, self.cell_size, self.cell_size)
                    if cell_rect.collidepoint(event.pos):
                        item = self.items[idx]
                        if not item.sold_out:
                            if Currency_System.pocket_money >= item.price:
                                add_to_inventory_callback(item.name)
                                Currency_System.pocket_money -= item.price
                                item.sold_out = True
                                self.buy_messages.append(f"Purchased {item.name}! -{item.price} Pocket money")
                                self.message_timer = 120
                                print(f"[SHOP] Purchased {item.name} for {item.price} Pocket money. Remaining: {Currency_System.pocket_money}")
                            else:
                                self.buy_messages.append(f"Not enough money! Need {item.price}")
                                self.message_timer = 120
                                print(f"[SHOP] Failed to buy {item.name}: Need {item.price}, have {Currency_System.pocket_money}")
                        break
        return Currency_System.pocket_money

    def draw(self, screen):
        # Shop background
        pg.draw.rect(screen, (45, 45, 55), self.rect)
        pg.draw.rect(screen, (150, 150, 170), self.rect, 2)

        # Title
        title = self.font_large.render("SHOP", True, (255, 220, 100))
        title_rect = title.get_rect(center=(self.rect.centerx, self.rect.y + 20))
        screen.blit(title, title_rect)

        # Draw 3x3 grid
        for i in range(self.grid_rows):
            for j in range(self.grid_cols):
                idx = i * self.grid_cols + j
                if idx >= len(self.items):
                    continue
                item = self.items[idx]
                cell_x = self.grid_start_x + j * (self.cell_size + self.cell_spacing)
                cell_y = self.grid_start_y + i * (self.cell_size + self.cell_spacing)
                cell_rect = pg.Rect(cell_x, cell_y, self.cell_size, self.cell_size)

                # Determine button color
                if item.sold_out:
                    color = (60, 60, 70)
                elif self.hovered_index == idx:
                    color = (80, 80, 100)
                else:
                    color = item.icon_color

                pg.draw.rect(screen, color, cell_rect)
                pg.draw.rect(screen, (200, 200, 220), cell_rect, 1)

                # Item name
                if item.sold_out:
                    font = self.font_small
                    text = font.render("SOLD OUT", True, (150, 150, 150))
                    text_rect = text.get_rect(center=cell_rect.center)
                    screen.blit(text, text_rect)
                else:
                    font = self.font_small
                    if len(item.name) > 10:
                        name_display = item.name[:8] + ".."
                    else:
                        name_display = item.name
                    text = font.render(name_display, True, (255, 255, 255))
                    text_rect = text.get_rect(center=(cell_rect.centerx, cell_rect.centery - 8))
                    screen.blit(text, text_rect)

                    if self.hovered_index == idx:
                        buy_text = self.font_small.render("Buy!", True, (255, 255, 150))
                        buy_rect = buy_text.get_rect(center=(cell_rect.centerx, cell_rect.centery + 10))
                        screen.blit(buy_text, buy_rect)

        # Draw message at bottom of shop panel
        if self.buy_messages and self.message_timer > 0:
            msg = self.buy_messages[-1]
            msg_surface = self.font_small.render(msg, True, (255, 255, 150))
            msg_rect = msg_surface.get_rect(center=(self.rect.centerx, self.rect.y + self.rect.height - 15))
            screen.blit(msg_surface, msg_rect)
        
        # ========== Draw Description Panel ==========
        if self.desc_panel_rect and self.selected_item and self.hovered_index != -1:
            desc_x = self.desc_panel_rect.x
            desc_y = self.desc_panel_rect.y
            desc_w = self.desc_panel_rect.width
            desc_h = self.desc_panel_rect.height
            
            # Description panel background
            pg.draw.rect(screen, (50, 50, 65), (desc_x, desc_y, desc_w, desc_h))
            pg.draw.rect(screen, (130, 130, 150), (desc_x, desc_y, desc_w, desc_h), 2)
            
            # Top decoration bar
            top_bar = pg.Rect(desc_x, desc_y, desc_w, 5)
            pg.draw.rect(screen, (255, 220, 100), top_bar)
            
            y_offset = desc_y + 15
            
            # Item name
            name_text = self.font_medium.render(self.selected_item.name, True, (255, 255, 200))
            name_rect = name_text.get_rect(center=(desc_x + desc_w // 2, y_offset))
            screen.blit(name_text, name_rect)
            y_offset += 30
            
            # Prices
            price_text = self.font_small.render(f"Price: {self.selected_item.price}", True, (255, 220, 100))
            screen.blit(price_text, (desc_x + 12, y_offset))
            y_offset += 22
            
            # Rarity with color
            rarity_color = self.selected_item.get_rarity_color()
            rarity_text = self.font_small.render(f"Rarity: {self.selected_item.rarity}", True, rarity_color)
            screen.blit(rarity_text, (desc_x + 12, y_offset))
            y_offset += 25
            
            # line separator
            pg.draw.line(screen, (100, 100, 120), (desc_x + 10, y_offset), (desc_x + desc_w - 10, y_offset), 1)
            y_offset += 12
            
            # Description with text wrapping
            desc_lines = self.wrap_text(self.selected_item.description, self.font_small, desc_w - 25)
            for line in desc_lines:
                desc_text = self.font_small.render(line, True, (200, 200, 220))
                screen.blit(desc_text, (desc_x + 12, y_offset))
                y_offset += 18
        
        elif self.desc_panel_rect:
            # Show default message when no item is hovered
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
            
            hint_text2 = self.font_small.render("to see details", True, (180, 180, 200))
            hint_rect2 = hint_text2.get_rect(center=(desc_x + desc_w // 2, desc_y + 105))
            screen.blit(hint_text2, hint_rect2)
        # =============================================

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