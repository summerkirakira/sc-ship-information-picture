from PIL import Image, ImageDraw, ImageFont
from models import Sheet, ComponentData, Weapon, SearchItem, Weapon, Shield, Missile, EMP, PowerPlant, QDrive, Ship, ShipNameBinding, Mount, MissileRack
from translation import Translation
from calculator import Calculator
import pathlib
import logging
import abc
from generate_fake_ship import load_fake_ship
from pathlib import Path
from typing import Union
from typing import Optional
import json

ship_name_binding_path = pathlib.Path(__file__).parent / "data" / "ship_name_binding.json"

ship_pic_path = pathlib.Path('/Users/forever/Documents/Code/ship-render')

icon_path = pathlib.Path(__file__).parent / "data" / "image"

with open(ship_name_binding_path, 'r') as f:
    data = json.load(f)
    ship_name_binding = [ShipNameBinding(**d) for d in data]


def get_binding_by_local_name(local_name: str) -> Optional[ShipNameBinding]:
    for binding in ship_name_binding:
        if binding.local_name == local_name:
            return binding
    return None


def convert_size_info(size_info: list[int]) -> str:
    size_dict = {}
    for size in size_info:
        if size in size_dict:
            size_dict[size] += 1
        else:
            size_dict[size] = 1
    size_str = ''
    for size in size_dict:
        size_str += f'{size_dict[size]}S{size} '
    return size_str


