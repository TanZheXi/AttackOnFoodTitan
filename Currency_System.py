import pygame as pg
import random

# Variables for CLS_1
pocket_money = 0
current_stage = 1

# Setup for CLS_2
pg.font.init()
ui_font = pg.font.SysFont(None, 36)

def update_economy(enemy_hp, current_stage=1, is_boss=False, force_award=False):
    """
    Award pocket money when enemy_hp <= 0 OR when force_award=True.
    - enemy_hp: current hp (<=0) OR max_hp (if force_award=True)
    - current_stage: 1-based stage number
    - is_boss: True for boss rewards
    - force_award: explicitly award currency regardless of enemy_hp
    Returns True if money was awarded.
    """
    global pocket_money

    if force_award or enemy_hp <= 0:
        # Base drop for stage 1
        min_pocket_drop = 50
        max_pocket_drop = 100

        # Drop multiplier based on the stage
        multiplier = 1.30

        # Formula for pocket_money multiplier
        scaled_min_drop = int(min_pocket_drop * (multiplier ** (current_stage - 1)))
        scaled_max_drop = int(max_pocket_drop * (multiplier ** (current_stage - 1)))

        # Boss Drop Multiplier
        if is_boss:
            boss_multiplier = 5
            scaled_min_drop *= boss_multiplier
            scaled_max_drop *= boss_multiplier

        # RNG for the pocket drop
        dropped_pocket_money = random.randint(scaled_min_drop, scaled_max_drop)
        pocket_money += dropped_pocket_money

        # Debug print
        enemy_type = "BOSS" if is_boss else "Titan"
        print(f"Stage {current_stage} {enemy_type} defeated! Dropped: ${dropped_pocket_money} | Total: ${pocket_money}")

        return True
    return False


def draw_ui(window):
    """Logic for drawing the money on screen"""
    money_text = ui_font.render(f"Pocket Money: ${pocket_money}", True, (34, 139, 34))
    window.blit(money_text, (280, 100))