import os
import sys
import grpc
from concurrent import futures
import threading
sys.path.append(os.path.join(os.path.dirname(__file__), '../wallet'))

import store_pb2
import store_pb2_grpc
import wallet_pb2
import wallet_pb2_grpc

class StoreService(store_pb2_grpc.StoreServiceServicer):
    def __init__(self, price, port, seller_account, wallet_server,stop_event):
        self.price = price
        self.port = port
        self.seller_account = seller_account
        self.wallet_server = wallet_server
        self.seller_balance = 0
        self.orders = {}
        self.channel = grpc.insecure_channel(self.wallet_server)
        self.wallet_stub = wallet_pb2_grpc.WalletServiceStub(self.channel)
        self._initialize_seller_balance()
        self._stop_event = stop_event  

    def _initialize_seller_balance(self):
        # Busca o saldo inicial

        response = self.wallet_stub.ReadBalance(wallet_pb2.ReadBalanceRequest(wallet_id=self.seller_account))
        self.seller_balance = response.balance

    def Price(self, request, context):
        return store_pb2.PriceResponse(price=self.price)

    def Sell(self, request, context):
        order_id = request.order_id
        try:
            response = self.wallet_stub.Transfer(wallet_pb2.TransferRequest(order_id=order_id, amount=self.price, wallet_id=self.seller_account))
            status = response.status
            if status == 0:
                self.seller_balance += self.price
            return store_pb2.SellResponse(status=status)
        except grpc.RpcError:
            return store_pb2.SellResponse(status=-9)  # RPC error

    def Shutdown(self, request, context):
        shutdown_request = wallet_pb2.ShutdownRequest()
        try:
            response = self.wallet_stub.Shutdown(shutdown_request)
            final_balance = self.seller_balance
            remaining_orders = response.remaining_orders
            self._stop_event.set()
            return store_pb2.ShutdownResponse(final_balance=final_balance, remaining_orders=remaining_orders)
        except grpc.RpcError:
            self._stop_event.set()
            return store_pb2.ShutdownResponse(final_balance=self.seller_balance, remaining_orders=-9)

def serve():
    stop_event = threading.Event()

    if len(sys.argv) != 5:
        print("Usage: store_server.py <price> <port> <seller_account> <wallet_server>")
        return
    price = int(sys.argv[1])
    port = int(sys.argv[2])
    seller_account = sys.argv[3]
    wallet_server = sys.argv[4]

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    store_pb2_grpc.add_StoreServiceServicer_to_server(StoreService(price, port, seller_account, wallet_server,stop_event), server)
    server.add_insecure_port(f'0.0.0.0:{port}')
    server.start()
    stop_event.wait()

    server.stop(0)

if __name__ == '__main__':
    serve()
