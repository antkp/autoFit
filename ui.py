import pyqtgraph as pg
from pyqtgraph.dockarea import *
from pyqtgraph.Qt import QtCore, QtGui
from pyqtgraph.parametertree import Parameter, ParameterTree



class PParameter (pg.parametertree.Parameter):

    def __init__(self, chparent, sigValueChanged, child, addChild):
        super().__init__()



class Ui:
    def __init__(self, main_window):
        self.path = ''

        self.params1 = [
            {'name': 'select folder', 'type': 'action', 'tip': "select folder"},
            {'name': 'coeff scale X', 'type': 'float', 'value': 5.0, 'step': 0.001},
            {'name': 'coeff scale Y', 'type': 'float', 'value': 1.0, 'step': 0.001}
            ]

        self.params2 = [
            {'name': 'select filter', 'type': 'list', 'values':
                ['- no filter -', 'gauss', 'savitzky–golay', 'lowess'], 'value': '- no filter -',
                'tip': 'https://docs.scipy.org/doc/scipy/reference/generated/scipy.ndimage.gaussian_filter1d.html'},
            {'name': 'gauss', 'type': 'group', 'expanded': True, 'visible': False, 'children': [
                {'name': 'sigma', 'type': 'float', 'value': 3.0, 'limits': (0.0, 6.0), 'step': 0.1}]},
            {'name': 'savitzky–golay', 'type': 'group', 'expanded': True, 'visible': False,
                'tip': 'https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.savgol_filter.html',
                'children': [
                    {'name': 'size', 'type': 'int', 'value': 31, 'limits': (11, 501), 'step': 1},
                    {'name': 'order', 'type': 'int', 'value': 3, 'limits': (2, 10), 'step': 1}]},
            {'name': 'lowess', 'type': 'group', 'expanded': True, 'visible': False,
                'tip': 'https://www.statsmodels.org/stable/generated/statsmodels.nonparametric.smoothers_lowess.lowess.html',
                'children': [
                    {'name': 'fraction', 'type': 'float', 'value': 0.025, 'limits': (0.0, 1.0), 'step': 0.01},
                    {'name': 'iteration', 'type': 'int', 'value': 0, 'limits': (0, 5), 'step': 1}]}]

        self.p = PParameter.create(name='params', type='group', children=self.params1)
        self.pp = PParameter.create(name='filter', type='group', children=self.params2)
        self.p.addChild(self.pp)

        self.area = DockArea()
        main_window.setCentralWidget(self.area)
        main_window.resize(1200, 700)
        main_window.setWindowTitle('LT_1.01 - BETA')
        self.filename = ''
        pg.setConfigOption('background', ('#141414'))
        pg.setConfigOption('foreground', (250, 250, 250))

        self.d1 = Dock("config", size=(300, 700))
        self.d1.hideTitleBar()
        self.d2 = Dock("raw data", size=(900, 100))
        self.d2.hideTitleBar()
        #self.d3 = Dock("raw data", size=(900, 100))
        #self.d3.hideTitleBar()

        self.area.addDock(self.d1, 'left')
        self.area.addDock(self.d2, 'right')
        #self.area.addDock(self.d3, 'bottom', self.d2)

        self.t = ParameterTree()
        self.t.setParameters(self.p, showTop=False)

        self.w1 = pg.LayoutWidget()
        self.w1.addWidget(self.t)
        self.d1.addWidget(self.w1)

        self.w2 = pg.PlotWidget(title="-- no data --")
        self.w2.setAutoPan(y=True, x=True)

        self.region = pg.LinearRegionItem(values=(0, 1), brush=(70, 70, 70, 70), movable=True)

        self.wi2Text = '  === p0 ===    ' + '\n' + '  === p1 ===    '
        self.wi2 = QtGui.QLabel(self.wi2Text)
        self.wi2.setFont(QtGui.QFont('Menlo', 12, QtGui.QFont.Bold))
        self.wi2.setAlignment(QtCore.Qt.AlignLeft)
        self.wi2.setAlignment(QtCore.Qt.AlignTop)

        self.d2.addWidget(self.w2, row=0, col=0)
        self.d2.addWidget(self.wi2, row=0, col=1)

        self.r4 = pg.ROI([0, 0], [10, 0], resizable=False, removable=True)
        self.r4.addRotateHandle([1, 0], [0, 1])
        self.r4.addTranslateHandle([0, 0], [0.5, 0.5])


    def adFolderPath(self, directory):
        path = dict(name='path', type='text', value=directory, visible=True)
        self.p.addChild(path)

    def adNewlimb(self, par):

        filename = dict(name=par.filename, type='group', removable=True, renamable=False, expanded=False)
        m = par.m
        color = dict(name=str(m)+'_color', type='color', value=par.color, tip='plot color', removable=True, renamable=False)
        # scalex = dict(name=str(m)+'_scale X', type='float', value=par.xscale, tip="scale coeff x-axis",
        #                removable=True, renamable=False)
        # scaley = dict(name=str(m)+'_scale Y', type='float', value=par.yscale, tip="scale coeff x-axis",
        #               removable=True, renamable=False)
        offsetx = dict(name=str(m)+'_offset X', type='float', value=par.offsetx, tip="offsetf in x-dir",
                       removable=True, renamable=False)
        offsety = dict(name=str(m)+'_offset Y', type='float', value=par.offsety, tip="offset in y-dir",
                       removable=True, renamable=False)
        tilt = dict(name=str(m)+'_tilt', type='float', value=par.tilt, tip="tilt from the right",
                        removable=True, renamable=False)

        self.more = [color, offsetx, offsety, tilt]

        self.p.addChild(filename)
        for i in self.more:
            self.p.child(par.filename).addChild(i)

