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
    """ Build the database to store travel time
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

    def import_time(self, idx_weight, idx_sta):
        """ Import vertexes's travel time
        Args:
            idx_weight: dictionary of vertexes's travel time
            idx_sta: index of station location
        Returns:
        Raises:
            Native exceptions.
        """
        """
        timenode = []
        with open(filepath, newline='') as file:
            csvreader = csv.reader(file)
            next(csvreader)
            path = []
            for row in csvreader:
                row_float = []
                for elem in row:
                    row_float.append(float(elem))
                path.append(row_float)
                timenode.append(TimeNode(self._norm.get_norm_index(row_float[0:3],2),row_float[3]))
        """
        sql = ("CREATE TABLE IF NOT EXISTS table_%d (ID BIGINT, TRAVEL_TIME FLOAT, PRIMARY KEY(ID))"
               % idx_sta)
        self._cursor.execute(sql)
        for idx, time in idx_weight.items():
            sql = ("INSERT INTO table_%d (id, travel_time) VALUES(%d, %f) \
                   ON DUPLICATE KEY UPDATE travel_time = LEAST(travel_time, VALUES(travel_time))"
                   % (idx_sta, idx, time))
            try:
                self._cursor.execute(sql)
                self._db.commit()
            except:
                self._db.rollback()

    def get_time(self, loc_sta, loc_sou):
        """ Get the travel time of specific source
        Args:
            loc_sta: location of station
            loc_sou: location of source
        Returns:
            travel_time: travel time of specific source
        Raises:
            Native exceptions.
        """

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
        """ Close the connection session
        Args:
        Returns:
        Raises:
            Native exceptions.
        """
        self._db.close()

class TestDataStore(object):
    """ Access to database to check
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

    def get_num_row(self):
        """ Return the number of row
        Args:
        Returns:
            num_row: total number of rows in database
        Raises:
            Native exceptions.
        """
        sql = ("SELECT SUM(table_rows) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = '%s'"
               % self._db_setting)
        self._cursor.execute(sql)
        num_row = self._cursor.fetchone()[0]
        return num_row

    def delete_and_recreate_db(self):
        """ Clean up and Recreate Database for other test
        Args:
        Returns:
        Raises:
            Native exceptions.
        """
        sql = "DROP DATABASE travel_time"
        self._cursor.execute(sql)
        sql = "CREATE DATABASE travel_time"
        self._cursor.execute(sql)

    def close_db(self):
        """ Close the connection session
        Args:
        Returns:
        Raises:
            Native exceptions.
        """
        self._db.close()


def _test_mod_read_weight_file(filepath):
    norm = normgrid.NormGrid()
    with open(filepath, newline='') as file:
        csvreader = csv.reader(file)
        next(csvreader)
        idx_path = {}
        loc_path = []
        count = 0

        for row in csvreader:
            row_float = []
            for elem in row:
                row_float.append(float(elem))
            if count == 0:
                loc_sou = row_float[0:3]
                count += 1
            idx_path[norm.get_norm_index(row_float[0:3], 2)] = row_float[3]
            loc_path.append(row_float)
        idx_sta = norm.get_norm_index(row_float[0:3], 2)
        loc_sta = row_float[0:3]
    return (idx_path, idx_sta, loc_sou, loc_sta, loc_path)


class DataTest(unittest.TestCase):
    """ Test with Database write and read action
    """
    def test_mod_with_duplicate_element(self):
        """ Test if duplicate table will cause error in reading travel time
        """
        test = DataStore()

        info_result1 = _test_mod_read_weight_file('./tmp/result1.csv')
        test.import_time(info_result1[0], info_result1[1])

        info_result2 = _test_mod_read_weight_file('./tmp/result1.csv')
        test.import_time(info_result2[0], info_result2[1])
        test.close_db()

        check = TestDataStore()
        num_row = check.get_num_row()
        check.delete_and_recreate_db()
        check.close_db()
        self.assertEqual(len(info_result1[0]), num_row)

    def test_mod_with_table_correctness(self):
        """ Test if travel times stored in table are correct
        """
        test = DataStore()

        info_result = _test_mod_read_weight_file('./tmp/result1.csv')
        test.import_time(info_result[0], info_result[1])

        time = []
        time_check = []
        for loc in info_result[4]:
            time.append(test.get_time(info_result[3], loc[0:3]))
            time_check.append(loc[3])
        test.close_db()
        self.assertEqual(time, time_check)

    def test_mod_with_two_tables(self):
        """ Test if two or more tables can be created in database
        """
        test = DataStore()
        check = TestDataStore()
        check.delete_and_recreate_db()

        info_result1 = _test_mod_read_weight_file('./tmp/result1.csv')
        info_result2 = _test_mod_read_weight_file('./tmp/result2.csv')
        test.import_time(info_result1[0], info_result1[1])
        test.import_time(info_result2[0], info_result2[1])

        time1 = []
        time1_check = []
        for loc in info_result1[4]:
            time1.append(test.get_time(info_result1[3], loc[0:3]))
            time1_check.append(loc[3])
        time2 = []
        time2_check = []
        for loc in info_result2[4]:
            time2.append(test.get_time(info_result2[3], loc[0:3]))
            time2_check.append(loc[3])
        test.close_db()
        num_row = check.get_num_row()

        check.delete_and_recreate_db()
        check.close_db()
        self.assertEqual((num_row, time1, time2), (len(info_result1[0])+len(info_result2[0])
                                                   , time1_check, time2_check))


def main():
    """ unit test
    """
    unittest.main()


if __name__ == '__main__':
    main()
