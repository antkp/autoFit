import os
import numpy as np
from pyqtgraph.Qt import QtCore, QtGui
from scipy.ndimage import gaussian_filter1d
from statsmodels.nonparametric.smoothers_lowess import lowess

class Data(QtCore.QObject):
    sig_data_loaded = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.plotarray =[]
        self.rawxarray = []
        self.rawyarray = []
        self.autoxarray = []
        self.autoyarray = []
        self.Y_filtered = []
        self.xarray = []
        self.yarray = []
        self.rioarray = []
        self.scalex = 5.0
        self.scaley = 1.0
        self.offsetxarray = []
        self.offsetyarray = []
        self.tiltarray = []
        self.colorarray = ['#FFEEB3', '#DEA895', '#F2B0F5', '#959FDE', '#AAFAE8', '#FFEEB3', '#DEA895', '#F2B0F5',
                           '#FFEEB3', '#DEA895', '#F2B0F5', '#959FDE', '#AAFAE8', '#FFEEB3', '#DEA895', '#F2B0F5']

    def selectDir(self):
        print('enter selectDir')
        path = QtGui.QFileDialog.getExistingDirectory(None, 'Select folder:', '/Users/antkp/Dropbox/phyton/phythonProject/measure',
                                                      QtGui.QFileDialog.ShowDirsOnly)
        path = '/Users/antkp/Dropbox/phyton/pythonProject/measure'

        self.files = [f for f in os.listdir(path) if f.endswith(".lsdf")]
        self.files.sort()
        print('exit selectDir')
        return path, self.files

    def readfile(self, path):
        print('enter loadfile')
        head = 1
        delimiter = '\t'
        xcol = 2
        ycol = 1
        text = open(path, 'r').read()
        text = text[0:text.find('0;0;')]
        text = text.replace('nan', '0')
        temp_file = open("temp", "w+")
        temp_file.write(text)
        data = np.genfromtxt('temp', skip_header=head, delimiter=delimiter, usecols=[xcol, ycol], autostrip=True, )
        temp_file.close()
        x_raw = data[:, 0]
        y_raw = data[:, 1]
        print('exit loadfile')
        return (x_raw[0:], y_raw[0:])

    # def scale_array(self, array, coeff):
    #     print('enter scale_array')
    #     sc_array = array * coeff
    #     print('exit scale_array')
    #     return sc_array
    #
    # def offset_array(self, array, offset):
    #     print('enter offset_array')
    #     off_array = array + offset
    #     print('exit offset_array')
    #     return off_array

    def tilt_array(self, array, tilt):
        #print('enter tilt_array')
        if tilt == 0.0:
            tarray = np.zeros(len(array))
        else:
            tarray = np.arange(start=0, stop=tilt, step= tilt/len(array))
        if len(array) != len(tarray):
            tarray = np.delete(tarray, -1)
        #print('exit tilt_array')
        return array + tarray

    def gauss_filter(self, y, sigma):
        y_f = gaussian_filter1d(y, sigma)
        return y_f

    def lowess_filter(self, y, fraction, iteration):
        print('enter lowess_filter')
        y_f = lowess(y, np.arange(len(y)), is_sorted=True, frac=fraction, it=iteration)
        y_f = y_f[:, 1]
        print('exit lowess_filter')
        return y_f

    def lincomp(self, y):
        print('enter lincomp')
        yd = y
        delta = yd[-1] - yd[0]
        n = len(y)
        comparray = np.arange(0, delta, (delta / n))
        if n != len(comparray):
            arr = y - comparray[:n]
        else:
            arr = y - comparray
        print('exit lincomp')
        return arr

