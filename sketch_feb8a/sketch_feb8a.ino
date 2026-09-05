#define BUZZER 26

void setup() {
  Serial.begin(115200);
  pinMode(BUZZER, OUTPUT);
  digitalWrite(BUZZER, LOW);
  Serial.println("ESP32 READY");
}

void loop() {
  if (Serial.available()) {
    char c = Serial.read();
    Serial.println(c);

    if (c == 'A') {
      digitalWrite(BUZZER, HIGH);
    }
    if (c == 'B') {
      digitalWrite(BUZZER, LOW);
    }
  }
}
