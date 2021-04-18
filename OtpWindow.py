from PyQt5.QtWidgets import *


class OtpWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('OTP window')
        self.setGeometry(100, 100, 200, 100)
        layout = QVBoxLayout()
        layout.addStretch(1)
        edit = QLineEdit()
        self.edit = edit
        subLayout = QHBoxLayout()

        btnOK = QPushButton("OTP 전달")
        btnOK.clicked.connect(self.onOKButtonClicked)
        layout.addWidget(edit)

        subLayout.addWidget(btnOK)
        layout.addLayout(subLayout)
        layout.addStretch(1)
        self.setLayout(layout)

    def onOKButtonClicked(self):
        self.accept()

    def showModal(self):
        return super().exec_()
