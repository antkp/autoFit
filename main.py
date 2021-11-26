import sys
from pyqtgraph.Qt import QtCore, QtGui
from ui import Ui
from data import Data
from control import Control


def main():
    print('main')
    app = QtGui.QApplication([])
    win = QtGui.QMainWindow()
    ui = Ui(win)
    data = Data()
    control = Control(data, ui)
    win.show()

    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()


if __name__ == '__main__':
    main()