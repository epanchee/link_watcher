from argparse import ArgumentParser

from daemon import FetchDaemon
from fetcher.agents import FetchItem, FetchAgent
from fetcher.config_parser import FetcherConfigParser
from fetcher.serializing import JsonSerializer
from fetcher.storing import MultipleSaveDriver, StdoutDriver, TextDriver

driver2class = {
    'stdout': StdoutDriver,
    'text': TextDriver
}

serializer2class = {
    'json': JsonSerializer
}

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
        '--serializer', '-d', type=str, choices=['json'],
        help="Choose the serialization mechanism"
    )
    parser.add_argument(
        '--text_output',
        type=str,
        help="Output file if TextDriver was chosen"
    )

    args = parser.parse_args()

    output_driver = StdoutDriver()
    kwargs = dict()     # TODO: remove this workaround
    if args.text_output:
        kwargs['path'] = args.text_output
    if args.save_driver:
        if len(args.save_driver) > 1:
            output_driver = MultipleSaveDriver(
                drivers=[driver2class[driver](**kwargs) for driver in args.save_driver]
            )
        else:
            output_driver = driver2class[args.save_driver[0]](**kwargs)
    if args.serializer:
        output_driver.serializer = serializer2class[args.serializer]

    config = FetcherConfigParser(config_file=args.config)
    fd = FetchDaemon(
        agent=FetchAgent(
            url=config.url,
            fetch_items=config.get_primary()
        ),
        output_driver=output_driver,
        interval=args.interval
    )
    fd.start()
