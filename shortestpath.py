#!/usr/bin/python

""" The stuffs related to building graph.
"""
import unittest
import json
import graphbuilder
import normgrid
import my_util

class ShortestPath(object):
    """ Build the edge of the graph
    """
    def __init__(self, settings=None):
        self._graphbuild = graphbuilder.GraphBuilder(settings)
        self._norm = normgrid.NormGrid()
        self._result_stage_1 = {}
        self._result_stage_2 = {}
        self._filepath_edges = './_input/edges.txt'
        self._filepath_dijk = './../dijkstra/dijk2'

    def _run_dijk2(self, edges, sta_loc, sou_loc, stage):
        idx_vertex = []
        for edge in edges:
            edge_info = edge.get_info()
            idx_vertex.append(edge_info[0])
            idx_vertex.append(edge_info[1])
        idx_vertex = list(set(idx_vertex))
        idx_vertex[idx_vertex.index(self._norm.get_norm_index(sta_loc, stage))] = idx_vertex[0]
        idx_vertex[0] = self._norm.get_norm_index(sta_loc, stage)
        with open(self._filepath_edges, 'w') as the_file:
            line = (str(len(idx_vertex))+", "
                    +str(idx_vertex.index(self._norm.get_norm_index(sou_loc, stage)))+"\n")
            the_file.write(line)
            for edge in edges:
                edge_info = edge.get_info()
                line = (str(idx_vertex.index(edge_info[0]))
                        +", "+str(idx_vertex.index(edge_info[1]))
                        +", "+str(edge_info[2])+"\n")
                the_file.write(line)
        cmd = '%s %s' % (self._filepath_dijk, self._filepath_edges)
        result_dict = json.loads(my_util.run_cmd_get_result(cmd).decode('utf-8'))
        if stage == 1:
            self._result_stage_1 = result_dict
        else:
            self._result_stage_2 = result_dict
        return idx_vertex

    def execute_dijk(self, sta_loc, sou_loc):
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
        edges = self._graphbuild.build_graph(sta_loc, sou_loc, 1)
        idx_vertex = self._run_dijk2(edges, sta_loc, sou_loc, 1)
        idx_path = list(map(int, self._result_stage_1['shortest_path']))
        path = []
        for idx in idx_path:
            path.append(self._norm.recover_norm_loc(idx_vertex[idx], 1))
        edges = self._graphbuild.build_graph(sta_loc, sou_loc, 2, path)
        self._run_dijk2(edges, sta_loc, sou_loc, 2)
        return self._result_stage_2['shortest_weight']

    #def export_path(self, filepath):


class ShortestPathTest(unittest.TestCase):
    """ Test with vertex and edge correctness in graph
    """
    def test_mod_with_sta_sou(self):
        """ Test if program can run
        """
        settings = {'extra_range':[0, 0, 0], 'ranges':[0.01, 0.01, 1]
                                                      , 'path_model':'./_input/MOD_H13_uniform'}
        short = ShortestPath(settings)
        loc_sta = [120, 23, 0]
        loc_sou = [120.01, 23.01, 1]
        result = short.execute_dijk(loc_sta, loc_sou)
        print(result)
        self.assertEqual(1, 1)

def main():
    """ unit test
    """

    # --> check for Stage 1
    unittest.main()


if __name__ == '__main__':
    main()