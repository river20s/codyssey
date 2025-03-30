import csv
import os
import datetime
import random

class DummySensor:
    '''더미 센서 클래스'''

    LOG_FILENAME = 'env_log.csv' # 저장할 로그 파일

    def __init__(self):
        self.env_values = {
            'mars_base_internal_temperature': None,    # 화성 기지 내부 온도
            'mars_base_external_temperature': None,    # 화성 기지 외부 온도
            'mars_base_internal_humidity': None,       # 화성 기지 내부 습도
            'mars_base_external_illuminance': None,    # 화성 기지 외부 광량
            'mars_base_internal_co2': None,            # 화성 기지 내부 이산화탄소 농도
            'mars_base_internal_oxygen': None          # 화성 기지 내부 산소 농도
        }
        # 단위 정보 
        self.units = {                                 
            'mars_base_internal_temperature': '°',
            'mars_base_external_temperature': '°',
            'mars_base_internal_humidity': '%',
            'mars_base_external_illuminance': 'W/㎡',
            'mars_base_internal_co2': '%',
            'mars_base_internal_oxygen': '%'
        }
        # 로그 파일이 없으면 헤더 작성
        try:
            if not os.path.exists(self.LOG_FILENAME):
                with open(self.LOG_FILENAME, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(["Timestamp", "Sensor", "Reading"])
        except Exception:
            pass


    def log(self, sensor, reading):
        '''현재 시각과 함께 센서의 값을 CSV 형식으로 기록'''
        try:
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            with open(self.LOG_FILENAME, 'a', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([timestamp, sensor, reading])
        except Exception:
            pass

    def set_env(self):
        '''각 데이터의 값을 범위 내에서 랜덤으로 생성하고 로그 파일에 기록'''
        try:
            self.env_values['mars_base_internal_temperature'] = random.uniform(18, 30)
            self.env_values['mars_base_external_temperature'] = random.uniform(0, 21)
            self.env_values['mars_base_internal_humidity'] = random.uniform(50, 60)
            self.env_values['mars_base_external_illuminance'] = random.uniform(500, 715)
            self.env_values['mars_base_internal_co2'] = random.uniform(0.02, 0.1)
            self.env_values['mars_base_internal_oxygen'] = random.uniform(4, 7)
        except Exception:
            pass

        # env_values의 각 값을 로그 파일에 기록 
        for key, value in self.env_values.items():
            try:
                reading = f"{value:.2f}{self.units[key]}"
                self.log(key, reading)
            except Exception:
                pass

    def get_env(self):
        return self.env_values
    
'''DummySensor의 인스턴스인 ds 객체 생성'''
ds = DummySensor()
try:
    ds.set_env()
except Exception:
    pass
env_data = ds.get_env()
for key, value in env_data.items():
    try:
        print(f'{key}: {value:.2f}{ds.units[key]}')
    except Exception:
        print(f'{key}: {value}')