from webapi.common import generate_error, generate_success, log, fullname
from webapi.constants import ERROR_INVALID_REQUEST, ERROR_INVALID_RESPONSE

import inspect
import json


class RequestHandler (object):
    handlers = {}

    def __init__(self, webapi):
        self.server = webapi.server
        self.add(PingHandler)
        # TODO get all handlers inside of this module automatically
        pass

    def add(self, klass):
        if not inspect.isclass(klass):
            klass = type(klass)
        if not issubclass(klass, Handler):
            log('Class (%s) must be a subclass of Handler' % fullname(klass))
            return
        handles = getattr(klass, 'handles', None)
        if not handles:
            log('Missing handles attribute for %s' % fullname(klass))
            return
        if handles in self.handlers:
            log('%s (%s) has already a handler' % (handles, fullname(klass)))
            return
        self.handlers[handles] = klass

    def parse(self, data):
        try:
            result = json.loads(data)
            if not isinstance(result, dict):
                result = {}
        except ValueError:
            result = {}
        return result

    def handle(self, data, is_parsed=True):
        if is_parsed:
            request = data
            if not isinstance(request, dict):
                request = {}
        else:
            request = self.parse(data)
        key = request.get('request', None)
        if not key or not isinstance(key, basestring):
            return generate_error(ERROR_INVALID_REQUEST)
        handlers = self.handlers
        if key not in handlers:
            return generate_error(ERROR_INVALID_REQUEST, key)
        handler = handlers[key](self)
        response = handler.handle(request.get('data', None))
        if isinstance(response, basestring):
            return response
        if isinstance(response, dict):
            response['request'] = key
            return json.dumps(response)
        return generate_error(ERROR_INVALID_RESPONSE, key)


class Handler (object):
    handles = None

    def __init__(self, handler):
        self.handler = handler
        self.server = handler.server

    def error(self, error_code):
        return generate_error(error_code, self.handles)

    def success(self, data=None):
        return generate_success(self.handles, data)

    def handle(self, data):
        pass


class PingHandler (Handler):
    handles = 'ping'

    def handle(self, data):
        return self.success('pong')
