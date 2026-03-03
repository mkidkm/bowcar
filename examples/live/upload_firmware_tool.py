import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from bowcar import LiveBowCar

def main():
    print("=== BowCar 펌웨어 자동 업로더 ===")
    print("PC와 바우카(아두이노)가 USB 케이블로 연결되어 있어야 합니다.\n")
    
    car = LiveBowCar()
    
    # 펌웨어 강제 업로드 실행
    car._upload_firmware()

    print("\n펌웨어 업로드 과정이 완료되었습니다.")
    print("이제 다른 모든 live 예제 파일들을 정상적으로 실행할 수 있습니다.")

if __name__ == "__main__":
    main()
