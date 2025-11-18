/*
 * SmartCar - Triple Mode Control System
 * NGÀY: 19/11/2025
 *
 * MODE 1: OpenCV Hand Gesture Control
 *   - Nhận lệnh X/W/S/A/D từ Python OpenCV
 *   - X=Dừng, W=Tiến, S=Lùi, A=Trái, D=Phải
 *
 * MODE 2: Manual Keyboard Control (Serial Monitor)
 *   - Điều khiển trực tiếp W/A/S/D/X qua Serial Monitor
 *   - Hỗ trợ điều chỉnh tốc độ (1/2/3)
 *
 * MODE 3: Python Keyboard Control
 *   - Nhận lệnh W/A/S/D/X từ Python script
 *   - Điều khiển thời gian thực không có menu tốc độ
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

// Global variables
int operationMode = 0; // 0=Not selected, 1=OpenCV, 2=Manual, 3=Python Keyboard
int currentSpeed = DEFAULT_SPEED;
char currentCommand = 'X';
unsigned long lastCommandTime = 0;

void setup()
{
  // Initialize Serial communication
  Serial.begin(9600);

  // Configure motor pins as outputs
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);
  pinMode(ENA, OUTPUT);
  pinMode(ENB, OUTPUT);

  // Start with motors stopped
  stopMotors();

  // Display mode selection menu
  printModeSelectionMenu();
}

void loop()
{
  // If mode not selected yet, wait for mode selection
  if (operationMode == 0)
  {
    if (Serial.available() > 0)
    {
      char input = Serial.read();

      if (input == '1')
      {
        operationMode = 1;
        Serial.println("\n>>> CHON CHE DO 1: OpenCV Hand Gesture Control");
        Serial.println("Waiting for commands from Python...");
        Serial.println("Commands: X=Stop | W=Forward | S=Backward | A=Left | D=Right\n");
      }
      else if (input == '2')
      {
        operationMode = 2;
        Serial.println("\n>>> CHON CHE DO 2: Manual Keyboard Control");
        printManualControlMenu();
      }
      else if (input == '3')
      {
        operationMode = 3;
        Serial.println("\n>>> CHON CHE DO 3: Python Keyboard Control");
        Serial.println("Waiting for keyboard commands from Python...");
        Serial.println("Commands: W=Forward | S=Backward | A=Left | D=Right | X=Stop\n");
      }
    }
    return;
  }

  // Mode 1: OpenCV Hand Gesture Control
  if (operationMode == 1)
  {
    loopOpenCVMode();
  }
  // Mode 2: Manual Keyboard Control
  else if (operationMode == 2)
  {
    loopManualMode();
  }
  // Mode 3: Python Keyboard Control
  else if (operationMode == 3)
  {
    loopPythonKeyboardMode();
  }
}

// ====================== MODE SELECTION MENU ======================
void printModeSelectionMenu()
{
  Serial.println("\n╔═══════════════════════════════════════════════════════════╗");
  Serial.println("║           SMARTCAR - DUAL MODE CONTROL SYSTEM           ║");
  Serial.println("║                   NT106.Q14.2_GROUP2                    ║");
  Serial.println("╚═══════════════════════════════════════════════════════════╝");
  Serial.println("\nCHON CHE DO HOAT DONG:");
  Serial.println("  [1] OpenCV Hand Gesture Control");
  Serial.println("      → Dieu khien bang cu chi tay (AI)");
  Serial.println("      → Can chay Python script: transfer_UART.py");
  Serial.println();
  Serial.println("  [2] Manual Keyboard Control");
  Serial.println("      → Dieu khien bang phim W/A/S/D/X");
  Serial.println("      → Dieu chinh toc do bang phim 1/2/3");
  Serial.println();
  Serial.println("  [3] Python Keyboard Control");
  Serial.println("      → Dieu khien bang phim W/A/S/D/X tu Python");
  Serial.println("      → Toc do co dinh, khong co menu");
  Serial.println();
  Serial.print("Nhap lua chon (1, 2 hoac 3): ");
}

// ====================== MODE 1: OpenCV Control ======================
void loopOpenCVMode()
{
  // Read command from Serial (sent by Python OpenCV)
  if (Serial.available() > 0)
  {
    char command = Serial.read();

    // Only process valid OpenCV commands
    if (command == 'X' || command == 'W' || command == 'S' ||
        command == 'A' || command == 'D')
    {
      currentCommand = command;
      lastCommandTime = millis();
    }
  }

  // Safety: Auto-stop if no command received for 2 seconds
  if (millis() - lastCommandTime > 2000)
  {
    currentCommand = 'X';
  }

  // Execute current command with fixed OpenCV speed
  executeCommand(currentCommand, DEFAULT_SPEED);
}

// ====================== MODE 2: Manual Control ======================
void loopManualMode()
{
  // Read command from Serial (keyboard input)
  if (Serial.available() > 0)
  {
    char command = Serial.read();

    // Process movement commands
    if (command == 'W' || command == 'w')
    {
      currentCommand = 'W';
      Serial.println(">>> TIEN");
    }
    else if (command == 'S' || command == 's')
    {
      currentCommand = 'S';
      Serial.println(">>> LUI");
    }
    else if (command == 'A' || command == 'a')
    {
      currentCommand = 'A';
      Serial.println(">>> TRAI");
    }
    else if (command == 'D' || command == 'd')
    {
      currentCommand = 'D';
      Serial.println(">>> PHAI");
    }
    else if (command == 'X' || command == 'x' || command == ' ')
    {
      currentCommand = 'X';
      Serial.println(">>> DUNG");
    }
    // Speed control
    else if (command == '1')
    {
      currentSpeed = SLOW_SPEED;
      Serial.print("Toc do: CHAM (");
      Serial.print(currentSpeed);
      Serial.println(")");
    }
    else if (command == '2')
    {
      currentSpeed = DEFAULT_SPEED;
      Serial.print("Toc do: TRUNG BINH (");
      Serial.print(currentSpeed);
      Serial.println(")");
    }
    else if (command == '3')
    {
      currentSpeed = FAST_SPEED;
      Serial.print("Toc do: NHANH (");
      Serial.print(currentSpeed);
      Serial.println(")");
    }
    // Help menu
    else if (command == 'H' || command == 'h' || command == '?')
    {
      printManualControlMenu();
    }
  }

  // Execute current command with user-selected speed
  executeCommand(currentCommand, currentSpeed);
}

void printManualControlMenu()
{
  Serial.println("\n========================================");
  Serial.println("   MANUAL CONTROL - HUONG DAN");
  Serial.println("========================================");
  Serial.println("DIEU KHIEN:");
  Serial.println("  W/w - Tien");
  Serial.println("  S/s - Lui");
  Serial.println("  A/a - Trai");
  Serial.println("  D/d - Phai");
  Serial.println("  X/x/Space - Dung");
  Serial.println("\nTOC DO:");
  Serial.println("  1 - Cham (120)");
  Serial.println("  2 - Trung binh (180)");
  Serial.println("  3 - Nhanh (250)");
  Serial.println("\nKHAC:");
  Serial.println("  H/h/? - Hien thi menu");
  Serial.println("========================================");
  Serial.print("Toc do hien tai: ");
  Serial.println(currentSpeed);
  Serial.println("San sang nhan lenh...\n");
}

// ====================== MODE 3: Python Keyboard Control ======================
void loopPythonKeyboardMode()
{
  // Read command from Serial (sent by Python keyboard script)
  if (Serial.available() > 0)
  {
    char command = Serial.read();

    // Process movement commands (uppercase only for simplicity)
    if (command == 'W')
    {
      currentCommand = 'W';
    }
    else if (command == 'S')
    {
      currentCommand = 'S';
    }
    else if (command == 'A')
    {
      currentCommand = 'A';
    }
    else if (command == 'D')
    {
      currentCommand = 'D';
    }
    else if (command == 'X')
    {
      currentCommand = 'X';
    }
  }

  // Execute current command with default speed
  executeCommand(currentCommand, DEFAULT_SPEED);
}

// ====================== MOTOR CONTROL FUNCTIONS ======================
void executeCommand(char cmd, int speed)
{
  switch (cmd)
  {
  case 'W': // Forward
    moveForward(speed);
    break;

  case 'S': // Backward
    moveBackward(speed);
    break;

  case 'A': // Left
    turnLeft(speed);
    break;

  case 'D': // Right
    turnRight(speed);
    break;

  case 'X': // Stop
  default:
    stopMotors();
    break;
  }
}

void moveForward(int speed)
{
  analogWrite(ENA, speed);
  analogWrite(ENB, speed);
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, HIGH);
}

void moveBackward(int speed)
{
  analogWrite(ENA, speed);
  analogWrite(ENB, speed);
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, HIGH);
  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, LOW);
}

void turnLeft(int speed)
{
  analogWrite(ENA, speed);
  analogWrite(ENB, speed);
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, HIGH);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, HIGH);
}

void turnRight(int speed)
{
  analogWrite(ENA, speed);
  analogWrite(ENB, speed);
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, LOW);
}

void stopMotors()
{
  digitalWrite(ENA, LOW);
  digitalWrite(ENB, LOW);
}
