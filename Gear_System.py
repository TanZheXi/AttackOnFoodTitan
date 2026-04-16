import json

# 1. Open the external file and load it into a dictionary
with open('gears.json', 'r') as file:
    gear_database = json.load(file)

total_bonus_damage = 0

def recalculate_stats():
    global total_bonus_damage
    total_bonus_damage = 0
    for item_name, stats in gear_database.items():
        if stats["owned"] == True:
            total_bonus_damage += stats["damage"]

def gain_gear(item_name):
    if item_name in gear_database:
        if not gear_database[item_name]["owned"]:
            gear_database[item_name]["owned"] = True # <--- FIXED!
            print(f"Loot Acquired: {item_name}!")
            recalculate_stats()
            return True
    return False

"""For Rebirth/Prestige reset"""
def lose_all_gear():
    print("Reseting")
    for item_name in gear_database:
      gear_database[item_name]["owned"] = False
    recalculate_stats()