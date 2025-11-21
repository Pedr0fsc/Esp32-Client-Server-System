#include <WiFi.h>
#include <ArduinoJson.h>

// ==================== CONFIGURAÇÕES - ALTERE AQUI ====================
const char* ssid = "SEU_WIFI_AQUI";           // Nome da sua rede WiFi
const char* password = "SUA_SENHA_AQUI";       // Senha do WiFi
const char* serverIP = "192.168.1.100";        // IP do computador com servidor
const int serverPort = 5000;                   // Porta do servidor TCP

// Pino do LED (LED embutido do ESP32)
const int LED_PIN = 2;  // GPIO2 - LED azul embutido da maioria dos ESP32
// =====================================================================

WiFiClient client;
unsigned long lastSendTime = 0;
const unsigned long sendInterval = 2000; // Envia dados a cada 2 segundos

// Variáveis para simular sensores
float temperatura = 25.0;
float umidade = 60.0;

void setup() {
  Serial.begin(115200);
  delay(1000);
  
  Serial.println("\n=== ESP32 Cliente TCP ===");
  
  // Configura o pino do LED
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);
  
  // Conecta ao WiFi
  conectarWiFi();
  
  // Conecta ao servidor TCP
  conectarServidor();
}

void loop() {
  // Verifica se ainda está conectado ao WiFi
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("[!] WiFi desconectado. Reconectando...");
    conectarWiFi();
  }
  
  // Verifica se ainda está conectado ao servidor
  if (!client.connected()) {
    Serial.println("[!] Servidor desconectado. Reconectando...");
    conectarServidor();
  }
  
  // Envia dados periódicos (a cada 2 segundos)
  if (millis() - lastSendTime >= sendInterval) {
    enviarDadosSensor();
    lastSendTime = millis();
  }
  
  // Verifica se recebeu comandos do servidor
  receberComandos();
  
  delay(10); // Pequeno delay para não sobrecarregar
}

void conectarWiFi() {
  Serial.print("Conectando ao WiFi: ");
  Serial.println(ssid);
  
  WiFi.begin(ssid, password);
  
  int tentativas = 0;
  while (WiFi.status() != WL_CONNECTED && tentativas < 20) {
    delay(500);
    Serial.print(".");
    tentativas++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n✓ WiFi conectado!");
    Serial.print("IP do ESP32: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("\n[!] Falha ao conectar WiFi");
    Serial.println("Reiniciando em 5 segundos...");
    delay(5000);
    ESP.restart();
  }
}

void conectarServidor() {
  Serial.print("Conectando ao servidor ");
  Serial.print(serverIP);
  Serial.print(":");
  Serial.println(serverPort);
  
  int tentativas = 0;
  while (!client.connect(serverIP, serverPort) && tentativas < 5) {
    Serial.println("[!] Falha na conexão. Tentando novamente...");
    delay(2000);
    tentativas++;
  }
  
  if (client.connected()) {
    Serial.println("✓ Conectado ao servidor!");
    
    // Pisca LED 3 vezes para indicar conexão
    for (int i = 0; i < 3; i++) {
      digitalWrite(LED_PIN, HIGH);
      delay(200);
      digitalWrite(LED_PIN, LOW);
      delay(200);
    }
  } else {
    Serial.println("[!] Não foi possível conectar ao servidor");
    Serial.println("Verifique se o servidor está rodando");
    Serial.println("Tentando novamente em 5 segundos...");
    delay(5000);
  }
}

void enviarDadosSensor() {
  if (!client.connected()) {
    return;
  }
  
  // Simula variação nos sensores (valores realistas)
  temperatura = 25.0 + random(-20, 50) / 10.0;  // 23°C a 27°C
  umidade = 60.0 + random(-100, 100) / 10.0;     // 50% a 70%
  
  // Cria JSON com os dados
  StaticJsonDocument<200> doc;
  doc["type"] = "data";
  doc["from"] = "esp32";
  
  JsonObject payload = doc.createNestedObject("payload");
  payload["temp"] = temperatura;
  payload["hum"] = umidade;
  
  // Serializa para string
  String jsonString;
  serializeJson(doc, jsonString);
  
  // Envia para o servidor
  client.println(jsonString);
  
  Serial.print("[→] Enviado: ");
  Serial.println(jsonString);
}

void receberComandos() {
  if (!client.connected()) {
    return;
  }
  
  // Verifica se há dados disponíveis
  while (client.available()) {
    String comando = client.readStringUntil('\n');
    comando.trim(); // Remove espaços e quebras de linha
    
    if (comando.length() > 0) {
      Serial.print("[←] Comando recebido: ");
      Serial.println(comando);
      
      // Processa comandos
      if (comando.indexOf("led_on") >= 0) {
        digitalWrite(LED_PIN, HIGH);
        Serial.println("[LED] Aceso ✓");
        
        // Confirma ao servidor
        client.println("[ESP32] LED aceso!");
      }
      else if (comando.indexOf("led_off") >= 0) {
        digitalWrite(LED_PIN, LOW);
        Serial.println("[LED] Apagado ✓");
        
        // Confirma ao servidor
        client.println("[ESP32] LED apagado!");
      }
      else if (comando.indexOf("status") >= 0) {
        // Comando extra: retorna status do ESP32
        String status = "[ESP32] Online - Temp: " + String(temperatura) + 
                       "°C, Umidade: " + String(umidade) + "%";
        client.println(status);
        Serial.println("[INFO] Status enviado");
      }
      else {
        // Comando desconhecido
        Serial.print("[?] Comando não reconhecido: ");
        Serial.println(comando);
      }
    }
  }
}