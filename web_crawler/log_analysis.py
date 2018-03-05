from matplotlib import pyplot as plt


def get_times(log_file: str):
    times = []

    with open(log_file, 'r') as file:
        data_str_list = file.read().strip().split('\n')

    for data_str in data_str_list:
        if not data_str[0].isnumeric():
            break
        times.append(float(data_str[:data_str.find(' ')]))

    return times


def get_time_diff(times: list):
    diff = []
    prev = times[0]
    for time in times[1:]:
        diff.append(time - prev)
        prev = time

    return diff


def draw_time_diff_graph(log_file):
    time_diff = get_time_diff(get_times(log_file))
    plt.ylabel('Time difference (sec)')
    plt.xlabel('Number of data')
    plt.plot(time_diff)
    plt.show()


if __name__ == "__main__":
    draw_time_diff_graph("../raw/log.txt")
