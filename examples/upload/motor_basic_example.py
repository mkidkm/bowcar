import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from bowcar import UploadBowCar

def main():
    print("BowCar 모터 주행 기본 예제입니다.")
    car = UploadBowCar()

    # 초보자 교육용: 자동차 전진, 후진, 회전하기
    
    # 1. 2초 동안 앞으로 가기
    car.motor(150, 150)  # 왼쪽 모터 150, 오른쪽 모터 150 속도로 전진
    car.delay(2000)
    
    # 2. 1초 동안 멈추기
    car.motor(0, 0)
    car.delay(1000)
    
    # 3. 2초 동안 뒤로 가기
    car.motor(-150, -150) # 음수(-)를 넣으면 모터가 반대로 돕니다.
    car.delay(2000)
    
    # 4. 제자리 돌기 (우회전)
    car.motor(100, -100)  # 왼쪽 바퀴는 앞으로, 오른쪽 바퀴는 뒤로
    car.delay(1500)       # 1.5초 동안 제자리 회전
    
    # 5. 제자리 돌기 (좌회전)
    car.motor(-100, 100)  # 왼쪽 바퀴는 뒤로, 오른쪽 바퀴는 앞으로
    car.delay(1500)
    
    # 6. 완전히 멈추기
    car.motor(0, 0)

    # 생성된 C++ 코드를 아두이노로 업로드합니다.
    print("코드를 아두이노에 업로드합니다...")
    car.upload_code()
    print("완료!")

if __name__ == "__main__":
    main()
