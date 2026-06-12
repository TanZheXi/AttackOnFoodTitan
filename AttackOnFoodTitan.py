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
from Abilities import SpicySurge, CrispyPrecision

class BoostIndicator: #(For Kitchen Guide Quest: x2 Currency Boost)
    def __init__(self, x, y, width, height):
        self.rect = pg.Rect(x, y, width, height)
        self.font = pg.font.SysFont(None, 16)
        self.font_small = pg.font.SysFont(None, 12)
        self.visible = False
        self.end_time = 0
        self.duration = 3 * 60 * 60  # 3 hours in seconds

    def activate(self, end_time):
        self.visible = True
        self.end_time = end_time
        print(f"[BOOST] x2 Currency Boost activated! Expires in 3 hours.")

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
            return {
                "visible": True,
                "end_time": self.end_time
            }
        return {"visible": False}

    def restore_save_data(self, data):
        if data and data.get("visible", False):
            self.visible = True
            self.end_time = data.get("end_time", 0)
            if time.time() >= self.end_time:
                self.visible = False
                print("[BOOST] Boost expired during offline time")
            else:
                print(f"[BOOST] Boost restored. Expires at {time.ctime(self.end_time)}")

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

LEFT_WIDTH = 300        # Stats section
MIDDLE_WIDTH = 550      # Monster UI section
RIGHT_WIDTH = WINDOW_WIDTH - LEFT_WIDTH - MIDDLE_WIDTH  # 450px, Player interaction section

LEFT_AREA_X = 0
MIDDLE_AREA_X = LEFT_WIDTH
RIGHT_AREA_X = LEFT_WIDTH + MIDDLE_WIDTH

MIDDLE_CENTER_X = MIDDLE_AREA_X + MIDDLE_WIDTH // 2

Currency_System.MIDDLE_CENTER_X = MIDDLE_CENTER_X

# ========== BACKGROUND SYSTEM ==========
# Background image list (in order corresponding to Stage 1-30, 31-60, 61-90, 91-120, 121-150)
BACKGROUNDS = [
    "bg_kitchen.png",   # Stage 1-30: Kitchen
    "bg_party.png",     # Stage 31-60: Party time
    "bg_bbq.png",       # Stage 61-90: BBQ outside house
    "bg_camping.png",   # Stage 91-120: Camping
    "bg_beach.png"      # Stage 121-150: Beach picnic
]

# Obtain the absolute path to the background images folder
background_folder = os.path.join(os.path.dirname(__file__), "Background")


# ===========================================

pg.init()
pg.mixer.init()
window = pg.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pg.display.set_caption("Attack On Food Titan")

# =================================================================

# ========== BACKGROUND MUSIC SYSTEM ==========
# BGM list
MUSIC_FILES = [
    "Opening1.MP3",
    "Opening2.MP3", 
    "Opening3.MP3"
]

# Obtain the BGM folder path
bgm_folder = os.path.join(os.path.dirname(__file__), "BGM")

# Build the complete music file paths
music_paths = []
for music_file in MUSIC_FILES:
    music_path = os.path.join(bgm_folder, music_file)
    music_paths.append(music_path)
    print(f"[BGM] Found: {music_file} at {music_path}")

# Current music index
current_music_index = 0

def play_next_music():
    """Play the next background music, looping"""
    global current_music_index
    try:
        # Stop current playback
        pg.mixer.music.stop()
        # Load and play the next song
        pg.mixer.music.load(music_paths[current_music_index])
        pg.mixer.music.play()
        print(f"[BGM] Now playing: {MUSIC_FILES[current_music_index]}")
        # Update index to the next song (looping)
        current_music_index = (current_music_index + 1) % len(music_paths)
    except Exception as e:
        print(f"[BGM] Error playing music: {e}")

def start_background_music():
    """Start playing the background music loop"""
    try:
        # Set the callback for when the music finishes playing
        pg.mixer.music.set_endevent(pg.USEREVENT + 1)
        # Play the first song
        play_next_music()
    except Exception as e:
        print(f"[BGM] Failed to start background music: {e}")

# Initialize the mixer (if not already initialized)
try:
    pg.mixer.init()
    print("[BGM] Mixer initialized")
