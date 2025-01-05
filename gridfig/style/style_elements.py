import copy
from typing import Any, Callable, Dict, List, Optional, Union, Hashable
from gridfig.data.data_grid import DataGrid

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
    """
    A base class for defining default and context-dependent styles.

    There are two methods of defining context-dependent styles:
    1. Using `rules`, a list of StyleRule objects. If a condition is met, they provide given arguments.
    2. Using `type_style`, a dictionary where data grid attributes (e.g., strings) are keys for styles.
       This method is faster but less flexible. Arguments from `rules` overwrite `type_style` as
       they require a more intentional implementation.

    """
    def __init__(self, args: Optional[Dict[str, Any]] = None, **kwargs: Any) -> None:
        self.name = ''  # Determines the key where arguments for this style element are saved (see gridfig).
        self.args = args if args is not None else {}
        self.args.update(kwargs)
        self.rules: List[StyleRule] = []
        self.type_style: Dict[str, Dict[str, Any]] = {}

    def addRule(self, rule: StyleRule) -> None:
        """Adds a StyleRule to the rules list."""
        self.rules.append(rule)

    def rmRule(self, rule: StyleRule) -> None:
        """Removes a StyleRule from the rules list."""
        self.rules = [r for r in self.rules if r != rule]

    def addTypeStyle(self, type_val, args = None, **kwargs):
        """_summary_

        Args:
            type_val (_type_): _description_
            args (_type_): _description_
        """
        args = args if args is not None else {}
        args.update(kwargs)
        self.type_style[type_val] = args
        return
    
    def updateArgs(self, new_args: Dict[str, Any]) -> None:
        """Updates the default arguments."""
        self.args.update(new_args)

    def getName(self) -> str:
        return self.name
    
    def getStyles(self, dg: DataGrid) -> Dict[str, Any]:
        """
        Returns style arguments based on the data grid and defined rules. Note that
        this super class ignores the type_style variable - only subclasses handle where
        to find the keys for that within the DataGrid.

        Args:
            dg: The data grid object.
        """
        ret_args = copy.deepcopy(self.args)
        for rule in self.rules:
            ret_args.update(rule(dg))
        
        
        return ret_args


class FigArgs(StyleElement):
    """
    Styles for the figure, which consists of the space outside or between panels.
    """
    def __init__(self, args: Optional[Dict[str, Any]] = None, **kwargs: Any) -> None:
        super().__init__(args, **kwargs)
        self.name = 'fig'

    def getStyles(self, dg: DataGrid) -> Dict[str, Any]:
        """
        Returns style arguments for the figure.
        Args:
            dg: The data grid object.
        """
        ret_args = super().getStyles(dg)
        for ft in dg.fig_type:  # Iterate through data grid figure types.
            if ft in self.type_style:
                ret_args.update(self.type_style[ft])
            else:
                print(f"Warning: Figure type '{ft}' not found in type_style.")
        return ret_args


class PanelArgs(StyleElement):
    """
    Styles for each panel.
    """
    def __init__(self, args: Optional[Dict[str, Any]] = None, **kwargs: Any) -> None:
        super().__init__(args, **kwargs)
        self.name = 'axis'

    def getStyles(self, dg: DataGrid, panel_i: int, panel_j: int) -> Dict[str, Any]:
        """
        Returns style arguments for a specific panel.
        Args:
            dg: The data grid object.
            panel_i: Panel row index.
            panel_j: Panel column index.
        """
        ret_args = super().getStyles(dg)
        for at in dg.panels[panel_i, panel_j].axis_types:
            if at in self.type_style:
                ret_args.update(self.type_style[at])
            else:
                print(f"Warning: Axis type '{at}' not found in type_style.")
        return ret_args


class VizArgs(StyleElement):
    """
    Styles for individual plot elements (lines, contours, etc.), with additional methods for finer control.
    """
    def __init__(self, args: Optional[Dict[str, Any]] = None, **kwargs: Any) -> None:
        super().__init__(args, **kwargs)
        self.panel_style: Dict[Any, Dict[Any, Dict[str, Any]]] = {}
        self.name = 'plot'

    def addMatchRule(self, in_attrs: Optional[Dict[str, Any]] = None, 
                     rm_attrs: Optional[Dict[str, Any]] = None, 
                     plot_args: Optional[Dict[str, Any]] = None, 
                     **kwargs: Any) -> None:
        """
        Adds a style rule for data containers matching certain properties.
        Args:
            in_attrs: Attributes that must be present in the data container.
            rm_attrs: Attributes that must not be present in the data container.
            plot_args: Arguments to apply if the condition is met.
        """
        in_attrs = in_attrs or {}
        rm_attrs = rm_attrs or {}
        plot_args = plot_args or {}
        plot_args.update(kwargs)

        def _matchCondition(dg: DataGrid, panel_i: int, panel_j: int, dc_idx: int) -> bool:
            return dg.panels[panel_i, panel_j][dc_idx].isMatch(in_attrs, rm_attrs)

        self.rules.append(StyleRule(_matchCondition, plot_args))

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

    def rmPanelStyle(self, panel_prop: Hashable, panel_val: Hashable) -> None:
        """
        Removes a specific panel style by property and value.
        Args:
            panel_prop: The panel property to remove.
            panel_val: The specific value of the panel property to remove.
        """
        if panel_prop in self.panel_style and panel_val in self.panel_style[panel_prop]:
            del self.panel_style[panel_prop][panel_val]
            if not self.panel_style[panel_prop]:  # Remove property if empty
                del self.panel_style[panel_prop]

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

        panel_prop = dg.panels[panel_i, panel_j].getPanelProp()
        dc = dg.panels[panel_i, panel_j][dc_idx]

        for pt in dc.plot_types:
            if pt in self.type_style:
                ret_args.update(self.type_style[pt])
            else:
                print(f"Warning: Plot type '{pt}' not found for this panel.")

        if panel_prop in self.panel_style:
            if dc.hasProp(panel_prop):
                panel_val = dc.getProp(panel_prop)
                if panel_val in self.panel_style[panel_prop]:
                    ret_args.update(self.panel_style[panel_prop][panel_val])

        return ret_args


