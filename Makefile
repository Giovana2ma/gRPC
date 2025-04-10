# Diretórios dos arquivos proto
WALLET_DIR = wallet
STORE_DIR = store

# Arquivos proto e stubs
WALLET_PROTO = $(WALLET_DIR)/wallet.proto
STORE_PROTO = $(STORE_DIR)/store.proto

WALLET_STUBS = $(WALLET_DIR)/wallet_pb2.py $(WALLET_DIR)/wallet_pb2_grpc.py
STORE_STUBS = $(STORE_DIR)/store_pb2.py $(STORE_DIR)/store_pb2_grpc.py

# Variáveis para comandos
PYTHON = python3
GRPC_TOOLS = grpc_tools.protoc

# Comandos de limpeza
clean:
	rm -f $(WALLET_STUBS) $(STORE_STUBS)

# Comandos para gerar os stubs
stubs: wallet_stubs store_stubs

wallet_stubs: $(WALLET_STUBS)

$(WALLET_STUBS): $(WALLET_PROTO)
	$(PYTHON) -m $(GRPC_TOOLS) -I$(WALLET_DIR) --python_out=$(WALLET_DIR) --grpc_python_out=$(WALLET_DIR) $(WALLET_PROTO)

store_stubs: $(STORE_STUBS)

$(STORE_STUBS): $(STORE_PROTO)
	$(PYTHON) -m $(GRPC_TOOLS) -I$(STORE_DIR) --python_out=$(STORE_DIR) --grpc_python_out=$(STORE_DIR) $(STORE_PROTO)

# Comando para executar o servidor de carteiras
run_serv_banco: wallet_stubs
	$(PYTHON) $(WALLET_DIR)/wallet_server.py $(arg1)

# Comando para executar o cliente de carteiras
run_cli_banco: wallet_stubs
	$(PYTHON) $(WALLET_DIR)/wallet_client.py $(arg1) $(arg2)

# Comando para executar o servidor da loja
run_serv_loja: store_stubs
	$(PYTHON) $(STORE_DIR)/store_server.py $(arg1) $(arg2) $(arg3) $(arg4)

# Comando para executar o cliente da loja
run_cli_loja: store_stubs
	$(PYTHON) $(STORE_DIR)/store_client.py $(arg1) $(arg2) $(arg3) 
