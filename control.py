import os
import pyqtgraph as pg
import numpy as np
from statsmodels.nonparametric.smoothers_lowess import lowess

class Control:

    def __init__(self, data, ui):
        self.data = data
        self.ui = ui

        self.ui.p.child('select folder').sigActivated.connect(self.onSelectBtn)