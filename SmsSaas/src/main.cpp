#include <ArduinoWebsockets.h>
#include <ESP8266WiFi.h>
#include <SoftwareSerial.h>

#define TX D1 // GPIO5 (D1 on most ESP8266 boards)
#define RX D2 // GPIO4 (D2 on most ESP8266 boards)
#define BUILTIN_LED D4

const char *ssid = "কালাভুনা";                           // WiFi SSID
const char *password = "sabir4141";          // WiFi Password
const char *websocket_server = "192.168.1.107"; // WebSocket Server IP
const uint16_t websocket_port = 8000;            // WebSocket Port

using namespace websockets;

WebsocketsClient client;
SoftwareSerial SIM900(RX, TX); // SIM900A Communication

void Send_SMS(const char *number, const char *msg);
void onMessageCallback(WebsocketsMessage message);

void setup()
{
  Serial.begin(9600); // Debugging Serial
  SIM900.begin(9600); // GSM Module Serial
  pinMode(BUILTIN_LED, OUTPUT);
  digitalWrite(BUILTIN_LED, HIGH);

  // Connect to WiFi
  Serial.print("Connecting to WiFi");
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED)
  {
    digitalWrite(BUILTIN_LED, LOW);
    delay(250);
    Serial.print(".");
    digitalWrite(BUILTIN_LED, HIGH);
    delay(250);
  }
  Serial.println("\nConnected to WiFi");

  // Connect to WebSocket Server
  Serial.println("Connecting to WebSocket...");
  bool connected = client.connect(websocket_server, websocket_port, "/ws");
  if (connected)
  {
    Serial.println("WebSocket Connected!");
    client.send("ESP8266 Connected!");
  }
  else
  {
    Serial.println("WebSocket Connection Failed!");
  }

  // Set WebSocket Event Handler
  client.onMessage(onMessageCallback);
}

void loop()
{
  if (client.available())
  {
    client.poll(); // Listen for WebSocket messages
  }
  delay(500);
}

// WebSocket Message Handler
void onMessageCallback(WebsocketsMessage message)
{
  Serial.printf("Received: %s\n", message.data().c_str());

  // Example message format: "+8801730288553|Hello, this is a test message"
  char *payload = strdup(message.data().c_str()); // Make mutable copy
  char *phone = strtok(payload, "|");
  char *msg = strtok(NULL, "|");

  if (phone && msg)
  {
    Send_SMS(phone, msg);
    client.send("SENT:" + String(phone)); // Send acknowledgment
  }

  free(payload); // Free allocated memory
}

// Function to Send SMS via SIM900A
void Send_SMS(const char *number, const char *msg)
{
  digitalWrite(BUILTIN_LED, LOW); // Turn on LED
  SIM900.println("AT+CMGF=1");    // Set SMS Text Mode
  delay(100);
  SIM900.print("AT+CMGS=\"");
  SIM900.print(number);
  SIM900.println("\"");
  delay(100);
  SIM900.print(msg);
  delay(100);

  // Send SMS command (Ctrl+Z / ASCII 26)
  SIM900.write(26);
  delay(5000);
  Serial.println("SMS Sent!");
  digitalWrite(BUILTIN_LED, HIGH); // Turn off LED
}