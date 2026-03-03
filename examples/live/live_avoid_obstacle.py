import sys
import os
import time
import random
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from bowcar import LiveBowCar

def main():
    print("BowCar 실시간 장애물 회피 자율주행 예제입니다.")
    car = LiveBowCar()
    
    if not car.connection or not car.connection.is_open:
        print("연결 실패")
        return

    print("초음파 센서로 장애물을 피하며 돌아다닙니다.")
    print("Ctrl+C를 누르면 즉시 멈추고 종료됩니다.\n")

    try:
        # 무한 루프 자율주행 로직
        while True:
            # 1. 현재 앞에 있는 장애물과의 거리를 확인합니다.
            distance = car.get_distance()
            
            if distance < 15.0: # 15cm 이내에 장애물이 나타나면?
                print(f"\r장애물 감지! (거리: {distance:.1f}cm) 🚨", end="        ")
                # 일단 멈추고 뒤로 살짝 물러납니다.
                car.motor(-150, -150)
                car.red('on')
                time.sleep(0.5) # 0.5초 동안 후진
                
                # 왼쪽 혹은 오른쪽으로 무작위 회전합니다.
                turn_direction = random.choice(['left', 'right'])
                if turn_direction == 'left':
                    car.motor(-100, 100) # 좌회전
                else:
                    car.motor(100, -100) # 우회전
                
                # 랜덤하게 0.5초 ~ 1초 사이 동안 회전하여 방향을 크게 틉니다.
                time.sleep(random.uniform(0.5, 1.0))
                
            else:
                # 장애물이 없으면 안심하고 전진!
                print(f"\r안전 전진 중... (거리: {distance:.1f}cm) 🟢", end="        ")
                car.red('off')
                car.motor(150, 150)
                
            # 센서를 너무 자주 읽으면 응답이 밀릴 수 있어 0.1초 쉬어줍니다.
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\n자율주행을 종료합니다.")
    finally:
        car.red('off')
        car.motor(0, 0)
        car.close()

if __name__ == "__main__":
    main()
