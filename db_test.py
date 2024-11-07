import asyncio

import helpers
from helpers import DBOption

async def main():
    target_price = 00000
    price_id = None
    for i in range(1, 100):
        price_list = await helpers.get_db_option(i, DBOption.PRICE_CATEGORY)
        if not price_list:
            break
        if target_price >= price_list[0] and target_price <= price_list[1]:
            price_id = i
            break
    print(price_id)

asyncio.run(main())

