import sqlite3
import os

from fastapi import FastAPI, Query
from typing import Annotated
from dadata import Dadata

app = FastAPI()
dadata = Dadata(os.getenv('DADATA_TOKEN'))


def address_exists(msg: str, city: str, street: str, house: str, street_type: str) -> bool:
    msg = (msg.lower().replace('ё', 'е').replace(',', '').replace(' дом ', ' ').
           replace(' строение ', 'с').replace(' корпус ', 'к'))
    city = city.lower().replace('ё', 'е').replace(',', '')
    street = street.lower().replace('ё', 'е').replace(',', '')
    house = house.lower()
    if msg.count(street) == 1:
        msg = msg.replace(street, '').strip().replace('  ', ' ')
        if msg.count(house) == 1:
            msg = msg.replace(house, '').strip().replace('  ', ' ')
            if msg:  # msg have something more than street and house
                if street_type in msg:  # it is probably street type
                    msg = msg.replace(street_type, '').strip()
                res = True
                for remaining_word in msg.split():  # if there is anything left in msg, it must be in city
                    if remaining_word not in city or len(remaining_word) < 4:
                        res = False
                        break
            else:
                res = True
        else:
            res = False
    else:
        res = False
    return res


def get_data_from_db(msg: str) -> dict:
    res = {}
    if not msg:
        return res
    with sqlite3.connect(os.getenv('DB_NAME')) as connection:
        cursor = connection.cursor()
        connection.create_function("address_exists", 5, address_exists)
        query = f'''
            select * 
                from codes 
                    where address_exists('{msg}', city, street, house, street_type)
        '''
        data = cursor.execute(query).fetchall()
        print(data)
        if data:
            shortest_city = data[0][1]
            for _id, city, *args in data:
                if len(city) < len(shortest_city):
                    shortest_city = city
            for _id, city, street_type, street, house, entrance, code_type, code in data:
                if shortest_city in city:
                    res.setdefault('address', f"{shortest_city}, {street_type} {street}, дом {house}")
                    res.setdefault('data', {})
                    res['data'].setdefault(entrance, []).append((code, code_type))
    return res


def get_address_by_geo(lat: float, lon: float) -> str | None:
    houses = dadata.geolocate(name="address", lat=lat, lon=lon)
    address = None
    if houses:
        house_data = houses[0]['data']
        if house_data['street']:
            address = f"{house_data['city']} {house_data['street']} {house_data['house']}"
            if house_data['block']:
                address += house_data['block_type'].replace('стр', 'с') + house_data['block'].replace(' стр ', 'с')
    return address


@app.get("/codes_msg")
async def get_codes_by_message(message: Annotated[str, Query(min_length=7, max_length=100)]) -> dict:
    return get_data_from_db(message)


@app.get("/codes_geo")
async def get_codes_by_geo(lat: float, lon: float) -> dict:
    address = get_address_by_geo(lat, lon)
    return get_data_from_db(address)
