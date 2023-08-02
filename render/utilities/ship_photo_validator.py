import json
import pathlib

ship_in_shop_path = pathlib.Path(__file__).parent.parent / "data" / "formatted_ship_alias.json"
ship_name_binding_path = pathlib.Path(__file__).parent.parent / "data" / "ship_name_binding.json"

with open(ship_in_shop_path, "r") as f:
    ship_in_shop = json.load(f)

with open(ship_name_binding_path, "r") as f:
    ship_name_binding = json.load(f)

for ship_info in ship_in_shop:
    is_find = False
    for ship in ship_name_binding:
        if ship_info["name"] == ship["upgrade_name"]:
            is_find = True
            break
    if not is_find:
        print(ship_info["name"])