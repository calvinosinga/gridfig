
class Gridfig:
    """
    overarching class that handles the interfacing between the backend, style manager,
    and data grid. Gridfig cannot change anything in these 
    """
    def __init__(self, dg, sm, be):
        self.dg = dg
        self.sm = sm
        self.be = be

        return