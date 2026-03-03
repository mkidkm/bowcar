import sys
import os
import time
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from bowcar import LiveBowCar

def main():
    print("BowCar 인터랙티브 네오픽셀 예제입니다.")
    car = LiveBowCar()
    
    if not car.connection or not car.connection.is_open:
        print("연결 실패")
        return

    print("조도 센서 값에 따라 네오픽셀 전체 색상이 실시간으로 변합니다.")
    print("센서를 손으로 가려보세요! Ctrl+C를 누르면 종료됩니다.\n")

    try:
        while True:
            light_val = car.get_light()
            
            if light_val < 300:
                print(f"\r현재 밝기: {light_val} (어두움) -> 모닥불 모드 🔥", end="    ")
                car.neopixel_all(255, 50, 0)
            elif light_val < 600:
                print(f"\r현재 밝기: {light_val} (보통) -> 일상 모드 🌿", end="    ")
                car.neopixel_all(100, 255, 0)
            else:
                print(f"\r현재 밝기: {light_val} (밝음) -> 햇빛 모드 ☀️", end="    ")
                car.neopixel_all(0, 150, 255)
            
            time.sleep(0.2)

    except KeyboardInterrupt:
        print("\n종료합니다.")
    finally:
        car.neopixel_clear()
        car.close()

if __name__ == "__main__":
    main()
