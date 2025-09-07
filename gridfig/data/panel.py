from typing import Optional

class Panel(list):
    """
    Represents a panel of the plot. Inherits from the list class to store a list of
    DataContainer objects.

    Attributes:
    - panel_prop: The property being compared in this panel (e.g., color, type).
    - row_val: The value of the property that determines the row the panel belongs to.
    - col_val: The value of the property that determines the column the panel belongs to.
    """

    def __init__(
        self, 
        panel_prop: Optional[str] = None, 
        row_val: Optional[str] = None, 
        col_val: Optional[str] = None
    ):
        """
        Initialize the Panel with optional properties for panel, row, and column.

        :param panel_prop: The property being compared in this panel.
        :param row_val: The value of the property that determines the row the panel belongs to.
        :param col_val: The value of the property that determines the column the panel belongs to.
        :param axis_types: A list defining default styles or behaviors for the axes in this panel.
        """
        super().__init__()  # Initialize the list base class
        self.panel_prop: str = panel_prop if panel_prop is not None else "_na_"
        self.row_val: str = row_val if row_val is not None else "_na_"
        self.col_val: str = col_val if col_val is not None else "_na_"


    def __str__(self) -> str:
        """
        Returns a readable string representation of the panel and its properties.

        :return: String describing the panel's properties and the number of DataContainers it holds.
        """
        first_line = (f"Panel with row_val={self.row_val}, col_val={self.col_val}, "
            f"containing {len(self)} Dataset(s).\n")
        each_item = '\tIncludes: '
        for i in range(len(self)):
            panel_val = self[i][self.panel_prop].unique()[0]
            each_item += f"{panel_val}, "
        each_item = each_item[:-2]
        return first_line + each_item
    
class PanelFunc:
    """
    Adjusts the data of the DataContainers of a Panel according to some specified behavior.
    Sometimes it's easier to adjust the data after it's been sorted into panels, rather than
    creating new data containers and trying to sort from there.
    Intended to be used as a superclass.
    """

    def __init__(self):
        """
        Initialize the AdjustData object with optional in_attrs and rm_attrs.
        """
        return

    def __call__(self, panel: Panel) -> None:
        """
        Perform adjustments on the DataContainers in a Panel. 
        This method is meant to be implemented by subclasses.

        :param panel: The Panel object containing DataContainers to adjust.
        """
        raise NotImplementedError("Subclasses must implement this method.")



# class Ratio(PanelFunc):
#     """
#     A subclass of PanelFunc that calculates a ratio of the data of DataContainers in a Panel.

#     Attributes:
#     - denom_in_attrs: dict, determines which DataContainers to use as the denominator.
#     - denom_rm_attrs: dict, determines which DataContainers to exclude from being used as the denominator.
#     - data_idx: int, the index in the data array to normalize (default: 1).
#     """

#     def __init__(self, 
#                  in_attrs: Optional[Dict[str, str]] = None, 
#                  rm_attrs: Optional[Dict[str, str]] = None, 
#                  denom_in_attrs: Optional[Dict[str, str]] = None, 
#                  denom_rm_attrs: Optional[Dict[str, str]] = None, 
#                  data_idx: int = 1):
#         """
#         Initialize the RatioPanel object.

#         :param in_attrs: Dictionary specifying attributes of DataContainers to include (default: empty dict).
#         :param rm_attrs: Dictionary specifying attributes of DataContainers to exclude (default: empty dict).
#         :param denom_in_attrs: Dictionary specifying attributes of DataContainers to use as the denominator.
#         :param denom_rm_attrs: Dictionary specifying attributes of DataContainers to exclude as the denominator.
#         :param data_idx: Index of the data array to normalize (default: 1).
#         """
#         super().__init__(in_attrs, rm_attrs)
#         self.denom_in_attrs: Dict[str, str] = denom_in_attrs if denom_in_attrs is not None else {}
#         self.denom_rm_attrs: Dict[str, str] = denom_rm_attrs if denom_rm_attrs is not None else {}
#         self.data_idx: int = data_idx

#     def __call__(self, panel: Panel) -> None:
#         """
#         Normalize the data of DataContainers in the given Panel.

