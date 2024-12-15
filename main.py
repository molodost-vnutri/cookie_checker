import asyncio

from loguru import logger

from source.database import lifespan
from source.services.reading_folder import Reader
from source.services.checker import Checker
from source.config import config
from source.services.logo import logo

async def check(cookie, proxy):
    f = Checker(cookie, proxy)
    await f.checker()

async def main():
    logo.logo_cls()
    try:
        await lifespan()
        reader = Reader('data')
        pull = []
        async for cookies, proxy in reader:
            for cookie in cookies:
                pull.append(check(cookie, proxy))
            if config.threads == len(pull):
                asyncio.gather(*pull)
                pull.clear()
            
        if pull:
            asyncio.gather(*pull)
            pull.clear()
    except KeyboardInterrupt:
        logger.info('Завершил работу')
    except Exception as e:
        logger.exception(e)

asyncio.run(main())