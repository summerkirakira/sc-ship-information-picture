from models import Ship
import json
from pydantic import BaseModel
from calculator import Calculator
from pathlib import Path
# from pic_drawer import PicDrawer, ShipDrawer
import pathlib


class FakeShip(BaseModel):
    name: str
    chinese_name: str
    health: int
    quantum_fuel: int
    fuel: int
    manufactory: str
    manufactory_chinese_name: str
    size: int
    role: str
    mass: float
    description: str
    crewSize: int
    cargo: int

    class Component(BaseModel):
        size: int
        name: str
        num: int

    weapon: list[Component]
    shield: list[Component]
    missile: list[Component]

    class Dimension(BaseModel):
        x: int
        y: int
        z: int

    dimension: Dimension

    def convert_to_real_ship(self):
        with open(Path(__file__).parent / "data" / "fake_ship" / "sample_ship.json", 'r', encoding="utf-8") as f:
            sample_ship = Ship(**json.load(f))
        with open(Path(__file__).parent / "data" / "fake_ship" / "sample_turret.json", 'r', encoding="utf-8") as f:
            sample_turret = Ship.Data.Loadout(**json.load(f))
        with open(Path(__file__).parent / "data" / "fake_ship" / "sample_missile.json", 'r', encoding="utf-8") as f:
            sample_missile = Ship.Data.Loadout(**json.load(f))
        with open(Path(__file__).parent / "data" / "fake_ship" / "sample_shield.json", 'r', encoding="utf-8") as f:
            sample_shield = Ship.Data.Loadout(**json.load(f))
        sample_ship.data.name = self.name
        sample_ship.data.chineseName = self.chinese_name
        sample_ship.data.manufacturerData.data.chineseName = self.manufactory_chinese_name
        sample_ship.data.manufacturerData.data.name = self.manufactory
        sample_ship.data.chineseDescription = self.description
        sample_ship.data.hull.mass = self.mass
        sample_ship.data.hull.hp[0].hp = self.health
        sample_ship.data.vehicle.size.x = self.dimension.x
        sample_ship.data.vehicle.size.y = self.dimension.y
        sample_ship.data.vehicle.size.z = self.dimension.z
        sample_ship.data.qtFuelCapacity = self.quantum_fuel
        sample_ship.data.fuelCapacity = self.fuel
        sample_ship.data.vehicle.crewSize = self.crewSize
        sample_ship.data.vehicle.career = self.role
        sample_ship.localName = f"fake_{self.name.lower()}"
        # sample_ship.data.items.cargos.append(Ship.Data.Items.Cargo(**{
        #     "data": {
        #         "cargoGrid": {
        #             "scus": self.cargo
        #         }
        #     }
        # }))

        for weapon in self.weapon:
            for i in range(weapon.num):
                turret_copy = sample_turret.copy(deep=True)
                turret_copy.mount.data.chineseName = weapon.name
                turret_copy.mount.data.size = weapon.size
                sample_ship.data.loadout.append(turret_copy)
        for shield in self.shield:
            for i in range(shield.num):
                shield_copy = sample_shield.copy(deep=True)
                shield_copy.mount.data.chineseName = shield.name
                shield_copy.mount.data.size = shield.size
                sample_ship.data.loadout.append(shield_copy)
        for missile in self.missile:
            for i in range(missile.num):
                missile_copy = sample_missile.copy(deep=True)
                missile_copy.mount.data.chineseName = missile.name
                missile_copy.mount.data.size = missile.size
                sample_ship.data.loadout.append(missile_copy)
        return sample_ship


def load_fake_ship():
    with open(Path(__file__).parent / "data" / "fake_ship" / "fake_ships.json", 'r', encoding="utf-8") as f:
        data = json.load(f)
        fake_ships = [FakeShip(**d) for d in data]
        new_ships = [fake_ship.convert_to_real_ship() for fake_ship in fake_ships]
    return new_ships


# if __name__ == '__main__':
#     calculator = Calculator()
#
#     for ship in load_fake_ship():
#         ship_drawer = ShipDrawer(ship, calculator)
#         ship_drawer.draw(pathlib.Path("test/"))
