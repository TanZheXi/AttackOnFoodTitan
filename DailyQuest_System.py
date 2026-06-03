import pygame as pg
from datetime import datetime

pg.init()
pg.font.init()

class Quest:
    def __init__(self, quest_id, name, description, requirements, rewards):
        self.quest_id = quest_id
        self.name = name
        self.description = description
        self.requirements = requirements
        self.rewards = rewards
        self.completed = False
        self.claimed = False
        self.progress = [0] * len(requirements)

    def update_progress(self, req_index, amount=1):
        if self.completed or self.claimed:
            return False
        if req_index < len(self.progress):
            self.progress[req_index] = min(self.progress[req_index] + amount, self.requirements[req_index][1])
            self.check_completion()
            return True
        return False

    def check_completion(self):
        if self.completed:
            return
        all_complete = all(p >= req[1] for p, req in zip(self.progress, self.requirements))
        if all_complete:
            self.completed = True

    def get_progress_percentage(self, req_index):
        if req_index >= len(self.progress):
            return 0
        target = self.requirements[req_index][1]
        if target == 0:
            return 100
        return int((self.progress[req_index] / target) * 100)

    def get_requirement_text(self, req_index):
        if req_index >= len(self.requirements):
            return ""
        req = self.requirements[req_index]
        return f"{req[0]}: {self.progress[req_index]}/{req[1]}"

    def can_claim(self):
        return self.completed and not self.claimed

    def claim(self, quest_manager):
        if self.can_claim():
            self.claimed = True
            quest_manager.add_bottle_caps(self.rewards.get("bottle_cap", 0))
            return True
        return False


class QuestManager:
    MAX_BOTTLE_CAPS = 300  # Maximum bottle caps limit

    def __init__(self):
        self.quests = []
        self.selected_quest_index = -1
        self.bottle_caps = 0
        self.last_reset_date = None
        self._init_quests()
        self._check_daily_reset()

    def _init_quests(self):
        req1 = [
            ("Defeat Food Titan", 5),
            ("Upgrade base damage", 10),
            ("Upgrade any skill", 3)
        ]
        req2 = [
            ("Defeat with Magical Kitchenware", 5),
            ("Clear stage with Kitchenware", 1),
            ("Upgrade Magical Kitchenware", 5)
        ]
        req3 = [
            ("Defeat with pet", 5),
            ("Clear stage with pet", 1),
            ("Upgrade pet", 5)
        ]
        req4 = [
            ("Defeat Food Titan", 10)
        ]

        self.quests = [
            Quest(0, "Skill Improvement", "", req1, {"bottle_cap": 200}),
            Quest(1, "Coordinate Magical Kitchenware", "", req2, {"bottle_cap": 200}),
            Quest(2, "Picnic time with family and pets", "", req3, {"bottle_cap": 200}),
            Quest(3, "Scraps Engineering", "", req4, {"bottle_cap": 200})
        ]

    def _check_daily_reset(self):
        today = datetime.now().date()
        if self.last_reset_date:
            if isinstance(self.last_reset_date, str):
                last_date = datetime.fromisoformat(self.last_reset_date).date()
            else:
                last_date = self.last_reset_date
            if last_date != today:
                self.reset_daily_quests()
                # 每日重置时扣除超出上限的 bottle caps
                self._apply_bottle_cap_limit()
        self.last_reset_date = today.isoformat()

    def _apply_bottle_cap_limit(self):
        """Apply bottle cap limit, deduct excess amount"""
        if self.bottle_caps > self.MAX_BOTTLE_CAPS:
            excess = self.bottle_caps - self.MAX_BOTTLE_CAPS
            self.bottle_caps = self.MAX_BOTTLE_CAPS
            print(f"[DAILY QUEST] Daily reset: Excess {excess} Bottle Caps deducted. New total: {self.bottle_caps}")

    def reset_daily_quests(self):
        for quest in self.quests:
            quest.completed = False
            quest.claimed = False
            quest.progress = [0] * len(quest.requirements)
        self.selected_quest_index = -1
        print("[DAILY QUEST] Quests reset for new day")

    def update_progress(self, quest_id, req_index, amount=1):
        if quest_id < len(self.quests):
            return self.quests[quest_id].update_progress(req_index, amount)
        return False

    def update_progress_by_type(self, progress_type, amount=1):
        for quest in self.quests:
            if quest.completed or quest.claimed:
                continue
            if progress_type == "defeat_titan":
                quest.update_progress(0, amount)
            elif progress_type == "upgrade_base_damage":
                if quest.quest_id == 0:
                    quest.update_progress(1, amount)
            elif progress_type == "upgrade_skill":
                if quest.quest_id == 0:
                    quest.update_progress(2, amount)
            elif progress_type == "defeat_with_kitchenware":
                if quest.quest_id == 1:
                    quest.update_progress(0, amount)
            elif progress_type == "clear_stage_with_kitchenware":
                if quest.quest_id == 1:
                    quest.update_progress(1, amount)
            elif progress_type == "upgrade_kitchenware":
                if quest.quest_id == 1:
                    quest.update_progress(2, amount)
            elif progress_type == "defeat_with_pet":
                if quest.quest_id == 2:
                    quest.update_progress(0, amount)
            elif progress_type == "clear_stage_with_pet":
                if quest.quest_id == 2:
                    quest.update_progress(1, amount)
            elif progress_type == "upgrade_pet":
                if quest.quest_id == 2:
                    quest.update_progress(2, amount)
            elif progress_type == "gain_scraps":
                if quest.quest_id == 3:
                    quest.update_progress(0, amount)

    def claim_quest(self, quest_index):
        if quest_index < len(self.quests):
            return self.quests[quest_index].claim(self)
        return False

    def add_bottle_caps(self, amount):
        self.bottle_caps += amount
        print(f"[DAILY QUEST] Earned {amount} Bottle Caps! Total: {self.bottle_caps}")

    def get_save_data(self):
        quest_data = []
        for quest in self.quests:
            quest_data.append({
                "completed": quest.completed,
                "claimed": quest.claimed,
                "progress": quest.progress.copy()
            })
        return {
            "quests": quest_data,
            "bottle_caps": self.bottle_caps,
            "last_reset_date": self.last_reset_date
        }

    def restore_save_data(self, data):
        if not data:
            return
        quests_data = data.get("quests", [])
        for i, quest_data in enumerate(quests_data):
            if i < len(self.quests):
                self.quests[i].completed = quest_data.get("completed", False)
                self.quests[i].claimed = quest_data.get("claimed", False)
                progress = quest_data.get("progress", [])
                for j, p in enumerate(progress):
                    if j < len(self.quests[i].progress):
                        self.quests[i].progress[j] = p
                self.quests[i].check_completion()
        self.bottle_caps = data.get("bottle_caps", 0)
        self.last_reset_date = data.get("last_reset_date", None)
        self._check_daily_reset()
    
