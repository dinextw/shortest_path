#!/usr/bin/python

""" The stuffs related to building graph.
"""
import time
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

    def __eq__(self, that):
        if not isinstance(that, Edge):
            return False
        info_that = that.get_info()
        return self._idx_vertex1 == info_that[0] and self._idx_vertex2 == info_that[1]

    def __hash__(self):
        idx_sort = sorted([self._idx_vertex1, self._idx_vertex2])
        return ((idx_sort[0]+idx_sort[1])*(idx_sort[0]+idx_sort[1]+1)//2
                +idx_sort[1])

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

    def get_info(self):
        """ Return the information of edge
        Args:
        Returns:
            list : list of index & weight
        Raises:
            Native exceptions.
        """
        return [self._idx_vertex1, self._idx_vertex2, self._weight]


class GraphBuilder(object):
    """ Build the edge of the graph
    """
    def __init__(self, settings=None):
        if settings is None:
            self._extra_range = [0.02, 0.02, 20]
            self._ranges = [0.05, 0.05, 2]
        self._norm = normgrid.NormGrid()
        self._geo = geomodel.GeoModel()
        self._bnd = {}
        self._incs = []

    def _set_boundary(self, sta_loc, sou_loc, stage):
        loc_min = []
        loc_max = []
        for idx in range(3):
            loc_min.append(min(sta_loc[idx], sou_loc[idx]))
            loc_max.append(max(sta_loc[idx], sou_loc[idx]))

        if stage == 1:
            extra_bound = self._extra_range
        elif stage == 2:
            extra_bound = [0, 0, 0]
        else:
            print("Error in Stage Selection in extra bound")

        self._bnd['idx_loc_min'] = self._norm.get_norm_index([loc_min[0]-extra_bound[0]
                                                              , loc_min[1]-extra_bound[1]
                                                              , loc_min[2]], stage)
        self._bnd['idx_loc_lonmax'] = (self._norm.get_norm_index([loc_max[0]+extra_bound[0]
                                                                  , loc_min[1]-extra_bound[1]
                                                                  , loc_min[2]], stage))
        self._bnd['idx_loc_lonlatmax'] = (self._norm.get_norm_index([loc_max[0]+extra_bound[0]
                                                                     , loc_max[1]+extra_bound[1]
                                                                     , loc_min[2]], stage))
        for idx in range(3):
            loc_max[idx] = loc_max[idx] + extra_bound[idx]
        self._bnd['idx_loc_max'] = self._norm.get_norm_index(loc_max, stage)

    def _is_in_boundary(self, idx_loc, num_lon, num_lat):
        if idx_loc < self._bnd['idx_loc_min'] or idx_loc > self._bnd['idx_loc_max']:
            return False
        elif (idx_loc % (num_lon * num_lat) < self._bnd['idx_loc_min'] % (num_lon * num_lat)
              or idx_loc % (num_lon * num_lat) > self._bnd['idx_loc_lonlatmax']
              % (num_lon * num_lat)):
            return False
        elif ((idx_loc % (num_lon * num_lat)) % num_lon < self._bnd['idx_loc_min'] % num_lon
              or (idx_loc % (num_lon * num_lat))
              % num_lon > self._bnd['idx_loc_lonmax'] % num_lon):
            return False

        return True

    def _create_edge(self, edges, idx, setting):
        """ Create edge for each vertex
        Add inc to create edge in different directions
        then check if the connected vertex exists or the edge is repeated
        Args:
            edges: edge list to add
            idx: index of the current vertex
        Returns:
        Raises:
            Native exceptions.
        """
        for inc in self._incs:
            if self._is_in_boundary(idx + inc, setting['num_lon'], setting['num_lat']):
                loc = self._norm.recover_norm_loc(idx, setting['stage'])
                loc_adj = self._norm.recover_norm_loc(idx+inc, setting['stage'])
                dist = (my_util.get_distance_in_earth(loc, loc_adj, setting['shiftlo']
                                                      , 6374.7524414062500))
                edge = Edge(idx, idx+inc, dist*(1/self._geo.get_speed(loc)
                                                +1/self._geo.get_speed(loc_adj)
                                                *0.5))
                if setting['stage'] == 2:
                    edge_reverse = Edge(idx+inc, idx
                                        , dist*(1/self._geo.get_speed(loc)
                                                +1/self._geo.get_speed(loc_adj)
                                                *0.5))
                    if edge in edges or edge_reverse in edges:
                        continue
                    # --> Use Matlab to check if number of edges per vertex is 124
                    #with open('edge.txt', 'a') as the_file:
                    #    edge_info = edge.get_info()
                    #    the_file.write(str(edge_info)+"\n")
                edges.add(edge)

    def _divide_and_create(self, edges, stage, setting):
        """ Divide cubic into vertex and create edge
        Designate cubic's lon, lat, dep to divide into vertex, then create edge by each vertex
        Args:
            edges: edge list to add
            stage: designated stage
            setting: formed by variables
        Returns:
        Raises:
            Native exceptions.
        """
        shiftlo = my_util.get_shiftlo(self._norm.get_norm_loc(setting['loc_upper'], stage)
                                      , self._norm.get_norm_loc(setting['loc_lower'], stage))
        for diff_idx_dep in range(0, self._bnd['idx_loc_max']-self._bnd['idx_loc_lonlatmax']+1
                                  , setting['num_lon']*setting['num_lat']):
            for diff_idx_lat in range(0, (self._bnd['idx_loc_lonlatmax']
                                          -self._bnd['idx_loc_lonmax']+1)
                                      , setting['num_lon']):
                for idx in range(self._bnd['idx_loc_min'] + diff_idx_lat + diff_idx_dep
                                 , self._bnd['idx_loc_lonmax'] + 1 + diff_idx_lat + diff_idx_dep):
                    self._create_edge(edges, idx
                                      , {'shiftlo':shiftlo
                                                   , 'stage':stage
                                                             , 'num_lon':setting['num_lon']
                                                                         , 'num_lat':\
                                                                            setting['num_lat']}
                                     )

    def _build_inc(self, num_lon, num_lat, stage):
        """ Create inc for desinate stage
        For Stage 1, link level = 1 => nonoverlapping one cubic
        , so incs can be in specific directions only
        For Stage 2, link level = 2 => cubics may be overlapping
        . create inc in all the directions and then filter repeated ones in other function later
        Args:
            num_lon: number of longitude indexes
            num_lat: number of latitude indexes
        Returns:
        Raises:
            Native exceptions.
        """
        self._incs = []
        if stage == 1:
            self._incs = [1, num_lon, 1+num_lon, num_lon*num_lat, num_lon*num_lat+1
                          , num_lon*num_lat+num_lon, num_lon*num_lat+num_lon+1
                          , num_lon*num_lat-num_lon, num_lon*num_lat-num_lon+1
                          , 1-num_lon
                          , 1-num_lon-num_lon*num_lat, 1-num_lat*num_lon, 1+num_lon-num_lat*num_lon]
        elif stage == 2:
            for diff_dep in range(0, 3*num_lon*num_lat, num_lon*num_lat):
                for diff_lat in range(-2*num_lon, 3*num_lon, num_lon):
                    for diff_lon in range(-2, 3, 1):
                        if diff_lon+diff_lat+diff_dep == 0:
                            continue
                        else:
                            self._incs.append(diff_lon+diff_lat+diff_dep)

    def build_graph(self, sta_loc, sou_loc, stage, path=None):
        """ Build the whole graph by edge list
        The graph consists of overlapping or connecting cubics.
        Each cubic is formed by loc_upper(uppermost coordiante) and loc_lower(lowermost coordiante)
        Divide cubic furthrer into vertex and then create edge
        Args:
            sta_loc: location of station
            sou_loc: location of source
            stage: designated stage
        Returns:
            edge: list of edges in the graph
        Raises:
            Native exceptions.
        """
        edges = set()
        self._bnd = {}
        if stage == 1:
            loc_bound_upper = [sta_loc]
            loc_bound_lower = [sou_loc]
        elif stage == 2:
            if path is None:
                print("Error in empty stage 1 path")
                return None
            loc_bound_upper = [[a-b/2 for a, b in zip(sublist, self._ranges)] for sublist in path]
            loc_bound_lower = [[a+b/2 for a, b in zip(sublist, self._ranges)] for sublist in path]
        else:
            print("Error in stage selection in building graph initialization")
            return None
        num_lon = self._norm.get_num_lon_index(stage)
        num_lat = self._norm.get_num_lat_index(stage)
        self._build_inc(num_lon, num_lat, stage)
        for (loc_upper, loc_lower) in zip(loc_bound_upper, loc_bound_lower):
            self._set_boundary(loc_upper, loc_lower, stage)
            self._divide_and_create(edges, stage
                                    , {'loc_upper':loc_upper
                                                   , 'loc_lower':loc_lower
                                                                 , 'num_lon':num_lon
                                                                             , 'num_lat':num_lat})
        return edges


def main():
    """ unit test
    """


    graphbuild = GraphBuilder()

    # --> check for Stage 1
    loc_sta = [120, 23, 0]
    loc_sou = [120.01, 23.01, 1]
    print("The station is ", loc_sta)
    print("The source is ", loc_sou)
    edge = graphbuild.build_graph(loc_sta, loc_sou, 1)
    print("The number of edges is ", len(edge))

    # --> check for Stage 2
    time_start = time.time()
    loc_sta = [120, 23, 0]
    loc_sou = [120.01, 23.01, 1]
    print("The station is ", loc_sta)
    print("The source is ", loc_sou)
    edge = graphbuild.build_graph(loc_sta, loc_sou, 2, [loc_sta, loc_sou])
    time_end = time.time()
    print("The number of edges is ", len(edge))
    print("CPU Time is ", time_end - time_start)
if __name__ == '__main__':
    main()
