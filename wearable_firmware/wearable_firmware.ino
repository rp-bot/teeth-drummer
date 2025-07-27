const int fsrPin1 = A0;  // First FSR on A0
const int fsrPin2 = A1;  // Second FSR on A1

int fsrReading1;
int fsrReading2;

// The threshold below which we consider the reading to be noise.
const int NOISE_THRESHOLD = 10; 

void setup() {
  Serial.begin(9600);   // Start serial communication
}

void loop() {
  fsrReading1 = analogRead(fsrPin1);  // Read from FSR1
  fsrReading2 = analogRead(fsrPin2);  // Read from FSR2

  // If the reading is below our threshold, force it to zero.
  if (fsrReading1 < NOISE_THRESHOLD) {
    fsrReading1 = 0;
  }
  if (fsrReading2 < NOISE_THRESHOLD) {
    fsrReading2 = 0;
  }


  // Format for Serial Plotter: values separated by tabs or commas
  Serial.print(fsrReading1);
  Serial.print("\t");                // Tab-separated for better plot
  Serial.println(fsrReading2);

  delay(20);  // Plot at ~50Hz
}
