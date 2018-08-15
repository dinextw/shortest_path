#!/usr/bin/python

""" The stuffs related to building graph.
"""
import csv
import unittest
import pymysql
import normgrid

class TimeNode(object):
    """ Edge unit of the graph
    """
    def __init__(self, idx, time):
        self._idx = idx
        self._time = time

    def set_idx(self, idx):
        """ Set the index of connected vertice
        Args:
            idx_vertex1, idx_vertex2: index of connected vertices
        Returns:
        Raises:
            Native exceptions.
        """
        if (idx < 0 or idx > 12856320000000):
            print("Index out of range")
        else:
            self._idx = idx

    def set_time(self, time):
        """ Set the weight of the edge
        Args:
            weight: weight of the edge
        Returns:
        Raises:
            Native exceptions.
        """
        if time < 0:
            print("Time out of range")
        else:
            self._time = time

    def get_info(self):
        """ Return the information of edge
        Args:
        Returns:
            list : list of index & weight
        Raises:
            Native exceptions.
        """
        return [self._idx, self._time]


class DataStore(object):
    """ Build the edge of the graph
    """
    def __init__(self, settings=None):
        if settings is None:
            self._host = '35.194.204.50'
            self._user = 'root'
            self._password = 'sh791114'
            self._db_setting = 'travel_time'
        else:
            self._host = settings['host']
            self._user = settings['root']
            self._password = settings['password']
            self._db_setting = settings['db']
        self._db = pymysql.connect(host=self._host
                                   , user=self._user
                                   , password=self._password
                                   , db=self._db_setting)
        self._cursor = self._db.cursor()
        self._norm = normgrid.NormGrid()

    def import_time(self, filepath):
        #timenode = []
        with open(filepath, newline='') as file:
            csvreader = csv.reader(file)
            next(csvreader)
            path = []
            for row in csvreader:
                row_float = []
                for elem in row:
                    row_float.append(float(elem))
                path.append(row_float)
                #timenode.append(TimeNode(self._norm.get_norm_index(row_float[0:3],2),row_float[3]))
        sql = ("CREATE TABLE IF NOT EXISTS table_%d (ID BIGINT, TRAVEL_TIME FLOAT, PRIMARY KEY(ID))"
               % self._norm.get_norm_index(path[-1][0:3], 2))
        self._cursor.execute(sql)
        for vertex in path:
            sql = ("INSERT INTO table_%d (id, travel_time) VALUES(%d, %f) \
                   ON DUPLICATE KEY UPDATE travel_time = LEAST(travel_time, VALUES(travel_time))"
                   % (self._norm.get_norm_index(path[-1][0:3], 2)
                      , self._norm.get_norm_index(vertex[0:3], 2), vertex[3]))
            try:
                self._cursor.execute(sql)
                self._db.commit()
            except:
                self._db.rollback()

    def get_time(self, loc_sta, loc_sou):
        idx_sta = self._norm.get_norm_index(loc_sta, 2)
        idx_sou = self._norm.get_norm_index(loc_sou, 2)
        sql = "SELECT travel_time FROM table_%d WHERE id = %d" % (idx_sta, idx_sou)
        try:
            self._cursor.execute(sql)
            travel_time = self._cursor.fetchone()[0]
            return travel_time
        except:
            print("Error in looking for travel time")

    def close_db(self):
        self._db.close()


class GraphTest(unittest.TestCase):
    """ Test with vertex and edge correctness in graph
    """

def main():
    """ unit test
    """
    test = DataStore()
    test.import_time('./tmp/result.csv')
    print(test.get_time([120, 23, 0], [120.01, 23.01, 1]))
    test.close_db()
    # --> check for Stage 1


if __name__ == '__main__':
    main()
