// This Arduino sketch is designed for control of bipolar,
// 4-wire stepper motor. The specific model of stepper
// used here is a RS Pro High Torque Stepper (stock No 535-0372)
// NEMA 17, 2.1 Ohm, 1.33 A, 2.8 V, with a L298N stepper motor
// chip on a Duinotech XC4492 driver board sold through Jaycar
// electronics. This motor has 200 steps with no gear reduction.
// The control board is connected to the Arduino via digital 
// pins 1 through 6, where 1 and 6 are always HIGH as enable pins.
//
// IMPORTANT: The power supply for the motor is connected through
// the driver board at 5V and maximum 0.8A. The 5V logic power 
// supply for the board is from the Arduino, and not from the 
// inbuilt regulator.
//
// Also, a circuit is incorporated with a pushbutton, potentiometer,
// and LED to adjust the position of the stepper manually. If the
// LED is off, the stepper is controlled via serial commands, in the
// form of 'c<pos>' where <pos> ranges from 0 to 200 for 0deg to 
// 360deg from the stepper position at reset.
//
// A module is included in PLACE to control the stepper with this
// sketch through the PLACE web app (see https://place.auckland.ac.nz/ 
// and https://github.com/palab/place for source).

#include <AccelStepper.h>
#define HALFSTEP 8

// Motor pin definitions
#define motorPin1  2     // IN1 on the driver 
#define motorPin2  3     // IN2 on the driver 
#define motorPin3  4     // IN3 on the driver 
#define motorPin4  5     // IN4 on the driver

// Enable pin definitions
int en1 = 1;
int en2 = 6;

//Serial receiving variables
const byte numChars = 32;
char receivedChars[numChars]; // an array to store the received data
char _version[ ] = "v2.0 14/05/18";
boolean newData = false;

// Initialize with pin sequence IN1-IN3-IN2-IN4 for using the AccelStepper with L298N
AccelStepper stepper1(HALFSTEP, motorPin1, motorPin2, motorPin3, motorPin4);
boolean newMove = true;
boolean firstMove = true;
int pos = 0;
int rot_speed = 1000;
int step_multiple = 4;

//Specify the pins for moving stepper manually
int button = 12;
int led = 13;
int pot = 0;
bool manualMode = false;
int prevPotPos = 0;
int potPos = 0;
int prevRead = HIGH;

void setup() {
  
  Serial.begin(9600);

  pinMode(button, INPUT);
  digitalWrite (button, HIGH);
  pinMode(led, OUTPUT);

  stepper1.setMaxSpeed(2000.0);
  stepper1.setAcceleration(1000.0);
  stepper1.setSpeed(rot_speed);
  stepper1.moveTo(pos);

  prevPotPos = analogRead(pot);
  potPos = analogRead(pot);

  // Enable Stepper driver channels
  pinMode(en1, OUTPUT);
  pinMode(en2, OUTPUT);
  digitalWrite(en1, HIGH);
  digitalWrite(en2, HIGH);  

}//--(end setup )---


void loop() {
 
  if (manualMode == false or newMove == true){
    recvWithEndMarker();
    showNewData();
    stepper1.run();
  }
  else{
    potPos = analogRead(pot);
    if (abs(potPos - prevPotPos) > 7){
      newMove = true;
      stepper1.move(round(abs(potPos - prevPotPos)/4));
      prevPotPos = potPos;
    }
  }

  //Print the current position to serial when finished moving
  if (newMove == true and stepper1.distanceToGo() == 0) {
    newMove = false;
    if (firstMove == true){
      firstMove = false;
      Serial.println('r');
    }
    else{
      if (manualMode == false){
        Serial.println(stepper1.currentPosition() / step_multiple); 
      }  
    }
  }

 
  if (newMove == false and digitalRead(button) == HIGH and prevRead == LOW){
    if (manualMode == false){
      digitalWrite(led, HIGH);
      manualMode = true;
    }
    else{
      digitalWrite(led, LOW);
      manualMode = false; 
      stepper1.setCurrentPosition(0);
      stepper1.setSpeed(rot_speed);     
    }
  }
    
  prevRead = digitalRead(button);
}

void recvWithEndMarker() {
 static byte ndx = 0;
 char endMarker = '\n';
 char rc;
 
 if (Serial.available() > 0 && newData == false) {
   rc = Serial.read();
   
   if (rc != endMarker) {
     receivedChars[ndx] = rc;
     ndx++;
     if (ndx >= numChars) {
         ndx = numChars - 1;
     }
   }
   
  else {
    receivedChars[ndx] = '\0'; // terminate the string
    ndx = 0;
    newData = true;
    }
  }
}

void showNewData() {
 if (newData == true) {
   newData = false;

    if (receivedChars[0] == 'c') {
      char posChar[numChars-1];
      memcpy(posChar,receivedChars+1,numChars-1);
      pos =  atoi(posChar) * step_multiple;
      newMove = true;
      stepper1.moveTo(pos);      
    }

    if (receivedChars[0] == 'g') {
        Serial.println(pos);
    }   

    if (receivedChars[0] == 'i') {
        Serial.println(_version);
    }   
  }
}
