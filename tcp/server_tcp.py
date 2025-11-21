import socket
import threading
import json
import sys
import time

# --- Configurações da REDE ---
HOST = '0.0.0.0'  # CORRIGIDO: Aceita conexões externas (ESP32)
PORT = 5000       # CORRIGIDO: Porta padrão do trabalho
BUFFER_SIZE = 4096  # Aumentado para suportar benchmark
ENCODING = 'utf-8'

clientes_ativos = []  # Lista de dicionários: {'socket': socket, 'addr': addr, 'nome': nome}
clientes_lock = threading.Lock()


def log_conexao(addr):
    print(f"[CONEXÃO] {addr[0]}:{addr[1]}")

def log_desconexao(addr, nome="Cliente"):
    print(f"[DESCONEXÃO] {nome} ({addr[0]}:{addr[1]})")

def log_mensagem(addr, msg):
    print(f"[MSG] {addr[0]}:{addr[1]}: {msg.strip()}")


def broadcast(mensagem, remetente_socket=None):
    """Envia mensagem para todos os clientes, exceto o remetente"""
    with clientes_lock:
        for cliente in clientes_ativos:
            if cliente['socket'] != remetente_socket:
                try:
                    cliente['socket'].sendall(mensagem.encode(ENCODING))
                except Exception as e:
                    print(f"[ERRO] Não foi possível enviar para {cliente['nome']}: {e}")


def processar_mensagem(mensagem, cliente_info):
    """Processa comandos e mensagens especiais"""
    
    # Comando /nick
    if mensagem.startswith('/nick '):
        novo_nome = mensagem[6:].strip()
        if novo_nome:
            nome_antigo = cliente_info['nome']
            cliente_info['nome'] = novo_nome
            aviso = f">>> {nome_antigo} agora é {novo_nome}"
            broadcast(aviso, cliente_info['socket'])
            print(f"[NICK] {nome_antigo} → {novo_nome}")
        return True
    
    # Comando /sair
    if mensagem == '/sair':
        return 'sair'
    
    # Verifica se é JSON do ESP32
    if mensagem.startswith('{'):
        try:
            dados = json.loads(mensagem)
            if dados.get('type') == 'data' and dados.get('from') == 'esp32':
                payload = dados.get('payload', {})
                msg_formatada = f"[ESP32] Temp: {payload.get('temp')}°C, Umidade: {payload.get('hum')}%"
                broadcast(msg_formatada, cliente_info['socket'])
                print(f"[ESP32] {payload}")
                return True
        except json.JSONDecodeError:
            pass  # Não é JSON válido, trata como mensagem normal
    
    return False


def handle_client(conn, addr):
    """Gerencia cada cliente conectado"""
    log_conexao(addr)

    # Cria informações do cliente
    cliente_info = {
        'socket': conn,
        'addr': addr,
        'nome': f"Cliente_{addr[1]}"
    }

    # Adiciona à lista de clientes ativos
    with clientes_lock:
        clientes_ativos.append(cliente_info)
    
    # Notifica outros clientes
    broadcast(f">>> {cliente_info['nome']} entrou no chat", conn)

    try:
        while True:
            # Recebe dados
            dados = conn.recv(BUFFER_SIZE)
            if not dados:
                break
            
            mensagem = dados.decode(ENCODING)
            log_mensagem(addr, mensagem)
            
            # Processa comandos especiais
            resultado = processar_mensagem(mensagem, cliente_info)
            
            if resultado == 'sair':
                break
            elif resultado:
                continue  # Comando processado, não retransmitir
            
            # Mensagem normal - retransmite para todos
            if not mensagem.startswith('/'):
                # Se a mensagem já tem formato "Nome: mensagem", usa direto
                if ':' in mensagem and not mensagem.startswith('{'):
                    broadcast(mensagem, conn)
                else:
                    # Adiciona o nome do cliente
                    broadcast(f"{cliente_info['nome']}: {mensagem}", conn)
            
    except ConnectionResetError:
        pass
    except Exception as e:
        print(f"[ERRO] Cliente {addr}: {e}")
    finally:
        # Remove cliente da lista
        with clientes_lock:
            if cliente_info in clientes_ativos:
                clientes_ativos.remove(cliente_info)
        
        # Notifica desconexão
        broadcast(f">>> {cliente_info['nome']} saiu do chat")
        log_desconexao(addr, cliente_info['nome'])
        conn.close()


def main_server():
    """Função principal do servidor"""
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((HOST, PORT))
        server_socket.listen(5)
        
        print("=" * 60)
        print(f"Servidor TCP iniciado em {HOST}:{PORT}")
        print("Aguardando conexões...")
        print("=" * 60)

    except socket.error as e:
        print(f"[ERRO] Falha ao iniciar servidor: {e}")
        sys.exit(1)

    # Loop principal
    while True:
        try:
            conn, addr = server_socket.accept()
            thread_cliente = threading.Thread(target=handle_client, args=(conn, addr))
            thread_cliente.daemon = True
            thread_cliente.start()
            
            print(f"[INFO] Clientes conectados: {threading.active_count() - 1}")

        except KeyboardInterrupt:
            print("\n[INFO] Servidor encerrado pelo usuário")
            break
        except Exception as e:
            print(f"[ERRO] Ao aceitar conexão: {e}")
            time.sleep(1)
    
    server_socket.close()


if __name__ == '__main__':
    main_server()