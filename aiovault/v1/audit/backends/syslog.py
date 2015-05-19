from .bases import AuditBackend


class SyslogBackend(AuditBackend):
    """The `syslog` audit backend writes audit logs to syslog.
    """

    def validate(self, *, facility='AUTH', tag='vault', log_raw=False):
        """Configure audit backend.

        Parameters:
            facility (str): The syslog facility to use
            tag (str): The syslog tag to use
            log_raw (bool): Should security sensitive information be logged raw
        """
        return {
            'facility': facility,
            'tag': tag,
            'log_raw': 'true' if log_raw else 'false'
        }
