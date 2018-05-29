#!/usr/bin/python

""" Provide some common utility functions.
"""

import argparse
import datetime
import bisect
import inspect
import json
import math
import os
import subprocess
import sys
import time

DEBUG_FILE = './_debug.log'

def run_cmd_get_result(cmd):
    """ Run shell command and return the output.
    Args:
        cmd: the shell command
    Returns:
        The output of running shell command.
    Raises:
        Native exceptions.
    """

    cmds = cmd.split(' ')
    parent_dir = os.path.dirname(cmds[0])
    curr_dir = os.getcwd()
    if parent_dir and parent_dir != '.':
        #print '***** DEBUG, parent_dir=%s' % parent_dir
        os.chdir(parent_dir)

    ret = ''
    #cmd = cmd.encode('utf8')
    pipe = subprocess.Popen([cmd], stdout=subprocess.PIPE, shell=True)
    ret = pipe.stdout.read().strip()

    os.chdir(curr_dir)

    return ret

def check_if_contain_in_list(lst, item):
    """  Efficient `item in lst` for sorted lists
    Args:
        lst:        the list
        item:       the item to be compared
    Returns:
        prev_idx:   the previous index
        next_idx:   the next idex
        (-1, -1):   less than the min item, or larger than the max item
    Raises:
        Native exceptions.
    """
    if item > lst[-1] or item < lst[0]:
        return (-1, -1)

    insert = bisect.bisect_left(lst, item)
    if lst[insert] == item:
        return (insert, insert)

    return (insert - 1, insert)

def haversine(lon1, lat1, lon2, lat2, alt=6371):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees).
    Args:
        lon1, lon2:     the longitute values
        lat1, lat2:     the latitute values
        rad:            the altitude, 6371 is the earch radius
    Returns:
        distance:       the distance in KM
    Raises:
        Native exceptions.
    rad:    6371 is earth radius.
    """
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(math.radians, [lon1, lat1, lon2, lat2])

    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    val1 = (math.sin(dlat / 2) ** 2 +
            math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2)
    val2 = 2 * math.asin(math.sqrt(val1))
    distance = alt * val2
    return distance

def haversine_ex(point1, point2):
    """
    Calculate distance between two points in earch, by using haversine formula
    Args:
        point1:         coordinate array of the first point,
                        [lon, lat, dep]
        point1:         coordinate array of the first point,
                        [lon, lat, dep]
    Returns:
        distance:       the distance in KM
    Raises:
        Native exceptions.
    """
    dep_diff = point1[2] - point2[2]
    radius = 6371 - min([point1[2], point2[2]])
    surf_diff = haversine(point1[0], point1[1], point2[0], point2[1], radius)
    dist = math.sqrt(dep_diff ** 2 + surf_diff ** 2)

    return dist

def _decide_lons(point1, point2):
    bre_p1 = point1[0] if point1[0] > 0 else 360.0 + point1[0]
    bso_p2 = point2[0] if point2[0] > 0 else 360.0 + point2[0]
    diff_lon = abs(bso_p2 - bre_p1)
    if diff_lon <= 180.0:
        if bso_p2 <= bre_p1:
            #shift_lon = bso_p2 - (180.0 - diff_lon) / 2.0
            lon_1 = (180.0 - diff_lon) / 2.0
            lon_2 = lon_1 + diff_lon
        else:
            #shift_lon = bre_p1 - (180.0 - diff_lon) / 2.0
            lon_2 = (180.0 - diff_lon) / 2.0
            lon_1 = lon_2 + diff_lon
    else:
        diff_lon = 360.0 - diff_lon
        if bso_p2 <= bre_p1:
            #shift_lon = bso_p2 - (diff_lon + (180.0 - diff_lon) / 2.0)
            lon_1 = (180.0 - diff_lon) / 2.0 + diff_lon
            lon_2 = lon_1 - diff_lon
        else:
            #shift_lon = bre_p1 - (diff_lon + (180.0 - diff_lon) / 2.0)
            lon_2 = (180.0 - diff_lon) / 2.0 + diff_lon
            lon_1 = lon_2 - diff_lon

    return lon_1, lon_2

def get_shiftlo(point_station, point_source):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees).
    Args:
        point_station:  the location of station
        point_source:   the location of earthquake source
    Returns:
        shiftlo:        the value to shift at longitude
    Raises:
        Native exceptions.
    """
    bre_p1 = point_station[0] if point_station[0] > 0 else 360.0 + point_station[0]
    bso_p2 = point_source[0] if point_source[0] > 0 else 360.0 + point_source[0]
    diff_lon = abs(bso_p2 - bre_p1)
    shift_lon = 0.0e10
    if diff_lon <= 180.0:
        if bso_p2 <= bre_p1:
            shift_lon = bso_p2 - (180.0 - diff_lon) / 2.0
        else:
            shift_lon = bre_p1 - (180.0 - diff_lon) / 2.0
    else:
        diff_lon = 360.0 - diff_lon
        if bso_p2 <= bre_p1:
            shift_lon = bso_p2 - (diff_lon + (180.0 - diff_lon) / 2.0)
        else:
            shift_lon = bre_p1 - (diff_lon + (180.0 - diff_lon) / 2.0)

    return shift_lon

