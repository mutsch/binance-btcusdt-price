import json

from common.proto import test_task_pb2


class OrderBook:
    def __init__(self):
        self.bids = {}
        self.asks = {}

    def deserialize_from_binance_json(self, snapshot_json: json, time: int):
        self.time = time

        for ask in snapshot_json["asks"]:
            price, quantity = ask
            price = float(price)
            quantity = float(quantity)
            self.asks[price] = quantity

        for bid in snapshot_json["bids"]:
            price, quantity = bid
            price = float(price)
            quantity = float(quantity)
            self.bids[price] = quantity

    def serialize_to_json(self):
        return {
            "asks": self.asks,
            "bids": self.bids,
            "time": self.time,
        }

    @staticmethod
    def deserialize_from_proto(order_book: list, timestamp: int):
        result = OrderBook()
        result.time = timestamp
        for order in order_book:
            if order.type == test_task_pb2.Order.OrderType.ASK:
                result.asks[order.value] = order.quantity
            else:
                result.bids[order.value] = order.quantity
        return result

    def serialize_to_proto(self):
        order_book = []
        for ask in self.asks:
            order_book.append(test_task_pb2.Order(type=test_task_pb2.Order.OrderType.ASK,
                                                  value=ask,
                                                  quantity=self.asks[ask]))
        for bid in self.bids:
            order_book.append(test_task_pb2.Order(type=test_task_pb2.Order.OrderType.BID,
                                                  value=bid,
                                                  quantity=self.bids[bid]))
        return order_book