class PicDrawer:
    def __init__(self):
        self.font_path: pathlib.Path = pathlib.Path(__file__).parent / "data" / "fonts" / "WeiRuanYaHei.ttf"
        self.font = ImageFont.truetype(str(self.font_path), size=24)
        self.font_big = ImageFont.truetype(str(self.font_path), size=32)
        self.font_bigger = ImageFont.truetype(str(self.font_path), size=48)
        self.width = 1400
        self.draw = ImageDraw.Draw(Image.new('RGB', (1, 1)))
        self.watermark_path = pathlib.Path(__file__).parent / "data" / "image" / "watermark.png"

        self.watermark = Image.open(str(self.watermark_path)).convert("RGBA")

    def get_font_render_size(self, text: str, font: ImageFont) -> tuple[int, int]:
        """
        Returns the size of the text rendered with the given font
        :param text: the text
        :param font: the font
        :return: the size of the text rendered with the given font
        """
        box = self.draw.textbbox((0, 0), text=text, font=font)
        return box[2] - box[0], box[3] - box[1]

    @classmethod
    def draw_text(cls, draw: ImageDraw, text: str, x: int, y: int, font: ImageFont, fill=(0, 0, 0)):
        """
        Draws the text with the given font at the given position
        :param fill:
        :param draw: the ImageDraw object
        :param text: the text
        :param x: the x position
        :param y: the y position
        :param font: the font
        :return:
        """
        draw.text((x, y), text, font=font, fill=fill)

    @classmethod
    def add_watermark_png(cls, image: Image, water_mark: Image):
        """
        Adds a watermark to the given image
        :param image: the image
        :param water_mark: the watermark
        :return: the image with the watermark
        """
        image.paste(water_mark, (image.width - water_mark.width, image.height - water_mark.height), water_mark)
        return image

    def draw_sheet(self, sheet: Sheet) -> Image:
        """
        Draws a sheet with the given data
        :param sheet: the sheet
        :return:
        """
        sheet_height = sheet.row_height * len(sheet.columns) + sheet.header_height
        sheet_pic = Image.new('RGB', (sheet.width, sheet_height), (255, 255, 255))
        title_size = self.get_font_render_size(sheet.title, self.font_bigger)
        draw = ImageDraw.Draw(sheet_pic)
        self.draw_text(draw,
                       sheet.title,
                       int((sheet.width - title_size[0]) / 2),
                       -5 + int((sheet.header_height - title_size[1]) / 2),
                       self.font_bigger)
        true_width: int = sheet.width - sheet.margin * 2
        current_row: int = 0
        current_width_position: float = 0
        current_column: int = 0
        for row_position in range(len(sheet.columns)):
            current_color: str = sheet.colors[row_position % len(sheet.colors)]
            draw.rectangle(((0, row_position * sheet.row_height + sheet.header_height),
                            (sheet.width, (row_position + 1) * sheet.row_height + sheet.header_height)),
                           fill=current_color,
                           width=0)

        for column in sheet.columns:
            for word in column.data:
                word_size = self.get_font_render_size(word, self.font)
                self.draw_text(draw,
                               word,
                               int(current_width_position * true_width) + sheet.margin,
                               -5 + sheet.header_height + current_row * sheet.row_height + int((sheet.row_height - word_size[1]) / 2),
                               self.font)
                current_width_position += sheet.width_ratio[current_column]
                current_column += 1
            current_row += 1
            current_width_position = 0
            current_column = 0
        self.add_watermark_png(sheet_pic, self.watermark)
        return sheet_pic

    class ComponentDrawer:
        def __init__(self, data: ComponentData, calculator: Calculator):
            self.default_font_path: pathlib.Path = pathlib.Path(__file__).parent / "data" / "fonts" / "WeiRuanYaHei.ttf"
            self.default_font = ImageFont.truetype(str(self.default_font_path), size=55)
            self.width = 4961
            self.height = 2480
            self.pic = Image.new('RGBA', (self.width, self.height), (76, 75, 74))
            self.drawer = ImageDraw.Draw(self.pic)
            self.pic_path = pathlib.Path("/Users/forever/Documents/SC PIC/item_pics")
            self.data = data
            self.calculator = calculator

        def get_shop_data(self) -> SearchItem:
            return self.calculator.find_item_by_ref(self.data.data.ref)

        def add_frame(self) -> Image:
            frame_path = pathlib.Path(__file__).parent / "data" / "image" / "frame.png"
            frame = Image.open(str(frame_path)).convert("RGBA")
            self.pic.paste(frame, (0, 0), frame)
            self.drawer.rectangle(((2650, 1840), (2650 + 480, 1840 + 480)), outline="white", width=11)
            self.drawer.rectangle(((3220, 1840), (3220 + 1000, 1840 + 480)), outline="white", width=11)
            self.drawer.rectangle(((4300, 1840), (4300 + 480, 1840 + 480)), outline="white", width=11)

            self.drawer.line(((2650 + 40, 1840 + 240), (2650 + 480 - 40, 1840 + 240)), fill="white", width=11)
            self.drawer.line(((3220 + 40, 1840 + 240), (3220 + 1000 - 40, 1840 + 240)), fill="white", width=11)

            self.drawer.line(((4650, 1000), (4650, 1840)), fill="white", width=5)
            return frame

        def add_background(self):
            """
            tile the background image
            :return:
            """
            background_path = pathlib.Path(__file__).parent / "data" / "image" / "grey.gif"
            background = Image.open(str(background_path)).convert("RGBA")
            for x in range(0, self.width, background.width):
                for y in range(0, self.height, background.height):
                    self.pic.paste(background, (x, y), background)
            # block_size = 100
            # for x in range(0, self.width, block_size):
            #     for y in range(0, self.height, block_size):
            #         self.drawer.rectangle(((x, y), (x + block_size, y + block_size)), outline="white", width=1)
            pass

        def add_component_pic(self):
            try:
                component_pic_path = self.pic_path / f"{self.data.localName}.png"
                if not component_pic_path.exists():
                    component_pic_path = self.pic_path / f"{self.data.localName}_scitem.png"
                component_pic = Image.open(str(component_pic_path)).convert("RGBA")
                component_pic = self.resize(component_pic, 1.3)
                self.pic.paste(component_pic, (250, 500), component_pic)
            except FileNotFoundError:
                print(f"{self.data.localName} not found")

        def add_description(self):
            description = self.data.data.chineseDescription
            if description is None:
                description = self.data.data.description
            if description is None:
                description = ""
            description_list = description.split("\\n")
            if len(description_list) > 1:
                description = description_list[-1]
            self.add_text_block(description, x=250, y=2000, width=2000, font=self.default_font)

        def add_chinese_name(self):
            title_font = ImageFont.truetype(str(self.default_font_path), size=150)
            if self.data.data.chineseName:
                self.add_reversed_text(self.data.data.chineseName, x=4270, y=300, font=title_font)
            else:
                self.add_reversed_text(self.data.data.name, x=4270, y=300, font=title_font)
            pass

        def add_english_name(self):
            title_font = ImageFont.truetype(str(self.default_font_path), size=100)
            self.add_reversed_text(self.data.data.name, x=4270, y=500, font=title_font)
            pass

        def add_general_type(self):
            font = ImageFont.truetype(str(self.default_font_path), size=150)
            self.drawer.text((4400, 1960), "??????", font=font, fill="white")

        def add_manufacturer_chinese_name(self):
            font = ImageFont.truetype(str(self.default_font_path), size=110)
            if not self.data.data.manufacturerData.data.chineseName:
                self.data.data.manufacturerData.data.chineseName = self.data.data.name
            while font.getlength(self.data.data.manufacturerData.data.chineseName) > 1000:
                font = ImageFont.truetype(str(self.default_font_path), size=font.size - 1)
            text = self.data.data.manufacturerData.data.chineseName
            if text.startswith("??????"):
                text = "????????????"
            elif text.startswith("??????"):
                text = "????????????????????????"
            self.add_text_center(text, x=3710, y=1885, font=font)
            pass

        def add_manufacturer_english_name(self):
            font = ImageFont.truetype(str(self.default_font_path), size=110)
            text = self.data.data.manufacturerData.data.name
            if text.startswith("Musashi"):
                text = text.split("&")[0]
            elif text.startswith("Roberts"):
                text = "Roberts Space Industries"
            while font.getlength(text) > 900:
                font = ImageFont.truetype(str(self.default_font_path), size=font.size - 1)
            # get the height of the font
            bbox = self.drawer.textbbox((0, 0), text, font=font)
            height = bbox[3] - bbox[1]
            self.add_text_center(text, x=3710, y=2190 - int(height / 2), font=font)
            # self.add_text_center(text, x=3710, y=2110, font=font)
            pass

        def add_type(self):
            font = ImageFont.truetype(str(self.default_font_path), size=110)
            "change size number to roman numerals"
            if self.data.data.size == 1:
                text = "I"
            elif self.data.data.size == 2:
                text = "II"
            elif self.data.data.size == 3:
                text = "III"
            elif self.data.data.size == 4:
                text = "IV"
            elif self.data.data.size == 5:
                text = "V"
            elif self.data.data.size == 6:
                text = "VI"
            elif self.data.data.size == 7:
                text = "VII"
            elif self.data.data.size == 8:
                text = "VIII"
            elif self.data.data.size == 9:
                text = "IX"
            elif self.data.data.size == 10:
                text = "X"
            else:
                text = f"{self.data.data.size}"
            if text is None:
                text = "-"
            while font.getlength(text) > 470:
                font = ImageFont.truetype(str(self.default_font_path), size=font.size - 1)
            self.add_text_center(text, x=2880, y=1885, font=font, fill=(255, 140, 64))
            pass

        def add_subtype(self):
            font = ImageFont.truetype(str(self.default_font_path), size=110)
            text = Translation.get_translation(self.data.data.subType)
            if text is None:
                text = "-"
            while font.getlength(text) > 470:
                font = ImageFont.truetype(str(self.default_font_path), size=font.size - 1)
            self.add_text_center(text, x=2880, y=2110, font=font)
            pass

        def add_shop_infos(self):
            shop_info: SearchItem = self.get_shop_data()
            if shop_info is None:
                return
            font = ImageFont.truetype(str(self.default_font_path), size=80)
            price_font = ImageFont.truetype(str(self.default_font_path), size=100)
            if len(shop_info.results) > 4:
                shop_info.results = shop_info.results[:4]
            x = 4270
            start_y = 1500
            if len(shop_info.results) > 0:
                self.add_reversed_text(f"{shop_info.results[0].item.basePrice}aUEC",
                                       x=x,
                                       y=start_y - len(shop_info.results) * 250 + 130,
                                       font=price_font, fill=(255, 140, 64))
            for i, result in enumerate(shop_info.results):
                if result.shop.data.nameChinese:
                    self.add_reversed_text(result.shop.data.nameChinese, x=x, y=start_y - i * 250, font=font)
                else:
                    self.add_reversed_text("??????", x=x, y=start_y - i * 250, font=font)
                if result.shop.data.locationChinese:
                    self.add_reversed_text(result.shop.data.locationChinese, x=x, y=start_y - i * 250 + 100, font=font)
                else:
                    self.add_reversed_text(result.shop.data.location, x=x, y=start_y - i * 250 + 100, font=font)
                if i != len(shop_info.results) - 1:
                    self.drawer.line(((x - 600, start_y - i * 250 - 15),
                                      (x, start_y - i * 250 - 15)),
                                     fill="white",
                                     width=5)

        @abc.abstractmethod
        def add_details(self):
            pass

        def add_signature(self):
            signature_path = pathlib.Path(__file__).parent / "data" / "image" / "signature.png"
            signature = Image.open(str(signature_path)).convert("RGBA")
            self.pic.paste(signature, (self.width - signature.width - 60, 20), signature)

        def draw(self, pic_path: pathlib.Path):
            self.add_background()
            self.add_frame()
            self.add_component_pic()
            self.add_general_type()
            self.add_chinese_name()
            self.add_english_name()
            self.add_manufacturer_chinese_name()
            self.add_manufacturer_english_name()
            self.add_type()
            self.add_subtype()
            self.add_description()
            self.add_shop_infos()
            self.add_details()
            self.add_signature()
            self.save(pic_path)
            print(f"{self.data.data.chineseName} ({self.data.data.name}) saved")

        def save(self, pic_path: pathlib.Path):
            self.pic.save(str(pic_path / f"{self.data.data.ref}.png"))

        @classmethod
        def resize(cls, image: Image, ratio: float) -> Image:
            return image.resize((int(image.width * ratio), int(image.height * ratio)))

        def add_text_block(self, text: str, x: int, y: int, font: ImageFont, width: int, fill=(255, 255, 255)):
            """
            Draws the text with the given font at the given position
            :param width: the width of the text block
            :param fill: the fill color of the text
            :param text: the text
            :param x: the x position
            :param y: the y position
            :param font: the font
            :return:
            """
            processed_text = ""
            current_width = 0
            for item in text:
                if current_width > width:
                    processed_text += "\n"
                    current_width = 0
                current_width = current_width + font.getlength(item)
                processed_text += item
            self.drawer.text((x, y), processed_text, font=font, fill=fill)

        def add_reversed_text(self, text: str, x: int, y: int, font: ImageFont, fill=(255, 255, 255)):
            text = str(text)
            text_length = font.getlength(text)
            self.drawer.text((x - text_length, y), text, font=font, fill=fill)

        def add_text_center(self, text: str, x: int, y: int, font: ImageFont, fill=(255, 255, 255)):
            text_length = font.getlength(text)
            self.drawer.text((x - text_length / 2, y), text, font=font, fill=fill)


