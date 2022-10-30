import argparse
import logging

from sparrot.config import settings
from sparrot.logger import Logger, setup_logger
from sparrot.resolve import Resolver

logger = Logger()


def main():
    parser = argparse.ArgumentParser(
        description="""
                             _   
     ___ ___ ___ ___ ___ ___| |_ 
    |_ -| . | .'|  _|  _| . |  _|
    |___|  _|__,|_| |_| |___|_|  
        |_|                      
    """,
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument("domain")
    parser.add_argument("-k", "--api-key", default=None, help="Whoxy API key")

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_const",
        dest="loglevel",
        const=logging.INFO,
        default=logging.WARNING,
        help="enable verbose output",
    )

    parser.add_argument(
        "--debug",
        action="store_const",
        dest="loglevel",
        const=logging.DEBUG,
        help="enable debut output",
    )

    args = parser.parse_args(namespace=settings.args)
    setup_logger(settings.args.loglevel)
    logger.debug(settings.args)

    if not settings.api_key:
        logger.error("Missing API key, either set it in the config file or pass it on the command line.")
        return

    resolver = Resolver()
    resolver.resolve(args.domain)
    resolver.print()


if __name__ == "__main__":
    main()
