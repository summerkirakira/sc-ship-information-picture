import json
from pathlib import Path
from thefuzz import process
from models import ShipNameBinding

ship_list_path = Path(__file__).parent / "data" / "ship_list.json"
ship_upgrade_path = Path(__file__).parent / "data" / "upgrade_info.json"

ship_photo_path = Path('/Users/forever/Documents/Code/ship-render')
ship_name_binding_path = Path(__file__).parent / "data" / "ship_name_binding.json"


with open(ship_name_binding_path, 'r') as f:
    data = json.load(f)
    ship_name_binding = [ShipNameBinding(**d) for d in data]

with open(ship_upgrade_path, 'r') as f:
    data = json.load(f)
    ship_upgrade = data


photo_list = ship_photo_path.glob('*.png')

with open(ship_list_path, 'r') as f:
    ship_list = json.load(f)

for photo in photo_list:
    photo_name = photo.stem
    is_new = True
    for ship_binding in ship_name_binding:
        if photo_name == ship_binding.photo_name:
            is_new = False
            break
    if not is_new:
        continue
    ship_name = process.extractOne(photo_name, [ship['data']['name'] for ship in ship_list])
    result = input(f'{photo_name} -> {ship_name[0]}? (y/n/s)')
    if result == 's':
        continue
    if result != 'y':
        for ship in [ship['data']['name'] for ship in ship_list]:
            if result.lower() == ship.lower():
                ship_name = (ship, 100)
    ship_upgrade_name = process.extractOne(ship_name[0], [ship['name'] for ship in ship_upgrade[0]['data']['ships']])
    upgrade_name = input(f'{ship_name[0]} -> {ship_upgrade_name[0]}? (y/n/s)')
    if upgrade_name == 's':
        continue
    if upgrade_name != 'y':
        for ship in [ship['name'] for ship in ship_upgrade[0]['data']['ships']]:
            if upgrade_name.lower() == ship.lower():
                ship_upgrade_name = (ship, 100)
    local_name = ''
    for ship in ship_list:
        if ship['data']['name'] == ship_name[0]:
            local_name = ship['localName']
            break
    ship_price = 0
    for ship in ship_upgrade[0]['data']['ships']:
        if ship['name'] == ship_upgrade_name[0]:
            ship_price = ship['msrp']
            break
    ship_name_binding.append(ShipNameBinding(local_name=local_name,
                                             photo_name=photo_name,
                                             ship_name=ship_name[0],
                                             ship_price=ship_price,
                                             upgrade_name=ship_upgrade_name[0]))
    with open(ship_name_binding_path, 'w') as f:
        json.dump([ship_binding.dict() for ship_binding in ship_name_binding], f, indent=4)

