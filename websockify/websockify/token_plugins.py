from __future__ import print_function
import os
import sys
from logging import error as log

class BasePlugin(object):
    def __init__(self, src):
        self.source = src

    def lookup(self, token):
        return None


class ReadOnlyTokenFile(BasePlugin):
    # source is a token file with lines like
    #   token: host:port
    # or a directory of such files
    def __init__(self, *args, **kwargs):
        super(ReadOnlyTokenFile, self).__init__(*args, **kwargs)
        self._targets = None

    def _load_targets(self):
        if os.path.isdir(self.source):
            cfg_files = [os.path.join(self.source, f) for
                         f in os.listdir(self.source)]
        else:
            cfg_files = [self.source]

        self._targets = {}
        index = 1
        for f in cfg_files:
            for line in [l.strip() for l in open(f).readlines()]:
                if line and not line.startswith('#'):
                    try:
                        tok, target = line.split(': ')
                        self._targets[tok] = target.strip().rsplit(':', 1)
                    except ValueError:
                        print >>sys.stderr, "Syntax error in %s on line %d" % (self.source, index)
                index += 1

    def lookup(self, token):
        if self._targets is None:
            self._load_targets()

        if token in self._targets:
            return self._targets[token]
        else:
            return None


# the above one is probably more efficient, but this one is
# more backwards compatible (although in most cases
# ReadOnlyTokenFile should suffice)
class TokenFile(ReadOnlyTokenFile):
    # source is a token file with lines like
    #   token: host:port
    # or a directory of such files
    def lookup(self, token):
        self._load_targets()

        return super(TokenFile, self).lookup(token)


class BaseTokenAPI(BasePlugin):
    # source is a url with a '%s' in it where the token
    # should go

    # we import things on demand so that other plugins
    # in this file can be used w/o unnecessary dependencies

    def process_result(self, resp):
        host, port = resp.text.split(':')
        port = port.encode('ascii','ignore')
        return [ host, port ]

    def lookup(self, token):
        import requests

        resp = requests.get(self.source % token)

        if resp.ok:
            return self.process_result(resp)
        else:
            return None


class JSONTokenApi(BaseTokenAPI):
    # source is a url with a '%s' in it where the token
    # should go

    def process_result(self, resp):
        resp_json = resp.json()
        return (resp_json['host'], resp_json['port'])


class JWTTokenApi(BasePlugin):
    # source is a JWT-token, with hostname and port included
    # Both JWS as JWE tokens are accepted. With regards to JWE tokens, the key is re-used for both validation and decryption.
	def lookup(self, token):
		try:
			import jwt
			try:
				parsed = jwt.decode(token,'secret',algorithms='HS256')
				return(parsed['host'],int(parsed['port']))				
			except Exception as e:
				print(str(e))
		except ImportError as e:
				print(str(e))

class TokenRedis(object):
    def __init__(self, src):
        self._server, self._port = src.split(":")

    def lookup(self, token):
        try:
            import redis
            import simplejson
        except ImportError as e:
            print("package redis or simplejson not found, are you sure you've installed them correctly?", file=sys.stderr)
            return None

        client = redis.Redis(host=self._server,port=self._port)
        stuff = client.get(token)
        if stuff is None:
            return None
        else:
            combo = simplejson.loads(stuff.decode("utf-8"))
            pair = combo["host"]
            return pair.split(':')
