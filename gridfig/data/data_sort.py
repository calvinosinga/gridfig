from typing import List, Dict, Union, Optional
import numpy as np
from gridfig.data.data_grid import DataGrid
from gridfig.data.panel import Panel
from gridfig.data.data_container import DataContainer

class DataSort(list):
    """
    Class that contains a list of DataContainer objects and can organize them into a GridFig object.
    Inherits from list.
    """

    def getPropVals(self, key: str) -> List[str]:
        """
        Iterate through each DataContainer and save all unique values for a given property.
        Ignore empty strings.

        :param key: The property key to check in each DataContainer.
        :return: A list of unique property values.
        """
        unique_vals = set()
        for dc in self:
            value = dc.getProp(key)
            if value and value != "_na_":
                unique_vals.add(value)
        return list(unique_vals)


    def __str__(self) -> str:
        """
        Provides a detailed string representation of the DataSort object.

        :return: A string that includes the length of the list and the unique values 
                 associated with each property across all DataContainers.
        """
        result = [f"DataSort contains {len(self)} DataContainer(s)."]
        unique_properties = {}

        # Collect unique values for each property
        for dc in self:
            for key in dc.listProps():
                if key not in unique_properties:
                    unique_properties[key] = set()
                unique_properties[key].add(dc.getProp(key))

        # Add each unique property and its values to the result
        for prop, values in unique_properties.items():
            result.append(f"{prop}: {', '.join(map(str, sorted(values)))}")
        
        return "\n".join(result)
    
    def printMatching(self,
                      in_attrs: Dict[str, Union[str, List[str]]],
                      rm_attrs: Optional[Dict[str, Union[str, List[str]]]] = None):
        """
        Print all DataContainers that match the given inclusion attributes and do not match the exclusion attributes.

        :param in_attrs: Dictionary of attributes to check for inclusion.
        :param rm_attrs: Dictionary of attributes to check for exclusion.
        """
        matching_containers = [
            dc for dc in self if dc.isMatch(in_attrs, rm_attrs)
        ]
        for dc in matching_containers:
            print(dc)
    
    def createGridfig(self, 
                      panel_prop: str, 
                      row_prop: Union[str, Dict[str, List[str]]], 
                      col_prop: Union[str, Dict[str, List[str]]], 
                      in_attrs: Optional[Dict[str, Union[str, List[str]]]] = None, 
                      rm_attrs: Optional[Dict[str, Union[str, List[str]]]] = None):
        """
        Organizes DataContainers into a GridFig object.

        :param panel_prop: The property being compared in each panel.
        :param row_prop: Determines the rows in the grid (can be a string or dictionary).
        :param col_prop: Determines the columns in the grid (can be a string or dictionary).
        :param in_attrs: Optional attributes that DataContainers must match to be included.
        :param rm_attrs: Optional attributes that DataContainers must not match to be included.
        :return: A GridFig object.
        """
        # Handle row_prop
        if isinstance(row_prop, str):
            row_vals = self.getPropVals(row_prop)
            row_dict = {row_prop: row_vals}
        elif isinstance(row_prop, dict):
            if len(row_prop) != 1:
                raise ValueError("row_prop dictionary must have exactly one key.")
            row_key, row_vals = next(iter(row_prop.items()))
            if not isinstance(row_vals, list):
                row_vals = [row_vals]
            row_dict = {row_key: row_vals}
            row_prop = row_key # to pass into datagrid
        else:
            raise TypeError("row_prop must be a string or a dictionary.")

        # Handle col_prop
        if isinstance(col_prop, str):
            col_vals = self.getPropVals(col_prop)
            col_dict = {col_prop: col_vals}
        elif isinstance(col_prop, dict):
            if len(col_prop) != 1:
                raise ValueError("col_prop dictionary must have exactly one key.")
            col_key, col_vals = next(iter(col_prop.items()))
            if not isinstance(col_vals, list):
                col_vals = [col_vals]
            col_dict = {col_key: col_vals}
            col_prop = col_key # to pass into datagrid
        else:
            raise TypeError("col_prop must be a string or a dictionary.")

        # Extract row and column keys
        row_key = next(iter(row_dict.keys()))
        col_key = next(iter(col_dict.keys()))

        # Initialize a numpy array for panels
        panels = np.empty((len(row_dict[row_key]), len(col_dict[col_key])), dtype=object)

        for i, row_val in enumerate(row_dict[row_key]):
            for j, col_val in enumerate(col_dict[col_key]):
                panels[i, j] = Panel([], panel_prop, row_val, col_val)

        # Iterate through DataContainers and populate the panels
        for dc in self:
            # Check in_attrs
            if not dc.isMatch(in_attrs):
                continue

            # Check rm_attrs
            if rm_attrs and dc.isMatch(rm_attrs):
                continue

            # Determine row and column indices
            row_val = dc.get(row_key)
            col_val = dc.get(col_key)

            if row_val in row_dict[row_key] and col_val in col_dict[col_key]:
                i = row_dict[row_key].index(row_val)
                j = col_dict[col_key].index(col_val)
                panels[i, j].append(dc.copy())

        # Create and return the GridFig object
        return DataGrid(panels, row_prop, col_prop)
