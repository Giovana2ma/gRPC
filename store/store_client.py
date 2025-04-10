import os
import sys
import grpc
from concurrent import futures
sys.path.append(os.path.join(os.path.dirname(__file__), '../wallet'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../store'))


import store_pb2
import store_pb2_grpc
import wallet_pb2
import wallet_pb2_grpc

def get_price(store_stub):
    # Busca o valor do produto da loja
    
    try:
        price_response = store_stub.Price(store_pb2.PriceRequest())
        print(price_response.price)
        return price_response.price
    except grpc.RpcError as e:
        print(f"Failed to get price: {e.code()}: {e.details()}")
        return
    

def main():

    if len(sys.argv) != 4:
        print("Usage: store_client.py <account_id> <wallet_server_address> <store_server_address>")
        return

    account_id = sys.argv[1]
    wallet_server_address = sys.argv[2]
    store_server_address = sys.argv[3]

    # Conectar ao servidor de loja
    store_channel = grpc.insecure_channel(store_server_address)
    store_stub = store_pb2_grpc.StoreServiceStub(store_channel)

    # Conectar ao servidor de carteiras
    wallet_channel = grpc.insecure_channel(wallet_server_address)
    wallet_stub = wallet_pb2_grpc.WalletServiceStub(wallet_channel)

    price = get_price(store_stub)


    # Ler comandos da entrada padrão
    for line in sys.stdin:
        line = line.strip()
        if line.startswith("C"):
            try:
                # Executar RPC de emissão de ordem de pagamento
                response = wallet_stub.CreatePaymentOrder(wallet_pb2.CreatePaymentOrderRequest(wallet_id=account_id, amount=price))
                order_id = response.order_id
                if response.status < 0:
                    print(response.status)
                if response.status == 0:
                    print(order_id)
                    # Executar RPC de venda na loja
                    sale_response = store_stub.Sell(store_pb2.SellRequest(order_id = order_id))
                    print(sale_response.status)

            except grpc.RpcError as e:
                print(f"RPC failed: {e.code()}: {e.details()}")

        elif line.startswith("T"):
            try:
                # Encerrar o servidor da loja
                terminate_response = store_stub.Shutdown(store_pb2.ShutdownRequest())
                print(terminate_response.final_balance, terminate_response.remaining_orders)
                break
            except grpc.RpcError as e:
                print(f"RPC failed: {e.code()}: {e.details()}")
                break

        # Ignorar qualquer outro comando

if __name__ == "__main__":
    main()
