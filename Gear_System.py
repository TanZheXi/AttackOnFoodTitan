import json

# 1. Open the external file and load it into a dictionary
with open('gears.json', 'r') as file:
    gear_database = json.load(file)

"""Variables"""
total_bonus_damage = 0
crafting_scraps = 0

# --- The Player's Body ---
equipped_slots = {
    "weapon": None,
    "hat": None,
    "armor": None,
    "aroma": None  
}

def recalculate_stats():
    global total_bonus_damage
    total_bonus_damage = 0
    for slot_name, item_name in equipped_slots.items():
        if item_name is not None: 
            total_bonus_damage += gear_database[item_name]["damage"]

def gain_gear(item_name):
    """Call this when a player buys or crafts an item!"""
    global crafting_scraps 
    
    if item_name in gear_database:
        
        # 1. Fetch the stats so we can use them easily
        scrap_reward = gear_database[item_name]["scrap_value"]
        rarity_tier = gear_database[item_name]["rarity"] 
        
        # SCENARIO A: The player ALREADY owns it 
        if gear_database[item_name]["owned"] == True:
            crafting_scraps += scrap_reward
            print(f"Duplicate [{rarity_tier}] {item_name} found! Smashed into {scrap_reward} Scraps. (Total Scraps: {crafting_scraps})")
            return True
            
        # SCENARIO B: The player DOES NOT own it
        else:
            gear_database[item_name]["owned"] = True 
            print(f"Loot Acquired: [{rarity_tier}] {item_name}!") 
            recalculate_stats()
            return True
            
    return False

def equip_gear(item_name):
    """Takes an item from the backpack and puts it on the player's body."""
    # 1. Verify the player actually owns the item
    if item_name in gear_database and gear_database[item_name]["owned"] == True:
        
        target_slot = gear_database[item_name]["slot"]
        
        old_item = equipped_slots[target_slot]
        if old_item is not None:
            print(f"Removed {old_item} from {target_slot} and put it back in backpack.")
            
        # Put the new item on the player and update the equipped gear
        equipped_slots[target_slot] = item_name
        print(f"Equipped [{gear_database[item_name]['rarity']}] {item_name} to {target_slot}!")
        
        # Update the damage 
        recalculate_stats()
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
            recalculate_stats() # Recalculate to remove the item's damage
            return True
        else:
            print(f"Your {slot_name} slot is already empty!")
            return False
    else:
        print(f"Error: {slot_name} is not a valid body part.")
        return False

"""For Rebirth/Prestige reset"""
def lose_all_gear():
    print("Prestige Triggered! Resetting all gear and slots...")
    
    # 1. Empty the body slots
    for slot in equipped_slots:
        equipped_slots[slot] = None
        
    # 2. Empty the backpack
    for item_name in gear_database:
        gear_database[item_name]["owned"] = False
        
    # 3. Recalculate damage back to 0
    recalculate_stats()