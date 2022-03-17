from wsgiref.simple_server import make_server
from komarova_framework.main import Framework
from urls import front_controllers
from views import routes


application = Framework(routes, front_controllers)


with make_server('', 8080, application) as httpd:
    print("Serving on port 8080...")
    httpd.serve_forever()
