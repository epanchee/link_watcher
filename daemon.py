import logging
import os
from glob import glob
from time import sleep

from fetcher.agents import FetchAgent
from fetcher.config_parser import FetcherConfigParser
from fetcher.storing import SaveDriver


def list_configs(conf_path):
    return [conf_path] if os.path.isfile(conf_path) else glob(f"{conf_path}/*.yaml")


class FetchDaemon:

    def __init__(
            self,
            conf_path: str = '',
            output_driver: SaveDriver = None,
            interval: int = 600
    ):
        configs = [
            FetcherConfigParser(config_path=config) for config in list_configs(conf_path)
        ]
        self.agents = [
            FetchAgent(
                config=config,
                fetch_items=config.get_primary()
            )
            for config in configs
        ]
        self.output_driver = output_driver
        self.interval = interval
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        logging.basicConfig(format='%(asctime)s %(message)s')

    def start(self):
        self.logger.info(f'Fetching daemon started. Interval: {self.interval} sec')
        while True:
            try:
                for agent in self.agents:
                    self.logger.info(f'Started fetching {agent.config.config_path}')
                    for data in agent.fetch():
                        self.output_driver.push(data)
                    self.logger.info('Fetching done')
                sleep(self.interval)
            except (KeyboardInterrupt, SystemExit):
                self.logger.info('Stopping fetching daemon ...')
                self.output_driver.close_output()
                break
            except Exception as e:
                self.logger.exception(e)
