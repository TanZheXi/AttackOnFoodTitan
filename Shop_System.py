import pygame as pg

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
        self.font_small = pg.font.SysFont(None, 16)
        self.font_medium = pg.font.SysFont(None, 20)
        self.font_large = pg.font.SysFont(None, 24)

        # 9 items for 3x3 grid (Creating a 3x3 boxes storing goods that the Shop will sells)
        self.items = [
            ShopItem("Apple", 80, "Uncommon", "Fruit 1", (180, 180, 220)),
            ShopItem("Banana", 30, "Common", "Fruit 2", (220, 120, 120)),
            ShopItem("Carrot", 120, "Rare", "Fruit 3", (150, 150, 200)),
            ShopItem("Ur dad belt", 200, "Epic", "Ur dad favourite weapon", (200, 130, 250)),
            ShopItem("Ur sister's pen", 45, "Common", "Sis pls don't tell mom about it, I will do anything", (160, 120, 80)),
            ShopItem("Ur mom credit card", 300, "Legendary", "Mom gonna be so mad about me if she know", (255, 100, 50)),
            ShopItem("Wok", 60, "Rare", "Tool 1", (255, 215, 0)),
            ShopItem("Fork", 90, "Uncommon", "Tool 2", (170, 170, 190)),
            ShopItem("Spon", 150, "Epic", "Tool 3", (180, 100, 220)),
        ]

        self.selected_item = None
        self.hovered_index = -1
        self.buy_messages = []
        self.message_timer = 0

        # Grid settings (3x3 grid setting)
        self.grid_cols = 3
        self.grid_rows = 3
        self.cell_size = 70
        self.grid_start_x = self.rect.x + 10
        self.grid_start_y = self.rect.y + 50
        self.cell_spacing = 8

    def update(self):
        if self.message_timer > 0:
            self.message_timer -= 1
        else:
            self.buy_messages = []

    def handle_event(self, event, pocket_money, add_to_inventory_callback):
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
                            if pocket_money >= item.price:
                                add_to_inventory_callback(item.name)
                                pocket_money -= item.price
                                item.sold_out = True
                                self.buy_messages.append(f"Purchased {item.name}! -{item.price} Pocket money")
                                self.message_timer = 120
                                # Print code just for testing
                                print(f"[SHOP] Purchased {item.name} for {item.price} Pocket money. Remaining: {pocket_money}")
                            else:
                                self.buy_messages.append(f"Not enough money! Need {item.price}")
                                self.message_timer = 120
                                print(f"[SHOP] Failed to buy {item.name}: Need {item.price}, have {pocket_money}")
                        break
        return pocket_money

    def draw(self, screen):
        # Shop background
        pg.draw.rect(screen, (45, 45, 55), self.rect)
        pg.draw.rect(screen, (150, 150, 170), self.rect, 2)

        # Title
        title = self.font_large.render("SHOP", True, (255, 220, 100))
        title_rect = title.get_rect(center=(self.rect.centerx, self.rect.y + 25))
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
                    # Sold：Semi-Transparent Dark Black
                    color = (60, 60, 70)
                elif self.hovered_index == idx:
                    # Mouse hover above button：Dark color
                    color = (80, 80, 100)
                else:
                    color = item.icon_color

                pg.draw.rect(screen, color, cell_rect)
                pg.draw.rect(screen, (200, 200, 220), cell_rect, 2)

                # Item name (wrapped to fit) - Show goods' name in the middle of button
                if item.sold_out:
                    font = self.font_small
                    text = font.render("SOLD OUT", True, (150, 150, 150))
                    text_rect = text.get_rect(center=cell_rect.center)
                    screen.blit(text, text_rect)
                else:
                    font = self.font_small
                    if len(item.name) > 12:
                        name_display = item.name[:10] + "..."
                    else:
                        name_display = item.name
                    text = font.render(name_display, True, (255, 255, 255))
                    text_rect = text.get_rect(center=(cell_rect.centerx, cell_rect.centery - 10))
                    screen.blit(text, text_rect)

                    # Show "Buy it?" when Mouse hover on top of the items
                    if self.hovered_index == idx:
                        buy_text = self.font_small.render("Buy it?", True, (255, 255, 150))
                        buy_rect = buy_text.get_rect(center=(cell_rect.centerx, cell_rect.centery + 15))
                        screen.blit(buy_text, buy_rect)

        # Draw info panel on the right side of shop
        # Show a tips panel about information of the items in Shop
        info_panel_x = self.rect.x + self.rect.width - 190
        info_panel_y = self.rect.y + 50
        info_panel_width = 175
        info_panel_height = 280

        if self.selected_item and self.hovered_index != -1:
            # Clay color panel
            pg.draw.rect(screen, (60, 60, 75), (info_panel_x, info_panel_y, info_panel_width, info_panel_height))
            pg.draw.rect(screen, (180, 180, 200), (info_panel_x, info_panel_y, info_panel_width, info_panel_height), 2)

            y_offset = info_panel_y + 15
            # Goods' name
            name_text = self.font_medium.render(self.selected_item.name, True, (255, 255, 200))
            screen.blit(name_text, (info_panel_x + 10, y_offset))
            y_offset += 35

            # Goods' prices
            price_text = self.font_small.render(f"Price: {self.selected_item.price}", True, (255, 220, 100))
            screen.blit(price_text, (info_panel_x + 10, y_offset))
            y_offset += 25

            # Goods' rarity
            rarity_color = self.selected_item.get_rarity_color()
            rarity_text = self.font_small.render(f"Rarity: {self.selected_item.rarity}", True, rarity_color)
            screen.blit(rarity_text, (info_panel_x + 10, y_offset))
            y_offset += 30

            # Description about goods
            desc_lines = self.wrap_text(self.selected_item.description, self.font_small, 180)
            for line in desc_lines:
                desc_text = self.font_small.render(line, True, (200, 200, 220))
                screen.blit(desc_text, (info_panel_x + 10, y_offset))
                y_offset += 22

        # Draw message at bottom
        if self.buy_messages and self.message_timer > 0:
            msg = self.buy_messages[-1]
            msg_surface = self.font_medium.render(msg, True, (255, 255, 150))
            msg_rect = msg_surface.get_rect(center=(self.rect.centerx, self.rect.y + self.rect.height - 20))
            screen.blit(msg_surface, msg_rect)

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