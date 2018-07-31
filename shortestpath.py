#!/usr/bin/python

""" The stuffs related to building graph.
"""
import unittest
import json
import os.path
import graphbuilder
import normgrid
import my_util

class ShortestPath(object):
    """ Build the edge of the graph
    """
    def __init__(self, settings=None):
        self._graphbuild = graphbuilder.GraphBuilder(settings)
        self._norm = normgrid.NormGrid()
        self._result = {}
        self._idx_vertex = {}
        self._filepath_edges = './_input/edges.txt'
        self._filepath_dijk = './../dijkstra/dijk2'
        self._path = {}

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
            self._result['1'] = result_dict
        else:
            self._result['2'] = result_dict
        self._idx_vertex[str(stage)] = idx_vertex

    def _retrieve_norm_path(self, stage):
        if stage == 1:
            result_dict = self._result['1']
        else:
            result_dict = self._result['2']
        idx_path = list(map(int, result_dict['shortest_path']))
        path = []
        for idx in idx_path:
            path.append(self._norm.recover_norm_loc(self._idx_vertex[str(stage)][idx], stage))
        self._path[str(stage)] = path

    def execute_dijk(self, sta_loc, sou_loc):
        """ Execute Dijkstra Program
        Run the dijkstra program by station and source location
        Args:
            sta_loc: location of station
            sou_loc: location of source
        Returns:
            _result_stage_2: travel time of two points
        Raises:
            Native exceptions.
        """
        assert isinstance(sta_loc, list) and isinstance(sou_loc, list) \
            , 'Error in station or source location type'
        assert sta_loc != sou_loc, 'Error in same station and source location'

        edges = self._graphbuild.build_graph(sta_loc, sou_loc, 1)
        self._run_dijk2(edges, sta_loc, sou_loc, 1)
        self._retrieve_norm_path(1)
        edges = self._graphbuild.build_graph(sta_loc, sou_loc, 2, self._path['1'])
        self._run_dijk2(edges, sta_loc, sou_loc, 2)
        self._retrieve_norm_path(2)
        return float(self._result['2']['shortest_weight'])

    def export_path(self, filepath):
        """ Export Stage 2 Path
        Args:
            filepath: Stage 2's file location
        Returns:
        Raises:
            Native exceptions.
        """
        with open(filepath, "w") as out_file:
            tmp = '{0:>18s}, {1:>18s}, {2:>18s}'.format(
                'LON', 'LAT', 'DEP')
            out_file.write('%s\n' % tmp)
            for data in self._path['2']:
                tmp = '{0:>6.12f}, {1:>6.12f}, {2:>6.12f}'.format(
                    data[0], data[1], data[2])
                out_file.write('%s\n' % tmp)

    def get_weight(self):
        """ Return the weight dictionary of every vertexes in graph
        Args:
        Returns:
            idx_weight: dictionary of index versus weight
        Raises:
            Native exceptions.
        """
        idx_weight = {}
        for weight, idx in zip(self._result['2']['total_shortest_vertex_weight']
                               , self._idx_vertex['2']):
            idx_weight[idx] = float(weight)
        return idx_weight

class ShortestPathTest(unittest.TestCase):
    """ Test with vertex and edge correctness in graph
    """
    def test_mod_with_sta_sou(self):
        """ Test if dijkstra can run
        """
        settings = {'extra_range':[0, 0, 0], 'ranges':[0.01, 0.01, 1]
                                                      , 'path_model':'./_input/MOD_H13_uniform'}
        short = ShortestPath(settings)
        loc_sta = [120, 23, 0]
        loc_sou = [120.01, 23.01, 1]
        result = short.execute_dijk(loc_sta, loc_sou)
        self.assertEqual(result, 1.81024)

    def test_mod_with_export_path(self):
        """ Test if output file exists
        """
        settings = {'extra_range':[0, 0, 0], 'ranges':[0.01, 0.01, 1]
                                                      , 'path_model':'./_input/MOD_H13_uniform'}
        short = ShortestPath(settings)
        loc_sta = [120, 23, 0]
        loc_sou = [120.01, 23.01, 1]
        short.execute_dijk(loc_sta, loc_sou)
        filepath = './tmp/result.csv'
        short.export_path(filepath)
        self.assertTrue(os.path.isfile(filepath))

    def test_mod_with_return_weight(self):
        """ Test if weight list is correct
        """
        settings = {'extra_range':[0, 0, 0], 'ranges':[0.01, 0.01, 1]
                                                      , 'path_model':'./_input/MOD_H13_uniform'}
        short = ShortestPath(settings)
        norm = normgrid.NormGrid()
        loc_sta = [120, 23, 0]
        loc_sou = [120.01, 23.01, 1]
        short.execute_dijk(loc_sta, loc_sou)
        weights = short.get_weight()
        self.assertEqual(weights[norm.get_norm_index(loc_sta, 2)], 0)


def main():
    """ unit test
    """

    # --> check for Stage 1
    unittest.main()


if __name__ == '__main__':
    main()
