import socket
import threading
import sys
import time

# --- Configurações da REDE ---
HOST = '127.0.0.1'  # Servidor rodando localmente. Tem que trocar pra 0.0.0.0
PORT = 6767
BUFFER_SIZE = 1024
ENCODING = 'utf-8'

clientes_ativos = []
clientes_lock = threading.Lock()


def log_conexao(addr):
    print(f"Conexão estabelecida com: {addr[0]}:{addr[1]}")

def log_desconexao(addr):
    print(f"Cliente {addr[0]}:{addr[1]} desconectado.")

def log_mensagem(addr, msg):
    print(f"MENSAGEM De {addr[0]}:{addr[1]}: {msg.strip()}")

# ----

def retransmitir_mensagem(remetente_socket, mensagem_bytes, remetente_addr):
  
    with clientes_lock:
        msg_cabecalho_remetente = f"[{remetente_addr[1]}] {mensagem_bytes.decode(ENCODING)}".encode(ENCODING)
        
        # Itera sobre a lista de clientes ativos
        for cliente_socket in clientes_ativos:
            if cliente_socket != remetente_socket:
                try:
                    # Envia a mensagem com o prefixo
                    cliente_socket.sendall(msg_cabecalho_remetente)
                except Exception as e:
                    print(f"Não foi possível enviar para um cliente: {e}")
              

# --- Função de Gerenciamento de Cliente 

def handle_client(conn, addr):
    log_conexao(addr)

    # 1. Adiciona o novo cliente à lista de ativos
    with clientes_lock:
        clientes_ativos.append(conn)

    try:
        # Loop principal para receber dados do cliente
        while True:
            # Recebe os dados
            dados = conn.recv(BUFFER_SIZE)
            if not dados:
                break
            mensagem_str = dados.decode(ENCODING)
            log_mensagem(addr, mensagem_str)
            retransmitir_mensagem(conn, dados, addr)
            
    except ConnectionResetError:
        # Cliente fechou a conexão
        pass
    except Exception as e:
        print(f"Ocorreu um erro com o cliente {addr}: {e}")
    finally:
        # remove o cliente da lista e fecha o socket
        with clientes_lock:
            if conn in clientes_ativos:
                clientes_ativos.remove(conn)
        
        # Fecha a conexão do socket
        conn.close()
        log_desconexao(addr)

def main_server():
    
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # Permite que o socket seja reutilizado        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # bind do socket ao endereço e porta
        server_socket.bind((HOST, PORT))
        
        #escuta para novas conexões 
        server_socket.listen(5)
        print(f" server Escutando em {HOST}:{PORT}")

    except socket.error as e:
        print(f"Falha ao iniciar o servidor: {e}")
        sys.exit(1)

    # Loop para aceitar novas conexões
    while True:
        try:
            conn, addr = server_socket.accept()
            thread_cliente = threading.Thread(target=handle_client, args=(conn, addr))
            thread_cliente.start()
            
            # Mostra o número de threads ativas (clientes + principal)
            print(f"THREADS ATIVAS, {threading.active_count() - 1} clientes conectados.")

        except KeyboardInterrupt:
            print("\n Servidor encerrado pelo usuário.")
            break
        except Exception as e:
            print(f"Ocorreu um erro ao aceitar a conexão: {e}")
            time.sleep(1) 

    
    server_socket.close()

#--------------------------------------

if __name__ == '__main__':
    main_server()