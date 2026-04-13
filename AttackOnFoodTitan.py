import pygame as pg
import sys

'''General'''

pg.init()
window = pg.display.set_mode((800,600)) # Adjust the window size from here by editing (x,y) value
pg.display.set_caption("Attack On Food Titan") # Rename the title of window by editing ("Name")
IsRunning = True
while IsRunning:
    for event in pg.event.get():
        if event.type == pg. QUIT:
            IsRunning = False
            break
    window.fill((227,227,227)) # Adjust the window color from here by editing its RGB code
    pg.display.update()
pg.quit()


''' Tan Zhe Xi '''
## TZX_1. MINIGAME SYSTEM

'''write your code here, which is inside the grey title, use TZX_1 for quick search for the code during interview'''

## TZX_2. GEAR & DATA DESIGN



## TZX_3. ABILITY TO CLICK TO DEAL DAMAGE



## TZX_4. ADJUSTING STATS ACCORDING TO PRESTIGE LEVELS




''' Eng Kai Hin '''
## EKH_1. BUTTON INTERACTION SYSTEM

'''write your code here, which is inside the grey title, use EKH_1 for quick search for the code during interview'''

## EKH_2. AFK SYSTEM



## EKH_3. SHOP SYSTEM



## EKH_4. CLEAR WHEN PRESTIGE SYSTEM




''' Chen Lik Shen '''
## CLS_1. GAIN & LOST OF GEAR & CURRENCY SYSTEM

'''write your code here, which is inside the grey title, use CLS_1 for quick search for the code during interview'''

## CLS_2. GAME UI & SOUND EFFECT



## CLS_3. CRAFTING SYSTEM



## CLS_4. SYSTEM TO ADD NEW GEAR, CHARACTER, AND RECIPES ACCORDING TO EACH PRESTIGE LEVELS




'''
References list

# [Name of the code] (From line x to line x)
#Source code: (Creater of the sources - Platform)
#Link: the link to your reference sources

***Example***
# Game menu and screen (line 1 - line 9)
#Source code: Baober - YouTube
#Link: https://youtu.be/xHPmXArK6Tg?si=6RO2iZDTE0iYFLBu

'''