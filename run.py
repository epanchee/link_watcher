import os
from argparse import ArgumentParser

from fetcher.daemon import FetchDaemon
from fetcher.serializing import serializer2class
from fetcher.storing import MultipleSaveDriver, driver2class

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument(
        '--interval', '-i', type=int, default=600,
        help='Interval between fetching'
    )
    parser.add_argument(
        '--config', '-c', type=str,
        help='Path to YAML config file or directory. Default is "config/"', default='config'
    )
    parser.add_argument(
        '--save_driver', '-s', type=str, nargs='+',
        help=f"Choose how to save the data. You can use multiple drivers. "
             f"{list(driver2class.keys())} are available"
    )
    parser.add_argument(
        '--serializer', '-d', type=str, choices=list(serializer2class.keys()),
        help=f"Choose the serialization mechanism."
    )
    parser.add_argument(
        '--text_output',
        type=str,
        help="Output file if TextDriver was chosen",
        default=f"/tmp/fetch_agent.out.{os.getpid()}"
    )
    parser.add_argument('--debug', action='store_true', help='Set log level to DEBUG')

    args = parser.parse_args()

    kwargs = dict()  # TODO: remove this workaround
    kwargs['debug'] = args.debug
    if args.text_output:
        kwargs['path'] = args.text_output
    if args.save_driver:
        if len(args.save_driver) > 1:
            output_driver = MultipleSaveDriver(
                drivers=[driver2class[driver](**kwargs) for driver in args.save_driver],
                debug=args.debug
            )
        else:
            output_driver = driver2class[args.save_driver[0]](**kwargs)
    else:
        output_driver = driver2class['stdout'](**kwargs)
    if args.serializer:
        output_driver.serializer = serializer2class[args.serializer]

    fd = FetchDaemon(
        conf_path=args.config,
        output_driver=output_driver,
        interval=args.interval
    )
    fd.start()
