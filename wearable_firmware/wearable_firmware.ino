// Define the analog pins for the four FSRs
const int fsrPin1 = A0;  // First FSR on A0
const int fsrPin2 = A1;  // Second FSR on A1
const int fsrPin3 = A2;  // Third FSR on A2
const int fsrPin4 = A3;  // Fourth FSR on A3

// Variables to store the readings
int fsrReading1;
int fsrReading2;
int fsrReading3;
int fsrReading4;

// The threshold below which we consider the reading to be noise.
const int NOISE_THRESHOLD = 10;

void setup() {
  Serial.begin(9600);   // Start serial communication
}

void loop() {
  // Read from all four FSRs
  fsrReading1 = analogRead(fsrPin1);
  fsrReading2 = analogRead(fsrPin2);
  fsrReading3 = analogRead(fsrPin3);
  fsrReading4 = analogRead(fsrPin4);

  // If a reading is below our threshold, force it to zero.
  if (fsrReading1 < NOISE_THRESHOLD) {
    fsrReading1 = 0;
  }
  if (fsrReading2 < NOISE_THRESHOLD) {
    fsrReading2 = 0;
  }
  if (fsrReading3 < NOISE_THRESHOLD) {
    fsrReading3 = 0;
  }
  if (fsrReading4 < NOISE_THRESHOLD) {
    fsrReading4 = 0;
  }

  // Format for Serial Plotter: values separated by tabs
  Serial.print(fsrReading1);
  Serial.print("\t");
  Serial.print(fsrReading2);
  Serial.print("\t");
  Serial.print(fsrReading3);
  Serial.print("\t");
  Serial.println(fsrReading4); // Use println on the last value for a new line

  delay(20);  // Plot at ~50Hz
}