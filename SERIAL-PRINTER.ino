// Flex Sensor Resistance Monitor (in Ohms)
// This code reads values from all five flex sensors and converts them to resistance in ohms

// Analog pins for flex sensors
int thumbPin = A0;
int indexPin = A1;
int middlePin = A2;
int ringPin = A3;
int littlePin = A4;

// Constants for resistance calculation
const float VCC = 5.0;      // Supply voltage (typically 5V on Arduino)
const float FIXED_RESISTOR = 10000.0;  // Value of the fixed resistor in the voltage divider (10K ohm)

void setup() {
  // Initialize serial communication
  Serial.begin(9600);
  
  // Set all analog pins as INPUT
  pinMode(thumbPin, INPUT);
  pinMode(indexPin, INPUT);
  pinMode(middlePin, INPUT);
  pinMode(ringPin, INPUT);
  pinMode(littlePin, INPUT);
  
  // Print header for better readability
  Serial.println("Thumb(ohms), Index(ohms), Middle(ohms), Ring(ohms), Little(ohms)");
}

// Function to convert analog reading to resistance in ohms
float calculateResistance(int analogValue) {
  // Convert ADC value to voltage
  float voltage = analogValue * VCC / 1023.0;
  
  // Calculate resistance using voltage divider formula:
  // R_flex = R_fixed * (Vcc/V - 1)
  if (voltage == 0) return 999999; // Avoid division by zero
  float resistance = FIXED_RESISTOR * (VCC / voltage - 1.0);
  
  return resistance;
}

void loop() {
  // Read analog values from all sensors
  int thumbRaw = analogRead(thumbPin);
  int indexRaw = analogRead(indexPin);  
  int middleRaw = analogRead(middlePin);
  int ringRaw = analogRead(ringPin);
  int littleRaw = analogRead(littlePin);
  
  // Convert to resistance in ohms
  float thumbResistance = calculateResistance(thumbRaw);
  float indexResistance = calculateResistance(indexRaw);
  float middleResistance = calculateResistance(middleRaw);
  float ringResistance = calculateResistance(ringRaw);
  float littleResistance = calculateResistance(littleRaw);
  
  // Print timestamp and all resistance values in CSV format
  Serial.print(thumbResistance);
  Serial.print(", ");
  Serial.print(indexResistance);
  Serial.print(", ");
  Serial.print(middleResistance);
  Serial.print(", ");
  Serial.print(ringResistance);
  Serial.print(", ");
  Serial.println(littleResistance);
  
  // Wait 2 seconds before the next reading
  delay(2000);
}