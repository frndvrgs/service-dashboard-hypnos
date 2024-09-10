import asyncio
import logging
from common.interruptible import Interruptible


class AnalyzeSourceCodeService(Interruptible):
    def __init__(self):
        super().__init__()

    async def process(self, id_work, id_repository, code_dump):
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

            # Simulating LLM processing
            # analysis_result = f"analysis of repository {id_repository}: {len(code_dump)} characters of code processed."
            analysis_result = code_dump

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
            logging.error(f"Error in AnalyzeSourceCode: {str(e)}")
            yield {
                "id_work": id_work,
                "id_repository": id_repository,
                "process_status": "error",
                "error_message": str(e),
            }
