import json

import geopy.distance
from math import sqrt
import requests

SNU_923_LAT = 37.463421
SNU_923_LON = 126.959497
SNU_923_COORD = (SNU_923_LAT, SNU_923_LON)

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
cur_coord = SNU_923_COORD
cur_lat = cur_coord[0]
cur_lon = cur_coord[1]

nearby_dist_km = 5

MIN_RIBBON_NUM = 1
PRICE_RANGES = ['미만', '1~2']
INCLUDE_FOOD_TYPES = ['']
EXCLUDE_FOOD_TYPES = ['디저트']
#############################################

if not INCLUDE_FOOD_TYPES:
    INCLUDE_FOOD_TYPES = ['']

if EXCLUDE_FOOD_TYPES == ['']:
    EXCLUDE_FOOD_TYPES = []

lat1, lon1, _ = geopy.distance.distance(kilometers=nearby_dist_km * sqrt(2)).destination((cur_lat, cur_lon),
                                                                                         bearing=225)
lat2, lon2, _ = geopy.distance.distance(kilometers=nearby_dist_km * sqrt(2)).destination((cur_lat, cur_lon), bearing=45)

# print(lat1, lon1)
# print(lat2, lon2)


def get_restaurants():
    page = 0
    while True:
        try:
            url = (f"https://www.bluer.co.kr/api/v1/restaurants?page={page}"
                   "&size=200"
                   f"&latitude1={lat1}"
                   f"&longitude1={lon1}"
                   f"&latitude2={lat2}"
                   f"&longitude2={lon2}")
            res = requests.get(url, headers={'User-agent': 'Mozilla/5.0'}).text

            for r in json.loads(res)['_embedded']['restaurants']:
                yield r
        except:
            break

        page += 1


li = []
se = set()

cnt = 0
for r in get_restaurants():
    cnt += 1
    if cnt%100 == 0:
        print(f"cnt = {cnt}.")

    r_gps = (r['gps']['latitude'], r['gps']['longitude'])
    dist = geopy.distance.distance((cur_lat, cur_lon), r_gps).km
    r_ribbon_type = r['headerInfo']['ribbonType']
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

for restaurant in li:
    if (any(s in restaurant['priceRange'] for s in PRICE_RANGES)
            and restaurant['ribbonNum'] >= MIN_RIBBON_NUM
            and any(s in restaurant['foodTypes'] for s in INCLUDE_FOOD_TYPES)
            and all(s not in restaurant['foodTypes'] for s in EXCLUDE_FOOD_TYPES)):
        print(f"{restaurant['name']}{'☆'*restaurant['ribbonNum']}"
              f"({restaurant['priceRange']}, {restaurant['foodTypes']}): "
              f"https://www.bluer.co.kr/restaurants/{restaurant['id']} ({round(restaurant['dist'], 2)}km) "
              f"{restaurant['gps']}")

# baz = restaurants[0]

# for k in baz.keys():
#     print(k)
