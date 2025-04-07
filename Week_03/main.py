import csv
import pickle

def read_file(filepath):
    """ 
    Mars_Base_Inventory_List.csv의 내용을 읽어들여 리스트 객체로 저장하여 반환한다.
    T.C = O(n)
    - 파일의 모든 행을 순회하므로 시간 복잡도는 O(n)이다.
    S.C = O(n)
    - 읽은 모든 행을 저장하므로 O(n)이다.
    """
    try:
        with open(filepath, newline='', encoding='utf-8') as csvfile:
            inventory_reader = csv.reader(csvfile, delimiter=',', quotechar='"') # csv 파일의 내용을 읽는 이터레이터
            data = list(inventory_reader) # 파일 내용을 저장하는 리스트 객체
        return data
    except FileNotFoundError:
        print(f'파일을 찾을 수 없습니다: {filepath}')
    except Exception as e:
        print(f'파일을 읽는 중 오류가 발생했습니다: {e}')
    return [] # 오류가 발생하면 빈 리스트 반환
        
def print_file(data, filepath):
    """
    csv 파일의 내용을 출력한다.
    T.C = O(n)
    - 리스트의 각 행을 한 번씩 반복하므로 O(n)이다.
    S.C = O(1)
    - 추가적인 메모리 공간은 없다.
    """
    print('출력:', filepath)
    if not data:
        print('데이터가 없습니다.')
        return
    for row in data:
        print(', '.join(row)) # csv 파일 내용을 출력

def sort_by_flammability(data):
    """
    내용을 flammability가 높은 순서로 정렬하고 data_sorted로 반환한다.
    첫 행은 헤더로 가정한다. 
    T.C = O(n log n)
    - sorted() 함수가 사용하는 Timsort의 시간 복잡도는 O(n log n)이다.
    S.C = O(n)
    - 새로운 리스트를 복사하고 반환하므로 추가적인 메모리 공간이 필요하다.
    """
    header = data[0]
    rows = data[1:]
    try: 
        rows_sorted = sorted(rows, key=lambda row: float(row[4]), reverse=True)
    except Exception as e: 
        print(f'정렬 중 오류 발생: {e}')
        rows_sorted = rows # 오류 발생 시 정렬하지 않음
    return [header] + rows_sorted

def filter_flammability(data, threshold=0.7):
    """
    flammability가 임계점 이상인 항목을 filtered_data로 반환한다.
    첫 행은 헤더로 가정한다.
    T.C = O(n)
    - 헤더와 필터링한 리스트를 합치므로 O(n)이다.
    S.C = O(n)
    - 새로운 리스트를 만들고 헤더와 합쳐 반환하므로 O(n)이다.
    """
    if not data:
        return []
    header = data[0]
    filtered_data = []
    for row in data[1:]:
        try:
            flammability = float(row[4])
            if flammability >= threshold:
                filtered_data.append(row)
        except ValueError: # 'Various'와 같이 숫자로 변환할 수 없는 경우 무시
            pass       
    return [header] + filtered_data

def print_filtered_data(filtered_data, threshold=0.7):
    """
    flammability 값이 임계점보다 높은 항목을 출력한다.
    첫 행은 헤더로 가정한다.
    T.C = O(n)
    - 각 행에 대해 for 루프가 실행된다.
    S.C = O(1)
    - 추가 저장 데이터가 없다.
    """
    print('\n인화성 값이 {} 이상인 항목:'.format(threshold))
    if not filtered_data:
        print('데이터가 없습니다.')
        return
    for row in filtered_data:
        print(', '.join(row))

def save_filtered_csv(filtered_data, csv_filename):
    """
    필터링한 데이터를 CSV 형식으로 저장한다.
    T.C = O(n)
    - 각 행을 한 번씩 기록하므로 O(n)이다.
    S.C = O(1)
    - 함수 내부에서 추가로 사용되는 자료구조는 없다.
    """
    try:
        with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writer.writerows(filtered_data)
            print(f'\n필터링된 CSV 파일 저장함: {csv_filename}')
    except Exception as e:
        print(f'\nCSV 파일 저장 중 오류 발생: {e}')
        
def save_sorted_binary(data_sorted, bin_filename):
    """
    정렬된 데이터 data_sorted를 이진 파일로 저장한다.
    T.C = O(n)
    - 모든 요소를 순회하여 직렬화한다.
    S.C = O(n)
    - 직렬화 과정에서 데이터의 크기에 비례하는 추가 메모리가 사용될 수 있음을 고려한다.
    """
    try:
        with open(bin_filename, 'wb') as bin_flie:
            pickle.dump(data_sorted, bin_flie)
        print(f'\n정렬된 이진 파일 저장 완료: {bin_filename}')
    except Exception as e:
        print(f'\n이진 파일 저장 중 오류 발생: {e}')

def print_binary_file(bin_filename):
    """
    이진 파일 'Mars_Base_Inventory_List.bin'을 읽어와 출력한다.
    pickle 모듈을 사용해 역직렬화 하고
    데이터의 각 행이 리스트임을 가정해 출력한다.
    T.C = O(n)
    - 역직렬화 과정에서 O(n) 시간이 사용된다.
    S.C = O(n)
    - 역직렬화 과정에서 O(n) 공간이 사용된다.
    """
    print('\n출력:', bin_filename)
    try: 
        with open(bin_filename, 'rb') as bin_file:
            data = pickle.load(bin_file)
    except FileNotFoundError:
        print(f'\n이진 파일을 찾을 수 없습니다: {bin_filename}')
        return
    except Exception as e:
        print(f'\n이진 파일 읽기 중 오류 발생: {e}')
        return
    
    if not data:
        print('\n데이터가 없습니다.')
    for row in data:
        print(', '.join(row))

def main():
    filepath = 'Mars_Base_Inventory_List.csv'
    bin_filename = 'Mars_Base_Inventory_List.bin'
    csv_filename = 'Mars_Base_Inventory_danger.csv'

    data = read_file(filepath)
    print_file(data, filepath) # 전체 데이터 출력


    data_sorted = sort_by_flammability(data) # flammability 기준 내림차순으로 데이터 정렬 
    save_sorted_binary(data_sorted, bin_filename) # 정렬한 데이터를 이진 파일로 저장 
    print_binary_file(bin_filename) # 저장한 이진 파일을 출력

    filtered_data = filter_flammability(data, threshold=0.7) # 임계점 기준 데이터 필터링
    print_filtered_data(filtered_data, threshold=0.7) # 필터링 데이터 출력
    save_filtered_csv(filtered_data, csv_filename) # 필터링 데이터 별도 CSV 파일로 저장

if __name__ == '__main__':
    main()