import sys, ast, operator, re
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QGridLayout, QLineEdit, QPushButton
)

_OPS = {
    ast.Add: operator.add, ast.Sub: operator.sub,
    ast.Mult: operator.mul, ast.Div: operator.truediv,
    ast.UAdd: operator.pos, ast.USub: operator.neg,
    ast.Pow: operator.pow, ast.Mod: operator.mod,
}

def safe_eval(expr: str) -> float:
    """
    :param expr: 문자열로 표현된 수식으로 연산자가 포함될 수 있음 (예: '1234+5678')
    :return: 수식의 계산 결과 (예: 6912.0)
    - 허용된 연산자만 처리하여 위험한 코드 실행 방지
    - eval()을 사용하지 않고, ast 모듈을 사용하여 안전하게 수식을 평가함
    - 지원하는 연산자: +, -, *, /, **, %, +/− (부호 변경)
    - 지원하지 않는 연산자: // (정수 나누기), //= (정수 나누기 대입)
    """
    node = ast.parse(expr, mode='eval').body # 수식을 AST 트리로 변환
    def _eval(n): # 재귀적으로 AST 노드를 평가하는 내부 함수 
        if isinstance(n, ast.Num): # 숫자 노드
            return n.n
        if isinstance(n, ast.BinOp): # 이진 연산자 노드
            return _OPS[type(n.op)](_eval(n.left), _eval(n.right))
        if isinstance(n, ast.UnaryOp):
            return _OPS[type(n.op)](_eval(n.operand))
        raise ValueError(f'Unsupported: {n!r}')
    return _eval(node)

def format_with_commas(s: str) -> str:
    """
    :param s: 숫자 문자열 (예: '1234' 등)
    :return: 콤마가 적용된 숫자 문자열 (예: '1,234' 등)
    - 숫자 문자열의 부호를 분리
    - 정수 부분에 천 단위 콤마를 추가
    - 소수점 부분은 그대로 유지
    """
    sign = '+' if s.startswith('+') else ('-' if s.startswith('-') else '')
    if sign: s = s[1:]
    parts = s.split('.', 1)
    try:
        parts[0] = f'{int(parts[0]):,}'
    except ValueError:
        pass
    return sign + '.'.join(parts) if len(parts) > 1 else sign + parts[0]

def format_expression(expr: str) -> str:
    """
    :param expr: 문자열로 표현된 수식으로 연산자가 포함될 수 있음 (예: '1234+5678')
    :return: 콤마가 적용된 새로운 수식 (예: '1,234+5,678')
    - UI에 표시되는 숫자에 천 단위 콤마를 추가함
    - 연산자는 그대로 유지, 숫자 부분만 포맷팅
    """
    def repl(m):
        """
        :param m: 정규 표현식 매칭 객체
        :return: 매칭된 숫자 문자열에 콤마를 추가한 문자열
        - format_with_commas()를 사용하여 콤마를 추가함
        """
        return format_with_commas(m.group())
    return re.sub(r'\d+(\.\d+)?', repl, expr)

class Calculator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.internal = ''  # 파이썬 eval용: '*' '/' '-' 등
        self.display_expr = ''  # UI 표시용: '×', '÷', '−'
        self._init_ui()

    def _init_ui(self):
        self.setWindowTitle('Calculator')
        central = QWidget()
        self.setCentralWidget(central)
        grid = QGridLayout()
        central.setLayout(grid)

        self.display = QLineEdit()
        self.display.setReadOnly(True)
        self.display.setAlignment(Qt.AlignRight)
        self.display.setFixedHeight(50)
        grid.addWidget(self.display, 0, 0, 1, 4)

        buttons = {
            'AC': (1, 0), '+/−': (1, 1), '%': (1, 2), '÷': (1, 3),
            '7': (2, 0), '8': (2, 1), '9': (2, 2), '×': (2, 3),
            '4': (3, 0), '5': (3, 1), '6': (3, 2), '−': (3, 3),
            '1': (4, 0), '2': (4, 1), '3': (4, 2), '+': (4, 3),
            '0': (5, 0), '.': (5, 2), '=': (5, 3),
        }
        for txt, pos in buttons.items():
            btn = QPushButton(txt)
            btn.setFixedSize(60, 60)
            if txt == '0':
                grid.addWidget(btn, pos[0], pos[1], 1, 2)
            else:
                grid.addWidget(btn, pos[0], pos[1])
            btn.clicked.connect(self._on_button_clicked)

        self.show()

    def _on_button_clicked(self):
        txt = self.sender().text()

        # 1) AC → 초기화
        if txt == 'AC':
            self.internal = ''
            self.display_expr = ''
            self.display.clear()
            return

        # 2) = → 계산
        if txt == '=':
            try:
                raw = safe_eval(self.internal)
                disp = format_with_commas(str(raw))
                # 계산 후에는 internal/표시 표현 모두 결과 숫자로 초기화
                self.internal = str(raw)
                self.display_expr = disp
                self.display.setText(disp)
            except Exception:
                # Error 상태
                self.internal = ''
                self.display_expr = 'Error'
                self.display.setText('Error')
            return

        # 3) Error 뒤 입력 → 완전 초기화
        if self.display_expr == 'Error':
            self.internal = ''
            self.display_expr = ''

        # 4) 버튼별 internal/표시 표현 업데이트
        ui = txt
        if txt == '×':
            py = '*'
        elif txt == '÷':
            py = '/'
        elif txt == '−':
            py = '-'
        else:
            py = txt

        self.internal += py
        self.display_expr += ui

        # 5) 실시간 콤마 포맷 반영
        self.display.setText(format_expression(self.display_expr))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    calc = Calculator()
    sys.exit(app.exec_())
