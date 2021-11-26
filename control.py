import os
import pyqtgraph as pg
import numpy as np


# ToDo wenn möglich nur die Abgeleiteten werte in W3 anzeigen alles andere in W2
#  nach "linreg" und rio-handle bewegung teilweise Abstürze (tilt geht wohl --> Offset eher nich ???)
#  'linreg' scheint sich immer auf ungefilterte daten zu stützen !? --> hier immer die Actuellen nutzen !


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
        self.ui.p.child('filter').hide()

    def onSelectBtn(self):
        print('enter onSelectBtn')
        directory, self.folder = self.data.selectDir()
        lowess_frac = 0.023
        lowess_it = 0
        low_cut_coeff = 0.7
        high_cut_coeff = 1.3
        i = 0

        self.ui.p.child('filter').show()
        self.ui.p.child('filter').child('select filter').sigValueChanged.connect(self.on_filter)
        self.ui.p.child('filter').child('gauss').child('sigma').sigValueChanged.connect(self.on_filter)
        self.ui.p.child('filter').child('lowess').child('fraction').sigValueChanged.connect(self.on_filter)
        self.ui.p.child('filter').child('lowess').child('iteration').sigValueChanged.connect(self.on_filter)
        self.ui.p.child('coeff scale X').sigValueChanged.connect(self.scale)
        self.ui.p.child('coeff scale Y').sigValueChanged.connect(self.scale)

        self.ui.w2.clear()
        for key in self.data.files:
            ### find start/stop values from data_name
            q = [pos for pos, char in enumerate(key) if char == '_']
            # print('q = ', q)
            p = [pos for pos, char in enumerate(key) if char == '.']
            # print('p = ', p)
            start_x_pos = int(key[q[1] + 1:q[2]])  # start value given in filename # 01_x(y)_-1083_-683.lsdf --> '-1083'
            # print('start_x_pos = ', start_x_pos)
            end_x_pos = int(key[q[2] + 1:p[0]])  # stopvalue given in filename # 01_x(y)_-1083_-683.lsdf --> '-683' todo use end_x_pos to cutt data !
            # print('end_x_pos = ', end_x_pos)

            ### read rawdata from files ###
            x, y = self.data.readfile(os.path.join(directory, key))
            self.data.files[i] = str(int(key[:2]))
            self.data.rawxarray.append(x)
            self.data.rawyarray.append(y)

            ### autocut raw data ###
            autox, autoy, self.low, self.high = self.auto_cut_pitch(x, y, lowess_frac, lowess_it, low_cut_coeff, high_cut_coeff)

            ### init data arrays ####
            self.data.autoxarray.append(autox)
            self.data.autoyarray.append(autoy)
            self.data.Y_filtered.append(autoy)
            self.data.xarray.append(0.0)
            self.data.yarray.append(0.0)
            self.data.offsetxarray.append(start_x_pos)
            self.data.offsetyarray.append(0.0)
            self.data.tiltarray.append(0.0)
            self.data.plotarray.append(self.ui.w2.plot())
            self.data.rioarray.append(pg.ROI([0.0, 0.0], [0.0, 0.0]))
            self.init_data_arrays(i)
            ### init tree ###
            par = Measurement(self.data.files[i], int(self.data.files[i]), self.data.xarray[i],
                              self.data.yarray[i], self.data.colorarray[i], self.data.offsetxarray[i],
                              self.data.offsetyarray[i], self.data.tiltarray[i])
            self.ui.adNewlimb(par)
            self.init_rio(self.data.xarray[i], self.data.yarray[i], i)
            self.init_signals(i)
            i = i + 1
        self.ui.w2.autoRange()
        self.ui.p.addChild(self.ui.ppp)
        self.ui.p.child('___').child('lin-reg').sigActivated.connect(self.on_linreg)
        self.ui.p.child('___').child('merge').sigActivated.connect(self.on_merge)

        print('exit onSelectBtn')

    def init_data_arrays(self, i):
        ###---init arrays ---####
        self.data.scalex = self.ui.p.child('coeff scale X').value()
        self.data.scaley = self.ui.p.child('coeff scale Y').value()
        self.data.xarray[i] = self.data.autoxarray[i] * self.data.scalex
        self.data.yarray[i] = self.data.Y_filtered[i] * self.data.scaley
        self.data.xarray[i] = self.data.xarray[i] + self.data.offsetxarray[i]
        self.data.yarray[i] = self.data.yarray[i] + self.data.offsetyarray[i]
        self.plot_graph(self.data.xarray[i], self.data.yarray[i], self.data.colorarray[i], self.data.files[i])

    def scale(self):
        print('enter initial')
        self.data.scalex = self.ui.p.child('coeff scale X').value()
        self.data.scaley = self.ui.p.child('coeff scale Y').value()
        self.ui.w2.clear()
        for i in range(len(self.data.xarray)):
            self.data.scalex = self.ui.p.child('coeff scale X').value()
            self.data.scaley = self.ui.p.child('coeff scale Y').value()
            self.data.xarray[i] = self.data.autoxarray[i] * self.data.scalex
            self.data.yarray[i] = self.data.Y_filtered[i] * self.data.scaley
            self.data.xarray[i] = self.data.xarray[i] + self.data.offsetxarray[i]
            self.data.yarray[i] = self.data.yarray[i] + self.data.offsetyarray[i]
            self.plot_graph(self.data.xarray[i], self.data.yarray[i], self.data.colorarray[i], self.data.files[i])
            self.init_rio(self.data.xarray[i], self.data.yarray[i], i)
        self.ui.w2.autoRange()

        print('exit initial')

    def init_rio(self, xarray, yarray, i):
        """add rios to data"""

        print('enter init_riox')
        h = yarray[-1] - yarray[0]
        l = xarray[-1] - xarray[0]
        a = np.degrees(np.arctan(h / l))

        self.data.rioarray[i] = pg.ROI([self.data.xarray[i][0], self.data.yarray[i][0]],
                                       size=[self.data.xarray[i][-1] - self.data.xarray[i][0], 0], angle=a,
                                       resizable=False)
        self.data.rioarray[i].addRotateHandle([1, 0], [0, 1])
        self.data.rioarray[i].addTranslateHandle([0, 0], [0.5, 0.5])
        self.ui.w2.addItem(self.data.rioarray[i])
        self.data.rioarray[i].sigRegionChanged.connect(self.on_rioUpdate)
        print('exit init_riox')

    def init_signals(self, i):
        ###---init signals ---####
        self.ui.p.child(self.data.files[i]).child(self.data.files[i] + '_show_diff').sigActivated.connect(
            self.on_show_diff)
        self.ui.p.child(self.data.files[i]).child(self.data.files[i] + '_color').sigValueChanged.connect(
            self.on_val)
        self.ui.p.child(self.data.files[i]).child(self.data.files[i] + '_offset X').sigValueChanged.connect(
            self.on_val)
        self.ui.p.child(self.data.files[i]).child(self.data.files[i] + '_offset Y').sigValueChanged.connect(
            self.on_val)
        self.ui.p.child(self.data.files[i]).child(self.data.files[i] + '_tilt').sigValueChanged.connect(self.on_val)
        self.data.rioarray[i].sigRegionChanged.connect(self.on_rioUpdate)

    def auto_cut_pitch(self, x, y, frac, it, low_cut_coeff, high_cut_coeff):
        print('enter auto_cut_pitch')
        # -- filtern --
        y_lowess = self.data.lowess_filter(y, frac, it)
        # -- ableiten --
        y_df_lowess = abs(np.diff(y_lowess))
        # -- thresh --
        start = int(len(y_df_lowess) / 3)
        stop = 2 * start
        a = np.average(y_df_lowess[start:stop])
        low_cut = a * low_cut_coeff
        self.data.y_low_array.append(low_cut)
        high_cut = a * high_cut_coeff
        self.data.y_high_array.append(high_cut)
        # -- cut --
        yc = y[:-1]
        y_df_cut = y_df_lowess[y_df_lowess > low_cut]  # alles größer low

        # todo IDEE --> die gefilterten und abgeleitetene Daten sind beim Losfahren stärker verrauscht, es könnte
        #  besser sein die Daten von hinten zu beschneiden und die verfahrene länge aus dem Dateinamen abzuleiten ?

        y_cut = yc[y_df_lowess > low_cut]
        y_ccut = y_cut[y_df_cut < high_cut]

        print('edge_count up = ', self.data.edge_count(y_df_lowess, high_cut, low_cut)[0])
        print('edge_count down = ', self.data.edge_count(y_df_lowess, high_cut, low_cut)[1])

        y_ccut = self.data.lincomp(y_ccut)
        y_ccut = y_ccut - y_ccut[0]
        dx = round(x[20] - x[19], 3)
        x_cut = np.arange(0, len(y_ccut), 1)
        x_cut = x_cut * 0.01
        x_df = x[:-1]
        self.data.x_df_array.append(x_df)
        self.data.y_df_lowess_array.append(y_df_lowess)

        self.ui.w3.plot(x_df, y_df_lowess)
        self.ui.w3.autoRange()

        print('exit auto_cut_pitch')
        return x_cut, y_ccut, low_cut, high_cut

    def plot_graph(self, x, y, color, name):
        print('enter plotgraph')
        self.data.plotarray[int(name) - 1] = self.ui.w2.plot(x, y, pen=color, name=name)
        print('exit plotgraph')

    def update_plot(self, u):
        print('enter_update_plot')
        self.ui.w2.removeItem(self.data.plotarray[int(u)])
        for i in range(len(self.data.xarray)):
            self.data.xarray[i] = self.data.autoxarray[i] * self.data.scalex
            self.data.yarray[i] = self.data.Y_filtered[i] * self.data.scaley
            self.data.xarray[i] = self.data.xarray[i] + self.data.offsetxarray[i]
            self.data.yarray[i] = self.data.yarray[i] + self.data.offsetyarray[i]
            self.data.yarray[i] = self.data.tilt_array(self.data.yarray[i], self.data.tiltarray[i])
        self.plot_graph(self.data.xarray[u], self.data.yarray[u], self.data.colorarray[u], self.data.files[u])
        print('exit_update_plot')

    def on_val(self, name, val):
        print('enter_on_val')
        name = name.name()
        u = int(name[0]) - 1
        x = self.ui.p.child(self.data.files[u]).children()
        print('x[0].value() = ', x[0].value())
        c = x[1].value()
        print('c = ', c)
        self.data.colorarray[u] = c.name()
        self.data.offsetxarray[u] = x[2].value()
        self.data.offsetyarray[u] = x[3].value()
        self.data.tiltarray[u] = x[4].value()
        r = self.data.rioarray[u]
        r.setPos([x[2].value(), x[3].value()])
        a = np.degrees(np.arctan(x[4].value() / r.size()[0]))
        r.setAngle(a)
        self.update_plot(u)
        print('exit_on_val')

    def on_rioUpdate(self, rio):
        print('enter rioUpdate')
        i = self.data.rioarray.index(rio)
        p = rio.pos()
        t = np.tan(np.radians(rio.angle())) * rio.size()[0]
        self.data.offsetxarray[i] = p[0]
        self.data.offsetyarray[i] = p[1]
        self.data.tiltarray[i] = t
        self.ui.p.child(self.data.files[i]).child(self.data.files[i] + '_offset X').setValue(p[0],
                                                                                             blockSignal=self.on_val)
        self.ui.p.child(self.data.files[i]).child(self.data.files[i] + '_offset Y').setValue(p[1],
                                                                                             blockSignal=self.on_val)
        self.ui.p.child(self.data.files[i]).child(self.data.files[i] + '_tilt').setValue(t, blockSignal=self.on_val)
        self.update_plot(i)
        print('exit rioUpdate')

    def on_show_diff(self, name):
        print('x = ', name)
        name = name.name()
        u = int(name[0]) - 1
        self.ui.w3.clear()
        for i in range(len(self.data.xarray)):
            self.ui.w3.plot(self.data.x_df_array[u], self.data.y_df_lowess_array[u])
            self.ui.w3.plot(self.data.x_df_array[u], self.data.y_high_array[u] * np.ones(len(self.data.x_df_array[u])),
                            pen=(255, 0, 0))
            self.ui.w3.plot(self.data.x_df_array[u], self.data.y_low_array[u] * np.ones(len(self.data.x_df_array[u])),
                            pen=(255, 0, 0))
        self.ui.w3.autoRange()

    def on_merge(self):
        print('enter on_merge')
        with pg.BusyCursor():
            self.data.xmergearray = self.data.xarray[0]
            self.data.ymergearray = self.data.yarray[0]
            for i in range(len(self.data.xarray) - 1):
                print('on merge --> i = ', i)
                self.data.xmergearray, self.data.ymergearray = self.data.smooth_transition(self.data.xmergearray,
                                                                                           self.data.ymergearray,
                                                                                           self.data.xarray[i + 1],
                                                                                           self.data.yarray[i + 1])

            self.ui.w3.clear()
            self.ui.w3.plot(self.data.xmergearray, self.data.ymergearray, name='merge')
            self.ui.w3.autoRange()

    def on_linreg(self):
        print('enter on_linreg')

        self.ui.w2.clear()
        self.ui.w3.clear()
        with pg.BusyCursor():
            self.data.xlinregarray = self.data.xarray
            self.data.ylinregarray = self.data.yarray
            for i in range(len(self.data.xarray) - 1):
                print('self.data.xlinregarray[i] = ', self.data.xlinregarray[i])
                self.data.xlinregarray[i + 1], self.data.ylinregarray[i + 1] =\
                    self.data.linreg(self.data.xlinregarray[i], self.data.ylinregarray[i],
                                     self.data.xlinregarray[i + 1], self.data.ylinregarray[i + 1])

            for i in range(len(self.data.xarray)):
                self.init_rio(self.data.xlinregarray[i], self.data.ylinregarray[i], i)
                # den Ausdruck besser in die Schleife darunter packen, aber dies führt zu fehlern

            for i in range(len(self.data.xarray)):
                #self.init_riox(self.data.xlinregarray[i], self.data.ylinregarray[i], i)
                self.on_rioUpdate(self.data.rioarray[i])


            self.ui.w2.autoRange()
            self.ui.w3.autoRange()

    def on_filter(self):
        with pg.BusyCursor():
            print('on_filter')
            self.filter = self.ui.p.child('filter').child('select filter').value()
            for i in range(len(self.data.xarray)):
                if self.filter == '- no filter -':
                    self.ui.p.child('filter').child('gauss').hide()
                    self.ui.p.child('filter').child('lowess').hide()
                    self.data.Y_filtered[i] = self.data.autoyarray[i]
                if self.filter == 'gauss':
                    self.ui.p.child('filter').child('gauss').show()
                    self.ui.p.child('filter').child('lowess').hide()
                    sigma = self.ui.p.child('filter').child('gauss').child('sigma').value()
                    self.data.Y_filtered[i] = self.data.gauss_filter(self.data.autoyarray[i], sigma)
                if self.filter == 'lowess':
                    self.ui.p.child('filter').child('gauss').hide()
                    self.ui.p.child('filter').child('lowess').show()
                    fraction = self.ui.p.child('filter').child('lowess').child('fraction').value()
                    iteration = self.ui.p.child('filter').child('lowess').child('iteration').value()
                    self.data.Y_filtered[i] = self.data.lowess_filter(self.data.autoyarray[i], fraction, iteration)
                self.update_plot(i)
