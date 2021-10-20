import sys
from pyqtgraph.Qt import QtCore, QtGui , QtWidgets
from ui import Ui
from data import Data
from control import Control


# todo
#   update/remove each plot
#   read start position from data name
#   fit data --> least squares



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