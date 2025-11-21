import socket
import threading

class UDPServer:
    def __init__(self, host="0.0.0.0", port=5001, buffer_size=65536):
        self.host = host
        self.port = port
        self.buffer_size = buffer_size
        
        # Lista para guardar endereços dos clientes conectados
        self.clientes = []  # Lista de tuplas (ip, porta)
        self.clientes_lock = threading.Lock()
        
        # Dicionário para mapear endereço → nome
        self.nomes_clientes = {}  # {(ip, porta): "nome"}
        
        # Cria o socket UDP
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
    def adicionar_cliente(self, addr):
        """Adiciona cliente à lista se não existir"""
        with self.clientes_lock:
            if addr not in self.clientes:
                self.clientes.append(addr)
                print(f"[+] Novo cliente: {addr[0]}:{addr[1]} | Total: {len(self.clientes)}")
    
    def remover_cliente(self, addr):
        """Remove cliente da lista"""
        with self.clientes_lock:
            if addr in self.clientes:
                self.clientes.remove(addr)
                nome = self.nomes_clientes.get(addr, "Desconhecido")
                print(f"[-] Cliente saiu: {nome} ({addr[0]}:{addr[1]}) | Total: {len(self.clientes)}")
                
                # Remove do dicionário de nomes
                if addr in self.nomes_clientes:
                    del self.nomes_clientes[addr]
    
    def broadcast(self, mensagem, remetente_addr=None):
        """Envia mensagem para TODOS os clientes, exceto o remetente"""
        with self.clientes_lock:
            for cliente_addr in self.clientes:
                # Não envia de volta para quem enviou
                if cliente_addr != remetente_addr:
                    try:
                        self.socket.sendto(mensagem.encode('utf-8'), cliente_addr)
                    except Exception as e:
                        print(f"[!] Erro ao enviar para {cliente_addr}: {e}")

    def start(self):
        """Inicia o servidor e começa a escutar"""
        try:
            self.socket.bind((self.host, self.port))
            print("=" * 60)
            print(f"Servidor UDP iniciado em {self.host}:{self.port}")
            print("Aguardando mensagens...")
            print("=" * 60)
            print()
        except Exception as e:
            print(f"[!] Erro ao iniciar servidor: {e}")
            return

        while True:
            try:
                data, addr = self.socket.recvfrom(self.buffer_size)
                self.on_message(data, addr)
            except KeyboardInterrupt:
                print("\n[!] Servidor encerrado pelo usuário")
                break
            except Exception as e:
                print(f"[!] Erro: {e}")

    def on_message(self, data, addr):
        """Trata as mensagens recebidas"""
        try:
            mensagem = data.decode('utf-8')
            
            # Adiciona cliente se for novo
            self.adicionar_cliente(addr)
            
            # Extrai nome do cliente se possível
            if ":" in mensagem and not mensagem.startswith("["):
                nome = mensagem.split(":")[0].strip()
                self.nomes_clientes[addr] = nome
            
            # Log da mensagem (trunca se for muito grande - benchmark)
            if len(mensagem) > 100:
                print(f"[MSG] {addr[0]}:{addr[1]} - [DADOS GRANDES: {len(mensagem)} bytes]")
            else:
                print(f"[MSG] {addr[0]}:{addr[1]} - {mensagem}")
            
            # Verifica se é comando de saída
            if "saiu do chat" in mensagem.lower():
                self.broadcast(mensagem, addr)
                self.remover_cliente(addr)
                return
            
            # Verifica se é entrada no chat
            if "entrou no chat" in mensagem.lower():
                self.broadcast(mensagem, addr)
                return
            
            # Verifica se é mudança de nome
            if "mudou o nome para" in mensagem.lower():
                self.broadcast(mensagem, addr)
                return
            
            # Mensagem normal - retransmite para todos os outros clientes
            self.broadcast(mensagem, addr)
            
        except UnicodeDecodeError:
            print(f"[!] Erro ao decodificar mensagem de {addr}")
        except Exception as e:
            print(f"[!] Erro ao processar mensagem: {e}")


if __name__ == "__main__":
    # Porta 5001 para UDP (diferente do TCP que usa 5000)
    server = UDPServer(host="0.0.0.0", port=5001)
    
    try:
        server.start()
    except KeyboardInterrupt:
        print("\n[!] Servidor UDP encerrado")