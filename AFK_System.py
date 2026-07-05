import pygame as pg
import json
import os
import time
import Click_Damage_Feature
import Equipment_System

pg.init()
pg.font.init()  

class AFKSystem:
    def __init__(self, save_file="afk_save.json"):
        self.save_file = save_file
        self.last_save_time = time.time()
        self.afk_income_rate = 1 / 3600
        self.max_afk_earnings = 100
        
    def save_game_data(self, pocket_money, monster_hp, monster_max_hp, monster_name, monster_color, progression_index, stage, inventory_items=None, shop_items_state=None, pet_data=None, upgrade_level=0, guide_data=None, boost_data=None, michelin_stars=0, ability_data=None, player_upgrade_data=None, companion_data=None, boss_timer_active=False, boss_timer_start=0, boss_timer_duration=30):
        # ✅ Save crit values BEFORE anything else
        crit_chance_value = Click_Damage_Feature.get_crit_chance()
        crit_multiplier_value = Click_Damage_Feature.get_crit_multiplier()
        shop_state = []
        if shop_items_state:
            for item in shop_items_state:
                if isinstance(item, dict):
                    shop_state.append({
                        "name": item.get("name", "Unknown"),
                        "sold_out": item.get("sold_out", False)
                    })
                else:
                    shop_state.append({
                        "name": item.name,
                        "sold_out": item.sold_out
                    })

        save_data = {
            "pocket_money": pocket_money,
            "michelin_stars": michelin_stars,
            "last_time": self.last_save_time,
            "monster": {
                "name": monster_name,
                "hp": monster_hp,
                "max_hp": monster_max_hp,
                "color": monster_color,
                "boss_timer_active": boss_timer_active,
                "boss_timer_start": boss_timer_start,
                "boss_timer_duration": boss_timer_duration
            },
            "progression_index": progression_index,
            "stage": stage,
            "inventory": inventory_items if inventory_items else [],
            "shop_items": shop_state,
            "pet_data": pet_data if pet_data else [],
            "upgrade_level": upgrade_level,
            "guide_data": guide_data if guide_data else {},
            "boost_data": boost_data if boost_data else {"visible": False},
            "crit_chance": crit_chance_value,
            "crit_multiplier": crit_multiplier_value,
            "base_damage": getattr(Equipment_System, "base_damage", 1)
        }
        
        if ability_data:
            save_data["ability_data"] = ability_data
        if player_upgrade_data:
            save_data["player_upgrade_data"] = player_upgrade_data
        if companion_data:
            save_data["companion_data"] = companion_data
        
        try:
            with open(self.save_file, 'w') as f:
                json.dump(save_data, f)
            print(f"[SAVE] Game saved. Money: {pocket_money}, Progress: {progression_index}, Stage: {stage}, Items: {len(inventory_items) if inventory_items else 0}, Pets: {len(pet_data) if pet_data else 0}, Upgrade Level: {upgrade_level}, Michelin Stars: {michelin_stars}")
        except Exception as e:
            print(f"Save failed: {e}")
    
    def load_and_calculate_afk_rewards(self):
        if not os.path.exists(self.save_file):
            return 0, None, 0, 1, 1, [], [], [], 0, {}, {"visible": False}, 0, {}, {}, {}
        
        try:
            with open(self.save_file, 'r') as f:
                save_data = json.load(f)
            
            last_time = save_data.get("last_time", time.time())
            saved_money = save_data.get("pocket_money", 0)
            current_time = time.time()
            time_diff = current_time - last_time
            
            raw_earnings = int(time_diff * self.afk_income_rate)
            afk_earnings = min(raw_earnings, self.max_afk_earnings)
            
            monster_data = save_data.get("monster", None)
            progression_index = save_data.get("progression_index", 1)
            stage = save_data.get("stage", 1)
            inventory = save_data.get("inventory", [])
            shop_state = save_data.get("shop_items", [])
            pet_data = save_data.get("pet_data", [])
            upgrade_level = save_data.get("upgrade_level", 0)
            guide_data = save_data.get("guide_data", {})
            boost_data = save_data.get("boost_data", {"visible": False})
            saved_michelin_stars = save_data.get("michelin_stars", 0)
            ability_data = save_data.get("ability_data", {})
            player_upgrade_data = save_data.get("player_upgrade_data", {})
            companion_data = save_data.get("companion_data", [])
            
            

            # Restore crit values from save data
            Click_Damage_Feature.set_crit_chance(save_data.get("crit_chance", 0.05))
            Click_Damage_Feature.set_crit_multiplier(save_data.get("crit_multiplier", 2.0))

            # ✅ Restore base damage
            saved_base_damage = save_data.get("base_damage", 1)
            Equipment_System.base_damage = save_data.get("base_damage", 1)
            print(f"[LOAD] Restored Base Damage: {Equipment_System.base_damage}")
            
            if monster_data and "boss_timer_active" not in monster_data:
                monster_data["boss_timer_active"] = False
                monster_data["boss_timer_start"] = 0
                monster_data["boss_timer_duration"] = 30
            
            return (
                afk_earnings,
                monster_data,
                saved_money,
                progression_index,
                stage,
                inventory,
                shop_state,
                pet_data,
                upgrade_level,
                guide_data,
                boost_data,
                saved_michelin_stars,
                ability_data,
                player_upgrade_data,
                companion_data
            )
            
        except Exception as e: 
            print(f"Loading failed: {e}")
            return 0, None, 0, 1, 1, [], [], [], 0, {}, {"visible": False}, 0, {}, {}, {}
    
    def update_save_time(self):
        self.last_save_time = time.time()

afk_system = AFKSystem()

def show_afk_rewards(window, afk_earnings):
    if afk_earnings > 0:
        overlay = pg.Surface((1300, 750))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        window.blit(overlay, (0, 0))
        
        font_big = pg.font.SysFont(None, 48)
        font_small = pg.font.SysFont(None, 32)
        
        title_text = font_big.render("Welcome Back!", True, (255, 255, 0))
        reward_text = font_small.render(f"You earned ${afk_earnings} while away!", True, (0, 255, 0))

        if afk_earnings >= 100:
            limit_text = font_small.render("You've reached the $100 AFK limit", True, (255, 255, 0))
            limit_rect = limit_text.get_rect(center=(650, 320))
            window.blit(limit_text, limit_rect)

        continue_text = font_small.render("Click anywhere to continue", True, (255, 255, 255))
        continue_rect = continue_text.get_rect(center=(650, 360))
        
        title_rect = title_text.get_rect(center=(650, 200))
        reward_rect = reward_text.get_rect(center=(650, 280))
        
        window.blit(title_text, title_rect)
        window.blit(reward_text, reward_rect)
        window.blit(continue_text, continue_rect)
        
        pg.display.update()
        
        waiting = True
        while waiting:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    exit()
                elif event.type == pg.MOUSEBUTTONDOWN:
                    waiting = False