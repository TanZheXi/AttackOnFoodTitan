import pygame as pg
import random
import Equipment_System
import time
import math
import os
import Player_Upgrade_System

class Monster:
    def __init__(self, name, max_hp, color):
        self.name = name
        self.max_hp = float(max_hp)   
        self.hp = float(max_hp)
        self.color = color
        self.rect = pg.Rect(0, 0, 200, 200)
        
        self.creation_time = time.time()
        self.hurt_time = 0
        
        self.anim_timer = time.time()
        self.anim_speed = 0.15 
        
        self.state = "idle" 
        self.death_time = 0
        self.current_frame = 0

        # --- 1. LOAD NORMAL & DEAD SHEETS ---
        self.idle_frames = self._load_sheet(name, "")
        self.dead_frames = self._load_sheet(name, " Dead") 

        # --- 2. LOAD MULTIPLE HURT VARIATIONS! ---
        self.hurt_variations = []
        
        # This will look for " Hurt 1.png", " Hurt 2.png", and " Hurt 3.png"
        for suffix in [" Hurt 1", " Hurt 2", " Hurt 3"]:
            frames = self._load_sheet(name, suffix)
            if frames:
                self.hurt_variations.append(frames)
                
        self.current_hurt_frames = None # Will hold the randomly picked one

    def _load_sheet(self, name, suffix):
        """Helper function to universally load and slice ANY sprite sheet layout"""
        frames = []
        try:
            # Look for the file in your Monster_Images folder
            img_path = os.path.join(os.path.dirname(__file__), "Monster_Images", f"{name}{suffix}.png")
            
            if os.path.exists(img_path):
                raw_img = pg.image.load(img_path).convert_alpha()
                img_w = raw_img.get_width()
                img_h = raw_img.get_height()
                
                # --- UNIVERSAL SLICER CONFIGURATION ---
                # Tell the game how many columns and rows each monster uses!
                layouts = {
                    "Sushi Serpent": (2, 2),  # 2 columns, 2 rows (Square Grid)
                    "Bread Monster": (2, 2),  # 2 columns, 2 rows (Square Grid)
                    "Ice Cream Overlord": (2, 2), # 2 columns, 2 rows (Horizontal Strip)
                    "Cake Emperor": (2, 2), # 2 columns, 2 rows (Horizontal Strip)
                }
                
                # Check if we have a custom layout for this monster
                if name in layouts:
                    cols, rows = layouts[name]
                else:
                    # If not listed above, automatically assume it is a 1-Row horizontal strip
                    rows = 1
                    cols = max(1, img_w // img_h)

                # Calculate the exact size of a single frame
                frame_w = img_w // cols
                frame_h = img_h // rows
                
                # Slice the image based on our rows and columns
                for row in range(rows):
                    for col in range(cols):
                        # Cut out the current frame
                        frame = raw_img.subsurface((col * frame_w, row * frame_h, frame_w, frame_h))
                        
                        # --- MAGIC TRICK: SKIP EMPTY FRAMES ---
                        # If the frame is completely blank, get_bounding_rect().width will be 0. 
                        # We only add frames that have actual pixel art in them!
                        if frame.get_bounding_rect().width > 0:
                            frames.append(pg.transform.scale(frame, (200, 200)))
                            
        except Exception as e:
            # Silently pass if the file doesn't exist (like Hurt2/Hurt3)
            pass 
            
        return frames

    def take_damage(self, dmg):
        if self.state == "dead":
            return
            
        self.hp = max(self.hp - float(dmg), 0.0)
        self.hurt_time = time.time()
        
        # --- 3. PICK A RANDOM HURT ANIMATION ON EVERY CLICK! ---
        if self.hurt_variations:
            self.current_hurt_frames = random.choice(self.hurt_variations)
        
        if self.is_defeated():
            self.state = "dead"
            self.death_time = time.time()
        else:
            self.state = "hurt"

    def is_defeated(self):
        return self.hp <= 0.0

    def draw(self, surface):
        now = time.time()
        
        # --- CALCULATE DURATIONS ---
        hurt_duration = 0.16  
        hurt_anim_speed = 0.04 
        
        is_hurt_flash = (now - self.hurt_time) < hurt_duration 
        if self.state == "hurt" and not is_hurt_flash:
            self.state = "idle"
            self.current_frame = 0 
            
        # --- CHOOSE ACTIVE ANIMATION LIST ---
        active_frames = self.idle_frames
        if self.state == "dead":
            if self.dead_frames:
                active_frames = self.dead_frames
            elif self.current_hurt_frames:
                active_frames = self.current_hurt_frames 
        elif self.state == "hurt" and self.current_hurt_frames:
            active_frames = self.current_hurt_frames
            
        # --- ANIMATION FRAME LOGIC ---
        if self.state == "dead":
            self.current_frame = 0 # Freeze completely on frame 0, no extra animations
        elif self.state == "hurt" and self.current_hurt_frames:
            time_since_hit = now - self.hurt_time
            self.current_frame = int(time_since_hit / hurt_anim_speed)
            self.current_frame = min(self.current_frame, len(active_frames) - 1)
        else:
            self.current_frame = 0 # Safe global idle fallback

        # --- POSITION TRANSFORMATIONS ---
        # Keep the exact same float running so it doesn't jarringly freeze or drop out of the air
        float_offset = math.sin((now - self.creation_time) * self.hover_speed) * self.hover_height
        draw_y = self.rect.y + float_offset
        
        # --- ALPHA VANISH TRANSPARENCY ---
        if active_frames:
            if self.state == "dead":
                # Create a volatile copy of the frame to modify its transparency channel safely
                current_img = active_frames[self.current_frame].copy()
                elapsed_death = now - self.death_time
                
                # Fades alpha from 255 (fully visible) to 0 (invisible) over 1 second
                alpha_value = max(255 - int(elapsed_death * 255), 0)
                current_img.set_alpha(alpha_value)
            else:
                current_img = active_frames[self.current_frame]
        else:
            current_img = None

        # --- DRAW MONSTER ---
        if current_img:
            img_rect = current_img.get_rect(center=(self.rect.centerx, draw_y + 100))
            surface.blit(current_img, img_rect.topleft)
        else:
            draw_rect = pg.Rect(self.rect.x, draw_y, self.rect.width, self.rect.height)
            display_color = (255, 100, 100) if is_hurt_flash else self.color
            pg.draw.rect(surface, display_color, draw_rect, border_radius=15)

        # --- DRAW HEALTH BARS (Only if alive) ---
        if self.state != "dead":
            bar_y = self.rect.y - 25
            pg.draw.rect(surface, (100, 100, 100), (self.rect.x, bar_y, self.rect.width, 10))
            hp_bar_width = int((self.hp / self.max_hp) * self.rect.width)
            pg.draw.rect(surface, (255, 0, 0), (self.rect.x, bar_y, hp_bar_width, 10))
            
            font = pg.font.SysFont(None, 30)
            text = font.render(f"{self.name} HP: {self.hp:.1f}/{self.max_hp:.1f}", True, (0, 0, 0))
            text_rect = text.get_rect(center=(self.rect.centerx, bar_y - 15))
            surface.blit(text, text_rect)

    def take_damage(self, dmg):
        if self.state == "dead":
            return
            
        self.hp = max(self.hp - float(dmg), 0.0)
        self.hurt_time = time.time()
        
        # --- 3. PICK A RANDOM HURT ANIMATION ON EVERY CLICK! ---
        if self.hurt_variations:
            self.current_hurt_frames = random.choice(self.hurt_variations)
        
        if self.is_defeated():
            self.state = "dead"
            self.death_time = time.time()
        else:
            self.state = "hurt"

    def is_defeated(self):
        return self.hp <= 0.0

    def draw(self, surface):
        now = time.time()
        
        # --- CALCULATE DURATIONS ---
        hurt_duration = 0.16  
        hurt_anim_speed = 0.04 
        
        # Return to idle when hurt animation finishes
        is_hurt_flash = (now - self.hurt_time) < hurt_duration 
        if self.state == "hurt" and not is_hurt_flash:
            self.state = "idle"
            self.current_frame = 0 
            
        # --- CHOOSE ACTIVE ANIMATION LIST ---
        active_frames = self.idle_frames
        
        if self.state == "dead":
            if self.dead_frames:
                active_frames = self.dead_frames
            elif self.current_hurt_frames:
                active_frames = self.current_hurt_frames 
        elif self.state == "hurt" and self.current_hurt_frames:
            active_frames = self.current_hurt_frames
            
        # --- ANIMATION LOGIC ---
        if self.state == "dead":
            if active_frames:
                self.current_frame = 0  # Just freeze on the first frame, no extra animation!
                
        elif self.state == "hurt" and self.current_hurt_frames:
            time_since_hit = now - self.hurt_time
            self.current_frame = int(time_since_hit / hurt_anim_speed)
            self.current_frame = min(self.current_frame, len(active_frames) - 1)
            
        else:
            self.current_frame = 0

        # --- JUICE & TRANSFORMATIONS ---
        # Keep the exact same float running so it doesn't freeze or drop!
        # (Assuming your anim_speed or hover variables are hardcoded here based on your file)
        float_offset = math.sin((now - self.creation_time) * 4) * 4
        draw_y = self.rect.y + float_offset
        
        if active_frames:
            if self.state == "dead":
                # --- PURE VANISH EFFECT ---
                current_img = active_frames[self.current_frame].copy()
                elapsed_death = now - self.death_time
                
                # Fades from 255 (solid) to 0 (invisible) over 1 second
                alpha_value = max(255 - int(elapsed_death * 255), 0)
                current_img.set_alpha(alpha_value)
            else:
                current_img = active_frames[self.current_frame]
        else:
            current_img = None

        # --- DRAW THE ACTUAL MONSTER ---
        if current_img:
            img_rect = current_img.get_rect(center=(self.rect.centerx, draw_y + 100))
            surface.blit(current_img, img_rect.topleft)
        else:
            draw_rect = pg.Rect(self.rect.x, draw_y, self.rect.width, self.rect.height)
            display_color = (255, 100, 100) if is_hurt_flash else self.color
            pg.draw.rect(surface, display_color, draw_rect, border_radius=15)

        # --- DRAW HEALTH BARS ---
        if self.state != "dead":
            bar_y = self.rect.y - 25
            pg.draw.rect(surface, (100, 100, 100), (self.rect.x, bar_y, self.rect.width, 10))
            hp_bar_width = int((self.hp / self.max_hp) * self.rect.width)
            pg.draw.rect(surface, (255, 0, 0), (self.rect.x, bar_y, hp_bar_width, 10))
            
            font = pg.font.SysFont(None, 30)
            text = font.render(f"{self.name} HP: {self.hp:.1f}/{self.max_hp:.1f}", True, (0, 0, 0))
            text_rect = text.get_rect(center=(self.rect.centerx, bar_y - 15))
            surface.blit(text, text_rect)


class MonsterManager:
    def __init__(self):
        self.food_monsters = [
            {"name": "Bread Monster", "color": (139, 69, 19)},
            {"name": "Baguette Monster", "color": (222, 184, 135)},
            {"name": "Croissant Titan", "color": (255, 215, 0)},
            {"name": "Donut King", "color": (255, 105, 180)},
            {"name": "Pizza Beast", "color": (255, 69, 0)},
            {"name": "Burger Giant", "color": (160, 82, 45)},
            {"name": "Sushi Serpent", "color": (70, 130, 180)},
            {"name": "Taco Titan", "color": (255, 255, 0)},
            {"name": "Ice Cream Overlord", "color": (173, 216, 230)},
            {"name": "Cake Emperor", "color": (255, 182, 193)},
        ]
        self.progression_index = 0
        self.stage = 1
        self.current_monster = self.spawn_monster()

    def spawn_monster(self):
        hp_value = 50 + (self.progression_index * 100)
        data = random.choice(self.food_monsters)
        return Monster(data["name"], hp_value, data["color"])

    def next_monster(self):
        self.progression_index += 1
        if self.progression_index % 10 == 0:
            self.stage += 1
        self.current_monster = self.spawn_monster()

    def draw_counter(self, surface):
        font = pg.font.SysFont(None, 36)
        counter_value = (self.progression_index % 10) + 1
        counter_text = font.render(f"Monster {counter_value}/10", True, (0, 0, 0))
        #surface.blit(counter_text, (surface.get_width() - 200, 20))
        return counter_text

    def draw_stage_counter(self, surface):
        font = pg.font.SysFont(None, 48, bold=True)
        stage_text = font.render(f"Stage {self.stage}", True, (0, 0, 0))
        #surface_width = surface.get_width()
        #stage_x = (surface_width - stage_text.get_width()) // 2
        #surface.blit(stage_text, (stage_x, 20))
        return stage_text


class DamageText:
    def __init__(self, damage, pos, is_critical=False, suffix=""):
        self.damage = float(damage)   # store as float
        self.display_text = f"+${self.damage}{suffix}" #Use to display symbol
        self.x, self.y = float(pos[0]), float(pos[1])
        self.vy = -60.0
        self.alpha = 255
        self.lifetime_ms = 800
        self.start_ms = pg.time.get_ticks()
        self.color = (0, 0, 0) if not is_critical else (220, 40, 40)
        self.font = pg.font.SysFont(None, 28 if not is_critical else 36)
        self.is_critical = is_critical

    def update(self, dt_ms):
        # Limit maximum time step to avoid large jumps
        dt_ms = min(dt_ms, 50)
        
        elapsed = pg.time.get_ticks() - self.start_ms
        if elapsed >= self.lifetime_ms:
            return True
        
        # Gravity effect (negative gravity makes it slow down as it rises)
        gravity = -20.0
        self.vy += gravity * (dt_ms / 1000.0)
        self.y += self.vy * (dt_ms / 1000.0)
        
        # Fade out effect
        fade_start = self.lifetime_ms * 0.6
        if elapsed > fade_start:
            fade_ratio = (elapsed - fade_start) / (self.lifetime_ms - fade_start)
            self.alpha = max(0, int(255 * (1 - fade_ratio)))
        
        return False

    def draw(self, surface):
        # Format decimal display
        if self.is_critical:
            text_str = f"{self.damage:.2f}!"
        else:
            text_str = f"{self.damage:.1f}"

        txt_surf = self.font.render(text_str, True, self.color)
        txt_surf.set_alpha(self.alpha)
        rect = txt_surf.get_rect(center=(int(self.x), int(self.y)))
        surface.blit(txt_surf, rect)

    def is_alive(self):
        elapsed = pg.time.get_ticks() - self.start_ms
        return elapsed < self.lifetime_ms


# Damage System 
# Use Equipment_System.base_damage if available, otherwise fallback
damage_per_click = getattr(Equipment_System, "base_damage", 1)

# Base critical values
crit_chance = 0.05        # 5% default crit chance
crit_multiplier = 2.0     # critical hits deal 200% damage

def calculate_damage(base_damage=None, extra_chance=0.0, extra_multi=1.0):
    """
    Calculate final damage with critical hits.
    
    Parameters:
    - base_damage: optional base damage (if None, uses Equipment_System.base_damage)
    - extra_chance: additional critical chance from abilities (CrispyPrecision)
    - extra_multi: additional critical multiplier from abilities (CrispyPrecision)
    
    Returns:
    - final_damage (int): the calculated damage value
    - is_critical (bool): whether the hit was critical
    """
    # Get base damage
    if base_damage is None:
        damage = float(Equipment_System.base_damage)
    else:
        damage = float(base_damage)
    
    # Apply equipment multiplier
    damage *= float(Equipment_System.total_damage_multiplier)
    
    # Apply upgrade bonus from Player Upgrade System
    upgrade_level = getattr(Player_Upgrade_System, "level", 0)
    damage += upgrade_level
    if upgrade_level > 0 and upgrade_level % 50 == 0:
        damage *= 1.2
    
    # Calculate total critical chance and multiplier
    total_crit_chance = crit_chance + float(extra_chance)
    total_crit_multi = crit_multiplier * float(extra_multi)
    
    # Determine if hit is critical
    is_critical = random.random() < total_crit_chance
    if is_critical:
        damage *= total_crit_multi
    
    return int(damage), is_critical