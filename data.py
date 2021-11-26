import os
import numpy as np
from pyqtgraph.Qt import QtCore, QtGui
from scipy.ndimage import gaussian_filter1d
from statsmodels.nonparametric.smoothers_lowess import lowess
from scipy.stats import linregress

class Data(QtCore.QObject):
    sig_data_loaded = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()

        # x = np.empty(3)

        self.x_df_array = []
        self.y_df_lowess_array = []
        self.y_high_array = []
        self.y_low_array = []
        self.plotarray = []
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
        self.xlinregarray = []
        self.ylinregarray = []
        self.xmergearray = []
        self.ymergearray = []

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

    def smooth_transition(self, xa, ya, xb, yb):
        y_a_1, x_a_1, y_a_2, x_a_2, y_b_1, x_b_1, y_b_2, x_b_2 = self.array_overlap(xa, ya, xb, yb)
        q = 1.0 / (len(y_a_2) - 1)
        kp = np.arange(0, 1.0 + q, q)
        kn = kp[::-1]
        x_m = x_a_2

        if len(kp) > len(y_b_1):
            y_m = (y_b_1 * kp[:-1] + y_a_2 * kn[:-1])
        else:
            y_m = (y_b_1 * kp + y_a_2 * kn)

        sum_x = np.append(x_a_1, x_m[1:-1])
        sum_x = np.append(sum_x, x_b_2)
        sum_y = np.append(y_a_1, y_m[1:-1])
        sum_y = np.append(sum_y, y_b_2)
        return sum_x, sum_y

    def array_overlap(self, xa, ya, xb, yb):
        r = 3
        xa = np.round(xa, r)
        print('xb = ', xb)
        xb = np.round(xb, r)
        print('xa = ', xa)
        print('xb[0] = ', xb[0])
        sa = np.where(xa == xb[0])
        sa = sa[0][0]
        print('sa = ', sa)
        y_a_1 = ya[:sa + 1]
        x_a_1 = xa[:sa + 1]
        y_a_2 = ya[sa:]
        x_a_2 = xa[sa:]
        print('xb = ', xb)
        print('xa[0] = ', xa[-1])
        sb = np.where(xb == xa[-1])[0][0]
        print('sb = ', sb)
        y_b_1 = yb[:sb + 1]
        x_b_1 = xb[:sb + 1]
        y_b_2 = yb[sb:]
        x_b_2 = xb[sb:]
        return y_a_1, x_a_1, y_a_2, x_a_2, y_b_1, x_b_1, y_b_2, x_b_2

    def linreg(self, xa, ya, xb, yb):
        print('linreg xa = ', xa)
        print('linreg xb = ', xb)

        y_a_1, x_a_1, y_a_2, x_a_2, y_b_1, x_b_1, y_b_2, x_b_2 = self.array_overlap(xa, ya, xb, yb)
        res_a = linregress(x_a_2, y_a_2)
        res_b = linregress(x_b_1, y_b_1)

        inter_1 = (res_a.intercept - res_b.intercept)
        slope_1 = (res_a.slope - res_b.slope)
        reg_y_2 = (inter_1 + slope_1 * xb) + yb
        return xb, reg_y_2

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

    def edge_count(self, y, upper, lower):  # todo diese funktion ausbauen (wird derzeit kaum genutzt)
        cu = np.flatnonzero((y[:-1] < upper) & (y[1:] > upper)) + 1
        cl = np.flatnonzero((y[:-1] > lower) & (y[1:] < lower)) + 1
        return len(cu), len(cl)



