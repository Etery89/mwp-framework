
class RecordNotFoundError(Exception):
    def __init__(self, message):
        super().__init__(f'Record not found: {message}')


class DataBaseCommitError(Exception):
    def __init__(self, message):
        super().__init__(f'Db commit error: {message}')