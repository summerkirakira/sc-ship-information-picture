import requests
from pathlib import Path


headers = {
    'Authorization': "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE2NjkwNzYxMTIsImV4cCI6MTY2OTY4MDkxMn0.yVHgIVLw2P1i8w9mDyK8g6K7hU-Zq3-_tvSE8KIyY6c",
    'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36",
    'Referer': "https://www.erkul.com/",
}

SAVE_PATH = Path(__file__).parent / 'temp_data'
SAVE_PATH.mkdir(exist_ok=True)


def update():

    component_list = [
        'bombs',
        'coolers',
        'emps',
        'mining-lasers',
        'missile-racks',
        'missiles',
        'mounts',
        'paints',
        'power-plants',
        'qdrives',
        'qeds',
        'shields',
        'ships',
        'shops',
        'turrets',
        'utilities',
        'weapons'
    ]
    for component in component_list:
        print(f'Updating {component}')
        r = requests.get(f'https://api.erkul.games/live/{component}', headers=headers)
        with open(SAVE_PATH / f'{component.replace("-", "_")}.json', 'w') as f:
            f.write(r.text)


if __name__ == '__main__':
    update()