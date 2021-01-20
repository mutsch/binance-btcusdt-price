import logging
import grpc
from datetime import *
from concurrent import futures
from common import *
from influxdb import *


INFLUX_DB_NAME = "test_task_db"

FAIR_PRICE_MEASUREMENT = "fair_price"
ORDER_BOOK_MEASUREMENT = "order_book"


class Server:
    @staticmethod
    def start(conf: Configuration):
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=16))
        test_task_pb2_grpc.add_StorerServicer_to_server(StorerService(conf), server)
        server.add_insecure_port("[::]:" + conf.node_port)
        server.start()
        server.wait_for_termination()


class StorerService(test_task_pb2_grpc.ConverterServicer):
    def __init__(self, conf: Configuration):
        self.configuration = conf
        self.connectToDB()

    def connectToDB(self):
        influx_conf = self.configuration.clusters[DB_INFLUX]
        self.db_client = InfluxDBClient(host=influx_conf.cluster_host, port=influx_conf.cluster_port)
        self.db_client.create_database(INFLUX_DB_NAME)
        self.db_client.switch_database(INFLUX_DB_NAME)

    def SaveOrderBook(self, request, context):
        order_book = OrderBook.deserializeFromProto(request.order_book, request.timestamp)
        order_book_str = json.dumps(order_book.serializeToJson())
        json_body = [{
            "measurement": ORDER_BOOK_MEASUREMENT,
            "time": datetime.fromtimestamp(request.timestamp).strftime("%Y-%m-%dT%H:%M:%S"),
            "fields": {
                "order_book": order_book_str
            }
        }]
        result = self.db_client.write_points(json_body)
        return test_task_pb2.SaveOrderBookResponse(is_success=result)

    def SaveFairPrice(self, request, context):
        json_body = [{
            "measurement": FAIR_PRICE_MEASUREMENT,
            "time": datetime.fromtimestamp(request.timestamp).strftime("%Y-%m-%dT%H:%M:%S"),
            "fields": {
                "price": request.price
            }
        }]
        result = self.db_client.write_points(json_body)
        return test_task_pb2.SaveFairPriceResponse(is_success=result)
