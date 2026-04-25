import pygame as pg

pg.init()
pg.font.init()

class InventorySystem:
    def __init__(self, x, y, width, height):
        self.rect = pg.Rect(x, y, width, height)
        self.font_small = pg.font.SysFont(None, 20)
        self.font_medium = pg.font.SysFont(None, 28)
        self.items = []  # List of item names
        self.scroll_offset = 0
        self.item_height = 30

    def restore_inventory(self, inventory_items):
        """Restore inventory from saved data"""
        self.items = inventory_items.copy()
        print(f"[INVENTORY] Restored {len(self.items)} items: {self.items}")

    def get_inventory_state(self):
        """Get current inventory for saving"""
        return self.items.copy()

    def add_item(self, item_name):
        """Adding items into player's inventory"""
        self.items.append(item_name)
        print(f"[INVENTORY] Added: {item_name}. Total items: {len(self.items)}")

    def handle_event(self, event):
        """Variable here is for scroling to view more Goods in Shop in the futere"""
        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 4:  # Scroll up
                self.scroll_offset = max(0, self.scroll_offset - 1)
            elif event.button == 5:  # Scroll down
                max_scroll = max(0, len(self.items) - 10)
                self.scroll_offset = min(max_scroll, self.scroll_offset + 1)

    def draw(self, screen):
        # Draw UI for Inventory
        pg.draw.rect(screen, (45, 45, 55), self.rect)
        pg.draw.rect(screen, (150, 150, 170), self.rect, 2)

        # Title
        title = self.font_medium.render("INVENTORY", True, (255, 220, 100))
        title_rect = title.get_rect(center=(self.rect.centerx, self.rect.y + 25))
        screen.blit(title, title_rect)

        # List items that the player have
        if not self.items:
            empty_text = self.font_medium.render("Empty", True, (150, 150, 150))
            empty_rect = empty_text.get_rect(center=self.rect.center)
            screen.blit(empty_text, empty_rect)
            return

        # Draw item list
        y_offset = self.rect.y + 55
        visible_items = self.items[self.scroll_offset:self.scroll_offset + 10]

        for idx, item_name in enumerate(visible_items):
            item_rect = pg.Rect(self.rect.x + 15, y_offset, self.rect.width - 30, self.item_height)
            color = (55, 55, 70) if idx % 2 == 0 else (60, 60, 80)
            pg.draw.rect(screen, color, item_rect)
            pg.draw.rect(screen, (120, 120, 140), item_rect, 1)

            item_text = self.font_small.render(f"• {item_name}", True, (220, 220, 240))
            screen.blit(item_text, (self.rect.x + 25, y_offset + 8))

            y_offset += self.item_height

        # Scroll indicator (Scroll bar)
        if len(self.items) > 10:
            scroll_text = self.font_small.render(f"Scroll: {self.scroll_offset + 1}-{min(self.scroll_offset + 10, len(self.items))}/{len(self.items)}", True, (180, 180, 180))
            screen.blit(scroll_text, (self.rect.x + 15, self.rect.y + self.rect.height - 25))