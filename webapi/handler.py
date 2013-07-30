from webapi.common import (generate_error, generate_success, log, fullname,
                           encode_player)
from webapi.constants import (ERROR_INVALID_REQUEST, ERROR_SYSTEM,
                              ERROR_INVALID_PLAYER)

from cuwo.script import get_player, InvalidPlayer

from twisted.python import log as logging

import inspect
import json
import sys
import time


class InvalidRequest(Exception):
    pass


def requires(*args):
    def requires(func):
        def new_func(self, data):
            if data is None:
                raise InvalidRequest()
            if len(args) > 0:
                if not isinstance(data, dict):
                    raise InvalidRequest()
                for arg in args:
                    if arg not in data:
                        raise InvalidRequest()
            return func(self, data)
        new_func.__module__ = func.__module__
        new_func.func_name = func.func_name
        return new_func
    return requires


def validate(arg=None, **kwargs):
    def validate(func):
        if len(kwargs) == 0 and not arg:
            return func

        def new_func(self, data):
            if arg:
                if not isinstance(data, arg):
                    raise InvalidRequest()
                return func(self, data)
            for key in kwargs.keys():
                if key in data:
                    if not isinstance(data[key], kwargs[key]):
                        raise InvalidRequest()
            return func(self, data)
        new_func.__module__ = func.__module__
        new_func.func_name = func.func_name
        return new_func
    return validate


class RequestHandler (object):
    handlers = {}

    def __init__(self, script):
        self.script = script
        self.server = script.server
        self._loadHandlers()

    def _loadHandlers(self):
        classes = inspect.getmembers(sys.modules[__name__], inspect.isclass)
        for (name, klass) in classes:
            if issubclass(klass, Handler):
                if klass is not Handler and klass is not MultiHandler:
                    self.add(klass)

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
        except InvalidPlayer:
            return generate_error(ERROR_INVALID_PLAYER, key)
        except InvalidRequest:
            return generate_error(ERROR_INVALID_REQUEST, key)
        except:
            logging.err()
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

    def get_player(self, name):
        if not name or not isinstance(name, basestring):
            raise InvalidPlayer()
        return get_player(self.server, name)

    def _handle_internal(self, accepted, data):
        self.accepted = accepted
        response = self.handle(data)
        if isinstance(response, basestring):
            try:
                json.loads(response)
                return response
            except ValueError:
                pass
        return self.success(response)

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
        return 'pong'


class ScriptHandler (MultiHandler):
    accepts = ['get-scripts']

    def handle_get_scripts(self, data):
        return self.handler.script.script_data


class PlayerHandler (MultiHandler):
    accepts = ['get-players', 'get-player']

    @requires()
    @validate(basestring)
    def handle_get_player(self, data):
        player = self.get_player(data)
        return encode_player(player, True)

    def handle_get_players(self, data):
        players = {}
        for player in self.server.players.values():
            players[player.entity_id] = encode_player(player)
        return players


class ChatHandler (Handler):
    accepts = 'send-message'

    @requires('message')
    @validate(message=basestring, player=basestring)
    def handle(self, data):
        message = data.get('message', None)
        name = data.get('player', None)
        if name:
            player = self.get_player(name)
            player.send_chat(message)
        else:
            self.server.send_chat(message)


class TimeHandler (MultiHandler):
    accepts = ['get-time', 'set-time']

    def handle_get_time(self, data):
        return self.success(self.server.get_clock())

    @requires()
    @validate(basestring)
    def handle_set_time(self, data):
        try:
            time.strptime(data, '%H:%M')
            self.server.set_clock(data)
        except ValueError:
            raise InvalidRequest


class CommandHandler (MultiHandler):
    accepts = ['kick', 'ban']

    @requires('player')
    @validate(player=basestring)
    def handle_kick(self, data):
        player = self.get_player(data['player'])
        player.kick()

    @requires('player')
    @validate(player=basestring, reason=basestring)
    def handle_ban(self, data):
        player = self.get_player(data['player'])
        reason = data.get('reason', "No reason specified")
        self.server.call_scripts('ban', player.address.host, reason)
