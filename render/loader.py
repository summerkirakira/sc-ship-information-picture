from models import Missile, Bomb, Shield, Weapon, Cooler, EMP, MiningLaser, Mount, PowerPlant, QDrive, Qed, Utility, Paint, MissileRack, Ship, Shop, ComponentData, Archive
import json
import pathlib
from typing import Callable, Optional
from translation import Translation


class Loader:
    def __init__(self):
        self.missile_path = pathlib.Path(__file__).parent / "data" / "missiles.json"
        self.shop_path = pathlib.Path(__file__).parent / "data" / "shops.json"
        self.bomb_path = pathlib.Path(__file__).parent / "data" / "bombs.json"
        self.shield_path = pathlib.Path(__file__).parent / "data" / "shields.json"
        self.weapon_path = pathlib.Path(__file__).parent / "data" / "weapons.json"
        self.cooler_path = pathlib.Path(__file__).parent / "data" / "coolers.json"
        self.emp_path = pathlib.Path(__file__).parent / "data" / "emps.json"
        self.mining_laser_path = pathlib.Path(__file__).parent / "data" / "mining_lasers.json"
        self.mount_path = pathlib.Path(__file__).parent / "data" / "mounts.json"
        self.power_plant_path = pathlib.Path(__file__).parent / "data" / "power_plants.json"
        self.qdrive_path = pathlib.Path(__file__).parent / "data" / "qdrives.json"
        self.qed_path = pathlib.Path(__file__).parent / "data" / "qeds.json"
        self.utility_path = pathlib.Path(__file__).parent / "data" / "utilities.json"
        self.paint_path = pathlib.Path(__file__).parent / "data" / "paints.json"
        self.ship_path = pathlib.Path(__file__).parent / "data" / "ships.json"
        self.missile_rack_path = pathlib.Path(__file__).parent / "data" / "missile_racks.json"
        self.archive_path = pathlib.Path(__file__).parent / "data" / "archive.json"
        self.localization_path = pathlib.Path(__file__).parent / "data" / "global.ini"
        self.loaner_path = pathlib.Path(__file__).parent / "data" / "loaner_ships.json"

        self.missiles: list[Missile] = []
        self.shops: list[Shop] = []
        self.bombs: list[Bomb] = []
        self.shields: list[Shield] = []
        self.weapons: list[Weapon] = []
        self.coolers: list[Cooler] = []
        self.emps: list[EMP] = []
        self.mining_lasers: list[MiningLaser] = []
        self.mounts: list[ComponentData] = []
        self.power_plants: list[PowerPlant] = []
        self.qdrives: list[ComponentData] = []
        self.qeds: list[ComponentData] = []
        self.utilities: list[Utility] = []
        self.paints: list[Paint] = []
        self.ships: list[Ship] = []
        self.missile_racks: list[ComponentData] = []

        self.localization = Translation(self.localization_path)

        # self.load_all()
        self.load_from_archive()
        # self.save_all()

    def translate_component(func: Callable[['Loader'], list[ComponentData]], *args, **kwargs) -> Callable[
        ['Loader'], list[ComponentData]]:
        def wrapper(self: 'Loader') -> list[ComponentData]:
            components_list: list[ComponentData] = func(self)
            for component in components_list:
                component.data.chineseNameShort = self.localization.get_item_name_short(component.localName)
                component.data.chineseName = self.localization.get_item_name(component.localName)
                component.data.chineseDescription = self.localization.get_item_description(component.localName)
                if component.data.manufacturerData:
                    component.data.manufacturerData.data.chineseName = self.localization.get_manufacturer_name(
                        component.data.manufacturerData.data.calculatorName,
                        component.data.manufacturerData.data.nameSmall,
                        component.data.chineseDescription)
            return components_list

        return wrapper

    def translate_vehicle(func: Callable[['Loader'], list[ComponentData]], *args, **kwargs) -> Callable[
        ['Loader'], list[ComponentData]]:
        def wrapper(self: 'Loader') -> list[ComponentData]:
            components_list: list[ComponentData] = func(self)
            for component in components_list:
                component.data.chineseNameShort = None
                component.data.chineseName = self.localization.get_vehicle_name(component.localName)
                component.data.chineseDescription = self.localization.get_vehicle_description(component.localName)
                if component.data.manufacturerData:
                    component.data.manufacturerData.data.chineseName = self.localization.get_manufacturer_name(
                        component.data.manufacturerData.data.calculatorName,
                        component.data.manufacturerData.data.nameSmall,
                        component.data.chineseDescription)
            return components_list

        return wrapper

    @translate_component
    def load_missiles(self) -> list[Missile]:
        with open(self.missile_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return [Missile(**d) for d in data]

    @translate_component
    def load_bombs(self) -> list[Bomb]:
        with open(self.bomb_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return [Bomb(**d) for d in data]

    @translate_component
    def load_shields(self) -> list[Shield]:
        with open(self.shield_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        for d in data:
            d['data']['itemClass'] = d['data']['class']
        return [Shield(**d) for d in data]

    @translate_component
    def load_coolers(self) -> list[Cooler]:
        with open(self.cooler_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        for d in data:
            d['data']['itemClass'] = d['data']['class']
        return [Cooler(**d) for d in data]

    @translate_component
    def load_weapons(self) -> list[Weapon]:
        with open(self.weapon_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return [Weapon(**d) for d in data]

    @translate_component
    def load_emps(self) -> list[EMP]:
        with open(self.emp_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return [EMP(**d) for d in data]

    @translate_component
    def load_mining_lasers(self) -> list[MiningLaser]:
        with open(self.mining_laser_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return [MiningLaser(**d) for d in data]

    @translate_component
    def load_mounts(self) -> list[Mount]:
        with open(self.mount_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return [Mount(**d) for d in data]

    @translate_component
    def load_power_plants(self) -> list[PowerPlant]:
        with open(self.power_plant_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        for d in data:
            if 'class' in d['data']:
                d['data']['itemClass'] = d['data']['class']
        return [PowerPlant(**d) for d in data]

    @translate_component
    def load_qdrives(self) -> list[QDrive]:
        with open(self.qdrive_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        for d in data:
            if 'class' in d['data']:
                d['data']['itemClass'] = d['data']['class']
        return [QDrive(**d) for d in data]

    @translate_component
    def load_qeds(self) -> list[Qed]:
        with open(self.qed_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        for d in data:
            if 'class' in d['data']:
                d['data']['itemClass'] = d['data']['class']
        return [Qed(**d) for d in data]

    @translate_component
    def load_utilities(self) -> list[Utility]:
        with open(self.utility_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return [Utility(**d) for d in data]

    @translate_component
    def load_paints(self) -> list[Paint]:
        with open(self.paint_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return [Paint(**d) for d in data]

    @translate_vehicle
    def load_ships(self) -> list[Ship]:
        with open(self.ship_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return [Ship(**d) for d in data]

    @translate_component
    def load_missile_racks(self) -> list[MissileRack]:
        with open(self.missile_rack_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return [MissileRack(**d) for d in data]

    def load_shops(self) -> list[Shop]:
        with open(self.shop_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        shops: list[Shop] = [Shop(**d) for d in data]
        for shop in shops:
            shop.data.nameChinese = self.localization.get_translation(shop.data.name)
            shop.data.locationChinese = self.localization.get_translation(shop.data.location)
        return shops

    def load_all(self):
        self.weapons = self.load_weapons()
        self.missiles = self.load_missiles()
        self.ships = self.load_ships()
        self.shops = self.load_shops()
        self.bombs = self.load_bombs()
        self.shields = self.load_shields()
        self.coolers = self.load_coolers()
        self.emps = self.load_emps()
        self.mining_lasers = self.load_mining_lasers()
        self.mounts = self.load_mounts()
        self.power_plants = self.load_power_plants()
        self.qdrives = self.load_qdrives()
        self.qeds = self.load_qeds()
        self.utilities = self.load_utilities()
        self.paints = self.load_paints()
        self.missile_racks = self.load_missile_racks()
        for ship in self.ships:
            ship.isFlyable = True
        # self.match_loaner_ships()

    def find_ship_by_name(self, name: str) -> Optional[Ship]:
        for ship in self.ships:
            if ship.data.name == name:
                return ship
        input(f"找不到{name}的借用船, 请输入借用船名称，跳过请按输入q:")
        if name == "q":
            return None
        else:
            for ship in self.ships:
                if ship.data.name == name:
                    return ship
        return None

    def match_loaner_ships(self):
        with open(self.loaner_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        for ship_name in data:
            loaner_ship = self.find_ship_by_name(ship_name)
            if loaner_ship is None:
                continue
            for loaned_ship_name in data[ship_name]:
                loaned_ship = self.find_ship_by_name(loaned_ship_name)
                if loaned_ship is None:
                    continue
                loaner_ship.loanerShips.append(loaned_ship.data.name)

    def save_all(self):
        archive = Archive(
            weapons=self.weapons,
            missiles=self.missiles,
            ships=self.ships,
            shops=self.shops,
            bombs=self.bombs,
            shields=self.shields,
            coolers=self.coolers,
            emps=self.emps,
            mining_lasers=self.mining_lasers,
            mounts=self.mounts,
            power_plants=self.power_plants,
            quantum_drives=self.qdrives,
            qeds=self.qeds,
            utilities=self.utilities,
            paints=self.paints,
            missile_racks=self.missile_racks
        )
        with open(self.archive_path, "w", encoding="utf-8") as f:
            json.dump(archive.dict(), f, ensure_ascii=False, indent=4)

    def load_from_archive(self):
        with open(self.archive_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        archive = Archive(**data)
        self.weapons = archive.weapons
        self.missiles = archive.missiles
        self.ships = archive.ships
        self.shops = archive.shops
        self.bombs = archive.bombs
        self.shields = archive.shields
        self.coolers = archive.coolers
        self.emps = archive.emps
        self.mining_lasers = archive.mining_lasers
        self.mounts = archive.mounts
        self.power_plants = archive.power_plants
        self.qdrives = archive.quantum_drives
        self.qeds = archive.qeds
        self.utilities = archive.utilities
        self.paints = archive.paints
        self.missile_racks = archive.missile_racks


if __name__ == "__main__":
    is_debug = True
    loader = Loader()
