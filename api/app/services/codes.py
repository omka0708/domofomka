import os
import re
import aiosqlite
import dadata

dadata = dadata.DadataAsync(os.getenv('DADATA_TOKEN'))
street_types = ['улица' 'проспект', 'микрорайон', 'переулок', 'жилой комплекс', 'бульвар', 'тракт', 'поселок', 'проезд',
                'шоссе', 'аллея', 'площадь', 'набережная', 'квартал', 'территория', 'деревня', 'военный городок',
                'жилой массив', 'тупик']


def address_exists(msg: str, city: str, street: str, house: str, street_type: str) -> bool:
    msg = ((msg.lower().replace('ё', 'е').replace(',', '').replace(' дом ', ' ').
            replace('строение', 'с').replace('корпус', 'к').replace(' ', ''))
           .replace('-', ''))
    city = re.sub(r'\W', '', city).lower()
    street = street.lower().replace(',', '').replace('-', '').replace('  ', ' ')
    street_split = street.split()
    house = house.lower()

    if all(word in msg for word in street_split):
        for word in street_split:
            msg = msg.replace(word, '', 1)
        if msg.count(house) == 1:
            msg = msg.replace(house, '')
            if msg:  # msg have something more than street and house
                if street_type in msg:  # it is probably street type
                    msg = msg.replace(street_type, '')
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


def street_or_city_exists(word: str, city: str, street: str):
    return word in city.lower() or word in street.lower()


async def get_data_from_db(msg: str) -> dict:
    res = {}
    if not msg:
        return res

    msg_array = re.split(r"[^а-я]", msg)

    for street_type in street_types:
        if street_type in msg_array:
            msg_array.remove(street_type)

    longest_word = max(msg_array, key=len).lower()

    async with aiosqlite.connect(os.getenv('DB_NAME')) as connection:
        await connection.create_function("street_or_city_exists", 3, street_or_city_exists)
        query_street = f'''
            select *
                from codes
                    where street_or_city_exists('{longest_word}', city, street)
        '''
        data = []
        connection.row_factory = aiosqlite.Row
        async with connection.execute(query_street) as cursor:
            async for row in cursor:
                if address_exists(msg, row['city'], row['street'], row['house'], row['street_type']):
                    data.append(row)
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


async def get_address_by_geo(lat: float, lon: float) -> str | None:
    houses = await dadata.geolocate(name="address", lat=lat, lon=lon)
    address = None
    if houses:
        house_data = houses[0]['data']
        if house_data['street']:
            address = f"{house_data['city']} {house_data['street']} {house_data['house']}"
            if house_data['block']:
                address += house_data['block_type'].replace('стр', 'с') + house_data['block'].replace(' стр ', 'с')
    return address
