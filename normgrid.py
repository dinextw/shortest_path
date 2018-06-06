#!/usr/bin/python

""" The stuffs related to shortest path.
"""
import math
import decimal

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
    def __init__(self):
        self._grid_gap = [0.0025, 0.0025, 0.25]
    def _myround_lon(self, lon):
        unit = 1 / self._grid_gap[0]
        return math.ceil(lon*unit)/unit
    def _myround_lat(self, lat):
        unit = 1 / self._grid_gap[1]
        return math.ceil(lat*unit)/unit
    def _myround_dep(self, dep):
        unit = 1 / self._grid_gap[2]
        return math.ceil(dep*unit)/unit
    def get_norm_loc(self, loc):
        """ Normalize loctaion to grid point
        Args:
            lon, lat , dep: location of the unnormalized point
        Returns:
            loc: normalized location
        Raises:
            Native exceptions.
        """
        if loc[0] > 180 or loc[0] < -180:
            print("Out of range")
            return None
        if loc[1] > 90 or loc[1] < -90:
            print("Out of range")
            return None
        if loc[2] < -10:
            print("Out of range")
            return None

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
        if loc[0] > 180 or loc[0] < -180:
            print("Out of range")
            return None
        if loc[1] > 90 or loc[1] < -90:
            print("Out of range")
            return None
        if loc[2] < -10:
            print("Out of range")
            return None

        loc_norm = self.get_norm_loc(loc)
        num_lon = 360 / self._grid_gap[0]
        num_lat = 180 / self._grid_gap[1]
        return int((loc_norm[2] + 10) / self._grid_gap[2] * num_lon * num_lat
                   + (loc_norm[1] + 90) / self._grid_gap[1] * num_lon
                   + (loc_norm[0] + 180) / self._grid_gap[0])

def drange(start, end, jump):
    """ Get the float range for testing
    Args:
        start: starting float
        end: ending float
        jump: unit
    Returns:
        (dictionary of float?)
    Raises:
        Native exceptions.
    """
    while start < end:
        yield float(start)
        start += decimal.Decimal(jump)

def main():
    """ unit test
    """
    test = NormGrid()

    loc = [-180, -90, -10]
    print("Test for biggest normalized location is ", loc)
    loc_norm = test.get_norm_loc(loc)
    print("The normalized location is ", loc_norm)
    #請多測邊界數值（最大最小值 還有在邊緣的或者超出邊界的 以及剛好在四捨五入交界的）
    loc = [180, 90, 10]
    print("Test for biggest normalized location is ", loc)
    loc_norm = test.get_norm_loc(loc)
    print("The normalized location is ", loc_norm)
    index = test.get_norm_index(loc)
    loc = [123.00125, -10.175, 10.3]
    print("Test for biggest normalized location is ", loc)
    loc_norm = test.get_norm_loc(loc)
    print("The normalized location is ", loc_norm)
    #請測試index換為loc是否能換回來，以及是否only one（把所有index印出來檢查？！）
    loc = [120, 21, 0]
    index_start = test.get_norm_index(loc)
    print("The normalized starting index is ", index_start)
    loc = [122, 26, 0]
    index_end = test.get_norm_index(loc)
    print("The normalized ending index is ", index_end)
    index = []
    for lon in list(drange(120, 122, '0.0025')):
        for lat in list(drange(21, 26, '0.0025')):
            loc = [lon, lat, 0]
            index.append(test.get_norm_index(loc))
    print("Finish indexing")
    index_set = set(index)
    print("number of  nonduplicate index:", len(index_set)
          , ", and number of actual index:", len(index))


if __name__ == '__main__':
    main()
