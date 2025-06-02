import pyaudio
import wave
import time
import datetime # time 모듈 대신 datetime을 사용하여 좀 더 명확한 날짜/시간 객체 활용
import os
import sys # sys.stdout.flush() 를 위해 (선택적)

# --- 전역 상수 ---
FORMAT = pyaudio.paInt16  # 샘플 포맷 (16비트 정수)
CHANNELS = 1             # 채널 수 (모노)
RATE = 44100             # 샘플링 레이트 (Hz)
CHUNK = 1024             # 한 번에 읽어올 오디오 프레임(샘플) 수
RECORD_SECONDS = 5       # 기본 녹음 시간 (초) - 필요에 따라 조절 가능
RECORDS_DIR = "records"  # 녹음 파일을 저장할 하위 폴더 이름

def record_audio_to_file(filename: str, duration: int = RECORD_SECONDS) -> bool:
    """
    지정된 시간(duration) 동안 마이크에서 오디오를 녹음하여
    지정된 파일 이름(filename)으로 WAV 파일을 저장합니다.

    Args:
        filename (str): 저장될 WAV 파일의 전체 경로 및 이름.
        duration (int, optional): 녹음할 시간(초). 기본값은 RECORD_SECONDS.

    Returns:
        bool: 성공적으로 녹음 및 저장했으면 True, 아니면 False.
    """
    audio = pyaudio.PyAudio()

    # 녹음을 위한 오디오 스트림 열기
    stream = None  # stream 변수 초기화
    try:
        stream = audio.open(format=FORMAT,
                            channels=CHANNELS,
                            rate=RATE,
                            input=True, # 마이크 입력 스트림
                            frames_per_buffer=CHUNK)
    except Exception as e:
        print(f"오디오 스트림을 여는 중 오류 발생: {e}")
        print("사용 가능한 마이크가 있는지, 권한이 있는지 확인해주세요.")
        audio.terminate() # PyAudio 종료
        return False

    print(f"{duration}초 동안 녹음을 시작합니다... (파일: {filename})")
    frames = [] # 녹음된 오디오 데이터를 저장할 리스트

    # 지정된 시간 동안 스트림에서 데이터 읽기 (녹음)
    for i in range(0, int(RATE / CHUNK * duration)):
        try:
            data = stream.read(CHUNK)
            frames.append(data)
        except IOError as ex:
            # 스트림 읽기 중 I/O 오류 (예: 너무 많은 오버플로우)
            print(f"녹음 중 스트림 읽기 오류: {ex} - 녹음을 중단합니다.")
            # 이미 녹음된 부분이라도 저장 시도
            break 
        except Exception as e:
            print(f"녹음 중 예상치 못한 오류: {e} - 녹음을 중단합니다.")
            break


    print("녹음 완료.")

    # 스트림 중지 및 닫기, PyAudio 종료
    try:
        if stream and stream.is_active(): # stream이 None이 아니고 활성화 상태일 때만
            stream.stop_stream()
        if stream:
            stream.close()
    except Exception as e:
        print(f"오디오 스트림을 닫는 중 오류 발생: {e}")
    finally: # try 블록 실행 후 항상 실행됨 (오류 발생 여부와 관계없이)
        audio.terminate()


    # records 폴더가 없으면 생성
    if not os.path.exists(RECORDS_DIR):
        try:
            os.makedirs(RECORDS_DIR)
            print(f"'{RECORDS_DIR}' 폴더를 생성했습니다.")
        except OSError as e:
            print(f"'{RECORDS_DIR}' 폴더 생성 중 오류 발생: {e}")
            return False # 폴더 생성 실패 시 저장 불가

    # WAV 파일로 저장 (파일 경로는 RECORDS_DIR 포함)
    full_filepath = os.path.join(RECORDS_DIR, filename)
    
    if not frames: # 녹음된 데이터가 없는 경우
        print("녹음된 데이터가 없어 파일을 저장하지 않습니다.")
        return False

    try:
        with wave.open(full_filepath, 'wb') as wf:
            wf.setnchannels(CHANNELS)            # 채널 수 설정
            wf.setsampwidth(audio.get_sample_size(FORMAT)) # 샘플 너비(바이트 단위) 설정
            wf.setframerate(RATE)                # 샘플링 레이트 설정
            wf.writeframes(b''.join(frames))     # 모든 프레임(데이터 덩어리)을 하나로 합쳐서 씀
        print(f"녹음된 파일이 '{full_filepath}'로 저장되었습니다.")
        return True
    except wave.Error as e:
        print(f"WAV 파일 저장 중 오류 발생 (wave.Error): {e}")
        return False
    except Exception as e:
        print(f"WAV 파일 저장 중 예상치 못한 오류 발생: {e}")
        return False

def generate_filename() -> str:
    """현재 날짜와 시간을 기준으로 '년월일-시간분초.wav' 형식의 파일 이름을 생성합니다."""
    now = datetime.datetime.now()
    # 예: 20250602-200510.wav
    return now.strftime("%Y%m%d-%H%M%S") + ".wav"

# --- 메인 실행 로직 ---
if __name__ == "__main__":
    print("음성 녹음 프로그램을 시작합니다.")
    
    # 파일 이름 생성 (날짜와 시간 기반)
    output_filename = generate_filename()
    
    # 녹음 시간 설정 (예: 5초)
    # 사용자로부터 입력 받을 수도 있습니다. 예:
    # record_duration = int(input("녹음할 시간을 초 단위로 입력하세요 (예: 5): "))
    record_duration = 5 

    # 음성 녹음 및 파일 저장 함수 호출
    success = record_audio_to_file(output_filename, duration=record_duration)

    if success:
        print("프로그램이 성공적으로 완료되었습니다.")
    else:
        print("프로그램 실행 중 오류가 발생했습니다.")