const int fsrPin1 = A0;  // First FSR on A0
const int fsrPin2 = A1;  // Second FSR on A1

int fsrReading1;
int fsrReading2;

void setup() {
  Serial.begin(9600);   // Start serial communication
}

void loop() {
  fsrReading1 = analogRead(fsrPin1);  // Read from FSR1
  fsrReading2 = analogRead(fsrPin2);  // Read from FSR2

  // Format for Serial Plotter: values separated by tabs or commas
  Serial.print(fsrReading1);
  Serial.print("\t");                // Tab-separated for better plot
  Serial.println(fsrReading2);

  delay(20);  // Plot at ~50Hz
}
