import os
from glob import glob

import yaml

from fetcher.agents import FetchItem, ClassFetchItem


class NoConfigException(Exception):
    pass


def list_configs(conf_path):
    conf_list = [conf_path] if os.path.isfile(conf_path) else glob(f"{conf_path}/*.yaml")
    if conf_list:
        return conf_list
    else:
        raise NoConfigException(f"No configs found at {conf_path}")


class FetcherConfigParser:

    def __init__(self, config_path=''):
        self.config_path = config_path
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
        item_list[item_name] = self.parse_item(item_name, item_dict)

    def load(self):
        with open(self.config_path, 'r') as conf:
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
        return [item for item in self.fetch_base.values() if item.primary]
