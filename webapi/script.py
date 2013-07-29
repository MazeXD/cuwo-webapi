from cuwo.script import ConnectionScript, ServerScript

from webapi.websocket import WebFactory
from webapi.http import HTTP
from webapi.handler import RequestHandler
from webapi.common import log
from webapi.constants import WEBSOCKET_PORT, HTTP_PORT

from txws import WebSocketFactory


class WebAPIConnection (ConnectionScript):
    pass


class WebAPIServer (ServerScript):
    connection_class = WebAPIConnection

    def on_load(self):
        self.config = self.server.config.webapi
        self.handler = RequestHandler(self)

        # Allow other scripts to register handlers
        self.server.scripts.call('webapi_on_load', handler=self.handler)

        if self.config.get('enable_websocket', False):
            websocket_port = self.config.get('websocket_port', WEBSOCKET_PORT)
            self.server.listen_tcp(websocket_port,
                                   WebSocketFactory(
                                       WebFactory(self.config,
                                                  self.handler)))
            log('WebAPI(WebSocket) is listening on %s' % websocket_port)
        if self.config.get('enable_http', False):
            http_port = self.config.get('http_port', HTTP_PORT)
            self.server.listen_tcp(http_port, HTTP(self.config, self.handler))
            log('WebAPI(HTTP) is listening on %s' % http_port)


def get_class():
    return WebAPIServer
