import pygame as pg
import time
import random

import Click_Damage_Feature
from Click_Damage_Feature import calculate_damage, DamageText
import Button_System
import AFK_System
import Currency_System
import Gear_System
from Abilities import SpicySurge, CrispyPrecision   # NEW: import abilities system

# ========== UI LAYOUT ==========
WINDOW_WIDTH = 1300
WINDOW_HEIGHT = 750
LEFT_WIDTH = 300
MIDDLE_WIDTH = 550
RIGHT_WIDTH = WINDOW_WIDTH - LEFT_WIDTH - MIDDLE_WIDTH
LEFT_AREA_X = 0
MIDDLE_AREA_X = LEFT_WIDTH
RIGHT_AREA_X = LEFT_WIDTH + MIDDLE_WIDTH
MIDDLE_CENTER_X = MIDDLE_AREA_X + MIDDLE_WIDTH // 2
Currency_System.MIDDLE_CENTER_X = MIDDLE_CENTER_X
# =================================================================

pg.init()
pg.mixer.init()
window = pg.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pg.display.set_caption("Attack On Food Titan")

# Setup clock
clock = pg.time.Clock()

# Load AFK rewards and saved game data
afk_earnings, saved_monster_data, saved_money, saved_progression_index, saved_stage, saved_inventory, saved_shop_state, saved_pet_data, saved_upgrade_level = AFK_System.afk_system.load_and_calculate_afk_rewards()
Gear_System.load_gear()

if saved_money > 0:
    Currency_System.pocket_money = saved_money
if afk_earnings > 0:
    Currency_System.pocket_money += afk_earnings
    AFK_System.show_afk_rewards(window, afk_earnings)

monster_manager = Click_Damage_Feature.MonsterManager()
MONSTER_SIZE = 200

if saved_monster_data:
    monster_manager.progression_index = saved_progression_index
    monster_manager.stage = saved_stage
    current_monster = Click_Damage_Feature.Monster(
        saved_monster_data["name"],
        saved_monster_data["max_hp"],
        tuple(saved_monster_data["color"])
    )
    current_monster.hp = saved_monster_data["hp"]
    current_monster.rect.x = MIDDLE_CENTER_X - MONSTER_SIZE // 2
    current_monster.rect.y = 275
    monster_manager.current_monster = current_monster
else:
    current_monster = monster_manager.current_monster
    current_monster.rect.x = MIDDLE_CENTER_X - MONSTER_SIZE // 2
    current_monster.rect.y = 275

IsRunning = True
last_auto_save = time.time()
auto_save_interval = 5

PET_ATTACK_INTERVAL = 1.0
last_pet_attack_time = time.time()

Button_System.panel_manager.pending_inventory = saved_inventory if saved_inventory else []
Button_System.panel_manager.pending_shop_state = saved_shop_state if saved_shop_state else []
Button_System.panel_manager.pending_pet_data = saved_pet_data if saved_pet_data else []
Button_System.panel_manager.pending_money = Currency_System.pocket_money

data_restored = False
damage_texts = []

# Initialize abilities (positioned below monster, beside left partition line)
damage_boost = SpicySurge(
    x=LEFT_WIDTH + 5 + 35,
    y=current_monster.rect.y + current_monster.rect.height + 90,
    radius=35
)
crispy_precision = CrispyPrecision(
    x=damage_boost.x + 100,
    y=damage_boost.y,
    radius=35
)

def on_prestige_reset():
    if Button_System.panel_manager.shop_system:
        Button_System.panel_manager.shop_system.reset_shop()
    if Button_System.panel_manager.inventory_system:
        Button_System.panel_manager.inventory_system.reset_inventory()
    if Button_System.panel_manager.pet_system:
        Button_System.panel_manager.pet_system.reset_on_prestige()
    Gear_System.lose_all_gear()
    damage_texts.clear()

Currency_System.register_prestige_callback(on_prestige_reset)

