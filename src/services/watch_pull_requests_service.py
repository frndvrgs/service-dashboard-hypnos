import asyncio
import logging
from common.github_client import GitHubClient
from common.interruptible import Interruptible


class WatchPullRequestsService(Interruptible):
    def __init__(self):
        super().__init__()

    async def process(self, id_work, id_repository, code_dump, github_token):
        async with GitHubClient(github_token) as github_client:
            try:
                # Simulating immediate response
                yield {
                    "id_work": id_work,
                    "id_repository": id_repository,
                    "process_status": "started",
                }

                # Simulating work
                await asyncio.sleep(5)
                await self.check_interruption()

                # Simulating intermediate status
                yield {
                    "id_work": id_work,
                    "id_repository": id_repository,
                    "process_status": "in_progress",
                }

                # Simulating webhook wait and LLM processing
                analysis_result = f"Analyzed pull requests for repository {id_repository} with {len(code_dump)} characters of context."

                await asyncio.sleep(5)
                await self.check_interruption()

                # Final response
                yield {
                    "id_work": id_work,
                    "id_repository": id_repository,
                    "process_status": "completed",
                    "result": analysis_result,
                }
            except InterruptedError:
                yield {
                    "id_work": id_work,
                    "id_repository": id_repository,
                    "process_status": "interrupted",
                }
            except Exception as e:
                logging.error(f"Error in WatchPullRequests: {str(e)}")
                yield {
                    "id_work": id_work,
                    "id_repository": id_repository,
                    "process_status": "error",
                    "error_message": str(e),
                }
