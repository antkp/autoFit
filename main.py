import sys
from pyqtgraph.Qt import QtCore, QtGui , QtWidgets
from ui import Ui
from data import Data
from contr import Control

# todo
#   update/remove each plot --> change the structure
#   read start position from data name - option
#   fit data - least squares --> option
#   fit data - ICP ?  --> option
#   filter - option


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