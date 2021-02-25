import builtins
import logging
from abc import ABCMeta, abstractmethod

import lxml.html as lh
import requests


def gen_req_headers():
    return {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:85.0) Gecko/20100101 Firefox/85.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'ru,en;q=0.9,zh;q=0.8,nl;q=0.7,es;q=0.6',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive'
    }


class FetchAgent:

    def __init__(self, **kwargs):
        self.config = kwargs['config']
        self.fetch_items = kwargs.get('fetch_items', [])
        self.fetch_timeout = kwargs.get('fetch_timeout', 3)
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG if kwargs.get('debug', False) else logging.INFO)
        logging.basicConfig(format='%(asctime)s %(message)s')

    def fetch(self):
        response = requests.get(self.config.url, timeout=self.fetch_timeout, headers=gen_req_headers())
        tree = lh.fromstring(response.text)
        self.logger.debug(f"Scraping {self.config.url}")
        for fetch_item in self.fetch_items:
            fetched_group = []
            for item in fetch_item:
                try:
                    fetched_group.extend(item.seek_n_procces(tree))
                    self.logger.debug(f"Fetched {item.name}")
                except Exception as e:
                    self.logger.error(e)
            if fetched_group:
                yield fetch_item.name, fetched_group


class BaseFetchItem(metaclass=ABCMeta):

    def __init__(
            self,
            related: 'List[FetchItem] or FetchItem' = None,
            xpath: str = '',
            primary: bool = False,
            name: str = '',
            item_type: str = 'content',
            params: dict = None,
    ):
        self.name = name
        self.xpath = xpath
        self.related = related if related else []
        self.primary = primary
        self.item_type = item_type
        self.params = params

    def seek_n_procces(self, tree):
        return self.process(self.seek(tree))

    def __iter__(self):
        yield self
        for item in self.related:
            yield item

    def __str__(self):
        return f'name: {self.name}, item_type: {self.item_type},' \
               f' xpath: {self.xpath}, related: {self.related}, primary: {self.primary}'

    def process(self, data):
        return data

    @abstractmethod
    def seek(self, tree):
        pass


class FetchItem(BaseFetchItem):
    """
    Simple FetchItem to retrieve raw data from DOM-element without processing
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def seek(self, tree):
        return tree.xpath(self.xpath)[0].itertext()


class ClassFetchItem(BaseFetchItem):
    """
    FetchItem to check whether DOM-element has class from given list self.params['classes'] or not
    """

    def seek(self, tree):
        return list(tree.xpath(self.xpath)[0].classes)

    def check_inside(self, data):
        result = False
        condition = getattr(builtins, self.params.get('condition', 'any'))
        params = self.params.get('classes', list())
        if isinstance(params, list):
            result = condition([
                data_item in self.params['classes']
                for data_item in data
            ])
        return result

    def process(self, data):
        return [self.name if self.check_inside(data) else '']
