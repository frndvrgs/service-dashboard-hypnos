import asyncio
import aiohttp
import logging
from common.github_client import GitHubClient
from common.interruptible import Interruptible
from common.fetch_raw_code import fetch_raw_code


class DumpSourceCodeService(Interruptible):
    def __init__(self):
        super().__init__()
        self.github_client = None

    async def process(self, id_work, id_repository, github_token):
        async with GitHubClient(github_token) as self.github_client:
            try:
                yield {
                    "id_work": id_work,
                    "id_repository": id_repository,
                    "process_status": "started",
                }

                logging.info("DumpSourceCode started")
                # Simulating work
                await asyncio.sleep(5)
                await self.check_interruption()

                logging.info("DumpSourceCode in_progress")
                yield {
                    "id_work": id_work,
                    "id_repository": id_repository,
                    "process_status": "in_progress",
                }

                repo = await self.github_client.get_repository(id_repository)

                await self.check_interruption()
                contents = await self.github_client.get_repository_contents(
                    repo["full_name"]
                )
                await self.check_interruption()

                # Extract download_urls
                download_urls = [
                    file["download_url"]
                    for file in contents
                    if file["type"] == "file" and "download_url" in file
                ]

                # Fetch and process content from each URL
                async with aiohttp.ClientSession() as session:
                    tasks = [fetch_raw_code(session, url) for url in download_urls]
                    results = await asyncio.gather(*tasks)

                # Concatenate all processed contents
                code_dump = "\n".join(filter(None, results))

                await asyncio.sleep(5)
                await self.check_interruption()

                logging.info("DumpSourceCode completed")
                yield {
                    "id_work": id_work,
                    "id_repository": id_repository,
                    "process_status": "completed",
                    "code_dump": code_dump,
                }
            except InterruptedError:
                yield {
                    "id_work": id_work,
                    "id_repository": id_repository,
                    "process_status": "interrupted",
                }
            except Exception as e:
                logging.error(f"Error in DumpSourceCode: {str(e)}")
                yield {
                    "id_work": id_work,
                    "id_repository": id_repository,
                    "process_status": "error",
                    "error_message": str(e),
                }
