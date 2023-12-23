from fastapi import FastAPI, Query
from fastapi.responses import RedirectResponse
from typing import Annotated

from .services import get_data_from_db, get_address_by_geo

app = FastAPI(title="Domofomka")


@app.get("/", include_in_schema=False)
async def redirect_to_docs():
    return RedirectResponse(url='/docs')


@app.get("/codes_msg", tags=["codes"])
async def get_codes_by_message(message: Annotated[str, Query(min_length=7, max_length=100)]) -> dict:
    return await get_data_from_db(message)


@app.get("/codes_geo", tags=["codes"])
async def get_codes_by_geo(lat: float, lon: float) -> dict:
    address = await get_address_by_geo(lat, lon)
    return await get_data_from_db(address)
