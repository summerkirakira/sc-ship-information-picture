import json
from bs4 import BeautifulSoup


with open("loaner_ships.html", "r", encoding="utf-8") as f:
    content = f.read()

soup = BeautifulSoup(content, "html.parser")


sheet = soup.find("table").find_all("tr")[1:]

loaner_ships_dict = {}

for row in sheet:
    ship_name = row.find("td").text
    loaner_ships = row.find_all("td")[1].text
    loaner_ships_dict[ship_name] = [ship.strip() for ship in loaner_ships.replace("and", "").split(",")]

with open("../data/loaner_ships.json", "w", encoding="utf-8") as f:
    f.write(json.dumps(loaner_ships_dict, indent=4, ensure_ascii=False))