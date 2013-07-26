import json


# webapi constants
VERSION = '0.0.1'
WEBSOCKET_PORT = 12350
HTTP_PORT = 12351

# error constants (common)
ERROR_INVALID_REQUEST = -1
ERROR_INVALID_RESPONSE = -2

# error constants (http)
ERROR_INVALID_METHOD = -20
ERROR_INVALID_KEY = -21

# response constants
AUTH_RESPONSE = json.dumps({'response': 'success', 'request': 'auth'})
