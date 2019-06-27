from liquidswap.liquidrpc import RawProxy, JSONRPCError
from liquidswap.exceptions import LiquidSwapError


DEFAULT_REGTEST_RPC_PORT = 7040
CONNECTION_ERROR_MESSAGE = \
    'Unable to connect to Liquid Node. Are you sure you have started the ' \
    'node and the parameters are correct?'


class ConnectionError(ValueError):
    """Unable to connect to the Liquid node"""


class ConnCtx(object):
    """Connection context

    Usage:
    with ConnCtx(credentials, critical) as cc:
        connection = cc.connection
        # code using connection
    """

    def __init__(self, credentials, critical, start_over=False):
        self.credentials = credentials
        # function to prompt a critical message, e.g. popup or logs
        self.critical = critical
        self.start_over = start_over

    def __enter__(self):
        return self

    @property
    def connection(self):
        """Get a connection with the Liquid node
        """
        try:
            return RawProxy(**self.credentials)
        except Exception as e:
            raise ConnectionError('{}\n\n{}'.format(CONNECTION_ERROR_MESSAGE,
                                                    str(e)))

    def __exit__(self, typ, value, stacktrace):
        if not typ:
            pass
        elif issubclass(typ, JSONRPCError):
            self.critical(title='Liquid Node Error',
                          message=value.error.get('message'),
                          start_over=self.start_over)
        elif issubclass(typ, LiquidSwapError):
            self.critical(title='Swap Error',
                          message=str(value),
                          start_over=self.start_over)
        elif issubclass(typ, Exception):
            self.critical(title='Error',
                          message=str(value),
                          start_over=self.start_over)

        return True
