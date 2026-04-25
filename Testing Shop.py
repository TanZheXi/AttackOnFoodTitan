import pygame as pg
import Button_System

pg.init()
window = pg.display.set_mode((800, 600))
pg.display.set_caption("Game Shop Test")
is_Running = True

while is_Running:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            is_Running = False
        Button_System.panel_manager.handle_event(event)
        for button in Button_System.buttons:
            button.handle_event(event)

    for button in Button_System.buttons:
        button.update()

    window.fill((30, 30, 40))
    for button in Button_System.buttons:
        button.draw(window)
    Button_System.panel_manager.draw(window)
    pg.display.update()

pg.quit()