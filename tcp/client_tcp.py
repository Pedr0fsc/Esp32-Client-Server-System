import socket
import threading
import sys
import time

socket_cliente = None
conectado = False
UsuarioNome = "Usuario"


def conexao(host, porta):
    global socket_cliente, conectado

    try:
        socket_cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_cliente.connect((host, porta))
        conectado = True

        print(f"Conectado ao servidor {host}:{porta}")
        print("\nComandos disponíveis:")
        print("  /nick <nome>    - Alterar seu nome")
        print("  /bench <bytes>  - Teste de performance")
        print("  /sair           - Desconectar")
        print("\n")

        return True

    except Exception as e:
        print(f"Erro ao conectar: {e}")
        return False


def receber_mensagens():
    global socket_cliente, conectado, UsuarioNome

    while conectado:
        try:
            mensagem = socket_cliente.recv(4096).decode("utf-8")

            if mensagem:
                print(f"\r{mensagem}")
                print(f"[{UsuarioNome}] ", end="", flush=True)
            else:
                print("\nConexão encerrada pelo servidor")
                conectado = False
                break

        except Exception as e:
            if conectado:
                print(f"\nErro ao receber mensagem: {e}")
            break


def enviar_benchmark(tamanho_bytes):
    """Envia grande volume de dados para teste de performance"""
    global socket_cliente
    
    print(f"\n[BENCHMARK TCP] Enviando {tamanho_bytes} bytes...")
    
    # Cria dados para enviar
    dados = "X" * tamanho_bytes
    
    # Marca tempo inicial
    tempo_inicio = time.time()
    
    # Envia em chunks para não estourar buffer
    CHUNK_SIZE = 4096
    enviados = 0
    
    try:
        while enviados < tamanho_bytes:
            chunk = dados[enviados:enviados + CHUNK_SIZE]
            socket_cliente.send(chunk.encode('utf-8'))
            enviados += len(chunk)
        
        # Calcula tempo total
        tempo_total = time.time() - tempo_inicio
        
        print(f"[BENCHMARK TCP] ✓ Concluído!")
        print(f"[BENCHMARK TCP] Tempo total: {tempo_total:.4f} segundos")
        print(f"[BENCHMARK TCP] Velocidade: {(tamanho_bytes / tempo_total / 1024 / 1024):.2f} MB/s")
        print()
        
    except Exception as e:
        print(f"[BENCHMARK TCP] ✗ Erro: {e}")


def processar_comando(mensagem):
    global UsuarioNome, conectado, socket_cliente

    # Comando /nick
    if mensagem.startswith("/nick "):
        novo_nome = mensagem[6:].strip()

        if novo_nome:
            UsuarioNome = novo_nome
            socket_cliente.send(mensagem.encode("utf-8"))
            print(f"Nome alterado para: {UsuarioNome}")
        else:
            print("Uso: /nick <nome>")

        return True

    # Comando /sair
    if mensagem == "/sair":
        print("Encerrando conexão...")
        conectado = False
        socket_cliente.send(mensagem.encode("utf-8"))
        return True
    
    # Comando /bench
    if mensagem.startswith("/bench "):
        try:
            partes = mensagem.split()
            if len(partes) < 2:
                raise ValueError
            
            tamanho = int(partes[1])
            
            if tamanho <= 0:
                print("[ERRO] Tamanho deve ser maior que zero")
                return True
            
            enviar_benchmark(tamanho)
            
        except ValueError:
            print("[ERRO] Uso: /bench <numero_de_bytes>")
            print("Exemplos:")
            print("  /bench 1000000      (1 MB)")
            print("  /bench 10000000     (10 MB)")
            print("  /bench 100000000    (100 MB)")
        
        return True

    return False


def enviar_mensagens():
    global socket_cliente, conectado, UsuarioNome

    while conectado:
        try:
            mensagem = input(f"[{UsuarioNome}] ")

            if not mensagem:
                continue

            # Verifica se é comando
            if mensagem.startswith("/"):
                if processar_comando(mensagem):
                    if mensagem == "/sair":
                        break
                    continue

            # Mensagem normal
            mensagem_completa = f"{UsuarioNome}: {mensagem}"
            socket_cliente.send(mensagem_completa.encode("utf-8"))

        except Exception as e:
            if conectado:
                print(f"\nErro ao enviar mensagem: {e}")
            break


def desconectar():
    global conectado, socket_cliente
    conectado = False

    if socket_cliente:
        try:
            socket_cliente.close()
        except:
            pass

    print("Desconectado.")


def iniciar_cliente(host, porta):
    if not conexao(host, porta):
        return

    thread_receber = threading.Thread(target=receber_mensagens, daemon=True)
    thread_receber.start()

    try:
        enviar_mensagens()
    except KeyboardInterrupt:
        print("\nInterrompido pelo usuário.")
    finally:
        desconectar()


def main():
    print("=" * 50)
    print("Cliente TCP - Chat com Benchmark")
    print("=" * 50)
    print()

    host = input("Host (Enter = localhost): ").strip()
    if not host:
        host = "localhost"

    porta = input("Porta (Enter = 5000): ").strip()
    if not porta:
        porta = 5000
    else:
        try:
            porta = int(porta)
        except ValueError:
            print("Porta inválida! Usando 5000.")
            porta = 5000

    print()
    iniciar_cliente(host, porta)


if __name__ == "__main__":
    main()