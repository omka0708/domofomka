import sqlite3
import re
import os

from fastapi import FastAPI, Query
from typing import Annotated
from dotenv import load_dotenv, find_dotenv
from dadata import Dadata

load_dotenv(find_dotenv())

app = FastAPI()
dadata = Dadata(os.getenv('DADATA_TOKEN'))


def regexp(value: str, pattern: str) -> bool:
    return re.compile(pattern.lower()).search(value.lower()) is not None


def get_data_from_db(msg: str, db_name: str) -> dict:
    pattern = '^.*' + '.* '.join(msg.split()) + '$'
    res = {}
    with sqlite3.connect(os.getenv('DB_NAME')) as connection:
        cursor = connection.cursor()
        connection.create_function("regexp", 2, regexp)
        query_find_first = f"select address from {db_name} where regexp ({db_name}.address, '{pattern}') limit 1"
        cursor.execute(query_find_first)
        address = cursor.fetchone()
        if address:
            address = address[0]
            query_find_all = f"select entrance, code from {db_name} where {db_name}.address == '{address}'"
            cursor.execute(query_find_all)
            data = cursor.fetchall()
            if data:
                res['address'] = address
                for ent, code in data:
                    res.setdefault('data', {})
                    res['data'].setdefault(ent, []).append(code)
    return res


def get_address_by_geo(lat: float, lon: float) -> str | None:
    houses = dadata.geolocate(name="address", lat=lat, lon=lon)
    address = None
    if houses:
        house_data = houses[0]['data']
        if house_data['street']:
            address = f"{house_data['region']} {house_data['street']} {house_data['house']}"
            if house_data['block']:
                address += house_data['block_type'].replace('стр', 'с') + house_data['block'].replace(' стр ', 'с')
    return address


def get_empty_result() -> dict:
    return {'yaeda': {}, 'delivery': {}, 'oldcodes': {}}


@app.get("/codes_msg")
async def get_codes_by_message(message: Annotated[str, Query(min_length=7, max_length=50)]) -> dict:
    result = {'yaeda': get_data_from_db(message, 'yaeda'),
              'delivery': get_data_from_db(message, 'delivery'),
              'oldcodes': get_data_from_db(message, 'oldcodes')}
    return result


@app.get("/codes_geo")
async def get_codes_by_geo(lat: float, lon: float) -> dict:
    address = get_address_by_geo(lat, lon)
    result = get_empty_result()
    if address:
        result = {'yaeda': get_data_from_db(address, 'yaeda'),
                  'delivery': get_data_from_db(address, 'delivery'),
                  'oldcodes': get_data_from_db(address, 'oldcodes')}
    return result
