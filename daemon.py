import logging
from time import sleep

from fetcher.agents import FetchAgent
from fetcher.config_parser import FetcherConfigParser
from fetcher.storing import SaveDriver


class FetchDaemon:

    def __init__(
            self,
            config: str = '',
            output_driver: SaveDriver = None,
            interval: int = 600
    ):
        self.config = FetcherConfigParser(config_file=config)
        self.agent = FetchAgent(
            url=self.config.url,
            fetch_items=self.config.get_primary()
        )
        self.output_driver = output_driver
        self.interval = interval
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        logging.basicConfig(format='%(asctime)s %(message)s')

    def start(self):
        self.logger.info(f'Fetching daemon started. Interval: {self.interval} sec')
        while True:
            try:
                for data in self.agent.fetch():
                    self.output_driver.push(data)
                self.logger.info('Fetching done')
                sleep(self.interval)
            except (KeyboardInterrupt, SystemExit):
                self.logger.info('Stopping fetching daemon ...')
                self.output_driver.close_output()
                break
            except Exception as e:
                self.logger.exception(e)