class WeaponDrawer(PicDrawer.ComponentDrawer):

    def __init__(self, data: Weapon, calculator: Calculator):
        super().__init__(data, calculator)
        self.data = data

    def add_details(self):
        self.add_ammo_amount()
        self.add_physical_info()
        self.add_distortion_info()
        self.add_damage_info()
        self.add_power_info()
        self.add_dps_info()

    def add_ammo_amount(self):
        ammo_path = pathlib.Path(__file__).parent / "data" / "image" / "ammo.png"
        ammo_pic = Image.open(str(ammo_path)).convert("RGBA")
        ammo_pic = self.resize(ammo_pic, 0.4)
        self.pic.paste(ammo_pic, (200, 300), ammo_pic)
        if self.data.data.ammoContainer.initialAmmoCount > 0:
            font = ImageFont.truetype(str(self.default_font_path), size=190)
            self.drawer.text((400, 290),
                             str(self.data.data.ammoContainer.initialAmmoCount),
                             font=font,
                             fill=(255, 140, 64))
        else:
            font = ImageFont.truetype(str(self.default_font_path), size=350)
            self.drawer.text((420, 160),
                             "???",
                             font=font,
                             fill=(255, 140, 64))

    def add_physical_info(self):
        text = f"??????: {self.data.data.health}??????\n??????: {self.data.data.mass}??????"
        self.drawer.text((200, 660), text, font=self.default_font)
        self.drawer.line(((580, 790), (580 + 100, 790 + 66)), fill="white", width=5)

    def add_distortion_info(self):
        text = f"????????????: {self.data.data.distortion.maximum}??????\n" \
               f"????????????: {self.data.data.distortion.decayRate}??????/???\n" \
               f"????????????: {self.data.data.distortion.decayDelay}???\n" \
               f"?????????: {self.data.data.distortion.recoveryRatio}"
        self.drawer.text((1700, 1600), text, font=self.default_font)
        self.drawer.line(((1550, 1550), (1550 + 120, 1550 + 190)), fill="white", width=5)

    def add_damage_info(self):

        text = f"????????????: {self.data.data.weapon.fireActions.ammoCost}???/???\n" \
               f"??????: {self.data.data.ammo.data.speed}???/???\n" \
               f"????????????: "
        damage_list: list[str] = []
        if self.data.data.ammo.data.damage.damageEnergy > 0:
            text += "????????"
            damage_list.append(f"????????????: {self.data.data.ammo.data.damage.damageEnergy}??????/???")
        if self.data.data.ammo.data.damage.damagePhysical > 0:
            text += "????????"
            damage_list.append(f"????????????: {self.data.data.ammo.data.damage.damagePhysical}??????/???")
        if self.data.data.ammo.data.damage.damageDistortion > 0:
            text += "????????"
            damage_list.append(f"????????????: {self.data.data.ammo.data.damage.damageDistortion}??????/???")
        if self.data.data.ammo.data.damage.damageThermal > 0:
            text += "????????"
            damage_list.append(f"????????????: {self.data.data.ammo.data.damage.damageThermal}??????/???")
        if self.data.data.ammo.data.damage.damageBiochemical > 0:
            text += "????????"
            damage_list.append(f"????????????: {self.data.data.ammo.data.damage.damageBiochemical}??????/???")
        if self.data.data.ammo.data.damage.damageStun > 0:
            text += "????????"
            damage_list.append(f"????????????: {self.data.data.ammo.data.damage.damageStun}??????/???")
        if text.endswith("??"):
            text = text[:-1]
            text += "\n"
            text += "\n".join(damage_list)
        if len(damage_list) == 0:
            text = text.replace("????????????: ", "")
            self.drawer.text((2290, 1370), text, font=self.default_font)
        else:
            self.drawer.text((2290, 1250), text, font=self.default_font)
        self.drawer.line(((2100, 1300), (2100 + 135, 1300 + 130)), fill="white", width=5)

    def add_power_info(self):
        text = f"????????????: {self.data.data.power.powerDraw}??????/???\n" \
               f"??????EM??????: {self.data.data.power.powerToEM}\n" \
               f"????????????: {self.data.data.heat.mass}??????/???\n" \
               f"????????????: {self.data.data.heat.maxCoolingRate}??????/???\n" \
               f"??????IR??????: {self.data.data.heat.temperatureToIR}"
        if self.data.data.weapon.regen:
            text += "\n" \
                   f"????????????: {self.data.data.weapon.regen.requestedRegenPerSec}??????/???\n" \
                   f"????????????: {self.data.data.weapon.regen.regenerationCooldown}???"
        self.drawer.text((2800, 900), text, font=self.default_font)
        self.drawer.line(((2600, 1000), (2600 + 120, 1000 + 70)), fill="white", width=5)

    def add_dps_info(self):
        text = f"??????: {self.data.data.weapon.fireActions.fireRate}???/???\n" \
               f"??????: {round(self.data.data.ammo.data.lifetime * self.data.data.ammo.data.speed)}???\n" \
               f"????????????: {self.data.data.weapon.damage.alphaMax}??????\n"
        self.drawer.text((1200, 350), text, font=self.default_font)
        self.drawer.line(((1370, 570), (1370 + 120, 570 + 90)), fill="white", width=5)

    def add_subtype(self):
        font = ImageFont.truetype(str(self.default_font_path), size=110)
        text = Translation.get_translation(self.data.data.group)
        if text is None:
            text = self.data.data.group
        while font.getlength(text) > 400:
            font = ImageFont.truetype(str(self.default_font_path), size=font.size - 1)
        self.add_text_center(text, x=2890, y=2130, font=font)
        pass

    def add_general_type(self):
        font = ImageFont.truetype(str(self.default_font_path), size=150)
        self.drawer.text((4400, 1960), "??????", font=font, fill="white")


