from PyQt5 import QtWidgets
from PyQt5.QtCore import QObject, pyqtSignal, QSize, QRect, QPoint, Qt
from PyQt5.QtGui import QIcon, QPixmap, QFont, QTextCharFormat, QPen, QColor, QCursor, QMouseEvent
from PyQt5.QtWidgets import QSystemTrayIcon, QLabel, QTextBrowser, QPushButton, QStatusBar, QApplication, \
    QMainWindow,QMenu

from GUI.baseUi import Ui_MainWindow
import sys
from loguru import logger
from threading import Thread
import brain
import asyncio


# 消息显示
class displayThread(QObject):
    displaySignal = pyqtSignal(str,str)
    def __init__(self , text,showType):
        self.text = text
        self.showType = showType
        super(displayThread, self).__init__()
    def run(self):
        self.displaySignal.emit(self.text,self.showType)

# 获取对话应答
class chatThread(QObject):
    chatSignal = pyqtSignal(str)
    def __init__(self , text):
        self.text = text
        super(chatThread, self).__init__()
    def run(self):
        tk,contents = brain.matchingThinking(self.text)
        logger.info("切换到思维：{}".format(tk))
        brain.activateThinking(tk) #激活
        brain.changeThinking(tk) #切换
        if brain.thinking is None:
            logger.error("不存在激活的思维")
            return 
        res = asyncio.run(brain.response(contents))
        self.chatSignal.emit(res)


class wincore (QtWidgets.QMainWindow,Ui_MainWindow):
    def __init__(self):
        super(wincore,self).__init__()
        self.setupUi(self)
        self.ui_init()
        self.robot_init()

    def ui_init(self):
        # 一些变量
        self.display_number_thread = 0
        self.chat_number_thread = 0
        # 底部消息栏
        self.statusBar=QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage('kuon的界面版本，当前处于简陋无比的状态',5000) 
        #窗体标题
        self.setWindowTitle('kuon UI')
        #图标
        self.setWindowIcon(QIcon('./GUI/logo.ico'))
        #按钮
        self.pushButton.setText('发送')
        self.pushButton.clicked.connect(self.send_msg)

        #文字
        self.format = QTextCharFormat()
        self.format.setFontPointSize(14)
        self.format.setTextOutline(QPen(QColor('#1E90FF'), 0.7, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
 
    def robot_init(self):
        asyncio.run(brain.defaultActivate())
 
    def send_msg(self):
        text = self.textEdit.toPlainText()
        self.textEdit.clear()
        self.createThreadDisplay(text,"myslef")
        self.createThreadChat(text)

    def chat(self,text):
        self.createThreadDisplay(text)

    #在消息框中现在消息
    def displayText(self,text,showType="normal"):
        if(showType == "normal"):
            color = "#d93636"
        elif(showType == "myslef"):
            color = "#1E90FF"
        else:
            color = "#0a0a0a"
        try:
            self.format.setTextOutline(
                QPen(QColor(color), 0.7, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            self.textBrowser.mergeCurrentCharFormat(self.format)
            self.textBrowser.append(text)
            self.display_number_thread -= 1  # 线程结束，减少线程数
        except Exception as ex:
            logger.error("错误信息："+str(ex))

    #创建线程进行显示
    def createThreadDisplay(self,text,showType ="normal"):
        self.display_number_thread += 1
        dThread = displayThread(text,showType)
        thread = Thread(target=dThread.run)
        thread.setDaemon(True)
        dThread.displaySignal.connect(self.displayText)
        thread.start()

    #创建对话线程
    def createThreadChat(self,text):
        self.chat_number_thread += 1
        cThread = chatThread(text)
        thread = Thread(target=cThread.run)
        thread.setDaemon(True)
        cThread.chatSignal.connect(self.chat)
        thread.start()

    def closeEvent(self,event):
        brain.closs()
        