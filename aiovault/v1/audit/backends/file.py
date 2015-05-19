from .bases import AuditBackend


class FileBackend(AuditBackend):
    """The `file` audit backend writes audit logs to a file.
    """

    def validate(self, *, path, log_raw=False):
        """Configure audit backend.

        Parameters:
            path (str): The path to where the file will be written. If this
                        path exists, the audit backend will append to it
            log_raw (bool): Should security sensitive information be logged raw
        """
        return {
            'path': path,
            'log_raw': 'true' if log_raw else 'false'
        }