class ShieldDrawer(PicDrawer.ComponentDrawer):

    def add_details(self):
        self.add_power_info()
        self.add_shield_info()
        self.add_distortion_info()
        self.add_physical_info()
        self.add_class_info()
        pass

    def add_shield_info(self):

        text = f"????????????: {self.data.data.shield.maxShieldHealth}??????\n" \
               f"????????????: {self.data.data.shield.maxShieldRegen}??????/???\n" \
               f"??????????????????: {self.data.data.shield.damagedRegenDelay}??????/???\n" \
               f"??????????????????: {self.data.data.shield.downedRegenDelay}??????/???\n"
        self.drawer.text((2390, 1350), text, font=self.default_font)
        self.drawer.line(((2200, 1400), (2200 + 135, 1350 + 130)), fill="white", width=5)

    def add_physical_info(self):
        text = f"??????: {self.data.data.health}??????\n??????: {self.data.data.mass}??????"
        self.drawer.text((170, 660), text, font=self.default_font)
        self.drawer.line(((550, 790), (550 + 100, 790 + 66)), fill="white", width=5)

    def add_distortion_info(self):
        text = f"????????????: {self.data.data.distortion.maximum}??????\n" \
               f"????????????: {self.data.data.distortion.decayRate}??????/???\n" \
               f"????????????: {self.data.data.distortion.decayDelay}???\n" \
               f"?????????: {self.data.data.distortion.recoveryRatio}"
        self.drawer.text((1800, 1700), text, font=self.default_font)
        self.drawer.line(((1700, 1700), (1650 + 120, 1650 + 190)), fill="white", width=5)

    def add_power_info(self):
        text = f"????????????: {self.data.data.power.powerDraw}??????/???\n" \
               f"??????EM??????: {self.data.data.power.powerToEM}\n" \
               f"????????????: {self.data.data.heat.mass}??????/???\n" \
               f"????????????: {self.data.data.heat.maxCoolingRate}??????/???\n" \
               f"??????IR??????: {self.data.data.heat.temperatureToIR}"
        self.drawer.text((2800, 900), text, font=self.default_font)
        self.drawer.line(((2600, 1000), (2600 + 120, 1000 + 70)), fill="white", width=5)

    def add_class_info(self):
        text = f"??????: {Translation.get_translation(self.data.data.itemClass)}\n" \
               f"??????: {self.data.data.grade}"
        self.drawer.text((1200, 350), text, font=self.default_font)
        self.drawer.line(((1370, 520), (1370 + 120, 520 + 90)), fill="white", width=5)

    def __init__(self, shield: Shield, calculator: Calculator):
        super().__init__(shield, calculator)
        self.data = shield

    def add_general_type(self):
        font = ImageFont.truetype(str(self.default_font_path), size=150)
        self.drawer.text((4400, 1960), "??????", font=font, fill="white")

    def add_subtype(self):
        font = ImageFont.truetype(str(self.default_font_path), size=110)
        text = "??????"
        while font.getlength(text) > 400:
            font = ImageFont.truetype(str(self.default_font_path), size=font.size - 1)
        self.add_text_center(text, x=2890, y=2110, font=font)
        pass


class MissileDrawer(PicDrawer.ComponentDrawer):
    def add_details(self):
        self.add_damage_info()
        self.add_tracking_info()
        self.add_physical_info()
        pass

    def __init__(self, data: Missile, calculator: Calculator):
        super().__init__(data, calculator)
        self.data = data
        pass

    def draw(self, pic_path: pathlib.Path):
        super().draw(pic_path)
        # self.pic.show()

    def add_damage_info(self):
        text = f"????????????: {self.data.data.missile.linearSpeed}???/???\n" \
               f"????????????: "
        damage_list: list[str] = []
        if self.data.data.missile.damage.damageEnergy > 0:
            text += "????????"
            damage_list.append(f"????????????: {self.data.data.missile.damage.damageEnergy}??????")
        if self.data.data.missile.damage.damagePhysical > 0:
            text += "????????"
            damage_list.append(f"????????????: {self.data.data.missile.damage.damagePhysical}??????")
        if self.data.data.missile.damage.damageDistortion > 0:
            text += "????????"
            damage_list.append(f"????????????: {self.data.data.missile.damage.damageDistortion}??????")
        if self.data.data.missile.damage.damageThermal > 0:
            text += "????????"
            damage_list.append(f"????????????: {self.data.data.missile.damage.damageThermal}??????")
        if self.data.data.missile.damage.damageBiochemical > 0:
            text += "????????"
            damage_list.append(f"????????????: {self.data.data.missile.damage.damageBiochemical}??????")
        if self.data.data.missile.damage.damageStun > 0:
            text += "????????"
            damage_list.append(f"????????????: {self.data.data.missile.damage.damageStun}??????")
        if text.endswith("??"):
            text = text[:-1]
            text += "\n"
            text += "\n".join(damage_list)
        text += f"\n????????????{self.data.data.missile.explosionSafetyDistance}???"
        if len(damage_list) == 0:
            text = text.replace("????????????: ", "")
            self.drawer.text((2290, 1370), text, font=self.default_font)
        else:
            self.drawer.text((2290, 1350), text, font=self.default_font)
        self.drawer.line(((2100, 1300), (2100 + 135, 1300 + 130)), fill="white", width=5)

    def add_tracking_info(self):
        text = f"??????????????????: {self.data.data.missile.lockRangeMax}???\n" \
               f"??????????????????: {self.data.data.missile.lockRangeMin}???\n" \
               f"????????????: {self.data.data.missile.lockTime}???\n" \
               f"????????????: {self.data.data.missile.lockingAngle}???\n" \
               f"??????????????????: {self.data.data.missile.lockSignalAmplifier}\n"
        self.drawer.text((900, 350), text, font=self.default_font)
        self.drawer.line(((1370, 570), (1370 + 120, 570 + 90)), fill="white", width=5)

    def add_physical_info(self):
        text = f"??????: {self.data.data.health}??????\n" \
               f"??????: {self.data.data.mass}??????\n" \
               f"??????: {self.data.data.missile.fuelTankSize}??????\n"
        self.drawer.text((200, 660), text, font=self.default_font)
        self.drawer.line(((580, 790), (580 + 100, 790 + 66)), fill="white", width=5)

    def add_subtype(self):
        font = ImageFont.truetype(str(self.default_font_path), size=110)
        text = Translation.get_translation(self.data.data.missile.trackingSignalType)
        if text is None:
            text = self.data.data.missile.trackingSignalType
        while font.getlength(text) > 400:
            font = ImageFont.truetype(str(self.default_font_path), size=font.size - 1)
        self.add_text_center(text, x=2890, y=2130, font=font)

    def add_general_type(self):
        font = ImageFont.truetype(str(self.default_font_path), size=150)
        self.drawer.text((4400, 1960), "??????", font=font, fill="white")


