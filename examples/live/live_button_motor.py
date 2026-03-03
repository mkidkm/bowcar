import sys
import os
import time
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from bowcar import LiveBowCar

def main():
    print("BowCar 바우카 자체 버튼 조종 예제입니다.")
    car = LiveBowCar()
    
    if not car.connection or not car.connection.is_open:
        print("연결 실패")
        return

    print("바우카 위에 있는 4개의 버튼(U, D, L, R)을 눌러보세요.")
    print("누르는 버튼에 따라 모터가 움직입니다.")
    print("Ctrl+C를 누르면 종료됩니다.\n")

    current_state = "stop"

    try:
        while True:
            btn_up = car.is_button_pressed('u')
            btn_down = car.is_button_pressed('d')
            btn_left = car.is_button_pressed('l')
            btn_right = car.is_button_pressed('r')
            
            if btn_up:
                if current_state != "up":
                    print("\r앞으로 전진! ⬆️", end="          ")
                    car.motor(150, 150)
                    current_state = "up"
            elif btn_down:
                if current_state != "down":
                    print("\r뒤로 후진! ⬇️", end="          ")
                    car.motor(-150, -150)
                    current_state = "down"
            elif btn_left:
                if current_state != "left":
                    print("\r좌회전! ⬅️", end="          ")
                    car.motor(-100, 100)
                    current_state = "left"
            elif btn_right:
                if current_state != "right":
                    print("\r우회전! ➡️", end="          ")
                    car.motor(100, -100)
                    current_state = "right"
            else:
                if current_state != "stop":
                    print("\r정지. 🛑", end="             ")
                    car.motor(0, 0)
                    current_state = "stop"

            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\n사용자에 의해 모터 조종 프로그램을 종료합니다.")
    finally:
        car.motor(0, 0)
        car.close()

if __name__ == "__main__":
    main()
