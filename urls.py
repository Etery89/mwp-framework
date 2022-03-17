from datetime import datetime
from start_views import Contacts, Page

start_routes = {
    "/contacts/": Contacts(),
    "/page/": Page()
}


def date_front(request):
    request['date'] = datetime.now().strftime("%d %B %Y")



def key_front(request):
    request['key'] = 'key'


front_controllers = [date_front, key_front]