# =========================
# Main Game Loop
# =========================
while IsRunning:
    dt_ms = clock.tick(60)   # frame delta in ms

    # -------------------------
    # Event Handling
    # -------------------------
    for event in pg.event.get():
        if event.type == pg.QUIT:
            inventory_state, shop_state, pet_data = Button_System.panel_manager.get_save_data()
            upgrade_level = 0
            if Button_System.panel_manager.player_upgrade_system:
                upgrade_level = Button_System.panel_manager.player_upgrade_system.level
            AFK_System.afk_system.save_game_data(
                pocket_money=Currency_System.pocket_money,
                monster_hp=current_monster.hp,
                monster_max_hp=current_monster.max_hp,
                monster_name=current_monster.name,
                monster_color=current_monster.color,
                progression_index=monster_manager.progression_index,
                stage=monster_manager.stage,
                inventory_items=inventory_state,
                shop_items_state=shop_state,
                pet_data=pet_data,
                upgrade_level=upgrade_level
            )
            IsRunning = False
            break

        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_g:
                # Sync between Gear_System and Inventory_System when gaining new gear
                Gear_System.gain_gear("OP WEAPON")
                Button_System.panel_manager.add_to_inventory("OP WEAPON")
                print("[DEBUG] Gained OP WEAPON and added to inventory")
            # Press 'E' to wear the item (only if it's in inventory and valid gear)
            elif event.key == pg.K_e:
                # Get the currently selected item from Inventory_System which can be done by hover on the item and press 'E'
                selected_item = Button_System.panel_manager.get_selected_inventory_item()
                if selected_item and selected_item in Gear_System.gear_database:
                    Gear_System.equip_gear(selected_item)
                    print(f"[DEBUG] Equipped {selected_item}")
                else:
                    print("[DEBUG] No valid item selected to equip")
            # Press 'U' to unequip weapon
            elif event.key == pg.K_u:
                Gear_System.unequip_gear("weapon")
            # Press 'C' to craft the item (Consumes scraps)
            elif event.key == pg.K_c:
                if Gear_System.craft_item("Golden Spatula"):
                    Button_System.panel_manager.add_to_inventory("Golden Spatula")
                    print("[DEBUG] Crafted Golden Spatula and added to inventory")

            # --- DEV HACKS FOR TESTING ---
            # Press 'N' to instantly skip to the next stage
            elif event.key == pg.K_n:
                monster_manager.stage += 1
                monster_manager.progression_index = (monster_manager.stage - 1) * 10
                monster_manager.current_monster = monster_manager.spawn_monster()
                print(f"[DEV CHEAT] Skipped to Stage {monster_manager.stage}")
                
            # Press 'P' to instantly trigger a Prestige
            elif event.key == pg.K_p:
                success = Currency_System.trigger_prestige(monster_manager)
                if not success:
                    print("[DEV WARNING] Prestige failed. Are you at least Stage 10?")

        # --- Click event handling ---
        elif event.type == pg.MOUSEBUTTONDOWN:
              if event.button == 1 and current_monster.rect.collidepoint(event.pos):
              # Get crit bonuses
               extra_chance, extra_multi = crispy_precision.get_crit_bonus()

               # Calculate damage (gear + upgrades + crit)
               final_damage, is_critical = calculate_damage(
               extra_chance=extra_chance,
               extra_multi=extra_multi
               )

               # Apply ability multipliers last
               final_damage *= damage_boost.get_multiplier()
               final_damage *= Currency_System.get_prestige_multiplier()

               #  Apply damage to monster
               current_monster.take_damage(final_damage)

               # Floating text popup
               popup_x = current_monster.rect.x + random.randint(20, current_monster.rect.width - 40)
               popup_y = current_monster.rect.y + random.randint(20, current_monster.rect.height - 40)
               damage_texts.append(DamageText(final_damage, (popup_x, popup_y), is_critical=is_critical))

               # Monster defeat check
               if current_monster.is_defeated():
                Currency_System.update_economy(current_monster.hp, monster_manager.progression_index + 1)
                monster_manager.next_monster()
                current_monster = monster_manager.current_monster
                current_monster.rect.x = MIDDLE_CENTER_X - MONSTER_SIZE // 2
                current_monster.rect.y = 275

        # Ability events
        damage_boost.handle_event(event)
        crispy_precision.handle_event(event)

        # UI Event
        Button_System.panel_manager.monster_manager = monster_manager
        Button_System.panel_manager.handle_event(event)
        for button in Button_System.buttons:
            button.handle_event(event)

    # -------------------------
    # Updates
    # -------------------------
    damage_boost.update()
    crispy_precision.update()

    # Pet auto attack
    current_time = time.time()
    if current_time - last_pet_attack_time >= PET_ATTACK_INTERVAL:
       pet_system = Button_System.panel_manager.pet_system
       if pet_system:
          base_pet_damage = pet_system.get_total_damage()
          if base_pet_damage > 0 and current_monster.hp > 0:
            extra_chance, extra_multi = crispy_precision.get_crit_bonus()

            # ✅ Calculate pet damage (gear + upgrades + crit)
            final_pet_damage, is_critical = calculate_damage(
            extra_chance=extra_chance,
            extra_multi=extra_multi
            ) 

            # ✅ Apply prestige + ability multipliers last
            final_pet_damage *= Currency_System.get_prestige_multiplier()
            final_pet_damage *= damage_boost.get_multiplier()

            # Apply prestige + Spicy Surge last
            final_pet_damage *= Currency_System.get_prestige_multiplier()
            final_pet_damage *= damage_boost.get_multiplier()

            current_monster.take_damage(final_pet_damage)

            damage_texts.append(DamageText(final_pet_damage, (popup_x, popup_y), is_critical=is_critical))

            if current_monster.is_defeated():
                Currency_System.update_economy(current_monster.hp, monster_manager.progression_index)
                monster_manager.next_monster()
                current_monster = monster_manager.current_monster
                current_monster.rect.x = MIDDLE_CENTER_X - MONSTER_SIZE // 2
                current_monster.rect.y = 275

       last_pet_attack_time = current_time


    # Update damage texts safely using dt_ms
    new_damage_texts = []
    for dt_obj in damage_texts:
        expired = dt_obj.update(dt_ms)
        if not expired:
            new_damage_texts.append(dt_obj)
    damage_texts = new_damage_texts
    
    # -------------------------
    # Drawing
    # -------------------------
    window.fill((227,227,227))
    pg.draw.line(window, (0, 0, 0), (MIDDLE_AREA_X, 0), (MIDDLE_AREA_X, WINDOW_HEIGHT), 3)
    pg.draw.line(window, (0, 0, 0), (RIGHT_AREA_X, 0), (RIGHT_AREA_X, WINDOW_HEIGHT), 3)

    font_counter = pg.font.SysFont(None, 36)
    counter_value = (monster_manager.progression_index % 10) + 1
    counter_surface = font_counter.render(f"Monster {counter_value}/10", True, (0, 0, 0))
    counter_rect = counter_surface.get_rect(center=(MIDDLE_CENTER_X, 120))
    window.blit(counter_surface, counter_rect)

    font_stage = pg.font.SysFont(None, 48, bold=True)
    stage_surface = font_stage.render(f"Stage {monster_manager.stage}", True, (0, 0, 0))
    stage_rect = stage_surface.get_rect(center=(MIDDLE_CENTER_X, 70))
    window.blit(stage_surface, stage_rect)

    current_monster.draw(window)

    Currency_System.draw_ui(window)

    for dt in damage_texts:
        dt.draw(window)

    for button in Button_System.buttons:
        button.draw(window)

    Button_System.panel_manager.draw(window)

    # Draw damage texts after panels so they appear on top
    for dt in damage_texts:
        dt.draw(window)

    # Abilities last so its visible
    damage_boost.draw(window)
    crispy_precision.draw(window)

    pg.display.update()

    

