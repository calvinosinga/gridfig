
from gridfig.data.data_grid import DataGrid
import numpy as np
from gridfig.style.style_grid import StyleGrid
from typing import Any, Dict, Optional, Tuple, Union, List, Callable, Hashable

import copy


class StyleRule:
    """
    Style rules are used to determine context-dependent styles where a simple dictionary mapping
    is not sufficient. When provided with a datagrid, they evaluate whether the condition to
    provide these styles is met and then return them.
    """

    def __init__(self, 
                 condition: Union[Callable[..., bool], List[Callable[..., bool]]], 
                 args: Optional[Dict[str, Any]] = None, 
                 **kwargs: Any) -> None:
        """
        Args:
            condition: A function or list of functions that return True or False, determining if the rule applies.
            args: Default style arguments to apply when the condition is met.
            kwargs: Additional keyword arguments to include in the style.
        """
        self.args = args if args is not None else {}
        self.args.update(kwargs)
        self.condition = condition if isinstance(condition, list) else [condition]

    def addCondition(self, new_condition: Callable[..., bool]) -> None:
        """Adds a new condition to the list of conditions."""
        self.condition.append(new_condition)

    def rmCondition(self, condition_to_remove: Callable[..., bool]) -> None:
        """Removes a condition from the list of conditions."""
        self.condition = [cond for cond in self.condition if cond != condition_to_remove]

    def __call__(self, *args: Any) -> Dict[str, Any]:
        """
        Generate conditional styles based on data object. Accepts:
        (DataGrid), (DataGrid, int, int), or (DataGrid, int, int, int).
        
        Args:
            args: Inputs to check against the rule's condition(s).
        
        Returns:
            A dictionary of styles if all conditions are met, otherwise an empty dictionary.
        """
        nargs = len(args)
        # Assert valid inputs
        if nargs not in {1, 3, 4}:
            raise ValueError("Expected arguments of length 1, 3, or 4.")
        if not isinstance(args[0], DataGrid): 
            raise TypeError("First argument must be a DataGrid object.")
        if nargs >= 3:
            if not all(isinstance(arg, int) for arg in args[1:3]):
                raise TypeError("Second and third arguments must be integers.")
        if nargs == 4 and not isinstance(args[3], int):
            raise TypeError("Fourth argument must be an integer.")

        for cond in self.condition:
            if not cond(*args):
                return {}

        return self.args



class StyleElement:

    def __init__(
            self,
            args: Optional[Dict[str, Any]] = None, 
            rules : Optional[List[StyleRule]] = None,
            **kwargs: Any
        ) -> None:

        self.name = ''  # Determines the key where arguments for this style element are saved.
        self.args = args if args is not None else {}
        self.args.update(kwargs)
        self.rules = rules if rules is not None else []

    def updateArgs(self, new_args: Optional[Dict[str, Any]] = None, **kwargs) -> None:
        """Updates the default arguments."""
        if new_args is None:
            new_args = {}
        new_args.update(kwargs)
        self.args.update(new_args)
        
    def addRule(self, rule):
        self.rules.append(rule)
        return
    
    def rmRule(self, rule):
        self.rules.remove(rule)
        return
    
    def getStyles(self, dg) -> Dict[str, Any]:
        raise NotImplementedError("getStyles must be implemented in subclass")

    def getName(self) -> str:
        return self.name

    def setDefault(self):
        return
    

class FigSE(StyleElement):

    def __init__(
            self,
            args: Optional[Dict[str, Any]] = None, 
            rules : Optional[List[StyleRule]] = None,
            **kwargs: Any
        ) -> None:
        super().__init__(args, rules, **kwargs)
        self.name = 'figure'
        return

    def getStyles(self, dg) -> Dict[str, Any]:
        args = copy.deepcopy(self.args)

        for rule in self.rules:
            new_args = rule(dg)
            if new_args:
                args.update(new_args)
                
        return args
    

