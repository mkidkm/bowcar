import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from bowcar import UploadBowCar

def main():
    print("BowCar 소리 감지(박수 소리) 출바알~ 예제입니다.")
    car = UploadBowCar()

    # 초보자 교육용: 마이크(소리) 센서를 이용하여 박수 소리에 반응하여 출발/정지하기
    
    # 자동차의 주행 상태를 저장할 변수를 만듭니다. (0: 정지, 1: 전진)
    car.set_value("int", "is_moving", 0)
    
    with car.bwhile("True"):
        # 소리 센서값이 600 이상이면 아주 큰 소리(박수)가 났다고 판단합니다.
        # 주변 소음에 따라 600이라는 값을 400~800 등으로 변경해야할 수 있습니다.
        with car.bif(car.check_sound(600, '>')):
            # 박수를 치면 현재 상태를 반전시킵니다. (정지 -> 출발 / 출발 -> 정지)
            with car.bif("is_moving == 0"):
                car.set_value("int", "is_moving", 1)  # 출발 상태로 변경
                car.blue('on')                        # 파란불 점등
            with car.belse():
                car.set_value("int", "is_moving", 0)  # 정지 상태로 변경
                car.blue('off')                       # 파란불 소등
                
            # 박수 한번에 코드가 여러번 실행되지 않도록 잠깐 기다려줍니다. (채터링 방지)
            car.delay(500) 
            
        # is_moving 변수 값에 따라 모터 동작시키기
        with car.bif("is_moving == 1"):
            car.motor(150, 150) # 앞으로 전진!
        with car.belse():
            car.motor(0, 0)     # 브레이크!
            
    # 생성된 C++ 코드를 아두이노로 업로드합니다.
    print("코드를 아두이노에 업로드합니다...")
    car.upload_code()
    print("완료!")

if __name__ == "__main__":
    main()
