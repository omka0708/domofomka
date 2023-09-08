# domofomka-api

This is an API for getting the intercom code at an given address.

## Install

Build `domofomka-api` from source:

    git clone https://github.com/omka0708/domofomka-api
    cd domofomka-api
    docker build -t domofomka-api .

You should have also `codes.db` and `.env` files in the `domofomka-api` folder.

Environment file `.env` should contain:
    
    DB_NAME=codes.db

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

`GET /codes/?message=`

    GET http://127.0.0.1:8000/codes?message=москва вернадского 15
    
#### Response

    {"yaeda":
        {"address":"Москва, проспект Вернадского, д. 15",
            "data":{"1":["44К5437","12КЛЮЧ1943","16К7180","45К4168","44К2557","1КЛЮЧ0464","2580"],"2":["69*8773","81*6262","61*8185"],"3":["7139","В13В1813"]}
        },
    "delivery":
        {"address":"Москва, проспект Вернадского, 15",
            "data":{"1":["4К5421","44К2557","44К5437"],"2":["81*6262","75*9437"],"3":["7139"],"4":["61*8185"],"5":["146*1197"],"6":["В188В3697В","В172В2850В"]}
        },
    "oldcodes":
        {"address":"г. Москва, пр-кт. Вернадского, д. 15",
            "data":{"1":["44К5437"],"2":["54К3287"],"3":["В13В1813"],"4":["133К2916"],"5":["148К4064"],"6":["В172В2850В"]}
        }
    }

### Get codes by longitude and latitude

*soon*

## Services

| Service       | Port | Usage                                                                       |
|---------------|------|-----------------------------------------------------------------------------|
| domofomka-api | 80   | When using `run domofomka-api`, visit `http://localhost:80` in your browser |
