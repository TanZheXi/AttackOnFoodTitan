import json

# 1. Open the external file and load it into a dictionary
with open('Equipment.json', 'r') as file:
    equipment_database = json.load(file)

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
    # Reset back to 1.0 before checking equipment
    total_damage_multiplier = 1.0 
    
    for slot_name, item_name in equipped_slots.items():
        if item_name is not None: 
            # Multiply the current total by the equipment's multiplier
            total_damage_multiplier *= equipment_database[item_name]["multiplier"]

def gain_equipment(item_name):
    """Call this when a player buys or crafts an item!"""
    global crafting_scraps 
    
    if item_name in equipment_database:
        
        # 1. Fetch the stats so we can use them easily
        scrap_reward = equipment_database[item_name]["scrap_value"]
        rarity_tier = equipment_database[item_name]["rarity"] 
        
        # SCENARIO A: The player ALREADY owns it 
        if equipment_database[item_name]["owned"] == True:
            crafting_scraps += scrap_reward
            print(f"Duplicate [{rarity_tier}] {item_name} found! Smashed into {scrap_reward} Scraps. (Total Scraps: {crafting_scraps})")
            return True
            
        # SCENARIO B: The player DOES NOT own it
        else:
            equipment_database[item_name]["owned"] = True 
            print(f"Loot Acquired: [{rarity_tier}] {item_name}!") 
            recalculate_stats()
            return True
            
    return False

def equip_equipment(item_name):
    """Takes an item from the backpack and puts it on the player's body."""
    # 1. Verify the player actually owns the item
    if item_name in equipment_database and equipment_database[item_name]["owned"] == True:
        
        target_slot = equipment_database[item_name]["slot"]
        
        old_item = equipped_slots[target_slot]
        if old_item is not None:
            print(f"Removed {old_item} from {target_slot} and put it back in backpack.")
            
        # Put the new item on the player and update the equipped equipment
        equipped_slots[target_slot] = item_name
        print(f"Equipped [{equipment_database[item_name]['rarity']}] {item_name} to {target_slot}!")
        
        # Update the damage 
        recalculate_stats()
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
            recalculate_stats() # Recalculate to remove the item's damage
            return True
        else:
            print(f"Your {slot_name} slot is already empty!")
            return False
    else:
        print(f"Error: {slot_name} is not a valid body part.")
        return False
    
def craft_item(item_name):
    global crafting_scraps
    # 1. Check if the item actually exists in the database
    if item_name not in equipment_database:
        print(f"Recipe Error: {item_name} does not exist!")
        return False
        
    # 2. Check if they already own it
    if equipment_database[item_name]["owned"] == True:
        print(f"You already own the {item_name}! No need to craft it.")
        return False
        
    # 3. Calculate the Crafting Cost (Scrap Value * 10)
    cost_to_craft = equipment_database[item_name]["scrap_value"] * 10
    
    # 4. Check if they have enough Scraps
    if crafting_scraps >= cost_to_craft:
        crafting_scraps -= cost_to_craft
        equipment_database[item_name]["owned"] = True
        
        rarity = equipment_database[item_name]["rarity"]
        print(f"FORGE SUCCESS! You crafted the [{rarity}] {item_name} for {cost_to_craft} Scraps. (Sent to Backpack)")
        return True
    else:
        print(f"Crafting Failed: {item_name} costs {cost_to_craft} Scraps. (You only have {crafting_scraps})")
        return False
    
"""For Rebirth/Prestige reset"""
def lose_all_equipment():
    print("Prestige Triggered! Resetting all equipment and slots...")
    
    # 1. Empty the body slots
    for slot in equipped_slots:
        equipped_slots[slot] = None
        
    # 2. Empty the backpack
    for item_name in equipment_database:
        equipment_database[item_name]["owned"] = False
        
    # 3. Recalculate damage back to 0
    recalculate_stats()

def save_equipment():
    """Saves the player's equipped slots, scrap count, and backpack to Equipment.json"""
    global crafting_scraps
    
    # 1. We need a place to store the scraps and slots inside the JSON
    # Let's create a special "Player_Data" section hidden in the equipment database
    equipment_database["Player_Data"] = {
        "scraps": crafting_scraps,
        "equipped": equipped_slots
    }
    
    # 2. Write the whole updated dictionary back to the Equipment.json file
    with open('Equipment.json', 'w') as file:
        json.dump(equipment_database, file, indent=4) # indent=4 makes it readable!
        
    print("Equipment System Auto-Saved!")

def load_equipment():
    """Reads Equipment.json and restores the player's scraps and equipped items."""
    global crafting_scraps, equipped_slots
    
    # 1. Check if the "Player_Data" section actually exists in the database
    if "Player_Data" in equipment_database:
        player_data = equipment_database["Player_Data"]
        
        # 2. Restore the scraps
        crafting_scraps = player_data.get("scraps", 0)
        
        # 3. Restore the equipped slots
        saved_slots = player_data.get("equipped", {})
        
        # We loop through in case you ever decide to add more than 4 slots later
        for slot, item_name in saved_slots.items():
            equipped_slots[slot] = item_name
            
        print("Equipment System Loaded Successfully!")
        
        # 4. CRITICAL: Recalculate stats so the player gets their damage buff
        recalculate_stats()
        return True
    else:
        print("No saved equipment data found. Starting fresh!")
        return False