def _geog_to_geoc(xla):
    rad_per_deg = 0.0174532925199432955
    b2a_sq = 0.993305521
    lat_new = math.atan(b2a_sq * math.tan(rad_per_deg * xla)) / rad_per_deg

    return lat_new

def get_distance_in_earth(point1, point2, shiftlo, radius):
    """
    Calculate distance between two points in earch.
    NOTE: The code is ported from Geo's C code.
          I don't understand the code actually.
    Args:
        point1:         coordinate array of the first point,
                        [lon, lat, dep]
        point1:         coordinate array of the first point,
                        [lon, lat, dep]
        shiftlo:        the value to shift at longitude
        radius:         the altitude, the average earth radius
    Returns:
        distance:       the distance in KM
    Raises:
        Native exceptions.
    """
    #print 'point1=%s, point2=%s' % (str(point1), str(point2))

    #print ('*****(my_util), input point1=%s, point2=%s, shiftlo=%f' %
    #       (str(point1), str(point2), shiftlo))

    r2d = 90.0 / math.asin(1.0)

    ts1 = (90.00 - _geog_to_geoc(point1[1])) / r2d
    tr2 = (90.00 - _geog_to_geoc(point2[1])) / r2d

    xx1 = (radius - point1[2]) * math.sin(ts1) * math.cos(
        (point1[0]-shiftlo) / r2d)
    yy1 = (radius - point1[2]) * math.sin(ts1) * math.sin(
        (point1[0]-shiftlo) / r2d)
    zz1 = (radius - point1[2]) * math.cos(ts1)
    xx2 = (radius - point2[2]) * math.sin(tr2) * math.cos(
        (point2[0]-shiftlo) / r2d)
    yy2 = (radius - point2[2]) * math.sin(tr2) * math.sin(
        (point2[0]-shiftlo) / r2d)
    zz2 = (radius - point2[2]) * math.cos(tr2)

    dist = math.sqrt((xx2 - xx1) ** 2 + (yy2 - yy1) ** 2 + (zz2 - zz1) ** 2)

    return dist



def get_time_string(seconds):
    """ Generate '00d:00h:00m:00s' format string based on input seconds.
    Args:
        seconds:    the seconds
    Returns:
        time_str:   the time string in '00d:00h:00m:00s'
    Raises:
        Native exceptions.
    """
    sec = datetime.timedelta(seconds=seconds)
    delta = datetime.datetime(1, 1, 1) + sec
    if delta.day > 1:
        tmp = ('%dd:%dh:%dm:%ds'
               % (delta.day-1, delta.hour, delta.minute, delta.second))
    elif delta.hour > 0:
        tmp = '%dh:%dm:%ds' % (delta.hour, delta.minute, delta.second)
    elif delta.minute > 0:
        tmp = '%dm:%ds' % (delta.minute, delta.second)
    else:
        tmp = '%ds' % delta.second

    return tmp


def get_arg_value(argv, key):
    """ Get value of key in arguments.
    Args:
        argv:       arguments array
        key:        the key to find value
    Returns:
        value_string:
                    For example, giving argv '-arg1 abc -arg2 99'
                    Then giving key='-arg1' will return 'abc'.
                    Giving key='-arg2' will return '99'.
    Raises:
        Native exceptions.
    """
    if key not in argv:
        return None

    try:
        next_idx = argv.index(key) + 1
        return argv[next_idx]
    except IndexError:
        return None

