# domofomka-api

This is an API for getting the intercom code at the given address.

## Install

Build `domofomka-api` from source:

    git clone https://github.com/omka0708/domofomka-api
    cd domofomka-api
    docker build -t domofomka-api .

You should have also `codes.db` and `.env` files in the `domofomka-api` folder.

Environment file `.env` should contain:
    
    DB_NAME=codes.db
    DADATA_TOKEN=<token>

Database `codes.db` should contain three tables `yaeda`, `delivery` and `oldcodes`, each of which has the structure:

    id INTEGER PRIMARY KEY AUTOINCREMENT,
    address TEXT NOT NULL,
    entrance TEXT NOT NULL,
    code TEXT NOT NULL
    
## Run

Run the image, binding associated ports, and mounting the present working directory:

    docker run -d --name domofomka-api -p 80:80 domofomka-api

## Usage

### Get codes by message
#### Request

`GET /codes_msg/`

    GET localhost:80/codes_msg?message=москва вернадского 15
    
#### Response

    {
    "yaeda":
        {
            "address":"Москва, проспект Вернадского, д. 15",
            "data":{"1":["44К5437","12КЛЮЧ1943","16К7180","45К4168","44К2557","1КЛЮЧ0464","2580"],"2":["69*8773","81*6262","61*8185"],"3":["7139","В13В1813"]}
        },
    "delivery":
        {
            "address":"Москва, проспект Вернадского, 15",
            "data":{"1":["4К5421","44К2557","44К5437"],"2":["81*6262","75*9437"],"3":["7139"],"4":["61*8185"],"5":["146*1197"],"6":["В188В3697В","В172В2850В"]}
        },
    "oldcodes":
        {
            "address":"г. Москва, пр-кт. Вернадского, д. 15",
            "data":{"1":["44К5437"],"2":["54К3287"],"3":["В13В1813"],"4":["133К2916"],"5":["148К4064"],"6":["В172В2850В"]}
        }
    }

### Get codes by latitude and longitude

`GET /codes_geo/`

    GET localhost:80/codes_geo?lat=55.617586&lon=37.495482
    
#### Response

    {
    "yaeda":
        {
            "address":"Москва, Профсоюзная улица, д. 156к5",
            "data":{"1":["255К2580","12К2889","28К3185"],"2":["72К3108"],"3":["110*4082","97*4840","75*6818"],"4":["133К2489","140К4793","134К3257","135К3001","121КЛЮЧ2073"],"5":["170*3304","151*6631","173*9572"],"6":["200К4578"]}
        },
    "delivery":
        {
            "address":"Москва, Профсоюзная улица, 156к5",
            "data":{"6":["200К4578"]}
        },
    "oldcodes":
        {
            "address":"г. Москва, ул. Профсоюзная, д. 156к5",
            "data":{"1":["35К9000"],"3":["75К1902"],"4":["150К9161"],"5":["170К3365"]}
        }
    }


