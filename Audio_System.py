import os
import pygame as pg

# Ensure the mixer is initialized before loading sounds.
try:
    pg.mixer.init()
except Exception:
    pass

try:
    click_path = os.path.join(os.path.dirname(__file__), "Sound_Effects", "Click_sfx.wav")
    GLOBAL_CLICK = pg.mixer.Sound(click_path)
    GLOBAL_CLICK.set_volume(0.05)
except Exception as e:
    GLOBAL_CLICK = None
    print(f"[AUDIO] Warning: Could not load shared click sound: {e}")
