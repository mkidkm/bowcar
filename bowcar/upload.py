import serial.tools.list_ports
import os
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Optional, Type, Union
from .base import BowCarBase

# 이 클래스에서 사용할 아두이노 보드, 폴더, 파일 이름 정보
FQBN = "arduino:avr:uno"
FOLDER_NAME = "arduino_bowcar"
FILE_NAME = "arduino_bowcar.ino"

# 음계 매핑(옥타브 별)
tones = [
  [ 33, 35, 37, 39, 41, 44, 46, 49, 52, 55, 58, 62 ],
  # 2옥타브: C2 ~ B2
  [ 65, 69, 73, 78, 82, 87, 93, 98, 104, 110, 117, 123 ],
  # 3옥타브: C3 ~ B3
  [ 131, 139, 147, 156, 165, 175, 185, 196, 208, 220, 233, 247 ],
  # 4옥타브: C4 ~ B4
  [ 262, 277, 294, 311, 330, 349, 370, 392, 415, 440, 466, 494 ],
  # 5옥타브: C5 ~ B5
  [ 523, 554, 587, 622, 659, 698, 740, 784, 831, 880, 932, 988 ],
  # 6옥타브: C6 ~ B6
  [ 1047, 1109, 1175, 1245, 1319, 1397, 1480, 1568, 1661, 1760, 1865, 1976 ]
]

# 음계 매핑 딕셔너리
SCALE_MAPPING = {
    "C0": 0, "C#": 1, "D0": 2, "D#": 3, "E0": 4, "F0": 5, "F#": 6,
    "G0": 7, "G#": 8, "A0": 9, "A#": 10, "B0": 11
}

