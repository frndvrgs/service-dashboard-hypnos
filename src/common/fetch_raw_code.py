import logging


async def fetch_raw_code(session, url):
    async with session.get(url) as response:
        if response.status == 200:
            return await response.read()
        else:
            logging.error(f"Failed to fetch {url}. Status: {response.status}")
            return None
