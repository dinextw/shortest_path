#!/usr/bin/python

""" The stuffs related to building graph.
"""
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
                or idx_vertex1 > 12856320000000 or idx_vertex2 > 12856320000000):
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
        if weight < 0:
            print("Weight out of range")
        else:
            self._weight = weight

class GraphBuilder(object):
    """ Build the edge of the graph
    """
    def __init__(self):
        self._norm = normgrid.NormGrid()
        self._geo = geomodel.GeoModel()
        self._extra_range = [0.02, 0.02, 20]
        self._idx_loc_min = None
        self._idx_loc_lonmax = None
        self._idx_loc_lonlatmax = None
        self._idx_loc_max = None
    def _set_boundary(self, sta_loc, sou_loc, stage):
        """
        """
        num_lon = 360 * self._norm.get_div() / self._norm.get_grid_gap(stage)[0]
        num_lat = 180 * self._norm.get_div() / self._norm.get_grid_gap(stage)[1]

        loc_min = []
        loc_max = []
        for idx in range(3):
            loc_min.append(min(sta_loc[idx], sou_loc[idx]))
            loc_max.append(max(sta_loc[idx], sou_loc[idx]))

        self._idx_loc_min = int(self._norm.get_norm_index(loc_min, stage)
                                - self._extra_range[0]/self._norm.get_grid_gap(stage)[0]
                                - self._extra_range[1]/self._norm.get_grid_gap(stage)[1]*num_lon)
        self._idx_loc_lonmax = int(self._norm.get_norm_index([loc_max[0], loc_min[1]
                                                              , loc_min[2]], stage)
                                   + self._extra_range[0]/self._norm.get_grid_gap(stage)[0]
                                   - self._extra_range[1]/self._norm.get_grid_gap(stage)[1]*num_lon)
        self._idx_loc_lonlatmax = int(self._norm.get_norm_index([loc_max[0], loc_max[1]
                                                                 , loc_min[2]], stage)
                                      +self._extra_range[0]/self._norm.get_grid_gap(stage)[0]
                                      +(self._extra_range[1]/self._norm.get_grid_gap(stage)[1]
                                        *num_lon))
        self._idx_loc_max = int(self._norm.get_norm_index(loc_max, stage)
                                + self._extra_range[0]/self._norm.get_grid_gap(stage)[0]
                                + self._extra_range[1]/self._norm.get_grid_gap(stage)[1]*num_lon
                                + self._extra_range[2]/self._norm.get_grid_gap(stage)[2]
                                * num_lon * num_lat)

    def _is_in_boundary(self, idx_loc, num_lon, num_lat):
        """
        """

        if idx_loc < self._idx_loc_min or idx_loc > self._idx_loc_max:
            return False
        elif (idx_loc % (num_lon * num_lat) < self._idx_loc_min
              or idx_loc % (num_lon * num_lat) > self._idx_loc_lonlatmax):
            return False
        elif ((idx_loc % (num_lon * num_lat)) % num_lon < self._idx_loc_min % num_lon
              or (idx_loc % (num_lon * num_lat))
              % num_lon > self._idx_loc_lonmax % num_lon):
            return False

        return True

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

        num_lon = 360 * self._norm.get_div() / self._norm.get_grid_gap(stage)[0]
        num_lat = 180 * self._norm.get_div() / self._norm.get_grid_gap(stage)[1]

        edge = []
        self._set_boundary(sta_loc, sou_loc, stage)
        if stage == 1:
            incs = [1, num_lon, num_lon * num_lat]

        elif stage == 2:
            incs = [[0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1], [1, 1, 0]
                    , [1, 0, 1], [0, 1, 1], [1, 1, 1]]
        else:
            print("Error in stage selection at building graph")

        for idx in range(self._norm.get_norm_index(sta_loc, stage)
                         +int(-self._extra_range[0]/self._norm.get_grid_gap(stage)[0]
                              -self._extra_range[1]/self._norm.get_grid_gap(stage)[1]*num_lon)
                         , self._norm.get_norm_index(sou_loc, stage)
                         +int(+self._extra_range[0]/self._norm.get_grid_gap(stage)[0]
                              +self._extra_range[1]/self._norm.get_grid_gap(stage)[1]*num_lon
                              +(self._extra_range[2]/self._norm.get_grid_gap(stage)[2]
                                *num_lon*num_lat))):
            if self._is_in_boundary(idx, num_lon, num_lat):
                for inc in incs:
                    if self._is_in_boundary(idx + inc, num_lon, num_lat):
                        loc = self._norm.recover_norm_loc(idx, stage)
                        loc_adj = self._norm.recover_norm_loc(idx+inc, stage)
                        dist = my_util.get_distance_in_earth(loc, loc_adj
                                                             , my_util.get_shiftlo(self
                                                                                   ._norm
                                                                                   .get_norm_loc(sta_loc
                                                                                                 , stage)
                                                                                   , self
                                                                                   ._norm
                                                                                   .get_norm_loc(sou_loc
                                                                                                 , stage))
                                                             , 6374.7524414062500)
                        weight = dist * (1 / self._geo.get_speed(loc)
                                         + 1 / self._geo.get_speed(loc_adj) * 0.5)
                        edge.append(Edge(idx, idx+inc, weight))


        return edge

def main():
    """ unit test
    """
    graphbuild = GraphBuilder()
    loc_sta = [120, 22, 0]
    loc_sou = [121, 23, 1]
    print("The station is ", loc_sta)
    print("The source is ", loc_sou)
    edge = graphbuild.build_graph(loc_sta, loc_sou, 1)
    print("The number of edges is ", len(edge))

if __name__ == '__main__':
    main()
