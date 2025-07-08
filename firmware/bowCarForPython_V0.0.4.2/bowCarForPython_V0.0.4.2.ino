const int RED_LED_PIN = 10;
const int BLUE_LED_PIN = 11;

void setup() {
  // 시리얼 통신을 9600 속도로 시작합니다.
  Serial.begin(9600); 
  // 아두이노 보드에 내장된 LED를 출력으로 설정합니다.
  pinMode(RED_LED_PIN, OUTPUT);
  pinMode(BLUE_LED_PIN, OUTPUT); 
}

void loop() {
  // 파이썬으로부터 수신한 데이터가 있는지 확인합니다.
  if (Serial.available() > 0) {
    // 줄바꿈 문자를 만날 때까지 문자열 전체를 읽어옴
    String command = Serial.readStringUntil('\n');
    command.trim();
    
    // '1'이라는 문자를 받으면 LED를 켭니다.
    if (command[0] == 'l'){
      if(command[1] == 'a'){
        if(command[2] == 'n'){
          digitalWrite(RED_LED_PIN, HIGH);
          digitalWrite(BLUE_LED_PIN, HIGH);
        }else{
          digitalWrite(RED_LED_PIN, LOW);
          digitalWrite(BLUE_LED_PIN, LOW);
        }
      }else if(command[1] == 'r'){
        if(command[2] == 'n'){
          digitalWrite(RED_LED_PIN, HIGH);
        }else{
          digitalWrite(RED_LED_PIN, LOW);
        }
      }else if(command[1] == 'b'){
        if(command[2] == 'n'){
          digitalWrite(BLUE_LED_PIN, HIGH);
        }else{
          digitalWrite(BLUE_LED_PIN, LOW);
        }
      }
    }
  }
}