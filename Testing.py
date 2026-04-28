import pygame as pg

pg.init()
window = pg.display.set_mode((800, 600))
pg.display.set_caption("Test")
is_Running = True

while is_Running:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            is_Running = False
    window.fill((227,227,227))
    pg.display.update()

pg.quit()