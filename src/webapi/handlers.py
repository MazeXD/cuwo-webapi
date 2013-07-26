from webapi.common import generate_error, generate_success, log, fullname
from webapi.constants import ERROR_INVALID_REQUEST, ERROR_SYSTEM

from twisted.python import log

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
        accepts = getattr(klass, 'accepts', None)
        if not accepts:
            log('Missing accepts attribute for %s' % fullname(klass))
            return
        if isinstance(accepts, basestring):
            accepts = accepts.lower()
            if accepts in self.handlers:
                log('%s (%s) has already a handler' % (
                    accepts, fullname(klass)))
                return
            self.handlers[accepts] = klass
            return
        if isinstance(accepts, list):
            for accept in accepts:
                accept = accept.lower()
                if accept in self.handlers:
                    log('%s (%s) has already a handler' % (
                        accept, fullname(klass)))
                    continue
                self.handlers[accept] = klass

    def parse(self, data):
        try:
            result = json.loads(data)
            if not isinstance(result, dict):
                result = {}
        except ValueError:
            result = {}
        return result

    def handle(self, data, is_parsed=False):
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
        key = key.lower()
        if key not in handlers:
            return generate_error(ERROR_INVALID_REQUEST, key)
        handler = handlers[key](self)
        try:
            response = handler._handle_internal(key, request.get('data', None))
        except:
            log.err()
            return generate_error(ERROR_SYSTEM, key)
        if isinstance(response, basestring):
            return response
        if isinstance(response, dict):
            response['request'] = key
            return json.dumps(response)
        return generate_error(ERROR_SYSTEM, key)


class Handler (object):
    accepts = None

    def __init__(self, handler):
        self.handler = handler
        self.server = handler.server

    def error(self, error_code):
        return generate_error(error_code, self.accepted)

    def success(self, data=None):
        return generate_success(self.accepted, data)

    def _handle_internal(self, accepted, data):
        self.accepted = accepted
        return self.handle(data)

    def handle(self, data):
        pass


class MultiHandler (Handler):
    def handle(self, data):
        name = 'handle_%s' % self.accepted.lower().replace('-', '_')
        method = getattr(self, name, None)
        if method is None:
            log('MultiHandler is missing %s handler method' % name)
            return self.error(ERROR_SYSTEM)
        return method(data)


class PingHandler (Handler):
    accepts = 'ping'

    def handle(self, data):
        return self.success('pong')