def simple_log(log_path, msg, print_console=False):
    """ Write log (msg) into log_path
    Args:
        log_path:    the log file path
        msg:         the log msg
    Returns:
    Raises:
        Native exceptions.
    """
    if print_console:
        print msg

    parent_dir = os.path.dirname(log_path)
    if not os.path.exists(parent_dir):
        os.mkdir(parent_dir)

    with open(log_path, 'a') as outfile:
        outfile.write('%s\n' % msg)


def write_endtime_log(log_path, start_time):
    """ Write total time log.
    Args:
        log_path:       the log file path
        stgart_time:    the start time
    Returns:
    Raises:
        Native exceptions.
    """
    elapsed_time = time.time() - start_time
    msg = ('-----> Total execution time=%.3f (%s)' %
           (elapsed_time, get_time_string(elapsed_time)))
    simple_log(log_path, msg)




def init_debug():
    """ Initialize the debug flag based on sys.argv='-debug'.
    Args:
    Returns:
    Raises:
        Native exceptions.
    """
    if '-debug' in sys.argv:
        if os.path.isfile(DEBUG_FILE):
            os.remove(DEBUG_FILE)

def debug_log(var_dict, notes=''):
    """ Write debug log (msg) into debug.log
    Args:
        log_path:    the log file path
        msg:         the log msg
    Returns:
    Raises:
        Native exceptions.
    """

    if '-debug' not in sys.argv:
        return

    #(frame, filename, line_number, function_name, lines, index) = (
    #    inspect.getouterframes(inspect.currentframe())[1])
    filename = inspect.getouterframes(inspect.currentframe())[1][1]
    line_number = inspect.getouterframes(inspect.currentframe())[1][2]
    function_name = inspect.getouterframes(inspect.currentframe())[1][3]


    header = ('<%s>(%d)[%s()]' %
              (os.path.basename(filename), line_number, function_name))
    vals = ''
    #keys = sorted(var_dict.keys())
    #for key in keys:
    #    vals = (('%s, %s=%s' % (vals, str(key), str(var_dict[key]))) if vals
    #        else ('%s=%s' % (str(key), str(var_dict[key]))))

    for key, val in var_dict.iteritems():
        vals = (('%s, %s=%s' % (vals, str(key), str(val))) if vals
                else ('%s=%s' % (str(key), str(val))))

    msg = '%s -> %s, %s' % (header, vals, notes)
    with open(DEBUG_FILE, 'a') as outfile:
        outfile.write('%s\n' % msg)

def get_current_time_str(millisecond=False):
    """ return the current time string in "%Y%m%d%H%M%S.%f"
    Args:
        None
    Returns:
        string:     the current time string in "%Y%m%d%H%M%S.%f"
    Raises:
        Native exceptions.
    """
    if millisecond:
        return datetime.datetime.now().strftime("%Y%m%d_%H%M%S.%f")
    else:
        return datetime.datetime.now().strftime("%Y%m%d_%H%M%S")


def quit_if_keys_not_exist(keys_to_check, target_dict):
    """ Quit the program if any key not found in the target_dict.
    Args:
        keys_to_check:      the keys to check
        target_dict:        the target dict
    Returns:
    Raises:
        Native exceptions.
    """
    filename = inspect.getouterframes(inspect.currentframe())[1][1]
    line_number = inspect.getouterframes(inspect.currentframe())[1][2]
    function_name = inspect.getouterframes(inspect.currentframe())[1][3]
    caller_info = ('<%s>(%d)[%s()]' %
                   (os.path.basename(filename), line_number, function_name))

    failed_keys = []
    for key in keys_to_check:
        if key not in target_dict:
            failed_keys.append(key)

    if failed_keys:
        print ('****** ERROR, expected keys(%s) not found when calling %s' %
               (str(failed_keys), caller_info))
        quit()

def check_and_create_parent_dir(file_paths):
    """ Check and create parent dir if not existing.
    Args:
        paths:          the paths to check
    Returns:
    Raises:
        Native exceptions.
    """

    for path in file_paths:
        parent_dir = os.path.dirname(path)
        #print ('***** DEBUG, file_paths=%s, parent_dir = %s' %
        #       (file_paths, parent_dir))
        if not os.path.exists(parent_dir):
            os.makedirs(parent_dir)