class UploadBowCar(BowCarBase):
    """
    파이썬 코드를 아두이노 C++ 코드로 생성하고 업로드하는 클래스입니다.
    """
    def __init__(self):
        self.includes:set[str] = set()    # #include 문
        self.definitions:set[str] = set() # #define 문
        self.globals:set[str] = set()     # 전역 변수/객체 선언
        self.declarations:set[str] = set() # 기타 전역 선언 (함수 등)
        self.setup_code:str = ""      # setup() 블록에 들어갈 코드
        self.loop_code:str = ""       # loop() 블록에 들어갈 코드
        self._indent_level:int = 1    # 코드 구조를 위한 들여쓰기 수준
        print("코드 생성 모드로 시작합니다.")

    def _get_indent(self):
        """현재 들여쓰기 수준에 맞는 공백을 반환합니다."""
        return "  " * self._indent_level

    # --- 범용 컨텍스트 매니저 ---
    class _BlockManager:
        def __init__(self, car_instance: 'UploadBowCar', open_clause:str):
            self.car = car_instance
            self.open_clause = open_clause

        def __enter__(self):
            self.car.loop_code += f"{self.car._get_indent()}{self.open_clause} {{\n"
            self.car._indent_level += 1

        def __exit__(self, exc_type: Optional[Type[BaseException]],
                    exc_val:Optional[BaseException],
                    exc_tb:object):
            self.car._indent_level -= 1
            self.car.loop_code += f"{self.car._get_indent()}}}\n"
            return False

    # --- 사용자 호출 메소드 (BowCarBase 구현) ---

    def _add_pin_mode(self, pin_name:str, mode:str):
        """pinMode 코드를 setup_code에 추가합니다 (중복 방지)."""
        pin_mode_line = f"  pinMode({pin_name}, {mode});\n"
        if pin_mode_line not in self.setup_code:
            self.setup_code += pin_mode_line
    
    def _add_value(self, type:str, name:str, initial_val=None): #type:ignore
        """
        전역 변수 선언을 중복 없이 추가합니다.
        예: _add_value("int", "sensorValue", 0) -> "int sensorValue = 0;"
        """
        command = f"{type} {name}"
        if initial_val is not None:
            command += f" = {initial_val}"
        command += ";"

        self.declarations.add(command)
    
    def red(self, status: str):
        self._add_pin_mode("RED_LED_PIN", "OUTPUT")
        if status == 'on':
            self.loop_code += f"{self._get_indent()}digitalWrite(RED_LED_PIN, HIGH);\n"
        elif status == 'off':
            self.loop_code += f"{self._get_indent()}digitalWrite(RED_LED_PIN, LOW);\n"

    def blue(self, status: str):
        self._add_pin_mode("BLUE_LED_PIN", "OUTPUT")
        if status == 'on':
            self.loop_code += f"{self._get_indent()}digitalWrite(BLUE_LED_PIN, HIGH);\n"
        elif status == 'off':
            self.loop_code += f"{self._get_indent()}digitalWrite(BLUE_LED_PIN, LOW);\n"
        
    def all_light(self, status: str):
        self.red(status)
        self.blue(status)

    def _ensure_neopixel(self):
        """네오픽셀 사용을 위한 선언 및 초기화 코드를 추가합니다."""
        self.includes.add("#include <Adafruit_NeoPixel.h>")
        self.definitions.add("#define NEOPIXEL_PIN 9")
        self.definitions.add("#define NEOPIXEL_COUNT 4")
        self.globals.add("Adafruit_NeoPixel strip(NEOPIXEL_COUNT, NEOPIXEL_PIN, NEO_GRB + NEO_KHZ800);")
        
        if "  strip.begin();" not in self.setup_code:
            self.setup_code += "  strip.begin();\n"
            self.setup_code += "  strip.show();\n"

    # --- 네오픽셀 제어 메소드 ---
    def neopixel(self, index: int, r: int, g: int, b: int):
        self._ensure_neopixel()
        self.loop_code += f"{self._get_indent()}strip.setPixelColor({index}, strip.Color({r}, {g}, {b}));\n"
        self.loop_code += f"{self._get_indent()}strip.show();\n"

    def neopixel_all(self, r: int, g: int, b: int):
        self._ensure_neopixel()
        self.loop_code += f"{self._get_indent()}for(int i=0; i<NEOPIXEL_COUNT; i++) {{ strip.setPixelColor(i, strip.Color({r}, {g}, {b})); }}\n"
        self.loop_code += f"{self._get_indent()}strip.show();\n"

    def neopixel_clear(self):
        self._ensure_neopixel()
        self.loop_code += f"{self._get_indent()}strip.clear();\n"
        self.loop_code += f"{self._get_indent()}strip.show();\n"

    def neopixel_brightness(self, value: int):
        self._ensure_neopixel()
        self.loop_code += f"{self._get_indent()}strip.setBrightness({value});\n"
        self.loop_code += f"{self._get_indent()}strip.show();\n"

    def buzzer(self, status: str, scale: str = "C0", octave: int = 4, note = 0): #type:ignore
        if status == 'on':
            if not 1 <= octave <= 6:
                print(f"오류: 옥타브는 1에서 6 사이여야 합니다. (입력값: {octave})")
                return
            if scale not in SCALE_MAPPING:
                print(f"오류: 음계는 C0~B0 식으로 설정해야 합니다. (입력값: {scale})")
                return
            
            self._add_pin_mode("BUZZER_PIN", "OUTPUT")
            frequency = tones[octave - 1][SCALE_MAPPING[scale]]
            command = f"tone(BUZZER_PIN, {frequency}"
            if note > 0:
                command += f", (float)duration/{note}*0.95"
            command += ");"
            self.loop_code += f"{self._get_indent()}{command}\n"
        elif status == 'off':
             self.loop_code += f"{self._get_indent()}noTone(BUZZER_PIN);\n"

    def set_duration(self, time:int=2000):
        self._add_value("int", "duration", 2000)
        self.loop_code += f"{self._get_indent()}duration = {time};\n"

    def motor(self, left: int, right: int):
        # Left Motor
        left_dir = '0' if left >= 0 else '1'
        left_speed = abs(left)
        self._add_pin_mode("LM_DIR_PIN", "OUTPUT")
        self._add_pin_mode("LM_PWM_PIN", "OUTPUT")
        self.loop_code += f"{self._get_indent()}digitalWrite(LM_DIR_PIN, {left_dir});\n"
        self.loop_code += f"{self._get_indent()}analogWrite(LM_PWM_PIN, {left_speed});\n"

        # Right Motor
        right_dir = '0' if right >= 0 else '1'
        right_speed = abs(right)
        self._add_pin_mode("RM_DIR_PIN", "OUTPUT")
        self._add_pin_mode("RM_PWM_PIN", "OUTPUT")
        self.loop_code += f"{self._get_indent()}digitalWrite(RM_DIR_PIN, {right_dir});\n"
        self.loop_code += f"{self._get_indent()}analogWrite(RM_PWM_PIN, {right_speed});\n"

    # --- 센서 제어 메소드 (New API) ---
    def is_button_pressed(self, button: str = 'u') -> str:
        pin_map = {'u': "UB_PIN", 'd': "DB_PIN", 'l': "LB_PIN", 'r': "RB_PIN"}
        pin_name = pin_map.get(button, 'UB_PIN')
        self._add_pin_mode(pin_name, "INPUT_PULLUP") # 버튼은 보통 풀업
        return f"(digitalRead({pin_name}) == LOW)"

    def check_light(self, threshold: int = 500, condition: str = '>') -> str:
        self._add_pin_mode("LS_PIN", "INPUT")
        return f"(analogRead(LS_PIN) {condition} {threshold})"

    def check_sound(self, threshold: int = 500, condition: str = '>') -> str:
        self._add_pin_mode("SS_PIN", "INPUT")
        return f"(analogRead(SS_PIN) {condition} {threshold})"

    def check_line(self, dir: str = 'l', threshold: int = 500, condition: str = '>') -> str:
        pin_name = 'IRL_PIN' if dir == 'l' else 'IRR_PIN'
        self._add_pin_mode(pin_name, "INPUT")
        return f"(analogRead({pin_name}) {condition} {threshold})"

    def check_distance(self, threshold: int = 10, condition: str = '<') -> str:
        self._ensure_distance_func()
        return f"(Distance() {condition} {threshold})"

    # --- 센서 값 직접 가져오기 메소드 ---
    def get_light(self) -> str:
        self._add_pin_mode("LS_PIN", "INPUT")
        return "analogRead(LS_PIN)"

    def get_button(self, button: str = 'u') -> str:
        # C++에서는 boolean 표현식이 곧 0/1 정수값으로 쓰일 수 있음.
        # 명시적으로 형변환하거나 삼항연산자를 쓸 수도 있지만, 여기선 boolean 식 반환.
        return self.is_button_pressed(button)

    def get_sound(self) -> str:
        self._add_pin_mode("SS_PIN", "INPUT")
        return "analogRead(SS_PIN)"

    def get_line(self, dir: str = 'l') -> str:
        pin_name = 'IRL_PIN' if dir == 'l' else 'IRR_PIN'
        self._add_pin_mode(pin_name, "INPUT")
        return f"analogRead({pin_name})"

    def get_distance(self) -> str:
        self._ensure_distance_func()
        return "Distance()"

    def _ensure_distance_func(self):
        """초음파 거리 계산 함수가 선언되었는지 확인하고 없으면 추가합니다."""
        self._add_pin_mode("TRIG_PIN","OUTPUT")
        self._add_pin_mode("ECHO_PIN","INPUT")
        
        Dist_Code = '''
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
'''
        self.declarations.add(Dist_Code)

    # --- 제어문 빌더 ---
    def bfor(self, condition: str):
        return self._BlockManager(self, f"for ({condition})")

    def bif(self, condition: str):
        cpp_condition = self._translate_condition(condition)
        return self._BlockManager(self, f"if ({cpp_condition})")

    def belif(self, condition: str):
        cpp_condition = self._translate_condition(condition)
        return self._BlockManager(self, f"else if ({cpp_condition})")

    def belse(self):
        return self._BlockManager(self, "else")
    
    def bwhile(self, condition: str = ""): #type: ignore
        cpp_condition = self._translate_condition(condition)
        return self._BlockManager(self, f"while ({cpp_condition})")

    def _translate_condition(self, condition: str) -> str:
        """파이썬 조건문 문자열을 C++ 형식으로 변환하는 헬퍼 메소드"""
        py_to_cpp_ops = {
            "and": "&&",
            "or": "||",
            "not": "!",
            # True/False도 C++에 맞게 소문자로 변경
            "True": "true", 
            "False": "false"
        }
        # 1. 공백을 기준으로 단어를 분리합니다.
        words = condition.split(' ')
        
        # 2. 각 단어를 확인하며 C++ 연산자로 치환합니다.
        cpp_words = [py_to_cpp_ops.get(word, word) for word in words]
        
        # 3. 다시 하나의 문자열로 합칩니다.
        return ' '.join(cpp_words)

    def delay(self, ms): # type: ignore
        self.loop_code += f"{self._get_indent()}delay({ms});\n"

    def bbreak(self): # 브레이크 설정
        self.loop_code += f"{self._get_indent()}break;\n"

    def set_value(self, type:str = 'int', name:str = 'x', val = None): #type: ignore
        self._add_value(type, name) #type:ignore
        if isinstance(val, str) and len(val) == 1:
            self.loop_code += f"{self._get_indent()}{name} = '{val}';\n"
        else:    
            self.loop_code += f"{self._get_indent()}{name} = {val};\n"

    def set_array(self, type: str, name: str, values: list):
        """
        배열을 선언하고 초기화합니다.
        예: set_array("int", "myArr", [1, 2, 3]) -> "int myArr[] = {1, 2, 3};"
        """
        # 리스트 값을 C++ 배열 초기화 문자열로 변환
        cpp_values = []
        for v in values:
            if isinstance(v, str):
                cpp_values.append(f'"{v}"') # 문자열은 따옴표 추가
            else:
                cpp_values.append(str(v))
        
        init_str = ", ".join(cpp_values)
        command = f"{type} {name}[] = {{{init_str}}};"
        self.declarations.add(command)

    def set_array_value(self, name: str, index: Union[int, str], value):
        """
        배열의 특정 인덱스 값을 변경합니다.
        예: set_array_value("myArr", 0, 10) -> "myArr[0] = 10;"
        """
        val_str = f"'{value}'" if isinstance(value, str) and len(value) == 1 else str(value)
        self.loop_code += f"{self._get_indent()}{name}[{index}] = {val_str};\n"

    # --- 코드 생성 및 업로드 ---
    def get_full_code(self):
        """모든 코드 버퍼를 합쳐 완전한 .ino 코드를 생성합니다."""
        # 여기에 필요한 전역 변수, 핀 번호 등을 추가
        initial_definitions = "// Auto-generated by BowCar\n#include <Arduino.h>\n"
        
        pin_definitions = '''
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

int duration = 2000;
'''
        
        full_code = (
            initial_definitions +
            "\n".join(self.includes) + "\n\n" +
            pin_definitions +
            "\n".join(self.definitions) + "\n" +
            "\n".join(self.globals) + "\n" +
            "\n".join(self.declarations) + "\n\n"
            "void setup() {\n"
            "  Serial.begin(9600);\n"
            + self.setup_code +
            "}\n\n"
            "void loop() {\n"
            + self.loop_code +
            "}\n"
        )
        return full_code

    def upload_code(self):
        """생성된 C++ 코드를 아두이노에 업로드합니다."""
        # 1. 라이브러리 설치 (Adafruit NeoPixel)
        print("필요한 라이브러리를 확인 및 설치합니다...")
        subprocess.run(['arduino-cli', 'lib', 'install', 'Adafruit NeoPixel'], check=False, capture_output=True)

        # 2. 코드 생성
        code = self.get_full_code()
        
        # 3. 임시 디렉토리 생성 및 파일 저장
        with tempfile.TemporaryDirectory() as temp_dir:
            sketch_name = "arduino_bowcar"
            sketch_dir = Path(temp_dir) / sketch_name
            sketch_dir.mkdir()
            
            ino_file = sketch_dir / f"{sketch_name}.ino"
            with open(ino_file, "w", encoding="utf-8") as f:
                f.write(code)
                
            # 4. arduino-cli를 사용하여 컴파일 및 업로드
            print(f"'{ino_file}' 파일 생성 완료!")
            print("코드 컴파일 및 업로드 시작...")
            
            # 아두이노 포트 찾기 (LiveBowCar의 로직 재사용 또는 간단히 구현)
            port = self._find_arduino_port()
            if not port:
                print("아두이노를 찾을 수 없습니다.")
                return

            command = [
                'arduino-cli', 'compile', '--upload',
                '--port', port,
                '--fqbn', 'arduino:avr:uno',
                str(sketch_dir)
            ]
            
            try:
                subprocess.run(command, check=True, capture_output=True, text=True, encoding='utf-8')
                print("코드 업로드 성공! Code upload successful!")
                
                # (선택 사항) 생성된 코드를 현재 디렉토리에도 저장하여 사용자가 볼 수 있게 함
                local_sketch_dir = Path(sketch_name)
                if not local_sketch_dir.exists():
                    local_sketch_dir.mkdir()
                shutil.copy(ino_file, local_sketch_dir / f"{sketch_name}.ino")
                
            except subprocess.CalledProcessError as e:
                print(f"코드 업로드 실패:\n{e.stderr}")
            except Exception as e:
                print(f"업로드 중 오류 발생: {e}")

    def _find_arduino_port(self):
        """아두이노 포트를 찾아 반환하고, 없으면 None을 반환합니다."""
        ports = serial.tools.list_ports.comports()
        for port in ports:
            if 'Arduino' in port.description or 'CH340' in port.description:
                print(f"아두이노 발견: {port.device}")
                return port.device
        print('아두이노를 찾을 수 없습니다!')
        return None