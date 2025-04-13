import time, platform, os
from Week_04.mars_mission_computer import DummySensor

class MissionComputer:
    def __init__(self):
        # 환경 값 초기화
        self.env_values = {
            'mars_base_internal_temperature': None,
            'mars_base_external_temperature': None,
            'mars_base_internal_humidity': None,
            'mars_base_external_illuminance': None,
            'mars_base_internal_co2': None,
            'mars_base_internal_oxygen': None
        }
        # DummySensor 인스턴스 ds
        self.ds = DummySensor()

    def get_mission_computer_info(self):
        os_name = platform.system() # OS 이름
        os_version = platform.version() 


    def print_json(self, data):
        """
        :param data: JSON 형식으로 출력할 데이터를 담은 딕셔너리
                     각 키는 문자열이며, 값은 None 또는 숫자 등 임의의 타입일 수 있음
        :type data: dict
        :return: None
        :rtype: None

        - 주어진 딕셔너리(data)를 JSON 형식으로 출력함
        - 각 키-값 쌍을 순회하면서, 값이 None이면 "null"으로, 그렇지 않으면 문자열로 변환하여 출력
        - 마지막 항목이 아닌 경우에는 항목 뒤에 쉼표를 붙임
        """
        print('{')
        keys = list(data.keys())
        for i, key in enumerate(keys):
            value = data[key]
            if value is None:
                value_str = 'null'
            else:
                value_str = str(value)
            # 마지막 항목이 아니면 쉼표 추가
            if i < len(keys) - 1:
                print(f'    "{key}": {value_str},')
            else:
                print(f'    "{key}": {value_str}')
        print('}')

    def get_sensor_data(self):
        """
        :return: None
        :rtype: None

        - "TO EXIT, PRESS CTRL+C" 안내 메시지 출력
        - DummySensor의 set_env()와 get_env()를 통해 각 센서 데이터 업데이트
        - 업데이트된 센서 데이터를 self.env_values에 저장하고, 각 센서별 값은 누적 데이터 딕셔너리에 추가
        - 5초마다 현재 센서 데이터를 JSON 형식으로 출력
        - 5분이 경과하면, 누적된 데이터를 기반으로 각 센서의 평균값을 계산하여 JSON 형식으로 출력한 후,
          누적 데이터를 초기화하고 타이머를 재설정
        - 사용자가 Ctrl+C를 누르면 KeyboardInterrupt가 발생하여 루프를 종료하고,
          "SYSTEM STOPPED..." 메시지를 출력
        """
        print('TO EXIT, PRESS CTRL+C')
        # 5분(300초)마다 평균을 계산하기 위한 누적 데이터와 타이머 초기화
        cumulative_data = { key: [] for key in self.env_values }
        start_time = time.time()

        try:
            while True:
                # 센서 데이터 업데이트
                self.ds.set_env()
                sensor_data = self.ds.get_env()
                self.env_values.update(sensor_data)

                # 누적 데이터 저장 (각 센서별)
                for key, value in sensor_data.items():
                    cumulative_data[key].append(value)

                # 센서 데이터 출력 (JSON)
                self.print_json(self.env_values)

                # 5분마다 누적 데이터의 평균값 계산 및 출력
                current_time = time.time()
                if current_time - start_time >= 300:
                    averages = {}
                    for key, values in cumulative_data.items():
                        if values:
                            avg = sum(values) / len(values)
                            averages[key] = avg
                        else:
                            averages[key] = None
                    print('=============== 5 MINUTE AVERAGE VALUES ===============')
                    self.print_json(averages)
                    # 누적 데이터 및 타이머 초기화
                    cumulative_data = { key: [] for key in self.env_values }
                    start_time = current_time

                # 5초 대기
                time.sleep(5)
        except KeyboardInterrupt:
            print('================== SYSTEM STOPPED... ==================')

ms = MissionComputer()
ms.get_sensor_data()
