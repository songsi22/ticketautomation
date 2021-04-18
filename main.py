# -*- coding: utf-8 -*-

import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import WebDriverException
from bs4 import BeautifulSoup
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QThread, pyqtSignal
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from OtpWindow import OtpWindow


class Worker(QThread):
    message = pyqtSignal(str)
    progressbar = pyqtSignal(int)
    w3signal = pyqtSignal()

    def __init__(self, w3id, w3passwd, npasswd, ds8k, mysql, mode):
        super().__init__()
        self.url = 'https://'

        self.w3id = w3id
        self.w3pwd = w3passwd
        self.npasswd = npasswd
        self.ds8kpasswd = ds8k
        self.mysqlpasswd = mysql

        self.mode = mode

    def run(self):
        try:
            if self.mode:
                options = webdriver.ChromeOptions()
                options.add_argument('headless')
                options.add_argument('window-size=1920x1080')
                options.add_argument("disable-gpu")
                options.add_argument(
                    "Mozilla/5.0 (Windows NT 6.3; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 "
                    "Safari/537.36")
                self.driver = webdriver.Chrome('./chromedriver', options=options)
            else:
                self.driver = webdriver.Chrome('./chromedriver')
            self.message.emit('실행 중')
            self.driver.implicitly_wait(3)
            self.ds8klist = ['DS8700', 'DS8870']

            self.driver.get(self.url)
            time.sleep(2)
            self.message.emit('login 시도')
            self.driver.find_element_by_css_selector('#credentialSignin').click()
            self.driver.find_element_by_css_selector('#user-name-input').send_keys(self.w3id)
            self.driver.find_element_by_css_selector('#password-input').send_keys(self.w3pwd, Keys.ENTER)
            try:
                self.driver.find_element_by_css_selector('#left-nav > div > div > a:nth-child(4)')
                self.message.emit('login 성공')
            except Exception as e:
                print(e)
                self.message.emit('login 실패')
                time.sleep(5)
                self.driver.close()
            try:
                ### w3 MFA check
                self.driver.find_element_by_css_selector('#otp-input')
                print('w3 MFA login')
                self.w3signal.emit()
                self.message.emit('5분내로 OTP 인증을 완료해주세요.')
                WebDriverWait(self.driver, timeout=360).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "#left-nav > div > div > a:nth-child(4)")))
                self.message.emit('login 성공')
            except:
                pass
            try:
                self.message.emit('티켓 페이지로 이동')
                self.driver.find_element_by_css_selector('#left-nav > div > div > a:nth-child(4)').click()
                self.driver.find_element_by_css_selector('#left-nav > div > div > a:nth-child(1)').click()
                self.driver.find_element_by_css_selector(
                    '#form1 > table:nth-child(29) > tbody > tr:nth-child(2) > td:nth-child(2) > a').click()
                try:
                    self.driver.find_element_by_css_selector(
                        '#form1 > table.basic-table > tbody > tr:nth-child(2) > td:nth-child(1)')
                    total = self.driver.find_element_by_css_selector(
                        '#form1 > div:nth-child(32) > b:nth-child(3)').text
                    total = int(total)
                    if '' in self.npasswd:
                        self.message.emit('최소 1개 이상의 변경할 비밀번호를 입력하세요')
                        time.sleep(5)
                        self.driver.close()
                    else:
                        try:
                            for i in range(total):
                                self.html = self.driver.page_source
                                soup = BeautifulSoup(self.html, 'html.parser')
                                hostname = soup.select_one(
                                    '#form1 > table.basic-table > tbody > tr:nth-child(3) > td:nth-child(2)').text.strip()
                                userid = soup.select_one(
                                    '#form1 > table.basic-table > tbody > tr:nth-child(2) > td:nth-child(2)').text.strip()
                                # self.resultLabel.repaint()
                                remains = self.driver.find_element_by_css_selector(
                                    '#form1 > div:nth-child(32) > b:nth-child(3)').text
                                remains = int(remains)
                                proNum = total - remains + 1
                                msg = str(proNum) + ' of ' + str(total) + ' - ' + hostname + ' / ' + userid + ' 처리 중'
                                print(msg)
                                self.message.emit(msg)
                                # print("%s of %s - %s / %s processing" % (total - remains + 1, total, hostname, userid))

                                assign = self.driver.find_element_by_css_selector(
                                    '#form1 > table.basic-table > tbody > tr:nth-child(2) > td:nth-child(9) > img:nth-child(1)')
                                assign.click()
                                newupdate = self.driver.find_element_by_css_selector(
                                    '#form1 > table:nth-child(45) > tbody > tr > td:nth-child(1) >'
                                    ' table:nth-child(4) > tbody > tr:nth-child(2) > td > font > textarea')
                                newupdate.send_keys('change the password')
                                newpass = self.driver.find_element_by_css_selector('#current_que_exe_passwd')
                                if hostname in self.ds8klist:
                                    newpass.send_keys(self.ds8kpasswd)
                                    print("%s %s" % (hostname, self.ds8kpasswd))
                                elif 'MYSQL_MYL_3306_BCRS-MONITOR' in hostname:
                                    newpass.send_keys(self.mysqlpasswd)
                                    print("%s %s" % (hostname, self.mysqlpasswd))
                                else:
                                    newpass.send_keys(self.npasswd)
                                    print("%s %s" % (hostname, self.npasswd))

                                ##### back button  only test used
                                # self.driver.find_element_by_css_selector(
                                #     '#form1 > table:nth-child(47) > tbody > tr > td:nth-child(2) > span:nth-child(1) > input[type=button]').click()
                                ### update button click
                                self.driver.find_element_by_css_selector(
                                    '#form1 > table:nth-child(47) > tbody > tr > td:nth-child(2) > span:nth-child(2) > input[type=submit]').click()
                                time.sleep(1)
                                ### close button click
                                self.driver.find_element_by_css_selector(
                                    '#form1 > table:nth-child(47) > tbody > tr > td:nth-child(1) > span:nth-child(2) > input[type=button]').click()
                                time.sleep(1)
                                self.driver.find_element_by_css_selector(
                                    '#form1 > table > tbody > tr > td:nth-child(1) > div > div > span > input[type=button]').click()
                                time.sleep(2)
                                pb_per = (100 / total) * (i + 1)
                                self.progressbar.emit(pb_per)
                            self.message.emit('모든 티켓 처리 완료')
                            self.driver.quit()
                        except Exception as e:
                            print(e)
                            self.message.emit('티켓이 없습니다.')
                except Exception as e:
                    print(e)
                    self.message.emit('티켓이 없습니다.')
                    self.driver.close()
            except Exception as e:
                print(e)
                self.message.emit('페이지 접근에 실패하였습니다.')

        except WebDriverException as e:
            print(e)
            if 'ERR_NAME_NOT_RESOLVED' in str(e):
                self.message.emit('VPN 연결을 확인하세요.')
            else:
                self.message.emit(e)
            time.sleep(5)
            self.driver.quit()

    def w3otp(self):
        win = OtpWindow()
        r = win.showModal()
        if r:
            text = win.edit.text()
            self.driver.find_element_by_css_selector('#otp-input').send_keys(text)