#         :param panel: The Panel object containing DataContainers to adjust.
#         """
#         # Find denominator
#         denom_containers = self.getMatching(panel, self.denom_in_attrs, self.denom_rm_attrs)
#         if len(denom_containers) != 1:
#             raise ValueError(f"Expected 1 denominator match but found {len(denom_containers)}.")

#         denom = denom_containers[0].getData()[self.data_idx]

#         # Validate data_idx
#         if not (0 <= self.data_idx < len(denom)):
#             raise IndexError(f"data_idx {self.data_idx} is out of bounds for denominator data.")

#         # Normalize data
#         for dc in self.getMatching(panel):
#             data = dc.getData()
#             if not (0 <= self.data_idx < len(data)):
#                 raise IndexError(f"data_idx {self.data_idx} is out of bounds for data in DataContainer.")
#             data[self.data_idx] /= denom


# class Multiply(PanelFunc):
#     """
#     A subclass of PanelFunc that multiplies a specified value or numpy array to the data of each 
#     DataContainer in a Panel along a specified axis.

#     Attributes:
#     - multiplier: The value or numpy array to multiply with the data.
#     - axis: The axis of the data to apply the multiplier (default: 0).
#     """

#     def __init__(self, 
#                  multiplier: Union[float, np.ndarray], 
#                  axis: int = 0, 
#                  in_attrs: Optional[Dict[str, str]] = None, 
#                  rm_attrs: Optional[Dict[str, str]] = None):
#         """
#         Initialize the MultiplyPanel object.

#         :param multiplier: The value or numpy array to multiply with the data.
#         :param axis: The axis of the data to apply the multiplier (default: 0).
#         :param in_attrs: Dictionary specifying attributes of DataContainers to include (default: empty dict).
#         :param rm_attrs: Dictionary specifying attributes of DataContainers to exclude (default: empty dict).
#         """
#         super().__init__(in_attrs, rm_attrs)
#         self.multiplier: Union[float, np.ndarray] = multiplier
#         self.axis: int = axis

#     def __call__(self, panel: Panel) -> None:
#         """
#         Multiply the data of each matching DataContainer in the Panel by the multiplier.

#         :param panel: The Panel object containing DataContainers to adjust.
#         """
#         for dc in self.getMatching(panel):
#             data = dc.getData()
            
#             # Check if multiplier is a numpy array and validate its shape
#             if isinstance(self.multiplier, np.ndarray):
#                 if self.multiplier.shape[0] != data.shape[self.axis]:
#                     raise ValueError(f"Multiplier array length ({self.multiplier.shape[0]}) does not match "
#                                      f"data length along axis {self.axis} ({data.shape[self.axis]}).")
                
#                 # Apply along the specified axis
#                 data *= np.expand_dims(self.multiplier, axis=(1 - self.axis))  # Broadcasting to match axis
#             else:
#                 data *= self.multiplier  # Scalar multiplication
            
#             dc.setData(data)  # Update the DataContainer data


# class Add(PanelFunc):
#     """
#     A subclass of PanelFunc that adds a specified value or numpy array to the data of each 
#     DataContainer in a Panel along a specified axis.

#     Attributes:
#     - addition: The value or numpy array to add to the data.
#     - axis: The axis of the data to apply the addition (default: 0).
#     """

#     def __init__(self, 
#                  addition: Union[float, np.ndarray], 
#                  axis: int = 0, 
#                  in_attrs: Optional[Dict[str, str]] = None, 
#                  rm_attrs: Optional[Dict[str, str]] = None):
#         """
#         Initialize the AddPanel object.

#         :param addition: The value or numpy array to add to the data.
#         :param axis: The axis of the data to apply the addition (default: 0).
#         :param in_attrs: Dictionary specifying attributes of DataContainers to include (default: empty dict).
#         :param rm_attrs: Dictionary specifying attributes of DataContainers to exclude (default: empty dict).
#         """
#         super().__init__(in_attrs, rm_attrs)
#         self.addition: Union[float, np.ndarray] = addition
#         self.axis: int = axis

