import logging
from abc import abstractmethod, ABCMeta
from typing import List


class SaveDriver(metaclass=ABCMeta):

    def __init__(self, **kwargs):
        self.sep = kwargs.get('separator', "\n")
        self.serializer = kwargs.get('serializer', None)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.DEBUG if kwargs.get('debug', False) else logging.INFO)
        logging.basicConfig(format='%(asctime)s %(message)s')

    def push(self, data):
        try:
            if getattr(self, 'serializer', None):
                data = self.serializer.serialize(data)
            self.ppush(data)
        except Exception as e:
            self.logger.error(e)
        self.logger.debug(f"Saved data {data} using {self.__class__}")

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
        self.logger.info(f"Saving data as text to {path}")

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


driver2class = {
    'stdout': StdoutDriver,
    'text': TextDriver
}
