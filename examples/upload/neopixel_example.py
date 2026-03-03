import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from bowcar import UploadBowCar

def main():
    print("BowCar 네오픽셀 제어 예제입니다.")
    car = UploadBowCar()

    # 1. 초기화 (모든 네오픽셀 끄기)
    car.neopixel_clear()
    car.delay(1000)

    # 2. 모든 네오픽셀 색상 동시 변경 (빨강 -> 초록 -> 파랑)
    car.neopixel_all(255, 0, 0)  # 빨간색 (Red)
    car.delay(1000)
    
    car.neopixel_all(0, 255, 0)  # 초록색 (Green)
    car.delay(1000)
    
    car.neopixel_all(0, 0, 255)  # 파란색 (Blue)
    car.delay(1000)

    # 3. 개별 네오픽셀 제어 (0번부터 3번까지 총 4개)
    car.neopixel_clear()
    car.delay(500)
    
    car.neopixel(0, 255, 0, 0)    # 0번 LED: 빨강
    car.delay(500)
    car.neopixel(1, 0, 255, 0)    # 1번 LED: 초록
    car.delay(500)
    car.neopixel(2, 0, 0, 255)    # 2번 LED: 파랑
    car.delay(500)
    car.neopixel(3, 255, 255, 255)# 3번 LED: 흰색
    car.delay(1000)

    # 4. 밝기 조절 (0 ~ 255)
    car.neopixel_all(255, 255, 255) # 전체 흰색으로 설정
    car.neopixel_brightness(30)     # 밝기를 30으로 (어둡게)
    car.delay(1000)
    
    car.neopixel_brightness(255)    # 밝기를 255로 (가장 밝게)
    car.delay(1000)

    # 5. 마무리 소등
    car.neopixel_clear()

    # 생성된 C++ 코드를 아두이노로 업로드합니다.
    print("코드를 아두이노에 업로드합니다...")
    car.upload_code()
    print("완료!")

if __name__ == "__main__":
    main()