#     def __call__(self, panel: Panel) -> None:
#         """
#         Add the specified value to the data of each matching DataContainer in the Panel.

#         :param panel: The Panel object containing DataContainers to adjust.
#         """
#         for dc in self.getMatching(panel):
#             data = dc.getData()

#             # Check if addition is a numpy array and validate its shape
#             if isinstance(self.addition, np.ndarray):
#                 if self.addition.shape[0] != data.shape[self.axis]:
#                     raise ValueError(f"Addition array length ({self.addition.shape[0]}) does not match "
#                                      f"data length along axis {self.axis} ({data.shape[self.axis]}).")
                
#                 # Apply along the specified axis
#                 data += np.expand_dims(self.addition, axis=(1 - self.axis))  # Broadcasting to match axis
#             else:
#                 data += self.addition  # Scalar addition
            
#             dc.setData(data)  # Update the DataContainer data


# class Shade(PanelFunc):
#     """
#     A subclass of PanelFunc that calculates the minima and maxima of matching DataContainers' data 
#     within a Panel and creates a new DataContainer to represent the shaded region.

#     Attributes:
#     - plot_type: The plot type for the newly created DataContainer (default: 'fill').
#     - visible: If False, set the plot type of the matched DataContainers to '_na_' (default: False).
#     - saved_data: A list to store copies of the data of matching DataContainers.
#     """

#     def __init__(self, 
#                  in_attrs: Optional[Dict[str, str]] = None, 
#                  rm_attrs: Optional[Dict[str, str]] = None, 
#                  plot_type: str = 'fill', 
#                  visible: bool = False):
#         """
#         Initialize the Shade object.

#         :param in_attrs: Dictionary specifying attributes of DataContainers to include.
#         :param rm_attrs: Dictionary specifying attributes of DataContainers to exclude.
#         :param plot_type: The plot type for the new shaded DataContainer (default: 'fill').
#         :param visible: If False, set plot_type of matched DataContainers to '_na_' (default: False).
#         """
#         super().__init__(in_attrs, rm_attrs)
#         self.plot_type: str = plot_type
#         self.visible: bool = visible
#         self.saved_data: List[np.ndarray] = []

#     def __call__(self, panel: Panel) -> None:
#         """
#         Calculate minima and maxima of the matching DataContainers' data and create a new shaded DataContainer.

#         :param panel: The Panel object containing DataContainers to adjust.
#         """
#         matched_data = []

#         # Step 1: Iterate through DataContainers and collect their data
#         for dc in self.getMatching(panel):
#             data = dc.getData()

#             # Save a copy of the data
#             self.saved_data.append(data.copy())
#             matched_data.append(data)

#             # If visible is False, set plot_type to '_na_'
#             if not self.visible:
#                 dc.setPlotType('_na_')

#         if not matched_data:
#             print("Warning: No matching DataContainers found.")
#             return

#         # Step 2: Handle mismatched data shapes
#         # Pad shorter arrays with NaNs to match the longest one
#         max_length = max(data.shape[0] for data in matched_data)
#         padded_data = []
#         for data in matched_data:
#             if data.shape[0] < max_length:
#                 padding = np.full((max_length - data.shape[0], *data.shape[1:]), np.nan)
#                 padded_data.append(np.vstack((data, padding)))
#                 print(f"Warning: Data shape mismatch. Padding with NaNs for data of shape {data.shape}.")
#             else:
#                 padded_data.append(data)

#         padded_data = np.array(padded_data)

#         # Step 3: Compute minima and maxima along the first axis
#         x = np.arange(max_length)  # Assuming x is a range for simplicity
#         min_vals = np.nanmin(padded_data, axis=0)
#         max_vals = np.nanmax(padded_data, axis=0)

#         # Combine into the [x, min, max] format
#         shaded_data = np.vstack((x, min_vals, max_vals)).T

#         # Step 4: Create a new DataContainer for the shaded region
#         new_dc = DataContainer(data=shaded_data, properties={'plot_type': self.plot_type})

#         # Step 5: Append the new DataContainer to the panel
#         panel.append(new_dc)
