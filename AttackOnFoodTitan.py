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




# ========== Show Loading Screen ==========
def show_loading_screen(screen, message, progress=0):
    """Shows a loading screen with a message and progress bar."""
    screen.fill((30, 30, 40))
    font = pg.font.SysFont(None, 48)
    font_small = pg.font.SysFont(None, 24)
    
    # Loading text
    text = font.render("Loading...", True, (255, 255, 255))
    text_rect = text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 50))
    screen.blit(text, text_rect)
    
    # Message text
    msg_text = font_small.render(message, True, (200, 200, 200))
    msg_rect = msg_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 20))
    screen.blit(msg_text, msg_rect)
    
    # Progress bar
    bar_width = 400
    bar_height = 20
    bar_x = (WINDOW_WIDTH - bar_width) // 2
    bar_y = WINDOW_HEIGHT // 2 + 60
    
    pg.draw.rect(screen, (60, 60, 80), (bar_x, bar_y, bar_width, bar_height))
    pg.draw.rect(screen, (100, 200, 100), (bar_x, bar_y, int(bar_width * progress), bar_height))
    pg.draw.rect(screen, (200, 200, 200), (bar_x, bar_y, bar_width, bar_height), 2)
    
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
        self.frames = frames
        self.current_frame = 0
        self.animation_speed = 0.08
        self.time_since_last_frame = 0
        self.is_active = True
        self.scale = scale
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.alpha = 255

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
        frame = self.frames[self.current_frame]
        
        if self.scale != 1.0:
            new_width = int(frame.get_width() * self.scale)
            new_height = int(frame.get_height() * self.scale)
            frame = pg.transform.scale(frame, (new_width, new_height))
        
        frame.set_alpha(self.alpha)
        
        # Calculate draw position with offset
        draw_x = self.x - frame.get_width() // 2 + self.offset_x
        draw_y = self.y - frame.get_height() // 2 + self.offset_y
        screen.blit(frame, (draw_x, draw_y))

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
afk_earnings, saved_monster_data, saved_money, saved_progression_index, saved_stage, saved_inventory, saved_shop_state, saved_pet_data, saved_upgrade_level, saved_guide_data, saved_boost_data = AFK_System.afk_system.load_and_calculate_afk_rewards()

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
    current_monster.hp = saved_monster_data["hp"]
    current_monster.rect.x = MIDDLE_CENTER_X - MONSTER_SIZE // 2
    current_monster.rect.y = 275
    monster_manager.current_monster = current_monster
else:
    current_monster = monster_manager.current_monster
    current_monster.rect.x = MIDDLE_CENTER_X - MONSTER_SIZE // 2
    current_monster.rect.y = 275

show_loading_screen(window, "Initializing systems...", 0.9)

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

damage_boost = SpicySurge(x=LEFT_WIDTH + 5 + 35, y=current_monster.rect.y + current_monster.rect.height + 90, radius=35)
crispy_precision = CrispyPrecision(x=damage_boost.x + 100, y=damage_boost.y, radius=35)

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

# ✅ Link into PanelManager so auto‑attack and events can use it
Button_System.panel_manager.player_upgrade_system = player_upgrade_system

# ✅ Link abilities before events fire
player_upgrade_system.spicy_ability = damage_boost
player_upgrade_system.crispy_ability = crispy_precision

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

show_loading_screen(window, "Starting game...", 1.0)

# Finding exact position by clicking anywhere you want
#def debug_get_mouse_pos():
    #if pg.mouse.get_pressed()[0]:  # left click
        #print("Mouse clicked at:", pg.mouse.get_pos())

