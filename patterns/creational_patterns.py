from copy import deepcopy
from sqlite3 import connect
from unicodedata import category
from patterns.behavioral_patterns import OblectOfObservation
from errors import RecordNotFoundError, DataBaseCommitError
from patterns.architectural_system_patterns import DomainObject


connection = connect('test_database.sqlite')

class User:
    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password
        self.role = None


class Lecturer(User):
    def __init__(self, username, email, password):
        super().__init__(username, email, password)
        self.role = 'lecturer'



class Learner(User, DomainObject):
    def __init__(self, username, email, password):
        super().__init__(username, email, password)
        self.role = 'learner'
        self.courses = []


class UserFactory:
    user_types = {
        'lecturer': Lecturer,
        'learner': Learner
    }

    @classmethod
    def create_user(cls, type_user, username, email, password):
        return cls.user_types[type_user](username, email, password)


class CoursePrototype:
    def clone(self):
        return deepcopy(self)


class Course(CoursePrototype, OblectOfObservation):
    def __init__(self, name, category):
        self.name = name
        self.category = category
        self.category.courses.append(self)
        self.type = None
        self.students = []
        super().__init__()

    def add_student(self, student):
        self.students.append(student)
        student.courses.append(self)
        self.notify()


class ThreeDayCourse(Course):
    def __init__(self, name, category):
        super().__init__(name, category)
        self.type = 'three day'


class WeekCourse(Course):
    def __init__(self, name, category):
        super().__init__(name, category)
        self.type = 'week'


class MonthCourse(Course):
    def __init__(self, name, category):
        super().__init__(name, category)
        self.type = 'month'


class CourseFactory:
    course_types = {
        'three day': ThreeDayCourse,
        'week': WeekCourse,
        'month': MonthCourse
    }

    @classmethod
    def create_course(cls, type_course, name, category):
        return cls.course_types[type_course](name, category)


class Category(DomainObject):
    id = 0

    def __init__(self, name, super_category):
        self.id = Category.id
        Category.id += 1
        self.name = name
        self.super_category = super_category
        self.courses = []

    def get_courses_count(self):
        courses_count = len(self.courses)
        if self.super_category:
            courses_count += self.super_category.get_courses_count()
        return courses_count


class Engine:
    def __init__(self):
        self.lecturers = []
        self.learners = []
        self.categories = []
        self.courses = []

    @staticmethod
    def create_user(type_user, username, email, password):
        return UserFactory.create_user(type_user, username, email, password)

    @staticmethod
    def create_course(type_course, name, category):
        return CourseFactory.create_course(type_course, name, category)

    @staticmethod
    def create_category(name, super_category=None):
        return Category(name, super_category)

    def get_category_by_id(self, category_id):
        for item in self.categories:
            print('item', item.id)
            if item.id == category_id:
                return item
        raise Exception(f'Нет категории с id = {category_id}')
    
    def get_course(self, name):
        for item in self.courses:
            if item.name == name:
                return item
        return None

    def get_student(self, name):
        for student in self.learners:
            if student.username == name:
                return student
        return None


class SingletonByName(type):

    def __init__(cls, name, bases, attrs, **kwargs):
        super().__init__(name, bases, attrs)
        cls.__instance = {}

    def __call__(cls, *args, **kwargs):
        if args:
            name = args[0]
        if kwargs:
            name = kwargs['name']

        if name in cls.__instance:
            return cls.__instance[name]
        else:
            cls.__instance[name] = super().__call__(*args, **kwargs)
            return cls.__instance[name]


class Logger(metaclass=SingletonByName):

    def __init__(self, name, writer):
        self.name = name
        self.writer = writer

    
    def log(self, text):
        data = f"LOG: <{text}>"
        self.writer.write(data)


# Architectural system pattern - Mapper
class LearnerMapper:
    def __init__(self, connection_obj):
        self.connection = connection_obj
        self.cursor = self.connection.cursor()
        self.table_name = "learner"

    def get_all(self):
        self.cursor.execute(f"SELECT * FROM {self.table_name}")
        query_result = []
        rows = self.cursor.fetchall()
        print(rows)
        for row in rows:
            id, username, email, password, role = row
            learner = Learner(username, email, password)
            learner.id = id
            query_result.append(learner)
        print(query_result)
        return query_result

    def get_row_by_id(self, id):
        self.cursor.execute(f"SELECT id, username FROM {self.table_name} WHERE id=?", (id,))
        query_result = self.cursor.fetchone()
        if not query_result:
            raise RecordNotFoundError(f"Record with id = {id} is not found.")
        return Learner(*query_result[1:4])

    def insert_row(self, obj):
        self.cursor.execute(f"INSERT INTO {self.table_name} (username, email, password, role) VALUES (?, ?, ?, ?)",
                            (obj.username, obj.email, obj.password, obj.role)
        )
        try:
            self.connection.commit()
        except Exception as e:
            raise DataBaseCommitError(f"Insert error {e.args}")

    def update_row(self, obj):
        self.cursor.execute(f"UPDATE {self.table_name} SET username=?, email=?, password=? WHERE id=?",
                            (obj.username, obj.email, obj.password, obj.id)
        )
        try:
            self.connection.commit()
        except Exception as e:
            raise DataBaseCommitError(f"Update error {e.args}")

    def delete_row(self, obj):
        self.cursor.execute(f"DELETE FROM {self.table_name} WHERE id=?", (obj.id,))
        try:
            self.connection.commit()
        except Exception as e:
            raise DataBaseCommitError(f"Delete error {e.args}")


class CategoryMapper:
    def __init__(self, connection_obj):
        self.connection = connection_obj
        self.cursor = self.connection.cursor()
        self.table_name = "category"

    def get_all(self):
        self.cursor.execute(f"SELECT * FROM {self.table_name}")
        query_result = []
        rows = self.cursor.fetchall()
        print(rows)
        for row in rows:
            id, name, super_category = row
            category = Category(name, super_category)
            category.id = id
            query_result.append(category)
        print(query_result)
        return query_result

    def get_row_by_id(self, id):
        self.cursor.execute(f"SELECT id, name FROM {self.table_name} WHERE id=?", (id,))
        query_result = self.cursor.fetchone()
        if not query_result:
            raise RecordNotFoundError(f"Record with id = {id} is not found.")
        return Category(*query_result[1:3])

    def insert_row(self, obj):
        self.cursor.execute(f"INSERT INTO {self.table_name} (name, super_category) VALUES (?, ?)",
                            (obj.name, obj.super_category)
        )
        try:
            self.connection.commit()
        except Exception as e:
            raise DataBaseCommitError(f"Insert error {e.args}")

    def update_row(self, obj):
        self.cursor.execute(f"UPDATE {self.table_name} SET name=?, super_category=? WHERE id=?",
                            (obj.name, obj.super_category, obj.id)
        )
        try:
            self.connection.commit()
        except Exception as e:
            raise DataBaseCommitError(f"Update error {e.args}")

    def delete_row(self, obj):
        self.cursor.execute(f"DELETE FROM {self.table_name} WHERE id=?", (obj.id,))
        try:
            self.connection.commit()
        except Exception as e:
            raise DataBaseCommitError(f"Delete error {e.args}")


class MapperRegistry:
    mappers = {
        'learner': LearnerMapper,
        'category': CategoryMapper
    }

    @staticmethod
    def get_mapper(obj):

        if isinstance(obj, Learner):
            return LearnerMapper(connection)
        elif isinstance(obj, Category):
            return CategoryMapper(connection)

    @staticmethod
    def get_current_mapper(name):
        return MapperRegistry.mappers[name](connection)

