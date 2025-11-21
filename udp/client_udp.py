import socket
import threading
import time

# Configurações do servidor UDP
SERVER_HOST = '127.0.0.1'  # localhost ou IP do servidor
SERVER_PORT = 5001          # Porta UDP (diferente do TCP que usa 5000)

# Variável para o nome do usuário
nome_usuario = "Usuario"

def receber_mensagens(sock):
    """Thread que fica recebendo mensagens do servidor"""
    while True:
        try:
            # Recebe mensagem do servidor
            mensagem, endereco = sock.recvfrom(65536)  # Buffer grande para benchmark
            print(mensagem.decode('utf-8'))
        except:
            # Se der erro, provavelmente o socket foi fechado
            break

def enviar_benchmark(sock, tamanho_bytes):
    """Envia dados grandes para teste de desempenho UDP"""
    print(f"\n[BENCHMARK UDP] Enviando {tamanho_bytes} bytes...")
    
    # Cria os dados para enviar
    dados = "X" * tamanho_bytes
    
    # Marca o tempo de início
    tempo_inicio = time.time()
    
    try:
        # UDP pode ter limite de tamanho por pacote
        # Vamos enviar em chunks se for muito grande
        CHUNK_SIZE = 65000  # Tamanho máximo seguro para UDP
        enviados = 0
        
        while enviados < tamanho_bytes:
            chunk = dados[enviados:enviados + CHUNK_SIZE]
            sock.sendto(chunk.encode('utf-8'), (SERVER_HOST, SERVER_PORT))
            enviados += len(chunk)
        
        # Calcula tempo total
        tempo_total = time.time() - tempo_inicio
        
        print(f"[BENCHMARK UDP] ✓ Concluído!")
        print(f"[BENCHMARK UDP] Tempo total: {tempo_total:.4f} segundos")
        print(f"[BENCHMARK UDP] Velocidade: {(tamanho_bytes / tempo_total / 1024 / 1024):.2f} MB/s")
        print()
        
    except Exception as e:
        print(f"[BENCHMARK UDP] ✗ Erro: {e}")

def main():
    global nome_usuario
    
    # Cria o socket UDP
    cliente_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    print("=" * 50)
    print("Cliente UDP - Chat com Benchmark")
    print("=" * 50)
    print()
    
    # Envia primeira mensagem para o servidor saber que existe
    mensagem_inicial = f"{nome_usuario} entrou no chat"
    cliente_socket.sendto(mensagem_inicial.encode('utf-8'), (SERVER_HOST, SERVER_PORT))
    
    # Inicia thread para receber mensagens
    thread_receber = threading.Thread(target=receber_mensagens, args=(cliente_socket,))
    thread_receber.daemon = True
    thread_receber.start()
    
    print("Comandos disponíveis:")
    print("  /nick <nome>    - Alterar seu nome")
    print("  /bench <bytes>  - Teste de desempenho")
    print("  /sair           - Sair do chat")
    print()
    
    # Loop principal para enviar mensagens
    while True:
        try:
            mensagem = input()
            
            # Comando /nick
            if mensagem.startswith('/nick '):
                novo_nome = mensagem.split(' ', 1)[1].strip()
                if novo_nome:
                    nome_anterior = nome_usuario
                    nome_usuario = novo_nome
                    aviso = f"{nome_anterior} mudou o nome para {nome_usuario}"
                    cliente_socket.sendto(aviso.encode('utf-8'), (SERVER_HOST, SERVER_PORT))
                    print(f"Nome alterado para: {nome_usuario}")
                else:
                    print("Uso: /nick <nome>")
            
            # Comando /bench
            elif mensagem.startswith('/bench '):
                try:
                    tamanho = int(mensagem.split()[1])
                    if tamanho <= 0:
                        print("[ERRO] Tamanho deve ser maior que zero")
                    else:
                        enviar_benchmark(cliente_socket, tamanho)
                except (IndexError, ValueError):
                    print("[ERRO] Uso: /bench <numero_de_bytes>")
                    print("Exemplos:")
                    print("  /bench 1000000      (1 MB)")
                    print("  /bench 10000000     (10 MB)")
            
            # Comando /sair
            elif mensagem == '/sair':
                mensagem_saida = f"{nome_usuario} saiu do chat"
                cliente_socket.sendto(mensagem_saida.encode('utf-8'), (SERVER_HOST, SERVER_PORT))
                print("Desconectando...")
                break
            
            # Mensagem normal
            else:
                mensagem_completa = f"{nome_usuario}: {mensagem}"
                cliente_socket.sendto(mensagem_completa.encode('utf-8'), (SERVER_HOST, SERVER_PORT))
                
        except KeyboardInterrupt:
            # Se apertar Ctrl+C
            print("\n\nDesconectando...")
            mensagem_saida = f"{nome_usuario} saiu do chat"
            cliente_socket.sendto(mensagem_saida.encode('utf-8'), (SERVER_HOST, SERVER_PORT))
            break
    
    # Fecha o socket
    cliente_socket.close()
    print("Conexão encerrada.")

if __name__ == "__main__":
    main()