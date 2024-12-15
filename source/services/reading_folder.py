import typing
import aiofiles
import pathlib
import os

from source.config import config
from source.services.cookie_format import convert_to_http_cookie


class Reader:
    folder: pathlib.Path = None
    proxy = None

    def __init__(self, folder: typing.Union[str, pathlib.Path]):
        if isinstance(folder, str):
            self.folder = pathlib.Path(folder)
        if isinstance(folder, pathlib.Path):
            self.folder = folder

    async def __aiter__(self):
        self.proxy = self.proxy_generator()
        for root, _, files in os.walk(self.folder):
            for file in files:
                path = pathlib.Path(root).joinpath(file)
                if path.is_file() and str(path).endswith('.txt'):
                    async with aiofiles.open(path, encoding='utf-8', errors='ignore') as async_file:
                        cookie = {}
                        async for line in async_file:
                            if line.count('\t') != 6:
                                continue
                            for service in config.services:
                                if any(x in line for x in service.cookie_name):
                                    cookie.setdefault(service.url, []).append(line.strip())
                        if cookie:
                            list_cookie = []
                            for key, value in cookie.items():
                                for service in config.services:
                                    if key == service.url:
                                        service.log_path = root
                                        cookie = convert_to_http_cookie(value)
                                        if service.headers:
                                            service.headers['Cookie'] = cookie
                                        else:
                                            service.headers = {'Cookie': cookie}
                                        list_cookie.append(service)
                            yield list_cookie, await anext(self.proxy) if config.proxy_type != "off" else None
    async def proxy_generator(self):
        while True:
            async with aiofiles.open(config.proxy_path, encoding='utf-8', errors='ignore') as file:
                async for line in file:
                    if not any(line.startswith(x) for x in ['http', 'https', 'socks4', 'socks5']):
                        yield f'{config.proxy_type}://{line}'
                    yield line