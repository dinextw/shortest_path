#!/usr/bin/python

""" The stuffs related to shortest path.
"""

class NormGridSingleton(type):
    """ Singleton class of NormGrid
    """
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(NormGridSingleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class NormGrid(metaclass=NormGridSingleton):
    """ Normalized to the fixed grid point
    Public Methods:
        normalized: normalize the point to nearest grid node
    """
    _grid_gap = None
    def __init__(self, grid_gap=None):
        if grid_gap is None:
            self._grid_gap = [0.0025, 0.0025, 0.25]
        else:
            self._grid_gap = grid_gap
    def _myround_lon(self, num):
        return float(self._grid_gap[0] * round(float(num) / self._grid_gap[0]))
    def _myround_lat(self, num):
        return float(self._grid_gap[1] * round(float(num) / self._grid_gap[1]))
    def _myround_dep(self, num):
        return float(self._grid_gap[2] * round(float(num)/self._grid_gap[2]))
    def get_norm_loc(self, loc):
        """ Normalize loctaion to grid point
        Args:
            lon, lat , dep: location of the unnormalized point
        Returns:
            loc: normalized location
        Raises:
            Native exceptions.
        """
        loc_norm = []
        loc_norm.append(self._myround_lon(loc[0]))
        loc_norm.append(self._myround_lat(loc[1]))
        loc_norm.append(self._myround_dep(loc[2]))
        return loc_norm
    def get_norm_index(self, loc):
        """ Get index of normalized grid point
        Args:
            lon, lat , dep: location of the unnormalized point
        Returns:
            index: normalized index
        Raises:
            Native exceptions.
        """
        loc_norm = self.get_norm_loc(loc)
        num_lon = 360 / self._grid_gap[0]
        num_lat = 180 / self._grid_gap[1]
        return int((loc_norm[2] + 10) * num_lon * num_lat + (loc_norm[1] + 90) * num_lon
                   + (loc_norm[0] + 180) / self._grid_gap[0])

def main():
    """ unit test
    """
    test = NormGrid()

    loc = [-180, -90, -10]
    print("Test for normalized location is ", loc)
    loc_norm = test.get_norm_loc(loc)
    print("The normalized location is ", loc_norm)
    index = test.get_norm_index(loc)
    print("The normalized index is ", index)

if __name__ == '__main__':
    main()
