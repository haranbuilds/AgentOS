class ModelProviderError(Exception):
    """Base exception for model provider failures"""


class ModelAuthenticationError(ModelProviderError):
    """Rasied when provider authentication fails"""


class ModelRateLimitError(ModelProviderError):
    """Raised when provider rate limits are exceeded"""


class ModelTimeoutError(ModelProviderError):
    """Raised when a Model request time out"""


class ModelUnavailableError(ModelProviderError):
    """Raised when the provider is temporarily unavailable"""


class ModelResponseError(ModelProviderError):
    """Raised when the provider response cannot be normalized"""
