
import numpy as np
import matplotlib.pyplot as plt
import os
from scipy.stats import linregress

def readfile( path):
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

def smooth_transition( xa, ya, xb, yb):
    y_a_1, x_a_1, y_a_2, x_a_2, y_b_1, x_b_1, y_b_2, x_b_2 = array_overlap(xa, ya, xb, yb)
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

def array_overlap(xa, ya, xb, yb):
    r = 2
    xa = np.round(xa, r)
    xb = np.round(xb, r)
    sa = np.where(xa == xb[0])
    sa = sa[0][0]
    y_a_1 = ya[:sa + 1]
    x_a_1 = xa[:sa + 1]
    y_a_2 = ya[sa:]
    x_a_2 = xa[sa:]
    sb = np.where(xb == xa[-1])[0][0]
    y_b_1 = yb[:sb + 1]
    x_b_1 = xb[:sb + 1]
    y_b_2 = yb[sb:]
    x_b_2 = xb[sb:]
    return y_a_1, x_a_1, y_a_2, x_a_2, y_b_1, x_b_1, y_b_2, x_b_2

def linreg( xa, ya, xb, yb):
    y_a_1, x_a_1, y_a_2, x_a_2, y_b_1, x_b_1, y_b_2, x_b_2 = array_overlap(xa, ya, xb, yb)
    res_a = linregress(x_a_2, y_a_2)
    res_b = linregress(x_b_1, y_b_1)

    inter_1 = (res_a.intercept - res_b.intercept)
    slope_1 = (res_a.slope - res_b.slope)
    reg_y_2 = (inter_1 + slope_1 * xb) + yb
    plt.plot(xb, reg_y_2, 'b', label='fit_1')
    return xb, reg_y_2


files = [f for f in os.listdir('/Users/antkp/Dropbox/phyton/pythonProject/measure') if f.endswith(".lsdf")]
files.sort()
dir = '/Users/antkp/Dropbox/phyton/pythonProject/measure'
xarray = []
yarray = []
i = 0
r = 3
xoff = [0, 70, 140, 210, 280, 350, 400, 470]
yoff = [0, 14, 20, 23, 20, 11, -6, 7]
for key in files:
    x, y = readfile(os.path.join(dir, key))
    files[i] = str(int(key[:2]))
    x = np.round(x, r)
    x = x+xoff[i]
    y = y + yoff[i]
    xarray.append(x)
    yarray.append(y)
    i = i+1

for i in range(len(xarray)):
    plt.plot(xarray[i], yarray[i], linewidth=1)

for i in range(len(xarray)-1):
    xarray[i+1],  yarray[i+1] = linreg(xarray[i], yarray[i], xarray[i+1], yarray[i+1])

x = xarray[0]
y = yarray[0]

for i in range(len(xarray)):
    plt.plot(xarray[i], yarray[i], linewidth=1)

for i in range(len(xarray)-1):
    print('i = ',  i)
    x, y = smooth_transition(x, y, xarray[i+1], yarray[i+1])
    plt.plot(x, y, linewidth=.5)


plt.show()