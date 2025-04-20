import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QGridLayout, QLineEdit, QPushButton
)

class Calculator(QMainWindow):
    def __init__(self):
        super().__init__()
        self._init_ui()

    def _init_ui(self):
        self.setWindowTitle('Calculator')
        central = QWidget()
        self.setCentralWidget(central)

        grid = QGridLayout()
        central.setLayout(grid)

        # 디스플레이용 QLineEdit 설정
        self.display = QLineEdit()
        self.display.setReadOnly(True)              # 직접 입력 방지
        self.display.setAlignment(Qt.AlignRight)    # 숫자 오른쪽 정렬
        self.display.setFixedHeight(50)             # 높이 고정
        grid.addWidget(self.display, 0, 0, 1, 4)

        # 버튼 텍스트 & 그리드 위치 매핑
        buttons = {
            'AC': (1, 0), '+/−': (1, 1), '%': (1, 2), '÷': (1, 3),
            '7': (2, 0), '8': (2, 1), '9': (2, 2), '×': (2, 3),
            '4': (3, 0), '5': (3, 1), '6': (3, 2), '−': (3, 3),
            '1': (4, 0), '2': (4, 1), '3': (4, 2), '+': (4, 3),
            '0': (5, 0), '.': (5, 2), '=': (5, 3),
        }

        for text, pos in buttons.items():
            btn = QPushButton(text)
            btn.setFixedSize(60, 60)
            # '0' 버튼은 가로 두 칸 차지
            if text == '0':
                grid.addWidget(btn, pos[0], pos[1], 1, 2)
            else:
                grid.addWidget(btn, pos[0], pos[1])
            btn.clicked.connect(self._on_button_clicked)

        self.show()

    def _on_button_clicked(self):
        text = self.sender().text() # 클릭된 버튼 요소 가져옴

        # 'AC'면 디스플레이 초기화
        if text == 'AC':
            self.display.clear()
            return
        
        # '='면 계산 수행
        if text == '=':
            expr = self.display.text()
            # UI기호 파이썬 문법으로 변환
            expr = expr.replace('×', '*').replace('÷', '/').replace('−', '-')
            try:
                # __builtins__ 비워서 최소한의 내장만 허용함
                result = str(eval(expr, {"__builtins__":None}, {}))
            except Exception:
                result = 'Error'
            self.display.setText(result)
            return

        # 숫자, 연산자, 소수점은 기존 텍스트에 이어붙임
        current = self.display.text()
        self.display.setText(current + text)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    calc = Calculator()
    sys.exit(app.exec_())
