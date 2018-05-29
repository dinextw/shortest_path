#!/usr/bin/python

""" The stuffs related to building geo model.
"""
import bisect
import normgrid
import my_util

class GeoSpeed(object):
    """ Look up the speed in velocity modeel
    Public Methods:
        renew_lon: rewrite the lon value
        renew_lat: rewrite the lat value
        renew_dep: rewrite the dep value
        renew_speed: rewrite the speed value
        display_lon: display the lon value
        display_lat: display the lat value
        display_dep: display the dep value
        display_speed: display the speed value
    """
    _lon = None
    _lat = None
    _dep = None
    _speed = None
    def __init__(self, lon=0, lat=0, dep=0, speed=0):
        self._lon = lon
        self._lat = lat
        self._dep = dep
        self._speed = speed
    def renew_lon(self, lon):
        """ Renew the value of lon
        Args:
            lon: longitude
        Returns:
        Raises:
            Native exceptions.
        """
        if lon > 180 or lon < 0:
            print("Out of range")
        else:
            self._lon = lon
    def renew_lat(self, lat):
        """ Renew the value of lat
        Args:
            lat: latitude
        Returns:
        Raises:
            Native exceptions.
        """
        if lat > 90 or lat < -90:
            print("Out of range")
        else:
            self._lat = lat
    def renew_dep(self, dep):
        """ Renew the value of dep
        Args:
            dep: depth
        Returns:
        Raises:
            Native exceptions.
        """
        if dep < -10:
            print("Out of range")
        else:
            self._dep = dep
    def renew_speed(self, speed):
        """ Renew the value of speed
        Args:
            speed: velocity
        Returns:
        Raises:
            Native exceptions.
        """
        if speed < 0:
            print("Out of range")
        else:
            self._speed = speed
    def display_lon(self):
        """ Return the value of lon
        Args:
        Returns:
            _lon: longitude
        Raises:
            Native exceptions.
        """
        return self._lon
    def display_lat(self):
        """ Return the value of lat
        Args:
        Returns:
            _lat: latitude
        Raises:
            Native exceptions.
        """
        return self._lat
    def display_dep(self):
        """ Return the value of dep
        Args:
        Returns:
            _dep: depth
        Raises:
            Native exceptions.
        """
        return self._dep
    def display_speed(self):
        """ Return the value of speed
        Args:
        Returns:
            _speed: velocity
        Raises:
            Native exceptions.
        """
        return self._speed