class DailyQuestSystem:
    def __init__(self, x, y, width, height):
        self.rect = pg.Rect(x, y, width, height)
        self.font_small = pg.font.SysFont(None, 12)
        self.font_medium = pg.font.SysFont(None, 15)
        self.font_large = pg.font.SysFont(None, 22)
        self.font_rule = pg.font.SysFont(None, 14)
        self.quest_manager = QuestManager()
        self.selected_quest = None
        self.message = ""
        self.message_timer = 0

    def update(self):
        if self.message_timer > 0:
            self.message_timer -= 1
        else:
            self.message = ""

    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos
            quests = self.quest_manager.quests
            card_height = 115
            card_spacing = 8
            start_y = self.rect.y + 15
            
            for i, quest in enumerate(quests):
                card_rect = pg.Rect(self.rect.x + 15, start_y + i * (card_height + card_spacing), 
                                   self.rect.width - 30, card_height)
                btn_rect = pg.Rect(card_rect.right - 65, card_rect.bottom - 25, 55, 20)
                if btn_rect.collidepoint(mouse_pos):
                    if quest.can_claim():
                        if self.quest_manager.claim_quest(i):
                            self.message = f"Claimed {quest.name}! +200 Bottle Caps"
                            self.message_timer = 180
                        else:
                            self.message = "Quest not ready to claim!"
                            self.message_timer = 120
                    elif quest.claimed:
                        self.message = "Already claimed!"
                        self.message_timer = 120
                    else:
                        self.message = "Complete all requirements first!"
                        self.message_timer = 120
                    return

    def draw(self, screen):
        pg.draw.rect(screen, (45, 45, 55), self.rect)
        pg.draw.rect(screen, (150, 150, 170), self.rect, 2)

        quests = self.quest_manager.quests
        card_height = 115
        card_spacing = 8
        start_y = self.rect.y + 15

        for i, quest in enumerate(quests):
            card_rect = pg.Rect(self.rect.x + 15, start_y + i * (card_height + card_spacing), 
                               self.rect.width - 30, card_height)
            
            if quest.claimed:
                color = (60, 60, 70)
            elif quest.completed:
                color = (65, 85, 65)
            else:
                color = (50, 50, 65)
            
            pg.draw.rect(screen, color, card_rect)
            pg.draw.rect(screen, (200, 200, 220), card_rect, 1)

            name_text = self.font_large.render(quest.name, True, (255, 220, 100))
            screen.blit(name_text, (card_rect.x + 10, card_rect.y + 5))

            y_offset = card_rect.y + 30
            for j, req in enumerate(quest.requirements):
                req_text = quest.get_requirement_text(j)
                text_surface = self.font_medium.render(req_text, True, (200, 200, 220))
                screen.blit(text_surface, (card_rect.x + 15, y_offset))
                
                progress_pct = quest.get_progress_percentage(j)
                bar_rect = pg.Rect(card_rect.x + 190, y_offset + 2, 90, 10)
                pg.draw.rect(screen, (60, 60, 80), bar_rect)
                pg.draw.rect(screen, (100, 100, 120), bar_rect, 1)
                fill_rect = pg.Rect(bar_rect.x, bar_rect.y, int(bar_rect.width * progress_pct / 100), bar_rect.height)
                pg.draw.rect(screen, (220, 220, 240), fill_rect)
                
                y_offset += 20

            btn_rect = pg.Rect(card_rect.right - 65, card_rect.bottom - 25, 55, 20)
            mouse_pos = pg.mouse.get_pos()
            
            if quest.claimed:
                btn_color = (80, 80, 80)
                btn_text = "CLAIMED"
            elif quest.can_claim():
                btn_color = (70, 130, 70) if btn_rect.collidepoint(mouse_pos) else (50, 100, 50)
                btn_text = "REDEEM"
            else:
                btn_color = (80, 80, 80) if btn_rect.collidepoint(mouse_pos) else (70, 70, 70)
                btn_text = "LOCKED"
            
            pg.draw.rect(screen, btn_color, btn_rect)
            pg.draw.rect(screen, (200, 200, 200), btn_rect, 1)
            btn_render = self.font_small.render(btn_text, True, (255, 255, 255))
            btn_rect_center = btn_render.get_rect(center=btn_rect.center)
            screen.blit(btn_render, btn_rect_center)

        # Rules box
        rules_y = self.rect.y + 15 + 4 * (card_height + card_spacing) + 5
        rules_height = 120
        rules_rect = pg.Rect(self.rect.x + 15, rules_y, self.rect.width - 30, rules_height)
        
        pg.draw.rect(screen, (35, 35, 45), rules_rect)
        pg.draw.rect(screen, (100, 100, 120), rules_rect, 2)
        
        rules_title = self.font_medium.render("DAILY QUEST RULES", True, (255, 220, 100))
        screen.blit(rules_title, (rules_rect.x + 10, rules_rect.y + 5))
        
        rules_lines = [
            "- Quests reset every real day at midnight",
            "- Complete ALL requirements to unlock REDEEM",
            "- Only ONE quest can be claimed per day",
            "- Prestige does NOT reset quest progress",
            "- Bottle Caps max 300, excess deducted daily"
        ]
        
        y_offset = rules_rect.y + 32
        for line in rules_lines:
            line_surface = self.font_rule.render(line, True, (180, 180, 200))
            screen.blit(line_surface, (rules_rect.x + 10, y_offset))
            y_offset += 18

        if self.message and self.message_timer > 0:
            msg_surface = self.font_medium.render(self.message, True, (255, 255, 150))
            msg_rect = msg_surface.get_rect(center=(self.rect.centerx, self.rect.bottom - 10))
            screen.blit(msg_surface, msg_rect)

    def get_bottle_caps(self):
        return self.quest_manager.bottle_caps

    def add_bottle_caps(self, amount):
        self.quest_manager.add_bottle_caps(amount)

    def get_save_data(self):
        return self.quest_manager.get_save_data()

    def restore_save_data(self, data):
        self.quest_manager.restore_save_data(data)

    # Progress tracking methods
    def on_defeat_titan(self):
        self.quest_manager.update_progress_by_type("defeat_titan", 1)

    def on_upgrade_base_damage(self):
        self.quest_manager.update_progress_by_type("upgrade_base_damage", 1)

    def on_upgrade_skill(self):
        self.quest_manager.update_progress_by_type("upgrade_skill", 1)

    def on_defeat_with_kitchenware(self):
        self.quest_manager.update_progress_by_type("defeat_with_kitchenware", 1)

    def on_clear_stage_with_kitchenware(self):
        self.quest_manager.update_progress_by_type("clear_stage_with_kitchenware", 1)

    def on_upgrade_kitchenware(self):
        self.quest_manager.update_progress_by_type("upgrade_kitchenware", 1)

    def on_defeat_with_pet(self):
        self.quest_manager.update_progress_by_type("defeat_with_pet", 1)

    def on_clear_stage_with_pet(self):
        self.quest_manager.update_progress_by_type("clear_stage_with_pet", 1)

    def on_upgrade_pet(self):
        self.quest_manager.update_progress_by_type("upgrade_pet", 1)

    def on_gain_scraps(self, amount):
        self.quest_manager.update_progress_by_type("gain_scraps", amount)