class EMPDrawer(PicDrawer.ComponentDrawer):

    def add_details(self):
        self.add_distortion_info()
        self.add_physical_info()
        self.add_emp_info()
        self.add_power_info()
        self.add_damage_info()
        pass

    def __init__(self, data: EMP, calculator: Calculator):
        super().__init__(data, calculator)
        self.data = data
        pass

    def add_distortion_info(self):
        text = f"????????????: {self.data.data.distortion.maximum}??????\n" \
               f"????????????: {self.data.data.distortion.decayRate}??????/???\n" \
               f"????????????: {self.data.data.distortion.decayDelay}???\n" \
               f"?????????: {self.data.data.distortion.recoveryRatio}"
        self.drawer.text((1800, 1700), text, font=self.default_font)
        self.drawer.line(((1700, 1700), (1650 + 120, 1650 + 190)), fill="white", width=5)

    def add_physical_info(self):
        text = f"??????: {self.data.data.health}??????\n??????: {self.data.data.mass}??????"
        self.drawer.text((200, 660), text, font=self.default_font)
        self.drawer.line(((580, 790), (580 + 100, 790 + 66)), fill="white", width=5)

    def add_emp_info(self):
        text = f"????????????: {self.data.data.emp.chargeTime}???\n" \
               f"????????????: {self.data.data.emp.cooldownTime}???\n" \
               f"????????????: {self.data.data.emp.unleashTime}???\n"
        self.drawer.text((900, 350), text, font=self.default_font)
        self.drawer.line(((1370, 570), (1370 + 120, 570 + 90)), fill="white", width=5)

    def add_power_info(self):
        text = f"????????????: {self.data.data.power.powerDraw}??????/???\n" \
               f"??????EM??????: {self.data.data.power.powerToEM}\n" \
               f"????????????: {self.data.data.heat.mass}??????/???\n" \
               f"????????????: {self.data.data.heat.maxCoolingRate}??????/???\n" \
               f"??????IR??????: {self.data.data.heat.temperatureToIR}"
        self.drawer.text((2800, 900), text, font=self.default_font)
        self.drawer.line(((2600, 1000), (2600 + 120, 1000 + 70)), fill="white", width=5)

    def add_damage_info(self):
        text = f"EMP??????: {self.data.data.emp.empRadius}???\n" \
               f"EMP??????: {self.data.data.emp.distortionDamage}??????\n"
        self.drawer.text((2290, 1370), text, font=self.default_font)
        self.drawer.line(((2100, 1300), (2100 + 135, 1300 + 130)), fill="white", width=5)

    def add_general_type(self):
        font = ImageFont.truetype(str(self.default_font_path), size=150)
        self.drawer.text((4400, 1960), "EMP", font=font, fill="white")

    def add_subtype(self):
        font = ImageFont.truetype(str(self.default_font_path), size=110)
        text = "A"
        while font.getlength(text) > 470:
            font = ImageFont.truetype(str(self.default_font_path), size=font.size - 1)
        self.add_text_center(text, x=2880, y=2110, font=font)
        pass


class PowerPlantDrawer(PicDrawer.ComponentDrawer):

    def add_details(self):
        self.add_power_info()
        self.add_distortion_info()
        self.add_physical_info()
        self.add_class_info()
        pass

    def __init__(self, data: PowerPlant, calculator: Calculator):
        super().__init__(data, calculator)
        self.data = data

    def add_power_info(self):
        text = f"??????: {self.data.data.power.powerDraw}??????/???\n" \
               f"??????EM??????: {self.data.data.power.powerToEM}\n" \
               f"????????????: {self.data.data.heat.mass}??????/???\n" \
               f"????????????: {self.data.data.heat.maxCoolingRate}??????/???\n" \
               f"??????IR??????: {self.data.data.heat.temperatureToIR}"
        self.drawer.text((2700, 900), text, font=self.default_font)
        self.drawer.line(((2500, 1000), (2500 + 120, 1000 + 70)), fill="white", width=5)

    def add_distortion_info(self):
        text = f"????????????: {self.data.data.distortion.maximum}??????\n" \
               f"????????????: {self.data.data.distortion.decayRate}??????/???\n" \
               f"????????????: {self.data.data.distortion.decayDelay}???\n" \
               f"?????????: {self.data.data.distortion.recoveryRatio}"
        self.drawer.text((1800, 1700), text, font=self.default_font)
        self.drawer.line(((1700, 1700), (1650 + 120, 1650 + 190)), fill="white", width=5)

    def add_physical_info(self):
        text = f"??????: {self.data.data.health}??????\n??????: {self.data.data.mass}??????"
        self.drawer.text((200, 660), text, font=self.default_font)
        self.drawer.line(((580, 790), (580 + 100, 790 + 66)), fill="white", width=5)

    def add_class_info(self):
        text = f"??????: {Translation.get_translation(self.data.data.itemClass)}\n" \
               f"??????: {self.data.data.grade}"
        self.drawer.text((1200, 350), text, font=self.default_font)
        self.drawer.line(((1370, 520), (1370 + 120, 520 + 90)), fill="white", width=5)

    def add_general_type(self):
        font = ImageFont.truetype(str(self.default_font_path), size=150)
        self.drawer.text((4400, 1960), "??????", font=font, fill="white")

    def add_subtype(self):
        font = ImageFont.truetype(str(self.default_font_path), size=110)
        text = "?????????"
        while font.getlength(text) > 470:
            font = ImageFont.truetype(str(self.default_font_path), size=font.size - 1)
        self.add_text_center(text, x=2880, y=2110, font=font)
        pass


