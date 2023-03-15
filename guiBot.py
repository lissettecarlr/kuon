
from GUI.mainWin import wincore
import sys
from PyQt5 import QtWidgets

                               
if __name__ == '__main__':
    app= QtWidgets.QApplication(sys.argv)
    win = wincore()
    win.show()
    sys.exit(app.exec_())