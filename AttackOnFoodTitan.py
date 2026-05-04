import pygame as pg
import time
import random
import Click_Damage_Feature
from Click_Damage_Feature import Monster, MonsterManager, DamageText, damage_per_click, calculate_damage
import Button_System
import AFK_System
import Currency_System
import Gear_System



'''General'''
# ========== UI LAYOUT (1300x750 Three Column Layout) ==========
WINDOW_WIDTH = 1300
WINDOW_HEIGHT = 750

LEFT_WIDTH = 300        # Nothing much happens here, will add on in future
MIDDLE_WIDTH = 550      # Monster UI section
RIGHT_WIDTH = WINDOW_WIDTH - LEFT_WIDTH - MIDDLE_WIDTH  # 450px, PLayer interaction section (Shop, Inventory, etc.)

# Origin points for each section (for easier UI element placement)
LEFT_AREA_X = 0
MIDDLE_AREA_X = LEFT_WIDTH
RIGHT_AREA_X = LEFT_WIDTH + MIDDLE_WIDTH

# Origin x for centering elements in the middle area
MIDDLE_CENTER_X = MIDDLE_AREA_X + MIDDLE_WIDTH // 2

# Transfer MIDDLE_CENTER_X to Currency_System for drawing money UI
Currency_System.MIDDLE_CENTER_X = MIDDLE_CENTER_X
# =================================================================

pg.init()
window = pg.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT)) 
pg.display.set_caption("Attack On Food Titan") 

# Load AFK rewards and saved game data
afk_earnings, saved_monster_data, saved_money, saved_progression_index, saved_stage, saved_inventory, saved_shop_state, saved_pet_data = AFK_System.afk_system.load_and_calculate_afk_rewards()

# Load saved gear data
Gear_System.load_gear()

# Reload saved money, then sum up with AFK rewards
if saved_money > 0:
    Currency_System.pocket_money = saved_money

if afk_earnings > 0:
    Currency_System.pocket_money += afk_earnings
    AFK_System.show_afk_rewards(window, afk_earnings)

# Initialize Monster Manager
monster_manager = Click_Damage_Feature.MonsterManager()

# Monster size
MONSTER_SIZE = 200

# if status of monster was saved, then load it
if saved_monster_data:
    # Restore waves of monster
    monster_manager.progression_index = saved_progression_index
    monster_manager.stage = saved_stage
    
    # Save monster's data
    current_monster = Click_Damage_Feature.Monster(
        saved_monster_data["name"],
        saved_monster_data["max_hp"],
        tuple(saved_monster_data["color"])
    )
    current_monster.hp = saved_monster_data["hp"]
    # Adjust monster position to the middle area center
    current_monster.rect.x = MIDDLE_CENTER_X - MONSTER_SIZE // 2
    current_monster.rect.y = 275
    monster_manager.current_monster = current_monster
    
    print(f"[LOAD] Restored progress: {saved_progression_index}/10, Stage: {saved_stage}, Monster HP: {current_monster.hp}/{current_monster.max_hp}")
else:
    current_monster = monster_manager.current_monster
    # Adjust monster position to the middle area center
    current_monster.rect.x = MIDDLE_CENTER_X - MONSTER_SIZE // 2
    current_monster.rect.y = 275

IsRunning = True
last_auto_save = time.time()
auto_save_interval = 5

# ========== PET ATTACK INTERVAL TIMER ==========
PET_ATTACK_INTERVAL = 1.0  # Attck every 1 second
last_pet_attack_time = time.time()
# ====================================

# Set data that will be restore
Button_System.panel_manager.pending_inventory = saved_inventory if saved_inventory else []
Button_System.panel_manager.pending_shop_state = saved_shop_state if saved_shop_state else []
Button_System.panel_manager.pending_pet_data = saved_pet_data if saved_pet_data else []
Button_System.panel_manager.pending_money = Currency_System.pocket_money

data_restored = False   # Shows data restore state

damage_texts = []