class QDriveDrawer(PicDrawer.ComponentDrawer):

    def __init__(self, data: QDrive, calculator: Calculator):
        super().__init__(data, calculator)
        self.data = data

    def add_details(self):
        self.add_power_info()
        self.add_distortion_info()
        self.add_physical_info()
        self.add_class_info()
        self.add_qdrive_info()
        pass

    def add_power_info(self):
        text = f"??????: {self.data.data.power.powerDraw}??????/???\n" \
               f"??????EM??????: {self.data.data.power.powerToEM}\n" \
               f"????????????: {self.data.data.heat.mass}??????/???\n" \
               f"????????????: {self.data.data.heat.maxCoolingRate}??????/???\n" \
               f"??????IR??????: {self.data.data.heat.temperatureToIR}"
        self.drawer.text((2700, 900), text, font=self.default_font)
        self.drawer.line(((2500, 1000), (2500 + 120, 1000 + 70)), fill="white", width=5)

    def add_distortion_info(self):
        text = f"????????????: {self.data.data.distortion.maximum}??????\n" \
               f"????????????: {self.data.data.distortion.decayRate}??????/???\n" \
               f"????????????: {self.data.data.distortion.decayDelay}???\n" \
               f"?????????: {self.data.data.distortion.recoveryRatio}"
        self.drawer.text((1800, 1700), text, font=self.default_font)
        self.drawer.line(((1700, 1700), (1650 + 120, 1650 + 190)), fill="white", width=5)

    def add_physical_info(self):
        text = f"??????: {self.data.data.health}??????\n??????: {self.data.data.mass}??????"
        self.drawer.text((200, 660), text, font=self.default_font)
        self.drawer.line(((580, 790), (580 + 100, 790 + 66)), fill="white", width=5)

    def add_class_info(self):
        text = f"??????: {Translation.get_translation(self.data.data.itemClass)}\n" \
               f"??????: {self.data.data.grade}"
        self.drawer.text((1200, 350), text, font=self.default_font)
        self.drawer.line(((1370, 520), (1370 + 120, 520 + 90)), fill="white", width=5)

    def add_qdrive_info(self):
        text = f"????????????: {self.data.data.qdrive.params.calibrationDelayInSeconds}???\n" \
               f"?????????: {self.data.data.qdrive.params.calibrationRate}\n" \
               f"????????????: {self.data.data.qdrive.params.driveSpeed}m/s({round(self.data.data.qdrive.params.driveSpeed / (3 * 10**8), 2)}C)\n" \
               f"??????????????????: {self.data.data.qdrive.params.stageOneAccelRate}m/s??\n" \
               f"??????????????????: {self.data.data.qdrive.params.stageTwoAccelRate}m/s??\n" \
               f"??????????????????: {self.data.data.qdrive.quantumFuelRequirement}??????/???\n"
        self.drawer.text((2350, 1300), text, font=self.default_font)
        self.drawer.line(((2150, 1350), (2150 + 130, 1350 + 130)), fill="white", width=5)

    def add_subtype(self):
        font = ImageFont.truetype(str(self.default_font_path), size=110)
        text = "??????"
        while font.getlength(text) > 470:
            font = ImageFont.truetype(str(self.default_font_path), size=font.size - 1)
        self.add_text_center(text, x=2880, y=2110, font=font)

    def add_general_type(self):
        font = ImageFont.truetype(str(self.default_font_path), size=150)
        self.drawer.text((4400, 1960), "??????", font=font, fill="white")


