import sys
import os
import time
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from bowcar import LiveBowCar

def main():
    print("BowCar 실시간 센서 모니터링 예제입니다.")
    car = LiveBowCar()
    
    if not car.connection or not car.connection.is_open:
        print("연결 실패")
        return

    print("초음파 거리 센서와 조도 센서 값을 실시간으로 읽어옵니다.")
    print("Ctrl+C를 누르면 종료됩니다.\n")

    try:
        while True:
            distance = car.get_distance()
            light = car.get_light()
            
            dist_bar = "█" * int(min(distance, 50) / 2)
            light_bar = "☼" * int(light / 50)
            
            print(f"\r거리: {distance:4.1f}cm | {dist_bar:<25} || 조도: {light:4d} | {light_bar:<20}", end="")
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\n\n모니터링을 종료합니다.")
    finally:
        car.close()

if __name__ == "__main__":
    main()
