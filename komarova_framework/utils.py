from quopri import decodestring


def decode_value(val):
    val_b = bytes(val.replace('%', '=').replace("+", " "), 'UTF-8')
    val_decode_str = decodestring(val_b)
    return val_decode_str.decode('UTF-8')