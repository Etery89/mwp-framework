from threading import local


class DomainObject:

    def mark_new(self):
        UnitOfWork.get_current_thread().mark_new(self)

    def mark_dirty(self):
        UnitOfWork.get_current_thread().mark_dirty(self)

    def mark_removed(self):
        UnitOfWork.get_current_thread().mark_removed(self)


class UnitOfWork:
    current_thread = local()

    def __init__(self):
        self.new_objects = []
        self.dirty_objects = []
        self.removed_objects = []

    def set_mapper_registry(self, MapperRegistry):
        self.MapperRegistry = MapperRegistry

    def mark_new(self, obj):
        self.new_objects.append(obj)

    def mark_dirty(self, obj):
        self.dirty_objects.append(obj)

    def mark_removed(self, obj):
        self.removed_objects.append(obj)

    def insert_new(self):
        for obj in self.new_objects:
            self.MapperRegistry.get_mapper(obj).insert_row(obj)

    def update_dirty(self):
        for obj in self.dirty_objects:
            self.MapperRegistry.get_mapper(obj).update_row(obj)

    def delete_removed(self):
        for obj in self.removed_objects:
            self.MapperRegistry.get_mapper(obj).delete_row(obj)

    def commit(self):
        self.insert_new()
        self.update_dirty()
        self.delete_removed()

        self.new_objects.clear()
        self.dirty_objects.clear()
        self.removed_objects.clear()

    @staticmethod
    def new_current_thread():
        __class__.set_current_thread(UnitOfWork())

    @classmethod
    def set_current_thread(cls, unit_of_work):
        cls.current_thread.unit_of_work = unit_of_work

    @classmethod
    def get_current_thread(cls):
        return cls.current_thread.unit_of_work



