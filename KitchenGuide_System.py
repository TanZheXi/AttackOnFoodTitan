import pygame as pg
import time
from datetime import datetime

pg.init()
pg.font.init()

class GuideQuest:
    def __init__(self, quest_id, name, description, requirement_text, requirement_target, reward_type):
        self.quest_id = quest_id
        self.name = name
        self.description = description
        self.requirement_text = requirement_text
        self.requirement_target = requirement_target
        self.reward_type = reward_type  # "weapon", "equipment", "pet", "boost"
        self.completed = False
        self.claimed = False
        self.progress = 0

    def update_progress(self, amount=1):
        if self.completed or self.claimed:
            return False
        self.progress = min(self.progress + amount, self.requirement_target)
        if self.progress >= self.requirement_target:
            self.completed = True
        return True

    def get_progress_percentage(self):
        if self.requirement_target == 0:
            return 100
        return int((self.progress / self.requirement_target) * 100)

    def get_requirement_text(self):
        return f"{self.requirement_text}: {self.progress}/{self.requirement_target}"

    def can_claim(self):
        return self.completed and not self.claimed

    def claim(self, guide_manager):
        if self.can_claim():
            self.claimed = True
            guide_manager.grant_reward(self.reward_type)
            return True
        return False


class GuideManager:
    def __init__(self):
        self.quests = []
        self.boost_active = False
        self.boost_end_time = 0
        self.boost_multiplier = 2.0
        self.all_rewards_claimed = False
        self._init_quests()

    def _init_quests(self):
        # Quest 1: Start Cooking
        quest1 = GuideQuest(
            0, "Start Cooking",
            "Click on any place on middle area to deal damage to monster",
            "Cook Food Titan", 10, "weapon"
        )
        # Quest 2: Equip an Equipment
        quest2 = GuideQuest(
            1, "Equip an Equipment",
            "Buy an equipment at shop and equip it in inventory",
            "Equip any equipment", 1, "equipment"
        )
        # Quest 3: Equip a pet
        quest3 = GuideQuest(
            2, "Equip a Pet",
            "Buy a pet at shop and equip it in pet inventory",
            "Equip any pet", 1, "pet"
        )
        # Quest 4: Show your improvement
        quest4 = GuideQuest(
            3, "Show your improvement!",
            "Each stage contains 10 Food Titans, defeat them and reach stage 2! All the best Chef!",
            "Reach Stage", 2, "boost"
        )

        self.quests = [quest1, quest2, quest3, quest4]

    def update_progress(self, progress_type, amount=1):
        """Update quest progress based on game events"""
        for quest in self.quests:
            if quest.completed or quest.claimed:
                continue
            
            if progress_type == "defeat_titan":
                if quest.quest_id == 0:
                    quest.update_progress(amount)
            elif progress_type == "equip_equipment":
                if quest.quest_id == 1:
                    quest.update_progress(amount)
            elif progress_type == "equip_pet":
                if quest.quest_id == 2:
                    quest.update_progress(amount)
            elif progress_type == "stage_reached":
                if quest.quest_id == 3:
                    quest.update_progress(amount)

    def grant_reward(self, reward_type):
        """Grant reward based on type"""
        if reward_type == "weapon":
            print("[KITCHEN GUIDE] Reward granted: Weapon (Rusty Spatula)")
            # Add to inventory and equipment system
            if hasattr(self, 'external_callbacks'):
                self.external_callbacks.get("add_to_inventory", lambda x: None)("Rusty Spatula")
                self.external_callbacks.get("gain_equipment", lambda x: None)("Rusty Spatula")
        elif reward_type == "equipment":
            print("[KITCHEN GUIDE] Reward granted: Equipment (Master Chef Hat)")
            if hasattr(self, 'external_callbacks'):
                self.external_callbacks.get("add_to_inventory", lambda x: None)("Master Chef Hat")
                self.external_callbacks.get("gain_equipment", lambda x: None)("Master Chef Hat")
        elif reward_type == "pet":
            print("[KITCHEN GUIDE] Reward granted: Pet (Baby Slime)")
            if hasattr(self, 'external_callbacks'):
                self.external_callbacks.get("add_to_inventory", lambda x: None)("Baby Slime")
                self.external_callbacks.get("add_pet", lambda x: None)("Baby Slime")
        elif reward_type == "boost":
            print("[KITCHEN GUIDE] Reward granted: x2 Currency Boost for 3 hours!")
            self.boost_active = True
            self.boost_end_time = time.time() + (3 * 60 * 60)  # 3 hours

    def is_boost_active(self):
        """Check if boost is still active"""
        if self.boost_active:
            if time.time() >= self.boost_end_time:
                self.boost_active = False
                print("[KITCHEN GUIDE] x2 Currency Boost has expired!")
        return self.boost_active

    def get_boost_multiplier(self):
        return self.boost_multiplier if self.is_boost_active() else 1.0

    def check_all_completed(self):
        """Check if all quests are claimed"""
        all_claimed = all(q.claimed for q in self.quests)
        if all_claimed and not self.all_rewards_claimed:
            self.all_rewards_claimed = True
            print("[KITCHEN GUIDE] All quests completed! Guide will be removed.")
        return all_claimed

    def get_save_data(self):
        quest_data = []
        for quest in self.quests:
            quest_data.append({
                "completed": quest.completed,
                "claimed": quest.claimed,
                "progress": quest.progress
            })
        return {
            "quests": quest_data,
            "boost_active": self.boost_active,
            "boost_end_time": self.boost_end_time,
            "all_rewards_claimed": self.all_rewards_claimed
        }

    def restore_save_data(self, data):
        if not data:
            return
        quests_data = data.get("quests", [])
        for i, quest_data in enumerate(quests_data):
            if i < len(self.quests):
                self.quests[i].completed = quest_data.get("completed", False)
                self.quests[i].claimed = quest_data.get("claimed", False)
                self.quests[i].progress = quest_data.get("progress", 0)
        self.boost_active = data.get("boost_active", False)
        self.boost_end_time = data.get("boost_end_time", 0)
        self.all_rewards_claimed = data.get("all_rewards_claimed", False)


