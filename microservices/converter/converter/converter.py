import grpc
import logging
from concurrent import futures
from common import *


class Server:
    @staticmethod
    def start(conf: Configuration):
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=16))
        test_task_pb2_grpc.add_ConverterServicer_to_server(ConverterService(conf), server)
        server.add_insecure_port("[::]:" + conf.node_port)
        server.start()
        server.wait_for_termination()


class ConverterService(test_task_pb2_grpc.ConverterServicer):
    def __init__(self, conf: Configuration):
        self.configuration = conf

    def convert(self, ord_book: list):
        best_ask = 0
        best_bid = float("inf")
        for order in ord_book:
            if order.type == test_task_pb2.Order.OrderType.ASK:
                best_ask = max(best_ask, order.value)
            else:
                best_bid = min(best_bid, order.value)
        return (best_ask + best_bid) / 2

    def save(self, value: float, timestamp: int):
        response = False
        try:
            storer_conf = self.configuration.clusters[MICROSERVICE_STORER]
            with grpc.insecure_channel(f"{storer_conf.cluster_host}:{storer_conf.cluster_port}") as channel:
                stub = test_task_pb2_grpc.StorerStub(channel)
                request = test_task_pb2.SaveFairPriceRequest(price=value, timestamp=timestamp)
                response = stub.SaveFairPrice(request).is_success
        except grpc.RpcError as e:
            logging.info(f"Exception: {e}")
            return False
        return response

    def ConvertAndSave(self, request, context):
        logging.info("Convert and save called!")
        result = self.save(self.convert(request.order_book), request.timestamp)
        logging.info(f"Result: {str(result)}")
        return test_task_pb2.ConvertAndSaveResponse(is_success=result)
