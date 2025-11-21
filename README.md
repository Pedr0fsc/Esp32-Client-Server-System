# Esp32-Client-Server-System

# **Guia Completo de Testes do Projeto**

## **Checklist de Preparação**

* \[ \] Todos os arquivos corrigidos copiados  
* \[ \] 4+ terminais abertos  
* \[ \] Servidor rodando  
* \[ \] ESP32 configurado (opcional)

---

## **TESTE 1: Servidor TCP com Múltiplos Clientes**

### **Passo 1: Iniciar Servidor TCP**

\# Terminal 1  
cd trabalho\_final/tcp  
python server\_tcp.py

**✅ Resultado esperado:**

\============================================================  
Servidor TCP iniciado em 0.0.0.0:5000  
Aguardando conexões...  
\============================================================

---

### **Passo 2: Conectar Cliente 1**

\# Terminal 2  
cd trabalho\_final/tcp  
python client\_tcp.py

**Inputs:**

Host (Enter \= localhost): \[ENTER\]  
Porta (Enter \= 5000): \[ENTER\]

**✅ Resultado esperado:**

Conectado ao servidor localhost:5000  
Use /nick \<nome\> para escolher seu nome  
Use /bench \<bytes\> para teste de performance  
Use /sair para sair

\[Usuario\] 

---

### **Passo 3: Mudar Nome do Cliente 1**

\# No Terminal 2 (Cliente 1\)  
\[Usuario\] /nick João

**✅ Resultado esperado:**

Nome alterado para João  
\[João\] 

**No Servidor (Terminal 1):**

\[CONEXÃO\] 127.0.0.1:xxxxx  
\[NICK\] Cliente\_xxxxx → João

---

### **Passo 4: Conectar Cliente 2**

\# Terminal 3  
cd trabalho\_final/tcp  
python client\_tcp.py

Pressione ENTER duas vezes, depois:

\[Usuario\] /nick Maria

**✅ Cliente 1 deve receber:**

\>\>\> Cliente\_xxxxx entrou no chat  
\>\>\> Cliente\_xxxxx agora é Maria

---

### **Passo 5: Conectar Cliente 3**

\# Terminal 4  
cd trabalho\_final/tcp  
python client\_tcp.py

\[Usuario\] /nick Pedro

---

### **Passo 6: Testar Chat Entre Clientes**

**Cliente 1 (João):**

\[João\] Olá pessoal\!

**✅ Clientes 2 e 3 devem receber:**

João: Olá pessoal\!

**Cliente 2 (Maria):**

\[Maria\] Oi João, tudo bem?

**✅ Clientes 1 e 3 recebem a mensagem**

---

### **Passo 7: Teste de Benchmark TCP**

**Cliente 1 (João):**

\[João\] /bench 1000000

**✅ Resultado esperado:**

\[BENCHMARK\] Enviando 1000000 bytes via TCP...  
\[BENCHMARK\] Tempo total: 0.1234 segundos  
\[BENCHMARK\] Taxa de transferência: 7.72 MB/s

**Teste com 10 MB:**

\[João\] /bench 10000000

---

### **Passo 8: Desconectar Cliente**

**Cliente 3 (Pedro):**

\[Pedro\] /sair

**✅ Outros clientes recebem:**

\>\>\> Pedro saiu do chat

**✅ No servidor:**

\[DESCONEXÃO\] Pedro (127.0.0.1:xxxxx)

---

## **TESTE 2: Servidor UDP com Múltiplos Clientes**

### **Passo 1: Iniciar Servidor UDP**

\# Terminal 1 (ou novo terminal)  
cd trabalho\_final/udp  
python server\_udp.py

**✅ Resultado esperado:**

\============================================================  
Servidor UDP iniciado em 0.0.0.0:5001  
Aguardando mensagens...  
\============================================================

---

### **Passo 2: Conectar 3 Clientes UDP**

**Terminal 2:**

cd trabalho\_final/udp  
python client\_udp.py

\# Primeiro comando  
/nick Alice

**Terminal 3:**

cd trabalho\_final/udp  
python client\_udp.py

/nick Bob

**Terminal 4:**

cd trabalho\_final/udp  
python client\_udp.py

/nick Carlos

---

### **Passo 3: Testar Chat UDP**

**Alice:**

Olá via UDP\!

**✅ Bob e Carlos recebem:**

Alice: Olá via UDP\!

---

### **Passo 4: Benchmark UDP**

**Alice:**

/bench 1000000

**✅ Resultado esperado:**

