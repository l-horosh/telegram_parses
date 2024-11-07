import aiosqlite
from enum import Enum

class DBOption(Enum):
    LOCATION = 1, 
    BRAND = 2,
    MODEL = 3,
    PRICE_CATEGORY = 4,
    LOCATION_ID_LIST = 5,
    BRAND_ID_LIST = 6,
    MODEL_ID_LIST = 7,
    PRICE_ID_LIST = 8,

    def to_str(self) -> (str | None):
        match self:
            case DBOption.LOCATION: 
                return 'location'
            case DBOption.BRAND:
                return 'brand'
            case DBOption.MODEL:
                return 'model'
            case DBOption.PRICE_CATEGORY:
                return 'price_category'
            case DBOption.LOCATION_ID_LIST: 
                return 'location_id'
            case DBOption.BRAND_ID_LIST:
                return 'brand_id'
            case DBOption.MODEL_ID_LIST:
                return 'model_id'
            case DBOption.PRICE_ID_LIST:
                return 'price_id'
            case _:
                return None 
    
    def get_table(self) -> (str | None):
        match self:
            case DBOption.LOCATION_ID_LIST | DBOption.BRAND_ID_LIST | DBOption.MODEL_ID_LIST | DBOption.PRICE_ID_LIST:
                return 'users_data'
            case DBOption.LOCATION | DBOption.BRAND | DBOption.MODEL | DBOption.PRICE_CATEGORY:
                return 'ids_data'
            case _:
                return None 
            
    def get_table_key(self) -> (str | None):
        match self:
            case DBOption.LOCATION_ID_LIST | DBOption.BRAND_ID_LIST | DBOption.MODEL_ID_LIST | DBOption.PRICE_ID_LIST:
                return "user_id"
            case DBOption.LOCATION | DBOption.BRAND | DBOption.MODEL | DBOption.PRICE_CATEGORY:
                return "category_id"
            case _:
                None

    def convert_to_python(self, value) -> (list | str): 
        to_int_list = (DBOption.LOCATION_ID_LIST, DBOption.BRAND_ID_LIST, DBOption.MODEL_ID_LIST, DBOption.PRICE_CATEGORY, DBOption.PRICE_ID_LIST)
        to_str = (DBOption.LOCATION, DBOption.BRAND, DBOption.MODEL)
        match self:
            case self if self in to_int_list:
                if not value or not value[0]:
                    return []
                else:
                    return eval(value[0])
            case self if self in to_str:
                if not value or not value[0]:
                    return None 
                else:
                    return value[0]
            case _:
                raise f"Wrong option {self}"
 

async def ensure_tables() -> None:
    async with aiosqlite.connect("db/database.db", timeout = 1000) as db:
        await db.execute('''CREATE TABLE IF NOT EXISTS users_data (
                    user_id INTEGER PRIMARY KEY,
                    location_id TEXT,
                    brand_id TEXT,
                    model_id TEXT,
                    price_id TEXT
                )''')
        await db.execute('''CREATE TABLE IF NOT EXISTS ids_data (
                    category_id INTEGER PRIMARY KEY,
                    location TEXT,
                    brand TEXT,
                    model TEXT,
                    price_category TEXT
                )''')
        await db.commit()

async def request_db_option(pk_id: int, option: DBOption) -> (list | None):
    if not pk_id:
        return None
    column = option.to_str()
    table = option.get_table()
    table_key = option.get_table_key()
    if not column or not table or not table_key:
        raise f"Wrong option {option}"

    await ensure_tables()
    async with aiosqlite.connect("db/database.db", timeout = 1000) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.cursor()
        await cursor.execute(f"SELECT {column} FROM {table} WHERE {table_key} = ?", (pk_id,)) 
        res = await cursor.fetchone()
    return res

async def get_db_option(pk_id: int, option: DBOption) -> (list | str | None):
    res = await request_db_option(pk_id, option)
    return option.convert_to_python(res)

async def set_db_option(pk_id: int, option: DBOption, value) -> None:
    if not pk_id:
        return 
    column = option.to_str()
    table = option.get_table()
    table_key = option.get_table_key()
    if not column or not table or not table_key:
        raise f"Wrong option {option}"
    
    await ensure_tables()

    async with aiosqlite.connect("db/database.db", timeout = 1000) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.cursor()
        await cursor.execute(f"INSERT OR IGNORE INTO {table} ({table_key}) VALUES(?)", (pk_id,)) 

        if value:
            await cursor.execute(f"UPDATE {table} SET {column} = ? WHERE {table_key} = ?", (str(value), pk_id,))
        else:
            await cursor.execute(f"UPDATE {table} SET {column} = NULL WHERE {table_key} = ?", (pk_id,))
        await db.commit()


async def validate_categories(post) -> None:
    for value, option in post.attributes_list:
        column = option.to_str()
        table = option.get_table()
        table_key = option.get_table_key()
        if not column or not table or not table_key:
            raise f"Wrong option {option}"

        await ensure_tables()
        async with aiosqlite.connect("db/database.db", timeout = 1000) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.cursor()
            await cursor.execute(f"SELECT {column} FROM {table} WHERE {column} = ?", (value,)) 
            res = await cursor.fetchone()
        
        if res and res[0]:
            continue    
            
        async with aiosqlite.connect("db/database.db", timeout = 1000) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.cursor()
            await cursor.execute(f"SELECT MAX({table_key}) FROM {table} WHERE {column} IS NOT NULL")
            target_id = await cursor.fetchone()
        
        if not target_id or not target_id[0]:
            target_id = 1
        else:
            target_id = target_id[0] + 1

        await set_db_option(target_id, option, value)

def convert_options_between_tables(option: DBOption) -> DBOption:
    match option:
        case DBOption.LOCATION:
            return DBOption.LOCATION_ID_LIST
        case DBOption.BRAND:
            return DBOption.BRAND_ID_LIST
        case DBOption.MODEL:
            return DBOption.MODEL_ID_LIST
        case DBOption.PRICE_CATEGORY:
            return DBOption.PRICE_ID_LIST
        case _:
            raise f"Wrong option {option}"

async def get_categories_ids(post) -> list:
    categories_list = []

    for value, option in post.attributes_list:
        column = option.to_str()
        table = option.get_table()
        table_key = option.get_table_key()
        if not column or not table or not table_key:
            raise f"Wrong option {option}"

        await ensure_tables()
        async with aiosqlite.connect("db/database.db", timeout = 1000) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.cursor()
            await cursor.execute(f"SELECT {table_key} FROM {table} WHERE {column} = ?", (value,)) 
            res = await cursor.fetchone()
        categories_list.append((res[0], convert_options_between_tables(option)))
    

    for i in range(1, 100):
        price_list = await get_db_option(i, DBOption.PRICE_CATEGORY)
        if not price_list:
            break
        if post.price >= price_list[0] and post.price <= price_list[1]:
            categories_list.append((i, DBOption.PRICE_ID_LIST))
            break

    return categories_list