class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(369, 240)
        MainWindow.setFixedSize(MainWindow.size())
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.execute = QtWidgets.QPushButton(self.centralwidget)
        self.execute.setGeometry(QtCore.QRect(150, 150, 75, 23))
        self.execute.setObjectName("execute")
        self.execute.clicked.connect(self.main)
        self.resultLabel = QtWidgets.QLabel(self.centralwidget)
        self.resultLabel.setGeometry(QtCore.QRect(20, 180, 331, 21))
        self.resultLabel.setText("VPN을 먼저 연결해주세요")
        self.resultLabel.setObjectName("resultLabel")
        self.progressbar = QtWidgets.QProgressBar(self.centralwidget)
        self.progressbar.setGeometry(QtCore.QRect(20, 205, 331, 21))
        self.progressbar.setObjectName('progressbar')
        self.modebox = QtWidgets.QCheckBox(self.centralwidget)
        self.modebox.setGeometry(QtCore.QRect(300, 150, 75, 23))
        self.modebox.setObjectName('modebox')
        self.modebox.setChecked(True)
        self.modebox.setText('hide')
        self.widget = QtWidgets.QWidget(self.centralwidget)
        self.widget.setGeometry(QtCore.QRect(20, 21, 331, 121))
        self.widget.setObjectName("widget")
        self.gridLayout = QtWidgets.QGridLayout(self.widget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.w3id = QtWidgets.QLabel(self.widget)
        self.w3id.setObjectName("w3id")
        self.gridLayout.addWidget(self.w3id, 0, 0, 1, 1)
        self.w3id_Edn = QtWidgets.QLineEdit(self.widget)
        self.w3id_Edn.setObjectName("w3id_Edn")
        self.gridLayout.addWidget(self.w3id_Edn, 0, 1, 1, 1)
        self.w3pwd = QtWidgets.QLabel(self.widget)
        self.w3pwd.setObjectName("w3pwd")
        self.gridLayout.addWidget(self.w3pwd, 1, 0, 1, 1)
        self.w3pwd_Edn = QtWidgets.QLineEdit(self.widget)
        self.w3pwd_Edn.setEchoMode(QtWidgets.QLineEdit.Password)
        self.w3pwd_Edn.setObjectName("w3pwd_Edn")
        self.gridLayout.addWidget(self.w3pwd_Edn, 1, 1, 1, 1)
        self.pwd = QtWidgets.QLabel(self.widget)
        self.pwd.setObjectName("pwd")
        self.gridLayout.addWidget(self.pwd, 2, 0, 1, 1)
        self.pwd_Edn = QtWidgets.QLineEdit(self.widget)
        self.pwd_Edn.setObjectName("pwd_Edn")
        self.gridLayout.addWidget(self.pwd_Edn, 2, 1, 1, 1)
        self.ds8kpwd = QtWidgets.QLabel(self.widget)
        self.ds8kpwd.setObjectName("ds8kpwd")
        self.gridLayout.addWidget(self.ds8kpwd, 3, 0, 1, 1)
        self.ds8k_Edn = QtWidgets.QLineEdit(self.widget)
        self.ds8k_Edn.setObjectName("ds8k_Edn")
        self.gridLayout.addWidget(self.ds8k_Edn, 3, 1, 1, 1)
        self.mysqlpwd = QtWidgets.QLabel(self.widget)
        self.mysqlpwd.setObjectName("mysqlpwd")
        self.gridLayout.addWidget(self.mysqlpwd, 4, 0, 1, 1)
        self.mysql_Edn = QtWidgets.QLineEdit(self.widget)
        self.mysql_Edn.setObjectName("mysql_Edn")
        self.gridLayout.addWidget(self.mysql_Edn, 4, 1, 1, 1)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "UAT-automation"))
        self.execute.setText(_translate("MainWindow", "실행"))
        self.w3id.setText(_translate("MainWindow", "w3 id"))
        self.w3pwd.setText(_translate("MainWindow", "w3 pwd"))
        self.pwd.setText(_translate("MainWindow", "pwd"))
        self.ds8kpwd.setText(_translate("MainWindow", "ds8k pwd"))
        self.mysqlpwd.setText(_translate("MainWindow", "mysql pwd"))

    def main(self):
        w3id = self.w3id_Edn.text()
        w3passwd = self.w3pwd_Edn.text()
        npasswd = self.pwd_Edn.text()
        ds8k = self.ds8k_Edn.text()
        mysql = self.mysql_Edn.text()
        mode = self.modebox.isChecked()
        self.worker = Worker(w3id, w3passwd, npasswd, ds8k, mysql, mode)
        self.worker.start()
        self.worker.message.connect(self.displayLabel)
        self.worker.progressbar.connect(self.progress_bar)
        self.worker.w3signal.connect(self.worker.w3otp)

    def progress_bar(self, no):
        self.progressbar.setValue(no)

    def displayLabel(self, msg):
        self.resultLabel.setText(msg)


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