def get_3d_coors_string(coors, fp12=True):
    """ Generate a coordinates string in array format.
    Args:
        coors:          the coordinates in array
    Returns:
        string:
    Raises:
        Native exceptions.
    """
    if fp12:
        return '%.12f, %.12f, %.12f' % (coors[0], coors[1], coors[2])
    else:
        return '%.6f, %.6f, %.6f' % (coors[0], coors[1], coors[2])


def write_dict_json(in_dict, json_filepath, to_console=False):
    """ Write dict to josn file.
    Args:
        dict:               the dict to write
        json_filepath:      the json filepath
    Returns:
        the json string
    Raises:
        Native exceptions.
    """
    dict_json = json.dumps(in_dict, indent=4, sort_keys=True)
    with open(json_filepath, 'w') as writefile:
        writefile.write(dict_json)

    if to_console:
        print dict_json

    return dict_json

def parse_args_by_helps(desc, argv_helps):
    """ Setup and get the args from sys.argv.
    Args:
        desc:               the description of the program
        argv_helps:         the dict of argv
    Returns:
        args:               the arguments object
    Raises:
        Native exceptions.
    """
    parser = argparse.ArgumentParser(description=desc)
    for key in argv_helps['required']:
        tmp = '-%s' % key
        parser.add_argument(tmp, action='store', dest=key,
                            required=True,
                            help=argv_helps['required'][key])
    for key in argv_helps['optional']:
        tmp = '-%s' % key
        parser.add_argument(tmp, action='store', dest=key,
                            default=argv_helps['optional_default'][key],
                            help=argv_helps['optional'][key])
    return parser.parse_args()


def trans_square_to_comma_vals(in_str):
    """ Transfer square string to comma string.
    Args:
        in_str:             ex: "[112][123][345]"
    Returns:
        rets:               ex: "112, 123, 345"
    Raises:
        Native exceptions.
    """
    tmps = in_str.split(']')
    rets = []
    for tmp in tmps:
        if tmp:
            rets.append(tmp[1:])
    return '%s,%s,%s' % (rets[0], rets[1], rets[2])


def main():
    """ unit test
    """

    # --> test get_distance_in_earth() and haversine_ex()
    '''
    radius = 6374.752598

    test_point_pairs = [
        [[120.42, 22.833, 0.66], [120.42, 22.823, -0.34]],
        [[120.42, 22.833, 0.66], [120.42, 22.8275, 0.2215]],
        [[120.42, 22.8275, 0.2215], [120.42, 22.823, -0.34]],
        [[120.413100, 23.425100, -0.020000], [120.412100, 23.419100, 0.968300]],
        [[120.421000, 22.829300, 0.643200], [120.422700, 22.823300, -0.340000]]
    ]

    #exp_vals = [1.49577, 0.752815, 0.752072]
    print '---> check with Geo program '
    #for idx, pair in enumerate(test_point_pairs):
    for pair in test_point_pairs:
        dist = get_distance_in_earth(pair[0], pair[1], radius)
        dist_h = haversine_ex(pair[0], pair[1])
        diff = dist_h - dist
        #diff = exp_vals[idx] - dist
        #print ('dist=%f, exp=%f, diff=%f, err_ratio=%f, dist_h=%f' %
        #       (dist, exp_vals[idx], diff, diff/exp_vals[idx], dist_h))
        print ('geo dist=%f, haversine dist=%f, diff=%f, err_ratio=%f%%' %
               (dist, dist_h, diff, diff * 100 / dist))
    #''' # pylint: disable=W0105

    # --> test check_and_create_parent_dir
    '''
    check_and_create_parent_dir(['./_test1/ggg.temp'])
    ''' # pylint: disable=W0105

    # --> test quit_if_keys_not_exist
    '''
    test_dict = {'key1':1, 'key2':2}
    #test_keys = ['key1', 'key3', 'key4']
    test_keys = ['key1', 'key2']
    quit_if_keys_not_exist(test_keys, test_dict)
    #''' # pylint: disable=W0105

if __name__ == '__main__':
    main()
