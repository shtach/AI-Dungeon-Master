"""

    Created by shtach
    Date: 5 May 2026
    Modified: -

"""


class AIClientError(Exception):
    """
        Raised for configuration and setup problems.
        Examples: missing API key, unknown provider name.
        Caller should treat this as unrecoverable — fix config, redeploy.
    """

class AIProviderError(Exception):
    """
        Raised when the provider responds with an error or is unreachable.
        Examples: rate limit, invalid key, network timeout, malformed response.
        Caller may retry or show a user-friendly message.
    """

class AIRateLimitError(AIProviderError):
    """
        Raised when the provider rejects a call with a rate-limit (HTTP 429).
        A subclass of AIProviderError so existing handlers keep working, while
        metering can flag these calls distinctly from other provider failures.
    """