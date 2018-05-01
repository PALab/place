// This Arduino sketch is designed for control of unipolar,
// 5-wire stepper motor. The specific model of stepper
// used here is a 28BYJ-48, with a ULN2003 stepper motor
// driver board. This motor has 64 steps, with reduction
// to a maximum of 4096 steps, although in this script, the
// roation is divided into 1024 steps, as this is the most
// reliable in terms of step accuracy. The motor is driven with
// a common-ground external power supply, and the control board
// is connected to the Arduino via digital pins 3 through 6.
//
// Also, a circuit is incorporated with a pushbutton, potentiometer,
// and LED to adjust the position of the stepper manually. If the
// LED is off, the stepper is controlled via serial commands, in the
// form of 'c<pos>' where <pos> ranges from 0 to 1024 for 0deg to 
// 360deg from the stepper position at reset.
//
// A module is included in PLACE to control the stepper with this
// sketch through the PLACE web app (see https://place.auckland.ac.nz/ 
// and https://github.com/palab/place for source).


#include <AccelStepper.h>
#define HALFSTEP 8

// Motor pin definitions
#define motorPin1  3     // IN1 on the ULN2003 driver 1
#define motorPin2  4     // IN2 on the ULN2003 driver 1
#define motorPin3  5     // IN3 on the ULN2003 driver 1
#define motorPin4  6     // IN4 on the ULN2003 driver 1

//Serial receiving variables
const byte numChars = 32;
char receivedChars[numChars]; // an array to store the received data
char _version[ ] = "v1.0 20/03/18";
boolean newData = false;

// Initialize with pin sequence IN1-IN3-IN2-IN4 for using the AccelStepper with 28BYJ-48
AccelStepper stepper1(HALFSTEP, motorPin1, motorPin3, motorPin2, motorPin4);
boolean newMove = true;
boolean firstMove = true;
int pos = 0;

void setup() {
  
  Serial.begin(9600);
  
  stepper1.setMaxSpeed(1000.0);
  stepper1.setAcceleration(500.0);
  stepper1.setSpeed(800);
  stepper1.moveTo(pos);

}//--(end setup )---


void loop() {
 recvWithEndMarker();
 showNewData();
 stepper1.run();

 //Print the current position to serial when finished moving
 if (newMove == true and stepper1.distanceToGo() == 0) {
   newMove = false;
   if (firstMove == true){
     firstMove = false;
     Serial.println('r');
   }
   else{
     Serial.println(stepper1.currentPosition() / 4); //NOTE THE /4. CAN GO SMALLER STEPS
   }
 }
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
      pos =  atoi(posChar) * 4;  //NOTE THE x4. CAN GO SMALLER STEPS
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
