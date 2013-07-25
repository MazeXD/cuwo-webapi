from cuwo.script import ConnectionScript, ServerScript
from .websocket import WebFactory
from .handlers import RequestHandler
from twisted.internet import reactor
from txws import WebSocketFactory


class WebAPIConnection (ConnectionScript):
    pass


class WebAPIServer (ServerScript):
    connection_class = WebAPIConnection

    def on_load(self):
        self.config = self.server.config.webapi
        self.handler = RequestHandler()

        if self.config.get('enable_websocket', False):
            port = self.config.websocket_port
            reactor.listenTCP(port, WebSocketFactory(WebFactory(self.config,
                                                                self.handler)))
            pass
        if self.config.get('enable_http', False):
            # TODO load http
            pass


def get_class():
    return WebAPIServer
