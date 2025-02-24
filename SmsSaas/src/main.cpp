#include <HardwareSerial.h>

#define RX 32
#define TX 33
#define Button 25

HardwareSerial MY_GSM(1); // Use Serial1 (ESP32 supports multiple hardware serials)

char Phone_No[] = "+8801730288553";

void Make_Call(const char *number);

void setup()
{
  Serial.begin(9600);
  MY_GSM.begin(9600, SERIAL_8N1, RX, TX); // Initialize Serial1 with proper pins
  pinMode(Button, INPUT_PULLUP);
}

void loop()
{
  if (digitalRead(Button) == LOW) // Button pressed
  {
    delay(50);                      // Basic debounce
    if (digitalRead(Button) == LOW) // Ensure it's still pressed
    {
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