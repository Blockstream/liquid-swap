# Copied from python-bitcoinlib f04a1a30cbeb16fd0e3a2e036769d6da4476fcc8 bitcoin/rpc.py

from __future__ import absolute_import, division, print_function, unicode_literals
import ssl

import http.client as httplib
import base64
import binascii
import decimal
import json
import os
import platform
import sys
import urllib.parse as urlparse

DEFAULT_USER_AGENT = "AuthServiceProxy/0.1"

DEFAULT_HTTP_TIMEOUT = 30

DEFAULT_ELEMENTS_RPC_PORT = 7041

unhexlify = lambda h: binascii.unhexlify(h.encode('utf8'))
hexlify = lambda b: binascii.hexlify(b).decode('utf8')


class JSONRPCError(Exception):
    """JSON-RPC protocol error base class

    Subclasses of this class also exist for specific types of errors; the set
    of all subclasses is by no means complete.
    """

    SUBCLS_BY_CODE = {}

    @classmethod
    def _register_subcls(cls, subcls):
        cls.SUBCLS_BY_CODE[subcls.RPC_ERROR_CODE] = subcls
        return subcls

    def __new__(cls, rpc_error):
        assert cls is JSONRPCError
        cls = JSONRPCError.SUBCLS_BY_CODE.get(rpc_error['code'], cls)

        self = Exception.__new__(cls)

        super(JSONRPCError, self).__init__(
            'msg: %r  code: %r' %
            (rpc_error['message'], rpc_error['code']))
        self.error = rpc_error

        return self

@JSONRPCError._register_subcls
class ForbiddenBySafeModeError(JSONRPCError):
    RPC_ERROR_CODE = -2

@JSONRPCError._register_subcls
class InvalidAddressOrKeyError(JSONRPCError):
    RPC_ERROR_CODE = -5

@JSONRPCError._register_subcls
class InvalidParameterError(JSONRPCError):
    RPC_ERROR_CODE = -8

@JSONRPCError._register_subcls
class VerifyError(JSONRPCError):
    RPC_ERROR_CODE = -25

@JSONRPCError._register_subcls
class VerifyRejectedError(JSONRPCError):
    RPC_ERROR_CODE = -26

@JSONRPCError._register_subcls
class VerifyAlreadyInChainError(JSONRPCError):
    RPC_ERROR_CODE = -27

@JSONRPCError._register_subcls
class InWarmupError(JSONRPCError):
    RPC_ERROR_CODE = -28


