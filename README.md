# domofomka-api

This is an API for getting the intercom code at the given address.

## Install

Build `domofomka-api` from source:

    git clone https://github.com/omka0708/domofomka-api
    cd domofomka-api
    docker build -t domofomka-api .

You should have also `codes.db` and `.env` files in the `domofomka-api` folder.

Environment file `.env` should contain:
    
    DB_NAME=<database_name>
    DADATA_TOKEN=<token>

Database should contain table `codes`, that has the structure:

    "id" INTEGER,
    "city" TEXT,
    "street_type" TEXT,
    "street" TEXT,
    "house" TEXT,
    "entrance" TEXT,
    "code_type" TEXT,
    "code" TEXT
    
## Run

Run the image, binding associated ports, and mounting the present working directory:

    docker run -d --name domofomka-api -p 80:80 domofomka-api

## Usage

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


