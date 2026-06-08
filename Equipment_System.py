import json
import os

# 1. Open the external file and load it into a dictionary
with open('Equipment.json', 'r') as file:
    equipment_database = json.load(file)

"""Variables"""
total_damage_multiplier = 1.0
crafting_scraps = 0

# --- Kitchen Guide callback ---
_equip_callback = None

def set_equip_callback(callback):
    """Set callback for when equipment is equipped"""
    global _equip_callback
    _equip_callback = callback

# --- The Player's Body ---
equipped_slots = {
    "weapon": None,
    "hat": None,
    "armor": None,
    "aroma": None  
}

def recalculate_stats():
    global total_damage_multiplier
    # Reset back to 1.0 before checking equipment
    total_damage_multiplier = 1.0 
    
    for slot_name, item_name in equipped_slots.items():
        if item_name is not None:
            # Multiply the current total by the equipment's multiplier
            total_damage_multiplier *= equipment_database[item_name]["multiplier"]

    print(f"[STATS] Total damage multiplier: {total_damage_multiplier}")

def gain_equipment(item_name):
    """Call this when a player buys or crafts an item!"""
    global crafting_scraps 
    
    if item_name in equipment_database:
        scrap_reward = equipment_database[item_name]["scrap_value"]
        rarity_tier = equipment_database[item_name]["rarity"]

        if equipment_database[item_name].get("owned", False) is True:
            crafting_scraps += scrap_reward
            print(f"Duplicate [{rarity_tier}] {item_name} found! Smashed into {scrap_reward} Scraps. (Total Scraps: {crafting_scraps})")
            save_equipment()
            return True
        else:
            equipment_database[item_name]["owned"] = True
            print(f"Loot Acquired: [{rarity_tier}] {item_name}!")
            recalculate_stats()
            save_equipment()
            return True

    return False

def upgrade_equipment(item_name):
    global crafting_scraps

    item = equipment_database.get(item_name)

    if not item or not item.get("owned", False):
        return  False 
    
    if "level" not in item:
        item["level"] = 1

    base_scrap_cost = item.get("scrap_value", 10)
    upgrade_cost = base_scrap_cost * item["level"]

    if crafting_scraps >= upgrade_cost:
        crafting_scraps -= upgrade_cost

        item["level"] += 1
        item["multiplier"] *= 1.10  # Increase multiplier by 10% per level

        recalculate_stats()
        print(f"Upgraded {item_name} to level {item['level']}! New multiplier: {item['multiplier']:.2f}. (Scraps left: {crafting_scraps})")

        return True
    else:
        print(f"Not enough Scraps to upgrade {item_name}! Upgrade cost: {upgrade_cost}, Scraps available: {crafting_scraps}")
        return False


def equip_equipment(item_name):
    """Takes an item from the backpack and puts it on the player's body."""
    global _equip_callback
    
    if item_name in equipment_database and equipment_database[item_name].get("owned", False) is True:
        target_slot = equipment_database[item_name]["slot"]

        old_item = equipped_slots[target_slot]
        if old_item is not None:
            print(f"Removed {old_item} from {target_slot} and put it back in backpack.")

        equipped_slots[target_slot] = item_name
        print(f"Equipped [{equipment_database[item_name]['rarity']}] {item_name} to {target_slot}!")

        recalculate_stats()
        save_equipment()  # save immediately after equipping
        print(f"[EQUIP] Saved to JSON - equipped weapon: {equipped_slots['weapon']}")

        # ========== Announce Kitchen Guide Equipment Update ==========
        if _equip_callback:
            _equip_callback()
        # =================================================

        return True
    else:
        print(f"You cannot equip {item_name} because you don't own it!")
        return False
    
def unequip_equipment(slot_name):
    """Removes an item from a specific body slot and leaves it empty."""
    if slot_name in equipped_slots:
        current_item = equipped_slots[slot_name]
        if current_item is not None:
            equipped_slots[slot_name] = None
            print(f"Unequipped {current_item} from {slot_name}! (Returned to Backpack)")
            recalculate_stats()
            save_equipment()  # save immediately after unequipping
            return True
        else:
            print(f"Your {slot_name} slot is already empty!")
            return False
    else:
        print(f"Error: {slot_name} is not a valid body part.")
        return False
    
