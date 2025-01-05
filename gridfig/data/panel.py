from typing import Iterable, Hashable, List, Optional

class Panel(list):
    """
    Represents a panel of the plot. Inherits from the list class to store a list of
    DataContainer objects.

    Attributes:
    - panel_prop: The property being compared in this panel (e.g., color, type).
    - row_val: The value of the property that determines the row the panel belongs to.
    - col_val: The value of the property that determines the column the panel belongs to.
    - axis_types: A list defining default styles or behaviors for the axes in this panel.
    """

    def __init__(
        self, 
        panel_prop: Optional[str] = None, 
        row_val: Optional[str] = None, 
        col_val: Optional[str] = None, 
        axis_types: Optional[List[Hashable]] = None
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
        self.axis_types: List[Hashable] = axis_types if axis_types is not None else []

    def addType(self, atype: Hashable) -> None:
        """
        Add a type to the axis_types list.

        :param atype: A hashable object or iterable of hashable objects defining a type.
        """
        if isinstance(atype, Iterable) and not isinstance(atype, (str, bytes)):
            for f in atype:
                self.addType(f)
        elif isinstance(atype, Hashable):
            self.axis_types.append(atype)
        else:
            print("WARNING: Given axis type is not hashable.")

    def hasType(self, atype: Hashable) -> bool:
        """
        Check if the axis_types list contains the specified type.

        :param atype: The type to check for.
        :return: True if the type is present, False otherwise.
        """
        return atype in self.axis_types

    def rmType(self, atype: Hashable) -> None:
        """
        Remove a type from the axis_types list.

        :param atype: The type to remove.
        """
        try:
            self.axis_types.remove(atype)
        except ValueError:
            print(f"WARNING: Type '{atype}' not found in axis_types.")

    # Getters and setters for panel_prop
    def getPanelProp(self) -> str:
        """Retrieve the panel property."""
        return self.panel_prop

    def setPanelProp(self, panel_prop: str) -> None:
        """Set the panel property."""
        self.panel_prop = panel_prop

    # Getters and setters for row_val
    def getRowVal(self) -> str:
        """Retrieve the row value."""
        return self.row_val

    def setRowVal(self, row_val: str) -> None:
        """Set the row value."""
        self.row_val = row_val

    # Getters and setters for col_val
    def getColVal(self) -> str:
        """Retrieve the column value."""
        return self.col_val

    def setColVal(self, col_val: str) -> None:
        """Set the column value."""
        self.col_val = col_val

    def __str__(self) -> str:
        """
        Returns a readable string representation of the panel and its properties.

        :return: String describing the panel's properties and the number of DataContainers it holds.
        """
        return (
            f"Panel with panel_prop={self.panel_prop}, row_val={self.row_val}, col_val={self.col_val}, "
            f"containing {len(self)} DataContainer(s)."
        )
