import pyaudio
import wave
import time
import datetime 
import os
import sys 
import speech_recognition as sr
import csv


FORMAT = pyaudio.paInt16 
CHANNELS = 1             
RATE = 44100             
CHUNK = 1024             
RECORD_SECONDS = 5       
RECORDS_DIR = "records"  

def record_audio_to_file(filename: str, duration: int = RECORD_SECONDS) -> bool:
    """
    Args:
        filename (str): 저장될 WAV 파일의 전체 경로 및 이름
        duration (int, optional): 녹음할 시간(초), 기본값은 RECORD_SECONDS

    Returns:
        bool: 성공적으로 녹음 및 저장했으면 True, 아니면 False
    """
    audio = pyaudio.PyAudio()
    
    stream = None  
    try:
        stream = audio.open(format=FORMAT,
                            channels=CHANNELS,
                            rate=RATE,
                            input=True, 
                            frames_per_buffer=CHUNK)
    except Exception as e:
        print(f"오디오 스트림을 여는 중 오류 발생: {e}")
        print("사용 가능한 마이크가 있는지, 권한이 있는지 확인해주세요.")
        audio.terminate()
        return False

    print(f"{duration}초 동안 녹음을 시작합니다... (파일: {filename})")
    frames = [] 

    for i in range(0, int(RATE / CHUNK * duration)):
        try:
            data = stream.read(CHUNK)
            frames.append(data)
        except IOError as ex:
    
            print(f"녹음 중 스트림 읽기 오류: {ex} - 녹음을 중단합니다.")
    
            break 
        except Exception as e:
            print(f"녹음 중 예상치 못한 오류: {e} - 녹음을 중단합니다.")
            break


    print("녹음 완료.")

    try:
        if stream and stream.is_active(): 
            stream.stop_stream()
        if stream:
            stream.close()
    except Exception as e:
        print(f"오디오 스트림을 닫는 중 오류 발생: {e}")
    finally: 
        audio.terminate()


    if not os.path.exists(RECORDS_DIR):
        try:
            os.makedirs(RECORDS_DIR)
            print(f"'{RECORDS_DIR}' 폴더를 생성했습니다.")
        except OSError as e:
            print(f"'{RECORDS_DIR}' 폴더 생성 중 오류 발생: {e}")
            return False 
        
    full_filepath = os.path.join(RECORDS_DIR, filename)
    
    if not frames:

        print("녹음된 데이터가 없어 파일을 저장하지 않습니다.")
        return False

    try:
        with wave.open(full_filepath, 'wb') as wf:
            wf.setnchannels(CHANNELS)  
            wf.setsampwidth(audio.get_sample_size(FORMAT)) 
            wf.setframerate(RATE)                
            wf.writeframes(b''.join(frames))   
        print(f"녹음된 파일이 '{full_filepath}'로 저장되었습니다.")
        return True
    except wave.Error as e:
        print(f"WAV 파일 저장 중 오류 발생 (wave.Error): {e}")
        return False
    except Exception as e:
        print(f"WAV 파일 저장 중 예상치 못한 오류 발생: {e}")
        return False

def generate_filename() -> str:
    now = datetime.datetime.now()
    
    return now.strftime("%Y%m%d-%H%M%S") + ".wav"

def transcribe_audio_file(wav_filepath: str) -> str | None:
    """
    Args:
        wav_filepath (str): 변환할 WAV 파일의 경로

    Returns:
        str | None: 성공 시 변환된 텍스트를, 실패 시 None을 반환
    """
    recognizer = sr.Recognizer()

    try:
        with sr.AudioFile(wav_filepath) as source:
            audio_data = recognizer.record(source)
    except FileNotFoundError:
        print(f"오류: STT 대상 파일 '{wav_filepath}'을 찾을 수 없습니다.")
        return None
    except Exception as e:
        print(f"오류: 오디오 파일 '{wav_filepath}' 처리 중 문제 발생: {e}")
        return None

    try:
        print(f"'{os.path.basename(wav_filepath)}' 파일의 음성을 인식하는 중...")
        text = recognizer.recognize_google(audio_data, language='ko-KR')
        print("  -> 인식 성공!")
        return text
    except sr.UnknownValueError:
        print("  -> 오류: Google Speech Recognition이 음성을 이해할 수 없습니다.")
        return "[음성 인식 실패]"
    except sr.RequestError as e:
        print(f"  -> 오류: Google Speech Recognition 서비스에 요청할 수 없습니다; {e}")
        return "[API 요청 오류]"
    except Exception as e:
        print(f"  -> 오류: 음성 인식 중 알 수 없는 오류 발생: {e}")
        return "[알 수 없는 오류]"


