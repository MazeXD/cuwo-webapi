from cuwo.script import ConnectionScript, ServerScript

from webapi.websocket import WebFactory
from webapi.handlers import RequestHandler

from txws import WebSocketFactory


class WebAPIConnection (ConnectionScript):
    pass


class WebAPIServer (ServerScript):
    connection_class = WebAPIConnection

    def on_load(self):
        self.config = self.server.config.webapi
        self.handler = RequestHandler()

        if self.config.get('enable_websocket', False):
            websocket_port = self.config.get('websocket_port', 12350)
            self.server.listen_tcp(websocket_port,
                                   WebSocketFactory(
                                       WebFactory(self.config,
                                                  self.handler)))
        if self.config.get('enable_http', False):
            # TODO load http
            pass


def get_class():
    return WebAPIServer
