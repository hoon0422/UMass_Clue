""" Module to analyze crawling.

This module has functions to analyze crawling by 'log.txt'.

"""

from matplotlib import pyplot as plt
import numpy as np
import os


def get_times(log_file: str):
    """
    Get a list of times when the crawler access to the detail page.
    :param log_file: the name of the log file.
    :return: a list of times when the crawler access to the detail page.
    """
    times = []

    with open(log_file, 'r') as file:
        data_str_list = file.read().strip().split('\n')

    for data_str in data_str_list:
        if not data_str[0].isnumeric():
            break
        times.append(float(data_str[:data_str.find(' ')]))

    return times


def get_time_diff(times: list):
    """
    Get the time difference from the list of times.
    :param times: the list of times, which is the result of 'get_times' function.
    :return: the list of time difference.
    """
    diff = []
    prev = times[0]
    for time in times[1:]:
        diff.append(time - prev)
        prev = time

    return diff


def get_total_time(times: list):
    """
    Get the total time for crawling.
    :param times: the list of times, which is the result of 'get_times' function.
    :return: total time for crawling in second.
    """
    return times[len(times) - 1] - times[0]


def draw_time_diff_graph(log_file):
    """
    Show the graph of time difference.
    :param log_file: the name of the log file.
    """
    time_diff = get_time_diff(get_times(log_file))
    plt.ylabel('Time difference (sec)')
    plt.xlabel('Number of data')
    plt.plot(time_diff)
    plt.show()


if __name__ == "__main__":
    times = get_times(os.path.join("..", "raw", "log.txt"))
    time_diff = get_time_diff(times)
    print("Total time:", "%d min %f sec" % (int(get_total_time(times) / 60), get_total_time(times) % 60))
    print("Average:", np.mean(time_diff))
    print("STD:", np.std(time_diff))

    plt.ylabel('Time difference (sec)')
    plt.xlabel('Number of data')
    plt.plot(time_diff)
    plt.show()
