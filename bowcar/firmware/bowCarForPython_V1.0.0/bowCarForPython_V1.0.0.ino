#include <Arduino.h>
#include <Adafruit_NeoPixel.h>

// Arduino pin numbers for BowCar
// 바우카를 위한 아두이노 핀 번호

// LED control pins
const int RED_LED_PIN =10;
const int BLUE_LED_PIN =11;

// Ultrasonic sensor pins
const int TRIG_PIN =13;
const int ECHO_PIN =12;

// IR sensor pins
const int IRL_PIN =A6;
const int IRR_PIN =A7;

// Sound sensor pin
const int SS_PIN =A3;

// Buzzer pin
const int BUZZER_PIN =3;

// Light Sensor
const int LS_PIN = A2;

// Motor control pins
const int LM_DIR_PIN =2;
const int LM_PWM_PIN =5;

const int RM_DIR_PIN =4;
const int RM_PWM_PIN =6;

// Button pin
const int UB_PIN =A0;
const int DB_PIN =A1;
const int LB_PIN =7;
const int RB_PIN =8;

// NeoPixel
const int NEOPIXEL_PIN = 9;
const int NEOPIXEL_COUNT = 4;
Adafruit_NeoPixel strip(NEOPIXEL_COUNT, NEOPIXEL_PIN, NEO_GRB + NEO_KHZ800);

int duration = 2000;

long Distance() {
    digitalWrite(TRIG_PIN, LOW);
    delayMicroseconds(2);
    digitalWrite(TRIG_PIN, HIGH);
    delayMicroseconds(10);
    digitalWrite(TRIG_PIN, LOW);

    long dura = pulseIn(ECHO_PIN, HIGH);
    delay(50);
    long dist = dura / 29 / 2;
    return dist;
}


void setup() {
  Serial.begin(9600);
  pinMode(UB_PIN, INPUT_PULLUP);
  pinMode(DB_PIN, INPUT_PULLUP);
  pinMode(LB_PIN, INPUT_PULLUP);
  pinMode(RB_PIN, INPUT_PULLUP);
  pinMode(RED_LED_PIN, OUTPUT);
  pinMode(LS_PIN, INPUT);
  pinMode(BLUE_LED_PIN, OUTPUT);
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  pinMode(BUZZER_PIN, OUTPUT);
  pinMode(LM_DIR_PIN, OUTPUT);
  pinMode(LM_PWM_PIN, OUTPUT);
  pinMode(RM_DIR_PIN, OUTPUT);
  pinMode(RM_PWM_PIN, OUTPUT);
  
  strip.begin();
  strip.show(); // Initialize all pixels to 'off'
}

void loop() {
  int Value = 0;
  int _temp = 0;
  String command = ""; 
  
  if (Serial.available() > 0) {
    command = Serial.readStringUntil('\n');
    
    // Command parsing
    // l: LED, b: Buzzer, s: Setting, m: Motor, r: Read Sensor, n: NeoPixel
    
    switch(command[0]){
      case 'l': // LED
        switch(command[1]){
          case 'r': // Red
            if(command[2]=='n') digitalWrite(RED_LED_PIN, HIGH);
            else digitalWrite(RED_LED_PIN, LOW);
            break;
          case 'b': // Blue
            if(command[2]=='n') digitalWrite(BLUE_LED_PIN, HIGH);
            else digitalWrite(BLUE_LED_PIN, LOW);
            break;
          case 'a': // All
             if(command[2]=='n') {
               digitalWrite(RED_LED_PIN, HIGH);
               digitalWrite(BLUE_LED_PIN, HIGH);
             }
            else {
               digitalWrite(RED_LED_PIN, LOW);
               digitalWrite(BLUE_LED_PIN, LOW);
            }
            break;
        }
        break;
        
      case 'b': // Buzzer
        if(command[1]=='n' && command[2]=='n'){
           noTone(BUZZER_PIN);
        }
        else{
           // Format: b[octave][scale][note] e.g., b4C04
           // Simplified buzzer logic for now
           tone(BUZZER_PIN, 262, duration/4*0.95); // Default C4
        }
        break;
        
      case 's': // Setting
         if(command[1]=='d'){
            duration = command.substring(2).toInt();
         }
         else if(command[1]=='w'){ // Set Wheel Direction
            int dir = command.substring(3).toInt();
            if(command[2]=='l') digitalWrite(LM_DIR_PIN, dir);
            else digitalWrite(RM_DIR_PIN, dir);
         }
         else if(command[1]=='m'){ // Set Motor Speed
            int speed = command.substring(3).toInt();
             if(command[2]=='l') analogWrite(LM_PWM_PIN, speed);
            else analogWrite(RM_PWM_PIN, speed);
         }
         break;
         
      case 'r': // Read sensor
        switch(command[1]){
          case 'l': // Light sensor
            Value = analogRead(LS_PIN);
            _temp = command.substring(3).toInt();
            if(command[2]=='u') Serial.println(Value > _temp);
            else Serial.println(Value < _temp);
            break;
          case 's': // Sound sensor
             Value = analogRead(SS_PIN);
            _temp = command.substring(3).toInt();
            if(command[2]=='u') Serial.println(Value > _temp);
            else Serial.println(Value < _temp);
            break;
          case 't': // Line tracer
             if(command[2]=='l') Value = analogRead(IRL_PIN);
             else Value = analogRead(IRR_PIN);
             
             _temp = command.substring(4).toInt();
             if(command[3]=='u') Serial.println(Value > _temp);
             else Serial.println(Value < _temp);
             break;
          case 'd': // Distance
             Value = Distance();
             _temp = command.substring(3).toInt();
             if(command[2]=='u') Serial.println(Value > _temp);
             else Serial.println(Value < _temp);
             break;
          case 'b': // Button
             // rb[button]
             // u, d, l, r
             int pin = UB_PIN;
             if(command[2]=='d') pin = DB_PIN;
             else if(command[2]=='l') pin = LB_PIN;
             else if(command[2]=='r') pin = RB_PIN;
             
             Serial.println(digitalRead(pin) == LOW); // Pressed = 1 (True)
             break;
        }
        break;
        
      case 'g': // Get sensor value
         switch(command[1]){
           case 'l': Serial.println(analogRead(LS_PIN)); break;
           case 's': Serial.println(analogRead(SS_PIN)); break;
           case 't': 
             if(command[2]=='l') Serial.println(analogRead(IRL_PIN));
             else Serial.println(analogRead(IRR_PIN));
             break;
           case 'd': Serial.println(Distance()); break;
         }
         break;

      case 'n': // NeoPixel
        // nc[idx][rrr][ggg][bbb]
        // na[rrr][ggg][bbb]
        // no
        // nb[val]
        if (command[1] == 'c') {
           int idx = command.substring(2, 3).toInt();
           int r = command.substring(3, 6).toInt();
           int g = command.substring(6, 9).toInt();
           int b = command.substring(9, 12).toInt();
           strip.setPixelColor(idx, strip.Color(r, g, b));
           strip.show();
        }
        else if (command[1] == 'a') {
           int r = command.substring(2, 5).toInt();
           int g = command.substring(5, 8).toInt();
           int b = command.substring(8, 11).toInt();
           for(int i=0; i<NEOPIXEL_COUNT; i++) {
             strip.setPixelColor(i, strip.Color(r, g, b));
           }
           strip.show();
        }
        else if (command[1] == 'o') {
           strip.clear();
           strip.show();
        }
        else if (command[1] == 'b') {
           int val = command.substring(2, 5).toInt();
           strip.setBrightness(val);
           strip.show();
        }
        break;
    }
  }
}