import aiohttp
import logging
from .exceptions import (
    GitHubAuthenticationError,
    GitHubRateLimitError,
    GitHubNotFoundError,
    GitHubAPIError,
    GitHubNetworkError,
    GitHubUnexpectedError,
)


class GitHubClient:
    def __init__(self, token):
        self.token = token
        self.base_url = "https://api.github.com"
        self.session = None

    async def __aenter__(self):
        await self.open()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()

    async def open(self):
        if self.session is None:
            self.session = aiohttp.ClientSession()

    async def close(self):
        if self.session:
            await self.session.close()
            self.session = None

    async def get_repository(self, repo_id):
        return await self._make_request(f"{self.base_url}/repositories/{repo_id}")

    async def get_repository_contents(self, repo_full_name, path=""):
        return await self._make_request(
            f"{self.base_url}/repos/{repo_full_name}/contents/{path}"
        )

    async def _make_request(self, url):
        if not self.session:
            await self.open()

        headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json",
        }
        try:
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                elif response.status == 401:
                    raise GitHubAuthenticationError("Invalid GitHub token")
                elif response.status == 403:
                    raise GitHubRateLimitError("GitHub API rate limit exceeded")
                elif response.status == 404:
                    raise GitHubNotFoundError("Resource not found")
                else:
                    raise GitHubAPIError(f"GitHub API error: {response.status}")
        except aiohttp.ClientError as e:
            logging.error(
                f"Network error while accessing GitHub API: {str(e)}", exc_info=True
            )
            raise GitHubNetworkError(f"Network error: {str(e)}")
        except Exception as e:
            logging.error(
                f"Unexpected error while accessing GitHub API: {str(e)}", exc_info=True
            )
            raise GitHubUnexpectedError(f"Unexpected error: {str(e)}")


# class GitHubClient:
#     def __init__(self, token):
#         self.token = token
#         self.base_url = "https://api.github.com"

#     async def get_repository(self, repo_id):
#         return await self._make_request(f"{self.base_url}/repositories/{repo_id}")

#     async def get_repository_contents(self, repo_full_name, path=""):
#         return await self._make_request(f"{self.base_url}/repos/{repo_full_name}/contents/{path}")

#     async def _make_request(self, url):
#         headers = {
#             "Authorization": f"token {self.token}",
#             "Accept": "application/vnd.github.v3+json"
#         }
#         try:
#             async with aiohttp.ClientSession() as session:
#                 async with session.get(url, headers=headers) as response:
#                     if response.status == 200:
#                         return await response.json()
#                     elif response.status == 401:
#                         raise GitHubAuthenticationError("Invalid GitHub token")
#                     elif response.status == 403:
#                         raise GitHubRateLimitError("GitHub API rate limit exceeded")
#                     elif response.status == 404:
#                         raise GitHubNotFoundError("Resource not found")
#                     else:
#                         raise GitHubAPIError(f"GitHub API error: {response.status}")
#         except aiohttp.ClientError as e:
#             logging.error(f"Network error while accessing GitHub API: {str(e)}", exc_info=True)
#             raise GitHubNetworkError(f"Network error: {str(e)}")
#         except Exception as e:
#             logging.error(f"Unexpected error while accessing GitHub API: {str(e)}", exc_info=True)
#             raise GitHubUnexpectedError(f"Unexpected error: {str(e)}")
