import json


def generate_error(error_code, request=None):
    result = {
        'response': 'error',
        'data': error_code
    }
    if isinstance(request, basestring):
        result['request'] = request
    return json.dumps(result)


def generate_success(request, data=None):
    result = {
        'response': 'success'
    }
    if data is not None:
        result['data'] = data
    if isinstance(request, basestring):
        result['request'] = request
    return json.dumps(result)


def log(message):
    print '[WebAPI] %s' % message


def fullname(klass):
    module = klass.__module__
    if not module:
        return klass.__name__
    return module + "." + klass.__name__
