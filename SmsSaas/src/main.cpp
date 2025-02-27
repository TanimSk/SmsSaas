#include <SoftwareSerial.h>

#define TX D1     // GPIO5 (D1 on most ESP8266 boards)
#define RX D2     // GPIO4 (D2 on most ESP8266 boards)
#define Button D3 // GPIO0 (D3 on most ESP8266 boards)
#define BUILTIN_LED D4

SoftwareSerial MY_GSM(RX, TX); // Create a SoftwareSerial instance for GSM communication

char Phone_No[] = "+8801730288553";

void Make_Call(const char *number);

void setup()
{
  Serial.begin(9600); // Debugging on Serial Monitor
  MY_GSM.begin(9600); // Initialize SoftwareSerial for GSM
  pinMode(Button, INPUT_PULLUP);
  pinMode(BUILTIN_LED, OUTPUT);
  digitalWrite(BUILTIN_LED, LOW);
}

void loop()
{
  digitalWrite(BUILTIN_LED, LOW);
  if (digitalRead(Button) == LOW) // Button pressed
  {
    delay(50);                      // Basic debounce
    if (digitalRead(Button) == LOW) // Ensure it's still pressed
    {
      digitalWrite(BUILTIN_LED, HIGH);
      Serial.println("Calling...");
      Make_Call(Phone_No);
      while (digitalRead(Button) == LOW)
        ; // Wait for button release
    }
  }
  delay(5);
}

void Make_Call(const char *number)
{
  MY_GSM.print("ATD");
  MY_GSM.print(number);
  MY_GSM.println(";");
  delay(20000);          // Wait for 20 seconds before hanging up
  MY_GSM.println("ATH"); // Hang up
  delay(100);
}