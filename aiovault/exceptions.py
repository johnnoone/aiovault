
class HTTPError(Exception):
    """Common http errors
    """

    def __init__(self, *args, **kwargs):
        if args and isinstance(args[0], dict):
            for k, v in args[0].items():
                setattr(self, k, v)

        args = list(args)
        for k, v in kwargs.items():
            setattr(self, k, v)
            args.append(v)

        super().__init__(*args)


class InvalidRequest(HTTPError):
    """Invalid request, missing or invalid data.

    See the "validation" section for more details on the error response
    """


class Unauthorized(HTTPError):
    """Unauthorized.

    Your authentication details are either incorrect or you don't have
    access to this feature
    """


class InvalidPath(HTTPError):
    """Invalid path.

    This can both mean that the path truly doesn't exist or that
    you don't have permission to view a specific path.
    We use 404 in some cases to avoid state leakage
    """


class RateLimitExceeded(HTTPError):
    """Rate limit exceeded.

    Try again after waiting some period of time
    """


class InternalServerError(HTTPError):
    """Internal server error.

    An internal error has occurred, try again later.
    If the error persists, report a bug
    """


class DownError(HTTPError):
    """Vault is down for maintenance or is currently sealed.

    Try again later
    """


class LoginError(InvalidRequest):
    """Raised when login failed
    """


class MountError(Exception):
    """Raised when mount failed
    """
