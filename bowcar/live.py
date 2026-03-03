import serial
import serial.tools.list_ports
import time
import subprocess
import tempfile
import shutil
import importlib.resources
from pathlib import Path
from typing import Union
from .base import BowCarBase

# 이 클래스에서 사용할 펌웨어 버전 정보
FIRMWARE_VERSION = "1.0.0" 

class LiveBowCar(BowCarBase):
    """
    아두이노와 실시간으로 통신하여 제어하는 클래스입니다.
    객체 생성 시, 시리얼 통신을 시작합니다. (펌웨어 업로드 필요 시 _upload_firmware 별도 호출)
    """
    def __init__(self):
        self.port = self._find_arduino_port()
        self.connection = None
        self.duration = 2000 # 버저 기본 지속 시간
        if self.port:
            self._connect_serial()
        else:
            print("오류: 아두이노를 찾을 수 없습니다. 연결 상태를 확인해주세요.")

    def _find_arduino_port(self):
        """아두이노가 연결된 시리얼 포트를 자동으로 찾습니다."""
        ports = serial.tools.list_ports.comports()
        for port in ports:
            # 아두이노 정품 또는 호환 보드(CH340 드라이버)를 찾습니다.
            if 'Arduino' in port.description or 'CH340' in port.description:
                return port.device
        return None

    def _upload_firmware(self):
        """패키지에 내장된 범용 펌웨어를 아두이노에 업로드합니다."""
        sketch_name = f"bowCarForPython_V{FIRMWARE_VERSION}"
        ino_filename = f"{sketch_name}.ino"
        print(f"'{sketch_name}' 펌웨어 업로드를 시작합니다...")
        
        try:
            self.close() # 기존 연결이 있다면 안전하게 닫습니다.
            time.sleep(1) # 포트가 완전히 닫힐 때까지 대기합니다.

            # 1. 라이브러리 설치 (Adafruit NeoPixel)
            print("필요한 라이브러리를 확인 및 설치합니다...")
            subprocess.run(['arduino-cli', 'lib', 'install', 'Adafruit NeoPixel'], check=False, capture_output=True)

            # 패키지 내 리소스 경로를 찾습니다.
            traversable_path = importlib.resources.files("bowcar.firmware").joinpath(sketch_name, ino_filename)
            with importlib.resources.as_file(traversable_path) as concrete_path:
                with tempfile.TemporaryDirectory() as temp_dir:
                    # arduino-cli는 스케치 파일과 폴더 이름이 같아야 합니다.
                    sketch_subdir = Path(temp_dir) / sketch_name
                    sketch_subdir.mkdir()
                    shutil.copy(concrete_path, sketch_subdir)
                    
                    command = [
                        'arduino-cli', 'compile', '--upload', 
                        '--port', str(self.port),
                        '--fqbn', 'arduino:avr:uno',
                        str(sketch_subdir)
                    ]
                    
                    subprocess.run(command, check=True, capture_output=True, text=True, encoding='utf-8')
                    print("펌웨어 업로드 성공! 1초 후 재연결을 시도합니다.")
                    time.sleep(1)
                    self._connect_serial()
        except (ModuleNotFoundError, FileNotFoundError):
            print("오류: 패키지 또는 펌웨어 파일을 찾을 수 없습니다. 설치 상태를 확인해주세요.")
        except subprocess.CalledProcessError as e:
            print(f"펌웨어 업로드 실패: {e}\n{e.stderr}")
        except Exception as e:
            print(f"펌웨어 업로드 중 알 수 없는 오류 발생: {e}")

    def _connect_serial(self):
        """시리얼 포트에 연결합니다."""
        try:
            self.connection = serial.Serial(self.port, 9600, timeout=3)
            print(f"시리얼 포트 연결 성공! (port: {self.port})")
            time.sleep(2) # 아두이노 부팅 및 안정화 대기
        except serial.SerialException as e:
            print(f"시리얼 포트 연결 실패: {e}")

    def send_command(self, command: str):
        """아두이노에 시리얼 명령을 보냅니다."""
        if self.connection and self.connection.is_open:
            self.connection.write(f"{command}\n".encode('utf-8'))
        else:
            print("연결되지 않아 명령을 보낼 수 없습니다.")
            
    def _get_sensor_value(self, command: str) -> int:
        """아두이노로부터 정수형 센서 값을 읽어옵니다."""
        if self.connection:
            self.connection.reset_input_buffer()

        self.send_command(command)
        if self.connection:
            try:
                line = self.connection.readline()
                if line:
                    return int(line.decode('utf-8').strip())
            except (ValueError, TypeError):
                return -1 # 잘못된 값이 수신된 경우
        return -1

    def _get_sensor_value_float(self, command: str) -> float:
        """아두이노로부터 실수형 센서 값을 읽어옵니다."""
        if self.connection:
            self.connection.reset_input_buffer()

        self.send_command(command)
        if self.connection:
            try:
                line = self.connection.readline()
                if line:
                    return float(line.decode('utf-8').strip())
            except (ValueError, TypeError):
                return -1.0
        return -1.0

    def close(self):
        """시리얼 연결을 닫습니다."""
        if self.connection and self.connection.is_open:
            self.connection.close()
            print('시리얼 연결을 닫았습니다.')
    
    def _get_condition_type(self, condition: str) -> str:
        """비교 연산자를 펌웨어 프로토콜('u' 또는 'd')로 변환합니다."""
        if condition in ('>', '>='):
            return 'u'
        elif condition in ('<', '<='):
            return 'd'
        else:
            # 기본값 또는 지원하지 않는 연산자는 'u'로 처리 (필요시 수정)
            return 'u'

    # --- BowCarBase 메소드 구현 ---

    def red(self, status: str):
        if status == 'on':
            self.send_command('lrn')
        elif status == 'off':
            self.send_command('lrf')

    def blue(self, status: str):
        if status == 'on':
            self.send_command('lbn')
        elif status == 'off':
            self.send_command('lbf')
        
    def all_light(self, status: str):
        if status == 'on':
            self.send_command('lan')
        elif status == 'off':
            self.send_command('laf')

    # --- 네오픽셀 제어 메소드 ---
    def neopixel(self, index: int, r: int, g: int, b: int):
        # nc[idx][rrr][ggg][bbb]
        command = f'nc{index}{r:03d}{g:03d}{b:03d}'
        self.send_command(command)

    def neopixel_all(self, r: int, g: int, b: int):
        # na[rrr][ggg][bbb]
        command = f'na{r:03d}{g:03d}{b:03d}'
        self.send_command(command)

    def neopixel_clear(self):
        # no
        self.send_command('no')

    def neopixel_brightness(self, value: int):
        # nb[val]
        command = f'nb{value:03d}'
        self.send_command(command)
        
    def buzzer(self, status: str, scale: str = "C0", octave: int = 4, note: int = 4):
        if status == 'on':
            command = f'b{octave}{scale}{note}'
            self.send_command(command)
            # 'live' 모드에서는 파이썬이 직접 기다려야 음 길이를 보장할 수 있습니다.
            if self.duration > 0 and note > 0:
                time.sleep(self.duration / note / 1000.0)
        elif status == 'off':
            self.send_command('bnn')
        
    def set_duration(self, time: int = 2000):
        self.duration = time
        self.send_command(f'sd{time:05d}')

    def motor(self, left: int, right: int):
        # Left Motor
        left_dir = '0' if left >= 0 else '1'
        left_speed = abs(left)
        self.send_command(f'swl{left_dir}')
        self.send_command(f'sml{left_speed:03d}')

        # Right Motor
        right_dir = '0' if right >= 0 else '1'
        right_speed = abs(right)
        self.send_command(f'swr{right_dir}')
        self.send_command(f'smr{right_speed:03d}')

    # --- 센서 제어 메소드 (New API) ---
    def is_button_pressed(self, button: str = 'u') -> bool:
        command = "rb" + button
        return self._get_sensor_value(command) == 1

    def check_light(self, threshold: int = 500, condition: str = '>') -> bool:
        type_char = self._get_condition_type(condition)
        command = "rl" + type_char + f'{threshold}'
        return self._get_sensor_value(command) == 1

    def check_sound(self, threshold: int = 500, condition: str = '>') -> bool:
        type_char = self._get_condition_type(condition)
        command = "rs" + type_char + f'{threshold}'
        return self._get_sensor_value(command) == 1

    def check_line(self, dir: str = 'l', threshold: int = 500, condition: str = '>') -> bool:
        type_char = self._get_condition_type(condition)
        command = "rt" + dir + type_char + f'{threshold}'
        return self._get_sensor_value(command) == 1

    def check_distance(self, threshold: int = 10, condition: str = '<') -> bool:
        type_char = self._get_condition_type(condition)
        command = "rd" + type_char + f'{threshold}'
        return self._get_sensor_value(command) == 1

    # --- 센서 값 직접 가져오기 메소드 ---
    def get_light(self) -> int:
        return self._get_sensor_value("gl")

    def get_button(self, button: str = 'u') -> int:
        # get_button은 현재 펌웨어 프로토콜 상 직접적인 명령어가 없을 수 있음.
        # 기존 코드에서도 get_button은 없었고 is_push만 있었음.
        # 하지만 base.py에 정의되어 있으므로 구현 필요.
        # 임시로 is_button_pressed와 동일하게 구현하거나, 펌웨어 지원 여부 확인 필요.
        # 여기서는 is_button_pressed와 동일하게 1/0 반환으로 구현.
        return 1 if self.is_button_pressed(button) else 0

    def get_sound(self) -> int:
        return self._get_sensor_value("gs")

    def get_line(self, dir: str = 'l') -> int:
        command = "gt" + dir
        return self._get_sensor_value(command)

    def get_distance(self) -> float:
        return self._get_sensor_value_float("gd")
        
    def delay(self, ms: int):
        """파이썬 스크립트를 지정된 시간만큼 멈춥니다."""
        time.sleep(ms / 1000.0)