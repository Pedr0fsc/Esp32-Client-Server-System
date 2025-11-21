import socket
import threading
import sys

socket_cliente = None
conectado = False
UsuarioNome = "Nenhum"


def conexao(host, porta):
    global socket_cliente, conectado

    try:
        socket_cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_cliente.connect((host, porta))
        conectado = True

        print(f"Conectado ao servidor {host}:{porta}")
        print("Use /nick <nome> para escolher seu nome")
        print("Use /sair para sair\n")

        return True

    except Exception as e:
        print(f"Erro ao conectar: {e}")
        return False


def receber_mensagens():
    global socket_cliente, conectado, UsuarioNome

    while conectado:
        try:
            mensagem = socket_cliente.recv(1024).decode("utf-8")

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


def processar_comando(mensagem):
    global UsuarioNome, conectado, socket_cliente

    if mensagem.startswith("/nick "):
        novo_nome = mensagem[6:].strip()

        if novo_nome:
            UsuarioNome = novo_nome
            socket_cliente.send(mensagem.encode("utf-8"))
            print(f"Nome alterado para {UsuarioNome}")
        else:
            print("Uso correto: /nick ")

        return True

    if mensagem == "/sair":
        print("Encerrando conexão...")
        conectado = False
        socket_cliente.send(mensagem.encode("utf-8"))
        return True

    return False


def enviar_mensagens():
    global socket_cliente, conectado, UsuarioNome

    while conectado:
        try:
            mensagem = input(f"[{UsuarioNome}] ")

            if not mensagem:
                continue

            if mensagem.startswith("/"):
                if processar_comando(mensagem):
                    if mensagem == "/sair":
                        break
                    continue

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

    print("Desconectado...")


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
    print("\nCliente TCP de Chat\n")

    host = input("Host (Enter = localhost): ").strip() #é preciso mudar na parte da porta o numero pelo valor escolhido do servidor
    if not host:
        host = "localhost"

    porta = input("Porta: ").strip()
    if not porta:
        porta = 5000
    else:
        porta = int(porta)

    print()
    iniciar_cliente(host, porta)


if __name__ == "__main__":
    main()
