#!/usr/bin/python

""" The stuffs related to shortest path.
"""
import os
import subprocess
import normgrid

class Bending(object):
    """ execute bending method
    Public Methods:
        get_time: get the travel time of two location
    """
    _filepath = None
    _norm = None
    def __init__(self, filepath=None):
        if filepath is None:
            self._filepath = "./_input/"
        else:
            self._filepath = filepath
        self._norm = normgrid.NormGrid()
    def get_time(self, sta_loc, sou_loc):
        """ Get the travel time of bending
        Args:
            sta_loc :  location of station
            sou_loc :  location of source
        Returns:
            time : travel time
        Raises:
            Native exceptions.
        """
        os.chdir(self._filepath)

        sta_loc_norm = self._norm.get_norm_loc(sta_loc)
        sta_loc_norm[2] = -sta_loc_norm[2]*1000
        with open('sta_location.txt', 'w') as file_sta:
            file_sta.write(" ".join(str(x) for x in sta_loc_norm))
        sou_loc_norm = self._norm.get_norm_loc(sou_loc)
        with open('sou_location.txt', 'w') as file_sou:
            file_sou.write(" ".join(str(x) for x in sou_loc_norm))

        subprocess.run("./pseudo_bending")

        with open('RESULTS.txt', 'r') as file_result:
            num = file_result.readline()
        return float(num)

def main():
    """ unit test
    """
    test = Bending()
    time = test.get_time([120.676000, 24.1475, -0.020000], [121.100000, 23.92, 9.000000])
    print(time)

if __name__ == '__main__':
    main()
