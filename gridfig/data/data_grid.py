import numpy as np
from gridfig.data.panel import Panel
from gridfig.data.panel_func import PanelFunc
from typing import Hashable, Union, List, Iterable, Optional, Any

class DataGrid:
    """
    Represents a 2D array of Panel objects. Provides methods for managing and manipulating 
    the organization of panels and includes 'fig_types' to define default styles for figures.
    """

    def __init__(self, 
                 panels: Union[List[List[Panel]], np.ndarray],
                 row_prop: str,
                 col_prop: str, 
                 fig_types: Optional[Iterable[Hashable]] = None):
        """
        Initialize the DataGrid with a 2D array of Panel objects.

        :param panels: A 2D array (list of lists) of Panel objects. Can also be a numpy array.
        :param fig_types: An iterable of hashable types that define default styles for the figure.
        """
        if not all(isinstance(row, list) for row in panels):
            raise ValueError("Panels must be a 2D array (list of lists).")
        if not all(isinstance(panel, Panel) for row in panels for panel in row):
            raise ValueError("All elements in panels must be instances of the Panel class.")
        
        # Transform panels into a 2D numpy array if not already
        self.panels: np.ndarray = np.array(panels, dtype=object)
        self.row_prop = row_prop
        self.col_prop = col_prop
        self.fig_types: List[Hashable] = list(fig_types) if fig_types else []

    def getShape(self):
        return self.panels.shape
    
    def addType(self, ftype: Union[Hashable, Iterable[Hashable]]) -> None:
        """
        Add one or more figure types to fig_types.

        :param ftype: A hashable type or an iterable of hashable types to add.
        """
        if isinstance(ftype, Iterable) and not isinstance(ftype, str):
            for f in ftype:
                self.addType(f)
        elif isinstance(ftype, Hashable):
            self.fig_types.append(ftype)
        else:
            print("WARNING: Given figure type is not hashable.")
            return

    def hasType(self, ftype: Hashable) -> bool:
        """
        Check if a specific figure type is present in fig_types.

        :param ftype: The figure type to check.
        :return: True if ftype is in fig_types, False otherwise.
        """
        return ftype in self.fig_types

    def rmType(self, ftype: Hashable) -> None:
        """
        Remove a specific figure type from fig_types.

        :param ftype: The figure type to remove.
        """
        self.fig_types.remove(ftype)

    def _getSlc(self, slc: Optional[Union[slice, str, List[str]]]) -> np.ndarray:
        """
        Interprets slc and returns the panels from the 2D array that slc is trying to access.

        :param slc: Can be an index, slice, string, list of strings, or None.
        :return: Selected panels as a numpy array.
        """
        if slc is None:
            return self.panels

        if isinstance(slc, (str, list)):
            if isinstance(slc, str):
                slc = [slc]
            return np.array([
                panel for row in self.panels for panel in row
                if panel.row_val in slc or panel.col_val in slc
            ]).reshape(-1, 1)

        return self.panels[slc]

    def adjustData(self, 
                   panel_func: PanelFunc, 
                   slc: Optional[Union[slice, str, List[str]]] = None) -> None:
        """
        Apply a function to selected panels.

        :param panel_func: A function that takes a Panel object as input.
        :param slc: The selection of panels to apply the function to. Defaults to None.
        """
        selected_panels = self._getSlc(slc)
        for panel in np.nditer(selected_panels, flags=["refs_ok"]):
            panel_func(panel.item())

    def rotatePanels(self, dir: str) -> None:
        """
        Rotate the panel array 90 degrees in the specified direction.

        :param dir: Direction to rotate ('cw' for clockwise, 'ccw' for counterclockwise).
        """
        if dir not in ["cw", "ccw"]:
            raise ValueError("Invalid direction. Use 'cw' for clockwise or 'ccw' for counterclockwise.")
        
        self.panels = np.rot90(self.panels, k=-1 if dir == "cw" else 1)

    def flipPanels(self) -> None:
        """
        Flip the axes of the panel array (transpose the array).
        """
        self.panels = self.panels.T

    def invertPanels(self, axis: int) -> None:
        """
        Invert the order of the panels array along the specified axis.

        :param axis: Must be 0 (row) or 1 (column).
        """
        if axis not in [0, 1]:
            raise ValueError("Invalid axis. Use 0 for rows or 1 for columns.")
        
        self.panels = np.flip(self.panels, axis=axis)

    def rowOrder(self, order: Union[List[int], List[str]]) -> None:
        """
        Reorder the rows of the panel array based on the specified order.

        :param order: A list of integers specifying the new row order, or a list of strings
                    specifying row values to match using getSlc.
        """
        if all(isinstance(o, int) for o in order):
            # Reorder rows by indices
            self.panels = self.panels[order]
        elif all(isinstance(o, str) for o in order):
            # Reorder rows by matching row values
            reordered_rows = []
            for row_val in order:
                row_match = self._getSlc(row_val)
                if row_match.size > 0:
                    reordered_rows.append(row_match[:, 0])  # Extract the row panels
                else:
                    raise ValueError(f"Row value '{row_val}' does not match any existing row.")
            self.panels = np.array(reordered_rows, dtype=object)
        else:
            raise TypeError("Order must be a list of integers or strings.")

    def colOrder(self, order: Union[List[int], List[str]]) -> None:
        """
        Reorder the columns of the panel array based on the specified order.

        :param order: A list of integers specifying the new column order, or a list of strings
                    specifying column values to match using getSlc.
        """
        if all(isinstance(o, int) for o in order):
            # Reorder columns by indices
            self.panels = self.panels[:, order]
        elif all(isinstance(o, str) for o in order):
            # Reorder columns by matching column values
            reordered_cols = []
            for col_val in order:
                col_match = self._getSlc(col_val)
                if col_match.size > 0:
                    reordered_cols.append(col_match[0, :])  # Extract the column panels
                else:
                    raise ValueError(f"Column value '{col_val}' does not match any existing column.")
            self.panels = np.array(reordered_cols, dtype=object).T
        else:
            raise TypeError("Order must be a list of integers or strings.")


    def rmPanels(self, slc: Optional[Union[slice, str, List[str]]]) -> None:
        """
        Remove the specified panels. Resize the array if an entire row or column is removed.

        :param slc: The panels to remove, interpreted by _getSlc.
        """
        panels_to_remove = self._getSlc(slc)

        for panel in np.nditer(panels_to_remove, flags=["refs_ok"]):
            panel_idx = np.where(self.panels == panel.item())
            self.panels[panel_idx] = Panel()  # Replace with empty Panel

        # Remove rows or columns with all empty Panels
        self.panels = np.array(
            [row for row in self.panels if not all(isinstance(panel, Panel) and len(panel) == 0 for panel in row)],
            dtype=object
        ).T  # Repeat for columns after transposing
        self.panels = np.array(
            [col for col in self.panels if not all(isinstance(panel, Panel) and len(panel) == 0 for panel in col)],
            dtype=object
        ).T

    @staticmethod
    def vstackGrids(dgs: List["DataGrid"]) -> "DataGrid":
        """
        Stack multiple DataGrid objects vertically. Fill smaller grids with empty panels.

        :param dgs: A list of DataGrid objects to stack.
        :return: A new DataGrid object with vertically stacked panels.
        """
        max_cols = max(len(dg.panels[0]) for dg in dgs)
        padded_panels = [
            np.pad(
                dg.panels, 
                ((0, 0), (0, max_cols - len(dg.panels[0]))), 
                constant_values=Panel()
            ) for dg in dgs
        ]
        return DataGrid(np.vstack(padded_panels))

    @staticmethod
    def hstackGrids(dgs: List["DataGrid"]) -> "DataGrid":
        """
        Stack multiple DataGrid objects horizontally. Fill smaller grids with empty panels.

        :param dgs: A list of DataGrid objects to stack.
        :return: A new DataGrid object with horizontally stacked panels.
        """
        max_rows = max(len(dg.panels) for dg in dgs)
        padded_panels = [
            np.pad(
                dg.panels,
                ((0, max_rows - len(dg.panels)), (0, 0)),
                constant_values=Panel()
            ) for dg in dgs
        ]
        return DataGrid(np.hstack(padded_panels))

    def __str__(self) -> str:
        """
        Print the dimensions of the panels array and their contents, including indices.

        :return: A string representation of the DataGrid object.
        """
        rows, cols = self.panels.shape
        result = [f"DataGrid with dimensions: {rows} x {cols}\n"]

        for i, row in enumerate(self.panels):
            for j, panel in enumerate(row):
                result.append(f"Panel at ({i}, {j}): {panel}")
        
        return "\n".join(result)
