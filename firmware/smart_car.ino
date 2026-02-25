/*
 * Smart Car - Triple Mode Control System Firmware
 *
 * MODE 1: OpenCV Hand Gesture Control
 *   - Receives command codes (X/W/S/A/D) from Python Computer Vision
 *   - X=Stop, W=Forward, S=Reverse, A=Left, D=Right
 *
 * MODE 2: Manual Keyboard Control (Serial Monitor)
 *   - Direct keyboard control via Serial Monitor (W/A/S/D/X)
 *   - Supports speed selection levels (1/2/3)
 *
 * MODE 3: Python Controller Mode
 *   - Receives high-speed command codes (W/A/S/D/X) from Python scripts
 *   - Real-time continuous execution with safety auto-stop timeout
 */

// Motor driver pins (L298N)
#define ENA 5
#define ENB 6
#define IN1 7
#define IN2 8
#define IN3 9
#define IN4 11

// Speed settings
#define SLOW_SPEED 120
#define DEFAULT_SPEED 180
#define FAST_SPEED 250

// Global state variables
int operationMode = 0; // 0=Not selected, 1=OpenCV, 2=Manual, 3=Python Controller
int currentSpeed = DEFAULT_SPEED;
char currentCommand = 'X';
unsigned long lastCommandTime = 0;

void setup()
{
  Serial.begin(9600);

  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);
  pinMode(ENA, OUTPUT);
  pinMode(ENB, OUTPUT);

  stopMotors();
  printModeSelectionMenu();
}

void loop()
{
  if (operationMode == 0)
  {
    if (Serial.available() > 0)
    {
      char input = Serial.read();

      if (input == '1')
      {
        operationMode = 1;
        Serial.println("\n>>> SELECTED MODE 1: OpenCV Hand Gesture Control");
        Serial.println("Waiting for command stream from Python vision module...");
        Serial.println("Command Codes: X=Stop | W=Forward | S=Reverse | A=Left | D=Right\n");
      }
      else if (input == '2')
      {
        operationMode = 2;
        Serial.println("\n>>> SELECTED MODE 2: Manual Keyboard Control");
        printManualControlMenu();
      }
      else if (input == '3')
      {
        operationMode = 3;
        Serial.println("\n>>> SELECTED MODE 3: Python Controller Mode");
        Serial.println("Waiting for control commands from Python launcher...");
        Serial.println("Command Codes: W=Forward | S=Reverse | A=Left | D=Right | X=Stop\n");
      }
    }
    return;
  }

  if (operationMode == 1)
  {
    loopOpenCVMode();
  }
  else if (operationMode == 2)
  {
    loopManualMode();
  }
  else if (operationMode == 3)
  {
    loopPythonKeyboardMode();
  }
}

// ====================== MODE SELECTION MENU ======================
void printModeSelectionMenu()
{
  Serial.println("\n===========================================================");
  Serial.println("          SMART CAR - MULTI-MODAL VEHICLE CONTROLLER         ");
  Serial.println("===========================================================");
  Serial.println("\nSELECT OPERATIONAL MODE:");
  Serial.println("  [1] OpenCV Hand Gesture Control");
  Serial.println("      -> Computer Vision Gesture Navigation (AI)");
  Serial.println("      -> Requires running: python3 serial_bridge/gesture_serial_bridge.py");
  Serial.println();
  Serial.println("  [2] Manual Keyboard Control");
  Serial.println("      -> Direct keyboard control via W/A/S/D/X");
  Serial.println("      -> Adjustable speed levels via 1/2/3");
  Serial.println();
  Serial.println("  [3] Python Controller Mode");
  Serial.println("      -> High-speed control from Python host scripts");
  Serial.println("      -> Fixed speed rate with active safety timeout");
  Serial.println();
  Serial.print("Enter choice (1, 2, or 3): ");
}

// ====================== MODE 1: OpenCV Control ======================
void loopOpenCVMode()
{
  if (Serial.available() > 0)
  {
    char command = Serial.read();

    if (command == 'X' || command == 'W' || command == 'S' ||
        command == 'A' || command == 'D')
    {
      currentCommand = command;
      lastCommandTime = millis();
    }
  }

  if (millis() - lastCommandTime > 2000)
  {
    currentCommand = 'X';
  }

  executeCommand(currentCommand);
  delay(50);
}

// ====================== MODE 2: Manual Control ======================
void printManualControlMenu()
{
  Serial.println("\n===========================================================");
  Serial.println("              MANUAL SERIAL KEYBOARD CONTROL MENU          ");
  Serial.println("===========================================================");
  Serial.println("  W: Move Forward");
  Serial.println("  S: Move Reverse");
  Serial.println("  A: Turn Left");
  Serial.println("  D: Turn Right");
  Serial.println("  X: Emergency Stop");
  Serial.println();
  Serial.println("SPEED SELECTION:");
  Serial.println("  1: Slow Speed    (120)");
  Serial.println("  2: Normal Speed  (180)");
  Serial.println("  3: Fast Speed    (250)");
  Serial.println("===========================================================");
}

void loopManualMode()
{
  if (Serial.available() > 0)
  {
    char input = Serial.read();
    input = toupper(input);

    if (input == '1')
    {
      currentSpeed = SLOW_SPEED;
      Serial.println("Speed set to SLOW (120)");
    }
    else if (input == '2')
    {
      currentSpeed = DEFAULT_SPEED;
      Serial.println("Speed set to NORMAL (180)");
    }
    else if (input == '3')
    {
      currentSpeed = FAST_SPEED;
      Serial.println("Speed set to FAST (250)");
    }
    else if (input == 'W' || input == 'S' || input == 'A' ||
             input == 'D' || input == 'X')
    {
      executeCommand(input);
      Serial.print("Executed Command: ");
      Serial.println(input);
    }
  }
}

// ====================== MODE 3: Python Controller Mode ======================
void loopPythonKeyboardMode()
{
  if (Serial.available() > 0)
  {
    char command = Serial.read();

    if (command == 'X' || command == 'W' || command == 'S' ||
        command == 'A' || command == 'D')
    {
      currentCommand = command;
      lastCommandTime = millis();
      executeCommand(command);
    }
  }

  if (millis() - lastCommandTime > 500)
  {
    stopMotors();
  }
}

// ====================== MOTOR DRIVER CONTROLS ======================
void executeCommand(char cmd)
{
  switch (cmd)
  {
    case 'W': moveForward(); break;
    case 'S': moveReverse(); break;
    case 'A': turnLeft(); break;
    case 'D': turnRight(); break;
    case 'X': stopMotors(); break;
    default: stopMotors(); break;
  }
}

void moveForward()
{
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, LOW);
  analogWrite(ENA, currentSpeed);
  analogWrite(ENB, currentSpeed);
}

void moveReverse()
{
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, HIGH);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, HIGH);
  analogWrite(ENA, currentSpeed);
  analogWrite(ENB, currentSpeed);
}

void turnLeft()
{
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, HIGH);
  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, LOW);
  analogWrite(ENA, currentSpeed);
  analogWrite(ENB, currentSpeed);
}

void turnRight()
{
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, HIGH);
  analogWrite(ENA, currentSpeed);
  analogWrite(ENB, currentSpeed);
}

void stopMotors()
{
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, LOW);
  analogWrite(ENA, 0);
  analogWrite(ENB, 0);
}
