#!/usr/bin/python

""" The stuffs related to building graph.
"""
import bisect
import numpy as np
import normgrid
import geomodel
import my_util

class Edge(object):
    """ Edge unit of the graph
    """
    def __init__(self, idx_vertex1, idx_vertex2, weight):
        self._idx_vertex1 = idx_vertex1
        self._idx_vertex2 = idx_vertex2
        self._weight = weight
    def set_idx(self, idx_vertex1, idx_vertex2):
        """ Set the index of connected vertice
        Args:
            idx_vertex1, idx_vertex2: index of connected vertices
        Returns:
        Raises:
            Native exceptions.
        """
        if (idx_vertex1 < 0 or idx_vertex2 < 0
            or idx_vertex1 > 12856320000000 or idx_vertex2 > 12856320000000:
            print("Index out of range")
        else:
            self._idx_vertex1 = idx_vertex1
            self._idx_vertex2 = idx_vertex2
    def set_weight(self, weight):
        """ Set the weight of the edge
        Args:
            weight: weight of the edge
        Returns:
        Raises:
            Native exceptions.
        """
        if weight < 0
            print("Weight out of range")
        else:
            self._weight = weight

class GraphBuilder(object):
    """ Build the edge of the graph
    """
    def __init__(self, setting):
        self._norm = normgrid.NormGrid()
        self._geo = geomodel.GeoModel()
        self._setting = setting
        self._edge = []
    def build_graph(self, sta_loc, sou_loc, stage):
        """ Build the whole graph
        Args:
            sta_loc: location of station
            sou_loc: location of source
            stage: number of stage
        Returns:
            _edge: list of edges in the graph
        Raises:
            Native exceptions.
        """
        sta_loc_norm = self._norm.get_norm_loc(sta_loc)
        sou_loc_norm = self._norm.get_norm_loc(sou_loc)
        grid_gap = [0.01, 0.01, 1]
        extra_range = [0.02, 0.02, 20]
        
        incs = [[0.0025, 0, 0], [0.0025, 0, 0], [0, 0.0025, 0], [0, 0, 0.25], [0.0025, 0.0025, 0]
                , [0.0025, 0, 0.25], [0, 0.0025, 0.25], [0.0025, 0.0025, 0.25]]
        if stage == 1:
            range_start = []
            range_end = []
            for idx in range(3):
                if sta_loc_norm[idx] > sou_loc_norm[idx]:
                    range_start.append(sou_loc_norm[idx] - extra_range[idx])
                    range_end.append(sta_loc_norm[idx] + extra_range[idx])
                elif sta_loc_norm[idx] < sou_loc_norm[idx]:
                    range_start.append(sta_loc_norm[idx] - extra_range[idx])
                    range_end.append(sou_loc_norm[idx] + extra_range[idx])
                else:
                    range_start = sta_loc_norm[idx]
                    range_end = sou_loc_norm[idx] + grid_gap[idx]
            for lon in list(my_util.drange(range_start[0], range_end[0], grid_gap[0])):
                for lat in list(my_util.drange(range_start[1], range_end[1], grid_gap[1])):
                    for dep in list(my_util.drange(range_start[2], range_end[2], grid_gap[2]):
                        loc = [lon, lat, dep]
                        loc_idx = self._norm.get_norm_index(loc)
                        loc_speed = self._geo.get_speed(loc)
                        shift_lo = my_util.get_shiftlo(sta_loc_norm, sou_loc_norm)
                        for inc in incs:
                            loc_adj = loc + inc
                            if my_util.is_in_boundary(loc_adj, loc_bound):
                                continue
                            else:
                                loc_adj_idx = self._norm.get_norm_index(loc)
                                loc_adj_speed = self._geo.get_speed(loc)
                                dist = my_util.get_distance_in_earth(loc, loc_adj, shift_lo
                                                                     , 6374.7524414062500)
                                weight = dist * (1 / loc_speed + 1 / loc_adj_speed) * 0.5
                                self._edge.append(Edge(loc_idx, loc_adj_idx, weight))
                                
        return self._edge
        

def main():
    """ unit test
    """
if __name__ == '__main__':
    main()
