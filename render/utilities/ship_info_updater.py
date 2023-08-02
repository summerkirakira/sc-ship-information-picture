from model import ShipGroup
import json


ship_group = ShipGroup()
ship_group.load_all()
for ship in ship_group.ships:
    if ship.photo_name is None:
        binding = ship_group.get_binding_by_local_name(ship.local_name)
        ship.photo_name = binding.photo_name

ship_group.save_all()