class BaseProxy(object):
    """Base JSON-RPC proxy class. Contains only private methods; do not use
    directly."""

    def __init__(self,
                 service_url=None,
                 service_port=None,
                 elements_conf_file=None,
                 timeout=DEFAULT_HTTP_TIMEOUT):

        # Create a dummy connection early on so if __init__() fails prior to
        # __conn being created __del__() can detect the condition and handle it
        # correctly.
        self.__conn = None
        authpair = None

        if service_url is None:
            # Figure out the path to the conf file
            if elements_conf_file is None:
                if platform.system() == 'Darwin':
                    elements_conf_file = os.path.expanduser('~/Library/Application Support/Elements/')
                elif platform.system() == 'Windows':
                    elements_conf_file = os.path.join(os.environ['APPDATA'], 'Elements')
                else:
                    elements_conf_file = os.path.expanduser('~/.elements')
                elements_conf_file = os.path.join(elements_conf_file, 'elements.conf')

            # Elements Core accepts empty rpcuser, not specified in elements_conf_file
            conf = {'rpcuser': ""}

            # Extract contents of elements.conf to build service_url
            try:
                with open(elements_conf_file, 'r') as fd:
                    for line in fd.readlines():
                        if '#' in line:
                            line = line[:line.index('#')]
                        if '=' not in line:
                            continue
                        k, v = line.split('=', 1)
                        conf[k.strip()] = v.strip()

            # Treat a missing elements.conf as though it were empty
            except FileNotFoundError:
                pass

            # if chain is specified, chain.key replaces key
            chain = conf.get('chain', 'liquidv1')
            for key in conf.copy():
                if key.startswith(chain + '.'):
                    conf[key[(len(chain) + 1):]] = conf.pop(key)

            if service_port is None:
                service_port = DEFAULT_ELEMENTS_RPC_PORT
            conf['rpcport'] = int(conf.get('rpcport', service_port))
            conf['rpchost'] = conf.get('rpcconnect', 'localhost')

            service_url = ('%s://%s:%d' %
                ('http', conf['rpchost'], conf['rpcport']))

            if 'rpcwallet' in conf:
                service_url += ('/wallet/%s' % conf['rpcwallet'])

            cookie_dir = conf.get('datadir', os.path.dirname(elements_conf_file))
            cookie_dir = os.path.join(cookie_dir, chain)
            cookie_file = conf.get('rpccookiefile', os.path.join(cookie_dir, ".cookie"))
            try:
                with open(cookie_file, 'r') as fd:
                    authpair = fd.read()
            except IOError as err:
                if 'rpcpassword' in conf:
                    authpair = "%s:%s" % (conf['rpcuser'], conf['rpcpassword'])

                else:
                    raise ValueError('Cookie file unusable (%s) and rpcpassword not specified in the configuration file: %r' % (err, elements_conf_file))

        else:
            url = urlparse.urlparse(service_url)
            authpair = "%s:%s" % (url.username, url.password)

        self.__service_url = service_url
        self.__url = urlparse.urlparse(service_url)

        if self.__url.scheme not in ('http',):
            raise ValueError('Unsupported URL scheme %r' % self.__url.scheme)

        if self.__url.port is None:
            port = httplib.HTTP_PORT
        else:
            port = self.__url.port
        self.__id_count = 0

        if authpair is None:
            self.__auth_header = None
        else:
            authpair = authpair.encode('utf8')
            self.__auth_header = b"Basic " + base64.b64encode(authpair)

        self.__conn = httplib.HTTPConnection(self.__url.hostname, port=port,
                                             timeout=timeout)

    def _call(self, service_name, *args):
        self.__id_count += 1

        postdata = json.dumps({'version': '1.1',
                               'method': service_name,
                               'params': args,
                               'id': self.__id_count})

        headers = {
            'Host': self.__url.hostname,
            'User-Agent': DEFAULT_USER_AGENT,
            'Content-type': 'application/json',
        }

        if self.__auth_header is not None:
            headers['Authorization'] = self.__auth_header

        self.__conn.request('POST', self.__url.path, postdata, headers)

        response = self._get_response()
        if response['error'] is not None:
            raise JSONRPCError(response['error'])
        elif 'result' not in response:
            raise JSONRPCError({
                'code': -343, 'message': 'missing JSON-RPC result'})
        else:
            return response['result']

    def _batch(self, rpc_call_list):
        postdata = json.dumps(list(rpc_call_list))

        headers = {
            'Host': self.__url.hostname,
            'User-Agent': DEFAULT_USER_AGENT,
            'Content-type': 'application/json',
        }

        if self.__auth_header is not None:
            headers['Authorization'] = self.__auth_header

        self.__conn.request('POST', self.__url.path, postdata, headers)
        return self._get_response()

    def _get_response(self):
        http_response = self.__conn.getresponse()
        if http_response is None:
            raise JSONRPCError({
                'code': -342, 'message': 'missing HTTP response from server'})

        return json.loads(http_response.read().decode('utf8'),
                          parse_float=decimal.Decimal)

    def close(self):
        if self.__conn is not None:
            self.__conn.close()

    def __del__(self):
        if self.__conn is not None:
            self.__conn.close()


class RawProxy(BaseProxy):
    """Low-level proxy to a bitcoin JSON-RPC service

    Unlike ``Proxy``, no conversion is done besides parsing JSON. As far as
    Python is concerned, you can call any method; ``JSONRPCError`` will be
    raised if the server does not recognize it.
    """
    def __init__(self,
                 service_url=None,
                 service_port=None,
                 elements_conf_file=None,
                 timeout=DEFAULT_HTTP_TIMEOUT,
                 **kwargs):
        super(RawProxy, self).__init__(service_url=service_url,
                                       service_port=service_port,
                                       elements_conf_file=elements_conf_file,
                                       timeout=timeout,
                                       **kwargs)

    def __getattr__(self, name):
        if name.startswith('__') and name.endswith('__'):
            # Python internal stuff
            raise AttributeError

        # Create a callable to do the actual call
        f = lambda *args: self._call(name, *args)

        # Make debuggers show <function bitcoin.rpc.name> rather than <function
        # bitcoin.rpc.<lambda>>
        f.__name__ = name
        return f


__all__ = (
    'JSONRPCError',
    'ForbiddenBySafeModeError',
    'InvalidAddressOrKeyError',
    'InvalidParameterError',
    'VerifyError',
    'VerifyRejectedError',
    'VerifyAlreadyInChainError',
    'InWarmupError',
    'RawProxy',
)
