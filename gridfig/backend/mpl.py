from gridfig.backend.backend import Backend
import matplotlib.pyplot as plt
import numpy as np

from gridfig.data.data_grid import DataGrid
from gridfig.style.style_grid import StyleGrid

class MPL(Backend):

    def __init__(self, dg : DataGrid, sg : StyleGrid):
        super().__init__()
        self.sg = sg
        self.dg = dg

        

    def makeFig(self):
        lo = self.sg.fstyles['layout']
        fargs = self.sg.fstyles['figure']
        nrows, ncols = self.dg.getShape()
        figsize = self._getFigsize(lo, nrows, ncols)
        fig = plt.Figure(figsize = figsize, **fargs)
        figwidth = figsize[0]; figheight = figsize[1]
        if 'height_ratios' not in lo:
            hrs = [1] * nrows
        else:
            hrs = lo['height_ratios']
        
        if 'width_ratios' not in lo:
            wrs = [1] * ncols
        else:
            wrs = lo['width_ratios']
        
        yb = [lo['top'], lo['bottom']]; xb = [lo['left'], lo['right']]
        hs = [lo['hspace']] * nrows; ws = [lo['wspace']] * ncols

        panel_width = lo['panel_width']
        panel_height = lo['panel_height']
        width_ratios = wrs * panel_width; height_ratios = hrs * panel_height
        xborder = xb * panel_width; yborder = yb * panel_height
        wspace = ws * panel_width; hspace = hs * panel_height

        axes = np.empty((nrows, ncols), dtype = object)
        for i in range(nrows):
            for j in range(ncols):
                # a label makes each axis unique - otherwise mpl will
                # return a previously made axis
                
                # ax = fig.add_subplot(label = str((i, j)))
                height = height_ratios[i]
                width = width_ratios[j]
                
                total_hspace = np.sum(hspace[:i])
                total_heights = np.sum(height_ratios[:i+1])
                total_widths = np.sum(width_ratios[:j])
                total_wspace = np.sum(wspace[:j])
                
                bot = figheight - yborder[0] - total_hspace - total_heights
                left = xborder[0] + total_widths + total_wspace
                axdim = [left / figwidth, bot / figheight, 
                        width / figwidth, height / figheight]
                # ax = fig.add_subplot(label = str((i, j)))
                # ax.set_position(axdim)
                ax = self._createAx(fig, axdim, i, j)
                
                axes[i, j] = ax
        self.fig = fig
        self.axes = axes

        return
    
    def _createAx(self, fig, position, i, j):
        ax = fig.add_subplot(label = str((i, j)))
        ax.set_position(position)

        def _setStyle(se_name, fn):
            if se_name in self.sg.astyles_all:
                fn(**self.sg.astyles_all[se_name])
            
            if se_name in self.sg.astyles[i, j]:
                fn(**self.sg.astyles[i,j][se_name])
            return
        
        _setStyle('ticks', ax.tick_params)
        _setStyle('axis', ax.set)
        for side in ax.spines.keys():

            _setStyle('edges', ax.spines[side].set)
        _setStyle('grid', ax.grid)
        _setStyle('legend', ax.legend)
        return ax


    def _getFigsize(self, lo, nrows, ncols):

        if 'height_ratios' not in lo:
            hrs = [1] * nrows
        else:
            hrs = lo['height_ratios']
        
        if 'width_ratios' not in lo:
            wrs = [1] * ncols
        else:
            wrs = lo['width_ratios']
        
        yb = [lo['top'], lo['bottom']]; xb = [lo['left'], lo['right']]
        hs = lo['hspace']; ws = lo['wspace']

        panel_width = lo['panel_width']
        panel_height = lo['panel_height']
        width_ratios = wrs * panel_width; height_ratios = hrs * panel_height
        xborder = xb * panel_width; yborder = yb * panel_height
        wspace = ws * panel_width; hspace = hs * panel_height
        
        total_widths = np.sum(width_ratios)
        total_wspace = np.sum(wspace)
        wborder_space = np.sum(xborder)

        total_heights = np.sum(height_ratios)
        total_hspace = np.sum(hspace)
        hborder_space = np.sum(yborder)
        
        # get figwidth and figheight in inches
        figwidth = total_widths + total_wspace + wborder_space
        figheight = total_heights + total_hspace + hborder_space

        return [figwidth, figheight]
    
    def setPlotFunc(self, pfunc):

        return


class VizContainer:

    def __init__(self, df, style):
        self.df = df
        self.style = style
        self.pfunc = None

    def setPfunc(self, pfunc):
        self.pfunc = pfunc



class MPLPfunc:

    def __init__(self):
        return
    
    def __call__(self, *args, **kwds):
        pass