pg.quit()



#References list

#1. ABILITY TO CLICK TO DEAL DAMAGE (Click_Damage_Feature.py)
#Source code: Copilot
#Link: None

#2. Drawer system (Button_System.py)
#Source code: Deepseek
#Link: None

#3. Shop system's UI system (Shop_System.py)
#Source code: Deepseek
#Link: None

#4. Code for fixing bug (AFK_System.py)
#Source code: Deepseek
#Link: None

#5. Code for decorational circle (Inventory_System.py)
#Source code: Deepseek
#Link: None

#6. UI reedit (Every file before window size=1300x750)
#Source code: Deepseek
#Link: None

#7. Pet system (Pet_System.py)
#Source code: Deepseek
#Link: None

#8. Link between Inventory_System and Gears_System
#Source code: Deepseek
#Link: None

#9. Scrollbar for button (Button_System.py)
#Source code: Deepseek
#Link: None

''' Tan Zhe Xi '''
## TZX_1. MINIGAME SYSTEM
## TZX_2. GEAR & DATA DESIGN
## TZX_3. ABILITY TO CLICK TO DEAL DAMAGE
#(Handled by Click_Damage_Feature.py)
## TZX_4. ADJUSTING STATS ACCORDING TO PRESTIGE LEVELS

''' Eng Kai Hin '''
## EKH_1. BUTTON INTERACTION SYSTEM
# (Handled by Button_System.py, which contains button and drawer system)
## EKH_2. AFK SYSTEM
# (Handled by AFK_System.py, which contains AFK system and data saving system that save player's data)
## EKH_3. SHOP SYSTEM
# (Handled by Shop_System.py and Inventory_System, One for buying item one for storing item)
## EKH_4. CLEAR WHEN PRESTIGE SYSTEM

''' Chen Lik Shen '''
## CLS_1. GAME UI & SOUND EFFECT
# (Handled by Currency_System.py)
## CLS_2. GAIN & LOST OF GEAR & CURRENCY SYSTEM
# (Handled by Currency_System.py)
## CLS_3. CRAFTING SYSTEM
## CLS_4. SYSTEM TO ADD NEW GEAR, CHARACTER, AND RECIPES ACCORDING TO EACH PRESTIGE LEVELS