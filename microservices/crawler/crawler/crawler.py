import logging
import grpc
import requests
from collections import deque
from common import *
from time import time, sleep


BINANCE_SNAPSHOT_URL = "https://api.binance.com/api/v3/depth?symbol=BTCUSDT&limit=100"


class Crawler:
    def __init__(self, conf: Configuration):
        self.configuration = conf
        self.buffer = deque()
        self.snapshot = OrderBook()
        self.isSnapshotLoaded = False

    def start(self):
        while True:
            response = requests.get(BINANCE_SNAPSHOT_URL)
            self.snapshot = OrderBook()
            self.snapshot.deserializeFromBinanceJson(response.json(), int(time()))
            self.save()
            sleep(1)

    def save(self):
        ord_book = self.snapshot.serializeToProto()
        timestamp = self.snapshot.time
        result = self.saveFairPrice(ord_book, timestamp)
        logging.info("Result: " + str(result))
        result = self.saveOrderBook(ord_book, timestamp)
        logging.info("Result: " + str(result))

    def saveFairPrice(self, ord_book: list, timestamp: int):
        logging.info("Save fair price!")
        response = False
        try:
            converter_conf = self.configuration.clusters[MICROSERVICE_CONVERTER]
            with grpc.insecure_channel(converter_conf.cluster_host + ":" + converter_conf.cluster_port) as channel:
                stub = test_task_pb2_grpc.ConverterStub(channel)
                request = test_task_pb2.ConvertAndSaveRequest(order_book=ord_book, timestamp=timestamp)
                response = stub.ConvertAndSave(request).is_success
        except grpc.RpcError as e:
            logging.info("Exception: " + str(e))
            return False
        return response

    def saveOrderBook(self, ord_book: list, timestamp: int):
        logging.info("Save order book!")
        response = False
        try:
            storer_conf = self.configuration.clusters[MICROSERVICE_STORER]
            with grpc.insecure_channel(storer_conf.cluster_host + ":" + storer_conf.cluster_port) as channel:
                stub = test_task_pb2_grpc.StorerStub(channel)
                request = test_task_pb2.SaveOrderBookRequest(order_book=ord_book, timestamp=timestamp)
                response = stub.SaveOrderBook(request).is_success
        except grpc.RpcError as e:
            logging.info("Exception: " + str(e))
            return False
        return response
