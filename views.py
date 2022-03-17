from multiprocessing import context
from os import name
from komarova_framework.templator import render
from patterns.creational_patterns import Engine, Logger, MapperRegistry
from komarova_framework.utils import decode_value
from patterns.structural_patterns import AppRoute, TimeMetric
from urls import start_routes
from patterns.behavioral_patterns import MessengerNotifier, EmailNotifier, ConsoleDebugNotifier,\
    ListView, CreateView, FileWriter, JsonSerializer

from patterns.architectural_system_patterns import UnitOfWork


engine = Engine()
logger = Logger('komarova_framework', FileWriter())
messenger_notifier = MessengerNotifier("MESSENGER")
email_notifier = EmailNotifier("EMAIL")
debug_notifier = ConsoleDebugNotifier("CONSOLE")

course_types = ['three day', 'week', 'month']
routes = start_routes

UnitOfWork.new_current_thread()
UnitOfWork.get_current_thread().set_mapper_registry(MapperRegistry)


@AppRoute(routes=routes, url="/")
class Index:
    @TimeMetric(name_cls='Index')
    def __call__(self, request):
        logger.log("Переход на главную страницу")
        mapper = MapperRegistry.get_current_mapper('category')
        categories = mapper.get_all()
        print(categories)
        return '200 OK', render("index.html", objects_list=categories)


@AppRoute(routes=routes, url="/create-category/")
class CreateCategory:
    def __call__(self, request):
        logger.log("Переход на страницу добавления категорий")
        if request['method'] == 'POST':

            data = request['data']

            name = data['name']
            name = decode_value(name)
            print(name)

            category_id = data.get('category_id')

            category = None
            if category_id:
                category = engine.get_category_by_id(int(category_id))

            new_category = engine.create_category(name, category)

            engine.categories.append(new_category)
            new_category.mark_new()
            UnitOfWork.get_current_thread().commit()

            return '200 OK', render('index.html', objects_list=engine.categories)
        else:
            categories = engine.categories
            return '200 OK', render('create_category.html',
                                    categories=categories)


@AppRoute(routes=routes, url="/create-course/")
class CreateCourse:
    category_id = -1

    def __call__(self, request):
        logger.log("Переход на страницу добавления курсов")
        if request['method'] == 'POST':
            data = request['data']

            name = data['name']
            name = decode_value(name)
            type_course = data['type']
            type_course = decode_value(type_course)

            try:
                if type_course not in course_types:
                    raise KeyError
            except KeyError:
                return '200 OK', 'A course of this type cannot be added'

            category = None
            if self.category_id != -1:
                category = engine.get_category_by_id(int(self.category_id))

                course = engine.create_course(type_course, name, category)
                course.observers.append(messenger_notifier)
                course.observers.append(email_notifier)
                course.observers.append(debug_notifier)
                engine.courses.append(course)

            return '200 OK', render('course_list.html',
                                    objects_list=category.courses,
                                    name=category.name,
                                    id=category.id)
        else:
            try:
                self.category_id = int(request['request_parameters']['id'])
                category = engine.get_category_by_id(int(self.category_id))

                return '200 OK', render('create_course.html',
                                        name=category.name,
                                        id=category.id)
            except KeyError as err:
                print(err)
                return '200 OK', 'No categories have been added yet'


@AppRoute(routes=routes, url="/courses-list/")
class CoursesList:
    def __call__(self, request):
        logger.log("Переход на страницу со списком курсов конкретной категории")
        try:
            category = engine.get_category_by_id(int(request['request_parameters']['id']))
            return '200 OK', render('course_list.html',
                                    objects_list=category.courses,
                                    name=category.name, id=category.id)
        except KeyError as err:
            print(err)
            return '200 OK', 'No courses have been added yet'


@AppRoute(routes=routes, url="/copy-course/")
class CopyCourse:
    def __call__(self, request):
        logger.log("Выполнение копирования существующего курса")
        request_params = request['request_parameters']

        try:
            name = request_params['name']

            old_course = engine.get_course(name)
            if old_course:
                new_name = f'copy_{name}'
                new_course = old_course.clone()
                new_course.name = new_name
                engine.courses.append(new_course)

            return '200 OK', render('course_list.html',
                                    objects_list=engine.courses,
                                    name=new_course.category.name)
        except KeyError:
            return '200 OK', 'No courses have been added yet'


@AppRoute(routes=routes, url="/create-student/")
class StudentCreateView(CreateView):
    template_name = "create_student.html"
    
    def create_obj(self, data):
        name = decode_value(data["name"])
        email = decode_value(data["email"])
        password = decode_value(data["password"])
        new_student = engine.create_user(type_user="learner", username=name, email=email, password=password)
        engine.learners.append(new_student)
        new_student.mark_new()
        UnitOfWork.get_current_thread().commit()


@AppRoute(routes=routes, url="/student-list/")
class StudentListView(ListView):
    template_name = "student_list.html"
    
    def get_queryset(self):
        mapper = MapperRegistry.get_current_mapper('learner')
        return mapper.get_all()


@AppRoute(routes=routes, url="/add-student/")
class AddStudentByCourseCreateView(CreateView):
    template_name = "add_student.html"

    def get_context_data(self):
        context = super().get_context_data()
        context["courses"] = engine.courses
        mapper = MapperRegistry.get_current_mapper('learner')
        context["students"] = mapper.get_all()
        return context

    def create_obj(self, data):
        course_name = decode_value(data["course_name"])
        student_name = decode_value(data["student_name"])
        course = engine.get_course(course_name)
        student = engine.get_student(student_name)
        course.add_student(student)


@AppRoute(routes=routes, url="/api-course/")
class CourseApi:

    def __call__(self, request):
        logger.log("Сериализация списка курсов.")
        courses = engine.courses
        return "200 OK", JsonSerializer(courses).save_by_json()

