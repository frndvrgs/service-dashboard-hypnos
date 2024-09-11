import asyncio
import logging
from common.interruptible import Interruptible
from langchain_anthropic import ChatAnthropic
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from typing import Mapping, Any


class AnalyzePullRequestService(Interruptible):
    def __init__(self, api_key):
        super().__init__()
        self.chat_model = ChatAnthropic(
            model_name="claude-2.1",
            anthropic_api_key=api_key,
            # temperature=0.2,
            # max_tokens_to_sample=4000
        )

    async def process(self, id_work, id_repository, id_pull_request, code_dump):
        try:
            yield {
                "id_work": id_work,
                "id_repository": id_repository,
                "id_pull_request": id_pull_request,
                "process_status": "started",
            }

            await self.check_interruption()

            yield {
                "id_work": id_work,
                "id_repository": id_repository,
                "id_pull_request": id_pull_request,
                "process_status": "in_progress",
            }

            prompt = ChatPromptTemplate.from_template(
                """
            You are an expert software engineer and code analyst. Your task is to provide a comprehensive and in-depth analysis of the following source code and the author. Be thorough, detailed, and insightful in your analysis.

            Source Code:
            {code}

            Please provide a detailed analysis covering the following aspects:

            1. Overall Architecture and Structure:
               - Describe the high-level architecture of the codebase.
               - Identify design patterns used and evaluate their appropriateness.
               - Assess the modularity and organization of the code.

            2. Main Components and Modules:
               - List and describe the primary components or modules.
               - Explain the responsibilities and interactions of each component.
               - Evaluate the separation of concerns and cohesion within the codebase.

            3. Key Functionalities:
               - Identify and explain the main features or functionalities implemented.
               - Analyze the implementation approach for each key functionality.
               - Assess the efficiency and effectiveness of the implementations.

            4. Code Quality and Best Practices:
               - Evaluate adherence to coding standards and best practices.
               - Identify areas where SOLID principles are followed or violated.
               - Assess the readability, maintainability, and scalability of the code.

            5. Security Analysis:
               - Identify potential security vulnerabilities or risks.
               - Suggest security best practices that should be implemented.
               - Evaluate handling of sensitive data, if applicable.

            6. Programmer Profile Analysis:
                - Guess the programmer's potential background or specialization areas.
                - Guess the programmer favorite IDE.
                - Guess the programmer favorite linux or unix distro.
                - Guess the programmer favorite clothe's colors and sci-fi movie.

            Please provide your analysis in a clear, structured format.

                """
            )

            chain = (
                {"code": RunnablePassthrough()}
                | prompt
                | self.chat_model
                | StrOutputParser()
            )

            analysis_result = await asyncio.to_thread(chain.invoke, code_dump)

            await self.check_interruption()

            yield {
                "id_work": id_work,
                "id_repository": id_repository,
                "id_pull_request": id_pull_request,
                "process_status": "completed",
                "result": analysis_result,
            }

        except InterruptedError:
            yield {
                "id_work": id_work,
                "id_repository": id_repository,
                "id_pull_request": id_pull_request,
                "process_status": "interrupted",
            }
        except Exception as e:
            logging.error(f"Error in AnalyzePullRequest: {str(e)}")
            yield {
                "id_work": id_work,
                "id_repository": id_repository,
                "id_pull_request": id_pull_request,
                "process_status": "error",
                "error_message": str(e),
            }
