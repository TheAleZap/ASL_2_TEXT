// Flex Sensor Gesture Recognition with Best Match Selection and NULL Value Support
// This code reads values from five flex sensors and determines which letter
// gesture is being made based on predefined resistance ranges

// Analog pins for flex sensors
const int FLEX_PINS[5] = {A0, A1, A2, A3, A4}; // Thumb, Index, Middle, Ring, Little

// Constants for resistance calculation
const float VCC = 5.0;             // Supply voltage (typically 5V on Arduino)
const float FIXED_RESISTOR = 10000.0; // Value of fixed resistor (10K ohm)

// Special NULL value to ignore a specific finger
const float NULL_VALUE = -1.0; // Using -1 as a sentinel since resistance is always positive

// ================= LETTER CONFIGURATION SECTION =================
// To modify letters, update the values in this section
// Each row represents a letter and its 5 sensor resistance values in ohms
// Format: {letter, tolerance_percentage, thumb, index, middle, ring, little}
// Use NULL_VALUE to ignore a specific finger in the matching algorithm

// Letter data structure
struct LetterConfig {
  char letter;
  float tolerance; // Individual tolerance percentage for each letter (0.10 = 10%)
  float sensorValues[5];
};

// Total number of configured letters (A-Z = 26)
const int NUM_LETTERS = 27;

//NEW VER NEW NEW
// Letter configurations - MODIFY VALUES AS NEEDED
LetterConfig LETTER_CONFIG[NUM_LETTERS] = {
  // Letter, Tolerance, Thumb,     Index,      Middle,     Ring,       Little
  {'_',     0.10,      26931.41, 23000.00, 24795.92, 26276.60, 33347.46},
  {'A',     0.15,     29346.16, 31585.37, 34094.83, 53540.37, 56000.00},
  {'B',     0.10,      29498.07,   22893.89,   24795.92,   26276.60,   33531.91},
  {'C',     0.10,      28171.65, 25644.60, 28458.65, 32803.35, 35066.08},
  {'D',     0.10,      36081.08, 22683.71, 35466.67, 53148.14, 53540.37},
  {'E',     0.10,      35265.48, 34094.83, 33717.95, 56428.57, 57302.63},
  {'F',     0.10,      27610.29,   28603.78,   24795.92,   26148.41,   32983.19},
  {'G',     0.10,      26276.60, 23106.80, 28458.65, 31084.34, 36712.33},
  {'H',     0.10,      26276.60, 23214.29, 24795.92, 35066.08, 37361.11},
  {'I',     0.10,      31250.00, 29651.16, 31926.23, 39660.19, 35066.08},
  {'J',     0.10,     28458.65, 28171.65, 29045.80, 29346.16, 33905.58},
  {'K',     0.10,      28603.78, 23322.48, 29498.07, 42731.96, 46833.33},
  {'L',     0.10,      26798.56, 22683.71, 34672.49, 52760.73, 52000.00},
  {'M',     0.10,      28171.65, 29346.16, 31084.34, 46519.33, 44705.88},
  {'N',     0.10,      26931.41, 29346.16, 31585.37, 44705.88, 41928.93},
  {'O',     0.10,      29195.41, 27610.29, 30275.59, 41928.93, 43281.25},
  {'P',     0.10,      25644.60,   22683.71, 24914.68, 40147.05, 45297.30},
  {'Q',     0.10,      30756.97, 27749.08, 33905.58, 46519.33, 45297.30},
  {'R',     0.10,      26148.41, 23214.29, 25769.23, 25894.74, 32983.19},
  {'S',     0.10,      26666.67, 30920.00, 34672.49, 53937.50, 59121.62},
  {'T',     0.10,      27888.89, 30756.97, 33164.56, 38947.37, 42731.96},
  {'U',     0.10,      31926.23, 23214.29, 38028.17, 53148.14, 33347.46},
  {'V',     0.10,      33347.46, 23000.00, 25034.25, 46519.33, 45901.64},
  {'W',     0.10,      28897.34, 23214.29, 24795.92, 26798.56, 56000.00},
  {'X',     0.10,      33905.58, 25769.23, 33164.56, 49824.56, 45297.30},
  {'Y',     0.10,      26148.41, 29195.41, 30920.00, 45000.00, 33164.56},
  {'Z',     0.10,      26798.56, 22788.46, 24914.68, 49132.95, 44414.89},

};
// ================= END LETTER CONFIGURATION SECTION =================

