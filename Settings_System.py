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
        
        # Display variables
        self.is_fullscreen = False
        self.update_external_sfx = None
        
        # State Caching (Stops Pygame from distorting/amplifying the audio)
        self._last_bgm = -1.0
        self._last_sfx = -1.0

        from Button_System import Main_button 

        # 2. Master Volume Buttons
        self.master_down_btn = Main_button(self.rect.x + 200, self.rect.y + 60, 30, 30, "-", (60,60,80), (100,100,120), callback=self.dec_master)
        self.master_up_btn = Main_button(self.rect.x + 300, self.rect.y + 60, 30, 30, "+", (60,60,80), (100,100,120), callback=self.inc_master)

        # 3. BGM Volume Buttons
        self.bgm_down_btn = Main_button(self.rect.x + 200, self.rect.y + 120, 30, 30, "-", (60,60,80), (100,100,120), callback=self.dec_bgm)
        self.bgm_up_btn = Main_button(self.rect.x + 300, self.rect.y + 120, 30, 30, "+", (60,60,80), (100,100,120), callback=self.inc_bgm)

        # 4. SFX Volume Buttons
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
        """Calculates final volume and ONLY pushes to Pygame if the volume changed."""
        final_bgm = self.master_volume * self.bgm_volume
        final_sfx = self.master_volume * self.sfx_volume
        
        # If the volume hasn't changed, ignore the request to prevent audio spikes
        if final_bgm == self._last_bgm and final_sfx == self._last_sfx:
            return
            
        self._last_bgm = final_bgm
        self._last_sfx = final_sfx
        
        # Apply to music
        pg.mixer.music.set_volume(final_bgm)
        
        # Apply to Global Click (reduced dampener to 0.1 for a quieter baseline)
        import Audio_System
        if Audio_System.GLOBAL_CLICK:
            Audio_System.GLOBAL_CLICK.set_volume(final_sfx * 0.1)
            
        # Apply to external sounds
        if self.update_external_sfx:
            self.update_external_sfx(final_sfx)

    def update_sfx_volume(self):
        """Safe routing that takes advantage of the caching mechanism."""
        self.apply_volumes()

    def toggle_display(self):
        if self.is_fullscreen:
            pg.display.set_mode((1300, 750), pg.FULLSCREEN)
        else:
            pg.display.set_mode((1300, 750))

    def handle_event(self, event, global_click=None):
        if self.master_down_btn.handle_event(event): return True
        if self.master_up_btn.handle_event(event): return True
        if self.bgm_down_btn.handle_event(event): return True
        if self.bgm_up_btn.handle_event(event): return True
        if self.sfx_down_btn.handle_event(event): return True
        if self.sfx_up_btn.handle_event(event): return True
        return False

    def draw(self, screen):
        screen.blit(self.font.render("Master Vol:", True, (255, 255, 255)), (self.rect.x + 20, self.rect.y + 65))
        screen.blit(self.font.render("Music Vol:", True, (255, 255, 255)), (self.rect.x + 20, self.rect.y + 125))
        screen.blit(self.font.render("SFX Vol:", True, (255, 255, 255)), (self.rect.x + 20, self.rect.y + 185))

        for btn in [self.master_down_btn, self.master_up_btn, self.bgm_down_btn, self.bgm_up_btn, self.sfx_down_btn, self.sfx_up_btn]:
            btn.update()
            btn.draw(screen)

        screen.blit(self.small_font.render(f"{int(self.master_volume * 100)}%", True, (200, 200, 200)), (self.rect.x + 245, self.rect.y + 68))
        screen.blit(self.small_font.render(f"{int(self.bgm_volume * 100)}%", True, (200, 200, 200)), (self.rect.x + 245, self.rect.y + 128))
        screen.blit(self.small_font.render(f"{int(self.sfx_volume * 100)}%", True, (200, 200, 200)), (self.rect.x + 245, self.rect.y + 188))