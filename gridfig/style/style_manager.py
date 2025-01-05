from gridfig.data.data_grid import DataGrid
import gridfig.style.style_elements as stel
from typing import Callable
import numpy as np

class StyleManager:
    """
    The style manager class comprises two tasks. First, users can define various default
    and context-dependent styles, and the style manager will map these specifications onto the 
    corresponding style elements. The style manager provides many useful methods for setting up
    these specifications quickly. Second, a datagrid is provided which yields the context to
    determine the context-dependent styles. A tuple containing dictionaries for the various styles
    is then returned, which is to be interpreted by the backend to map it to the actual visual
    elements. 
    """
    def __init__(self, default_layout = True):
        
        
        self.fargs = stel.FigArgs()
        self.aargs = stel.PanelArgs()
        self.vargs = stel.VizArgs()
        self.ticks = stel.Ticks()
        self.edges = stel.Edges()
        self.grid = stel.Grid()
        self.legend = stel.Legend()
        self.xlabel = stel.XLabel()
        self.ylabel = stel.YLabel()
        self.col_label = stel.ColLabel()
        self.row_label = stel.RowLabel()        
        # add ability to make general notations
        # self.panel_text = stel.PanelText()
        # self.fig_text = stel.FigText()
        
        self.layout = stel.Layout()
        if default_layout:
            # default layout (these need to be set at some point)
            self.layout.updateArgs({
                "panel_width": 3,
                "panel_height": 3,
                "xspace": 0.05,
                "yspace": 0.05,
                "top": 0.2,
                "bottom": 0.2,
                "left": 0.2,
                "right": 0.2,
            })

        self.fig_elements = [self.fargs, self.legend, self.xlabel, self.ylabel, self.layout]
        self.pan_elements = [self.aargs, self.ticks, self.edges, self.grid, self.col_label, self.row_label]
        
        # the text associated with certain prop_type -> prop_val combinations
        # needs to be consistent across style elements, so we have separate
        # way of defining the text. dict of dicts, with prop_type -> prop_val -> name
        # if no name provided, defaults to prop_val

        self.prop_text = {}
        self.label_key = 'label' # some softwares use different kwargs for the labels
        self.color_key = 'color' # some softwares use different kwargs for colors too
        
        self.col_idx = 1
        self.row_idx = 1
        return


    def _setArgs(self, arg_type, args, condition):
        
        if not args: # if args is empty, skip
            return
        
        if not hasattr(self, arg_type):
            raise ValueError(f"incorrect arg_type {arg_type}")
        
        selm = getattr(self, arg_type) # must be a Style Element

        if not isinstance(selm, stel.StyleElement):
            raise TypeError("cannot set arguments of non-StyleElement types (%s)"%type(selm))
        # if condition is none, then we set args as default
        if condition is None:
            selm.updateArgs(args)
        # if condition is a string, set TypeStyle
        elif isinstance(condition, str):
            selm.addTypeStyle(args)
        # if condition is a method, then create StyleRule and add it
        elif isinstance(condition, Callable):
            sr = stel.StyleRule(condition, args)
            selm.addRule(sr)
        else:
            raise TypeError("condition type not understood %s"%type(condition))
        return
    
    def setFigArgs(self, args, condition = None,  **kwargs):
        args.update(kwargs)
        
        self._setArgs('fargs', args, condition)
        return
    
    # td: repeat setFigArgs method but for pargs, ticks, edges, grid, legend, figtext, paneltext, and layout. Remaining elements will require special setters
    
    
    def setVizArgs(self, *params, **kwargs):
        
        
        # td: if params does not have length 1, raise error

        # td: if first argument is not a dictionary, raise error
        params[0].update(kwargs)

        # if we have one or two arguments, should behave like other "setArgs" functions
        if len(params) == 1 or len(params) == 2:
            self._setArgs('vargs', *params)
            return
        # the only other allowed number of arguments is 3
        elif len(params) == 3:
            # if the second is a string, and third is a list or str, we use addPanelStyle
            if isinstance(params[1], str) and isinstance(params[2], (str, list)):
                self.vargs.addPanelStyle(params[1], params[2]. params[0])
                return
            elif isinstance(params[1], dict) and isinstance(params[2], dict):
                self.vargs.addMatchRule(params[1], params[2], params[0])
                return

        # td: raise error that input was not correct. print different messages if there were too many arguments or if the types of the inputs were incorrect.
        return
    
    def setLegendAxes(self, slc, condition = None):
        self._setArgs('legend', {self.legend.getSliceKey():slc}, condition)
        return
      
    
    # we expect many xy labels to be set, add function for smoother use
    def setXYLabels(self, x_label = None, y_label = None, condition = None):
        if x_label is not None:
            self._setArgs('xlabel', {self.xlabel.getTextKey(): x_label}, condition)

        if y_label is not None:
            self._setArgs('ylabel', {self.ylabel.getTextKey(): y_label}, condition)
        return
    
    def setXYLabelArgs(self, args, condition = None, which = 'both', **kwargs):
        args.update(kwargs)

        # make sure that which can only be ['both', 'x', or 'y']
        if which == 'both' or which == 'x':
            self._setArgs('xlabel', args, condition)

        if which == 'both' or which == 'y':
            self._setArgs('ylabel', args, condition)

        return

    def setRowLabelIdx(self, idx):
        self.row_idx = idx
        return
    
    def setColLabelIdx(self, idx):
        self.col_idx = idx
        return
    
    def setRCLabels(self, row_label = None, col_label = None, condition = None):
        if row_label is not None:
            self._setArgs('row_label', {self.xlabel.getTextKey(): row_label}, condition)

        if col_label is not None:
            self._setArgs('col_label', {self.ylabel.getTextKey(): col_label}, condition)
        return
    
    def setRCLabelArgs(self, args, condition = None, which = 'both', **kwargs):
        args.update(kwargs)

        # make sure that which can only be ['both', 'col', or 'row']
        if which == 'both' or which == 'col':
            self._setArgs('row_label', args, condition)

        if which == 'both' or which == 'row':
            self._setArgs('col_label', args, condition)

        return
    
    def displayAs(self, prop, prop_vals, names):
        if not isinstance(prop_vals, list):
            prop_vals = [prop_vals]
        if not isinstance(names, list):
            names = [names]
        
        # check that text and prop_val have same length
        if prop not in self.prop_text:
            self.prop_text[prop] = {}

        for i in range(len(prop_vals)):
            self.prop_text[prop][prop_vals[i]] = names[i]
            
        return
    
    def setColors(self, prop, colors, vals):


        if isinstance(colors, str):
            import seaborn as sns
            colors = sns.color_palette(colors, len(vals))
            

        for i in range(len(vals)):
            self.setVizArgs({self.color_key:colors[i]}, prop, vals[i])
        
        return
    
    
    def getStyles(self, dg):
        """_summary_

        Args:
            dg (_type_): _description_
        """
        # get the fig-level style elements
        fig_dict = {}
        for stem in self.fig_elements:
            styles = stem.getStyles(dg)
            # even if args is empty, we still pass it - the gridfig will interpret it
            # and might be changed later by user
            fig_dict[stem.getName()] = styles
        
        # make arrays of panel and viz styles
        shape = dg.getShape()
        panel_style_arr = np.empty(shape, dtype = object)
        viz_style_arr = np.empty(shape, dtype = object)
        for i in range(shape[0]):
            for j in range(shape[1]):
                panel_dict = {}
                for stem in self.pan_elements:
                    styles = stem.getStyles(dg, i, j)
                    panel_dict[stem.getName()] = styles
                panel_style_arr[i, j] = panel_dict

                viz_style_arr[i, j] = []
                
                for k in range(len(dg.panels[i, j])):
                    # we assume here that vargs is the only viz-level style element (seems safe to me)
                    styles = stem.getStyles()
                    
                    viz_style_arr[i, j].append()
        
        return fig_dict, 
    
