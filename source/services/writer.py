from json import dumps

import aiofiles

from source.config import config
from source.services.crud import CRUD

async def save_result(cookie: str, path: str, service: str, parse_data: dict[str, str] = {}):
    data = None if not parse_data else dumps(parse_data, ensure_ascii=False, indent=2)
    if config.save_to == "file":
        async with aiofiles.open(f'{config.path}/{service}.txt', mode='a+', encoding='utf-8', errors='ignore') as file:
            result = f"""
cookie: {cookie}
path_to_folder: {path}
parse_data: {data}
--------------------------------
"""
            await file.write(result)
    else:
        await CRUD.insert_data(cookie=cookie, service=service, parse_data=data, path=path)