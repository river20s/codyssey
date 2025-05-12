import sys, ast, operator, re
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFontMetrics
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QGridLayout, QLineEdit, QPushButton
)
# >>>--- 계산기 클래스 --->>>
class Calculator:
    def __init__(self):
        """계산기 초기화"""
        self.current_value = 0.0
        self.stored_value = 0.0
        self.operation = None
        self.new_input = True       # 연산자 입력 후 새 숫자를 받을 준비가 되었는가
        self.has_decimal = False
        self.display_text = '0'
        self.result_just_shown = False # 방금 '=', '%' 등으로 결과가 표시되었는가

    def reset(self):
        """계산기 상태 초기화"""
        self.current_value = 0.0
        self.stored_value = 0.0
        self.operation = None
        self.new_input = True
        self.has_decimal = False
        self.display_text = '0'
        self.result_just_shown = False # 플래그 초기화
        return self.format_display(self.display_text)

    def input_number(self, number):
        """숫자 입력 처리"""
        # 결과가 방금 표시된 상태에서 숫자를 누르면 결과에 이어붙이기
        if self.result_just_shown:
            # display_text는 이미 결과값을 가지고 있음
            # '0'일 경우 새로 입력된 숫자로 대체 (05 대신 5)
            if self.display_text == '0' and str(number) != '0':
                self.display_text = str(number)
            # 'Error' 상태였다면 새 숫자로 시작
            elif self.display_text == 'Error':
                self.display_text = str(number)
            elif len(self.display_text) < 20: # 길이 제한
                self.display_text += str(number)

            self.result_just_shown = False   # 이어붙이기 시작했으므로 플래그 해제
            self.new_input = False           # 입력 중이므로 False
        elif self.new_input: # 연산자 입력 후 첫 숫자
            self.display_text = str(number)
            self.new_input = False
        else: # 숫자 입력 중 이어붙이기
            if self.display_text == '0' and str(number) != '0':
                self.display_text = str(number)
            elif self.display_text == '0' and str(number) == '0':
                pass # 0 다음에 0 계속 눌러도 0 유지
            elif len(self.display_text) < 20: # 길이 제한
                self.display_text += str(number)

        self.current_value = float(self.display_text)
        self.has_decimal = '.' in self.display_text
        return self.format_display(self.display_text)

    def input_decimal(self):
        """소수점 입력 처리"""
        # 결과가 방금 표시된 상태에서 '.'을 누르면 결과에 '.을 이어붙임
        if self.result_just_shown:
            if self.display_text == 'Error': # Error 상태였다면 "0."으로 시작
                self.display_text = '0.'
                self.has_decimal = True
            elif not self.has_decimal: # 기존 결과에 소수점이 없으면 추가
                self.display_text += '.'
                self.has_decimal = True
            self.result_just_shown = False # 이어붙이기 시작했으므로 플래그 해제
            self.new_input = False       # 입력 중이므로 False
        elif self.new_input: # 연산자 입력 후 첫 입력이 '.'
            self.display_text = '0.'
            self.new_input = False
            self.has_decimal = True
        elif not self.has_decimal: # 숫자 입력 중 '.' 입력
            if not self.display_text: # 혹시 display_text가 비어있다면
                self.display_text = '0.'
            else:
                self.display_text += '.'
            self.has_decimal = True
        
        # 현재 입력값 업데이트 (소수점만 찍어도 current_value에 반영되도록)
        return self.format_display(self.display_text)

    def _prepare_operation(self, op_name): 
        """연산 준비"""
        # 연속 연산 또는 결과값에 이은 연산 처리
        if self.operation and not self.new_input and not self.result_just_shown:
            self.equal()

        self.stored_value = self.current_value # 현재 표시된 값(결과 또는 입력값)을 저장
        self.operation = op_name
        self.new_input = True    # 다음 숫자 입력을 새 입력으로 받도록 준비
        self.has_decimal = False # 다음 입력은 소수점 없음으로 시작
        self.result_just_shown = False # 연산자 눌렀으니 결과표시 상태는 해제
        return self.format_display(self.display_text)

    def add(self, x=None, y=None):
        self._prepare_operation('add')
        if x is not None and y is not None: return x + y
        return self.format_display(self.display_text)

    def subtract(self, x=None, y=None):
        self._prepare_operation('subtract')
        if x is not None and y is not None: return x - y
        return self.format_display(self.display_text)

    def multiply(self, x=None, y=None):
        self._prepare_operation('multiply')
        if x is not None and y is not None: return x * y
        return self.format_display(self.display_text)

    def divide(self, x=None, y=None):
        self._prepare_operation('divide')
        if x is not None and y is not None:
            if y == 0: return 'Error'
            return x / y
        return self.format_display(self.display_text)

    def equal(self):
        """계산 결과 출력"""
        if not self.operation: # 저장된 연산이 없으면
            self.result_just_shown = True # =만 눌러도 결과 표시 상태로 간주
            return self.format_display(self.display_text)

        calculated_result = 0 # 임시 변수
        try:
            if self.operation == 'add':
                calculated_result = self.stored_value + self.current_value
            elif self.operation == 'subtract':
                calculated_result = self.stored_value - self.current_value
            elif self.operation == 'multiply':
                calculated_result = self.stored_value * self.current_value
            elif self.operation == 'divide':
                if self.current_value == 0:
                    self.reset()
                    self.display_text = 'Error' # 명시적으로 Error 설정
                    return 'Error' # format_display('Error')는 'Error' 반환
                calculated_result = self.stored_value / self.current_value
            else:
                self.result_just_shown = True
                return self.format_display(self.display_text)


            self.current_value = calculated_result
            self.display_text = self._format_result(calculated_result)
            self.operation = None # 연산 완료
            self.new_input = True
            self.result_just_shown = True # 결과가 방금 표시됨
            self.has_decimal = '.' in self.display_text
            return self.format_display(self.display_text)

        except Exception as e:
            self.reset()
            self.display_text = 'Error' # 명시적으로 Error 설정
            return 'Error'

    def negative_positive(self):
        """부호 전환 (양수/음수)"""
        if self.display_text == 'Error':
            return 'Error' # 에러 상태에서는 아무것도 하지 않음
        if self.display_text == '0': # 0은 부호 변경 의미 없음
            return self.format_display(self.display_text)

        if self.display_text.startswith('-'):
            self.display_text = self.display_text[1:]
        else:
            self.display_text = '-' + self.display_text
        self.current_value = float(self.display_text)
        
        # +/- 후에는 결과 상태가 아님, 계속 수정 가능해야 함
        self.result_just_shown = False
        self.new_input = False # +/- 는 현재 입력에 대한 수정이므로 new_input은 False 유지
        return self.format_display(self.display_text)

    def percent(self):
        """퍼센트 연산 (현재 값을 100으로 나눔)"""
        if self.display_text == 'Error':
            return 'Error'
        try:
            self.current_value = float(self.display_text) / 100 # display_text를 기준으로 계산
            self.display_text = self._format_result(self.current_value)
            self.has_decimal = '.' in self.display_text
            self.result_just_shown = True # %도 결과로 취급하여 이어붙이기 가능하도록
            self.new_input = True # % 다음 연산자를 누르면 새 입력 받아야 하므로 True
        except Exception:
            self.reset()
            self.display_text = 'Error'
            return 'Error'
        return self.format_display(self.display_text)

    def _format_result(self, result):
        if isinstance(result, float):
            if result == int(result):
                return str(int(result))
            result_str = f'{result:.6f}'.rstrip('0').rstrip('.')
            return result_str
        return str(result)

    def format_display(self, text):
        try:
            if text == 'Error':
                return text
            sign = ''
            if text.startswith('-'):
                sign = '-'
                text = text[1:]
            parts = text.split('.', 1)
            # 정수 부분에 천 단위 콤마 추가 전에, 정수 부분만 있는지 확인
            if parts[0]: # 정수 부분이 있는 경우
                 # int() 변환 전에 빈 문자열이 아닌지 확인
                if parts[0] == '': # 소수점 앞이 비었으면 0
                    parts[0] = '0'
                parts[0] = f'{int(parts[0]):,}'
            elif len(parts) > 1 : # 정수 부분은 없고 소수점만 있는 경우
                parts[0] = '0'


            if len(parts) > 1:
                return sign + parts[0] + '.' + parts[1]
            return sign + parts[0]
        except Exception: # 포매팅 중 오류 발생 시 원본 텍스트 반환
            return text

