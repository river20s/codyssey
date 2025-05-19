import zipfile
import itertools
import time
import string
import os
import multiprocessing 

def worker_crack_password(
    zip_filename: str,
    characters_to_try: list, 
    base_characters: str,   
    password_length: int,
    stop_event: multiprocessing.Event, 
    result_queue: multiprocessing.Queue 
) -> None:

    if password_length == 1: # 첫 문자가 곧 전체 암호인 경우
        password_generator = ((char,) for char in characters_to_try)
    elif password_length > 1:

        def generate_passwords_for_worker():         
            remaining_length = password_length - 1
            if remaining_length < 0:
                return

            if remaining_length == 0: 
                 for first_char in characters_to_try:
                    if stop_event.is_set(): return
                    yield (first_char,)
            else:
                for first_char in characters_to_try:
                    if stop_event.is_set(): return
                    
                    for p_tuple in itertools.product(base_characters, repeat=remaining_length):
                        if stop_event.is_set(): return
                        yield (first_char,) + p_tuple
        
        password_generator = generate_passwords_for_worker()

    else: 
        return

    attempts_in_worker = 0
    for pw_tuple in password_generator:
        if stop_event.is_set():
            break # 다른 워커가 암호를 찾았으면 중단

        attempts_in_worker +=1
        current_pw_candidate = "".join(pw_tuple)
        password_bytes = current_pw_candidate.encode('utf-8')

        try:
            with zipfile.ZipFile(zip_filename, 'r') as zf:
                # zf.setpassword(password_bytes)
                # if zf.testzip() is None: 
                #    
                #     if not stop_event.is_set(): # 중복 보고 방지
                #         result_queue.put(current_pw_candidate)
                #         stop_event.set()
                #     break
                
                zf.extractall(pwd=password_bytes)

                if not stop_event.is_set(): # 다른 프로세스가 먼저 결과를 넣지 않았는지 확인
                    result_queue.put(current_pw_candidate)
                    stop_event.set() # 다른 모든 프로세스에게 중지 신호
                break 
        except (RuntimeError, zipfile.BadZipFile, zipfile.zlib.error):
            pass # 잘못된 암호, 다음 시도 계속
        except Exception:
            # 예상치 못한 오류는 일단 무시하고 계속 (실제로는 로깅하거나 처리 필요)
            pass
        

def unlock_zip_parallel(zip_filename: str, password_output_filename: str) -> str | None:
    print(f"'{zip_filename}' 파일의 암호 해독을 병렬로 시작합니다...")
    
    possible_characters = string.ascii_lowercase + string.digits
    password_length = 6 
    
    start_time = time.time()
    found_password = None

    if not os.path.exists(zip_filename):
        print(f"오류: '{zip_filename}'파일을 찾을 수 없습니다.")
        return None 
    
    print(f"암호 대입 시작 시간: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time))}")

    num_processes = os.cpu_count()
    if num_processes is None or num_processes < 1:
        num_processes = 1 
    print(f"사용할 프로세스 수: {num_processes}")

    stop_event = multiprocessing.Event()
    result_queue = multiprocessing.Queue()
    processes = []

    chars_per_process = [[] for _ in range(num_processes)]
    for i, char_val in enumerate(possible_characters):
        chars_per_process[i % num_processes].append(char_val)
    
    total_expected_combinations = len(possible_characters) ** password_length
    print(f"총 {total_expected_combinations:,}개의 암호 조합을 시도합니다 (병렬).")


    for i in range(num_processes):
        if not chars_per_process[i]: 
            continue
        
        # 각 프로세스에 worker_crack_password 함수와 인자들을 전달
        process = multiprocessing.Process(
            target=worker_crack_password, 
            args=(
                zip_filename, 
                chars_per_process[i], # 이 워커가 담당할 첫 번째 문자들
                possible_characters,  # 나머지 자리에 사용될 전체 문자셋
                password_length,      # 전체 암호 길이
                stop_event, 
                result_queue,
            )
        )
        processes.append(process)
        process.start()
    
    while any(p.is_alive() for p in processes) and not stop_event.is_set():
        try:
            # 큐에서 결과를 기다림 (타임아웃 설정 가능)
            found_password = result_queue.get(timeout=1) # 1초마다 체크
            if found_password:
                stop_event.set() # 다른 프로세스들에게 중지 신호
                break
        except multiprocessing.queues.Empty: # 파이썬 버전에 따라 queue.Empty
            # 1초 동안 결과가 없으면 계속 대기 (또는 다른 작업 수행)
            pass 
        except Exception: # 다른 예상치 못한 큐 관련 오류 처리
            break

    for process in processes:
        if process.is_alive():
            process.terminate() 
        process.join(timeout=1) 

    if not found_password:
        while not result_queue.empty():
            pw = result_queue.get_nowait()
            if pw: 
                found_password = pw
                break
                
    end_time = time.time()
    total_elapsed_time = end_time - start_time
    

    if found_password:
        print(f"\n@@@@ 암호 발견 @@@: {found_password}")
        print(f"총 경과 시간: {total_elapsed_time:.2f}초")
        try:
            with open(password_output_filename, 'w') as f:
                f.write(found_password)
            print(f"찾은 암호를 '{password_output_filename}' 파일에 저장했습니다.")
        except IOError:
            print(f"오류: '{password_output_filename}' 파일에 암호를 저장할 수 없습니다.")
        return found_password
    else:
        print(f"\n모든 조합을 시도했지만 암호를 찾지 못했습니다. 총 경과 시간: {total_elapsed_time:.2f}초")
        return None

# --- main ---
if __name__ == "__main__":    
    TARGET_ZIP_FILE = "emergency_storage_key.zip" 
    PASSWORD_FILE = "password.txt"
    
    unlock_zip_parallel(TARGET_ZIP_FILE, PASSWORD_FILE)
