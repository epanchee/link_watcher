from abc import abstractmethod, ABCMeta
from typing import List


class SaveDriver(metaclass=ABCMeta):

    def __init__(self, **kwargs):
        self.sep = kwargs.get('separator', "\n")
        self.serializer = kwargs.get('serializer', None)

    def push(self, data):
        if getattr(self, 'serializer', None):
            data = self.serializer.serialize(data)
        self.ppush(data)

    @abstractmethod
    def ppush(self, data):
        pass

    @abstractmethod
    def close_output(self):
        pass

    def serialize(self):
        pass


class TextDriver(SaveDriver):

    def __init__(self, path='', **kwargs):
        super().__init__(**kwargs)
        self.ofile = open(path, 'a+')

    def ppush(self, data):
        self.ofile.write(f'{data}{self.sep}')
        self.ofile.flush()

    def close_output(self):
        self.ofile.close()


class StdoutDriver(SaveDriver):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def ppush(self, data):
        print(data, sep=self.sep or '')

    def close_output(self):
        pass


class MultipleSaveDriver(SaveDriver):

    def __init__(self, drivers: 'List[SaveDriver]', **kwargs):
        super().__init__(**kwargs)
        self.drivers = drivers

    def ppush(self, data):
        for driver in self.drivers:
            driver.push(data)

    def close_output(self):
        for driver in self.drivers:
            driver.close_output()
