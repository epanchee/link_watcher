import logging
from abc import abstractmethod, ABCMeta
from time import sleep
from typing import List

import psycopg2
import requests


class SaveDriver(metaclass=ABCMeta):

    def __init__(self, **kwargs):
        self.sep = kwargs.get('separator', "\n")
        self.serializer = kwargs.get('serializer', None)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.DEBUG if kwargs.get('debug', False) else logging.INFO)
        logging.basicConfig(format='%(name)s: %(asctime)s %(message)s')

    def push(self, data):
        try:
            if getattr(self, 'serializer', None):
                data = self.serializer.serialize(data)
            if data:
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


class TelegramSaveDriver(SaveDriver):

    def __init__(self, api_token: str = '', chat_id='', **kwargs):
        super().__init__(**kwargs)
        self.send_url = f"https://api.telegram.org/bot{api_token}/sendMessage?chat_id={chat_id}\
        &parse_mode=html&text={{message}}"

    def close_output(self):
        pass

    def ppush(self, data):
        requests.get(url=self.send_url.format(message=data), timeout=1)


class PostgresSaveDriver(SaveDriver):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.con = self.try_to_connect()
        if not self.con:
            return
        self.cur = self.con.cursor()
        try:
            self.cur.execute('''CREATE TABLE fetched
                  (
                      id SERIAL PRIMARY KEY,
                      data VARCHAR(1024)  NOT NULL,
                      ts TIMESTAMP DEFAULT NOW()
                  );''')
            self.con.commit()
            self.logger.info("Table created successfully")
        except Exception:
            pass

    def try_to_connect(self):
        con = None
        for _ in range(5):
            try:
                con = psycopg2.connect(database="postgres", user="postgres", password="postgres",
                                       host='docker_db' or "127.0.0.1", port="5432")
                break
            except Exception as e:
                self.logger.error(e)
                sleep(3)
        return con

    def close_output(self):
        if self.con:
            self.con.close()

    def ppush(self, data):
        if self.con:
            self.cur.execute(f"INSERT INTO fetched (data) VALUES (%s);", [data])
            self.con.commit()


driver2class = {
    'stdout': StdoutDriver,
    'text': TextDriver,
    'telegram': TelegramSaveDriver,
    'postgres': PostgresSaveDriver
}
