import socket

class UDPServer:
    def __init__(self, host="0.0.0.0", port=5005, buffer_size=1024):
        self.host = host
        self.port = port
        self.buffer_size = buffer_size

        # cria o socket udp
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def start(self):
        # inicia o servidor e começa a escutar
        self.socket.bind((self.host, self.port))
        print(f"Servidor UDP iniciado em {self.host}:{self.port}")

        while True:
            data, addr = self.socket.recvfrom(self.buffer_size)
            self.on_message(data, addr)

    def on_message(self, data, addr):
        # trata as mensagens recebidas
        mensagem = data.decode()
        print(f"Recebido de {addr}: {mensagem}")

        resposta = f"ACK: Recebi '{mensagem}'"
        self.send(resposta, addr)

    def send(self, message, addr):
        # envia a resposta para o cliente
        self.socket.sendto(message.encode(), addr)

if __name__ == "__main__":
    server = UDPServer(port=5005)
    server.start()
