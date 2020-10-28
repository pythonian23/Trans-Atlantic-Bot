import asyncio
import aiohttp
import json


async def a():
    async with aiohttp.ClientSession() as session:
        async with session.get('https://jsonplaceholder.typicode.com/todos/1') as response:
            b = await response.text()
            print(json.loads(b))


asyncio.run(a())
