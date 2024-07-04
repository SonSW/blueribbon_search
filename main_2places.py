import json

import geopy.distance
from math import sqrt
import requests

SNU_923_LAT = 37.463421
SNU_923_LON = 126.959497
SNU_923_COORD = (SNU_923_LAT, SNU_923_LON)

SNU_ENTRANCE_LAT = 37.465323
SNU_ENTRANCE_LON = 126.948741
SNU_ENTRANCE_COORD = (SNU_ENTRANCE_LAT, SNU_ENTRANCE_LON)

NAKSEONGDAE_IPGU_LAT = 37.477619
NAKSEONGDAE_IPGU_LON = 126.959531
NAKSEONGDAE_IPGU_COORD = (NAKSEONGDAE_IPGU_LAT, NAKSEONGDAE_IPGU_LON)

KU_LAT = 37.5893876
KU_LON = 127.0324773
KU_COORD = (KU_LAT, KU_LON)

UOS_LAT = 37.5838657
UOS_LON = 127.0587771
UOS_COORD = (UOS_LAT, UOS_LON)

#############################################
coord1 = SNU_923_COORD
coord2 = UOS_COORD

nearby_dist_km = 10

MIN_RIBBON_NUM = 1
PRICE_RANGES = ['미만', '1~2']
INCLUDE_FOOD_TYPES = ['']
EXCLUDE_FOOD_TYPES = ['디저트']
#############################################


def generate_restaurants(lat_sw, lon_sw, lat_ne, lon_ne):
    page = 0
    while True:
        try:
            url = (f"https://www.bluer.co.kr/api/v1/restaurants?page={page}"
                   "&size=200"
                   f"&latitude1={lat_sw}"
                   f"&longitude1={lon_sw}"
                   f"&latitude2={lat_ne}"
                   f"&longitude2={lon_ne}")
            res = requests.get(url, headers={'User-agent': 'Mozilla/5.0'}).text

            for r in json.loads(res)['_embedded']['restaurants']:
                yield r
        except:
            break

        page += 1


def get_restaurants_list(coord):
    lat, lon = coord

    lat_sw, lon_sw, _ = geopy.distance.distance(kilometers=nearby_dist_km * sqrt(2)).destination((lat, lon),
                                                                                                 bearing=225)
    lat_ne, lon_ne, _ = geopy.distance.distance(kilometers=nearby_dist_km * sqrt(2)).destination((lat, lon),
                                                                                                 bearing=45)

    li = []
    se = set()

    cnt = 0
    for r in generate_restaurants(lat_sw, lon_sw, lat_ne, lon_ne):
        cnt += 1
        if cnt % 100 == 0:
            print(f"cnt = {cnt}.")

        r_gps = (r['gps']['latitude'], r['gps']['longitude'])
        dist = geopy.distance.distance((lat, lon), r_gps).km
        r_ribbon_type = r['headerInfo']['ribbonType']
        # noinspection PyUnusedLocal
        ribbon_num = 0
        if r_ribbon_type == 'RIBBON_ONE':
            ribbon_num = 1
        elif r_ribbon_type == 'RIBBON_TWO':
            ribbon_num = 2
        elif r_ribbon_type == 'RIBBON_THREE':
            ribbon_num = 3
        else:
            ribbon_num = 0
        price_range = r['statusInfo']['priceRange'].strip()

        se.add(price_range)

        li.append({
            'gps': r_gps,
            'dist': dist,
            'id': r['id'],
            'name': r['headerInfo']['nameKR'],
            'ribbonNum': ribbon_num,
            'priceRange': price_range,
            'foodTypes': ', '.join(r['foodTypes'])
        })

    li.sort(key=lambda x: x['dist'])

    print(se)
    print(f"There were {cnt} restaurant(s).")

    return li


list1 = get_restaurants_list(coord1)
list2 = get_restaurants_list(coord2)

dist_by_id_1 = {x['id']:x['dist'] for x in list1}
all_list = [x for x in list2 if x['id'] in dist_by_id_1.keys()]
for x in all_list:
    x['dist'] = (round(dist_by_id_1[x['id']], 2), round(x['dist'], 2))

all_list.sort(key=lambda x: max(x['dist'][0], x['dist'][1]))

for restaurant in all_list:
    if (any(s in restaurant['priceRange'] for s in PRICE_RANGES)
            and restaurant['ribbonNum'] >= MIN_RIBBON_NUM
            and any(s in restaurant['foodTypes'] for s in INCLUDE_FOOD_TYPES)
            and all(s not in restaurant['foodTypes'] for s in EXCLUDE_FOOD_TYPES)):
        print(f"{restaurant['name']}{'☆' * restaurant['ribbonNum']}"
              f"({restaurant['priceRange']}, {restaurant['foodTypes']}):"
              f"https://www.bluer.co.kr/restaurants/{restaurant['id']} {restaurant['dist']}")