def craft_item(item_name):
    global crafting_scraps

    if item_name not in equipment_database:
        print(f"Recipe Error: {item_name} does not exist!")
        return False

    if equipment_database[item_name].get("owned", False) is True:
        print(f"You already own the {item_name}! No need to craft it.")
        return False

    cost_to_craft = equipment_database[item_name]["scrap_value"] * 10

    if crafting_scraps >= cost_to_craft:
        crafting_scraps -= cost_to_craft
        equipment_database[item_name]["owned"] = True

        rarity = equipment_database[item_name]["rarity"]
        print(f"FORGE SUCCESS! You crafted the [{rarity}] {item_name} for {cost_to_craft} Scraps. (Sent to Backpack)")
        save_equipment()
        return True
    else:
        print(f"Crafting Failed: {item_name} costs {cost_to_craft} Scraps. (You only have {crafting_scraps})")
        return False

"""For Rebirth/Prestige reset"""
def lose_all_equipment():
    print("Prestige Triggered! Resetting all equipment and slots...")

    for slot in equipped_slots:
        equipped_slots[slot] = None

    for item_name in equipment_database:
        if item_name != "Player_Data":
            equipment_database[item_name]["owned"] = False

    global crafting_scraps
    crafting_scraps = 0

    recalculate_stats()
    save_equipment()

def reset_equipment_to_default():
    """Reset all equipment data to default state (used for new games)"""
    global crafting_scraps, equipped_slots, equipment_database

    for item_name in equipment_database:
        if item_name != "Player_Data":
            equipment_database[item_name]["owned"] = False

    for slot in equipped_slots:
        equipped_slots[slot] = None

    crafting_scraps = 0

    equipment_database["Player_Data"] = {
        "scraps": 0,
        "equipped": {
            "weapon": None,
            "hat": None,
            "armor": None,
            "aroma": None
        }
    }

    recalculate_stats()
    save_equipment()
    print("[EQUIPMENT] Equipment system reset to default.")

def save_equipment():
    """Saves the player's equipped slots, scrap count, and backpack to Equipment.json"""
    global crafting_scraps

    equipment_database["Player_Data"] = {
        "scraps": crafting_scraps,
        "equipped": equipped_slots.copy()  # use copy to ensure we save the current state of equipped slots
    }

    with open('Equipment.json', 'w') as file:
        json.dump(equipment_database, file, indent=4) # indent=4 makes it readable!

    print("Equipment System Auto-Saved!")


def load_equipment():
    """Reads Equipment.json and restores the player's scraps and equipped items."""
    global crafting_scraps, equipped_slots, equipment_database
    
    # ========== Detect afk_save.json exists or not ==========
    afk_save_exists = os.path.exists("afk_save.json")

    with open('Equipment.json', 'r') as file:
        equipment_database = json.load(file)
    
    if not afk_save_exists:
        print("[EQUIPMENT] New game detected! Resetting all equipment ownership.")
        for item_name in equipment_database:
            if item_name != "Player_Data":
                equipment_database[item_name]["owned"] = False
        # Reset Player_Data
        equipment_database["Player_Data"] = {
            "scraps": 0,
            "equipped": {
                "weapon": None,
                "hat": None,
                "armor": None,
                "aroma": None
            }
        }

        with open('Equipment.json', 'w') as file:
            json.dump(equipment_database, file, indent=4)
    
    if "Player_Data" in equipment_database:
        player_data = equipment_database["Player_Data"]
        
        # 2. Restore the scraps
        crafting_scraps = player_data.get("scraps", 0)
        
        # 3. Restore the equipped slots (only if the player actually owns the item)
        saved_slots = player_data.get("equipped", {})
        
        for slot, item_name in saved_slots.items():
            if item_name and item_name in equipment_database and equipment_database[item_name].get("owned", False):
                equipped_slots[slot] = item_name
                print(f"[LOAD] Equipped {item_name} to {slot}")
            else:
                equipped_slots[slot] = None
            
        print("Equipment System Loaded Successfully!")
        print(f"[LOAD] Loaded equipped weapon: {equipped_slots['weapon']}")
        
        recalculate_stats()
        return True
    else:
        print("No saved equipment data found. Starting fresh!")
        return True

def upgrade_weapon_by_name(weapon_name):
    """Upgrades whatever weapon name is passed to it from the Forge!"""
    global crafting_scraps
    
    item = equipment_database.get(weapon_name)
    if not item or not item.get("owned", False): 
        return False
        
    if "level" not in item:
        item["level"] = 1
        
    cost = item.get("scrap_value", 10) * item["level"]
    
    if crafting_scraps >= cost:
        crafting_scraps -= cost
        item["level"] += 1
        item["multiplier"] += 0.5 
        
        recalculate_stats()
        save_equipment() 
        print(f"[FORGE] Upgraded {weapon_name} to Level {item['level']}!")
        return True
        
    return False