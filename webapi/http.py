from webapi.common import generate_error
from webapi.constants import (VERSION, ERROR_INVALID_METHOD,
                              ERROR_INVALID_KEY)

from twisted.web.resource import Resource
from twisted.web.server import Site


class HTTPResource(Resource):
    isLeaf = True

    def __init__(self, config, handler):
        Resource.__init__(self)
        self.config = config
        self.handler = handler

    def _check_key(self, request):
        if 'key' not in request.args:
            return False
        keys = request.args['key']
        for key in keys:
            if key in self.config.get('auth_keys', []):
                return True
        return False

    def subscribe(self, data):
        # TODO
        pass

    def render(self, request):
        request.setHeader('Content-Type', 'application/json')
        request.setHeader('Server', 'WebAPI v%s' % VERSION)
        if request.method == "HEAD":
            return
        if request.method != "POST":
            return generate_error(ERROR_INVALID_METHOD)
        data = self.handler.parse(request.content.getvalue())
        if not self._check_key(request):
            return generate_error(ERROR_INVALID_KEY, data.get('request', None))
        return self.handler.handle(self, data, True)


class HTTP(Site):
    def __init__(self, server, keys):
        Site.__init__(self, HTTPResource(server, keys))

    def log(self, request):
        pass
