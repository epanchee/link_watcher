from urllib import request

import lxml.html as lh


class FetchAgent:

    def __init__(self, **kwargs):
        self.url = kwargs.get('url', '')
        self.fetch_items = kwargs.get('fetch_items', [])

    def fetch(self):
        x = request.urlopen(self.url)
        tree = lh.parse(x)
        for fetch_item in self.fetch_items:
            fetched_group = []
            for item in fetch_item:
                fetched_group.extend(tree.xpath(item.xpath)[0].itertext())
            yield fetch_item.name, fetched_group


class FetchItem:

    def __init__(self, related: 'List[FetchItem] or FetchItem' = None, xpath: str = '',
                 name: str = ''):
        self.name = name
        self.xpath = xpath
        self.related = related if related else []

    def __iter__(self):
        yield self
        for item in self.related:
            yield item

    def __str__(self):
        return f'name: {self.name}, xpath: {self.xpath}, related: {self.related}'
