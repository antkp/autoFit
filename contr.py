import sys
import os
import pyqtgraph as pg
import numpy as np


class Measurement:
    def __init__(self, filename, m, xarray, yarray, color, xscale, yscale, offsetx, offsety, tilt):
        self.filename = filename
        self.m = m
        self.xarray = xarray
        self.yarray = yarray
        self.color = color
        self.xscale = xscale
        self.yscale = yscale
        self.offsetx = offsetx
        self.offsety = offsety
        self.tilt = tilt

class Control:

    def __init__(self, data, ui):
        self.data = data
        self.ui = ui

        self.ui.p.child('select folder').sigActivated.connect(self.onSelectBtn)


    def onSelectBtn(self):
        print('enter onSelectBtn')
        directory, self.files = self.data.selectDir()
        i = 0
        lowess_frac = 0.03
        lowess_it = 0
        low_cut_coeff = 0.7
        high_cut_coeff = 1.3

        for key in self.data.files:
            x, y = self.data.readfile(os.path.join(directory, key))
            self.data.rawxarray.append(x)
            self.data.rawyarray.append(y)

            autox, autoy, self.low, self.high = self.auto_cut_pitch(x, y, lowess_frac, lowess_it, low_cut_coeff, high_cut_coeff)

            self.data.autoxarray.append(autox)
            self.data.autoyarray.append(autoy)
            self.data.xarray.append(x)
            self.data.yarray.append(y)

            print('self.data.rioarray = ', len(self.data.rioarray))

            self.data.pitcharray.append(y*0)
            self.data.offsetxarray.append(0.0)
            self.data.offsetyarray.append(0.0)
            self.data.xscalearray.append(5.0)
            self.data.yscalearray.append(1.0)
            self.data.tiltarray.append(0.0)

        print('self.data.xscalearray = ', self.data.xscalearray)
        self.onFilesReady(directory)
        print('exit onSelectBtn')

    def auto_cut_pitch(self, x,  y, frac, it, low_cut_coeff, high_cut_coeff):
        print('enter auto_cut_pitch')
        # -- filtern --
        y_lowess = self.data.lowess_filter(y, frac, it)

        # -- ableiten --
        y_df_lowess = abs(np.diff(y_lowess))
        #x = np.delete(x, -1)

        # -- thresh --
        start= int(len(y_df_lowess)/3)
        stop = 2*start
        a = np.average(y_df_lowess[start:stop])

        low_cut = a * low_cut_coeff
        high_cut = a * high_cut_coeff

        # -- cut --
        yc = y[:-1]
        y_df_cut = y_df_lowess[y_df_lowess > low_cut] #alles größer low

        y_cut = yc[y_df_lowess > low_cut]
        y_ccut = y_cut[y_df_cut < high_cut]
        y_ccut = self.data.lincomp(y_ccut)

        dx = round(x[20]-x[19],3)
        print('dx = ', dx)
        x_cut = np.arange(0, len(y_ccut), 1)
        x_cut = x_cut*0.01

        print('len(x_cut) = ', len(x_cut))
        print('len(y_ccut) = ', len(y_ccut))

        print('exit auto_cut_pitch')
        return x_cut, y_ccut, low_cut, high_cut

    def onFilesReady(self, directory):
        print('enter onFilesReady')
        print('len(self.files)', len(self.files))
        print('len(self.data.autoxarray)', len(self.data.autoxarray))
        print('len(self.data.xarray)', len(self.data.xarray))
        print('len(self.data.yarray)', len(self.data.yarray))

        ix = 0
        for i in range(len(self.data.files)):
            print('ix =', ix)
            print('i =', i)

            print('self.data.autoxarray[i] = ', self.data.autoxarray[i])

            self.data.offsetxarray[i] = ix*0.05
            self.data.xarray[i] = self.data.scale_array(self.data.autoxarray[i], self.data.xscalearray[i])
            self.data.yarray[i] = self.data.scale_array(self.data.autoyarray[i], self.data.yscalearray[i])

            self.data.xarray[i] = self.data.offset_array(self.data.xarray[i], self.data.offsetxarray[i])
            self.data.yarray[i] = self.data.offset_array(self.data.yarray[i], self.data.offsetyarray[i])

            par = Measurement(self.files[i], i+1, self.data.xarray[i], self.data.yarray[i], self.data.colorarray[i],
                              self.data.xscalearray[i], self.data.yscalearray[i], self.data.offsetxarray[i],
                              self.data.offsetyarray[i], self.data.tiltarray[i])
            self.ui.adNewlimb(par)
            self.ui.p.child(self.files[i]).child(str(i+1)+'_color').sigValueChanged.connect(self.on_val)
            self.ui.p.child(self.files[i]).child(str(i+1)+'_scale X').sigValueChanged.connect(self.on_val)
            self.ui.p.child(self.files[i]).child(str(i+1)+'_scale Y').sigValueChanged.connect(self.on_val)
            self.ui.p.child(self.files[i]).child(str(i+1)+'_offset X').sigValueChanged.connect(self.on_val)
            self.ui.p.child(self.files[i]).child(str(i+1)+'_offset Y').sigValueChanged.connect(self.on_val)
            self.ui.p.child(self.files[i]).child(str(i+1)+'_tilt').sigValueChanged.connect(self.on_val)

            self.plot_graph(self.data.xarray[i], self.data.yarray[i], self.data.colorarray[i], self.files[i])
            ix = ix + int(len(self.data.xarray[i])/2)

        self.iniRio()
        self.ui.w2.autoRange()
        print('onFilesReady exit')

    def iniRio(self):
        print('enter inRio')
        for i in range(len(self.data.files)):
            print('i =', i)

            rioA = pg.ROI([self.data.xarray[i][0], self.data.yarray[i][0]],
                                  [self.data.xarray[i][-1]-self.data.xarray[i][0], 0],
                                  resizable=False, removable=True)
            rioA.addRotateHandle([1, 0], [0, 1])
            rioA.addTranslateHandle([0, 0], [0.5, 0.5])
            self.data.rioarray.append(rioA)
            self.ui.w2.addItem(rioA)
        print('exit inRio')


    def plot_graph(self, x, y, color, name):
        print('enter plotgraph')
        self.ui.w2.plot(x, y, pen=color, name=name)
        print('self.ui.w2.allChildItems()', self.ui.w2.allChildItems())
        print('int(name[0:2]) = ', int(name[0:2]))
        #print('self.data.rioarray = ', len(self.data.rioarray))
        print('exit plotgraph')


    def update_plot(self):
        print('enter_update_plot')
        self.ui.w2.clear()
        for i in range(len(self.data.xscalearray)):

            #self.data.xarray[i] = self.data.scale_array(self.data.rawxarray[i], self.data.xscalearray[i])
            #self.data.yarray[i] = self.data.scale_array(self.data.rawyarray[i], self.data.yscalearray[i])
            self.data.xarray[i] = self.data.scale_array(self.data.autoxarray[i], self.data.xscalearray[i])
            self.data.yarray[i] = self.data.scale_array(self.data.autoyarray[i], self.data.yscalearray[i])
            self.data.xarray[i] = self.data.offset_array(self.data.xarray[i], self.data.offsetxarray[i])
            self.data.yarray[i] = self.data.offset_array(self.data.yarray[i], self.data.offsetyarray[i])

            self.data.yarray[i] = self.data.pitch_array(self.data.yarray[i], self.data.tiltarray[i])
            print('self.data.yarray[i] = ', len(self.data.yarray[i]))

            self.plot_graph(self.data.xarray[i], self.data.yarray[i], self.data.colorarray[i], self.files[i])

        self.ui.w2.autoRange()

        print('exit_update_plot')

    def on_val(self, name, val):
        print('enter_on_val')
        name = name.name()
        u = int(name[0])-1
        x = self.ui.p.child(self.files[u]).children()

        c = x[0].value()
        self.data.colorarray[u] = c.name()
        self.data.xscalearray[u] = x[1].value()
        self.data.yscalearray[u] = x[2].value()
        self.data.offsetxarray[u] = x[3].value()
        self.data.offsetyarray[u] = x[4].value()
        self.data.tiltarray[u] = x[5].value()

        self.update_plot()
        print('exit_on_val')

