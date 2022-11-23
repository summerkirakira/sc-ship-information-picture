import json
from pathlib import Path
import os
from thefuzz import process


def format_ship_file(name):
    ship_path = Path(__file__).parent / "data" / "ships.json"

    with open(ship_path, 'r') as f:
        ships = json.load(f)

    with open(ship_path, 'w') as f:
        json.dump(ships, f, indent=4)


def get_aliases():
    alias_path = Path(__file__).parent / "data" / "alias.json"
    new_alias_path = Path(__file__).parent / "data" / "new_alias.json"

    with open(alias_path, 'r') as f:
        aliases = json.load(f)

    current_ships = os.listdir(Path(__file__).parent / "test")
    current_ships = [ship.split('.')[0] for ship in current_ships]
    new_aliases = {}
    for ship in aliases:
        match_ship = process.extractOne(ship, current_ships)
        if match_ship[1] == 100:
            continue
        result = input(f'{ship} -> {match_ship[0]}? (y/n/s)')
        if result == 's':
            new_aliases[ship] = aliases[ship]
    with open(new_alias_path, 'w') as f:
        json.dump(new_aliases, f, indent=4, ensure_ascii=False)

get_aliases()

