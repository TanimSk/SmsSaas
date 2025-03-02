#include <WiFi.h>
#include <WebSocketClient.h>

#define TX 22
#define RX 23         // GPIO16 (RX on ESP32)
#define BUILTIN_LED 2 // LED GPIO pin for ESP32

const char *ssid = "কালাভূনা";       // WiFi SSID
const char *password = "sabir4141"; // WiFi Password

WebSocketClient wsClient; // WebSocket client instance

HardwareSerial SIM900(1); // Use hardware serial 1 for SIM900 (you can also use Serial1, Serial2, etc.)

WiFiClient wifiClient;

void Send_SMS(const char *number, const char *msg);

void setup()
{
  Serial.begin(9600);                     // Debugging Serial
  SIM900.begin(9600, SERIAL_8N1, RX, TX); // Start Hardware Serial for GSM Module
  pinMode(BUILTIN_LED, OUTPUT);
  digitalWrite(BUILTIN_LED, LOW);

  // Connect to WiFi
  Serial.print("Connecting to WiFi");
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED)
  {
    digitalWrite(BUILTIN_LED, HIGH);
    delay(250);
    Serial.print(".");
    digitalWrite(BUILTIN_LED, LOW);
    delay(250);
  }
  Serial.println("\nConnected to WiFi");

  // Connect to WebSocket server
  if (wifiClient.connect("192.168.1.107", 8000))
  {
    Serial.println("Connected to WebSocket server");
  }
  else
  {
    Serial.println("Connection failed.");
    while (1)
    {
      // Hang on failure
    }
  }

  // Handshake with the server
  wsClient.path = "/ws/messages/";
  wsClient.host = "192.168.1.107";
  if (wsClient.handshake(wifiClient))
  {
    Serial.println("Handshake successful");
  }
  else
  {
    Serial.println("Handshake failed.");
    while (1)
    {
      // Hang on failure
    }
  }

  // Wait to ensure the connection is established
  delay(1000);
}

void loop()
{
  String data;

  if (wifiClient.connected())
  {
    wsClient.getData(data); // Get data from WebSocket server
    if (data.length() > 0)
    {
      Serial.print("Received data: ");

      // Example message format: "+8801730288553|Hello, this is a test message"
      char *payload = strdup(data.c_str()); // Make mutable copy
      char *phone = strtok(payload, "|");
      char *id = strtok(NULL, "|");
      char *message = strtok(NULL, "|");

      Serial.println(String(phone) + " " + String(message) + " " + String(id));

      if (phone && message)
      {
        Send_SMS(phone, message);      // Send SMS if the phone number and message are valid
        wsClient.sendData(String(id)); // Send acknowledgment back to the server
      }

      free(payload); // Free allocated memory
    }

    wsClient.sendData("OK");
  }
  else
  {
    Serial.println("Client disconnected.");
    while (1)
    {
      // Hang on disconnect.
    }
  }

  // Wait to fully let the client disconnect
  delay(3000);
}

// Function to Send SMS via SIM900A
void Send_SMS(const char *number, const char *msg)
{
  digitalWrite(BUILTIN_LED, HIGH); // Turn on LED
  SIM900.println("AT+CMGF=1");     // Set SMS Text Mode
  delay(1000);
  SIM900.println("AT+CMGS=\"" + String(number) + "\"\r");
  delay(1000);
  SIM900.println(msg);
  delay(200);
  // Send SMS command (Ctrl+Z / ASCII 26)
  SIM900.write((char)26);
  delay(2000);

  digitalWrite(BUILTIN_LED, LOW); // Turn off LED
  Serial.println("SMS Sent!");
}