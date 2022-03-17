from quopri import decodestring
from komarova_framework.methods_handlers import *

class PageNotFound404:
    def __call__(self, request):
        return '404 WHAT', '404 PAGE Not Found'


class Framework:
    """Main class framework. Application"""

    def __init__(self, routes, fronts_controllers):
        self.routes = routes
        self.fronts_controllers = fronts_controllers

    def __call__(self, environ, start_response):
        path = environ['PATH_INFO']
        if path in self.routes:
            view = self.routes[path]
        else:
            view = PageNotFound404()

        request = {}
        method = environ['REQUEST_METHOD']
        request['method'] = method

        if method == 'GET':
            query = environ['QUERY_STRING']
            query_parameters = self.decode_value(parse_query_data(query))
            print(f'Get query - {query_parameters}')
            request['request_parameters'] = query_parameters
        if method == 'POST':
            post_query = parse_wsgi_input_data(get_wsgi_input_data(environ))
            query_data = self.decode_value(post_query)
            print(f'Post query - {query_data}')
            request['data'] = query_data

        for controller in self.fronts_controllers:
            controller(request)
        code, body = view(request)
        start_response(code, [('Content-Type', 'text/html')])
        return [body.encode('utf-8')]

    def decode_value(self, data):
        new_data = {}
        for key, value in data.items():
            new_value = bytes(value.replace('%', '=').replace("+", " "), 'UTF-8')
            new_key = bytes(key.replace('%', '=').replace("+", " "), 'UTF-8')
            new_value_decode_str = decodestring(new_value).decode('UTF-8')
            new_key_decode_str = decodestring(new_key).decode('UTF-8')
            new_data[new_key_decode_str] = new_value_decode_str
        return new_data
