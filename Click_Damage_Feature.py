import pygame as pg
import random
import Equipment_System
import time
import math
import os
import Player_Upgrade_System

def format_number(amount):
    """Formats large numbers with K, M, B, etc. suffixes."""
    if amount < 1000:
        return f"{int(amount)}"

    suffixes = ["", "K", "M", "B", "T", "Qa", "Qi"]
    
    magnitude = 0
    temp_amount = float(amount)
    while temp_amount >= 1000 and magnitude < len(suffixes) - 1:
        magnitude += 1
        temp_amount /= 1000.0
    if temp_amount >= 1000 and magnitude == len(suffixes) - 1:
        return f"{float(amount):.2e}"
    return f"{temp_amount:.2f}{suffixes[magnitude]}"

class Monster:
    def __init__(self, name, max_hp, color):
        self.name = name
        self.max_hp = float(max_hp)   
        self.hp = float(max_hp)
        self.color = color
        self.rect = pg.Rect(0, 0, 200, 200)
        
        self.creation_time = time.time()
        self.hurt_time = 0
        
        # --- MONSTER WEIGHT & SPEED SETTINGS ---
        self.anim_timer = time.time()
        self.anim_speed = 0.4 
        self.hover_speed = 4.0
        self.hover_height = 4.0
        
        # Custom settings for heavy/slow monsters
        if self.name == "Bread Monster":
            self.anim_speed = 0.35      # Slower breathing
            self.hover_speed = 2.0      # Bobs up and down very slowly
            self.hover_height = 1.0     # Barely lifts off the ground
        
        self.state = "idle" 
        self.death_time = 0
        self.current_frame = 0

        # --- 1. LOAD NORMAL & DEAD SHEETS ---
        self.idle_frames = self._load_sheet(name, "")
        self.dead_frames = self._load_sheet(name, " Dead") 

        # --- 2. LOAD MULTIPLE HURT VARIATIONS! ---
        self.hurt_variations = []
        for suffix in [" Hurt 1", " Hurt 2", " Hurt 3"]:
            frames = self._load_sheet(name, suffix)
            if frames:
                self.hurt_variations.append(frames)
                
        self.current_hurt_frames = None

    def _load_sheet(self, name, suffix):
        """Helper function to universally load and slice ANY sprite sheet layout"""
        frames = []
        try:
            img_path = os.path.join(os.path.dirname(__file__), "Monster_Images", f"{name}{suffix}.png")
            
            if os.path.exists(img_path):
                raw_img = pg.image.load(img_path).convert_alpha()
                img_w = raw_img.get_width()
                img_h = raw_img.get_height()
                
                # --- UNIVERSAL SLICER CONFIGURATION ---
                layouts = {
                    "Sushi Serpent": (2, 2),  
                    "Bread Monster": (2, 2),  
                    "Ice Cream Overlord": (2, 2), 
                    "Cake Emperor": (2, 2), 
                    "Cheese Titan": (2, 2),
                    "Wicked Onion": (2, 2),
                    "Garlic Minion": (2, 2),
                    "Titan Aroma": (2, 2),
                    "Flying Pea": (2, 2),
                    "Infested Grape": (2, 2),
                }
                
                if name in layouts:
                    cols, rows = layouts[name]
                else:
                    rows = 1
                    cols = max(1, img_w // img_h)

                frame_w = img_w // cols
                frame_h = img_h // rows
                
                for row in range(rows):
                    for col in range(cols):
                        frame = raw_img.subsurface((col * frame_w, row * frame_h, frame_w, frame_h))
                        if frame.get_bounding_rect().width > 0:
                            frames.append(pg.transform.scale(frame, (200, 200)))
                            
        except Exception as e:
            pass 
            
        return frames

    def take_damage(self, dmg):
        if self.state == "dead":
            return
            
        self.hp = max(self.hp - float(dmg), 0.0)
        self.hurt_time = time.time()
        
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
        
        hurt_duration = 0.16  
        hurt_anim_speed = 0.04 
        
        is_hurt_flash = (now - self.hurt_time) < hurt_duration 
        if self.state == "hurt" and not is_hurt_flash:
            self.state = "idle"
            
        active_frames = self.idle_frames
        if self.state == "dead":
            if self.dead_frames:
                active_frames = self.dead_frames
            elif self.current_hurt_frames:
                active_frames = self.current_hurt_frames 
        elif self.state == "hurt" and self.current_hurt_frames:
            active_frames = self.current_hurt_frames
            
        if self.state == "dead":
            self.current_frame = 0 
        elif self.state == "hurt" and self.current_hurt_frames:
            time_since_hit = now - self.hurt_time
            self.current_frame = int(time_since_hit / hurt_anim_speed)
            self.current_frame = min(self.current_frame, len(active_frames) - 1)
        else:
            if active_frames:
                if now - self.anim_timer > self.anim_speed:
                    self.current_frame = (self.current_frame + 1) % len(active_frames)
                    self.anim_timer = now
            else:
                self.current_frame = 0

        float_offset = math.sin((now - self.creation_time) * self.hover_speed) * self.hover_height
        draw_y = self.rect.y + float_offset
        
        if active_frames:
            safe_frame = min(self.current_frame, len(active_frames) - 1)
            
            if self.state == "dead":
                current_img = active_frames[safe_frame].copy()
                elapsed_death = now - self.death_time
                alpha_value = max(255 - int(elapsed_death * 255), 0)
                current_img.set_alpha(alpha_value)
            else:
                current_img = active_frames[safe_frame]
        else:
            current_img = None

        if current_img:
            img_rect = current_img.get_rect(center=(self.rect.centerx, draw_y + 100))
            surface.blit(current_img, img_rect.topleft)
        else:
            draw_rect = pg.Rect(self.rect.x, draw_y, self.rect.width, self.rect.height)
            display_color = (255, 100, 100) if is_hurt_flash else self.color
            pg.draw.rect(surface, display_color, draw_rect, border_radius=15)

        # --- DRAW HEALTH BARS ---
        if self.state != "dead":
            # 1. DEFINE YOUR LONGER WIDTH HERE
            bar_width = 300  
            bar_x = self.rect.centerx - (bar_width // 2) 
            bar_y = self.rect.y - 35
            bar_height = 28
            
            # Draw the gray background bar
            pg.draw.rect(surface, (60, 60, 60), (bar_x, bar_y, bar_width, bar_height))
            
            # Draw the red health fill
            hp_bar_width = int((self.hp / self.max_hp) * bar_width)
            pg.draw.rect(surface, (200, 30, 30), (bar_x, bar_y, hp_bar_width, bar_height))
            
            # Draw a crisp black border around the whole bar
            pg.draw.rect(surface, (0, 0, 0), (bar_x, bar_y, bar_width, bar_height), 2)
            
            font = pg.font.SysFont(None, 24)
            text_center_y = bar_y + (bar_height // 2)
            
            # --- LEFT SIDE: MONSTER NAME ---
            name_str = self.name
            name_shadow = font.render(name_str, True, (0, 0, 0))
            # midleft anchors the text to the left side with a 10px padding
            name_shadow_rect = name_shadow.get_rect(midleft=(bar_x + 10 + 1, text_center_y + 1))
            surface.blit(name_shadow, name_shadow_rect)
            
            name_text = font.render(name_str, True, (255, 255, 255))
            name_rect = name_text.get_rect(midleft=(bar_x + 10, text_center_y))
            surface.blit(name_text, name_rect)
            
            # --- RIGHT SIDE: HP AMOUNT ---
            hp_str = f"{format_number(self.hp)} HP"
            hp_shadow = font.render(hp_str, True, (0, 0, 0))
            # midright anchors the text to the right side with a 10px padding
            hp_shadow_rect = hp_shadow.get_rect(midright=(bar_x + bar_width - 10 + 1, text_center_y + 1))
            surface.blit(hp_shadow, hp_shadow_rect)
            
            hp_text = font.render(hp_str, True, (255, 255, 255))
            hp_rect = hp_text.get_rect(midright=(bar_x + bar_width - 10, text_center_y))
            surface.blit(hp_text, hp_rect)


class MonsterManager:
    def __init__(self):
        self.food_monsters = [
            {"name": "Sushi Serpent", "color": (139, 69, 19)},
            {"name": "Bread Monster", "color": (222, 184, 135)},
            {"name": "Ice Cream Overlord", "color": (255, 215, 0)},
            {"name": "Cake Emperor", "color": (255, 105, 180)},
            {"name": "Cheese Titan", "color": (255, 69, 0)},
            {"name": "Wicked Onion", "color": (160, 82, 45)},
            {"name": "Garlic Minion", "color": (70, 130, 180)},
            {"name": "Titan Aroma", "color": (255, 255, 0)},
            {"name": "Flying Pea", "color": (173, 216, 230)},
            {"name": "Infested Grape", "color": (255, 182, 193)},
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
        return counter_text

    def draw_stage_counter(self, surface):
        font = pg.font.SysFont(None, 48, bold=True)
        stage_text = font.render(f"Stage {self.stage}", True, (0, 0, 0))
        return stage_text


class DamageText:
    def __init__(self, damage, pos, is_critical=False, suffix=""):
        self.damage = float(damage)   
        self.display_text = f"+${format_number(self.damage)}{suffix}" 
        self.x, self.y = float(pos[0]), float(pos[1])
        self.vy = -60.0
        self.alpha = 255
        self.lifetime_ms = 800
        self.start_ms = pg.time.get_ticks()
        self.color = (0, 0, 0) if not is_critical else (220, 40, 40)
        self.font = pg.font.SysFont(None, 28 if not is_critical else 36)
        self.is_critical = is_critical

    def update(self, dt_ms):
        dt_ms = min(dt_ms, 50)
        elapsed = pg.time.get_ticks() - self.start_ms
        if elapsed >= self.lifetime_ms:
            return True
        
        gravity = -20.0
        self.vy += gravity * (dt_ms / 1000.0)
        self.y += self.vy * (dt_ms / 1000.0)
        
        fade_start = self.lifetime_ms * 0.6
        if elapsed > fade_start:
            fade_ratio = (elapsed - fade_start) / (self.lifetime_ms - fade_start)
            self.alpha = max(0, int(255 * (1 - fade_ratio)))
        
        return False

    def draw(self, surface):
        if self.is_critical:
            text_str = f"{format_number(self.damage)}!"
        else:
            text_str = f"{format_number(self.damage)}"

        txt_surf = self.font.render(text_str, True, self.color)
        txt_surf.set_alpha(self.alpha)
        rect = txt_surf.get_rect(center=(int(self.x), int(self.y)))
        surface.blit(txt_surf, rect)

    def is_alive(self):
        elapsed = pg.time.get_ticks() - self.start_ms
        return elapsed < self.lifetime_ms


damage_per_click = getattr(Equipment_System, "base_damage", 1)

crit_chance = 0.05        
crit_multiplier = 2.0     

def calculate_damage(base_damage=None, extra_chance=0.0, extra_multi=1.0):
    if base_damage is None:
        damage = float(Equipment_System.base_damage)
    else:
        damage = float(base_damage)
    
    damage *= float(Equipment_System.total_damage_multiplier)
    
    upgrade_level = getattr(Player_Upgrade_System, "level", 0)
    damage += upgrade_level
    if upgrade_level > 0 and upgrade_level % 50 == 0:
        damage *= 1.2
    
    total_crit_chance = crit_chance + float(extra_chance)
    total_crit_multi = crit_multiplier * float(extra_multi)
    
    is_critical = random.random() < total_crit_chance
    if is_critical:
        damage *= total_crit_multi
    
    return int(damage), is_critical