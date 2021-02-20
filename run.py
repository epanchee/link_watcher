from argparse import ArgumentParser

from daemon import FetchDaemon
from fetcher.agents import FetchItem, FetchAgent
from fetcher.config_parser import FetcherConfigParser
from fetcher.serializing import JsonSerializer
from fetcher.storing import MultipleSaveDriver, StdoutDriver, TextDriver

floor = FetchItem(xpath='/html/body/div[2]/section/div[2]/div[2]/div[1]/div[1]/div[4]')
flat1 = FetchItem(xpath='/html/body/div[2]/section/div[2]/div[2]/div[1]/div[2]/div/div[7]/div[4]',
                  name='flat1', related=floor)
floor = FetchItem(xpath='/html/body/div[2]/section/div[2]/div[2]/div[1]/div[1]/div[2]')
flat2 = FetchItem(xpath='/html/body/div[2]/section/div[2]/div[2]/div[1]/div[2]/div/div[7]/div[2]',
                  name='flat2', related=floor)

atomstroy = FetchAgent(
    url='https://www.atomstroy.net/zhilaya_nedvizhimost/art-gorod-park/ceny-i-nalichie',
    fetch_items=[flat1, flat2]
)

fd = FetchDaemon(
    agent=atomstroy,
    output_driver=MultipleSaveDriver(drivers=[
        StdoutDriver(),
        TextDriver(serializer=JsonSerializer, path='/tmp/fetcher.out')
    ]),
    interval=10
)

# fd.start()

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument(
        '--interval', '-i', type=int, default=600,
        help='Interval between fetching'
    )
    parser.add_argument('--config', '-c', type=str, help='Path to YAML config', required=True)
    parser.add_argument(
        '--save_driver', '-s', type=str, nargs='+',
        help="Choose how to save the data. You can use multiple drivers. 'stdout', 'text' are "
             "available "
    )
    parser.add_argument(
        '--text_output',
        type=str,
        help="Save data to this file if TextDriver was chosen"
    )

    args = parser.parse_args()

    config = FetcherConfigParser(config_file=args.config)
    fd = FetchDaemon(
        agent=FetchAgent(
            url=config.url,
            fetch_items=config.get_primary()
        ),
        output_driver=MultipleSaveDriver(drivers=[
            StdoutDriver(),
            TextDriver(serializer=JsonSerializer, path='/tmp/fetcher.out')
        ]),
        interval=args.interval
    )
    fd.start()