class Layout(FigSE):

    def __init__(self, args: Optional[Dict[str, Any]] = None, **kwargs: Any) -> None:
        super().__init__(args, **kwargs)
        self.name = 'layout'
        self.NEED_KEYS = {'top', 'bottom', 'left', 'right', 'panel_height', 'panel_width', 'wspace', 'hspace'}
        self.OPT_KEYS = {'height_ratios', 'width_ratios'}
    def updateArgs(self, new_args = None, **kwargs):

        if new_args is None:
            new_args = {}
        new_args.update(kwargs)

        keys = new_args.keys()

        # check new keys are allowed
        for k in keys:
            if k not in self.NEED_KEYS and k not in self.OPT_KEYS:
                raise ValueError(f"{k} argument is not allowed for Layout...")
            else:
                self.args[k] = new_args[k]
        return
        
    def setAllMargins(self, margin_size):
        self.updateArgs(top = margin_size, bottom = margin_size, left = margin_size, right = margin_size)
        return

    def setSquarePanels(self, panel_size):
        self.updateArgs(panel_width = panel_size, panel_height = panel_size)
        return
    
    def setPadding(self, pad):
        self.updateArgs(wspace = pad, hspace = pad)
        return
    
    def getStyles(self, dg):
        for k in self.NEED_KEYS:
            if k not in self.args:
                raise ValueError(f"{k} must be defined in layout")
        return super().getStyles(dg)
        
        


class PanelSE(StyleElement):

    def __init__(
            self,
            args: Optional[Dict[str, Any]] = None, 
            rules : Optional[List[StyleRule]] = None,
            **kwargs: Any
        ) -> None:
        super().__init__(args, rules, **kwargs)
        self.name = 'axis'
        return

    def getStyles(
            self, 
            dg : DataGrid, 
            i : int,
            j : int
        ) -> Dict[str, Any]:

        args = copy.deepcopy(self.args)

        for rule in self.rules:
            new_args = rule(dg, i, j)
            if new_args:
                args.update(new_args)
                
        return args

    def forAllPanels(self) -> bool:
        # whether or not the element is the same for all panels
        # if there are no rules, then this must be the same for all panels

        return len(self.rules) == 0

class Legend(PanelSE):
    """
    Styles for legends, typically applied at the figure level. Legend differs from some
    of the other elements because it contains a reserved key. This is a key that is not
    intended to be passed into the backend or the gridfig, but is instead interpreted 
    by the style manager
    """
    def __init__(self, args: Optional[Dict[str, Any]] = None, **kwargs: Any) -> None:
        super().__init__(args, **kwargs)
        self.name = 'legend'
        # we reserve the key _slc to indicate the panels that should contain a legend
        self.slc_key = '_slc'

    def setVisiblePanels(self, panel_slc):
        # create rule that legends are only visible in these panels

        def visibleCondition(dg, i, j):
            bool_arr = np.zeros(dg.getShape(), bool)
            bool_arr[panel_slc] = True
            return bool_arr[i, j]


        visRule = StyleRule(visibleCondition, visible = True)
        self.rules.append(visRule)
        return

    def setPanels(self, panels, args):
        # create rule with args, included in certain panels.
        return
        



class Ticks(PanelSE):
    """
    Styles for tick marks.
    """
    def __init__(self, args: Optional[Dict[str, Any]] = None, rules : Optional[List[StyleRule]] = None, **kwargs: Any) -> None:
        super().__init__(args, rules, **kwargs)
        self.name = 'ticks'

    def setDefault(self):
        def _noBottom(dg, i, j):
            nrows, _ = dg.getShape()
            return not (i == nrows - 1)
                
        self.rules.append(StyleRule(_noBottom, labelbottom = False))

        def _noLeft(dg, i, j):
            return not (j == 0)
        self.rules.append(StyleRule(_noLeft, labelleft = False))
        return 




