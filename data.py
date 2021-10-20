import os
import numpy as np
from pyqtgraph.Qt import QtCore, QtGui


class Data(QtCore.QObject):
    sig_data_loaded = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.rawxarray = []
        self.rawyarray = []
        self.autoxarray = []
        self.autoyarray = []
        self.xarray = []
        self.yarray = []
        self.rioarray = []
        self.pitcharray = []
        self.offsetxarray = []
        self.offsetyarray = []
        self.xscalearray = []
        self.yscalearray = []
        self.tiltarray = []
        self.colorarray = ['#FFEEB3', '#DEA895', '#F2B0F5', '#959FDE', '#AAFAE8', '#FFEEB3', '#DEA895', '#F2B0F5',
                           '#FFEEB3', '#DEA895', '#F2B0F5', '#959FDE', '#AAFAE8', '#FFEEB3', '#DEA895', '#F2B0F5']

    def selectDir(self):
        print('selectDir')
        path = QtGui.QFileDialog.getExistingDirectory(None, 'Select folder:', '/Users/antkp/Dropbox/phyton/phythonProject/measure',
                                                      QtGui.QFileDialog.ShowDirsOnly)
        path = '/Users/antkp/Dropbox/phyton/pythonProject/measure'

        self.files = [f for f in os.listdir(path) if f.endswith(".lsdf")]
        self.files.sort()
        print('files = ', self.files )


        # n = 0
        # for file in os.listdir(path):
        #     if file.endswith(".lsdf"):      #check numer of files *.lsdf
        #         n = n + 1
        # files = []
        # for i in range(n):
        #     st = 'm' + str(i + 1)
        #     for f in os.listdir(path):
        #         #if f.startswith(st):
        #         files.append(f)

        return path, self.files

    def loadfile(self, path):
        head = 1
        delimiter = '\t'
        #self.separator = '.'
        xcol = 2
        ycol = 1
        print('loadfile')
        text = open(path, 'r').read()
        text = text[0:text.find('0;0;')]
        text = text.replace('nan', '0')
        # if self.separator == ',':
        #     text = text.replace(',', '.')
        temp_file = open("temp", "w+")
        temp_file.write(text)
        data = np.genfromtxt('temp', skip_header=head, delimiter=delimiter, usecols=[xcol, ycol], autostrip=True, )
        temp_file.close()
        x_raw = data[:, 0]
        y_raw = data[:, 1]

        print('loadfile exit')

        return (x_raw[0:], y_raw[0:])

    def scale_array(self, array, coeff):
        sc_array = array * coeff
        return sc_array

    def offset_array(self, array, offset):
        off_array = array + offset
        return off_array

    def pitch_array(self, array, pitch):
        if pitch == 0.0:
            parray = np.zeros(len(array))
            print('len(array) = ', len(array))
            print('len(parray) = ', len(parray))
        else:
            parray = np.arange(start=0, stop=pitch, step= pitch/len(array))
            print('else_len(array) = ', len(array))
            print('else_len(parray) = ', len(parray))
        if len(array) != len(parray):
            parray = np.delete(parray, -1)
        return array + parray
