import grpc
from concurrent import futures
import wallet_pb2
import wallet_pb2_grpc
import threading
import sys

class WalletService(wallet_pb2_grpc.WalletServiceServicer):

    def __init__(self, stop_event):
        self.wallets = {}
        self.orders = {}
        self.next_order_id = 1
        self._stop_event = stop_event  

    def ReadBalance(self, request, context):

        # Recebe como parâmetro um string. Caso a carteira indicada não exista, deve retornar -1, 
        # caso contrário retorna o valor associado à carteira.

        wallet_id = request.wallet_id
        balance = self.wallets.get(wallet_id, -1)
        return wallet_pb2.ReadBalanceResponse(balance=balance)

    def CreatePaymentOrder(self, request, context):

        # cria uma ordem de pagamento debitando o valor solicitado da carteira indicada; 
        # em caso de sucesso, retorna o inteiro identificador da ordem, 
        # se a carteira não existe, retorna -1; 
        # se o valor a ser debitado é maior que o saldo na carteira, retorna -2.

        wallet_id = request.wallet_id
        amount = request.amount

        if wallet_id not in self.wallets:
            return wallet_pb2.CreatePaymentOrderResponse(order_id=-1, status=-1)
        if self.wallets[wallet_id] < amount:
            return wallet_pb2.CreatePaymentOrderResponse(order_id=-1, status=-2)

        order_id = self.next_order_id
        self.next_order_id += 1
        self.wallets[wallet_id] -= amount
        self.orders[order_id] = amount
        return wallet_pb2.CreatePaymentOrderResponse(order_id=order_id, status=0)

    def Transfer(self, request, context):
        # Remover a ordem de pagamento indicada e fazer a transferência do valor associado para a carteira identificada (string), 
        # sendo que, como controle, verifica primeiro se a ordem possui o valor fornecido para conferência; 
        # em caso de sucesso retorna 0;
        # se a ordem de pagamento não existe, retorna -1; 
        # se o valor da ordem difere do valor de conferência, retorna -2; 
        # se a string não corresponde a uma carteira existente, retorna -3.


        order_id = request.order_id
        amount = request.amount
        target_wallet_id = request.wallet_id

        if order_id not in self.orders:
            return wallet_pb2.TransferResponse(status=-1)
        if self.orders[order_id] != amount:
            return wallet_pb2.TransferResponse(status=-2)
        if target_wallet_id not in self.wallets:
            return wallet_pb2.TransferResponse(status=-3)

        self.wallets[target_wallet_id] += amount
        del self.orders[order_id]
        return wallet_pb2.TransferResponse(status=0)

    def Shutdown(self, request, context):
        # Comanda o servidor para terminar sua execução; 
        # o servidor escreve na saída padrão os valores atualizados das carteiras existentes (mesmo que sejam zero)
        # retorna o número de ordens de pagamento ainda existentes (que serão perdidas nesse caso) 
        # termina sua execução depois da resposta

        remaining_orders = len(self.orders)

        for wallet_id, balance in self.wallets.items():
            print(wallet_id,balance)

        self._stop_event.set()

        return wallet_pb2.ShutdownResponse(remaining_orders=remaining_orders)
    
def read_wallets(service):
    # Ler a entrada padrão para carregar carteiras
    for line in sys.stdin:
        parts = line.strip().split()
        if len(parts) == 2:
            wallet_id, balance_str = parts
            service.wallets[wallet_id] = int(balance_str)

def serve():
    stop_event = threading.Event()

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    service = WalletService(stop_event)
    wallet_pb2_grpc.add_WalletServiceServicer_to_server(service, server)

    port = int(sys.argv[1])
    server.add_insecure_port(f'0.0.0.0:{port}')
    server.start()

    # Iniciar a leitura de carteiras em uma thread separada
    threading.Thread(target=read_wallets, args=(service,), daemon=True).start()

    stop_event.wait()

    server.stop(0)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Uso: python wallet_server.py <porta>")
        sys.exit(1)
    serve()

