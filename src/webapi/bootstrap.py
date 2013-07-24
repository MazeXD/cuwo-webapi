from cuwo.script import ConnectionScript, ServerScript


class WebAPIConnection (ConnectionScript):
    pass


class WebAPIServer (ServerScript):
    connection_class = WebAPIConnection

    def on_load(self):
        self.config = self.server.config.webapi

        # TODO instantiate RequestHandler

        if self.config.get('enable_websocket', False):
            # TODO load websocket
            pass
        if self.config.get('enable_http', False):
            # TODO load http
            pass


def get_class():
    return WebAPIServer
