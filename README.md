BOWCAR Module for Python
========================

infomation
-----------

바우카를 이용하여 파이썬을 배우기 위한 모듈입니다.
this module for study python with bowcar hardware.

arduino-cli 의 설치가 필수입니다.
this module need 'arduino-cli'.

[Arduino-cli 설치](https://arduino.github.io/arduino-cli/1.2/installation/)
이곳에서 설치하시길 바랍니다.
if you want to install 'arduino-cli' click that url.

설치법
------
powershell 등에서 pip을 이용해 설치할 수 있습니다.
```
pip install bowcar
```


명령어
------

0. 시간 지연 관련
    - BowCar.delay(time) : time(ms)만큼 지연

1. led 관련
    - BowCar.red_on() : 빨간 led 켜기
    - BowCar.red_off() : 파란 led 끄기
    - BowCar.blue_on() : 파란 led 켜기
    - BowCar.blue_off() : 파란 led 끄기
    - BowCar.all_light_on() : 모든 led 켜기
    - BowCar.all_light_off() : 모든 led 끄기

2. 부저 관련
    - BowCar.buzzer_on(scale, octave, note) : octave의 scale에 해당하는 음을 note음표 만큼 실행
    - BowCar.buzzer_off() : 부저 끄기
    - BowCar.set_duration(time) : 부저음의 기본 길이를 time(ms)만큼 조정

3. 모터 관련
    - BowCar.set_speed(type, speed) : type('l','r','a')의 속력 값을 speed로 설정
    - BowCar.set_direction(type, direction) : type('l','r','a')의 방향을 direction으로 설정(기본 값 정면)

4. 조도 센서 관련
    - BowCar.get_light() : 조도 센서 값 읽어오기
    - BowCar.is_light(type,thresehold) : 조도 센서 값이 기준값 thresehold 보다 큰지 작은지 타입에 따른 결과를 1과 0으로 return

5. 버튼 관련
    - BowCar.get_button(type) : 버튼 type('u','d','l','r')의 값을 return
    - BowCar.is_push(type) : 버튼 type('u','d','l','r')이 누른 상태면 1, 아니면 0을 return

6. 사운드 센서 관련
    - BowCar.get_sound() : 사운드 센서 값 읽어오기
    - BowCar.is_sound(type,thresehold) : 사운드 센서 값이 기준값 thresehold 보다 큰지 작은지 타입에 따른 결과를 1과 0으로 알려줌

7. 라인 트레이서 관련
    - BowCar.get_line(dir) : dir('l','r') 방향의 라인트레이서 값 읽어오기
    - BowCar.is_line(dir,type,thresehold) : dir('l','r') 방향의 라인트레이서 값이 기준값 thresehold 보다 큰지 작은지 타입에 따른 결과를 1과 0으로 알려줌

8. 초음파 센서 관련
    - BowCar.get_distance() : 초음파 센서로 거리 값 구하기
    - BowCar.distance(type,thresehold) : 초음파 센서로 얻은 거리 값이 기준(thresehold)보다 큰지 작은지 타입에 따른 결과를 1과 0으로 알려줌

9. 반복문 관련
    - bfor("변수 초기화; 조건; 변화") : 들여쓰기를 기준으로 for문 작성
    - bwhile("조건") : 들여쓰기를 기준으로 조건을 만족하는 동안 계속 작동하는 while문 생성
    - bbreak() : 반복문에 브레이크 집어넣기

10. 조건문 관련
    - bif("조건") : 조건문 들여쓰기로 작성
    - belif("조건") : 조건문 들여쓰기로 작성
    - belse() : 조건문 들여쓰기로 작성

11. 변수 관련
    - set_value(종류, 이름, 값) : 변수가 없다면 새로 선언하고 저장합니다. 하지만 이미 변수가 있다면 바로 설정합니다.
