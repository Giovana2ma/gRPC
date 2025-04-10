# Digital Wallet & Store System with gRPC

This project implements a digital wallet and store system using **gRPC**, simulating a lightweight microservices architecture. The system is composed of two independent services that communicate through remote procedure calls (RPC):

- **Wallet Service**: Manages user accounts and balances, handles payment authorization.
- **Store Service**: Processes purchase requests by interacting with the wallet service to validate and complete transactions.

## Technologies

- Python 3
- gRPC & Protocol Buffers
- Multithreading (for concurrent request handling)

## Getting Started

Each service runs independently and communicates over configurable ports. To run the system:

make run_cli_banco arg1=carteira_cliente arg2=nome_do_host_do_serv_banco:5555
make run_serv_banco arg1=5555
make run_serv_loja arg1=10 arg2=6666 arg3=carteira_loja arg4=nome_do_host_do_serv_banco:5555
make run_cli_loja arg1=carteira_cliente arg2=nome_do_host_do_serv_banco:5555 arg3=nome_do_host_do_serv_loja:6666
