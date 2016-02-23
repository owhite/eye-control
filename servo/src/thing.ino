#include <Servo.h>
#include "servo_data.h"

Servo s1;
Servo s2;
Servo s3;
Servo s4;
Servo servos[4] = {s1, s2, s3, s4};

int ON = 0;
int OFF = 1;
int STARTING = 3;
int servoRoutineState = OFF;
int servoRoutineCounter = 0;
int servoRoutineMax = 0;
int servoIndexStart = 0;
int servoIndexStop = 0;
int servoRoutineNum = 0;

int servoVal;
int servoNum;
unsigned long servoTimeDelay; 

int sensitivity = 14; // may need to change if there are delays in loop()
int sensorValue;
int previousValue;

int LEDPin = 13;
int sensorPin = A1;

unsigned long resetInterval = 1000;
unsigned long previousMillis = 0;
unsigned long currentMillis = 0;

void startServoRoutine(int num) {
  digitalWrite(LEDPin, HIGH); 
  if (num < servoRoutineMax) {
    Serial.println("running");
    servoRoutineCounter = 0;
    servoIndexStart = servoArrayLengths[num * 2];
    servoIndexStop = servoArrayLengths[num * 2 + 1];
    servoRoutineState = ON;
  }
  else {
    servoRoutineNum = 0;
  }
  servoRoutineNum += 1;
}

void setup() {
  Serial.begin(115200);
  pinMode(LEDPin, OUTPUT);

  servoRoutineMax = sizeof(servoArrayLengths) / 4; // why 4, why not 2? 
  servos[0].attach(7);
  servos[1].attach(8);
  servos[2].attach(9);
  servos[3].attach(10);

  delay(2000);

  servoRoutineState = OFF;
  sensorValue = analogRead(sensorPin);
  previousValue = sensorValue;
}

void loop() {
  if (servoRoutineState == OFF) {
    // dont enter while the servos are running :-)
    sensorValue = analogRead(sensorPin);
    if (previousValue - sensorValue > sensitivity) {
      servoRoutineState = STARTING;
    }
    previousValue = sensorValue;
  }
  else if (servoRoutineState == STARTING) {
    startServoRoutine(servoRoutineNum);
  }
  else if (servoRoutineState == ON) {
    if (servoRoutineCounter + servoIndexStart > servoIndexStop) {
      // stop servo routine
      Serial.println("going off");
      digitalWrite(LEDPin, LOW); 
      delay(2000);
      sensorValue = analogRead(sensorPin);
      previousValue = sensorValue;
      servoRoutineState = OFF;
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

