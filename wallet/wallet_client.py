import grpc
import wallet_pb2
import wallet_pb2_grpc
import sys

def run_client(wallet_id, server_address):
    channel = grpc.insecure_channel(server_address)
    stub = wallet_pb2_grpc.WalletServiceStub(channel)

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        
        parts = line.split()
        command = parts[0]

        if command == 'S':
            response = stub.ReadBalance(wallet_pb2.ReadBalanceRequest(wallet_id=wallet_id))
            print(response.balance)

        elif command == 'O':
            try:
                amount = int(parts[1])
            except (IndexError, ValueError):
                print("Uso incorreto do comando O.")
                continue
            
            response = stub.CreatePaymentOrder(wallet_pb2.CreatePaymentOrderRequest(wallet_id=wallet_id, amount=amount))
            if response.status ==0:
                print(response.order_id)
            else:
                print(response.status)

        elif command == 'X':
            try:
                order_id = int(parts[1])
                amount = int(parts[2])
                target_wallet_id = parts[3]
            except (IndexError, ValueError):
                print("Uso incorreto do comando X.")
                continue
            
            response = stub.Transfer(wallet_pb2.TransferRequest(order_id=order_id, amount=amount, wallet_id=target_wallet_id))
            print(response.status)

        elif command == 'F':
            response = stub.Shutdown(wallet_pb2.ShutdownRequest())
            print(response.remaining_orders)
            break  

        else:
            continue

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Uso: python wallet_client.py <id_carteira> <endereco_servidor>")
        sys.exit(1)

    wallet_id = sys.argv[1]
    server_address = sys.argv[2]

    run_client(wallet_id, server_address)
