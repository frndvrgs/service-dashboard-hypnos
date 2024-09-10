class GitHubError(Exception):
    """Base class for GitHub-related errors"""


class GitHubAuthenticationError(GitHubError):
    """Raised when authentication fails"""


class GitHubRateLimitError(GitHubError):
    """Raised when the GitHub API rate limit is exceeded"""


class GitHubNotFoundError(GitHubError):
    """Raised when a requested resource is not found"""


class GitHubAPIError(GitHubError):
    """Raised for general GitHub API errors"""


class GitHubNetworkError(GitHubError):
    """Raised for network-related errors"""


class GitHubUnexpectedError(GitHubError):
    """Raised for unexpected errors"""
