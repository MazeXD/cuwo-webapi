import json


class RequestHandler (object):
    handlers = {}

    def __init__(self):
        # TODO get all handlers inside this module
        pass

    def add(self, handler):
        # TODO
        pass

    def handle(self, request):
        response = None
        return response


class Handler (object):
    request = None

    def handle(self, request):
        pass
