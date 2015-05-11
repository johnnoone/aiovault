from .bases import SecretBackend


class GenericBackend(SecretBackend):
    """Store arbitrary secrets within the configured physical storage.

    The generic backend allows for writing keys with arbitrary values.
    The only value that special is the ``lease`` key, which can be provided
    with any key to restrict the lease time of the secret. This is useful to
    ensure clients periodically renew so that key rolling can be time bounded.
    """
