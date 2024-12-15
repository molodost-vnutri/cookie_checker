import asyncio
from aiohttp import ClientSession

class RequestAPI:
    client: ClientSession = None
    headers: str = None
    def __init__(self, headers: str):
        self.client = ClientSession()
        self.headers = headers

    async def request(self, method: str, url: str, **kwargs):
        while True:
            try:
                async with self.client.request(
                    method=method.upper(),
                    url=url,
                    headers=self.headers,
                    **kwargs
                ) as response:
                    return await response.text()
            except Exception as e:
                print(e)
                await asyncio.sleep(5)
            finally:
                await self.client.close()