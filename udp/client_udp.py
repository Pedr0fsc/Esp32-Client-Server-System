import socket
import threading
import time

# configurações do servidor
SERVER_HOST = '127.0.0.1'
SERVER_PORT = 5001

# variavel para o nome do usuario
nome_usuario = "Usuario"

def receber_mensagens(sock):
    """Função que fica recebendo mensagens do servidor"""
    while True:
        try:
            # recebe mensagem do servidor
            mensagem, endereco = sock.recvfrom(4096)
            print(mensagem.decode('utf-8'))
        except:
            # se der erro, provavelmente o socket foi fechado
            break

def enviar_benchmark(sock, tamanho_bytes):
    """Envia dados grandes para teste de desempenho"""
    print(f"\n[BENCHMARK] Enviando {tamanho_bytes} bytes via UDP...")
    
    # cria os dados para enviar
    dados = "X" * tamanho_bytes
    
    # marca o tempo de inicio
    tempo_inicio = time.time()
    
    # envia os dados
    sock.sendto(dados.encode('utf-8'), (SERVER_HOST, SERVER_PORT))
    
    # calcula tempo total
    tempo_total = time.time() - tempo_inicio
    
    print(f"[BENCHMARK] Tempo total: {tempo_total:.4f} segundos")
    print(f"[BENCHMARK] Taxa de transferência: {(tamanho_bytes / tempo_total / 1024 / 1024):.2f} MB/s")

def main():
    global nome_usuario
    
    # cria o socket UDP
    cliente_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    print("=" * 50)
    print("Cliente UDP - Conectividade de Sistemas")
    print("=" * 50)
    
    # envia primeira mensagem para o servidor saber que existe
    mensagem_inicial = f"{nome_usuario} entrou no chat"
    cliente_socket.sendto(mensagem_inicial.encode('utf-8'), (SERVER_HOST, SERVER_PORT))
    
    # inicia thread para receber mensagens
    thread_receber = threading.Thread(target=receber_mensagens, args=(cliente_socket,))
    thread_receber.daemon = True
    thread_receber.start()
    
    print("\nComandos disponíveis:")
    print("  /nick <nome> - Alterar seu nome")
    print("  /bench <bytes> - Teste de desempenho")
    print("  /sair - Sair do chat\n")
    
    # loop principal para enviar mensagens
    while True:
        try:
            mensagem = input()
            
            # verifica se é um comando
            if mensagem.startswith('/nick '):
                # muda o nome do usuario
                novo_nome = mensagem.split(' ', 1)[1]
                nome_anterior = nome_usuario
                nome_usuario = novo_nome
                aviso = f"{nome_anterior} mudou o nome para {nome_usuario}"
                cliente_socket.sendto(aviso.encode('utf-8'), (SERVER_HOST, SERVER_PORT))
                print(f"Nome alterado para: {nome_usuario}")
                
            elif mensagem.startswith('/bench '):
                # executa benchmark
                try:
                    tamanho = int(mensagem.split(' ')[1])
                    enviar_benchmark(cliente_socket, tamanho)
                except:
                    print("Erro: use /bench <numero_de_bytes>")
                    
            elif mensagem == '/sair':
                # sai do chat
                mensagem_saida = f"{nome_usuario} saiu do chat"
                cliente_socket.sendto(mensagem_saida.encode('utf-8'), (SERVER_HOST, SERVER_PORT))
                print("Desconectando...")
                break
                
            else:
                # envia mensagem normal
                mensagem_completa = f"{nome_usuario}: {mensagem}"
                cliente_socket.sendto(mensagem_completa.encode('utf-8'), (SERVER_HOST, SERVER_PORT))
                
        except KeyboardInterrupt:
            # se apertar Ctrl+C
            print("\n\nDesconectando...")
            mensagem_saida = f"{nome_usuario} saiu do chat"
            cliente_socket.sendto(mensagem_saida.encode('utf-8'), (SERVER_HOST, SERVER_PORT))
            break
    
    # fecha o socket
    cliente_socket.close()
    print("Conexão encerrada.")

if __name__ == "__main__":
    main()