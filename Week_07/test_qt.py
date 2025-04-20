import sys
from PyQt5.QtWidgets import QApplication, QLabel

# PyQt5 테스트를 위한 코드

app = QApplication(sys.argv)
lbl = QLabel("Hello, I'm Ubukki...")
lbl.setFixedSize(200, 100)
lbl.show()
sys.exit(app.exec_())