class Layout(FigArgs):
    """
    The layout of the panels when using a grid, with the following configurable properties:
        - panel_width, panel_height: Size of panels in inches (default 3 inches each).
        - xspace, yspace: Empty space between panels (units of average panel size).
        - top, bottom, left, right: Borders in units of average panel size.
    """
    def __init__(self) -> None:
        super().__init__()
        self.name = 'layout'


    def getStyles(self, dg: DataGrid) -> Dict[str, Any]:
        """
        Returns layout styles for the figure.
        Args:
            dg: The data grid object.
        """
        required_keys = ["panel_width", "panel_height", "xspace", "yspace", "top", "bottom", "left", "right"]
        for key in required_keys:
            if key not in self.args:
                raise KeyError(f"Missing required layout key: '{key}'")
        return super().getStyles(dg)


class Ticks(PanelArgs):
    """
    Styles for tick marks.
    """
    def __init__(self, args: Optional[Dict[str, Any]] = None, **kwargs: Any) -> None:
        super().__init__(args, **kwargs)
        self.name = 'ticks'


class Edges(PanelArgs):
    """
    Styles for axis edges or splines.
    """
    def __init__(self, args: Optional[Dict[str, Any]] = None, **kwargs: Any) -> None:
        super().__init__(args, **kwargs)
        self.name = 'edges'

class Grid(PanelArgs):

    def __init__(self, args = None, **kwargs):
        super().__init__(args, **kwargs)
        self.name = 'grid'

class Legend(FigArgs):
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

        
        
    def getSliceKey(self) -> str:
        """
        Updates the slice indicating which panels should contain legends.
        Args:
            new_slice: New slice definition.
        """
        return self.slc_key

    
#### ANNOTATIONS ######################################################################

class Annotation(StyleElement):
    """
    Annotations are unique style elements, in the sense that it's much less useful to 
    define their positions before seeing the figure like the other elements. In other 
    words, the properties of the data do not determine its position, but rather the
    actual data itself and the whitespace around it
    
    Intended to be superclass and not instantiated directly by user.
    """
    def __init__(self, args: Optional[Dict[str, Any]] = None, **kwargs: Any) -> None:
        super().__init__(args, **kwargs)
        self.name = 'annot'

        self.pos_key = 'pos'
        self.text_key = 'text'

        # these should always have something assigned to it
        self.args[self.text_key] = ''
        self.args[self.pos_key] = (0, 0)
        return

    def getPosKey(self):
        return self.pos_key
    
    def getTextKey(self):
        return self.text_key

    
class FigText(Annotation, FigArgs):
    """
    General representation of annotations for the figure, position is in figure units.
    """
    def __init__(self, args: Optional[Dict[str, Any]] = None, **kwargs: Any) -> None:
        
        super().__init__(args, kwargs)
        self.name = 'fig_text'
        
class PanelText(Annotation, PanelArgs):
    """
    Text placed within panels, in axis units
    """

    def __init__(self, args: Optional[Dict[str, Any]] = None, **kwargs: Any) -> None:
        
        super().__init__(args, kwargs)
        self.name = 'axis_text'


class XLabel(FigText):
    def __init__(self, args: Optional[Dict[str, Any]] = None, **kwargs: Any) -> None:
        super().__init__(args, **kwargs)
        self.name = 'x_label'

    


class YLabel(FigText):
    def __init__(self, args: Optional[Dict[str, Any]] = None, **kwargs: Any) -> None:
        super().__init__(args, **kwargs)
        self.name = 'y_label'
        

class ColLabel(PanelText):
    def __init__(self, args: Optional[Dict[str, Any]] = None, **kwargs: Any) -> None:
        super().__init__(args, **kwargs)
        self.name = 'col_label'
         # annotations generally only needed in one row, so we reserve a key, defaults to one
        self.idx_key = '_idx'
        self.args[self.idx_key] = 1

    

    def getStyles(self, dg, panel_i, panel_j):
        if panel_i == self.args[self.idx_key]:
            return super().getStyles(dg, panel_i, panel_j)
        else:
            return {}
         


class RowLabel(PanelText):
    def __init__(self, args: Optional[Dict[str, Any]] = None, **kwargs: Any) -> None:
        super().__init__(args, **kwargs)
        self.name = 'row_label'
        self.idx_key = '_idx'
        self.args[self.idx_key] = 1


    def getStyles(self, dg, panel_i, panel_j):
        if panel_i == self.args[self.idx_key]:
            return super().getStyles(dg, panel_i, panel_j)
        else:
            return {}