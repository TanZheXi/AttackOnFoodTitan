import pygame as pg
import time
import random
import os
import Click_Damage_Feature
from Click_Damage_Feature import calculate_damage, DamageText
import Button_System
import AFK_System
import Currency_System
import Equipment_System
from KitchenGuide_System import KitchenGuideSystem
from Abilities import SpicySurge, CrispyPrecision,ManaSystem
from Player_Upgrade_System import PlayerUpgradeSystem




# ========== Spinner Loading Animation ==========
def show_loading_screen(screen, message, progress=0):
    """Shows a loading screen with a spinning circle animation."""
    screen.fill((30, 30, 40))
    font = pg.font.SysFont(None, 48)
    font_small = pg.font.SysFont(None, 24)
    
    # "Loading..." text
    text = font.render("Loading...", True, (255, 255, 255))
    text_rect = text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 50))
    screen.blit(text, text_rect)
    
    # message text
    msg_text = font_small.render(message, True, (200, 200, 200))
    msg_rect = msg_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 20))
    screen.blit(msg_text, msg_rect)

    # ===== Spinner（Spirit image） =====
    if spinner_frames:
        # Calculate which frame to display based on time (the frame changes each time this function is called)
        frame_index = int((pg.time.get_ticks() / 80) % len(spinner_frames))
        frame = spinner_frames[frame_index]
        
        # Print it at middle
        draw_x = WINDOW_WIDTH//2 - frame.get_width()//2
        draw_y = WINDOW_HEIGHT//2 + 80 - frame.get_height()//2
        screen.blit(frame, (draw_x, draw_y))
    else:
        # Show fallback text if spinner frames are not loaded
        fallback_text = font_small.render("Loading...", True, (200, 200, 200))
        fallback_rect = fallback_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 70))
        screen.blit(fallback_text, fallback_rect)
    # =================================
    
    pg.display.flip()
    