// Variables for tracking timing
unsigned long lastLetterTime = 0;
const unsigned long LETTER_INTERVAL = 2000; // 5 seconds between letter prints

void setup() {
  // Initialize serial communication
  Serial.begin(9600);
  
  // Set all analog pins as INPUT
  for (int i = 0; i < 5; i++) {
    pinMode(FLEX_PINS[i], INPUT);
  }
  
  Serial.println("Flex Sensor Gesture Recognition");
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

// Function to calculate error percentage between measured and reference values
float calculateError(float measured, float reference) {
  if (reference <= 0) return 999999.0; // Large error for invalid reference
  return abs(measured - reference) / reference;
}

// Calculate match score for a letter (lower is better)
float calculateMatchScore(float measured[5], LetterConfig letter) {
  float totalError = 0;
  int validSensors = 0;
  
  for (int i = 0; i < 5; i++) {
    // Skip this finger if it's marked as NULL_VALUE
    if (letter.sensorValues[i] == NULL_VALUE) {
      continue;
    }
    
    // Skip placeholder values
    if (letter.sensorValues[i] < 1.0) {
      return 999999.0; // Large error for unconfigured letters
    }
    
    // Calculate error for this sensor
    float error = calculateError(measured[i], letter.sensorValues[i]);
    totalError += error;
    validSensors++;
  }
  
  // Return average error if we have valid sensors, otherwise large error
  return (validSensors > 0) ? (totalError / validSensors) : 999999.0;
}

// Function to determine which letter best matches the current sensor readings
char recognizeLetter(float sensorValues[5]) {
  char bestLetter = ' ';
  float bestScore = 999999.0;
  
  // Check each letter configuration to find the best match
  for (int i = 0; i < NUM_LETTERS; i++) {
    // Skip letters with placeholder values (all zeros)
    bool hasValidValues = false;
    for (int j = 0; j < 5; j++) {
      if (LETTER_CONFIG[i].sensorValues[j] > 1.0 && 
          LETTER_CONFIG[i].sensorValues[j] != NULL_VALUE) {
        hasValidValues = true;
        break;
      }
    }
    if (!hasValidValues) continue;
    
    // Calculate match score for this letter
    float score = calculateMatchScore(sensorValues, LETTER_CONFIG[i]);
    
    // Check if this letter is within tolerance
    float tolerance = LETTER_CONFIG[i].tolerance;
    if (score <= tolerance) {
      // If this is the best match so far, save it
      if (score < bestScore) {
        bestScore = score;
        bestLetter = LETTER_CONFIG[i].letter;
      }
    }
  }
  
  return bestLetter;
}

void loop() {
  // Array to store current sensor resistance values
  float currentResistance[5];
  
  // Read all sensors and calculate resistance
  for (int i = 0; i < 5; i++) {
    int rawValue = analogRead(FLEX_PINS[i]);
    currentResistance[i] = calculateResistance(rawValue);
  }
  
  // Recognize current letter
  char currentLetter = recognizeLetter(currentResistance);
  
  // Check if it's time to print a letter (every 5 seconds)
  unsigned long currentTime = millis();
  if (currentTime - lastLetterTime >= LETTER_INTERVAL) {
    if (currentLetter != ' ') {
      Serial.println(currentLetter);
    } else {
      Serial.println("No match found");
    }
    lastLetterTime = currentTime;
  }
  
  // Short delay for stability
  delay(100);
}