except Exception as e:
    print(f"[BGM] Mixer init failed: {e}")

# Set the volume (0.0 to 1.0, 0.5 represents 50% volume)
pg.mixer.music.set_volume(0.5)

# Start playing the background music
start_background_music()
# ===========================================

# ========== SOUND EFFECTS ==========
# Monster defeated sound effect
titan_defeated_sound = None
try:
    sound_folder = os.path.join(os.path.dirname(__file__), "Sound_Effects")
    titan_defeated_path = os.path.join(sound_folder, "TitansDefeated.MP3")
    titan_defeated_sound = pg.mixer.Sound(titan_defeated_path)
    titan_defeated_sound.set_volume(0.6)  # Set volume to 60%
    print(f"[SOUND] Loaded: TitansDefeated.MP3")
except Exception as e:
    print(f"[SOUND] Warning: Could not load TitansDefeated.MP3 - {e}")
# ===================================

# ========== STATS PANEL BACKGROUND ==========
# Left side stats panel background image path
stats_panel_folder = os.path.join(os.path.dirname(__file__), "Background", "Stats_panel")
stats_panel_path = os.path.join(stats_panel_folder, "StatsPanel.png")

# Load stats panel background image
try:
    stats_panel_bg = pg.image.load(stats_panel_path).convert()
    # Scale to left area size (300 x 750)
    stats_panel_bg = pg.transform.scale(stats_panel_bg, (LEFT_WIDTH, WINDOW_HEIGHT))
    print(f"[STATS PANEL] Loaded: {stats_panel_path}")
except Exception as e:
    print(f"[STATS PANEL] Warning: Could not load background - {e}")
    # If image loading fails, create a gray placeholder background
    stats_panel_bg = pg.Surface((LEFT_WIDTH, WINDOW_HEIGHT))
    stats_panel_bg.fill((40, 40, 50))
# ===========================================

# Load background images and scale them to fit the middle area (550 x 750)
background_images = []
for bg_name in BACKGROUNDS:
    bg_path = os.path.join(background_folder, bg_name)
    print(f"[DEBUG] Looking for: {bg_path}")
    print(f"[DEBUG] File exists: {os.path.exists(bg_path)}")
    try:
        img = pg.image.load(bg_path).convert()
        # Scale to middle area size (550 x 750)
        img = pg.transform.scale(img, (MIDDLE_WIDTH, WINDOW_HEIGHT))
        background_images.append(img)
        print(f"[BACKGROUND] Loaded: {bg_name}")
    except Exception as e:
        print(f"[BACKGROUND] Warning: Could not load {bg_name} - {e}")
        # If image loading fails, create a gray placeholder background
        placeholder = pg.Surface((MIDDLE_WIDTH, WINDOW_HEIGHT))
        placeholder.fill((50, 50, 60))
        background_images.append(placeholder)

