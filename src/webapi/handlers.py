from webapi.common import (generate_error, generate_success, log, fullname,
                           encode_player)
from webapi.constants import (ERROR_INVALID_REQUEST, ERROR_SYSTEM,
                              ERROR_INVALID_PLAYER)

from cuwo.script import get_player, InvalidPlayer

from twisted.python import log as logging

import inspect
import json


class RequestHandler (object):
    handlers = {}

    def __init__(self, webapi):
        self.server = webapi.server
        self.add(PingHandler)
        self.add(PlayerHandler)
        self.add(ChatHandler)
        self.add(CommandHandler)
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
        except InvalidPlayer:
            return generate_error(ERROR_INVALID_PLAYER, key)
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
        response = method(data)
        if isinstance(response, basestring):
            return response
        return self.success(response)


class PingHandler (Handler):
    accepts = 'ping'

    def handle(self, data):
        return self.success('pong')


class PlayerHandler (MultiHandler):
    accepts = ['get-players', 'get-player']

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

    def handle(self, data):
        if not data or not isinstance(data, dict):
            return self.error(ERROR_INVALID_REQUEST)
        message = data.get('message', None)
        name = data.get('player', None)
        if not message or not isinstance(message, basestring):
            return self.error(ERROR_INVALID_REQUEST)
        if name:
            player = self.get_player(name)
            player.send_chat(message)
        else:
            self.server.send_chat(message)


class CommandHandler (MultiHandler):
    accepts = ['kick', 'ban']

    def handle_kick(self, data):
        if not data or not isinstance(data, dict):
            return self.error(ERROR_INVALID_REQUEST)
        if data['id'] is not None:
            player = self.get_player(data['id'])
        elif data['name'] is not None:
            player = self.get_player(data['name'])
        else:
            return self.error(ERROR_INVALID_REQUEST)
        player.kick()
        return self.success()

    def handle_ban(self, data):
        if not data or not isinstance(data, dict):
            return self.error(ERROR_INVALID_REQUEST)
        if data['id'] is not None:
            player = self.get_player(data['id'])
        elif data['name'] is not None:
            player = self.get_player(data['name'])
        else:
            return self.error(ERROR_INVALID_REQUEST)
        reason = data.get('reason', "No reason specified")
        self.server.call_scripts('ban', player.address.host, reason)
        return self.success()
