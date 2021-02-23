import builtins
from abc import ABCMeta, abstractmethod
from urllib import request

import lxml.html as lh
from fake_useragent import UserAgent


class FetchAgent:

    def __init__(self, **kwargs):
        self.config = kwargs['config']
        self.fetch_items = kwargs.get('fetch_items', [])

    def fetch(self):
        req = request.Request(self.config.url, headers={'User-Agent': UserAgent().random})
        x = request.urlopen(req)
        tree = lh.parse(x)
        for fetch_item in self.fetch_items:
            fetched_group = []
            for item in fetch_item:
                fetched_group.extend(item.seek_n_procces(tree))
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
