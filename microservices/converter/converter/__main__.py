import logging
import toml
import argparse
from .converter import Server
from common import *


# Set logger
logging.basicConfig(filename="converter.log",
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.INFO)


# Parsing arguments
parser = argparse.ArgumentParser()
parser.add_argument("--config")
args = parser.parse_args()


# Starting server
Server.start(load_configuration(MICROSERVICE_CONVERTER, toml.load(str(args.config))))
