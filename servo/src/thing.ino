#include <Servo.h>
#include "servo_data.h"

Servo s1;
Servo s2;
Servo s3;
Servo s4;
Servo servos[4] = {s1, s2, s3, s4};

int bigEyeRoutine = 8;

int ON = 0;
int OFF = 1;
int servoRoutineState = OFF;
int servoRoutineCounter = 0;
int servoRoutineMax = 0;
int servoIndexStart = 0;
int servoIndexStop = 0;
int servoRoutineNum = 0;

int servoVal;
int servoNum;
unsigned long servoTimeDelay; 

int sensitivity = 25; // may need to change if there are delays in loop()
int sensorValue;
int pirValue;
int previousValue;

int LEDPin = 13;
int pirPin = 11;
int switchPin = 6;
int sensorPin = A1;

int move_counter = 0;

unsigned long resetInterval = 1000;
unsigned long previousMillis = 0;
unsigned long currentMillis = 0;

void stopServoRoutine() {
  servos[0].detach();
  servos[1].detach();
  servos[2].detach();
  servos[3].detach();
  servoRoutineState = OFF;
  delay(2000); // let things settle
  sensorValue = analogRead(sensorPin);
  previousValue = sensorValue + 500;
  move_counter = 0;
  digitalWrite(LEDPin, LOW); 
}

void startServoRoutine() {
  digitalWrite(LEDPin, HIGH); 
  servoRoutineNum = servoRoutineNum % servoRoutineMax;
  servos[0].attach(7);
  servos[1].attach(8);
  servos[2].attach(9);
  servos[3].attach(10);

  servoRoutineCounter = 0;
  servoIndexStart = servoArrayLengths[servoRoutineNum * 2];
  servoIndexStop = servoArrayLengths[servoRoutineNum * 2 + 1];
  servoRoutineState = ON;

  servoRoutineNum += 1;
}

void setup() {
  Serial.begin(115200);
  pinMode(LEDPin, OUTPUT);
  pinMode(pirPin, INPUT);
  pinMode(switchPin, INPUT);

  servoRoutineMax = sizeof(servoArrayLengths) / 4; // why 4, why not 2? 

  delay(2000);

  servoRoutineState = OFF;
  sensorValue = analogRead(sensorPin);
  previousValue = sensorValue + 500;
}

void loop() {
  if (digitalRead(switchPin) == HIGH) {
    servoRoutineCounter = bigEyeRoutine;
    servoRoutineNum = bigEyeRoutine;
    startServoRoutine();
  }
  if (servoRoutineState == OFF) {
    // Serial.println("SAMPLING");
    // dont take readings while servos are running
    sensorValue = analogRead(sensorPin);
    if (sensorValue - previousValue > sensitivity) {
      //      char str[16];
      // sprintf(str, "BUMP %d %d", sensorValue, previousValue);
      // Serial.println(str);
      startServoRoutine();
    }
    previousValue = sensorValue;
    if (digitalRead(pirPin) == HIGH) {
      startServoRoutine();
    }
  }
  else if (servoRoutineState == ON) {
    if (servoRoutineCounter + servoIndexStart > servoIndexStop) {
      stopServoRoutine();
    }
    else {
      char str[16];
      servoTimeDelay = (unsigned long) servoArray[servoRoutineCounter + servoIndexStart];
      servoNum = servoArray[servoRoutineCounter + servoIndexStart + 1];
      servoVal = servoArray[servoRoutineCounter + servoIndexStart + 2];
      sprintf(str, "%d %d %d", servoTimeDelay, servoNum, servoVal);
      servos[servoNum].write(servoVal);
      delay(servoTimeDelay);
    }
    servoRoutineCounter+=3;
  }
  else {
    digitalWrite(LEDPin, LOW); 
  }
}