class KitchenGuideSystem:
    def __init__(self, x, y, width, height):
        self.rect = pg.Rect(x, y, width, height)
        self.font_small = pg.font.SysFont(None, 14)
        self.font_medium = pg.font.SysFont(None, 20)
        self.font_large = pg.font.SysFont(None, 26)
        self.font_desc = pg.font.SysFont(None, 16)
        self.guide_manager = GuideManager()
        self.message = ""
        self.message_timer = 0
        self.hovered_quest_index = -1
        self.external_callbacks = {}

    def set_callbacks(self, callbacks):
        """Set external callbacks for rewards"""
        self.guide_manager.external_callbacks = callbacks
        self.external_callbacks = callbacks

    def update(self):
        if self.message_timer > 0:
            self.message_timer -= 1
        else:
            self.message = ""

    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos
            quests = self.guide_manager.quests
            card_height = 90
            card_spacing = 10
            start_y = self.rect.y + 45

            for i, quest in enumerate(quests):
                card_rect = pg.Rect(self.rect.x + 15, start_y + i * (card_height + card_spacing),
                                   self.rect.width - 30, card_height)
                btn_rect = pg.Rect(card_rect.right - 65, card_rect.bottom - 25, 55, 20)
                if btn_rect.collidepoint(mouse_pos):
                    if quest.can_claim():
                        if self.guide_manager.claim_quest(i):  # Need to implement claim_quest method
                            reward_names = {0: "Weapon", 1: "Equipment", 2: "Pet", 3: "x2 Boost (3h)"}
                            self.message = f"Claimed: {reward_names.get(quest.quest_id, 'Reward')}!"
                            self.message_timer = 180
                        else:
                            self.message = "Quest not ready to claim!"
                            self.message_timer = 120
                    elif quest.claimed:
                        self.message = "Already claimed!"
                        self.message_timer = 120
                    else:
                        self.message = "Complete the requirement first!"
                        self.message_timer = 120
                    return

    def claim_quest(self, quest_index):
        """Helper method to claim quest"""
        if quest_index < len(self.guide_manager.quests):
            return self.guide_manager.quests[quest_index].claim(self.guide_manager)
        return False

    def get_boost_multiplier(self):
        return self.guide_manager.get_boost_multiplier()

    def is_guide_completed(self):
        return self.guide_manager.check_all_completed()

    def draw(self, screen):
        # Panel background
        pg.draw.rect(screen, (45, 45, 55), self.rect)
        pg.draw.rect(screen, (150, 150, 170), self.rect, 2)

        quests = self.guide_manager.quests
        card_height = 90
        card_spacing = 10
        start_y = self.rect.y + 15

        # Track hover
        mouse_pos = pg.mouse.get_pos()
        self.hovered_quest_index = -1

        for i, quest in enumerate(quests):
            card_rect = pg.Rect(self.rect.x + 15, start_y + i * (card_height + card_spacing),
                               self.rect.width - 30, card_height)

            # Check hover
            if card_rect.collidepoint(mouse_pos):
                self.hovered_quest_index = i

            # Card background
            if quest.claimed:
                color = (60, 60, 70)
            elif quest.completed:
                color = (65, 85, 65)
            else:
                color = (50, 50, 65)

            pg.draw.rect(screen, color, card_rect)
            pg.draw.rect(screen, (200, 200, 220), card_rect, 1)

            # Quest name
            name_text = self.font_medium.render(quest.name, True, (255, 220, 100))
            screen.blit(name_text, (card_rect.x + 10, card_rect.y + 5))

            # Requirement text
            req_text = quest.get_requirement_text()
            req_surface = self.font_small.render(req_text, True, (200, 200, 220))
            screen.blit(req_surface, (card_rect.x + 15, card_rect.y + 30))

            # Progress bar
            progress_pct = quest.get_progress_percentage()
            bar_rect = pg.Rect(card_rect.x + 15, card_rect.y + 50, card_rect.width - 100, 10)
            pg.draw.rect(screen, (60, 60, 80), bar_rect)
            pg.draw.rect(screen, (100, 100, 120), bar_rect, 1)
            fill_rect = pg.Rect(bar_rect.x, bar_rect.y, int(bar_rect.width * progress_pct / 100), bar_rect.height)
            pg.draw.rect(screen, (220, 220, 240), fill_rect)

            # Claim button
            btn_rect = pg.Rect(card_rect.right - 65, card_rect.bottom - 25, 55, 20)

            if quest.claimed:
                btn_color = (80, 80, 80)
                btn_text = "CLAIMED"
            elif quest.can_claim():
                btn_color = (70, 130, 70) if btn_rect.collidepoint(mouse_pos) else (50, 100, 50)
                btn_text = "CLAIM"
            else:
                btn_color = (80, 80, 80) if btn_rect.collidepoint(mouse_pos) else (70, 70, 70)
                btn_text = "LOCKED"

            pg.draw.rect(screen, btn_color, btn_rect)
            pg.draw.rect(screen, (200, 200, 200), btn_rect, 1)
            btn_render = self.font_small.render(btn_text, True, (255, 255, 255))
            btn_rect_center = btn_render.get_rect(center=btn_rect.center)
            screen.blit(btn_render, btn_rect_center)

        # ========== DESCRIPTION BOX (shows quest description on hover) ==========
        desc_y = self.rect.y + 15 + 4 * (card_height + card_spacing) + 10
        desc_height = 100
        desc_rect = pg.Rect(self.rect.x + 15, desc_y, self.rect.width - 30, desc_height)

        pg.draw.rect(screen, (35, 35, 45), desc_rect)
        pg.draw.rect(screen, (100, 100, 120), desc_rect, 2)

        desc_title = self.font_medium.render("QUEST INFO", True, (255, 220, 100))
        screen.blit(desc_title, (desc_rect.x + 10, desc_rect.y + 5))

        if self.hovered_quest_index >= 0 and self.hovered_quest_index < len(quests):
            quest = quests[self.hovered_quest_index]
            # Quest name
            name_text = self.font_small.render(quest.name, True, (255, 255, 200))
            screen.blit(name_text, (desc_rect.x + 10, desc_rect.y + 30))

            # Description (wrapped)
            desc_lines = self._wrap_text(quest.description, self.font_desc, desc_rect.width - 20)
            y_offset = desc_rect.y + 52
            for line in desc_lines:
                line_surface = self.font_desc.render(line, True, (180, 180, 200))
                screen.blit(line_surface, (desc_rect.x + 10, y_offset))
                y_offset += 18

            # Reward info
            reward_names = {0: "Reward: Weapon", 1: "Reward: Equipment", 2: "Reward: Pet", 3: "Reward: x2 Currency Boost (3h)"}
            reward_text = reward_names.get(quest.quest_id, "")
            reward_surface = self.font_small.render(reward_text, True, (255, 200, 100))
            screen.blit(reward_surface, (desc_rect.x + 10, desc_rect.bottom - 22))
        else:
            hint_text = self.font_small.render("Hover over a quest to see details", True, (150, 150, 170))
            hint_rect = hint_text.get_rect(center=(desc_rect.centerx, desc_rect.centery))
            screen.blit(hint_text, hint_rect)
        # ================================================================

        if self.message and self.message_timer > 0:
            msg_surface = self.font_medium.render(self.message, True, (255, 255, 150))
            msg_rect = msg_surface.get_rect(center=(self.rect.centerx, self.rect.bottom - 10))
            screen.blit(msg_surface, msg_rect)

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