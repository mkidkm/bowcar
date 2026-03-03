import sys
import os
import time
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from bowcar import LiveBowCar

def main():
    print("BowCar 실시간 제어(Live Mode) 예제입니다.")
    print("바우카가 USB로 연결되어 있어야 합니다.")
    
    car = LiveBowCar()
    
    # [최초 1회 필수] 펌웨어가 안 올라가 있다면 아래 코드를 주석 해제하여 실행하세요:
    # car._upload_firmware()

    if not car.connection or not car.connection.is_open:
        print("바우카 연결에 실패했습니다. 포트를 확인해주세요.")
        return

    print("연결 성공! 실시간 제어를 시작합니다.")

    try:
        # 1. LED 제어 (즉각 반응)
        print("빨간색 LED 켜기")
        car.red('on')
        time.sleep(1) # 파이썬의 time.sleep()을 사용해 대기합니다
        
        print("빨간색 LED 끄고 파란색 켜기")
        car.red('off')
        car.blue('on')
        time.sleep(1)
        
        car.all_light('off')
        
        # 2. 버저 울리기
        print("버저 소리 테스트 (도)")
        car.buzzer('on', 'C0', 4, 4) # 4옥타브 도(C), 4초(박자)
        time.sleep(0.5)
        
        # 3. 실시간 센서값 읽기 (조도 센서)
        print("\n--- 조도 센서 측정 시작 (3초간) ---")
        for i in range(3):
            light_val = car.get_light()
            print(f"{i+1}초: 조도 센서 값 = {light_val}")
            time.sleep(1)
            
        # 4. 모터 제어 (바퀴 회전)
        print("\n모터 전진 (속도 100)")
        car.motor(100, 100)
        time.sleep(2)
        
        print("모터 정지")
        car.motor(0, 0)
        
    except KeyboardInterrupt:
        print("\n사용자에 의해 종료되었습니다.")
    finally:
        car.motor(0, 0)
        car.close()
        print("실시간 제어 종료 완료.")

if __name__ == "__main__":
    main()
