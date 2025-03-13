def main():
    # 로그 파일의 경로를 지정함
    log_path = 'mission_computer_main.log'
    
    try:
        # 로그 파일을 열고 읽음음
        with open(log_path, encoding = 'utf-8') as log_file:
            log_content = log_file.read()
            # 로그 파일이 열렸음을 알리는 메시지 출력
            print(f"파일 열림: {log_path}\n")
            # 로그 파일 내용 출력
            print(log_content)
    except FileNotFoundError:
        # 파일이 없는 경우 에러 메시지 출력
        print(f"파일을 찾을 수 없습니다: {log_path}")
    except Exception as e:
        # 기타 예외 발생 시 에러 메시지 출력력
        print(f"에러가 발생했습니다: {e}")

if __name__ == '__main__':
    main()