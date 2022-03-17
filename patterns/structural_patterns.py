import time

class AppRoute:
    def __init__(self, routes, url):

        self.routes = routes
        self.url = url

    def __call__(self, cls):

        self.routes[self.url] = cls()


class TimeMetric:
    def __init__(self, name_cls):
        self.name = name_cls

    def __call__(self, cls):
        def get_time_metric(method):
            def wrapper(*args, **kwargs):
                time_start = time.time()
                call_method = method(*args, **kwargs)
                time_end = time.time()
                time_delta = time_end - time_start
                print(f"The class {self.name} method call lasted: {time_delta} microseconds.")
                return call_method
            return wrapper
        return get_time_metric(cls)

