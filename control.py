import os
import pyqtgraph as pg
import numpy as np


class Measurement:
    def __init__(self, filename, m, xarray, yarray, color, offsetx, offsety, tilt):
        self.filename = filename
        self.m = m
        self.xarray = xarray
        self.yarray = yarray
        self.color = color
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
        directory, self.folder = self.data.selectDir()
        lowess_frac = 0.03
        lowess_it = 0
        low_cut_coeff = 0.7
        high_cut_coeff = 1.3
        i = 0
        ix = 0
        self.ui.w2.clear()
        for key in self.data.files:
            ###---init data arrays ---####
            x, y = self.data.readfile(os.path.join(directory, key))
            self.data.files[i] = str(int(key[:2]))
            self.data.rawxarray.append(x)
            self.data.rawyarray.append(y)
            autox, autoy, self.low, self.high = self.auto_cut_pitch(x, y, lowess_frac, lowess_it, low_cut_coeff, high_cut_coeff)
            self.data.autoxarray.append(autox)
            self.data.autoyarray.append(autoy)
            self.data.xarray.append(0.0)
            self.data.yarray.append(0.0)
            self.data.offsetxarray.append(0.0)
            self.data.offsetyarray.append(0.0)
            self.data.tiltarray.append(0.0)
            self.data.plotarray.append(self.ui.w2.plot())
            self.data.rioarray.append(pg.ROI([0.0, 0.0], [0.0, 0.0]))

            ###---init arrays ---####
            self.data.offsetxarray[i] = ix*0.05 # todo den koeff 0,05 anpassen
            self.data.scalex = self.ui.p.child('coeff scale X').value()
            self.data.scaley = self.ui.p.child('coeff scale Y').value()
            self.data.xarray[i] = self.data.scale_array(self.data.autoxarray[i], self.data.scalex)
            self.data.yarray[i] = self.data.scale_array(self.data.autoyarray[i], self.data.scaley)
            self.data.xarray[i] = self.data.offset_array(self.data.xarray[i], self.data.offsetxarray[i])
            self.data.yarray[i] = self.data.offset_array(self.data.yarray[i], self.data.offsetyarray[i])

            self.plot_graph(self.data.xarray[i], self.data.yarray[i], self.data.colorarray[i], self.data.files[i])
            ix = ix + int(len(self.data.xarray[i])/2)

            ###---init tree---###
            print('y3 = ', self.data.autoyarray[i][0])
            par = Measurement(self.data.files[i], int(self.data.files[i]), self.data.xarray[i], self.data.yarray[i],
                              self.data.colorarray[i], self.data.offsetxarray[i], self.data.offsetyarray[i],
                              self.data.tiltarray[i])
            self.ui.adNewlimb(par)

            ###---init RIOs ---####
            self.data.rioarray[i] = pg.ROI([self.data.xarray[i][0], self.data.yarray[i][0]],
                                  [self.data.xarray[i][-1]-self.data.xarray[i][0], 0],
                                  resizable=False)
            self.data.rioarray[i].addRotateHandle([1, 0], [0, 1])
            self.data.rioarray[i].addTranslateHandle([0, 0], [0.5, 0.5])
            self.ui.w2.addItem(self.data.rioarray[i])

            ###---init signals ---####
            self.ui.p.child('coeff scale X').sigValueChanged.connect(self.initial)
            self.ui.p.child('coeff scale Y').sigValueChanged.connect(self.initial)
            self.ui.p.child(self.data.files[i]).child(self.data.files[i] + '_color').sigValueChanged.connect(self.on_val)
            self.ui.p.child(self.data.files[i]).child(self.data.files[i] + '_offset X').sigValueChanged.connect(self.on_val)
            self.ui.p.child(self.data.files[i]).child(self.data.files[i] + '_offset Y').sigValueChanged.connect(self.on_val)
            self.ui.p.child(self.data.files[i]).child(self.data.files[i] + '_tilt').sigValueChanged.connect(self.on_val)
            self.data.rioarray[i].sigRegionChanged.connect(self.on_rioUpdate)
            self.ui.w2.autoRange()
            i = i+1
        print('exit onSelectBtn')

    def initial(self):
        print('enter initial')
        self.data.scalex = self.ui.p.child('coeff scale X').value()
        self.data.scaley = self.ui.p.child('coeff scale Y').value()
        # i = 0
        ix = 0
        self.ui.w2.clear()
        for i in range(len(self.data.xarray)):
            ###---init arrays ---####
            self.data.offsetxarray[i] = ix*0.05 # todo den koeff 0,05 anpassen
            self.data.scalex = self.ui.p.child('coeff scale X').value()
            self.data.scaley = self.ui.p.child('coeff scale Y').value()
            self.data.xarray[i] = self.data.scale_array(self.data.autoxarray[i], self.data.scalex)
            self.data.yarray[i] = self.data.scale_array(self.data.autoyarray[i], self.data.scaley)
            self.data.xarray[i] = self.data.offset_array(self.data.xarray[i], self.data.offsetxarray[i])
            self.data.yarray[i] = self.data.offset_array(self.data.yarray[i], self.data.offsetyarray[i])

            self.plot_graph(self.data.xarray[i], self.data.yarray[i], self.data.colorarray[i], self.data.files[i])
            ix = ix + int(len(self.data.xarray[i])/2)

            ###---init RIOs ---####
            self.data.rioarray[i] = pg.ROI([self.data.xarray[i][0], self.data.yarray[i][0]],
                                  [self.data.xarray[i][-1]-self.data.xarray[i][0], 0],
                                  resizable=False)
            self.data.rioarray[i].addRotateHandle([1, 0], [0, 1])
            self.data.rioarray[i].addTranslateHandle([0, 0], [0.5, 0.5])
            self.ui.w2.addItem(self.data.rioarray[i])



        self.ui.w2.autoRange()
        print('exit initial')

    def auto_cut_pitch(self, x,  y, frac, it, low_cut_coeff, high_cut_coeff):
        print('enter auto_cut_pitch')
        # -- filtern --
        y_lowess = self.data.lowess_filter(y, frac, it)
        # -- ableiten --
        y_df_lowess = abs(np.diff(y_lowess))
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
        y_ccut = y_ccut - y_ccut[0]
        dx = round(x[20]-x[19],3)
        x_cut = np.arange(0, len(y_ccut), 1)
        x_cut = x_cut*0.01
        print('exit auto_cut_pitch')
        return x_cut, y_ccut, low_cut, high_cut

    def plot_graph(self, x, y, color, name):
        print('enter plotgraph')
        print('plot_y = ', y[0])
        self.data.plotarray[int(name)-1] = self.ui.w2.plot(x, y, pen=color, name=name)
        print('exit plotgraph')

    def update_plot(self, u):
        print('enter_update_plot')
        self.ui.w2.removeItem(self.data.plotarray[int(u)])
        print('u = ', u)
        for i in range(len(self.data.xarray)):
            self.data.xarray[i] = self.data.scale_array(self.data.autoxarray[i], self.data.scalex)
            self.data.yarray[i] = self.data.scale_array(self.data.autoyarray[i], self.data.scaley)
            self.data.xarray[i] = self.data.offset_array(self.data.xarray[i], self.data.offsetxarray[i])
            self.data.yarray[i] = self.data.offset_array(self.data.yarray[i], self.data.offsetyarray[i])
            self.data.yarray[i] = self.data.tilt_array(self.data.yarray[i], self.data.tiltarray[i])
        self.plot_graph(self.data.xarray[u], self.data.yarray[u], self.data.colorarray[u], self.data.files[u])
        #self.ui.w2.autoRange()
        print('exit_update_plot')

    def on_val(self, name, val):
        print('enter_on_val')
        name = name.name()
        u = int(name[0])-1
        print('u = ', u)
        print('name = ', name, ' value = ', val)
        x = self.ui.p.child(self.data.files[u]).children()
        c = x[0].value()
        self.data.colorarray[u] = c.name()
        #self.data.xscalearray[u] = x[1].value()
        #self.data.yscalearray[u] = x[2].value()
        self.data.offsetxarray[u] = x[1].value()
        self.data.offsetyarray[u] = x[2].value()
        self.data.tiltarray[u] = x[3].value()
        r = self.data.rioarray[u]
        r.setPos([x[1].value(), x[2].value()])
        a = np.degrees(np.arctan(x[3].value()/r.size()[0]))
        r.setAngle(a)
        print('exit_on_val')

    def on_rioUpdate(self, rio):
        print('enter rioUpdate')
        print('rio = ', rio)
        i = self.data.rioarray.index(rio)
        p = rio.pos()
        t = np.tan(np.radians(rio.angle())) * rio.size()[0]
        self.data.offsetxarray[i] = p[0]
        self.data.offsetyarray[i] = p[1]
        self.data.tiltarray[i] = t
        # def aChanged(self):
        #     self.b.setValue(1.0 / self.a.value(), blockSignal=self.bChanged)
        #
        # def bChanged(self):
        #     self.a.setValue(1.0 / self.b.value(), blockSignal=self.aChanged)
        self.ui.p.child(self.data.files[i]).child(self.data.files[i] + '_offset X').setValue(p[0], blockSignal=self.on_val)
        self.ui.p.child(self.data.files[i]).child(self.data.files[i] + '_offset Y').setValue(p[1], blockSignal=self.on_val)
        self.ui.p.child(self.data.files[i]).child(self.data.files[i] + '_tilt').setValue(t, blockSignal=self.on_val)
        self.update_plot(i)
        print('exit rioUpdate')

