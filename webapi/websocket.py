from webapi.constants import AUTH_RESPONSE

from twisted.internet.protocol import Protocol, Factory


class WebProtocol(Protocol):
    noisy = False
    authed = False
    subscribed = []

    def __init__(self, factory):
        self.factory = factory
        self.config = factory.config
        self.handler = factory.handler

    def connectionMade(self):
        self.factory.connections.append(self)

    def dataReceived(self, data):
        if not self.authed:
            if data not in self.config.get('auth_keys', []):
                self.disconnect()
                return
            self.authed = True
            self.send(AUTH_RESPONSE)
            return
        self.send(self.handler.handle(self, data))

    def subscribe(self, data):
        self.subscribed = []
        for event in data:
            self.subscribed.append(event)

    def send(self, data):
        self.transport.write(data)

    def connectionLost(self, reason="No reason"):
        self.factory.connections.remove(self)

    def disconnect(self):
        self.transport.loseConnection()


class WebFactory(Factory):
    noisy = False

    def __init__(self, config, handler):
        self.connections = []
        self.config = config
        self.handler = handler

    def broadcast(self, data):
        for connection in self.connections:
            if data['request'] in connection.subscribed:
                connection.send(data)

    def buildProtocol(self, addr):
        return WebProtocol(self)
