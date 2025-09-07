import numpy as np
from gridfig.data.panel import Panel
from gridfig.data.panel import PanelFunc
from typing import Hashable, Union, List, Iterable, Optional, Any

class DataGrid:
    """
    Represents a 2D array of Panel objects. Provides methods for managing and manipulating 
    the organization of panels.
    """

    def __init__(self, 
                 panels: Union[List[List[Panel]], np.ndarray],
                 row_prop: str,
                 col_prop: str):
        """
        Initialize the DataGrid with a 2D array of Panel objects.

        :param panels: A 2D array (list of lists) of Panel objects. Can also be a numpy array.
        """
        if isinstance(panels, np.ndarray):
            ndim = len(panels.shape)
            if not ndim == 2:
                raise ValueError(f"Panels is not 2D, has {ndim} dimensions")

        if isinstance(panels, list):
            if not all(isinstance(row, list) for row in panels):
                raise ValueError("Panels must be a 2D array (list of lists or numpy array).")
        
        if not all(isinstance(panel, Panel) for row in panels for panel in row):
            raise ValueError("All elements in panels must be instances of the Panel class.")
        
        # Transform panels into a 2D numpy array if not already
        self.panels: np.ndarray = np.array(panels, dtype=object)
        self.row_prop = row_prop
        self.col_prop = col_prop
        return

    def getShape(self):
        return self.panels.shape
    

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
        return

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

    @staticmethod
    def dataFrameToGrid(fdf, panel_prop, row_prop = None, col_prop = None, plot_columns = None) -> "DataGrid":
        # fdf is a filtered data frame
        
        # format row and column properties
        has_row = not (row_prop is None or row_prop == "")
        has_col = not (col_prop is None or col_prop == "")
        print(has_row, has_col)
        if not has_row:
            row_vals = [None]
            nrows = 1
        elif isinstance(row_prop, str):
            row_vals = np.array(fdf[row_prop].unique())
            nrows = len(row_vals)
            if not row_prop in fdf.columns:
                raise ValueError(f"row_prop {row_prop} is not in data frame")
        else:
            raise TypeError("row_prop must be a string.")
        if not has_col:
            col_vals = [None]
            ncols = 1
        elif isinstance(col_prop, str):
            col_vals = np.array(fdf[col_prop].unique())
            ncols = len(col_vals)
        else:
            raise TypeError("col_prop must be a string.")
        
        print(f"creating {nrows} x {ncols} data grid - Panel: {panel_prop}, Row: {row_prop}, Col: {col_prop}.")
        # format plot_columns correctly, plot_columns must include panel, row, column properties
        if plot_columns is None:
            plot_columns = []
        if not isinstance(plot_columns, list):
            raise TypeError("plot_columns must be a list")

        if panel_prop not in plot_columns:
            plot_columns.append(panel_prop)
        if row_prop not in plot_columns and has_row:
            plot_columns.append(row_prop)
        if col_prop not in plot_columns and has_col:
            plot_columns.append(col_prop)

        panels = np.empty((nrows, ncols), dtype = object)

        for i in range(nrows):
            for j in range(ncols):
                # for each panel, select the row/column combination
                panels[i, j] = Panel(panel_prop, row_vals[i], col_vals[j])


                if has_row and has_col:
                    panel_df = fdf[(fdf[row_prop] == row_vals[i]) & (fdf[col_prop] == col_vals[j])]
                elif has_row:
                    panel_df = fdf[fdf[row_prop] == row_vals[i]]
                elif has_col:
                    panel_df = fdf[fdf[col_prop] == col_vals[j]]
                else:
                    panel_df = fdf.copy()
                # get panel identifier for each object/data
                obj_list = panel_df[panel_prop].unique()

                for obj in obj_list:

                    obj_df = panel_df[panel_df[panel_prop] == obj]
                    panels[i, j].append(obj_df[plot_columns])
        
        
        return DataGrid(panels, row_prop, col_prop)

    def __str__(self) -> str:
        """
        Print the dimensions of the panels array and their contents, including indices.

        :return: A string representation of the DataGrid object.
        """
        rows, cols = self.panels.shape
        result = [f"DataGrid with dimensions: {rows} x {cols}"]
        result.append(f"Panel Property: {self.panels[0,0].panel_prop}, " + \
                      f"Row Property: {self.row_prop}, Column Property: {self.col_prop}\n")
        for i, row in enumerate(self.panels):
            for j, panel in enumerate(row):
                result.append(f"Panel at ({i}, {j}): {panel}")
        
        return "\n".join(result)
    