class Edges(PanelSE):
    """
    Styles for axis edges or splines.
    """
    def __init__(self, args: Optional[Dict[str, Any]] = None, rules : Optional[List[StyleRule]] = None, **kwargs: Any) -> None:
        super().__init__(args, rules, **kwargs)
        self.name = 'edges'


class Grid(PanelSE):

    def __init__(self, args = None, rules : Optional[List[StyleRule]] = None, **kwargs):
        super().__init__(args, rules, **kwargs)
        self.name = 'grid'







class VizSE(StyleElement):
    """
    Styles for individual plot elements (lines, contours, etc.), with additional methods for finer control.
    """
    def __init__(self, args: Optional[Dict[str, Any]] = None, **kwargs: Any) -> None:
        super().__init__(args, **kwargs)
        self.panel_style: Dict[Any, Dict[Any, Dict[str, Any]]] = {}
        self.name = 'plot'


    def addPanelStyle(self, panel_prop: Hashable, panel_val: Union[Hashable, List[Hashable]], 
                      args: Optional[Dict[str, Any]] = None, **kwargs: Any) -> None:
        """
        Adds style arguments for specific panel properties and values. This is a common type of
        context-dependent plot arg, where labels and colors are determined based on what is
        being compared in the panel. Note that this is separate from the type_styles dict
        (set using setTypeStyle) which uses only a data container's plot_type to determine
        plot arguments.

        Args:
            panel_prop: A hashable panel property.
            panel_val: A hashable value or list of values for the panel property.
            args: Style arguments to apply.
        """
        args = args if args is not None else {}
        args.update(kwargs)
        if not args:  # Exit if empty
            return
        
        if panel_prop not in self.panel_style:
            self.panel_style[panel_prop] = {}
        
        if not isinstance(panel_val, list):
            panel_val = [panel_val]
        
        for val in panel_val:
            if val not in self.panel_style[panel_prop]:
                self.panel_style[panel_prop][val] = args



    def getStyles(self, dg: DataGrid, panel_i: int, panel_j: int, dc_idx: int) -> Dict[str, Any]:
        """
        Returns style arguments for a specific plot element.
        Args:
            dg: The data grid object.
            panel_i: Panel row index.
            panel_j: Panel column index.
            dc_idx: Index of the data container in the panel.
        """
        ret_args = copy.deepcopy(self.args)
        
        for rule in self.rules:
            ret_args.update(rule(dg, panel_i, panel_j, dc_idx))

        panel_prop = dg.panels[panel_i, panel_j].panel_prop
        df = dg.panels[panel_i, panel_j][dc_idx] # pandas dataframe

        if panel_prop in self.panel_style:
            if panel_prop in df.columns:
                panel_val = df[panel_prop].unique()[0]
                if panel_val in self.panel_style[panel_prop]:
                    ret_args.update(self.panel_style[panel_prop][panel_val])

        return ret_args


class StyleManager:

    def __init__(self):
        self.elements = {}
        return
    
    def addElement(self, se : Union[StyleElement, List[StyleElement]]):
        if isinstance(se, StyleElement):
            self.elements[se.getName()] = se
        else:
            for elm in se:
                self.elements[elm.getName()] = elm
        return
    
    def getStyleGrid(
            self, 
            dg : DataGrid
        ) -> StyleGrid:
        """_summary_

        Args:
            dg (_type_): _description_
        """
        sg = StyleGrid(dg)
        nrows, ncols = dg.getShape()
        # iterate through each element
        for name, elm in self.elements.items():
            if isinstance(elm, FigSE):
                sg.setFigStyle(name, elm.getStyles(dg))
        
            elif isinstance(elm, PanelSE):
                if elm.forAllPanels():
                    sg.setAxStyleAll(name, elm.getStyles(dg, 0, 0))
                else:
                    for i in range(nrows):
                        for j in range(ncols):
                            sg.setAxStyle((i, j), name, elm.getStyles(dg, i, j))
            
            # elif isinstance(elm, VizSE):
                
        
        return sg