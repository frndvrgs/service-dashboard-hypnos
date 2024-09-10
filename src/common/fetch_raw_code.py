import logging


async def fetch_raw_code(session, url):
    async with session.get(url) as response:
        if response.status == 200:
            content = await response.text()
            # Removing extra spaces and line breaks
            return " ".join(content.split())
        else:
            logging.warning(
                f"failed to fetch content from {url}. status: {response.status}"
            )
            return ""
