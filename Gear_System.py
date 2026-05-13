import json
import os

# 1. Open the external file and load it into a dictionary
with open('gears.json', 'r') as file:
    gear_database = json.load(file)

"""Variables"""
total_damage_multiplier = 1.0
crafting_scraps = 0

# --- The Player's Body ---
equipped_slots = {
    "weapon": None,
    "hat": None,
    "armor": None,
    "aroma": None  
}

def recalculate_stats():
    global total_damage_multiplier
    # Reset back to 1.0 before checking gear
    total_damage_multiplier = 1.0 
    
    for slot_name, item_name in equipped_slots.items():
        if item_name is not None: 
            # Multiply the current total by the gear's multiplier
            total_damage_multiplier *= gear_database[item_name]["multiplier"]
    print(f"[STATS] Total damage multiplier: {total_damage_multiplier}")

def gain_gear(item_name):
    """Call this when a player buys or crafts an item!"""
    global crafting_scraps 
    
    if item_name in gear_database:
        
        scrap_reward = gear_database[item_name]["scrap_value"]
        rarity_tier = gear_database[item_name]["rarity"] 
        
        if gear_database[item_name].get("owned", False) == True:
            crafting_scraps += scrap_reward
            print(f"Duplicate [{rarity_tier}] {item_name} found! Smashed into {scrap_reward} Scraps. (Total Scraps: {crafting_scraps})")
            save_gear()
            return True
            
        else:
            gear_database[item_name]["owned"] = True 
            print(f"Loot Acquired: [{rarity_tier}] {item_name}!") 
            recalculate_stats()
            save_gear()
            return True
            
    return False

def equip_gear(item_name):
    """Takes an item from the backpack and puts it on the player's body."""
    print(f"[EQUIP] Trying to equip: {item_name}")
    
    if item_name in gear_database and gear_database[item_name].get("owned", False) == True:
        
        target_slot = gear_database[item_name]["slot"]
        
        old_item = equipped_slots[target_slot]
        if old_item is not None:
            print(f"Removed {old_item} from {target_slot} and put it back in backpack.")
            
        equipped_slots[target_slot] = item_name
        print(f"Equipped [{gear_database[item_name]['rarity']}] {item_name} to {target_slot}!")
        
        recalculate_stats()
        save_gear()  # save immediately after equipping
        print(f"[EQUIP] Saved to JSON - equipped weapon: {equipped_slots['weapon']}")
        
        return True
        
    else:
        print(f"You cannot equip {item_name} because you don't own it!")
        return False
    
def unequip_gear(slot_name):
    """Removes an item from a specific body slot and leaves it empty."""
    if slot_name in equipped_slots:
        current_item = equipped_slots[slot_name]
        if current_item is not None:
            equipped_slots[slot_name] = None
            print(f"Unequipped {current_item} from {slot_name}! (Returned to Backpack)")
            recalculate_stats()
            save_gear()  # save immediately after unequipping
            return True
        else:
            print(f"Your {slot_name} slot is already empty!")
            return False
    else:
        print(f"Error: {slot_name} is not a valid body part.")
        return False
    
def craft_item(item_name):
    global crafting_scraps
    if item_name not in gear_database:
        print(f"Recipe Error: {item_name} does not exist!")
        return False
        
    if gear_database[item_name].get("owned", False) == True:
        print(f"You already own the {item_name}! No need to craft it.")
        return False
        
    cost_to_craft = gear_database[item_name]["scrap_value"] * 10
    
    if crafting_scraps >= cost_to_craft:
        crafting_scraps -= cost_to_craft
        gear_database[item_name]["owned"] = True
        
        rarity = gear_database[item_name]["rarity"]
        print(f"FORGE SUCCESS! You crafted the [{rarity}] {item_name} for {cost_to_craft} Scraps. (Sent to Backpack)")
        save_gear()
        return True
    else:
        print(f"Crafting Failed: {item_name} costs {cost_to_craft} Scraps. (You only have {crafting_scraps})")
        return False
    
def lose_all_gear():
    """Reset all gear owned status and unequip everything (called on prestige)"""
    print("Prestige Triggered! Resetting all gear and slots...")
    
    for slot in equipped_slots:
        equipped_slots[slot] = None
        
    for item_name in gear_database:
        if item_name != "Player_Data":
            gear_database[item_name]["owned"] = False
        
    global crafting_scraps
    crafting_scraps = 0
        
    recalculate_stats()
    save_gear()

def reset_gear_to_default():
    """Reset all gear data to default state (used for new games)"""
    global crafting_scraps, equipped_slots, gear_database
    
    for item_name in gear_database:
        if item_name != "Player_Data":
            gear_database[item_name]["owned"] = False
    
    for slot in equipped_slots:
        equipped_slots[slot] = None
    
    crafting_scraps = 0
    
    gear_database["Player_Data"] = {
        "scraps": 0,
        "equipped": {
            "weapon": None,
            "hat": None,
            "armor": None,
            "aroma": None
        }
    }
    
    recalculate_stats()
    save_gear()
    print("[GEAR] Equipment system reset to default.")

def save_gear():
    """Saves the player's equipped slots, scrap count, and backpack to gears.json"""
    global crafting_scraps
    
    gear_database["Player_Data"] = {
        "scraps": crafting_scraps,
        "equipped": equipped_slots.copy()  # use copy to ensure we save the current state of equipped slots
    }
    
    with open('gears.json', 'w') as file:
        json.dump(gear_database, file, indent=4)
        
    print(f"[SAVE] Gear saved - equipped weapon: {equipped_slots['weapon']}")

def load_gear():
    """Reads gears.json and restores the player's scraps and equipped items."""
    global crafting_scraps, equipped_slots, gear_database
    
    afk_save_exists = os.path.exists("afk_save.json")
    
    with open('gears.json', 'r') as file:
        gear_database = json.load(file)
    
    if not afk_save_exists:
        print("[GEAR] New game detected! Resetting all equipment ownership.")
        for item_name in gear_database:
            if item_name != "Player_Data":
                gear_database[item_name]["owned"] = False
        gear_database["Player_Data"] = {
            "scraps": 0,
            "equipped": {
                "weapon": None,
                "hat": None,
                "armor": None,
                "aroma": None
            }
        }
        with open('gears.json', 'w') as file:
            json.dump(gear_database, file, indent=4)
    
    if "Player_Data" in gear_database:
        player_data = gear_database["Player_Data"]
        
        crafting_scraps = player_data.get("scraps", 0)
        
        saved_slots = player_data.get("equipped", {})
        
        for slot, item_name in saved_slots.items():
            if item_name and item_name in gear_database and gear_database[item_name].get("owned", False):
                equipped_slots[slot] = item_name
                print(f"[LOAD] Equipped {item_name} to {slot}")
            else:
                equipped_slots[slot] = None
            
        print("Gear System Loaded Successfully!")
        print(f"[LOAD] Loaded equipped weapon: {equipped_slots['weapon']}")
        
        recalculate_stats()
        return True
    else:
        print("No saved gear data found. Starting fresh!")
        return False