import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from bowcar import UploadBowCar

def main():
    print("BowCar 멜로디 연주 및 LED 댄스 예제입니다.")
    car = UploadBowCar()

    # 1. 연주할 음계와 박자를 파이썬 반복문을 사용해 아두이노 코드로 전개
    # 학교종이 땡땡땡 (초반부)
    notes = ["G4", "G4", "A4", "A4", "G4", "G4", "E4"]
    beats = [4, 4, 4, 4, 4, 4, 2] # 4는 4분음표(1박), 2는 2분음표(2박)
    
    car.set_duration(1000)

    # 파이썬 Loop으로 코드를 풀어서 생성하는 방식 (교육용으로 가장 확실함)
    for note, beat in zip(notes, beats):
        car.blue('on')
        car.buzzer('on', note, 4, beat)  # 4옥타브의 음계를 정해진 박자만큼 냅니다
        
        # 멜로디 하나가 끝나면 잠시 쉬고 불 끄기
        car.blue('off')
        car.buzzer('off')
        car.delay(100) # 음 간격 구분

    # 생성된 C++ 코드를 바우카에 업로드합니다.
    print("코드를 바우카에 업로드합니다...")
    car.upload_code()
    print("완료!")

if __name__ == "__main__":
    main()
