import pygame as pg

# Variables for CLS_1
pocket_money = 0

# Setup for CLS_2
pg.font.init()
ui_font = pg.font.SysFont(None, 48)

def update_economy(enemy_hp):
    global pocket_money
    if enemy_hp <= 0:
        pocket_money += 50
        return True # Signal that titan died
    return False

def draw_ui(window):
    """Logic for drawing the money on screen"""
    money_text = ui_font.render(f"Pocket Money: ${pocket_money}", True, (34, 139, 34))
    window.blit(money_text, (10, 550))