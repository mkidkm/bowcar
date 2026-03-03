import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from bowcar import UploadBowCar

def main():
    print("BowCar 적외선 라인 트레이서 예제입니다.")
    car = UploadBowCar()

    # 초보자 교육용: 검은(또는 어두운) 선을 따라가는 라인 트레이서 자율주행
    # 주의: 센서 특성에 따라 임계값(현재 500)을 검은색 측정값에 맞게 조절해야 합니다.
    
    line_threshold = 500 # 선을 인식하는 기준값
    
    with car.bwhile("True"):
        # 왼쪽, 오른쪽 센서의 감지 조건을 문자열 조건문으로 가져옵니다.
        # check_line('l', 500, '>') -> "(analogRead(IRL_PIN) > 500)"
        left_on_line = car.check_line('l', line_threshold, '>')
        right_on_line = car.check_line('r', line_threshold, '>')
        
        left_off_line = car.check_line('l', line_threshold, '<')
        right_off_line = car.check_line('r', line_threshold, '<')
        
        # 1. 왼쪽 센서만 선을 밟았을 때 (오른쪽으로 벗어남) -> 좌회전으로 복귀
        with car.bif(f"{left_on_line} && {right_off_line}"):
            car.motor(-100, 150) # 왼쪽 바퀴는 뒤로, 오른쪽 바퀴는 앞으로 (빠른 좌회전)
            
        # 2. 오른쪽 센서만 선을 밟았을 때 (왼쪽으로 벗어남) -> 우회전으로 복귀
        with car.belif(f"{left_off_line} && {right_on_line}"):
            car.motor(150, -100) # 우회전
            
        # 3. 양쪽 다 선 위에 있거나(교차로), 둘 다 선을 벗어난 경우 -> 직진
        with car.belse():
            car.motor(100, 100) # 안정적인 속도로 전진
            
    # 생성된 C++ 코드를 바우카에 업로드합니다.
    print("코드를 바우카에 업로드합니다...")
    car.upload_code()
    print("완료!")

if __name__ == "__main__":
    main()