class ShipDrawer(PicDrawer.ComponentDrawer):

    def __init__(self, data: Ship, calculator: Calculator):
        super().__init__(data, calculator)
        self.data = data

    def add_component_pic(self):
        try:
            pic_name = get_binding_by_local_name(self.data.localName).photo_name
            component_pic_path = ship_pic_path / f"{pic_name}.png"
            if not component_pic_path.exists():
                component_pic_path = self.pic_path / f"{self.data.localName}_scitem.png"
            component_pic = Image.open(str(component_pic_path)).convert("RGBA")
            component_pic = self.resize(component_pic, 1.3)
            self.pic.paste(component_pic, (250, 500), component_pic)
        except FileNotFoundError:
            print(f"{self.data.localName} not found")

    def add_subtype(self):
        font = ImageFont.truetype(str(self.default_font_path), size=110)
        text = Translation.get_translation(self.data.data.vehicle.career)
        if text is None:
            text = self.data.data.vehicle.career
        if text is None:
            return
        while font.getlength(text) > 400:
            font = ImageFont.truetype(str(self.default_font_path), size=font.size - 1)
        self.add_text_center(text, x=2890, y=2130, font=font)
        pass

    def add_size_info(self):
        text = f"??????: {self.data.data.vehicle.size.x}???x{self.data.data.vehicle.size.y}???x{self.data.data.vehicle.size.z}???\n"
        text += f"????????????: {self.data.data.vehicle.crewSize}???"
        self.drawer.text((710, 411), text, font=self.default_font)
        self.drawer.line(((1000, 556), (1060, 649)), fill="white", width=5)

    def find_component(self, component_type: str) -> list[Ship.Data.Loadout]:
        components = []
        for component in self.data.data.loadout:
            if component is not None:
                if component.itemTypes is not None and len(component.itemTypes) > 0:
                    if component.itemTypes[0]:
                        if component.itemTypes[0].type == component_type:
                            components.append(component)
        return components

    def add_shop_infos(self):
        shop_info: SearchItem = self.get_shop_data()
        if shop_info is None:
            return
        font = ImageFont.truetype(str(self.default_font_path), size=80)
        price_font = ImageFont.truetype(str(self.default_font_path), size=100)
        if len(shop_info.results) > 3:
            shop_info.results = shop_info.results[:3]
        x = 4270
        start_y = 1500
        if len(shop_info.results) > 0:
            self.add_reversed_text(f"{shop_info.results[0].item.basePrice}aUEC",
                                   x=x,
                                   y=start_y - len(shop_info.results) * 250 + 130,
                                   font=price_font, fill=(255, 140, 64))
        for i, result in enumerate(shop_info.results):
            self.add_reversed_text(result.shop.data.nameChinese, x=x, y=start_y - i * 250, font=font)
            self.add_reversed_text(result.shop.data.locationChinese, x=x, y=start_y - i * 250 + 100, font=font)
            if i != len(shop_info.results) - 1:
                self.drawer.line(((x - 600, start_y - i * 250 - 15),
                                  (x, start_y - i * 250 - 15)),
                                 fill="white",
                                 width=5)
    def add_speed_info(self):
        if self.data.data.ifcs is None:
            return
        text = f"????????????/???????????????: {self.data.data.ifcs.maxSpeed}???/???({self.data.data.ifcs.maxAfterburnSpeed}???/???)\n"
        text += f"??????????????????: {round(self.data.data.ifcs.afterburner.capacitorMax / self.data.data.ifcs.afterburner.capacitorAfterburnerIdleCost)}???\n"
        text += f"????????????: {int(self.data.data.ifcs.afterburner.afterburnAccelMultiplier.x * 100)}% / {int(self.data.data.ifcs.afterburner.afterburnAccelMultiplier.y * 100)}% / {int(self.data.data.ifcs.afterburner.afterburnAccelMultiplier.z * 100)}%\n"
        self.drawer.text((1515, 1728), text, font=self.default_font)
        self.drawer.line(((1786, 1600), (1876, 1703)), fill="white", width=5)

    def add_details(self):
        self.add_basic_info()
        self.add_hull_info()
        self.add_size_info()
        self.add_weapon_info()
        self.add_shield_info()
        self.add_missile_info()
        self.add_speed_info()

    def add_missile_info(self):
        font = ImageFont.truetype(str(self.default_font_path), size=70)
        text = "????????????"
        start_x = 2508
        current_y = 1418
        self.drawer.text((start_x, current_y), text, font=font, fill=(255, 140, 64))
        current_y += 100
        self.drawer.line(((2260, 1389), (start_x, current_y)), fill=(255, 140, 64), width=5)
        self.drawer.line(((start_x, current_y), (start_x + 300, current_y)), fill=(255, 140, 64), width=5)
        # find turret
        turrets = self.find_component("MissileLauncher")
        turrets_text_dict = {}
        for i, turret in enumerate(turrets):
            if turret.mount is not None:
                if turret.mount.data.chineseName is not None:
                    text = turret.mount.data.chineseName
                else:
                    text = f"S{turret.mount.data.size}?????????"
                if isinstance(turret.mount, MissileRack):
                    if turret.mount.data.ports is None:
                        continue
                    turret_size_text = f"1S{turret.mount.data.size} " + text + '[' + convert_size_info([port.maxSize for port in turret.mount.data.ports]) + '??????]'
                else:
                    turret_size_text = f"1S{turret.mount.data.size} " + text
                if turret_size_text[1:] in turrets_text_dict:
                    turrets_text_dict[turret_size_text[1:]] += int(turret_size_text[0])
                else:
                    turrets_text_dict[turret_size_text[1:]] = int(turret_size_text[0])
        turret_text_list = [str(value) + key for key, value in turrets_text_dict.items()]
        for i, text in enumerate(turret_text_list):
            self.drawer.text((start_x, current_y), text, font=self.default_font, fill="white")
            current_y += 80

    def add_weapon_info(self):
        font = ImageFont.truetype(str(self.default_font_path), size=70)
        text = "????????????"
        start_x = 2480
        current_y = 520
        self.drawer.text((start_x, current_y), text, font=font, fill=(255, 140, 64))
        self.drawer.line(((2247, 772), (2480, 614)), fill=(255, 140, 64), width=5)
        self.drawer.line(((2480, 614), (2783, 614)), fill=(255, 140, 64), width=5)
        current_y = 620
        # find turret
        turrets = self.find_component("Turret") + self.find_component("WeaponGun")
        turrets_text_dict = {}
        for i, turret in enumerate(turrets):
            if turret.mount is not None:
                if turret.mount.data.chineseName is not None:
                    text = turret.mount.data.chineseName
                else:
                    text = f"S{turret.mount.data.size}??????"
                if isinstance(turret.mount, Mount):
                    if turret.mount.data.ports is None:
                        turret_size_text = f"1S{turret.mount.data.size} " + text
                    else:
                        turret_size_text = convert_size_info([port.maxSize for port in turret.mount.data.ports]) + text
                else:
                    turret_size_text = f"1S{turret.mount.data.size} " + text
                if turret_size_text[1:] in turrets_text_dict:
                    turrets_text_dict[turret_size_text[1:]] += int(turret_size_text[0])
                else:
                    turrets_text_dict[turret_size_text[1:]] = int(turret_size_text[0])
            else:
                if turret.loadout is None:
                    continue
                for loadout in turret.loadout:
                    if loadout.component is None:
                        continue
                    turret_size_text = f"1S{loadout.component.data.size} "
                    if loadout.component.data.chineseName is not None:
                        turret_size_text += loadout.component.data.chineseName
                    else:
                        turret_size_text += loadout.component.data.name
                    if turret_size_text[1:] in turrets_text_dict:
                        turrets_text_dict[turret_size_text[1:]] += int(turret_size_text[0])
                    else:
                        turrets_text_dict[turret_size_text[1:]] = int(turret_size_text[0])
        turret_text_list = [str(value) + key for key, value in turrets_text_dict.items()]
        for i, text in enumerate(turret_text_list):
            self.drawer.text((start_x, current_y), text, font=self.default_font, fill="white")
            current_y += 80

        turrets = self.find_component("TurretBase")
        if len(turrets) == 0:
            return
        turrets_text_dict = {}
        for i, turret in enumerate(turrets):
            loadout_text = ""
            if turret.loadout is None:
                continue
            for loadout in turret.loadout:
                if loadout.component is None:
                    continue
                turret_size_text = f"1S{loadout.component.data.size} "
                if loadout.component.data.chineseName is not None:
                    turret_size_text += loadout.component.data.chineseName
                else:
                    turret_size_text += loadout.component.data.name
                if turret_size_text[1:] in turrets_text_dict:
                    turrets_text_dict[turret_size_text[1:]] += int(turret_size_text[0])
                else:
                    turrets_text_dict[turret_size_text[1:]] = int(turret_size_text[0])
        turret_text_list = [str(value) + key for key, value in turrets_text_dict.items()]
        for i, text in enumerate(turret_text_list):
            self.drawer.text((start_x, current_y), text + ' [??????]', font=self.default_font, fill="white")
            current_y += 80

    def add_shield_info(self):
        font = ImageFont.truetype(str(self.default_font_path), size=70)
        text = "????????????"
        start_x = 2540 + 300
        current_y = 980
        self.drawer.text((start_x, current_y), text, font=font, fill=(255, 140, 64))
        current_y += 100
        self.drawer.line(((2247 + 300, 1019), (start_x, current_y)), fill=(255, 140, 64), width=5)
        self.drawer.line(((start_x, current_y), (start_x + 300, current_y)), fill=(255, 140, 64), width=5)
        # find turret
        turrets = self.find_component("Shield")
        turrets_text_dict = {}
        for i, turret in enumerate(turrets):
            if turret.mount is not None:
                if turret.mount.data.chineseName is not None:
                    text = turret.mount.data.chineseName
                else:
                    text = f"S{turret.mount.data.size}??????"
                turret_size_text = f"1S{turret.mount.data.size} " + text
                if turret_size_text[1:] in turrets_text_dict:
                    turrets_text_dict[turret_size_text[1:]] += int(turret_size_text[0])
                else:
                    turrets_text_dict[turret_size_text[1:]] = int(turret_size_text[0])
        turret_text_list = [str(value) + key for key, value in turrets_text_dict.items()]
        for i, text in enumerate(turret_text_list):
            self.drawer.text((start_x, current_y), text, font=self.default_font, fill="white")
            current_y += 80

    def add_hp(self, hp: int):
        hp_icon = Image.open(str(icon_path / "hp_icon.png")).convert("RGBA")
        hp_icon = self.resize(hp_icon, 3)
        self.pic.paste(hp_icon, (200, 230), hp_icon)
        font = ImageFont.truetype(str(self.default_font_path), size=110)
        if hp >= 0:
            self.drawer.text((340, 227), str(int(hp)), font=font, fill="#ff4d4d")
        else:
            self.drawer.text((340, 227), ' -', font=font, fill="#ff4d4d")

    def add_quantum_fuel_info(self, quantum_fuel: int):
        quantum_fuel_icon = Image.open(str(icon_path / "quantum_fuel_icon.png")).convert("RGBA")
        quantum_fuel_icon = self.resize(quantum_fuel_icon, 1.5)
        self.pic.paste(quantum_fuel_icon, (800, 230), quantum_fuel_icon)
        font = ImageFont.truetype(str(self.default_font_path), size=110)
        if quantum_fuel >= 0:
            self.drawer.text((940, 227), str(int(quantum_fuel)), font=font, fill=(95, 198, 161))
        else:
            self.drawer.text((940, 227), ' -', font=font, fill=(95, 198, 161))

    def add_fuel_info(self, fuel: int):
        fuel_icon = Image.open(str(icon_path / "fuel_icon.png")).convert("RGBA")
        self.pic.paste(fuel_icon, (1350, 230), fuel_icon)
        font = ImageFont.truetype(str(self.default_font_path), size=110)
        if fuel >= 0:
            self.drawer.text((1490, 227), str(int(fuel)), font=font, fill="#66ccff")
        else:
            self.drawer.text((1490, 227), ' -', font=font, fill="#66ccff")

    def add_cargo_info(self, cargo: int):
        cargo_icon = Image.open(str(icon_path / "hull_icon.png")).convert("RGBA")
        cargo_icon = self.resize(cargo_icon, 3)
        self.pic.paste(cargo_icon, (2000, 230), cargo_icon)
        font = ImageFont.truetype(str(self.default_font_path), size=110)
        if cargo >= 0:
            self.drawer.text((2150, 227), str(int(cargo)), font=font, fill="#3365ff")
        else:
            self.drawer.text((2150, 227), ' -', font=font, fill="#3365ff")

    def add_price_info(self, price: int):
        # get length of price text
        if price < 0:
            return
        font = ImageFont.truetype(str(self.default_font_path), size=150)
        self.add_reversed_text(f"${int(price / 100)}",
                               x=4270,
                               y=650,
                               font=font, fill=(255, 140, 64))

    def add_hull_info(self):
        hp = 0
        for component in self.data.data.hull.hp:
            hp += component.hp
        self.add_hp(hp)
        self.add_quantum_fuel_info(int(self.data.data.qtFuelCapacity))
        self.add_fuel_info(int(self.data.data.fuelCapacity))
        cargo_size = 0
        for cargo in self.data.data.items.cargos:
            if cargo.data.cargoGrid is not None:
                cargo_size += cargo.data.cargoGrid.scus
        self.add_cargo_info(int(cargo_size))
        binding = get_binding_by_local_name(self.data.localName)
        if binding is not None:
            self.add_price_info(binding.ship_price)

    def add_basic_info(self):
        if self.data.data.ifcs is None:
            return
        ifcs = self.data.data.ifcs
        text = f"??????: {ifcs.angularVelocity.x}???/???\n??????: {ifcs.angularVelocity.z}???/???\n??????: {ifcs.angularVelocity.y}???/???\n"
        self.drawer.text((200, 600), text, font=self.default_font)
        self.drawer.line(((620, 790), (620 + 100, 790 + 66)), fill="white", width=5)

    def add_general_type(self):
        font = ImageFont.truetype(str(self.default_font_path), size=150)
        self.drawer.text((4400, 1960), "??????", font=font, fill="white")

    # def save(self, pic_path: pathlib.Path):
    #     self.pic.save(str(pic_path / f"{self.data.data.name}.png"))