\[BENCHMARK\] Enviando 1000000 bytes via UDP...  
\[BENCHMARK\] Tempo total: 0.0543 segundos  
\[BENCHMARK\] Taxa de transferência: 17.54 MB/s

**Teste com 10 MB:**

/bench 10000000

---

## **TESTE 3: Comparação TCP vs UDP**

### **Execute os benchmarks e compare:**

| Protocolo | 1 MB | 10 MB | Observação |
| ----- | ----- | ----- | ----- |
| TCP | \~0.12s | \~1.2s | Mais lento, confiável |
| UDP | \~0.05s | \~0.5s | Mais rápido, pode perder dados |

**Justificativa para o vídeo:**

* **TCP**: Mais lento porque garante entrega e ordem dos pacotes  
* **UDP**: Mais rápido porque não espera confirmação, mas pode perder dados

---

## **TESTE 4: Integração com ESP32**

### **Passo 1: Configurar ESP32**

1. Abra o código do ESP32  
2. Configure:

const char\* ssid \= "SeuWiFi";  
const char\* password \= "SuaSenha";  
const char\* serverIP \= "192.168.1.XXX";  // IP do seu computador

### **Passo 2: Upload no ESP32**

1. Compile e faça upload  
2. Abra o Monitor Serial (115200 baud)

**✅ Monitor Serial deve mostrar:**

\=== ESP32 Cliente TCP \===  
Conectando ao WiFi: SeuWiFi  
...........  
✓ WiFi conectado\!  
IP: 192.168.1.105  
Conectando ao servidor...  
✓ Conectado ao servidor\!  
\[→\] Enviado: {"type":"data","from":"esp32","payload":{"temp":25.3,"hum":60.2}}

---

### **Passo 3: Ver Dados do ESP32 no Cliente**

**✅ Nos clientes TCP, a cada 2 segundos aparece:**

\[ESP32\] Temp: 25.3°C, Umidade: 60.2%  
\[ESP32\] Temp: 26.1°C, Umidade: 58.7%

---

### **Passo 4: Controlar LED do ESP32**

**Em qualquer cliente TCP:**

led\_on

**✅ Resultados esperados:**

1. LED do ESP32 acende  
2. Monitor Serial mostra: `[LED] Aceso ✓`  
3. Cliente recebe: `[ESP32] LED aceso!`

**Desligar LED:**

led\_off

**✅ LED apaga e confirmação retorna**

---

## **TESTE 5: Cenário Completo (Para o Vídeo)**

### **Setup:**

1. Servidor TCP rodando  
2. 3 clientes conectados (João, Maria, Pedro)  
3. ESP32 conectado e enviando dados  
4. Monitor Serial visível

### **Roteiro:**

1\. João: Olá pessoal\!  
   → Maria e Pedro recebem

2\. Maria: Vou acender o LED do ESP32  
   → Maria: led\_on  
   → LED acende  
   → Todos recebem: \[ESP32\] LED aceso\!

3\. Pedro: Interessante\! Agora vou testar performance  
   → Pedro: /bench 10000000  
   → Mostra taxa de transferência

4\. João: Vou desconectar  
   → João: /sair  
   → Outros recebem: \>\>\> João saiu do chat

5\. Dados do ESP32 continuam chegando a cada 2s  
   \[ESP32\] Temp: 25.8°C, Umidade: 61.3%

---

## **Problemas Comuns e Soluções**

### **"Clientes não recebem mensagens"**

* Verifique se o servidor está retransmitindo  
* Confirme que a porta está correta (5000 TCP, 5001 UDP)

### **"ESP32 não conecta"**

* Verifique WiFi e senha  
* Confirme IP do computador (use `ipconfig` ou `ifconfig`)  
* Desative firewall temporariamente

### **"Benchmark muito lento"**

* Normal\! TCP é mais lento que UDP  
* Se estiver MUITO lento (\>10s para 10MB), pode ser problema de rede

### **"Servidor UDP não retransmite"**

* Use o código corrigido que forneci  
* O original só enviava ACK de volta

---

## **Sugestão de Estrutura do Vídeo**

**Minuto 0-1:** Arquitetura

* Mostrar diagrama: Servidor ↔ Clientes ↔ ESP32

**Minuto 1-2:** Demo TCP

* Conectar 3 clientes  
* Trocar mensagens  
* Comando /nick

**Minuto 2-3:** ESP32

* Mostrar dados chegando  
* Acender/apagar LED

**Minuto 3-4:** Benchmark

* Executar TCP e UDP  
* Mostrar diferença  
* Explicar por quê

**Minuto 4-5:** Conclusão

* Dificuldades (ex: configurar ESP32)  
* Aprendizados (sockets, threads, protocolos)