# ========== Main Loop ========== #
while IsRunning:
    dt_ms = clock.tick(60)
    dt_sec = dt_ms / 1000.0
    
    #debug_get_mouse_pos() 
    
    boost_indicator.update()
    damage_boost.update()
    crispy_precision.update()

    for event in pg.event.get():
        if event.type == pg.USEREVENT + 1:
            play_next_music()

        if event.type == pg.QUIT:
            inventory_state, shop_state, pet_data, guide_data = Button_System.panel_manager.get_save_data()
            upgrade_level = 0
            if Button_System.panel_manager.player_upgrade_system:
                upgrade_level = Button_System.panel_manager.player_upgrade_system.level
            boost_data = boost_indicator.get_save_data()
            
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
                boost_data=boost_data
            )
            IsRunning = False
            break

        elif event.type == pg.KEYDOWN:
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
            elif event.key == pg.K_p:
                Currency_System.trigger_prestige(monster_manager)

        elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            if current_monster.rect.collidepoint(event.pos):
                if attack_titan_sound:
                    attack_titan_sound.play()

                extra_chance, extra_multi = crispy_precision.get_crit_bonus()
                base_damage = getattr(Equipment_System, "base_damage", Click_Damage_Feature.damage_per_click)
                final_damage, is_critical = calculate_damage(base_damage, extra_chance, extra_multi)
                final_damage = int(final_damage * damage_boost.get_multiplier() * Currency_System.get_prestige_multiplier())
                current_monster.take_damage(final_damage)

                popup_x = current_monster.rect.x + random.randint(20, current_monster.rect.width - 20)
                popup_y = current_monster.rect.y + random.randint(20, current_monster.rect.height - 20)
                damage_texts.append(DamageText(str(final_damage), (popup_x, popup_y), is_critical))

                # Track if player got the final hit
                if current_monster.is_defeated() and not hasattr(current_monster, "last_hit_by"):
                    current_monster.last_hit_by = "player"

        damage_boost.handle_event(event)
        crispy_precision.handle_event(event)

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
    if not data_restored and Button_System.panel_manager.active_panel in ["Shop", "Inventory", "Pet"]:
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
        if Currency_System.trigger_prestige(monster_manager):
            Button_System.panel_manager.active_panel = None
        Button_System.panel_manager.wants_to_prestige = False

    # ========= Auto Save ==========
    if time.time() - last_auto_save >= auto_save_interval:
        inventory_state, shop_state, pet_data, guide_data = Button_System.panel_manager.get_save_data()
        upgrade_level = 0
        if Button_System.panel_manager.player_upgrade_system:
            upgrade_level = Button_System.panel_manager.player_upgrade_system.level
        boost_data = boost_indicator.get_save_data()
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
            boost_data=boost_data
        )
        AFK_System.afk_system.update_save_time()
        Equipment_System.save_equipment()
        last_auto_save = time.time()

    # ========== Draw ==========
    window.fill((227, 227, 227))
    window.blit(stats_panel_bg, (LEFT_AREA_X, 0))
    window.blit(get_current_background(monster_manager.stage), (MIDDLE_AREA_X, 0))
    
    boost_indicator.draw(window)

    pg.draw.line(window, (0, 0, 0), (MIDDLE_AREA_X, 0), (MIDDLE_AREA_X, WINDOW_HEIGHT), 3)
    pg.draw.line(window, (0, 0, 0), (RIGHT_AREA_X, 0), (RIGHT_AREA_X, WINDOW_HEIGHT), 3)

    font_counter = pg.font.SysFont(None, 36)
    counter_value = (monster_manager.progression_index % 10) + 1
    counter_surface = font_counter.render(f"Monster {counter_value}/10", True, (0, 0, 0))
    counter_rect = counter_surface.get_rect(center=(MIDDLE_CENTER_X, 120))
    window.blit(counter_surface, counter_rect)

    font_stage = pg.font.SysFont(None, 48, bold=True)
    stage_surface = font_stage.render(f"Stage {monster_manager.stage}", True, (0, 0, 0))
    stage_rect = stage_surface.get_rect(center=(MIDDLE_CENTER_X, 70))
    window.blit(stage_surface, stage_rect)

    current_monster.draw(window)

    # Always draw companions around the monster
    if Button_System.panel_manager.player_upgrade_system:
       Button_System.panel_manager.player_upgrade_system.draw_companions(window)

    Currency_System.draw_ui(window)

    for dt in damage_texts:
        dt.draw(window)
    for anim in attack_animations:
        anim.draw(window)
    for button in Button_System.buttons:
        button.draw(window)

    Button_System.panel_manager.draw(window)
    damage_boost.draw(window)
    crispy_precision.draw(window)

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
# ==========================================
# Contributors
# ==========================================
# Tan Zhe Xi (TZX)
#   - TZX_1. MINIGAME SYSTEM
#   - TZX_2. EQUIPMENT & DATA DESIGN
#   - TZX_3. ABILITY TO CLICK TO DEAL DAMAGE
#     (Handled by Click_Damage_Feature.py)
#   - TZX_4. ADJUSTING STATS ACCORDING TO PRESTIGE LEVELS
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