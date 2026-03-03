import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from bowcar import UploadBowCar

def main():
    print("BowCar 스마트 주행 (센서 활용) 예제입니다.")
    car = UploadBowCar()

    # 초보자 교육용: 센서값에 따라 다르게 움직이는 스마트 자동차 만들기
    
    # 무한히 반복하기
    with car.bwhile("True"):
        
        # 1. 앞에 장애물이 나타나면? (초음파 거리 센서가 15cm 보다 작으면)
        with car.bif(car.check_distance(15, '<')):
            car.motor(0, 0)         # 모터를 정지하고
            car.all_light('on')     # 모든 LED에 불을 켭니다 (위험 알림)
            car.buzzer('on', 'C0', 4, 2) # 버저에서 '도' 소리를 냅니다
        
        # 2. 터널처럼 어두운 곳에 들어가면? (조도 센서 값이 300 보다 작으면)
        with car.belif(car.check_light(300, '<')):
            car.red('on')           # 헤드라이트(빨간 LED)를 켭니다
            car.motor(100, 100)     # 조심스럽게(속도 100) 앞으로 갑니다
        
        # 3. 평상시 상태 (장애물도 없고 밝을 때)
        with car.belse():
            car.all_light('off')    # 불을 끄고
            car.buzzer('off')       # 소리도 끄고
            car.motor(150, 150)     # 정상 속도로 계속 전진합니다
            
    # 생성된 C++ 코드를 아두이노로 업로드합니다.
    print("코드를 아두이노에 업로드합니다...")
    car.upload_code()
    print("완료!")

if __name__ == "__main__":
    main()
