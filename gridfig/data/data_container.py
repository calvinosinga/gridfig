import pandas as pd
from typing import List, Dict, Union, Optional, Any

class DataContainer:
    """
    Stores data intended for plotting, associated properties, and plot types.
    """

    def __init__(
        self,
        data: pd.DataFrame,
        properties: Optional[Dict[str, Union[str, float, List]]] = None,
        plot_types: Optional[List[str]] = None,
    ):
        """
        Initialize the DataContainer.

        :param data: A pandas DataFrame containing the data for plotting.
        :param properties: A dictionary of properties describing the data or its origin.
        :param plot_types: A list of plot types that determine plotting behavior.
        """
        self.data = data  # DataFrame to store plotting data
        self.properties = pd.Series(properties if properties is not None else {})
        self.plot_types = plot_types if plot_types is not None else []

    def __str__(self) -> str:
        """
        Returns a readable string representation of the container's properties and data.
        """
        return (
            f"DataContainer Properties:\n{self.properties}\n\n"
            f"Data (head):\n{self.data.head()}\n\n"
            f"Plot Types: {self.plot_types}"
        )

    def isMatch(self, in_attrs: Dict, rm_attrs: Optional[Dict] = None) -> bool:
        """
        Determines if the container matches the inclusion and exclusion attributes.

        :param in_attrs: Dictionary of attributes to check for inclusion.
        :param rm_attrs: Dictionary of attributes to check for exclusion.
        :return: True if the container matches in_attrs and does not match rm_attrs.
        """
        # Check rm_attrs first
        if rm_attrs:
            for key, value in rm_attrs.items():
                if key in self.properties.index:
                    if isinstance(value, list):
                        if self.properties[key] in value:
                            return False
                    elif self.properties[key] == value:
                        return False

        # Check in_attrs
        for key, value in in_attrs.items():
            if key in self.properties.index:
                if isinstance(value, list):
                    if self.properties[key] not in value:
                        return False
                elif self.properties[key] != value:
                    return False

        return True

    def copy(self):
        """
        Creates a deep copy of the DataContainer.

        :return: A new DataContainer with copied data, properties, and plot types.
        """
        return DataContainer(
            data=self.data.copy(),
            properties=self.properties.to_dict(),
            plot_types=self.plot_types.copy(),
        )

    def addPlotType(self, plot_type: str):
        """
        Add a new plot type to the container.

        :param plot_type: The plot type to add.
        """
        if plot_type not in self.plot_types:
            self.plot_types.append(plot_type)
    
    def rmPlotType(self, plot_type: str):
        """
        Remove an existing plot type from the container.

        :param plot_type: The plot type to remove.
        :raises ValueError: If the plot type does not exist in the list.
        """
        self.plot_types.remove(plot_type)

    def hasPlotType(self, plot_type: str):
        """
        Check if the container supports a specific plot type.

        :param plot_type: The plot type to check.
        :return: True if the plot type is in the list, False otherwise.
        """
        return plot_type in self.plot_types
    
    def getData(self) -> pd.DataFrame:
        """
        Retrieves the data.

        :return: The pandas DataFrame containing the data for plotting.
        """
        return self.data
    
    # Property management functions
    def getProp(self, key: str) -> Any:
        """
        Retrieve the value of a property.

        :param key: The property key to retrieve.
        :return: The value of the property, or '_na_' if the key is not found.
        """
        return self.properties.get(key, '_na_')

    def setProp(self, key: str, value: Union[str, float, List[Any]]):
        """
        Set or update a property.

        :param key: The property key to set.
        :param value: The value to assign to the property.
        """
        self.properties[key] = value

    def rmProp(self, key: str):
        """
        Remove a property from the DataContainer.

        :param key: The property key to remove.
        :raises KeyError: If the property key does not exist.
        """
        if key in self.properties:
            del self.properties[key]
        else:
            raise KeyError(f"Prop '{key}' does not exist.")

    def hasProp(self, key: str) -> bool:
        """
        Check if a property exists in the DataContainer.

        :param key: The property key to check.
        :return: True if the property exists, False otherwise.
        """
        return key in self.properties

    def listProps(self) -> Dict[str, Any]:
        """
        List all properties of the DataContainer.

        :return: A dictionary of all properties and their values.
        """
        return self.properties.to_dict()

    # Example utility method for batch updates
    def updateProps(self, updates: Dict[str, Any]):
        """
        Update multiple properties at once.

        :param updates: A dictionary of property updates.
        """
        for key, value in updates.items():
            self.setProperty(key, value)
