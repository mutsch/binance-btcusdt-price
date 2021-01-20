import logging
import toml
import argparse
from .crawler import Crawler
from common import *


# Set logger
logging.basicConfig(filename="crawler.log",
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.INFO)


# Parsing arguments
parser = argparse.ArgumentParser()
parser.add_argument("--config")
args = parser.parse_args()


# Starting crawler
crawler = Crawler(load_configuration(MICROSERVICE_CRAWLER, toml.load(str(args.config))))
crawler.start()
