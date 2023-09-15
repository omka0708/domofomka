# domofomka

Application for getting the intercom code at the given address.
Used stack: *FastAPI*, *SQLite*, *Redis*.

## Install

Build `domofomka` from source:

    git clone https://github.com/omka0708/domofomka
    cd domofomka
    docker compose up -d

You should have `.env` file at the */domofomka* folder and SQLite3 database with `DB_NAME` name (configured in environment file) at */domofomka/api* folder.

Environment file `.env` should contain:
    
    DB_NAME=<database_name>
    DADATA_TOKEN=<dadata_token>
    VK_GROUP_TOKEN=<vk_group_token>
    VK_GROUP_ID=<vk_group_id>

Your SQLite3 database should contain table `codes`, that has the structure:

    "id" INTEGER,
    "city" TEXT,
    "street_type" TEXT,
    "street" TEXT,
    "house" TEXT,
    "entrance" TEXT,
    "code_type" TEXT,
    "code" TEXT
    
## Run

Run this command at the working directory */domofomka*:

    docker compose up --build

## API
### Get codes by message
#### Request

`GET /codes_msg/`

    GET localhost:80/codes_msg?message=трофимова 3
    
#### Response

    {
    "address":"Москва, улица Трофимова, дом 3",
    "data":
        {
        "1":[["#7546","yaeda"],["#4230","yaeda"],["*#7546","delivery"]],
        "2":[["#4230","yaeda"],["#4230","delivery"],["К4230","oldcodes"]]
        }
    }


### Get codes by latitude and longitude

`GET /codes_geo/`

    GET localhost:80/codes_geo?lat=55.617586&lon=37.495482
    
#### Response

    {
    "address":"Москва, улица Профсоюзная, дом 156к5",
    "data":
        {
        "1":[["255К2580","yaeda"],["12К2889","yaeda"],["28К3185","yaeda"]],
        "2":[["72К3108","yaeda"]],
        "3":[["110*4082","yaeda"],["97*4840","yaeda"],["75*6818","yaeda"]],
        "4":[["133К2489","yaeda"],["135К3001","yaeda"]],
        "5":[["170*3304","yaeda"],["151*6631","yaeda"],["173*9572","yaeda"]],
        "6":[["200К4578","yaeda"],["200К4578","delivery"]]
        }
    }
    
## VK Bot
### Get codes by message
![codes_by_msg](https://github.com/omka0708/domofomka/assets/56554057/d21e6146-95a7-4f09-a501-31d8fd2ae7df)

### Get codes by latitude and longitude
![codes_by_lat_lon](https://github.com/omka0708/domofomka/assets/56554057/85f2b4f6-7634-4b3a-b7a7-5ae10cdc9219)

## Telegram Bot

*soon*

