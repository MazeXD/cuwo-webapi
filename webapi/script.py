from cuwo.script import ConnectionScript, ServerScript

from webapi.websocket import WebFactory
from webapi.http import HTTP
from webapi.handler import RequestHandler
from webapi.common import log
from webapi.constants import VERSION, WEBSOCKET_PORT, HTTP_PORT

from txws import WebSocketFactory


class WebAPIConnection (ConnectionScript):
    pass


class WebAPIServer (ServerScript):
    connection_class = WebAPIConnection
    script_fullname = 'WebAPI'
    script_description = 'Provides an api to access internals over ' \
                         'http and websockets'
    script_version = VERSION

    def on_load(self):
        self.config = self.server.config.webapi
        self.handler = RequestHandler(self)

        self._collect_script_data()

        # Allow other scripts to register handlers
        self.server.scripts.call('webapi_on_load', handler=self.handler)

        if self.config.get('enable_websocket', False):
            websocket_port = self.config.get('websocket_port', WEBSOCKET_PORT)
            self.websocket = WebSocketFactory(WebFactory(self.config,
                                                         self.handler))
            self.server.listen_tcp(websocket_port, self.websocket)
            log('WebAPI(WebSocket) is listening on %s' % websocket_port)
        if self.config.get('enable_http', False):
            http_port = self.config.get('http_port', HTTP_PORT)
            self.http = HTTP(self.config, self.handler)
            self.server.listen_tcp(http_port, self.http)
            log('WebAPI(HTTP) is listening on %s' % http_port)

    def _collect_script_data(self):
        script_data = {}
        scripts = self.server.scripts.scripts
        for internal_name in scripts.keys():
            script = scripts[internal_name]
            name = getattr(script, 'script_fullname', internal_name)
            description = getattr(script, 'script_description', '')
            version = getattr(script, 'script_version', 'unknown')
            script_data[internal_name] = {
                'name': name,
                'description': description,
                'version': version
            }
        self.script_data = script_data


def get_class():
    return WebAPIServer