class BoostIndicator:
    def __init__(self, x, y, width, height):
        self.rect = pg.Rect(x, y, width, height)
        self.font = pg.font.SysFont(None, 16)
        self.font_small = pg.font.SysFont(None, 12)
        self.visible = False
        self.end_time = 0
        self.duration = 3 * 60 * 60

    def activate(self, end_time):
        self.visible = True
        self.end_time = end_time
        print(f"[BOOST] x2 Currency Boost activated!")

    def update(self):
        if self.visible:
            if time.time() >= self.end_time:
                self.visible = False
                print("[BOOST] x2 Currency Boost has expired!")

    def get_remaining_percentage(self):
        if not self.visible or self.end_time == 0:
            return 0
        remaining = max(0, self.end_time - time.time())
        return (remaining / self.duration) * 100

    def get_remaining_text(self):
        if not self.visible:
            return ""
        remaining = max(0, self.end_time - time.time())
        hours = int(remaining // 3600)
        minutes = int((remaining % 3600) // 60)
        seconds = int(remaining % 60)
        if hours > 0:
            return f"{hours}h {minutes}m"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"

    def get_save_data(self):
        if self.visible:
            return {"visible": True, "end_time": self.end_time}
        return {"visible": False}

    def restore_save_data(self, data):
        if data and data.get("visible", False):
            self.visible = True
            self.end_time = data.get("end_time", 0)
            if time.time() >= self.end_time:
                self.visible = False

    def draw(self, screen):
        if not self.visible:
            return
        bg_rect = pg.Rect(self.rect.x, self.rect.y, self.rect.width, self.rect.height)
        pg.draw.rect(screen, (30, 30, 40), bg_rect)
        pg.draw.rect(screen, (255, 200, 100), bg_rect, 2)
        
        title = self.font.render("x2 CURRENCY BOOST ACTIVE!", True, (255, 220, 100))
        screen.blit(title, (bg_rect.x + 10, bg_rect.y + 5))
        
        time_text = self.font_small.render(f"Time remaining: {self.get_remaining_text()}", True, (200, 200, 220))
        screen.blit(time_text, (bg_rect.x + 10, bg_rect.y + 28))
        
        bar_bg = pg.Rect(bg_rect.x + 10, bg_rect.y + 48, bg_rect.width - 20, 10)
        pg.draw.rect(screen, (60, 60, 80), bar_bg)
        pg.draw.rect(screen, (100, 100, 120), bar_bg, 1)
        
        progress = self.get_remaining_percentage() / 100
        fill_width = int((bg_rect.width - 20) * progress)
        fill_rect = pg.Rect(bg_rect.x + 10, bg_rect.y + 48, fill_width, 10)
        pg.draw.rect(screen, (255, 200, 100), fill_rect)
        
        hint = self.font_small.render("Earn 2x money from defeating monsters!", True, (180, 180, 200))
        screen.blit(hint, (bg_rect.x + 10, bg_rect.y + 65))

# ========== UI LAYOUT ==========
WINDOW_WIDTH = 1300
WINDOW_HEIGHT = 750

LEFT_WIDTH = 300
MIDDLE_WIDTH = 550
RIGHT_WIDTH = WINDOW_WIDTH - LEFT_WIDTH - MIDDLE_WIDTH

LEFT_AREA_X = 0
MIDDLE_AREA_X = LEFT_WIDTH
RIGHT_AREA_X = LEFT_WIDTH + MIDDLE_WIDTH

MIDDLE_CENTER_X = MIDDLE_AREA_X + MIDDLE_WIDTH // 2

Currency_System.MIDDLE_CENTER_X = MIDDLE_CENTER_X

# Setting up background images
BACKGROUNDS = ["bg_kitchen.png", "bg_party.png", "bg_bbq.png", "bg_camping.png", "bg_beach.png"]
background_folder = os.path.join(os.path.dirname(__file__), "Background")

# ===========================================
pg.init()
pg.mixer.init()
window = pg.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pg.display.set_caption("Attack On Food Titan")

#Load spinner spirit image
spinner_frames = []
spinner_frame_count = 18

try:
    spinner_path = os.path.join(os.path.dirname(__file__), "Background", "Image", "Spinner.png")
    if os.path.exists(spinner_path):
        spinner_sheet = pg.image.load(spinner_path).convert_alpha()

        # Remove near-white background from the spinner sheet
        for x in range(spinner_sheet.get_width()):
            for y in range(spinner_sheet.get_height()):
                r, g, b, a = spinner_sheet.get_at((x, y))
                # If RGB > 240, set to transparent
                if r > 240 and g > 240 and b > 240:
                    spinner_sheet.set_at((x, y), (0, 0, 0, 0))

        # Automatically calculate frame width based on the number of frames
        frame_width = spinner_sheet.get_width() // spinner_frame_count
        frame_height = spinner_sheet.get_height()
        for i in range(spinner_frame_count):
            frame = spinner_sheet.subsurface((i * frame_width, 0, frame_width, frame_height))
            spinner_frames.append(frame)
        print(f"[SPINNER] Loaded {len(spinner_frames)} frames from Spinner.png")
    else:
        print(f"[SPINNER] Warning: Spinner.png not found at {spinner_path}")
except Exception as e:
    print(f"[SPINNER] Error loading spinner: {e}")

# Show initial loading screen
show_loading_screen(window, "Initializing...", 0.05)

# ========== BGM System ==========
MUSIC_FILES = ["Opening1.MP3", "Opening2.MP3", "Opening3.MP3"]
bgm_folder = os.path.join(os.path.dirname(__file__), "BGM")
music_paths = []

# Load music files and print status
for music_file in MUSIC_FILES:
    music_path = os.path.join(bgm_folder, music_file)
    if os.path.exists(music_path):
        music_paths.append(music_path)
        print(f"[BGM] Found: {music_file}")
    else:
        print(f"[BGM] Warning: {music_file} not found")

current_music_index = 0

def play_next_music():
    """Play the next music track in the list, looping back to the start if necessary."""
    global current_music_index
    
    if not music_paths:
        print("[BGM] No music files found!")
        return
    
    try:
        # Load and play the current music track
        pg.mixer.music.load(music_paths[current_music_index])
        pg.mixer.music.play()
        
        # print the name of the currently playing track
        music_name = os.path.basename(music_paths[current_music_index])
        print(f"[BGM] Now playing: {music_name} ({current_music_index + 1}/{len(music_paths)})")
        
        # increment the index for the next track
        current_music_index = (current_music_index + 1) % len(music_paths)
        
    except Exception as e:
        print(f"[BGM] Error playing music: {e}")

def start_background_music():
    """Start the background music system"""
    if not music_paths:
        print("[BGM] No music files available!")
        return False
    
    try:
        # Set up the event that will be triggered when a music track ends
        pg.mixer.music.set_endevent(pg.USEREVENT + 1)
        
        # Play the first track immediately
        play_next_music()
        
        # Set a reasonable volume level (0.0 to 1.0)
        pg.mixer.music.set_volume(0.5)
        
        print(f"[BGM] Music system started with {len(music_paths)} songs")
        return True
        
    except Exception as e:
        print(f"[BGM] Failed to start: {e}")        
        return False

# Load BGM
start_background_music()
# ===========================================

# Continue with loading resources while music plays
show_loading_screen(window, "Loading resources...", 0.1)

# ========== Animation ==========
def remove_white_background(image, threshold=240):
    """Remove near-white background"""
    image = image.convert_alpha()
    for x in range(image.get_width()):
        for y in range(image.get_height()):
            try:
                r, g, b, a = image.get_at((x, y))
                if r > threshold and g > threshold and b > threshold:
                    image.set_at((x, y), (0, 0, 0, 0))
            except:
                pass
    return image

class AttackAnimation:
    """Handles slash and scratch animations when attacking monsters."""
    def __init__(self, x, y, frames, scale=0.5, offset_x=0, offset_y=0):
        self.x = x
        self.y = y
        self.current_frame = 0
        self.animation_speed = 0.08
        self.time_since_last_frame = 0
        self.is_active = True
        self.scale = scale
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.alpha = 255
        
        #CACHE THE SCALED FRAMES ONCE
        self.frames = []
        for f in frames:
            if self.scale != 1.0:
                new_width = int(f.get_width() * self.scale)
                new_height = int(f.get_height() * self.scale)
                self.frames.append(pg.transform.scale(f, (new_width, new_height)))
            else:
                self.frames.append(f)

    def update(self, dt):
        if not self.is_active:
            return
        self.time_since_last_frame += dt
        if self.time_since_last_frame >= self.animation_speed:
            self.time_since_last_frame = 0
            self.current_frame += 1
            if self.current_frame >= len(self.frames):
                self.is_active = False
            else:
                total_frames = len(self.frames)
                if self.current_frame > total_frames * 0.6:
                    fade_ratio = (self.current_frame - total_frames * 0.6) / (total_frames * 0.4)
                    self.alpha = max(0, int(255 * (1 - fade_ratio)))
                else:
                    self.alpha = 255

    def draw(self, screen):
        if not self.is_active or self.current_frame >= len(self.frames):
            return
            
        #CACHE THE SCALED FRAMES ONCE
        frame = self.frames[self.current_frame]
        
        # Copy to safely apply transparency
        temp_frame = frame.copy()
        temp_frame.set_alpha(self.alpha)
        
        draw_x = self.x - temp_frame.get_width() // 2 + self.offset_x
        draw_y = self.y - temp_frame.get_height() // 2 + self.offset_y
        screen.blit(temp_frame, (draw_x, draw_y))

    def is_finished(self):
        return not self.is_active

# ========== Load Animation Frames ==========
show_loading_screen(window, "Loading animations...", 0.1)

slash_animation_frames = []
scratch_animation_frames = []

try:
    image_folder = os.path.join(os.path.dirname(__file__), "Background", "Image")
    
    # Load slash animation
    slash_path = os.path.join(image_folder, "Slash.png")
    if os.path.exists(slash_path):
        slash_sheet = pg.image.load(slash_path).convert_alpha()
        slash_sheet = remove_white_background(slash_sheet)
        frame_width = slash_sheet.get_width() // 12
        frame_height = slash_sheet.get_height()
        for i in range(12):
            frame = slash_sheet.subsurface((i * frame_width, 0, frame_width, frame_height))
            slash_animation_frames.append(frame)
        print(f"[ANIMATION] Loaded Slash: {len(slash_animation_frames)} frames")
    
    # Load scratch animation
    scratch_path = os.path.join(image_folder, "Scratches.png")
    if os.path.exists(scratch_path):
        scratch_sheet = pg.image.load(scratch_path).convert_alpha()
        scratch_sheet = remove_white_background(scratch_sheet)
        frame_width = scratch_sheet.get_width() // 6
        frame_height = scratch_sheet.get_height()
        for i in range(6):
            frame = scratch_sheet.subsurface((i * frame_width, 0, frame_width, frame_height))
            scratch_animation_frames.append(frame)
        print(f"[ANIMATION] Loaded Scratch: {len(scratch_animation_frames)} frames")
except Exception as e:
    print(f"[ANIMATION] Error: {e}")

# ========== BGM ==========
show_loading_screen(window, "Loading music...", 0.2)

MUSIC_FILES = ["Opening1.MP3", "Opening2.MP3", "Opening3.MP3"]
bgm_folder = os.path.join(os.path.dirname(__file__), "BGM")
music_paths = []
for music_file in MUSIC_FILES:
    music_path = os.path.join(bgm_folder, music_file)
    if os.path.exists(music_path):
        music_paths.append(music_path)

current_music_index = 0

def play_next_music():
    global current_music_index
    if not music_paths:
        return
    try:
        pg.mixer.music.stop()
        pg.mixer.music.load(music_paths[current_music_index])
        pg.mixer.music.play()
        current_music_index = (current_music_index + 1) % len(music_paths)
    except Exception as e:
        print(f"[BGM] Error: {e}")

def start_background_music():
    try:
        pg.mixer.music.set_endevent(pg.USEREVENT + 1)
        if music_paths:
            play_next_music()
            pg.mixer.music.set_volume(0.5)
    except Exception as e:
        print(f"[BGM] Failed: {e}")

# ========== Sound Effects ==========
show_loading_screen(window, "Loading sound effects...", 0.3)

titan_defeated_sound = None
attack_titan_sound = None
pet_attack_sound = None

try:
    sound_folder = os.path.join(os.path.dirname(__file__), "Sound_Effects")
    
    titan_path = os.path.join(sound_folder, "TitansDefeated.MP3")
    if os.path.exists(titan_path):
        titan_defeated_sound = pg.mixer.Sound(titan_path)
        titan_defeated_sound.set_volume(0.6)
    
    attack_path = os.path.join(sound_folder, "AttackTitans.MP3")
    if os.path.exists(attack_path):
        attack_titan_sound = pg.mixer.Sound(attack_path)
        attack_titan_sound.set_volume(0.5)
    
    pet_path = os.path.join(sound_folder, "Scratching.MP3")
    if os.path.exists(pet_path):
        pet_attack_sound = pg.mixer.Sound(pet_path)
        pet_attack_sound.set_volume(0.5)
except Exception as e:
    print(f"[SOUND] Warning: {e}")

# ========== Background Image Loading ==========
show_loading_screen(window, "Loading backgrounds...", 0.4)

stats_panel_folder = os.path.join(os.path.dirname(__file__), "Background", "Stats_panel")
stats_panel_path = os.path.join(stats_panel_folder, "StatsPanel.png")

try:
    if os.path.exists(stats_panel_path):
        stats_panel_bg = pg.image.load(stats_panel_path).convert()
        stats_panel_bg = pg.transform.scale(stats_panel_bg, (LEFT_WIDTH, WINDOW_HEIGHT))
    else:
        stats_panel_bg = pg.Surface((LEFT_WIDTH, WINDOW_HEIGHT))
        stats_panel_bg.fill((40, 40, 50))
except Exception as e:
    stats_panel_bg = pg.Surface((LEFT_WIDTH, WINDOW_HEIGHT))
    stats_panel_bg.fill((40, 40, 50))

background_images = []
for i, bg_name in enumerate(BACKGROUNDS):
    show_loading_screen(window, f"Loading background {i+1}/{len(BACKGROUNDS)}...", 0.4 + (i * 0.05))
    bg_path = os.path.join(background_folder, bg_name)
    try:
        if os.path.exists(bg_path):
            img = pg.image.load(bg_path).convert()
            img = pg.transform.scale(img, (MIDDLE_WIDTH, WINDOW_HEIGHT))
            background_images.append(img)
        else:
            placeholder = pg.Surface((MIDDLE_WIDTH, WINDOW_HEIGHT))
            placeholder.fill((50, 50, 60))
            background_images.append(placeholder)
    except Exception as e:
        placeholder = pg.Surface((MIDDLE_WIDTH, WINDOW_HEIGHT))
        placeholder.fill((50, 50, 60))
        background_images.append(placeholder)

def get_background_index(stage):
    return ((stage - 1) // 30) % 5

def get_current_background(stage):
    idx = get_background_index(stage)
    if idx < len(background_images):
        return background_images[idx]
    return background_images[0]

# ========== Load Save Data ==========
show_loading_screen(window, "Loading save data...", 0.7)

clock = pg.time.Clock()
afk_earnings, saved_monster_data, saved_money, saved_progression_index, saved_stage, saved_inventory, saved_shop_state, saved_pet_data, saved_upgrade_level, saved_guide_data, saved_boost_data, saved_michelin_stars, saved_ability_data, saved_player_upgrade_data, saved_companion_data = AFK_System.afk_system.load_and_calculate_afk_rewards()

Currency_System.michelin_stars = saved_michelin_stars
Equipment_System.load_equipment()

if saved_money > 0:
    Currency_System.pocket_money = saved_money
if afk_earnings > 0:
    Currency_System.pocket_money += afk_earnings
    AFK_System.show_afk_rewards(window, afk_earnings)

monster_manager = Click_Damage_Feature.MonsterManager()
MONSTER_SIZE = 200

if saved_monster_data:
    monster_manager.progression_index = saved_progression_index
    monster_manager.stage = saved_stage
    current_monster = Click_Damage_Feature.Monster(
        saved_monster_data["name"],
        saved_monster_data["max_hp"],
        tuple(saved_monster_data["color"])
    )
    
    # --- Restart the fight if they quit during death animation ---
    if saved_monster_data["hp"] <= 0:
        current_monster.hp = saved_monster_data["max_hp"]
    else:
        current_monster.hp = saved_monster_data["hp"]
    # -------------------------------------------------------------

    # Restore boss timer data
    is_boss = (saved_progression_index % 10 == 9)
    if is_boss:
        current_monster.boss_timer_active = True
        current_monster.boss_timer_start = saved_monster_data.get("boss_timer_start", time.time())
    else:
        current_monster.boss_timer_active = False
    
    current_monster.boss_timer_duration = 30
        
    current_monster.rect.x = MIDDLE_CENTER_X - MONSTER_SIZE // 2
    current_monster.rect.y = 275
    monster_manager.current_monster = current_monster
else:
    current_monster = monster_manager.current_monster
    current_monster.rect.x = MIDDLE_CENTER_X - MONSTER_SIZE // 2
    current_monster.rect.y = 275

show_loading_screen(window, "Initializing systems...", 0.9)

try:
    icon_path = os.path.join(os.path.dirname(__file__), "Icon", "Monster.png")
    raw_monster_icon = pg.image.load(icon_path).convert_alpha()
    # Scale it down to 35x35 so it fits perfectly next to the text
    hud_monster_icon = pg.transform.scale(raw_monster_icon, (35, 35))
except Exception as e:
    print(f"Could not load monster icon: {e}")
    hud_monster_icon = None

IsRunning = True
last_auto_save = time.time()
auto_save_interval = 5

PET_ATTACK_INTERVAL = 1.0
last_pet_attack_time = time.time()

COMPANION_ATTACK_INTERVAL = 1.0  # one attack per second
last_companion_attack_time = time.time()

Button_System.panel_manager.pending_inventory = saved_inventory if saved_inventory else []
Button_System.panel_manager.pending_shop_state = saved_shop_state if saved_shop_state else []
Button_System.panel_manager.pending_pet_data = saved_pet_data if saved_pet_data else []
Button_System.panel_manager.pending_guide_data = saved_guide_data if saved_guide_data else {}
Button_System.panel_manager.pending_money = Currency_System.pocket_money

data_restored = False
damage_texts = []
attack_animations = []

boost_indicator = BoostIndicator(x=LEFT_AREA_X + 10, y=WINDOW_HEIGHT - 100, width=280, height=85)
if saved_boost_data:
    boost_indicator.restore_save_data(saved_boost_data)

# ✅ Place abilities near the left panel, bottom aligned
damage_boost = SpicySurge(
    x=LEFT_WIDTH + 60,        # safely inside middle area, not touching left panel
    y=WINDOW_HEIGHT - 120,    # keep same vertical position
    radius=35
)

crispy_precision = CrispyPrecision(
    x=damage_boost.x + 100,   # offset to the right of Spicy Surge
    y=damage_boost.y,
    radius=35
)

mana_system = ManaSystem()

# =========================
# Initialize upgrade system
# =========================
player_upgrade_system = PlayerUpgradeSystem(
    x=RIGHT_AREA_X + 20,
    y=100,
    width=400,
    height=400
)

# ✅ Link mana system to player upgrade system
player_upgrade_system.mana_system = mana_system

# ========== Restore Player Upgrade Data ==========
if saved_player_upgrade_data:
    player_upgrade_system.level = saved_player_upgrade_data.get("level", 0)
    player_upgrade_system.current_cost = saved_player_upgrade_data.get("current_cost", player_upgrade_system.base_cost)
    player_upgrade_system.spicy_level = saved_player_upgrade_data.get("spicy_level", 0)
    player_upgrade_system.spicy_cost = saved_player_upgrade_data.get("spicy_cost", 50000)
    player_upgrade_system.spicy_damage_boost = saved_player_upgrade_data.get("spicy_damage_boost", 0.0)
    player_upgrade_system.spicy_unlocked = saved_player_upgrade_data.get("spicy_unlocked", False)
    player_upgrade_system.crispy_level = saved_player_upgrade_data.get("crispy_level", 0)
    player_upgrade_system.crispy_cost = saved_player_upgrade_data.get("crispy_cost", 250000)
    player_upgrade_system.crispy_crit_damage = saved_player_upgrade_data.get("crispy_crit_damage", 0.0)
    player_upgrade_system.crispy_crit_chance = saved_player_upgrade_data.get("crispy_crit_chance", 0.0)
    player_upgrade_system.crispy_unlocked = saved_player_upgrade_data.get("crispy_unlocked", False)
    player_upgrade_system.crit_dmg_level = saved_player_upgrade_data.get("crit_dmg_level", 0)
    player_upgrade_system.crit_dmg_cost = saved_player_upgrade_data.get("crit_dmg_cost", 100)
    player_upgrade_system.crit_dmg_bonus = saved_player_upgrade_data.get("crit_dmg_bonus", 0.0)
    player_upgrade_system.crit_chance_level = saved_player_upgrade_data.get("crit_chance_level", 0)
    player_upgrade_system.crit_chance_cost = saved_player_upgrade_data.get("crit_chance_cost", 250)
    player_upgrade_system.crit_chance_bonus = saved_player_upgrade_data.get("crit_chance_bonus", 0.0)
    player_upgrade_system.mana_cap_level = saved_player_upgrade_data.get("mana_cap_level", 0)
    player_upgrade_system.mana_cap_cost = saved_player_upgrade_data.get("mana_cap_cost", 500)
    player_upgrade_system.mana_cap_bonus = saved_player_upgrade_data.get("mana_cap_bonus", 0)
    player_upgrade_system.mana_regen_level = saved_player_upgrade_data.get("mana_regen_level", 0)
    player_upgrade_system.mana_regen_cost = saved_player_upgrade_data.get("mana_regen_cost", 750)
    player_upgrade_system.mana_regen_bonus = saved_player_upgrade_data.get("mana_regen_bonus", 0.0)
    
    # ✅ CRITICAL FIX: Restore crit values from saved data
    crit_dmg_bonus = saved_player_upgrade_data.get("crit_dmg_bonus", 0.0)
    crit_chance_bonus = saved_player_upgrade_data.get("crit_chance_bonus", 0.0)
    
    if crit_dmg_bonus > 0:
        Click_Damage_Feature.set_crit_multiplier(2.0 + crit_dmg_bonus)
        print(f"[LOAD] Restored Crit Multiplier: {Click_Damage_Feature.get_crit_multiplier():.2f}")
    
    if crit_chance_bonus > 0:
        Click_Damage_Feature.set_crit_chance(0.05 + crit_chance_bonus)
        print(f"[LOAD] Restored Crit Chance: {Click_Damage_Feature.get_crit_chance()*100:.1f}%")

    # --- NEW FIX 1: Apply loaded stats directly to the real Mana System ---
    mana_system.max_mana += player_upgrade_system.mana_cap_bonus
    mana_system.regen_rate += player_upgrade_system.mana_regen_bonus
    
    # --- NEW FIX 2: Recalculate Ability Mana Costs based on Level ---
    spicy_mana = 20
    for _ in range(player_upgrade_system.spicy_level):
        spicy_mana = int(spicy_mana * 1.07)
        
    crispy_mana = 30
    for _ in range(player_upgrade_system.crispy_level):
        crispy_mana = int(crispy_mana * 1.09)

    # --- NEW FIX 3: Apply the Ability Upgrades & correctly scaled Mana Costs ---
    if player_upgrade_system.spicy_unlocked:
        damage_boost.set_upgrade_bonus(player_upgrade_system.spicy_damage_boost, spicy_mana)
    if player_upgrade_system.crispy_unlocked:
        crispy_precision.set_upgrade_bonus(player_upgrade_system.crispy_crit_chance, player_upgrade_system.crispy_crit_damage, crispy_mana)


# ========== Restore Companion Data ==========
if saved_companion_data:
    for i, comp_data in enumerate(saved_companion_data):
        if i < len(player_upgrade_system.companions):
            comp = player_upgrade_system.companions[i]
            comp.level = comp_data.get("level", 0)
            comp.current_cost = comp_data.get("current_cost", comp.base_cost)

# ========== Restore Ability Data ==========
if saved_ability_data:
    if "SpicySurge" in saved_ability_data and player_upgrade_system.spicy_unlocked:
        spicy_data = saved_ability_data["SpicySurge"]
        damage_boost.active = spicy_data.get("active", False)
        damage_boost.cooldown = spicy_data.get("cooldown", False)
        damage_boost.start_time = spicy_data.get("start_time", 0)
        damage_boost.cooldown_start = spicy_data.get("cooldown_start", 0)
        if damage_boost.active:
            elapsed = time.time() - damage_boost.start_time
            if elapsed >= damage_boost.duration:
                damage_boost.active = False
                damage_boost.cooldown = True
                damage_boost.cooldown_start = time.time()
    
    if "CrispyPrecision" in saved_ability_data and player_upgrade_system.crispy_unlocked:
        crispy_data = saved_ability_data["CrispyPrecision"]
        crispy_precision.active = crispy_data.get("active", False)
        crispy_precision.cooldown = crispy_data.get("cooldown", False)
        crispy_precision.start_time = crispy_data.get("start_time", 0)
        crispy_precision.cooldown_start = crispy_data.get("cooldown_start", 0)
        if crispy_precision.active:
            elapsed = time.time() - crispy_precision.start_time
            if elapsed >= crispy_precision.duration:
                crispy_precision.active = False
                crispy_precision.cooldown = True
                crispy_precision.cooldown_start = time.time()

# ✅ Link into PanelManager so auto‑attack and events can use it
Button_System.panel_manager.player_upgrade_system = player_upgrade_system

# ✅ Link abilities before events fire
player_upgrade_system.spicy_ability = damage_boost
player_upgrade_system.crispy_ability = crispy_precision
player_upgrade_system.mana_system = mana_system

def on_prestige_reset():
    # Only reset the shop so players can re-buy things if needed
    if Button_System.panel_manager.shop_system:
        Button_System.panel_manager.shop_system.reset_shop()
        
    # We removed the inventory and equipment wipes from here!
    print("[PRESTIGE] Prestige completed. Gear was kept safe!")

    damage_texts.clear()
    attack_animations.clear()

Currency_System.register_prestige_callback(on_prestige_reset)

Button_System.panel_manager.kitchen_guide_system = KitchenGuideSystem(0, 0, 1, 1)
if saved_guide_data:
    Button_System.panel_manager.kitchen_guide_system.guide_manager.restore_save_data(saved_guide_data)

Equipment_System.set_equip_callback(lambda: (
    Button_System.panel_manager.kitchen_guide_system.guide_manager.update_progress("equip_equipment", 1)
    if Button_System.panel_manager.kitchen_guide_system else None
))

if Button_System.panel_manager.kitchen_guide_system:
    original_grant_reward = Button_System.panel_manager.kitchen_guide_system.guide_manager.grant_reward
    def enhanced_grant_reward(reward_type):
        original_grant_reward(reward_type)
        if reward_type == "boost":
            boost_indicator.activate(Button_System.panel_manager.kitchen_guide_system.guide_manager.boost_end_time)
    Button_System.panel_manager.kitchen_guide_system.guide_manager.grant_reward = enhanced_grant_reward

def sync_sfx_volumes(new_volume):
    if attack_titan_sound: 
        attack_titan_sound.set_volume(new_volume)
    if titan_defeated_sound: 
        titan_defeated_sound.set_volume(new_volume)
    if pet_attack_sound: 
        pet_attack_sound.set_volume(new_volume)
    if Button_System.panel_manager.prestige_sound: 
        Button_System.panel_manager.prestige_sound.set_volume(new_volume)

# Pass this function into the PanelManager so the Settings panel can trigger it
Button_System.panel_manager.sync_sfx_callback = sync_sfx_volumes

show_loading_screen(window, "Starting game...", 1.0)


# ---  Developer Mode Flag ---
dev_mode = False

# Add this line to store the prestige button rect
prestige_button = {"rect": None}

# ========== Main Loop ========== #
while IsRunning:
    dt_ms = clock.tick(60)
    dt_sec = dt_ms / 1000.0
    
    #debug_get_mouse_pos() 
    
    boost_indicator.update()

    # Update abilities only if unlocked
    if player_upgrade_system.spicy_unlocked:
       damage_boost.update()
    if player_upgrade_system.crispy_unlocked:
       crispy_precision.update() 
       
    # --- Event Handling ---
    for event in pg.event.get():
        if event.type == pg.USEREVENT + 1:
            play_next_music()

        if event.type == pg.QUIT:
            inventory_state, shop_state, pet_data, guide_data = Button_System.panel_manager.get_save_data()
            upgrade_level = 0
            if Button_System.panel_manager.player_upgrade_system:
                upgrade_level = Button_System.panel_manager.player_upgrade_system.level
            
            # Save player upgrade data
            player_upgrade_save_data = {}
            if Button_System.panel_manager.player_upgrade_system:
                pug = Button_System.panel_manager.player_upgrade_system
                player_upgrade_save_data = {
                    "level": pug.level,
                    "current_cost": pug.current_cost,
                    "spicy_level": pug.spicy_level,
                    "spicy_cost": pug.spicy_cost,
                    "spicy_damage_boost": pug.spicy_damage_boost,
                    "spicy_unlocked": pug.spicy_unlocked,
                    "crispy_level": pug.crispy_level,
                    "crispy_cost": pug.crispy_cost,
                    "crispy_crit_damage": pug.crispy_crit_damage,
                    "crispy_crit_chance": pug.crispy_crit_chance,
                    "crispy_unlocked": pug.crispy_unlocked,
                    "crit_dmg_level": pug.crit_dmg_level,
                    "crit_dmg_cost": pug.crit_dmg_cost,
                    "crit_dmg_bonus": pug.crit_dmg_bonus,
                    "crit_chance_level": pug.crit_chance_level,
                    "crit_chance_cost": pug.crit_chance_cost,
                    "crit_chance_bonus": pug.crit_chance_bonus,
                    "mana_cap_level": pug.mana_cap_level,
                    "mana_cap_cost": pug.mana_cap_cost,
                    "mana_cap_bonus": pug.mana_cap_bonus,
                    "mana_regen_level": pug.mana_regen_level,
                    "mana_regen_cost": pug.mana_regen_cost,
                    "mana_regen_bonus": pug.mana_regen_bonus
                }
            
            # Save companion data
            companion_save_data = []
            if Button_System.panel_manager.player_upgrade_system:
                for comp in Button_System.panel_manager.player_upgrade_system.companions:
                    companion_save_data.append({
                        "name": comp.name,
                        "level": comp.level,
                        "current_cost": comp.current_cost,
                        "base_cost": comp.base_cost,
                        "base_damage": comp.base_damage
                    })
            
            ability_save_data = {}
            if player_upgrade_system.spicy_unlocked:
                ability_save_data["SpicySurge"] = {
                    "active": damage_boost.active,
                    "cooldown": damage_boost.cooldown,
                    "start_time": damage_boost.start_time if damage_boost.active else 0,
                    "cooldown_start": damage_boost.cooldown_start if damage_boost.cooldown else 0,
                    "duration": damage_boost.duration,
                    "cooldown_time": damage_boost.cooldown_time
                }
            if player_upgrade_system.crispy_unlocked:
                ability_save_data["CrispyPrecision"] = {
                    "active": crispy_precision.active,
                    "cooldown": crispy_precision.cooldown,
                    "start_time": crispy_precision.start_time if crispy_precision.active else 0,
                    "cooldown_start": crispy_precision.cooldown_start if crispy_precision.cooldown else 0,
                    "duration": crispy_precision.duration,
                    "cooldown_time": crispy_precision.cooldown_time
                }
            
            boost_data = boost_indicator.get_save_data()

            # Get boss timer data before saving
            is_boss = (monster_manager.progression_index % 10 == 9)
            boss_timer_active = current_monster.boss_timer_active if is_boss else False
            boss_timer_start = current_monster.boss_timer_start if is_boss else 0
            
            AFK_System.afk_system.save_game_data(
                pocket_money=Currency_System.pocket_money,
                monster_hp=current_monster.hp,
                monster_max_hp=current_monster.max_hp,
                monster_name=current_monster.name,
                monster_color=current_monster.color,
                progression_index=monster_manager.progression_index,
                stage=monster_manager.stage,
                inventory_items=inventory_state,
                shop_items_state=shop_state,
                pet_data=pet_data,
                upgrade_level=upgrade_level,
                guide_data=guide_data,
                boost_data=boost_data,
                michelin_stars=Currency_System.michelin_stars,
                ability_data=ability_save_data,
                player_upgrade_data=player_upgrade_save_data,
                companion_data=companion_save_data,
                boss_timer_active=boss_timer_active,     
                boss_timer_start=boss_timer_start
            )
            IsRunning = False
            break

        elif event.type == pg.KEYDOWN:
            # --- NEW: Developer Mode Toggle (F12 Key) ---
            if event.key == pg.K_F12:
                dev_mode = not dev_mode
                print(f"[SYSTEM] Developer Mode is now {'ON' if dev_mode else 'OFF'}")

            # ===== PRESTIGE KEYBIND (Always available, not just in dev mode) =====
            if event.key == pg.K_p:
            # Check if prestige is ready
              current_stars = Currency_System.michelin_stars
              next_requirement = Currency_System.get_next_prestige_requirement(current_stars)

              if next_requirement is None:
                 print("[PRESTIGE] Max prestige already reached!")
              elif monster_manager.stage >= next_requirement:
                 success, new_monster = Currency_System.trigger_prestige(monster_manager)
                 if success:
                    # ✅ Update the current_monster reference
                    current_monster = new_monster

                    # Set the monster's position
                    current_monster.rect.x = MIDDLE_CENTER_X - MONSTER_SIZE // 2
                    current_monster.rect.y = 275

                    # ✅ Force HP to max
                    current_monster.hp = current_monster.max_hp
            
                    # Reset animations and texts
                    damage_texts.clear()
                    attack_animations.clear()
                    # Reset any open panels
                    Button_System.panel_manager.active_panel = None
            else:
                print(f"[PRESTIGE] Need Stage {next_requirement} to prestige! (Current: Stage {monster_manager.stage})")
    
                
            # Only allow these keybinds if Developer Mode is ON
            if dev_mode:
                if event.key == pg.K_g:
                    Equipment_System.gain_equipment("OP WEAPON")
                    Button_System.panel_manager.add_to_inventory("OP WEAPON")
                elif event.key == pg.K_e:
                    selected_item = Button_System.panel_manager.get_selected_inventory_item()
                    if selected_item and selected_item in Equipment_System.equipment_database:
                        Equipment_System.equip_equipment(selected_item)
                elif event.key == pg.K_u:
                    Equipment_System.unequip_equipment("weapon")
                elif event.key == pg.K_c:
                    if Equipment_System.craft_item("Golden Spatula"):
                        Button_System.panel_manager.add_to_inventory("Golden Spatula")
                elif event.key == pg.K_n:
                    monster_manager.stage += 1
                    monster_manager.progression_index = (monster_manager.stage - 1) * 10
                    monster_manager.current_monster = monster_manager.spawn_monster()  

        elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            # ===== CHECK PRESTIGE BUTTON CLICK =====
            if prestige_button_rect and prestige_button_rect.collidepoint(event.pos):
               print(f"[DEBUG] Prestige button clicked!")
               print(f"[DEBUG] Current Stage: {monster_manager.stage}")
               print(f"[DEBUG] Current Stars: {Currency_System.michelin_stars}")
        
               # Check if prestige is ready
               current_stars = Currency_System.michelin_stars
               next_requirement = Currency_System.get_next_prestige_requirement(current_stars)
        
               if next_requirement is None:
                  print("[PRESTIGE] Max prestige already reached!")
               elif monster_manager.stage >= next_requirement:
                  print(f"[DEBUG] ✓ Prestige condition met! Stage {monster_manager.stage} >= {next_requirement}")
                  success, updated_monster = Currency_System.trigger_prestige(monster_manager)
                  if success:
                      # ✅ Update the current_monster reference
                      current_monster = updated_monster
                
                      # ✅ Set the monster's position
                      current_monster.rect.x = MIDDLE_CENTER_X - MONSTER_SIZE // 2
                      current_monster.rect.y = 275
                
                      # Reset animations and texts
                      damage_texts.clear()
                      attack_animations.clear()
                      # Reset any open panels
                      Button_System.panel_manager.active_panel = None
                
                      print(f"[DEBUG] ✓ Prestige successful! Monster HP: {current_monster.hp}/{current_monster.max_hp}")
                  else:
                      print("[DEBUG] ✗ Prestige failed!")
               else:
                  print(f"[PRESTIGE] Need Stage {next_requirement} to prestige! (Current: Stage {monster_manager.stage})") 
            else:
                print(f"[DEBUG] ✗ Click not on prestige button")

            if current_monster.rect.collidepoint(event.pos):
                if attack_titan_sound:
                    attack_titan_sound.play()

                extra_chance, extra_multi = crispy_precision.get_crit_bonus()
                
                # Add permanent player upgrades to the ability bonus!
                if Button_System.panel_manager.player_upgrade_system:
                    extra_chance += Button_System.panel_manager.player_upgrade_system.crit_chance_bonus
                    extra_multi += Button_System.panel_manager.player_upgrade_system.crit_dmg_bonus
                
                # Match the Stats Panel calculation
                raw_base = getattr(Equipment_System, "base_damage", Click_Damage_Feature.damage_per_click)
            
                eq_multi = float(Equipment_System.total_damage_multiplier)
                
                upgrade_lvl = 0
                if Button_System.panel_manager.player_upgrade_system:
                    upgrade_lvl = Button_System.panel_manager.player_upgrade_system.level
                    
                base_calc = (raw_base * eq_multi) + upgrade_lvl
                if upgrade_lvl > 0 and upgrade_lvl % 50 == 0:
                    base_calc *= 1.2

                # Pass the fully calculated base into the crit function
                final_damage, is_critical = calculate_damage(base_calc, extra_chance, extra_multi)
                final_damage = int(final_damage * damage_boost.get_multiplier() * Currency_System.get_prestige_multiplier())
                current_monster.take_damage(final_damage)

                popup_x = current_monster.rect.x + random.randint(20, current_monster.rect.width - 20)
                popup_y = current_monster.rect.y + random.randint(20, current_monster.rect.height - 20)
                damage_texts.append(DamageText(str(final_damage), (popup_x, popup_y), is_critical))

                # Track if player got the final hit
                if current_monster.is_defeated() and not hasattr(current_monster, "last_hit_by"):
                    current_monster.last_hit_by = "player"

        if player_upgrade_system.spicy_unlocked:
           damage_boost.handle_event(event, mana_system)  
        if player_upgrade_system.crispy_unlocked:
           crispy_precision.handle_event(event, mana_system)  

        Button_System.panel_manager.monster_manager = monster_manager
        Button_System.panel_manager.handle_event(event)
        for button in Button_System.buttons:
            button.handle_event(event)

    # ========== Pet auto attack ==========
    current_time = time.time()
    if current_time - last_pet_attack_time >= PET_ATTACK_INTERVAL:
        pet_system = Button_System.panel_manager.pet_system
        if pet_system:
            base_pet_damage = pet_system.get_total_damage()
            if base_pet_damage > 0 and current_monster.hp > 0:
                if pet_attack_sound:
                    pet_attack_sound.play()

                if scratch_animation_frames:
                    attack_animations.append(AttackAnimation(
                        current_monster.rect.centerx,
                        current_monster.rect.centery,
                        scratch_animation_frames,
                        scale=0.4,
                        offset_x=0,
                        offset_y=0
                    ))

                extra_chance, extra_multi = crispy_precision.get_crit_bonus()
                
                # Add permanent player upgrades for the pet 
                if Button_System.panel_manager.player_upgrade_system:
                    extra_chance += Button_System.panel_manager.player_upgrade_system.crit_chance_bonus
                    extra_multi += Button_System.panel_manager.player_upgrade_system.crit_dmg_bonus

                pet_damage, is_critical = calculate_damage(base_pet_damage, extra_chance, extra_multi)
                final_pet_damage = int(pet_damage * damage_boost.get_multiplier() * Currency_System.get_prestige_multiplier())
                current_monster.take_damage(final_pet_damage)

                popup_x = current_monster.rect.x + random.randint(20, current_monster.rect.width - 20)
                popup_y = current_monster.rect.y + random.randint(20, current_monster.rect.height - 20)
                damage_texts.append(DamageText(str(final_pet_damage), (popup_x, popup_y), is_critical))

                # Track if pet got the final hit
                if current_monster.is_defeated() and not hasattr(current_monster, "last_hit_by"):
                    current_monster.last_hit_by = "pet"
                    
        last_pet_attack_time = current_time

    # ========== Companion auto attack ==========
    current_time = time.time()
    if current_time - last_companion_attack_time >= COMPANION_ATTACK_INTERVAL:
        if Button_System.panel_manager.player_upgrade_system:
            for comp in Button_System.panel_manager.player_upgrade_system.companions:
                if comp.level > 0 and current_monster.hp > 0:
                   dmg = comp.get_damage()
                   current_monster.take_damage(dmg)

                   popup_x = current_monster.rect.x + random.randint(20, current_monster.rect.width - 20)
                   popup_y = current_monster.rect.y + random.randint(20, current_monster.rect.height - 20)
                   damage_texts.append(DamageText(str(dmg), (popup_x, popup_y), False))

                   if current_monster.is_defeated() and not hasattr(current_monster, "last_hit_by"):
                      current_monster.last_hit_by = comp.name

        last_companion_attack_time = current_time
    # ========== Boss Timer Check ==========
    if current_monster.boss_timer_active and not current_monster.is_defeated():
       elapsed = time.time() - current_monster.boss_timer_start
       if elapsed >= current_monster.boss_timer_duration:
           print("[BOSS TIMER] Failed to defeat boss in time!")
           # Reset to monster 5 of current stage
           monster_manager.progression_index = (monster_manager.stage - 1) * 10 + 4
           monster_manager.current_monster = monster_manager.spawn_monster()
           current_monster = monster_manager.current_monster
           current_monster.rect.x = MIDDLE_CENTER_X - MONSTER_SIZE // 2
           current_monster.rect.y = 275

    # ========== Monster Death & Respawn Logic ==========
    if current_monster.state == "dead":
        # 1. Give rewards ONLY ONCE
        if not hasattr(current_monster, "rewards_given"):
            current_monster.rewards_given = True
            
            Currency_System.update_economy(current_monster.max_hp, monster_manager.progression_index + 1)
            if titan_defeated_sound:
                titan_defeated_sound.play()
            
            if Button_System.panel_manager.kitchen_guide_system:
                if getattr(current_monster, "last_hit_by", "player") == "pet":
                    Button_System.panel_manager.kitchen_guide_system.guide_manager.update_progress("defeat_with_pet", 1)
                else:
                    Button_System.panel_manager.kitchen_guide_system.guide_manager.update_progress("defeat_titan", 1)
        
        # 2. Wait 1 second for the fade out vanish to finish!
        if time.time() - current_monster.death_time > 1.0:
            monster_manager.next_monster()
            current_monster = monster_manager.current_monster
            current_monster.rect.x = MIDDLE_CENTER_X - MONSTER_SIZE // 2
            current_monster.rect.y = 275

    # ========== Update Damage Texts ==========
    new_damage_texts = []
    for dt_obj in damage_texts:
        if not dt_obj.update(dt_ms):
            new_damage_texts.append(dt_obj)
    damage_texts = new_damage_texts

    new_animations = []
    for anim in attack_animations:
        anim.update(dt_sec)
        if not anim.is_finished():
            new_animations.append(anim)
    attack_animations = new_animations

    # ========== Load Saved Data ==========
    if not data_restored:
        Button_System.panel_manager.load_saved_data(
            Currency_System.pocket_money,
            saved_inventory,
            saved_shop_state,
            saved_pet_data,
            saved_guide_data
        )
        data_restored = True

    if Button_System.panel_manager.pet_system and not hasattr(Button_System.panel_manager.pet_system, '_callback_set'):
        Button_System.panel_manager.pet_system.guide_callback = lambda: (
            Button_System.panel_manager.kitchen_guide_system.guide_manager.update_progress("equip_pet", 1)
            if Button_System.panel_manager.kitchen_guide_system else None
        )
        Button_System.panel_manager.pet_system._callback_set = True

    if Button_System.panel_manager.player_upgrade_system and not hasattr(Button_System.panel_manager.player_upgrade_system, '_callback_set'):
        Button_System.panel_manager.player_upgrade_system.upgrade_callback = lambda: (
            Button_System.panel_manager.kitchen_guide_system.guide_manager.update_progress("upgrade_base_damage", 1)
            if Button_System.panel_manager.kitchen_guide_system else None
        )
        Button_System.panel_manager.player_upgrade_system._callback_set = True

    if Button_System.panel_manager.player_upgrade_system and saved_upgrade_level > 0:
        if Button_System.panel_manager.player_upgrade_system.level == 0:
            for _ in range(saved_upgrade_level):
                Button_System.panel_manager.player_upgrade_system.purchase_upgrade()

    Button_System.panel_manager.global_pocket_money = Currency_System.pocket_money
    Button_System.panel_manager.current_stage = monster_manager.stage

    if Button_System.panel_manager.kitchen_guide_system:
        Button_System.panel_manager.kitchen_guide_system.guide_manager.update_progress("stage_reached", monster_manager.stage)

    if getattr(Button_System.panel_manager, 'wants_to_prestige', False):
        success, new_monster = Currency_System.trigger_prestige(monster_manager)
        if success:
            # ✅ Update the current_monster reference
            current_monster = new_monster
            current_monster.rect.x = MIDDLE_CENTER_X - MONSTER_SIZE // 2
            current_monster.rect.y = 275

            # ✅ Force HP to max
            current_monster.hp = current_monster.max_hp
            Button_System.panel_manager.active_panel = None
        Button_System.panel_manager.wants_to_prestige = False

    # ========= Auto Save ==========
    if time.time() - last_auto_save >= auto_save_interval:
        inventory_state, shop_state, pet_data, guide_data = Button_System.panel_manager.get_save_data()
        upgrade_level = 0
        if Button_System.panel_manager.player_upgrade_system:
            upgrade_level = Button_System.panel_manager.player_upgrade_system.level
        
        # Save player upgrade data
        player_upgrade_save_data = {}
        if Button_System.panel_manager.player_upgrade_system:
            pug = Button_System.panel_manager.player_upgrade_system
            player_upgrade_save_data = {
                "level": pug.level,
                "current_cost": pug.current_cost,
                "spicy_level": pug.spicy_level,
                "spicy_cost": pug.spicy_cost,
                "spicy_damage_boost": pug.spicy_damage_boost,
                "spicy_unlocked": pug.spicy_unlocked,
                "crispy_level": pug.crispy_level,
                "crispy_cost": pug.crispy_cost,
                "crispy_crit_damage": pug.crispy_crit_damage,
                "crispy_crit_chance": pug.crispy_crit_chance,
                "crispy_unlocked": pug.crispy_unlocked,
                "crit_dmg_level": pug.crit_dmg_level,
                "crit_dmg_cost": pug.crit_dmg_cost,
                "crit_dmg_bonus": pug.crit_dmg_bonus,
                "crit_chance_level": pug.crit_chance_level,
                "crit_chance_cost": pug.crit_chance_cost,
                "crit_chance_bonus": pug.crit_chance_bonus,
                "mana_cap_level": pug.mana_cap_level,
                "mana_cap_cost": pug.mana_cap_cost,
                "mana_cap_bonus": pug.mana_cap_bonus,
                "mana_regen_level": pug.mana_regen_level,
                "mana_regen_cost": pug.mana_regen_cost,
                "mana_regen_bonus": pug.mana_regen_bonus
            }
        
        # Save companion data
        companion_save_data = []
        if Button_System.panel_manager.player_upgrade_system:
            for comp in Button_System.panel_manager.player_upgrade_system.companions:
                companion_save_data.append({
                    "name": comp.name,
                    "level": comp.level,
                    "current_cost": comp.current_cost,
                    "base_cost": comp.base_cost,
                    "base_damage": comp.base_damage
                })
        
        ability_save_data = {}
        if player_upgrade_system.spicy_unlocked:
            ability_save_data["SpicySurge"] = {
                "active": damage_boost.active,
                "cooldown": damage_boost.cooldown,
                "start_time": damage_boost.start_time if damage_boost.active else 0,
                "cooldown_start": damage_boost.cooldown_start if damage_boost.cooldown else 0,
                "duration": damage_boost.duration,
                "cooldown_time": damage_boost.cooldown_time
            }
        if player_upgrade_system.crispy_unlocked:
            ability_save_data["CrispyPrecision"] = {
                "active": crispy_precision.active,
                "cooldown": crispy_precision.cooldown,
                "start_time": crispy_precision.start_time if crispy_precision.active else 0,
                "cooldown_start": crispy_precision.cooldown_start if crispy_precision.cooldown else 0,
                "duration": crispy_precision.duration,
                "cooldown_time": crispy_precision.cooldown_time
            }
        
        boost_data = boost_indicator.get_save_data()

        # Get boss timer data before saving
        is_boss = (monster_manager.progression_index % 10 == 9)
        boss_timer_active = current_monster.boss_timer_active if is_boss else False
        boss_timer_start = current_monster.boss_timer_start if is_boss else 0

        AFK_System.afk_system.save_game_data(
            pocket_money=Currency_System.pocket_money,
            monster_hp=current_monster.hp,
            monster_max_hp=current_monster.max_hp,
            monster_name=current_monster.name,
            monster_color=current_monster.color,
            progression_index=monster_manager.progression_index,
            stage=monster_manager.stage,
            inventory_items=inventory_state,
            shop_items_state=shop_state,
            pet_data=pet_data,
            upgrade_level=upgrade_level,
            guide_data=guide_data,
            boost_data=boost_data,
            michelin_stars=Currency_System.michelin_stars,
            ability_data=ability_save_data,
            player_upgrade_data=player_upgrade_save_data,
            companion_data=companion_save_data,
            boss_timer_active=boss_timer_active,      
            boss_timer_start=boss_timer_start
        )
        AFK_System.afk_system.update_save_time()
        Equipment_System.save_equipment()
        last_auto_save = time.time()

    # ========== Draw ==========
    window.fill((227, 227, 227))
    window.blit(stats_panel_bg, (LEFT_AREA_X, 0))
    
    # --- DRAW LIVE STATS PANEL (LEFT AREA) ---
    overlay_y = 100
    overlay_height = WINDOW_HEIGHT - overlay_y - 20
    
    # 1. Softer Overlay with Rounded Corners
    # Create a surface for the dark overlay that supports alpha
    overlay = pg.Surface((LEFT_WIDTH - 20, overlay_height), pg.SRCALPHA)
    # Use Pygame's built-in drawing on the transparent surface to get rounded corners
    pg.draw.rect(overlay, (25, 25, 35, 220), (0, 0, LEFT_WIDTH - 20, overlay_height), border_radius=12)
    window.blit(overlay, (LEFT_AREA_X + 10, overlay_y))
    
    # 2. Sleek Inner Border
    pg.draw.rect(window, (100, 100, 120), (LEFT_AREA_X + 10, overlay_y, LEFT_WIDTH - 20, overlay_height), 2, border_radius=12)
    
    # IDEALLY: Replace "courier" with a custom font file: pg.font.Font("Fonts/MyGameFont.ttf", size)
    font_section = pg.font.SysFont("courier", 20, bold=True)
    font_main_stat = pg.font.SysFont("courier", 22, bold=True) # Bigger for total output
    font_sub_stat = pg.font.SysFont("courier", 15, bold=True)  # Smaller for breakdown
    
    stats_y = 120
    
    # Calculate Live Stats
    raw_base = getattr(Equipment_System, "base_damage", Click_Damage_Feature.damage_per_click)
    eq_multi = float(Equipment_System.total_damage_multiplier)
    
    upgrade_lvl = 0
    if Button_System.panel_manager.player_upgrade_system:
        upgrade_lvl = Button_System.panel_manager.player_upgrade_system.level
        
    base_calc = (raw_base * eq_multi) + upgrade_lvl
    if upgrade_lvl > 0 and upgrade_lvl % 50 == 0:
        base_calc *= 1.2
        
    ability_multi = damage_boost.get_multiplier()
    prestige_multi = Currency_System.get_prestige_multiplier()
    
    final_click_dmg = int(base_calc * ability_multi * prestige_multi)
    
    pet_base = 0
    pet_sys = Button_System.panel_manager.pet_system
    if pet_sys:
        pet_base = pet_sys.get_total_damage()
        
    final_pet_dmg = int(pet_base * ability_multi * prestige_multi)
    
    # Use getter functions to get current crit values
    base_crit_c = Click_Damage_Feature.get_crit_chance()
    base_crit_m = Click_Damage_Feature.get_crit_multiplier()
    extra_crit_c, extra_crit_m = crispy_precision.get_crit_bonus()

    total_crit_c = base_crit_c + extra_crit_c
    total_crit_m = base_crit_m * extra_crit_m

    # Helper function: Draw text with a subtle drop shadow
    def draw_text_with_shadow(text, font, color, x, y):
        shadow = font.render(text, True, (15, 15, 20)) # Dark shadow
        main_text = font.render(text, True, color)
        window.blit(shadow, (x + 2, y + 2)) # Offset shadow by 2 pixels
        window.blit(main_text, (x, y))
        return main_text.get_width()

    # Helper function: Clean Underline Headers instead of bulky boxes
    def draw_sleek_header(title, y):
        draw_text_with_shadow(title, font_section, (255, 220, 100), LEFT_AREA_X + 25, y)
        # Draw a sleek fade-out line under the text
        pg.draw.line(window, (100, 100, 120), (LEFT_AREA_X + 25, y + 25), (LEFT_AREA_X + LEFT_WIDTH - 25, y + 25), 2)
        return y + 35

    # Helper function for Main Stats (Bigger, punchier)
    def draw_main_stat(label, value, color, y_offset):
        draw_text_with_shadow(label, font_sub_stat, (200, 200, 210), LEFT_AREA_X + 25, y_offset + 4)
        
        val_surf = font_main_stat.render(str(value), True, color)
        val_x = LEFT_AREA_X + LEFT_WIDTH - val_surf.get_width() - 25
        draw_text_with_shadow(str(value), font_main_stat, color, val_x, y_offset)
        return y_offset + 30

    # Helper function for Sub Stats (Smaller, subdued)
    def draw_sub_stat(label, value, color, y_offset):
        draw_text_with_shadow(label, font_sub_stat, (160, 160, 170), LEFT_AREA_X + 25, y_offset)
        
        val_surf = font_sub_stat.render(str(value), True, color)
        val_x = LEFT_AREA_X + LEFT_WIDTH - val_surf.get_width() - 25
        draw_text_with_shadow(str(value), font_sub_stat, color, val_x, y_offset)
        return y_offset + 22

    # --- SECTION 1: DAMAGE OUTPUT ---
    stats_y = draw_sleek_header("COMBAT POWER", stats_y)
    stats_y = draw_main_stat("Click DMG", Currency_System.format_money(final_click_dmg), (255, 100, 100), stats_y)
    stats_y = draw_main_stat("Pet DMG", Currency_System.format_money(final_pet_dmg), (100, 255, 100), stats_y)
    stats_y += 15
    
    # --- SECTION 2: BASE BREAKDOWN ---
    stats_y = draw_sleek_header("BASE STATS", stats_y)
    stats_y = draw_sub_stat("Weapon Multi", f"x{Currency_System.format_money(eq_multi)}", (200, 200, 200), stats_y)
    stats_y = draw_sub_stat("Upgrade Added", f"+{upgrade_lvl}", (200, 200, 200), stats_y)
    stats_y = draw_sub_stat("Pet Base", Currency_System.format_money(pet_base), (200, 200, 200), stats_y)
    stats_y += 15
    
    # --- SECTION 3: MULTIPLIERS & CRITS ---
    stats_y = draw_sleek_header("MULTIPLIERS", stats_y)
    stats_y = draw_sub_stat("Prestige Multi", f"x{(prestige_multi)}", (255, 215, 0), stats_y)
    stats_y = draw_sub_stat("  1 Michelin Star =", "+0.1x", (180, 180, 180), stats_y)
    stats_y = draw_sub_stat("Ability Multi", f"x{ability_multi:.2f}", (255, 150, 50), stats_y)
    stats_y = draw_sub_stat("Crit Chance", f"{total_crit_c * 100:.1f}%", (150, 200, 255), stats_y)
    stats_y = draw_sub_stat("Crit Damage", f"{total_crit_m * 100:.1f}%", (150, 200, 255), stats_y)    
    window.blit(get_current_background(monster_manager.stage), (MIDDLE_AREA_X, 0))

    # --- SECTION 4: MANA SYSTEM ---
    stats_y += 15
    stats_y = draw_sleek_header("MANA SYSTEM", stats_y)
    stats_y = draw_sub_stat("Current Mana", f"{int(mana_system.current_mana)} / {mana_system.max_mana}", (0, 255, 255), stats_y)
    stats_y = draw_sub_stat("Mana Regen", f"+{mana_system.regen_rate:.1f}/sec", (0, 200, 200), stats_y)
    
    boost_indicator.draw(window)

    pg.draw.line(window, (0, 0, 0), (MIDDLE_AREA_X, 0), (MIDDLE_AREA_X, WINDOW_HEIGHT), 3)
    pg.draw.line(window, (0, 0, 0), (RIGHT_AREA_X, 0), (RIGHT_AREA_X, WINDOW_HEIGHT), 3)

    font_counter = pg.font.SysFont(None, 36)
    counter_value = (monster_manager.progression_index % 10) + 1
    
    # Notice we removed the word "Monster" here!
    counter_str = f" {counter_value}/10"
    
    counter_shadow = font_counter.render(counter_str, True, (0, 0, 0))
    counter_surface = font_counter.render(counter_str, True, (255, 255, 255))
    
    # Calculate width to keep the icon and text perfectly centered as a group
    text_width = counter_surface.get_width()
    icon_width = hud_monster_icon.get_width() if hud_monster_icon else 0
    total_width = icon_width + text_width
    
    start_x = MIDDLE_CENTER_X - (total_width // 2)
    
    # 1. Draw the Alien Icon
    if hud_monster_icon:
        icon_rect = hud_monster_icon.get_rect(midleft=(start_x, 120))
        window.blit(hud_monster_icon, icon_rect)
        text_start_x = icon_rect.right
    else:
        text_start_x = start_x
        
    # 2. Draw the Text (Shadow + Main)
    shadow_rect = counter_shadow.get_rect(midleft=(text_start_x + 2, 120 + 2))
    window.blit(counter_shadow, shadow_rect)
    
    text_rect = counter_surface.get_rect(midleft=(text_start_x, 120))
    window.blit(counter_surface, text_rect)

    font_stage = pg.font.SysFont(None, 48, bold=True)
    stage_str = f"Stage {monster_manager.stage}"
    
    # 3. Draw Stage Shadow (Black, offset by +2 pixels)
    stage_shadow = font_stage.render(stage_str, True, (0, 0, 0))
    stage_shadow_rect = stage_shadow.get_rect(center=(MIDDLE_CENTER_X + 2, 70 + 2))
    window.blit(stage_shadow, stage_shadow_rect)
    
    # 4. Draw Main Stage Text (White)
    stage_surface = font_stage.render(stage_str, True, (255, 255, 255))
    stage_rect = stage_surface.get_rect(center=(MIDDLE_CENTER_X, 70))
    window.blit(stage_surface, stage_rect)

    current_monster.draw(window)

    pet_system = Button_System.panel_manager.pet_system
    if pet_system:
        equipped_pets = pet_system.get_equipped_pets()
        pet_size = 60
        pet_spacing = 15
        start_x = MIDDLE_CENTER_X - (len(equipped_pets) * pet_size + (len(equipped_pets) - 1) * pet_spacing) // 2
        pet_y = current_monster.rect.y + current_monster.rect.height + 20
        font_pet = pg.font.SysFont(None, 14)
        
        for idx, pet in enumerate(equipped_pets):
            pet_x = start_x + idx * (pet_size + pet_spacing)
            pet_rect = pg.Rect(pet_x, pet_y, pet_size, pet_size)
            
            # Try to get the cached icon from Pet_System
            pet_icon = pet_system._get_item_icon(pet.name)
            
            if pet_icon:
                # Scale up to 60x60 so the sprite pops without the background box
                display_icon = pg.transform.scale(pet_icon, (60, 60))
                icon_rect = display_icon.get_rect(center=pet_rect.center)
                
                # Blit just the image directly to the window (no background!)
                window.blit(display_icon, icon_rect)
            else:
                # Fallback just in case an image is missing
                name_text = font_pet.render(pet.name[:6]+"..", True, (0, 0, 0))
                name_rect = name_text.get_rect(center=pet_rect.center)
                window.blit(name_text, name_rect)
                
    # Always draw companions around the monster
    if Button_System.panel_manager.player_upgrade_system:
       Button_System.panel_manager.player_upgrade_system.draw_companions(window)

    Currency_System.draw_ui(window)

    # ========== DRAW PRESTIGE INDICATOR ==========
    if player_upgrade_system:
        current_stars = Currency_System.michelin_stars
        current_stage = monster_manager.stage
        
        # Get prestige progress
        progress, next_requirement = Currency_System.get_prestige_progress(current_stage, current_stars)

        # DEBUG: Print the status
        print(f"[DEBUG] Prestige check - Stage: {current_stage}, Stars: {current_stars}, Next Req: {next_requirement}, Progress: {progress}%")
        
        if next_requirement is not None:
            # Draw prestige indicator in top-right corner
            x = RIGHT_AREA_X + 10
            y = 10
            width = 160
            height = 70
            
            # Store the rect for click detection
            prestige_button_rect = pg.Rect(x, y, width, height)
            
            # Background - change color when ready to prestige
            if progress >= 100:
                bg_color = (0, 80, 0)  # Dark green when ready
            else:
                bg_color = (40, 40, 50)  # Normal dark
            
            pg.draw.rect(window, bg_color, prestige_button_rect)
            pg.draw.rect(window, (255, 215, 0), prestige_button_rect, 2)
            
            # Title
            font = pg.font.SysFont(None, 14)
            title = font.render(f"★ PRESTIGE ★", True, (255, 215, 0))
            window.blit(title, (x + 10, y + 3))
            
            # Progress bar
            bar_x = x + 10
            bar_y = y + 25
            bar_width = width - 20
            bar_height = 14
            
            pg.draw.rect(window, (60, 60, 60), (bar_x, bar_y, bar_width, bar_height))
            
            # Color based on progress
            if progress >= 100:
                bar_color = (0, 255, 0)  # Green - ready to prestige
                bar_text = "CLICK TO PRESTIGE!"
            elif progress >= 75:
                bar_color = (255, 255, 0)  # Yellow - close
                bar_text = f"Stage {current_stage}/{next_requirement}"
            elif progress >= 50:
                bar_color = (255, 165, 0)  # Orange - halfway
                bar_text = f"Stage {current_stage}/{next_requirement}"
            else:
                bar_color = (255, 100, 100)  # Red - far away
                bar_text = f"Stage {current_stage}/{next_requirement}"
            
            pg.draw.rect(window, bar_color, (bar_x, bar_y, int(bar_width * (progress / 100)), bar_height))
            
            # Text
            small_font = pg.font.SysFont(None, 12)
            text = small_font.render(bar_text, True, (0, 0, 0) if progress >= 100 else (255, 255, 255))
            window.blit(text, (bar_x + 5, bar_y + 2))
            
            # Stars indicator
            stars_text = small_font.render(f"★ x{current_stars}", True, (255, 215, 0))
            window.blit(stars_text, (x + 10, y + 48))
            
            # Next prestige info
            next_req = Currency_System.get_next_prestige_requirement(current_stars)
            if next_req:
                next_text = small_font.render(f"Next: Stage {next_req}", True, (200, 200, 200))
                window.blit(next_text, (x + 70, y + 48))
        else:
            # Max prestige reached
            x = RIGHT_AREA_X + 10
            y = 10
            width = 160
            height = 40
            
            prestige_button_rect = pg.Rect(x, y, width, height)
            
            pg.draw.rect(window, (40, 40, 50), prestige_button_rect)
            pg.draw.rect(window, (255, 215, 0), prestige_button_rect, 2)
            
            font = pg.font.SysFont(None, 16)
            text = font.render("★ MAX PRESTIGE ★", True, (255, 215, 0))
            window.blit(text, text.get_rect(center=(x + width//2, y + height//2)))

    for dt in damage_texts:
        dt.draw(window)
    for anim in attack_animations:
        anim.draw(window)
    for button in Button_System.buttons:
        button.draw(window)

    Button_System.panel_manager.draw(window)
    
    # Draw abilities only if unlocked
    if player_upgrade_system.spicy_unlocked:
       damage_boost.draw(window, mana_system)
    if player_upgrade_system.crispy_unlocked:
       crispy_precision.draw(window, mana_system)

    # ========== DRAW MANA BAR ABOVE ABILITY BUTTONS ==========
    # Update mana system
    mana_system.update()
    
    # Fixed positions from where abilities are created
    SPICY_X = LEFT_WIDTH + 60      # damage_boost.x
    CRISPY_X = SPICY_X + 100       # crispy_precision.x (damage_boost.x + 100)
    ABILITY_Y = WINDOW_HEIGHT - 120
    ABILITY_RADIUS = 35
    
    mana_bar_height = 16
    
    # Center the mana bar between both ability positions
    left_x = SPICY_X - ABILITY_RADIUS - 10
    right_x = CRISPY_X + ABILITY_RADIUS + 10
    mana_bar_width = right_x - left_x
    mana_bar_x = left_x
    mana_bar_y = ABILITY_Y - ABILITY_RADIUS - mana_bar_height - 20
    
    mana_rect = pg.Rect(mana_bar_x, mana_bar_y, mana_bar_width, mana_bar_height)

    # Background
    pg.draw.rect(window, (40, 40, 40), mana_rect)

    # Filled portion
    mana_ratio = mana_system.current_mana / mana_system.max_mana
    fill_rect = pg.Rect(mana_rect.x, mana_rect.y, int(mana_rect.width * mana_ratio), mana_rect.height)
    pg.draw.rect(window, (0, 255, 255), fill_rect)
    
    # Border
    pg.draw.rect(window, (200, 200, 200), mana_rect, 2)

    # Text
    font = pg.font.SysFont(None, 20)
    text = font.render(f"{int(mana_system.current_mana)}/{mana_system.max_mana}", True, (0, 0, 0))
    text_rect = text.get_rect(center=mana_rect.center)
    window.blit(text, text_rect)

    # Label
    label = font.render("MANA", True, (200, 200, 200))
    label_rect = label.get_rect(center=(mana_rect.centerx, mana_rect.y - 15))
    window.blit(label, label_rect)

    pg.display.update()

pg.quit()


# ==========================================
# References
# ==========================================
# 1. ABILITY TO CLICK TO DEAL DAMAGE (Click_Damage_Feature.py)
#    Source code: Copilot
#    Link: None
#
# 2. Drawer system (Button_System.py)
#    Source code: Deepseek
#    Link: None
#
# 3. Shop system's UI system (Shop_System.py)
#    Source code: Deepseek
#    Link: None
#
# 4. Code for fixing bug (AFK_System.py)
#    Source code: Deepseek
#    Link: None
#
# 5. Code for decorational circle (Inventory_System.py)
#    Source code: Deepseek
#    Link: None
#
# 6. UI reedit (Every file before window size=1300x750)
#    Source code: Deepseek
#    Link: None
#
# 7. Pet system (Pet_System.py)
#    Source code: Deepseek
#    Link: None
#
# 8. Kitchen Guide system (KitchenGuide_System.py)
#    Source code: Deepseek
#    Link: None
#
# 9. Animation Tutorial (AttackOnFoodTitan.py)
#    Source code: Deepseek
#    Link: None
#
# 10. Loading screen implementation (AttackOnFoodTitan.py)
#     Source code: Deepseek
#     Link: None
#
# 11. Boss Timer (AttackOnFoodTitan.py, Click_Damage_Feature.py)
#     Source code: Copilot
#     Link: None
#
# 12. Monster HP Scaling (Click_Damage_System.py)
#     Source code: Copilot
#     Link: None
#
# 13. Base Damage Upgrade scaling (Player_Upgrade_system.py) 
#     Source: Copilot
#     Link: None
#
# 14. Other Upgrade Scaling (Player_Upgrade_System.py, Abilities.py)
#     Source: DeepSeek
#     Link: None
#
# 15. Scrollbar for easier navigation in Player Upgrade Panel (Player_Upgrade_System.py)
#     Source: Copilot
#     Link: None
#
# 16. Companion upgrade scaling (Player_Upgrade_System.py)
#     Source: Copilot
#     Link: None
#
# 17. Prestige requirement (Currency_System.py)
#     Source: DeepSeek
#     Link: None
#
# 18. Critical Hit Chance and Damage (Click_Damage_Feature.py)
#     Source: Copilot
#     Link: None
#
# 19. Mana Bar and Mana Point System (Abilities.py)
#     Source: Copilot
#     Link: None
#
# 20. Help received when fixing bug 
#     Source: Copilot and DeepSeek
#     Link: None
#
# 21. Companions (Player_Upgrade_System)
#     Source: Copilot
#     Link: None
#
# ==========================================
# Contributors
# ==========================================
# Tan Zhe Xi (TZX)
#   - TZX_1. Prestige Gimmick (Handled by AttackOnFoodTitan.py, Iventory_System.py, Pet_System.py,Currency_System.py, Button_System.py, Player_Upgrade_System.py)
#   - TZX_2. Player Data Design (Handled by Player_Upgrade_System.py, AttackOnFoodTitan.py, Abilities.py)
#   - TZX_3. ABILITY TO CLICK TO DEAL DAMAGE (Handled by Click_Damage_Feature.py)
#   - TZX_4. Abilities/Power Up (Abilities.py, AttackOnFoodTitan.py, Player_Upgrade_System.py, AFK_System.py)
#   - TZX_5. Companion Data Design (Player_Upgrade_System.py, AttackOnFoodTitan.py, AFK_System.py)
#   - TZX_6. Scaling (Player_Upgrade_System.py, Click_Damage_Feature.py, Abilities.py)
#
# Eng Kai Hin (EKH)
#   - EKH_1. BUTTON INTERACTION SYSTEM
#     (Handled by Button_System.py, which contains button and drawer system)
#   - EKH_2. AFK SYSTEM
#     (Handled by AFK_System.py, which contains AFK system and data saving system that save player's data)
#   - EKH_3. SHOP SYSTEM
#     (Handled by Shop_System.py and Inventory_System, One for buying item one for storing item)
#   - EKH_4. CLEAR WHEN PRESTIGE SYSTEM
#
# Chen Lik Shen (CLS)
#   - CLS_1. GAME UI & SOUND EFFECT
#     (Handled by Currency_System.py)
#   - CLS_2. GAIN & LOST OF EQUIPMENT & CURRENCY SYSTEM
#     (Handled by Currency_System.py)
#   - CLS_3. CRAFTING SYSTEM
#   - CLS_4. SYSTEM TO ADD NEW EQUIPMENT, CHARACTER, AND RECIPES ACCORDING TO EACH PRESTIGE LEVELS