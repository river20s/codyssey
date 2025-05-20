import os
import zipfile


def load_caesar_target_from_zip() -> str | None:
    """
    ../Week_10/password.txt 안의 암호를 사용하여,
    emergency_storage_key.zip 내부에 있는 암호문을 읽어옴.
    
    Returns:
        :str: 읽어온 카이사르 암호 해독 대상 텍스트
        :None: 파일 경로 오류, 암호 오류, 파일 읽기 오류 등
    """
    base_path = os.path.join('..', 'Week_10')

    zip_pw_path = os.path.join(base_path, 'password.txt')
    zip_file_path = os.path.join(base_path, 'emergency_storage_key.zip')

    filename_inside_zip = 'password.txt'

    zip_pw_str = None
    caesar_target_text = None

    # --- '../Week_10/password.txt' 에서 ZIP 파일 암호 가져오기 ---
    try:
        if not os.path.exists(zip_pw_path):
            print(f"오류: ZIP 암호 파일 '{zip_pw_path}'을 찾을 수 없습니다.")
            return None
        with open(zip_pw_path, 'r', encoding='utf-8') as f:
            zip_pw_str = f.read() # strip()으로 공백 제거 할 수 있을 듯, 지금은 X
        
        if not zip_pw_str:
            print(f"오류: ZIP 파일 '{zip_pw_path}'이 비어 있습니다.")
            return None
        # print(f"    -> 로드된 ZIP 암호: '{zip_pw_str}'")

    except FileNotFoundError: # 명시적으로 작성
        print(f"오류: ZIP 암호 파일 '{zip_pw_path}'을 찾을 수 없습니다.")
        return None
    except IOError as e:
        print(f"오류: ZIP 암호 파일'{zip_pw_path}' 읽기 중 오류")
        return None
    except Exception as e:
        print("오류: ZIP 암호 파일 처리 중 예외 발생: {e}")
        return None

    # --- ZIP 파일 열고, ZIP 내부의 password.txt 내용 가져오기
    try:
        if not os.path.exists(zip_file_path):
            print(f"오류: ZIP 파일 '{zip_file_path}'을 찾을 수 없습니다.")
            return None
        
        with zipfile.ZipFile(zip_file_path, 'r') as zf:
            zip_pw_bytes = zip_pw_str.encode('utf-8')

            if filename_inside_zip not in zf.namelist():
                print(f"오류: ZIP 파일 내에 '{filename_inside_zip}' 파일이 없습니다.")
                return None

            content_bytes = zf.read(filename_inside_zip, pwd=zip_pw_bytes)
            caesar_target_text = content_bytes.decode('utf-8')
            # print(f"    -> 로드된 암호문: '{caesar_target_text}'")

    except FileNotFoundError: 
        print(f"오류: ZIP 파일 내에 '{filename_inside_zip}' 파일이 없습니다.")
        return None
    except zipfile.BadZipFile:
        print(f"오류: '{filename_inside_zip}'은 유효한 ZIP 파일이 아니거나 손상되었을 수 있습니다.")
        return None
    except RuntimeError as e:
        print(f"오류: ZIP 파일 '{filename_inside_zip}'의 암호가 틀렸거나 파일을 열 수 없습니다. (사용된 암호: '{zip_pw_str}') 오류: {e}")
        return None
    except KeyError:
        print(f"오류: ZIP 파일 내에 '{filename_inside_zip}' 파일이 없습니다 (KeyError).")
        return None
    except Exception as e:
        print(f"오류: ZIP 파일에서 내용 추출 중 알 수 없는 예외 발생: {e}")
        return None   

    if caesar_target_text is not None:
        # print("암호문 로딩 성공")
        return caesar_target_text
    else:
        print("암호문을 가져오지 못했습니다.")
        return None


def caesar_cipher_decode(target_text: str, key: int) -> str:
    """
    :target_text:
    :key:

    Return:
        :str:

    """
    # 해독된 문자들을 저장할 빈 리스트를 준비 (나중에 "".join())
    # 입력된 target_text의 각 문자 char에 대해 
    # a. char 가 대문자라면
    # a.1. char를 0-25 사이 숫자로 변환
    # a.2. char를 평문 해석 
    # a.3. 결과를 알파벳으로 변환
    # b. char 가 소문자라면 (위 1~3)
    # c. char가 알파벳이 아니라면 변경하지 않고 그대로 리스트에 추가
    # 반복 끝나면 결과 리스트 문자열 하나의 문자열로 합쳐서 반환

    decrypted_list = []

    for char_in_text in target_text:
        if char_in_text.isupper():
            crypto_numeric = ord(char_in_text) - ord('A')
            plain_numeric = (crypto_numeric - key + 26) % 26
            plain_char = chr(plain_numeric + ord('A'))
            decrypted_list.append(plain_char)
        
        elif char_in_text.islower():
            crypto_numeric = ord(char_in_text) - ord('a')
            plain_numeric = (crypto_numeric - key + 26) % 26
            plain_char = chr(plain_numeric + ord('a'))
            decrypted_list.append(plain_char)
        
        else:
            decrypted_list.append(char_in_text)

    return "".join(decrypted_list)


# --- main ---
if __name__ == "__main__":
    target_text = load_caesar_target_from_zip()

    if target_text:
        print("#" * 30)
        print(f"Ciphertext: {target_text}")
        all_plain_text = {}
        for key in range(26):
            plain_text = caesar_cipher_decode(target_text, key)
            all_plain_text[key] = plain_text
            print(f"        Key = {key:02d}--> Plaintext: {plain_text}")

    selected_key = -1
    while True:
        try:
            key_input_str = input("해석된 평문을 만든 key 값: ")
            selected_key = int(key_input_str)
            if 0 <= selected_key <= 25:
                break
            else:
                print("오류: key 값은 0에서 25 사이여야 합니다. 다시 입력해주세요.")
        except ValueError:
            print("오류: 숫자를 입력해주세요.")
        except Exception as e:
            print(f"입력 중 예상치 못한 오류 발생: {e}")

    final_plaintext = all_plain_text.get(selected_key)
    if final_plaintext is not None:
        print(f"\n선택된 Key {selected_key}로 해독된 최종 평문: '{final_plaintext}'")
        output_filename = "result.txt"
        try:
            with open(output_filename, 'w', encoding='utf-8') as f:
                f.write(final_plaintext)
        except IOError as e:
            print(f"오류: {output_filename} 파일에 평문 저장 중 I/O 오류 발생")
        except Exception as e:
            print(f"오류: 파일 저장 중 예외 발생 {e}")
    else:
        print(f"오류: 선택된 key에 해당되는 해독된 텍스트 찾을 수 없음")
else:
    print("암호문을 가져오는 데 실패했습니다.")

    




