class UnauthorizedError(RuntimeError):
    pass


class BadRequestError(RuntimeError):
    pass


class ServerError(RuntimeError):
    pass


class ParseResponseError(RuntimeError):
    """Raised when there is an error parsing the response from the API."""

    pass


class UnknownError(RuntimeError):
    pass