class GeoModel(object):
    """ Look up the speed in velocity modeel
    Public Methods:
        get_speed: get the speed of the location
    """
    _scales = []
    _geo_speeds = []
    _norm = None
    _filepath = None
    def __init__(self, filepath=None):
        if filepath is None:
            self._filepath = "./_input/MOD_H13"
        else:
            self._filepath = filepath
        self._norm = normgrid.NormGrid()
        self._read_model()

    def _read_scales(self, nums_line, lons_line, lats_line, deps_line):
        nums = [float(elem) for elem in nums_line.split()]
        lons = [float(elem) for elem in lons_line.split()]
        lats = [float(elem) for elem in lats_line.split()]
        deps = [float(elem) for elem in deps_line.split()]

        if nums[2] != len(lons):
            print("Dimension error in reading longitude index")
        else:
            self._scales.append(lons)
        if nums[3] != len(lats):
            print("Dimension error in reading latitude index")
        else:
            self._scales.append(lats)
        if nums[4] != len(deps):
            print("Dimension error in reading depth index")
        else:
            self._scales.append(deps)

    def _read_model(self):
        with open(self._filepath, 'r') as file_model:
            self._read_scales(file_model.readline()
                              , file_model.readline()
                              , file_model.readline()
                              , file_model.readline())

            for dep_idx in range(len(self._scales[2])):
                for lat_idx in range(len(self._scales[1])):
                    velocities_line = file_model.readline()
                    velocities = [float(elem) for elem in velocities_line.split()]

                    if len(velocities) != len(self._scales[0]):
                        print("Dimension error in reading velocity(longitude)")
                        break
                    else:
                        for lon_idx in range(len(self._scales[0])):
                            if len(self._geo_speeds) < (lon_idx + 1):
                                self._geo_speeds.append([])
                            if len(self._geo_speeds[lon_idx]) < (lat_idx + 1):
                                self._geo_speeds[lon_idx].append([])
                            if len(self._geo_speeds[lon_idx][lat_idx]) < (dep_idx + 1):
                                geo_speed = GeoSpeed(self._scales[0][lon_idx]
                                                     , self._scales[1][lat_idx]
                                                     , self._scales[2][dep_idx]
                                                     , velocities[lon_idx])
                                self._geo_speeds[lon_idx][lat_idx].append(geo_speed)

    def _nearest_idx(self, loc):
        lon_idx = bisect.bisect_right(self._scales[0], loc[0]) - 1
        lat_idx = bisect.bisect_right(self._scales[1], loc[1]) - 1
        dep_idx = bisect.bisect_right(self._scales[2], loc[2]) - 1
        return [lon_idx, lat_idx, dep_idx]

    def get_speed(self, loc):
        """ Return the speed of the location
        Args:
            loc: location
        Returns:
            velocity: speed of the normalized location
        Raises:
            Native exceptions.
        """
        loc_norm = self._norm.get_norm_loc(loc)
        near_idx = self._nearest_idx(loc_norm)
        dist_lon = my_util.haversine(self._scales[0][near_idx[0]]
                                     , self._scales[1][near_idx[1]]
                                     , self._scales[0][near_idx[0]+1]
                                     , self._scales[1][near_idx[1]]
                                     , 6371.0 - self._scales[2][near_idx[2]])
        dist_lat = my_util.haversine(self._scales[0][near_idx[0]]
                                     , self._scales[1][near_idx[1]]
                                     , self._scales[0][near_idx[0]]
                                     , self._scales[1][near_idx[1]+1]
                                     , 6371.0 - self._scales[2][near_idx[2]])
        dist_dep = self._scales[2][near_idx[2]+1] - self._scales[2][near_idx[2]]

        velocity = 0
        incs = [[0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1], [1, 1, 0],
                [1, 0, 1], [0, 1, 1], [1, 1, 1]]
        for inc in incs:
            if inc[0] == 1:
                diff_lon = my_util.haversine(loc_norm[0]
                                             , loc_norm[1]
                                             , self._scales[0][near_idx[0]]
                                             , loc_norm[1]
                                             , 6371.0 - self._scales[2][near_idx[2]])
            else:
                diff_lon = my_util.haversine(loc_norm[0]
                                             , loc_norm[1]
                                             , self._scales[0][near_idx[0]+1]
                                             , loc_norm[1]
                                             , 6371.0 - self._scales[2][near_idx[2]])
            if inc[1] == 1:
                diff_lat = my_util.haversine(loc_norm[0]
                                             , loc_norm[1]
                                             , loc_norm[0]
                                             , self._scales[1][near_idx[1]]
                                             , 6371.0 - self._scales[2][near_idx[2]])
            else:
                diff_lat = my_util.haversine(loc_norm[0]
                                             , loc_norm[1]
                                             , loc_norm[0]
                                             , self._scales[1][near_idx[1]+1]
                                             , 6371.0 - self._scales[2][near_idx[2]])
            if inc[2] == 1:
                diff_dep = abs(self._scales[2][near_idx[2]] - loc_norm[2])
            else:
                diff_dep = abs(self._scales[2][near_idx[2]+1] - loc_norm[2])

            velocity = (velocity
                        + (self._geo_speeds
                           [near_idx[0]+inc[0]][near_idx[1]+inc[1]][near_idx[2]+inc[2]]
                           .display_speed())
                        * diff_lon * diff_lat * diff_dep
                        / (dist_lon * dist_lat * dist_dep))

        return velocity

def main():
    """ unit test
    """
    geo_model = GeoModel()
    print(geo_model.get_speed([122.04, 23.46, 20]))

if __name__ == '__main__':
    main()