# <<<--- 계산기 클래스 ---<<<
# >>>--- UI 클래스 --->>>

class CalculatorUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.calculator = Calculator()  
        self._init_ui()
    
    def _init_ui(self):
        """UI 초기화"""
        self.setWindowTitle('Calculator')
        central = QWidget()
        self.setCentralWidget(central)
        grid = QGridLayout()
        central.setLayout(grid)

        # 결과 표시 영역
        self.display = QLineEdit('0')
        self.display.setReadOnly(True)
        self.display.setAlignment(Qt.AlignRight)
        self.display.setFixedHeight(50)
        grid.addWidget(self.display, 0, 0, 1, 4)

        # 버튼 배치 
        buttons = {
            'AC': (1, 0), '+/−': (1, 1), '%': (1, 2), '÷': (1, 3),
            '7': (2, 0), '8': (2, 1), '9': (2, 2), '×': (2, 3),
            '4': (3, 0), '5': (3, 1), '6': (3, 2), '−': (3, 3),
            '1': (4, 0), '2': (4, 1), '3': (4, 2), '+': (4, 3),
            '0': (5, 0), '.': (5, 2), '=': (5, 3),
        }
        
        # 버튼 생성
        for txt, pos in buttons.items():
            btn = QPushButton(txt)
            btn.setFixedSize(60, 60)
            if txt == '0':
                grid.addWidget(btn, pos[0], pos[1], 1, 2)
            else:
                grid.addWidget(btn, pos[0], pos[1])
            btn.clicked.connect(self._on_button_clicked)

        self.show()
        self._adjust_font_size()  # 초기 폰트 사이즈 조정
    
    def _on_button_clicked(self):
        """버튼 클릭 이벤트 처리"""
        button_text = self.sender().text()
        result = None
        
        # 버튼별 처리
        if button_text == 'AC':
            result = self.calculator.reset()
        elif button_text == '+/−':
            result = self.calculator.negative_positive()
        elif button_text == '%':
            result = self.calculator.percent()
        elif button_text == '÷':
            result = self.calculator.divide()
        elif button_text == '×':
            result = self.calculator.multiply()
        elif button_text == '−':
            result = self.calculator.subtract()
        elif button_text == '+':
            result = self.calculator.add()
        elif button_text == '=':
            result = self.calculator.equal()
        elif button_text == '.':
            result = self.calculator.input_decimal()
        else:  # 숫자 버튼
            result = self.calculator.input_number(int(button_text))
        
        # 결과 표시
        self.display.setText(result)
        self._adjust_font_size()  # 표시 내용에 따라 폰트 크기 조정
    
    def _adjust_font_size(self):
        """표시 내용에 따라 폰트 크기 조정"""
        text = self.display.text()
        font = self.display.font()
        
        # 기본 폰트 크기
        base_size = 16
        font.setPointSize(base_size)
        
        # 텍스트 길이에 따라 폰트 크기 조정
        metrics = QFontMetrics(font)
        text_width = metrics.horizontalAdvance(text)
        display_width = self.display.width() - 20  # 여백 고려
        
        # 텍스트가 화면을 넘어가면 폰트 크기 줄임
        if text_width > display_width:
            reduction_factor = display_width / text_width
            new_size = max(8, int(base_size * reduction_factor))  # 최소 크기 8pt
            font.setPointSize(new_size)
        
        self.display.setFont(font)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    calc = CalculatorUI()
    sys.exit(app.exec_())