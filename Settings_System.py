import pygame as pg

class SettingsSystem:
    def __init__(self, x, y, width, height):
        self.rect = pg.Rect(x, y, width, height)
        self.font = pg.font.SysFont(None, 28)
        self.small_font = pg.font.SysFont(None, 22)
        
        # 1. Volume Variables
        self.master_volume = 1.0
        self.bgm_volume = 0.5
        self.sfx_volume = 0.5
        
        # Callback to update sounds located in the main file
        self.update_external_sfx = None

        from Button_System import Main_button # Make sure this is imported!

        # 2. Master Volume Buttons (Y = 60)
        self.master_down_btn = Main_button(self.rect.x + 200, self.rect.y + 60, 30, 30, "-", (60,60,80), (100,100,120), callback=self.dec_master)
        self.master_up_btn = Main_button(self.rect.x + 300, self.rect.y + 60, 30, 30, "+", (60,60,80), (100,100,120), callback=self.inc_master)

        # 3. BGM Volume Buttons (Y = 120)
        self.bgm_down_btn = Main_button(self.rect.x + 200, self.rect.y + 120, 30, 30, "-", (60,60,80), (100,100,120), callback=self.dec_bgm)
        self.bgm_up_btn = Main_button(self.rect.x + 300, self.rect.y + 120, 30, 30, "+", (60,60,80), (100,100,120), callback=self.inc_bgm)

        # 4. SFX Volume Buttons (Y = 180)
        self.sfx_down_btn = Main_button(self.rect.x + 200, self.rect.y + 180, 30, 30, "-", (60,60,80), (100,100,120), callback=self.dec_sfx)
        self.sfx_up_btn = Main_button(self.rect.x + 300, self.rect.y + 180, 30, 30, "+", (60,60,80), (100,100,120), callback=self.inc_sfx)

    # --- Callbacks ---
    def inc_master(self): self.master_volume = min(1.0, self.master_volume + 0.1); self.apply_volumes()
    def dec_master(self): self.master_volume = max(0.0, self.master_volume - 0.1); self.apply_volumes()
    
    def inc_bgm(self): self.bgm_volume = min(1.0, self.bgm_volume + 0.1); self.apply_volumes()
    def dec_bgm(self): self.bgm_volume = max(0.0, self.bgm_volume - 0.1); self.apply_volumes()
    
    def inc_sfx(self): self.sfx_volume = min(1.0, self.sfx_volume + 0.1); self.apply_volumes()
    def dec_sfx(self): self.sfx_volume = max(0.0, self.sfx_volume - 0.1); self.apply_volumes()

    def apply_volumes(self):
        """Calculates final volume based on Master * Individual setting"""
        final_bgm = self.master_volume * self.bgm_volume
        final_sfx = self.master_volume * self.sfx_volume
        
        # Apply to music
        pg.mixer.music.set_volume(final_bgm)
        
        # Apply to Global Click
        import Audio_System
        if Audio_System.GLOBAL_CLICK:
            Audio_System.GLOBAL_CLICK.set_volume(final_sfx)
            
        # Apply to external sounds (like Attack, Titan Defeat, Pet)
        if self.update_external_sfx:
            self.update_external_sfx(final_sfx)

    def handle_event(self, event):
        if self.master_down_btn.handle_event(event): return True
        if self.master_up_btn.handle_event(event): return True
        if self.bgm_down_btn.handle_event(event): return True
        if self.bgm_up_btn.handle_event(event): return True
        if self.sfx_down_btn.handle_event(event): return True
        if self.sfx_up_btn.handle_event(event): return True
        return False

    def draw(self, screen):
        # Draw Labels
        screen.blit(self.font.render("Master Vol:", True, (255, 255, 255)), (self.rect.x + 20, self.rect.y + 65))
        screen.blit(self.font.render("Music Vol:", True, (255, 255, 255)), (self.rect.x + 20, self.rect.y + 125))
        screen.blit(self.font.render("SFX Vol:", True, (255, 255, 255)), (self.rect.x + 20, self.rect.y + 185))

        # Update and Draw Buttons
        for btn in [self.master_down_btn, self.master_up_btn, self.bgm_down_btn, self.bgm_up_btn, self.sfx_down_btn, self.sfx_up_btn]:
            btn.update()
            btn.draw(screen)

        # Draw Values
        screen.blit(self.small_font.render(f"{int(self.master_volume * 100)}%", True, (200, 200, 200)), (self.rect.x + 245, self.rect.y + 68))
        screen.blit(self.small_font.render(f"{int(self.bgm_volume * 100)}%", True, (200, 200, 200)), (self.rect.x + 245, self.rect.y + 128))
        screen.blit(self.small_font.render(f"{int(self.sfx_volume * 100)}%", True, (200, 200, 200)), (self.rect.x + 245, self.rect.y + 188))

    def handle_event(self, event, global_click=None):
        # We pass the event to each Main_button. 
        # The Main_button class automatically checks for collisions, plays the click sound, and triggers the callback!
        if self.master_down_btn.handle_event(event): return True
        if self.master_up_btn.handle_event(event): return True
        
        if self.bgm_down_btn.handle_event(event): return True
        if self.bgm_up_btn.handle_event(event): return True
        
        if self.sfx_down_btn.handle_event(event): return True
        if self.sfx_up_btn.handle_event(event): return True
        
        return False
    
    def update_sfx_volume(self):
    # This is a robust way to update all your sound objects at once
    # Ensure all your sounds are imported or accessible here
        from Audio_System import GLOBAL_CLICK
        if GLOBAL_CLICK: 
            GLOBAL_CLICK.set_volume(self.sfx_volume)
    
    # If you have other sounds, update them here:
    # titan_defeated_sound.set_volume(self.sfx_volume * 0.6)
    # pet_attack_sound.set_volume(self.sfx_volume * 0.5)

    def toggle_display(self):
        # 1300x750 is your current WINDOW_WIDTH x WINDOW_HEIGHT
        if self.is_fullscreen:
            pg.display.set_mode((1300, 750), pg.FULLSCREEN)
        else:
            pg.display.set_mode((1300, 750))

    def draw(self, screen):
        # Draw Labels
        screen.blit(self.font.render("Master Vol:", True, (255, 255, 255)), (self.rect.x + 20, self.rect.y + 65))
        screen.blit(self.font.render("Music Vol:", True, (255, 255, 255)), (self.rect.x + 20, self.rect.y + 125))
        screen.blit(self.font.render("SFX Vol:", True, (255, 255, 255)), (self.rect.x + 20, self.rect.y + 185))

        # Update and Draw Buttons using Main_button's built-in methods
        for btn in [self.master_down_btn, self.master_up_btn, self.bgm_down_btn, self.bgm_up_btn, self.sfx_down_btn, self.sfx_up_btn]:
            btn.update()
            btn.draw(screen)

        # Draw Values
        screen.blit(self.small_font.render(f"{int(self.master_volume * 100)}%", True, (200, 200, 200)), (self.rect.x + 245, self.rect.y + 68))
        screen.blit(self.small_font.render(f"{int(self.bgm_volume * 100)}%", True, (200, 200, 200)), (self.rect.x + 245, self.rect.y + 128))
        screen.blit(self.small_font.render(f"{int(self.sfx_volume * 100)}%", True, (200, 200, 200)), (self.rect.x + 245, self.rect.y + 188))