import json
import time
from jsonpickle import dumps, loads
from komarova_framework.templator import render
from komarova_framework.utils import decode_value

class Observer:

    def __init__(self, name):
        self.name = name

    def update(self, object_observation, text):
        pass


class OblectOfObservation:

    def __init__(self):
        self.observers = []

    def notify(self):
        for observer in self.observers:
            observer.update(self)


class MessengerNotifier(Observer):

    def update(self, object_observation):
        print("We notify subscribers in the messenger...")
        print(f"{self.name}: <К курсу {object_observation.name} присоединился {object_observation.students[-1].username}>")


class EmailNotifier(Observer):

    def update(self, object_observation):
        print("We notify subscribers in the site...")
        print(f"{self.name}: <К курсу {object_observation.name} присоединился {object_observation.students[-1].username}>")


class ConsoleDebugNotifier(Observer):

    def update(self, object_observation):
        print("Debug notify...")
        print(f"{self.name}: <К курсу {object_observation.name} присоединился {object_observation.students[-1].username}>")


class TemplateView:
    template_name = 'template.html'

    def get_context_data(self):
        return {}

    def get_template_name(self):
        return self.template_name

    def render_template_with_context(self):
        template_name = self.get_template_name()
        context = self.get_context_data()
        return '200 OK', render(template_name, **context)

    def __call__(self, request):
        return self.render_template_with_context()


class ListView(TemplateView):
    queryset = []
    template_name = 'list.html'
    context_object_name = 'objects_list'

    def get_queryset(self):
        return self.queryset

    def get_context_object_name(self):
        return self.context_object_name

    def get_context_data(self):
        queryset = self.get_queryset()
        context_object_name = self.get_context_object_name()
        context = {context_object_name: queryset}
        return context


class CreateView(TemplateView):
    template_name = 'create.html'

    @staticmethod
    def get_request_data(request):
        return request['data']

    def create_obj(self, data):
        pass

    def __call__(self, request):
        if request['method'] == 'POST':
            data = self.get_request_data(request)
            self.create_obj(data)

            return self.render_template_with_context()
        else:
            return super().__call__(request)


class JsonSerializer:
    def __init__(self, obj):
        self.object_to_serialize = obj        

    def save_by_json(self):
        return dumps(self.object_to_serialize, indent=4)
    
    def load_by_python(self, data):
        return loads(data)


class DebugWriter:

    def write(self, data):
        print(data)


class FileWriter:

    def __init__(self):
        self.filename = "debug_log"

    def write(self, data):
        with open(self.filename, "a", encoding="utf-8") as f:
            f.write(f"{time.time()}: {data}\n")


