import pygame as pg
import time
import random
import traceback

from Click_Damage_Feature import Monster, MonsterManager, DamageText, damage_per_click, calculate_damage
import Button_System
import AFK_System
import Currency_System
import Gear_System

pg.init()
window = pg.display.set_mode((800, 600))
pg.display.set_caption("Attack On Food Titan")

# --- Safe AFK load ---
try:
    afk_earnings, saved_monster_data, saved_money = AFK_System.afk_system.load_and_calculate_afk_rewards()
except Exception as e:
    print("AFK load failed:", e)
    afk_earnings, saved_monster_data, saved_money = 0, None, 0

if saved_money and saved_money > 0:
    Currency_System.pocket_money = saved_money

if afk_earnings and afk_earnings > 0:
    Currency_System.pocket_money += afk_earnings
    try:
        AFK_System.show_afk_rewards(window, afk_earnings)
    except Exception as e:
        print("AFK reward display failed:", e)

monster_manager = MonsterManager()

# Restore saved monster safely
if saved_monster_data:
    try:
        restored = Monster(
            saved_monster_data.get("name", "Bread Monster"),
            saved_monster_data.get("max_hp", 50),
            tuple(saved_monster_data.get("color", (139, 69, 19)))
        )
        restored.hp = saved_monster_data.get("hp", restored.max_hp)
        restored.is_boss = saved_monster_data.get("is_boss", False)
        monster_manager.current_monster = restored
    except Exception as e:
        print("Monster restore failed:", e)

current_monster = monster_manager.current_monster

IsRunning = True
last_auto_save = time.time()
auto_save_interval = 5

damage_texts = []
clock = pg.time.Clock()

# --- Safe save wrapper ---
def safe_save():
    try:
        AFK_System.afk_system.save_game_data(
            Currency_System.pocket_money,
            current_monster.hp,
            current_monster.max_hp,
            current_monster.name,
            current_monster.color
        )
        AFK_System.afk_system.update_save_time()
    except Exception as e:
        print("AFK save failed:", e)
        traceback.print_exc()

while IsRunning:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            safe_save()
            IsRunning = False
            break

        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_g:
                try:
                    Gear_System.gain_gear("Golden Spatula")
                except Exception as e:
                    print("gain_gear failed:", e)
            elif event.key == pg.K_e:
                try:
                    Gear_System.equip_gear("Golden Spatula")
                except Exception as e:
                    print("equip_gear failed:", e)
            elif event.key == pg.K_u:
                try:
                    Gear_System.unequip_gear("weapon")
                except Exception as e:
                    print("unequip_gear failed:", e)

        elif event.type == pg.MOUSEBUTTONDOWN:
            #  Only left-click (button 1), ignore scroll 
            btn = getattr(event, "button", None)
            pos = getattr(event, "pos", None)
            if btn == 1 and pos and current_monster and getattr(current_monster, "rect", None):
                if current_monster.rect.collidepoint(pos):
                    # --- Always calculate damage first ---
                    gear_bonus = getattr(Gear_System, "total_bonus_damage", 0)
                    try:
                        final_damage, is_critical = calculate_damage(damage_per_click, gear_bonus)
                    except Exception:
                        final_damage, is_critical = damage_per_click + gear_bonus, False

                    # Apply damage
                    current_monster.take_damage(final_damage)

                    # Spawn floating damage text
                    popup_x = current_monster.rect.x + random.randint(20, max(20, current_monster.rect.width - 40))
                    popup_y = current_monster.rect.y + random.randint(20, max(20, current_monster.rect.height - 40))
                    damage_texts.append(DamageText(str(final_damage), (popup_x, popup_y), is_critical=is_critical))

                    # --- Currency update + next monster ---
                    if current_monster.is_defeated():
                        try:
                            Currency_System.update_economy(
                              current_monster.max_hp,
                              monster_manager.stage,
                              current_monster.is_boss,
                              force_award=True   # ensures currency updates
                              )
                        except TypeError:
                            try:
                                Currency_System.update_economy(current_monster.max_hp, monster_manager.stage)
                            except Exception as e:
                                print("Economy update failed:", e)
                        except Exception as e:
                            print("Economy update failed:", e)

                        monster_manager.next_monster()
                        current_monster = monster_manager.current_monster

        # Buttons safe handling
        for button in getattr(Button_System, "buttons", []):
            try:
                button.handle_event(event)
            except Exception as e:
                print("Button event failed:", e)

    # --- Auto save ---
    current_time = time.time()
    if current_time - last_auto_save >= auto_save_interval:
        safe_save()
        last_auto_save = current_time

    # Update buttons
    for button in getattr(Button_System, "buttons", []):
        try:
            button.update()
        except Exception as e:
            print("Button update failed:", e)

    # Update damage texts
    for dt in damage_texts[:]:
        try:
            dt.update()
            if not dt.is_alive():
                damage_texts.remove(dt)
        except Exception as e:
            print("DamageText update failed:", e)
            try:
                damage_texts.remove(dt)
            except ValueError:
                pass

    # --- Boss timer logic ---
    time_left = monster_manager.get_boss_time_left()
    if current_monster.is_boss:
        current_monster.time_left = time_left
    else:
        current_monster.time_left = None

    if monster_manager.check_boss_timer():
     print("Boss time expired! Returning to first monster of stage.")
     monster_manager.reset_to_first_monster()
     current_monster = monster_manager.current_monster


    # --- Draw everything ---
    window.fill((227, 227, 227))
    try:
        current_monster.draw(window)
    except Exception as e:
        print("Monster draw failed:", e)

    try:
        monster_manager.draw_counter(window)
        monster_manager.draw_stage_counter(window)
    except Exception as e:
        print("MonsterManager draw failed:", e)

    try:
        Currency_System.draw_ui(window)
    except Exception as e:
        print("Currency UI failed:", e)

    try:
        AFK_System.draw_AFK_ui(window)
    except Exception:
        pass

    for dt in damage_texts:
        try:
            dt.draw(window)
        except Exception as e:
            print("DamageText draw failed:", e)

    for button in getattr(Button_System, "buttons", []):
        try:
            button.draw(window)
        except Exception as e:
            print("Button draw failed:", e)

    # Safe panel_manager draw
    if hasattr(Button_System, "panel_manager"):
        try:
            Button_System.panel_manager.draw(window)
        except Exception as e:
            print("Panel manager draw failed:", e)

    pg.display.update()
    clock.tick(60)




'''
References list

#1. ABILITY TO CLICK TO DEAL DAMAGE (line 16 - line 40)
Source code: Copilot
Link: None

#2. Drawer system (Inside Button_System file, line 38 - line 77)
Source code: Deepseek
Link: None

Example:
# [Name of the code] (From line x to line x)
#Source code: (Creater of the sources - Platform)
#Link: the link to your reference sources

'''