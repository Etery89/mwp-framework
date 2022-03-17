

def parse_query_data(query_string):
    dict_query_string = {}
    if query_string:
        request_params = query_string.split('&')
        for param in request_params:
            key, value = param.split("=")
            dict_query_string[key] = value
    return dict_query_string


def get_wsgi_input_data(environ):
    content_length = environ["CONTENT_LENGTH"]
    if content_length:
        content_length = int(content_length)
    else:
        content_length = 0

    if content_length > 0:
        query_bytes = environ['wsgi.input'].read(content_length)
    else:
        query_bytes = b''
    return query_bytes


def parse_wsgi_input_data(query_bytes):
    dict_query_data = {}
    if query_bytes:
        data_string = query_bytes.decode(encoding='utf-8')
        # print(f'Decode string - {data_string}')
        dict_query_data = parse_query_data(data_string)
    return dict_query_data

