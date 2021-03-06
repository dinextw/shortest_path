#!/usr/bin/python

""" The stuffs related to building graph.
"""
import unittest
import json
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
            path_model = None
        else:
            self._extra_range = settings['extra_range']
            self._ranges = settings['ranges']
            path_model = settings['path_model']
        self._norm = normgrid.NormGrid()
        self._geo = geomodel.GeoModel(path_model)
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
                                                +1/self._geo.get_speed(loc_adj))
                            *0.5)
                edge_reverse = Edge(idx+inc, idx
                                    , dist*(1/self._geo.get_speed(loc)
                                            +1/self._geo.get_speed(loc_adj))
                                    *0.5)
                if edge in edges or edge_reverse in edges:
                    continue
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
        Stage 1 and Stage 2 with same code => cubics may be overlapping
        => Create inc in all the directions and then filter repeated ones in other function later
        Args:
            num_lon: number of longitude indexes
            num_lat: number of latitude indexes
        Returns:
        Raises:
            Native exceptions.
        """
        self._incs = []
        if stage == 1:
            for diff_dep in range(0, 2*num_lon*num_lat, num_lon*num_lat):
                for diff_lat in range(-1*num_lon, 2*num_lon, num_lon):
                    for diff_lon in range(-1, 2, 1):
                        if diff_lon+diff_lat+diff_dep == 0:
                            continue
                        else:
                            self._incs.append(diff_lon+diff_lat+diff_dep)
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
        assert isinstance(sta_loc, list) and isinstance(sou_loc, list) \
                , 'Error in station or source location type'
        assert sta_loc != sou_loc, 'Error in same station and source location'
        assert stage == 1 or stage == 2, 'Error in stage selection in building graph initialization'

        if stage == 1:
            loc_bound_upper = [sta_loc]
            loc_bound_lower = [sou_loc]
        elif stage == 2:
            assert path is not None, 'Error in empty stage 1 path'
            loc_bound_upper = [[a-b/2 for a, b in zip(sublist, self._ranges)] for sublist in path]
            loc_bound_lower = [[a+b/2 for a, b in zip(sublist, self._ranges)] for sublist in path]
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

def _test_mod_vertex_que(norm, idx_vertexes):
    num_bnd = 0
    num_surface = 0
    idx_bnd = 0
    loc_check = []
    loc_check_que = []
    for idx, val in enumerate(idx_vertexes):
        if idx == 0:
            loc_check_que.append(norm.recover_norm_loc(idx_vertexes[0], 1))
        elif idx == len(idx_vertexes)-1:
            loc_check_que.append(norm.recover_norm_loc(idx_vertexes[idx_bnd], 1))
            loc_check_que.append(norm.recover_norm_loc(idx_vertexes[idx], 1))
            loc_check.append(loc_check_que)
            break
        elif idx > 0 and idx_vertexes[idx] > idx_vertexes[idx-1]+1:
            if num_bnd == 0:
                loc_check_que.append(norm.recover_norm_loc(idx_vertexes[idx-1], 1))
                num_bnd += 1
            elif num_bnd == 1:
                if idx_vertexes[idx] > idx_vertexes[idx-1]+norm.get_num_lon_index(1):
                    loc_check_que.append(norm.recover_norm_loc(idx_vertexes[idx_bnd], 1))
                    loc_check_que.append(norm.recover_norm_loc(idx_vertexes[idx-1], 1))
                    if num_surface == 0:
                        loc_check.append(loc_check_que)
                    loc_check_que = []
                    loc_check_que.append(norm.recover_norm_loc(idx_vertexes[idx], 1))
                    num_surface += 1
                    num_bnd = 0
            idx_bnd = idx
    return loc_check


class GraphTest(unittest.TestCase):
    """ Test with vertex and edge correctness in graph
    """
    def test_mod_with_vertex_num(self):
        """ Test with number of vertexes in graph
        """
        settings = {'extra_range':[0, 0, 0], 'ranges':[0.01, 0.01, 1], 'path_model':None}
        graphbuild = GraphBuilder(settings)
        norm = normgrid.NormGrid()
        loc_sta = [120, 23, 0]
        loc_sou = [120.01, 23.01, 1]
        grid_gap = norm.get_grid_gap(1)
        edges = graphbuild.build_graph(loc_sta, loc_sou, 1)
        idx_vertex = []
        for edge in edges:
            edge_info = edge.get_info()
            idx_vertex.append(edge_info[0])
            idx_vertex.append(edge_info[1])
        grid_gap_whole = [(x1 - x2)/x3+1 for (x1, x2, x3) in zip(loc_sou, loc_sta, grid_gap)]
        self.assertEqual(len(set(idx_vertex))
                         , int(grid_gap_whole[0]*grid_gap_whole[1]*grid_gap_whole[2]))

    def test_mod_with_vertex_coor(self):
        """ Test with coordinate of boundary vertexes in graph
        """
        settings = {'extra_range':[0, 0, 0], 'ranges':[0.01, 0.01, 1], 'path_model':None}
        graphbuild = GraphBuilder(settings)
        norm = normgrid.NormGrid()
        loc = [[120, 23, 0], [120.01, 23.01, 1], [120, 23, 1], [120, 23.01, 0], [120.01, 23, 0]
               , [120, 23.01, 1], [120.01, 23.01, 0], [120.01, 23, 1]]
        edges = graphbuild.build_graph([120, 23, 0], [120.01, 23.01, 1], 1)
        idx_vertexes = []
        for edge in edges:
            edge_info = edge.get_info()
            idx_vertexes.append(edge_info[0])
            idx_vertexes.append(edge_info[1])
        idx_vertexes = list(set(idx_vertexes))
        idx_vertexes.sort()
        loc_check = _test_mod_vertex_que(norm, idx_vertexes)
        loc_check = [item for sublist in loc_check for item in sublist]
        for elem_loc in loc_check:
            self.assertTrue(elem_loc in loc, msg=None)

    def test_mod_with_edge_num(self):
        """ Test with number of edges in the graph
        """
        settings = {'extra_range':[0, 0, 0], 'ranges':[0.01, 0.01, 1], 'path_model':None}
        graphbuild = GraphBuilder(settings)
        loc_sta = [120, 23, 0]
        loc_sou = [120.01, 23.01, 1]
        edges = graphbuild.build_graph(loc_sta, loc_sou, 1)
        self.assertEqual(len(edges), 28)

    def test_mod_with_surface_edge(self):
        """ Test with edge only on surface in the graph
        """
        settings = {'extra_range':[0, 0, 0], 'ranges':[0.01, 0.01, 1], 'path_model':None}
        graphbuild = GraphBuilder(settings)
        loc_sta = [120, 23, 0]
        loc_sou = [120.01, 23, 1]
        edges = graphbuild.build_graph(loc_sta, loc_sou, 1)
        self.assertEqual(len(edges), 6)

    def test_mod_with_edge_direction(self):
        """ Test edge direction by dijkstra
        """
        settings = {'extra_range':[0, 0, 0], 'ranges':[0.01, 0.01, 1]
                                                      , 'path_model':'./_input/MOD_H13_uniform'}
        graphbuild = GraphBuilder(settings)
        loc_sta = [120, 23, 0]
        loc_sou = [120.01, 23.01, 1]
        edges = graphbuild.build_graph(loc_sta, loc_sou, 1)
        norm = normgrid.NormGrid()
        idx_vertex = []
        for edge in edges:
            edge_info = edge.get_info()
            idx_vertex.append(edge_info[0])
            idx_vertex.append(edge_info[1])
        idx_vertex = list(set(idx_vertex))
        idx_vertex[idx_vertex.index(norm.get_norm_index(loc_sta, 1))] = idx_vertex[0]
        idx_vertex[0] = norm.get_norm_index(loc_sta, 1)
        with open('./_input/edges.txt', 'w') as the_file:
            line = (str(len(idx_vertex))+", "
                    +str(idx_vertex.index(norm.get_norm_index(loc_sou, 1)))+"\n")
            the_file.write(line)
            for edge in edges:
                edge_info = edge.get_info()
                line = (str(idx_vertex.index(edge_info[0]))
                        +", "+str(idx_vertex.index(edge_info[1]))
                        +", "+str(edge_info[2])+"\n")
                the_file.write(line)
        cmd = './../dijkstra/dijk2 ./_input/edges.txt'
        result_dict = json.loads(my_util.run_cmd_get_result(cmd).decode('utf-8'))
        self.assertEqual(result_dict['shortest_weight'], '1.81024')

    def test_mod_with_more_edge(self):
        """ Test edge correctness by more edges in dijkstra
        """
        settings = None
        graphbuild = GraphBuilder(settings)
        loc_sta = [121.740700, 24.428, -0.113000]
        loc_sou = [121.860000, 24.79, 7.500000]
        edges = graphbuild.build_graph(loc_sta, loc_sou, 1)
        norm = normgrid.NormGrid()
        idx_vertex = []
        for edge in edges:
            edge_info = edge.get_info()
            idx_vertex.append(edge_info[0])
            idx_vertex.append(edge_info[1])
        idx_vertex = list(set(idx_vertex))
        idx_vertex[idx_vertex.index(norm.get_norm_index(loc_sta, 1))] = idx_vertex[0]
        idx_vertex[0] = norm.get_norm_index(loc_sta, 1)
        with open('./_input/edges.txt', 'w') as the_file:
            line = (str(len(idx_vertex))+", "
                    +str(idx_vertex.index(norm.get_norm_index(loc_sou, 1)))+"\n")
            the_file.write(line)
            for edge in edges:
                edge_info = edge.get_info()
                line = (str(idx_vertex.index(edge_info[0]))
                        +", "+str(idx_vertex.index(edge_info[1]))
                        +", "+str(edge_info[2])+"\n")
                the_file.write(line)
        cmd = './../dijkstra/dijk2 ./_input/edges.txt'
        result_dict = json.loads(my_util.run_cmd_get_result(cmd).decode('utf-8'))
        self.assertTrue(bool(result_dict['shortest_weight']))



def main():
    """ unit test
    """

    # --> check for Stage 1
    unittest.main()


if __name__ == '__main__':
    main()