def get_background_index(stage):
    """According to stage, return the background image index (0-4, looping)"""
    # Stage 1~30: index 0, stage 31-60: index 1, ...
    # Change to 0-based index and determine which background to show based on stage
    return ((stage - 1) // 30) % 5

def get_current_background(stage):
    """According to stage, return the corresponding background image"""
    idx = get_background_index(stage)
    if idx < len(background_images):
        return background_images[idx]
    return background_images[0]  # Default to first background if something goes wrong
# =================================================================

# Setup clock
clock = pg.time.Clock()

# Load AFK rewards and saved game data (returns 11 values including boost_data)
afk_earnings, saved_monster_data, saved_money, saved_progression_index, saved_stage, saved_inventory, saved_shop_state, saved_pet_data, saved_upgrade_level, saved_guide_data, saved_boost_data = AFK_System.afk_system.load_and_calculate_afk_rewards()

# Load saved equipment data
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

IsRunning = True
last_auto_save = time.time()
auto_save_interval = 5

PET_ATTACK_INTERVAL = 1.0
last_pet_attack_time = time.time()

# Set data that will be restored
Button_System.panel_manager.pending_inventory = saved_inventory if saved_inventory else []
Button_System.panel_manager.pending_shop_state = saved_shop_state if saved_shop_state else []
Button_System.panel_manager.pending_pet_data = saved_pet_data if saved_pet_data else []
Button_System.panel_manager.pending_guide_data = saved_guide_data if saved_guide_data else {}
Button_System.panel_manager.pending_money = Currency_System.pocket_money

data_restored = False
damage_texts = []

# init Boost Indicator
boost_indicator = BoostIndicator(
    x=LEFT_AREA_X + 10,
    y=WINDOW_HEIGHT - 100,
    width=280,
    height=85
)

# Restore boost state from saved data
if saved_boost_data:
    boost_indicator.restore_save_data(saved_boost_data)

# Initialize abilities (positioned below monster, beside left partition line)
damage_boost = SpicySurge(
    x=LEFT_WIDTH + 5 + 35,
    y=current_monster.rect.y + current_monster.rect.height + 90,
    radius=35
)
crispy_precision = CrispyPrecision(
    x=damage_boost.x + 100,
    y=damage_boost.y,
    radius=35
)

def on_prestige_reset():
    if Button_System.panel_manager.shop_system:
        Button_System.panel_manager.shop_system.reset_shop()
    if Button_System.panel_manager.inventory_system:
        Button_System.panel_manager.inventory_system.reset_inventory()
    if Button_System.panel_manager.pet_system:
        Button_System.panel_manager.pet_system.reset_on_prestige()
        print("[PRESTIGE] Pets unequipped.")

    Equipment_System.lose_all_equipment()
    print("[PRESTIGE] Equipment reset")

    damage_texts.clear()

Currency_System.register_prestige_callback(on_prestige_reset)

# ========== Load Kitchen Guide System ==========
Button_System.panel_manager.kitchen_guide_system = KitchenGuideSystem(0, 0, 1, 1)
if saved_guide_data:
    Button_System.panel_manager.kitchen_guide_system.guide_manager.restore_save_data(saved_guide_data)

# ========== Set Kitchen Guide Callbacks ==========
# Equipment equip callback
Equipment_System.set_equip_callback(lambda: (
    Button_System.panel_manager.kitchen_guide_system.guide_manager.update_progress("equip_equipment", 1)
    if Button_System.panel_manager.kitchen_guide_system else None
))

# Enhance grant_reward to activate boost indicator
if Button_System.panel_manager.kitchen_guide_system:
    original_grant_reward = Button_System.panel_manager.kitchen_guide_system.guide_manager.grant_reward
    
    def enhanced_grant_reward(reward_type):
        original_grant_reward(reward_type)
        if reward_type == "boost":
            boost_indicator.activate(Button_System.panel_manager.kitchen_guide_system.guide_manager.boost_end_time)
    
    Button_System.panel_manager.kitchen_guide_system.guide_manager.grant_reward = enhanced_grant_reward
# ====================================================

# =========================
# Main Game Loop
# =========================
while IsRunning:
    dt_ms = clock.tick(60)   # frame delta in ms
    
    # Update boost indicator
    boost_indicator.update()
    
    damage_boost.update()
    crispy_precision.update()

    # -------------------------
    # Event Handling
    # -------------------------
    for event in pg.event.get():
        if event.type == pg.USEREVENT + 1: #Detect when a music track finishes and play the next one
            play_next_music()

        if event.type == pg.QUIT:
            inventory_state, shop_state, pet_data, guide_data = Button_System.panel_manager.get_save_data()
            upgrade_level = 0
            if Button_System.panel_manager.player_upgrade_system:
                upgrade_level = Button_System.panel_manager.player_upgrade_system.level
            
            # Get boost save data
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
                # Sync between Equipment_System and Inventory_System when gaining new equipment
                Equipment_System.gain_equipment("OP WEAPON")
                Button_System.panel_manager.add_to_inventory("OP WEAPON")
                print("[DEBUG] Gained OP WEAPON and added to inventory")
            elif event.key == pg.K_e:
                selected_item = Button_System.panel_manager.get_selected_inventory_item()
                if selected_item and selected_item in Equipment_System.equipment_database:
                    Equipment_System.equip_equipment(selected_item)
                    print(f"[DEBUG] Equipped {selected_item}")
                else:
                    print("[DEBUG] No valid item selected to equip")
            elif event.key == pg.K_u:
                Equipment_System.unequip_equipment("weapon")
            # Press 'C' to craft the item (Consumes scraps)
            elif event.key == pg.K_c:
                if Equipment_System.craft_item("Golden Spatula"):
                    Button_System.panel_manager.add_to_inventory("Golden Spatula")
                    print("[DEBUG] Crafted Golden Spatula and added to inventory")

            elif event.key == pg.K_n:
                monster_manager.stage += 1
                monster_manager.progression_index = (monster_manager.stage - 1) * 10
                monster_manager.current_monster = monster_manager.spawn_monster()
                print(f"[DEV CHEAT] Skipped to Stage {monster_manager.stage}")

            elif event.key == pg.K_p:
                success = Currency_System.trigger_prestige(monster_manager)
                if not success:
                    print("[DEV WARNING] Prestige failed. Are you at least Stage 10?")

        # --- Click event handling ---
        elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            if current_monster.rect.collidepoint(event.pos):
                # Get crit bonuses from Crispy Precision ability
                extra_chance, extra_multi = crispy_precision.get_crit_bonus()

                # Get base damage from Equipment_System or default
                base_damage = getattr(Equipment_System, "base_damage", Click_Damage_Feature.damage_per_click)

                # Calculate damage using the imported function
                final_damage, is_critical = calculate_damage(base_damage, extra_chance, extra_multi)

                # Apply ability multipliers (Spicy Surge) and prestige multiplier
                final_damage = int(final_damage * damage_boost.get_multiplier() * Currency_System.get_prestige_multiplier())

                # Apply damage to monster
                current_monster.take_damage(final_damage)

                # Create floating damage text
                popup_x = current_monster.rect.x + random.randint(20, max(20, current_monster.rect.width - 40))
                popup_y = current_monster.rect.y + random.randint(20, max(20, current_monster.rect.height - 40))
                damage_texts.append(DamageText(str(final_damage), (popup_x, popup_y), is_critical))

                # Check if monster is defeated
                if current_monster.is_defeated():
                    Currency_System.update_economy(current_monster.hp, monster_manager.progression_index + 1)

                    # Play titan defeated sound effect
                    if titan_defeated_sound:
                        titan_defeated_sound.play()

                    # Update Kitchen Guide progress (Quest 1: Cook Food Titan)
                    if Button_System.panel_manager.kitchen_guide_system:
                        Button_System.panel_manager.kitchen_guide_system.guide_manager.update_progress("defeat_titan", 1)

                    monster_manager.next_monster()
                    current_monster = monster_manager.current_monster
                    current_monster.rect.x = MIDDLE_CENTER_X - MONSTER_SIZE // 2
                    current_monster.rect.y = 275

        # Ability events
        damage_boost.handle_event(event)
        crispy_precision.handle_event(event)

        # UI Event
        Button_System.panel_manager.monster_manager = monster_manager
        Button_System.panel_manager.handle_event(event)
        for button in Button_System.buttons:
            button.handle_event(event)

    # ========== PET AUTO ATTACK ==========
    current_time = time.time()
    if current_time - last_pet_attack_time >= PET_ATTACK_INTERVAL:
        pet_system = Button_System.panel_manager.pet_system
        if pet_system:
            base_pet_damage = pet_system.get_total_damage()
            if base_pet_damage > 0 and current_monster.hp > 0:
                # Get crit bonuses from Crispy Precision ability
                extra_chance, extra_multi = crispy_precision.get_crit_bonus()

                # Calculate pet damage using the imported function
                pet_damage, is_critical = calculate_damage(base_pet_damage, extra_chance, extra_multi)

                # Apply ability multipliers and prestige multiplier
                final_pet_damage = int(pet_damage * damage_boost.get_multiplier() * Currency_System.get_prestige_multiplier())

                current_monster.take_damage(final_pet_damage)

                popup_x = current_monster.rect.x + random.randint(20, max(20, current_monster.rect.width - 40))
                popup_y = current_monster.rect.y + random.randint(20, max(20, current_monster.rect.height - 40))
                damage_texts.append(DamageText(str(final_pet_damage), (popup_x, popup_y), is_critical))

                if current_monster.is_defeated():
                    Currency_System.update_economy(current_monster.hp, monster_manager.progression_index)

                    # Play titan defeated sound effect
                    if titan_defeated_sound:
                        titan_defeated_sound.play()

                    # Update Kitchen Guide progress (Quest 3: Defeat with pet)
                    if Button_System.panel_manager.kitchen_guide_system:
                        Button_System.panel_manager.kitchen_guide_system.guide_manager.update_progress("defeat_with_pet", 1)

                    monster_manager.next_monster()
                    current_monster = monster_manager.current_monster
                    current_monster.rect.x = MIDDLE_CENTER_X - MONSTER_SIZE // 2
                    current_monster.rect.y = 275
        last_pet_attack_time = current_time
    # =================================

    # ========== UPDATE DAMAGE TEXTS (ONLY ONE PLACE) ==========
    new_damage_texts = []
    for dt_obj in damage_texts:
        expired = dt_obj.update(dt_ms)
        if not expired:
            new_damage_texts.append(dt_obj)
    damage_texts = new_damage_texts
    # =========================================================

    # Load Inventory or Shop data when activated
    if not data_restored and (Button_System.panel_manager.active_panel == "Shop" or Button_System.panel_manager.active_panel == "Inventory" or Button_System.panel_manager.active_panel == "Pet"):
        Button_System.panel_manager.load_saved_data(
            Currency_System.pocket_money,
            saved_inventory,
            saved_shop_state,
            saved_pet_data,
            saved_guide_data
        )
        data_restored = True

    # ========== Set callbacks after systems are created ==========
    # Pet equip callback
    if Button_System.panel_manager.pet_system and not hasattr(Button_System.panel_manager.pet_system, '_callback_set'):
        Button_System.panel_manager.pet_system.guide_callback = lambda: (
            Button_System.panel_manager.kitchen_guide_system.guide_manager.update_progress("equip_pet", 1)
            if Button_System.panel_manager.kitchen_guide_system else None
        )
        Button_System.panel_manager.pet_system._callback_set = True

    # Player upgrade callback
    if Button_System.panel_manager.player_upgrade_system and not hasattr(Button_System.panel_manager.player_upgrade_system, '_callback_set'):
        Button_System.panel_manager.player_upgrade_system.upgrade_callback = lambda: (
            Button_System.panel_manager.kitchen_guide_system.guide_manager.update_progress("upgrade_base_damage", 1)
            if Button_System.panel_manager.kitchen_guide_system else None
        )
        Button_System.panel_manager.player_upgrade_system._callback_set = True
    # ==============================================================

# Restore upgrade level
    if Button_System.panel_manager.player_upgrade_system and saved_upgrade_level > 0:
        if Button_System.panel_manager.player_upgrade_system.level == 0:
            for _ in range(saved_upgrade_level):
                Button_System.panel_manager.player_upgrade_system.purchase_upgrade()
            print(f"[LOAD] Restored upgrade level: {saved_upgrade_level}")

    # Sync currency
    Button_System.panel_manager.global_pocket_money = Currency_System.pocket_money

    # Sync Stage & Check for Prestige
    Button_System.panel_manager.current_stage = monster_manager.stage

    # Update Kitchen Guide stage progress (Quest 4: Reach Stage)
    if Button_System.panel_manager.kitchen_guide_system:
        Button_System.panel_manager.kitchen_guide_system.guide_manager.update_progress("stage_reached", monster_manager.stage)

    if getattr(Button_System.panel_manager, 'wants_to_prestige', False):
        success = Currency_System.trigger_prestige(monster_manager)
        if success:
            Button_System.panel_manager.active_panel = None
        Button_System.panel_manager.wants_to_prestige = False

    # Auto save system for AFK
    current_time = time.time()
    if current_time - last_auto_save >= auto_save_interval:
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

        # Equipment system auto save
        Equipment_System.save_equipment()
        
        last_auto_save = current_time

    # -------------------------
    # Drawing
    # -------------------------
    window.fill((227, 227, 227))
    
    # Draw stats panel background
    window.blit(stats_panel_bg, (LEFT_AREA_X, 0))

    # Draw background (placed at the bottom, won't cover other UI)
    current_bg = get_current_background(monster_manager.stage)
    window.blit(current_bg, (MIDDLE_AREA_X, 0))
    
    # Draw Boost indicator (if active)
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

    pet_system = Button_System.panel_manager.pet_system
    if pet_system:
        equipped_pets = pet_system.get_equipped_pets()
        pet_size = 60
        pet_spacing = 10
        start_x = MIDDLE_CENTER_X - (len(equipped_pets) * pet_size + (len(equipped_pets) - 1) * pet_spacing) // 2
        pet_y = current_monster.rect.y + current_monster.rect.height + 20

        font_pet = pg.font.SysFont(None, 14)

        for idx, pet in enumerate(equipped_pets):
            pet_x = start_x + idx * (pet_size + pet_spacing)
            pet_rect = pg.Rect(pet_x, pet_y, pet_size, pet_size)
            pg.draw.rect(window, pet.color, pet_rect)
            pg.draw.rect(window, (200, 200, 200), pet_rect, 2)
            name_text = font_pet.render(pet.name, True, (0, 0, 0))
            name_rect = name_text.get_rect(center=(pet_rect.centerx, pet_rect.centery))
            window.blit(name_text, name_rect)

    Currency_System.draw_ui(window)

    if Button_System.panel_manager.pet_system:
        equipped_pets = Button_System.panel_manager.pet_system.get_equipped_pets()
        font_left = pg.font.SysFont(None, 20)
        y = 150
        for pet in equipped_pets:
            pet_text = font_left.render(f"Equipped: {pet.name}", True, (80, 80, 80))
            window.blit(pet_text, (10, y))
            y += 25

    for dt in damage_texts:
        dt.draw(window)

    for button in Button_System.buttons:
        button.draw(window)

    Button_System.panel_manager.draw(window)

    # Abilities drawn last so they are visible on top
    damage_boost.draw(window)
    crispy_precision.draw(window)

    pg.display.update()

pg.quit()


#References list

#1. ABILITY TO CLICK TO DEAL DAMAGE (Click_Damage_Feature.py)
#Source code: Copilot
#Link: None

#2. Drawer system (Button_System.py)
#Source code: Deepseek
#Link: None

#3. Shop system's UI system (Shop_System.py)
#Source code: Deepseek
#Link: None

#4. Code for fixing bug (AFK_System.py)
#Source code: Deepseek
#Link: None

#5. Code for decorational circle (Inventory_System.py)
#Source code: Deepseek
#Link: None

#6. UI reedit (Every file before window size=1300x750)
#Source code: Deepseek
#Link: None

#7. Pet system (Pet_System.py)
#Source code: Deepseek
#Link: None

#8. Kitchen Guide system (KitchenGuide_System.py)
#Source code: Deepseek
#Link: None

''' Tan Zhe Xi '''
## TZX_1. MINIGAME SYSTEM
## TZX_2. EQUIPMENT & DATA DESIGN
## TZX_3. ABILITY TO CLICK TO DEAL DAMAGE
#(Handled by Click_Damage_Feature.py)
## TZX_4. ADJUSTING STATS ACCORDING TO PRESTIGE LEVELS

''' Eng Kai Hin '''
## EKH_1. BUTTON INTERACTION SYSTEM
# (Handled by Button_System.py, which contains button and drawer system)
## EKH_2. AFK SYSTEM
# (Handled by AFK_System.py, which contains AFK system and data saving system that save player's data)
## EKH_3. SHOP SYSTEM
# (Handled by Shop_System.py and Inventory_System, One for buying item one for storing item)
## EKH_4. CLEAR WHEN PRESTIGE SYSTEM

''' Chen Lik Shen '''
## CLS_1. GAME UI & SOUND EFFECT
# (Handled by Currency_System.py)
## CLS_2. GAIN & LOST OF EQUIPMENT & CURRENCY SYSTEM
# (Handled by Currency_System.py)
## CLS_3. CRAFTING SYSTEM
## CLS_4. SYSTEM TO ADD NEW EQUIPMENT, CHARACTER, AND RECIPES ACCORDING TO EACH PRESTIGE LEVELS