while IsRunning:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            inventory_state, shop_state, pet_data = Button_System.panel_manager.get_save_data()
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
                pet_data=pet_data
            )
            IsRunning = False
            break
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_g:
                Gear_System.gain_gear("OP WEAPON") 
            # Press 'E' to wear the item 
            elif event.key == pg.K_e:
                Gear_System.equip_gear("OP WEAPON")
            # Press 'U' to unequip weapon
            elif event.key == pg.K_u:
                Gear_System.unequip_gear("weapon")
            # Press 'C' to craft the item (Consumes scraps) - Placeholder for crafting system
            elif event.key == pg.K_c:
                Gear_System.craft_item("Golden Spatula")

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

        elif event.type == pg.MOUSEBUTTONDOWN:
            if current_monster.rect.collidepoint(event.pos):
                
                # --- MERGED DAMAGE CALCULATION ---
                # 1. Base damage
                base_damage = Click_Damage_Feature.damage_per_click 
                
                # 2. Gear Multiplier
                gear_multi = Gear_System.total_damage_multiplier
                
                # 3. PRESTIGE MULTIPLIER (NEW!)
                prestige_multi = Currency_System.get_prestige_multiplier()
                
                # 4. Main branch's critical hit logic   
                calculated_base, is_critical = calculate_damage(base_damage, 0)
                
                # 5. Final God-Tier Math
                final_damage = int(calculated_base * gear_multi * prestige_multi)
                
                # Apply damage
                current_monster.take_damage(final_damage)

                # Spawn floating damage text
                popup_x = current_monster.rect.x + random.randint(20, current_monster.rect.width - 40)
                popup_y = current_monster.rect.y + random.randint(20, current_monster.rect.height - 40)
                damage_texts.append(DamageText(str(final_damage), (popup_x, popup_y), is_critical=is_critical))

                
                if current_monster.is_defeated():
                    # Trigger your economy system
                    Currency_System.update_economy(current_monster.hp, monster_manager.progression_index)
                    
                    # Spawn next monster
                    monster_manager.next_monster()
                    current_monster = monster_manager.current_monster
                    # Prevent monster from spawning at random position by setting it to the middle area center
                    current_monster.rect.x = MIDDLE_CENTER_X - MONSTER_SIZE // 2
                    current_monster.rect.y = 275

        Button_System.panel_manager.handle_event(event)
        for button in Button_System.buttons:
            button.handle_event(event)

    # ========== PET AUTO ATTACK ==========
    current_time = time.time()
    if current_time - last_pet_attack_time >= PET_ATTACK_INTERVAL:
        pet_system = Button_System.panel_manager.pet_system
        if pet_system:
            # 1. Get base pet damage
            base_pet_damage = pet_system.get_total_damage()
            
            if base_pet_damage > 0 and current_monster.hp > 0:
                # 2. Apply the Prestige Multiplier
                prestige_multi = Currency_System.get_prestige_multiplier()
                total_pet_damage = int(base_pet_damage * prestige_multi)

                # Pet damage application
                current_monster.take_damage(total_pet_damage)
                
                # Pop damge text for pet attack
                popup_x = current_monster.rect.x + random.randint(20, current_monster.rect.width - 40)
                popup_y = current_monster.rect.y + random.randint(20, current_monster.rect.height - 40)
                damage_texts.append(DamageText(str(total_pet_damage), (popup_x, popup_y), is_critical=False))
                
                # Check if monster is defeated after pet attack
                if current_monster.is_defeated():
                    Currency_System.update_economy(current_monster.hp, monster_manager.progression_index)
                    monster_manager.next_monster()
                    current_monster = monster_manager.current_monster
                    current_monster.rect.x = MIDDLE_CENTER_X - MONSTER_SIZE // 2
                    current_monster.rect.y = 275
        last_pet_attack_time = current_time
    # =================================

    # Load Inventory or Shop data when activated
    if not data_restored and (Button_System.panel_manager.active_panel == "Shop" or Button_System.panel_manager.active_panel == "Inventory" or Button_System.panel_manager.active_panel == "Pet"):
        Button_System.panel_manager.load_saved_data(
            Currency_System.pocket_money,
            saved_inventory,
            saved_shop_state,
            saved_pet_data
        )
        data_restored = True

    # Sync currency
    Button_System.panel_manager.global_pocket_money = Currency_System.pocket_money

    # --- NEW: Sync Stage & Check for Prestige ---
    Button_System.panel_manager.current_stage = monster_manager.stage
    
    if getattr(Button_System.panel_manager, 'wants_to_prestige', False):
        success = Currency_System.trigger_prestige(monster_manager)
        if success:
            Button_System.panel_manager.active_panel = None # Auto-close the panel
        Button_System.panel_manager.wants_to_prestige = False # Reset the flag

    # Auto save system for AFK
    current_time = time.time()
    if current_time - last_auto_save >= auto_save_interval:
        inventory_state, shop_state, pet_data = Button_System.panel_manager.get_save_data()
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
            pet_data=pet_data
        )
        AFK_System.afk_system.update_save_time()

        # Gear system auto save
        Gear_System.save_gear()

        last_auto_save = current_time

    for button in Button_System.buttons:
        button.update()

    # Update damage texts
    for dt in damage_texts[:]:
        dt.update()
        if not dt.is_alive():
            damage_texts.remove(dt)

    # Draw everything
    window.fill((227,227,227))
    
    # ========== Draw partition lines ==========
    pg.draw.line(window, (0, 0, 0), (MIDDLE_AREA_X, 0), (MIDDLE_AREA_X, WINDOW_HEIGHT), 3)
    pg.draw.line(window, (0, 0, 0), (RIGHT_AREA_X, 0), (RIGHT_AREA_X, WINDOW_HEIGHT), 3)
    # =====================================
    
    # ========== Draw top UI (swap positions: Monster counter on top, Stage on bottom) ==========
    font_counter = pg.font.SysFont(None, 36)
    counter_value = (monster_manager.progression_index % 10) + 1
    counter_surface = font_counter.render(f"Monster {counter_value}/10", True, (0, 0, 0))
    counter_rect = counter_surface.get_rect(center=(MIDDLE_CENTER_X, 120))
    window.blit(counter_surface, counter_rect)
    
    font_stage = pg.font.SysFont(None, 48, bold=True)
    stage_surface = font_stage.render(f"Stage {monster_manager.stage}", True, (0, 0, 0))
    stage_rect = stage_surface.get_rect(center=(MIDDLE_CENTER_X, 70))
    window.blit(stage_surface, stage_rect)
    # =====================================================
    
    current_monster.draw(window)

    # ========== Draw equipped pets as squares ==========
    pet_system = Button_System.panel_manager.pet_system
    if pet_system:
        equipped_pets = pet_system.get_equipped_pets()
        pet_size = 60  # Pet's square size
        pet_spacing = 10
        start_x = MIDDLE_CENTER_X - (len(equipped_pets) * pet_size + (len(equipped_pets) - 1) * pet_spacing) // 2
        pet_y = current_monster.rect.y + current_monster.rect.height + 20  # Place pet's square below Monster's square
        
        font_pet = pg.font.SysFont(None, 14)
        
        for idx, pet in enumerate(equipped_pets):
            pet_x = start_x + idx * (pet_size + pet_spacing)
            pet_rect = pg.Rect(pet_x, pet_y, pet_size, pet_size)
            
            # Draw pet square with its rareity color and a border
            pg.draw.rect(window, pet.color, pet_rect)
            pg.draw.rect(window, (200, 200, 200), pet_rect, 2)
            
            # Draw pet's name (black text)
            name_text = font_pet.render(pet.name, True, (0, 0, 0))
            name_rect = name_text.get_rect(center=(pet_rect.centerx, pet_rect.centery))
            window.blit(name_text, name_rect)   
    # ============================================

    Currency_System.draw_ui(window)

    # Draw damage texts
    for dt in damage_texts:
        dt.draw(window)

    for button in Button_System.buttons:
        button.draw(window)

    Button_System.panel_manager.draw(window)
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