if __name__ == '__main__':
    drawer = PicDrawer()
    # test_data = {
    #     "title": "Platinum Bay (ARC L1) ???????????????",
    #     "width": 2000,
    #     "width_ratio": [0.180, 0.142, 0.142, 0.142, 142, 0.142, 0.142],
    #     "column_size": 7,
    #     "columns": [
    #         {"data": ["????????????1", "????????????2", "????????????3", "????????????4", "????????????1", "????????????2", "????????????3"]},
    #         {"data": ["??????", "????????????", "????????????", "????????????", "????????????1", "????????????2", "????????????3"]},
    #         {"data": ["????????????", "????????????", "????????????", "??????", "????????????1", "????????????2", "????????????3"]},
    #         {"data": ["????????????", "????????????", "????????????", "????????????", "??????1", "????????????2", "????????????3"]},
    #         {"data": ["????????????", "????????????", "????????????", "????????????", "????????????1", "????????????2", "????????????3"]},
    #     ]
    # }
    # drawer.draw_sheet(Sheet(**test_data))
    calculator = Calculator()

    ship_data = calculator.ships + load_fake_ship()

    for ship in ship_data:
        try:
            ship_drawer = ShipDrawer(ship, calculator)
            ship_drawer.draw(pathlib.Path("test/"))
        except Exception as e:
            print(f"{ship.data.chineseName}({ship.localName}) ????????????")
            logging.exception(e)
            continue

    for i, weapon in enumerate(calculator.weapons):
        component_drawer = WeaponDrawer(weapon, calculator)
        component_drawer.draw(pathlib.Path("test/"))
    for i, shield in enumerate(calculator.shields):
        component_drawer = ShieldDrawer(shield, calculator)
        component_drawer.draw(pathlib.Path("test/"))
    for i, missile in enumerate(calculator.missiles):
        component_drawer = MissileDrawer(missile, calculator)
        component_drawer.draw(pathlib.Path("test/"))
    for i, emp in enumerate(calculator.emps):
        component_drawer = EMPDrawer(emp, calculator)
        component_drawer.draw(pathlib.Path("test/"))
    for i, power_plant in enumerate(calculator.power_plants):
        component_drawer = PowerPlantDrawer(power_plant, calculator)
        component_drawer.draw(pathlib.Path("test/"))
    for i, qdrive in enumerate(calculator.qdrives):
        component_drawer = QDriveDrawer(qdrive, calculator)
        component_drawer.draw(pathlib.Path("test/"))

