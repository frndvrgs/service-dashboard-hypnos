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

                await self.check_interruption()

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

                download_list = await self.get_download_list(
                    repo["full_name"], contents
                )

                await self.check_interruption()

                code_dump = await self.fetch_and_process_files(download_list)
                await self.check_interruption()

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

    async def get_download_list(self, repo_full_name, contents):
        download_list = []
        async for item in self.traverse_contents(repo_full_name, contents):
            if (
                item["type"] == "file"
                and "download_url" in item
                and self.is_likely_text_file(item["path"])
            ):
                download_list.append(
                    {"path": item["path"], "download_url": item["download_url"]}
                )
        return download_list

    async def traverse_contents(self, repo_full_name, contents):
        for item in contents:
            if item["type"] == "dir" and self.should_skip_directory(item["path"]):

                continue

            yield item
            if item["type"] == "dir":
                try:
                    sub_contents = await self.github_client.get_repository_contents(
                        repo_full_name, path=item["path"]
                    )
                    async for sub_item in self.traverse_contents(
                        repo_full_name, sub_contents
                    ):
                        yield sub_item
                except Exception as e:
                    logging.warning(
                        f"Error traversing directory {item['path']}: {str(e)}"
                    )

    async def fetch_and_process_files(self, download_list):
        async with aiohttp.ClientSession() as session:
            tasks = [
                self.fetch_and_format_file(session, item) for item in download_list
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)
        return "\n\n".join(
            filter(None, [r for r in results if not isinstance(r, Exception)])
        )

    async def fetch_and_format_file(self, session, item):
        try:
            content = await fetch_raw_code(session, item["download_url"])
            if content:
                decoded_content = content.decode("utf-8", errors="replace")
                return f"[FILE: {item['path']}]\n\n{decoded_content}\n\n[END OF FILE: {item['path']}]"
        except Exception as e:
            logging.warning(f"Error processing file {item['path']}: {str(e)}")
        return None

    @staticmethod
    def is_likely_text_file(filename):
        code_extensions = {
            ".js",
            ".ts",
            ".jsx",
            ".tsx",
            ".html",
            ".css",
            ".scss",
            ".sass",
            ".less",
            ".py",
            ".pyx",
            ".pyi",
            ".pyw",
            ".java",
            ".kt",
            ".kts",
            ".groovy",
            ".scala",
            ".c",
            ".cpp",
            ".cxx",
            ".h",
            ".hpp",
            ".hxx",
            ".cs",
            ".rb",
            ".erb",
            ".rake",
            ".php",
            ".phtml",
            ".go",
            ".rs",
            ".swift",
            ".m",
            ".mm",
            ".ex",
            ".exs",
            ".sh",
            ".bash",
            ".zsh",
            ".lua",
            ".pl",
            ".pm",
            ".hs",
            ".lhs",
            ".r",
            ".R",
            ".dart",
            ".kt",
            ".kts",
            ".ts",
            ".tsx",
            ".vb",
            ".fs",
            ".fsx",
            ".clj",
            ".cljs",
            ".cljc",
            ".md",
            ".markdown",
        }
        return any(filename.lower().endswith(ext) for ext in code_extensions)

    @staticmethod
    def should_skip_directory(directory_path):
        skip_directories = {
            "__pycache__",
            "node_modules",
            ".git",
            ".svn",
            ".hg",
            ".idea",
            ".vscode",
            "build",
            "dist",
            "target",
            "bin",
            "obj",
            "vendor",
            "venv",
            "env",
            ".env",
            ".venv",
            "out",
            "output",
            "tmp",
            "temp",
            "cache",
            ".cache",
            "logs",
            "log",
            "coverage",
            "public",
            "assets",
            "images",
            "img",
            "fonts",
            "docs",
        }
        return any(part in skip_directories for part in directory_path.split("/"))