def process_and_save_all_recordings():
    if not os.path.exists(RECORDS_DIR):
        print(f"오류: 녹음 파일이 저장된 '{RECORDS_DIR}' 폴더를 찾을 수 없습니다.")
        return

    wav_files = [f for f in os.listdir(RECORDS_DIR) if f.endswith('.wav')]
    if not wav_files:
        print(f"'{RECORDS_DIR}' 폴더에 처리할 녹음 파일(.wav)이 없습니다.")
        return
        
    print(f"\n총 {len(wav_files)}개의 녹음 파일에 대한 STT 작업을 시작합니다...")

    for wav_file in wav_files:
        full_wav_path = os.path.join(RECORDS_DIR, wav_file)
        
        transcribed_text = transcribe_audio_file(full_wav_path)
        
        if transcribed_text is not None:
            csv_filename = os.path.splitext(wav_file)[0] + '.csv'
            full_csv_path = os.path.join(RECORDS_DIR, csv_filename)
            
            try:
                with open(full_csv_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
                    csv_writer = csv.writer(csvfile)
                    csv_writer.writerow(['timestamp', 'text'])
                    csv_writer.writerow(['00:00:00', transcribed_text])
                
                print(f"  -> 인식된 텍스트를 '{full_csv_path}'에 저장했습니다.")
            except IOError as e:
                print(f"오류: CSV 파일 '{full_csv_path}' 저장 중 오류 발생: {e}")
            except Exception as e:
                print(f"오류: CSV 파일 저장 중 알 수 없는 오류 발생: {e}")
        print("-" * 20)


def search_keyword_in_transcripts(keyword: str):
    print(f"\n--- 키워드 '{keyword}' 검색 결과 ---")
    found_count = 0
    if not os.path.exists(RECORDS_DIR):
        print(f"오류: '{RECORDS_DIR}' 폴더를 찾을 수 없습니다.")
        return

    csv_files = [f for f in os.listdir(RECORDS_DIR) if f.endswith('.csv')]
    if not csv_files:
        print("검색할 스크립트(.csv) 파일이 없습니다.")
        return

    for csv_file in csv_files:
        full_csv_path = os.path.join(RECORDS_DIR, csv_file)
        try:
            with open(full_csv_path, 'r', newline='', encoding='utf-8-sig') as csvfile:
                csv_reader = csv.reader(csvfile)
                next(csv_reader) 
                for row in csv_reader:
                    if len(row) >= 2 and keyword.lower() in row[1].lower():
                        print(f"- 파일: '{csv_file}'")
                        print(f"  시간: {row[0]}")
                        print(f"  내용: {row[1]}")
                        found_count += 1
        except Exception as e:
            print(f"오류: '{csv_file}' 파일 읽기 중 오류 발생: {e}")
    
    if found_count == 0:
        print(f"모든 스크립트에서 '{keyword}' 키워드를 찾지 못했습니다.")


if __name__ == "__main__":
    print("음성 녹음 프로그램을 시작합니다.")
    

    output_filename = generate_filename()
    
    record_duration = 5 

    success = record_audio_to_file(output_filename, duration=record_duration)

    if success:
        print("프로그램이 성공적으로 완료되었습니다.")
    else:
        print("프로그램 실행 중 오류가 발생했습니다.")