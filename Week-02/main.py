def main():
    # 로그 파일의 경로를 지정함
    log_path = 'mission_computer_main.log'
    # 문제가 되는 로그를 별도로 저장하기 위한 경로를 지정함
    output_path = 'major_issues.log'
    
    try:
        # 로그 파일을 열고 읽음
        with open(log_path, encoding = 'utf-8') as log_file:
            log_content = log_file.read()
            # 로그 파일이 열렸음을 알리는 메시지 출력
            print(f"파일 열림: {log_path}\n")
            # 보너스 과제 수행을 위해 로그 파일 내용을 시간 역순으로 출력
            log_lines = log_content.splitlines()
            header = log_lines[0] # 첫 번째 줄은 헤더로 저장
            log_lines = log_lines[1:] # 헤더를 제외한 나머지 줄
            reversed_log_content = "\n".join(log_lines[::-1])

            # 상위 3개의 문제가 되는 로그를 추출함
            major_issues_lines = log_lines[:3]
            major_issues_content = "\n".join(major_issues_lines)

            print(header) # 헤더 출력
            print(reversed_log_content) # 시간 역순으로 로그 내용 출력

            # 상위 3개의 문제가 되는 로그를 별도 파일에 저장함
            with open(output_path, 'w', encoding = 'utf-8') as output_file:
                output_file.write(header + '\n' + major_issues_content)
                print(f"\n파일 저장됨: {output_path}")
            
    except FileNotFoundError:
        # 파일이 없는 경우 에러 메시지 출력
        print(f'파일을 찾을 수 없습니다: {log_path}')
    except Exception as e:
        # 기타 예외 발생 시 에러 메시지 출력
        print(f'에러가 발생했습니다: {e}')

if __name__ == '__main__':
    main()
