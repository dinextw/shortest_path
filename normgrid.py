#!/usr/bin/python

""" The stuffs related to shortest path.
"""
from decimal import Decimal, ROUND_HALF_UP, getcontext

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
        self._grid_gap = [0.01, 0.01, 1]
        self._div = 4
    def _myround_lon(self, lon, div):
        unit = int(div / self._grid_gap[0])
        return float((lon*unit).quantize(Decimal('1'), rounding=ROUND_HALF_UP)/unit)
    def _myround_lat(self, lat, div):
        unit = int(div / self._grid_gap[1])
        return float((lat*unit).quantize(Decimal('1'), rounding=ROUND_HALF_UP)/unit)
    def _myround_dep(self, dep, div):
        unit = int(div / self._grid_gap[2])
        return float((dep*unit).quantize(Decimal('1'), rounding=ROUND_HALF_UP)/unit)
    def get_grid_gap(self, stage):
        """ Get the current value of grid gap
        Args:
            stage: stage number
        Returns:
            grid gap by stage
        Raises:
            Native exceptions.
        """
        return [x / self.get_div(stage) for x in self._grid_gap]
    def get_div(self, stage):
        """ Get the current value of grid gap
        Args:
            None
        Returns:
            div
        Raises:
            Native exceptions.
        """
        if stage == 1:
            return 1
        elif stage == 2:
            return self._div
        print("Error in stage selection in getting div")
        return None
    def get_num_lon_index(self, stage):
        """ Get the number of longitude indexes
        Args:
            stage: number of stage
        Returns:
            number: number of longitude indexes
        Raises:
            Native exceptions.
        """
        return int(360 * self.get_div(stage) / self._grid_gap[0]) + 1
    def get_num_lat_index(self, stage):
        """ Get the number of latitude indexes
        Args:
            stage: number of stage
        Returns:
            number: number of latitude indexes
        Raises:
            Native exceptions.
        """
        return int(180 * self.get_div(stage) / self._grid_gap[1]) + 1
    def get_norm_loc(self, loc, stage):
        """ Normalize loctaion to grid point
        Args:
            loc: location of the unnormalized point
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
        loc_norm.append(self._myround_lon(Decimal(repr(loc[0])), self.get_div(stage)))
        loc_norm.append(self._myround_lat(Decimal(repr(loc[1])), self.get_div(stage)))
        loc_norm.append(self._myround_dep(Decimal(repr(loc[2])), self.get_div(stage)))
        return loc_norm
    def get_norm_index(self, loc, stage):
        """ Get index of normalized grid point
        Args:
            loc: location of the unnormalized point
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

        loc_norm = self.get_norm_loc(loc, stage)
        num_lon = self.get_num_lon_index(stage)
        num_lat = self.get_num_lat_index(stage)
        return int((loc_norm[2] + 10) * self.get_div(stage) / self._grid_gap[2] * num_lon * num_lat
                   + (loc_norm[1] + 90) * self.get_div(stage) / self._grid_gap[1] * num_lon
                   + (loc_norm[0] + 180) * self.get_div(stage) / self._grid_gap[0])
    def recover_norm_loc(self, idx_loc, stage):
        """ Get the normalized location from the index
        Args:
            idx_loc : index of location
        Returns:
            loc: normalized location
        Raises:
            Native exceptions.
        """
        loc = []
        getcontext().prec = 12
        num_lon = self.get_num_lon_index(stage)
        num_lat = self.get_num_lat_index(stage)
        lon = float(Decimal((idx_loc % (num_lon * num_lat)) % num_lon * self._grid_gap[0]
                            / self.get_div(stage))
                    - Decimal(180))
        loc.append(lon)
        lat = float(Decimal((idx_loc - int((lon + 180) * self.get_div(stage) / self._grid_gap[0]))
                            % (num_lon * num_lat)
                            * self._grid_gap[1]) / Decimal(self.get_div(stage) * num_lon)
                    - Decimal(90))
        loc.append(lat)
        dep = float(Decimal((idx_loc - int((lon + 180) * self.get_div(stage) / self._grid_gap[0])
                             - int((lat + 90) * self.get_div(stage) / self._grid_gap[1] * num_lon))
                            * self._grid_gap[2] / (self.get_div(stage) * num_lon * num_lat))
                    - Decimal(10))
        loc.append(dep)
        return loc

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
        start += Decimal(jump)

def main():
    """ unit test
    """
    test = NormGrid()

    stage = 2
    loc = [-180, -90, -10]
    print("The grid gap now is ", test.get_grid_gap(stage))
    print("Test for smallest normalized location is ", loc)
    loc_norm = test.get_norm_loc(loc, stage)
    print("The normalized location is ", loc_norm)
    print("The recovered location is ", test.recover_norm_loc(test.get_norm_index(loc, stage)
                                                              , stage))
    #請多測邊界數值（最大最小值 還有在邊緣的或者超出邊界的 以及剛好在四捨五入交界的）
    loc = [180, 90, 10]
    print("Test for biggest normalized location is ", loc)
    loc_norm = test.get_norm_loc(loc, stage)
    print("The normalized location is ", loc_norm)
    div = 1
    grid_gap = [0.01, 0.01, 1]
    num_lon = 360 * div / grid_gap[0]
    num_lat = 180 * div / grid_gap[1]
    num_dep = 20 * div / grid_gap[2]
    print("The estimate largest normalized index is ", (num_lon+1) * (num_lat+1) * (num_dep+1) - 1)
    print("The number of longitude indexes is ", test.get_num_lon_index(stage))
    print("The number of latitude indexes is ", test.get_num_lat_index(stage))
    print("The normalized index is ", test.get_norm_index(loc, stage))
    print("The recovered location is ", test.recover_norm_loc(test.get_norm_index(loc, stage)
                                                              , stage))
    index = test.get_norm_index(loc, stage)
    #loc = [123.00125, -10.175, 10.3]
    loc = [121.02, 23.02, 0]
    print("Test for normalized location is ", loc)
    loc_norm = test.get_norm_loc(loc, stage)
    print("The normalized location is ", loc_norm)
    print("The normalized index is ", test.get_norm_index(loc, stage))
    print("The recovered location is ", test.recover_norm_loc(test.get_norm_index(loc, stage)
                                                              , stage))
    print("=================")
    #請測試index換為loc是否能換回來，以及是否only one（把所有index印出來檢查？！）
    loc = [120, 21, 0]
    print("The testing starting location is ", loc)
    index_start = test.get_norm_index(loc, stage)
    print("The normalized starting index is ", index_start)
    print("The recovered location is ", test.recover_norm_loc(index_start, stage))
    loc = [122, 26, 0]
    index_end = test.get_norm_index(loc, stage)
    print("The testing ending location is ", loc)
    print("The normalized ending index is ", index_end)
    print("The recovered location is ", test.recover_norm_loc(index_end, stage))
    index = []
    if stage == 1:
        jump = '0.01'
    elif stage == 2:
        jump = '0.0025'
    else:
        print("Error in stage selection from testing program")
    for lon in list(drange(120, 122, jump)):
        for lat in list(drange(21, 26, jump)):
            loc = [lon, lat, 0]
            index.append(test.get_norm_index(loc, stage))
    print("Finish indexing")
    index_set = set(index)
    print("number of  nonduplicate index:", len(index_set)
          , ", and number of actual index:", len(index))

if __name__ == '__main__':
    main()
