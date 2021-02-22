import yaml

from fetcher.agents import FetchItem, ClassFetchItem


class FetcherConfigParser:

    def __init__(self, config_file=''):
        self.config_file = config_file
        self.fetch_base = dict()
        self.url = ''
        self.load()

    def get_related(self, related_names):
        related_refs = list()
        for related_name in related_names:
            if self.fetch_base.get(related_name):
                related_refs.append(self.fetch_base[related_name])
        return related_refs

    def parse_item(self, item_name, item_dict):
        # TODO: clean up this dirty code
        item_type = item_dict.get('type', 'content')
        if item_type == 'class':
            return ClassFetchItem(
                name=item_name,
                xpath=item_dict['xpath'],
                primary=item_dict.get('primary', False),
                related=self.get_related(item_dict.get('related', [])),
                item_type=item_dict.get('type', 'content'),
                params=item_dict.get('params', dict())
            )
        return FetchItem(
            name=item_name,
            xpath=item_dict['xpath'],
            primary=item_dict.get('primary', False),
            related=self.get_related(item_dict.get('related', []))
        )

    def load_item(self, item_list, item_name, item_dict):
        try:
            item_list[item_name] = self.parse_item(item_name, item_dict)
        except Exception as e:
            print(e)

    def load(self):
        with open(self.config_file, 'r') as conf:
            conf_items = yaml.load(conf, Loader=yaml.FullLoader)
            self.url = conf_items['url']

        # loading leaves first
        [
            self.load_item(self.fetch_base, item_name, item_dict)
            for item_name, item_dict in conf_items['items'].items()
            if not item_dict.get('related')
        ]
        # loading the rest
        [
            self.load_item(self.fetch_base, item_name, item_dict)
            for item_name, item_dict in conf_items['items'].items()
            if item_dict.get('related')
        ]

    def get_primary(self):
        self.load()
        return [item for item in self.fetch_base.values() if item.primary]
