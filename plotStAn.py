import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import sys


def plot_cumulative_and_new_cases(file):
    data = pd.read_csv(file)

    data_cumulative = []
    data_difference = []

    for col in data:
        data_cumulative.append(data[col].copy())
        data_difference.append(data[col].copy())

    for j in range(len(data_difference)):
        data_array = data_difference[j]
        length = len(data_array)
        result = []
        for i in range(length):
            if i == 0:
                result.append(data_array[i])
            else:
                result.append(data_array[i] - data_array[i - 1])
        data_difference[j] = pd.Series(result, copy=True)

    # Plot cumulative
    outbreaks = 0
    for data_points in data_cumulative:
        if max(data_points) >= 100:
            outbreaks += 1
        data_points.plot(kind='line')

    # print("Numer of outbreaks: {nr}".format(nr=outbreaks))

    plt.xlabel('Day in Simulation')
    plt.ylabel('Total number of infected cases')

    plt.show()
    plt.close()  # clf

    # Plot difference
    for data_points in data_difference:
        data_points.plot(kind='line')

    plt.xlabel('Day in Simulation')
    plt.ylabel('Number of new infected cases')

    plt.show()
    plt.close()  # clf


def final_freq_hist(file):
    data = pd.read_csv(file)

    final_frequencies = data.iloc[[-1]].squeeze().sort_values()

    x = np.arange(len(final_frequencies))

    plt.bar(x, height=final_frequencies)
    plt.xticks([])
    plt.show()
    plt.close()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Please supply (only) the name of the file containing stochastic "
              "analysis results.")
    else:
        plot_cumulative_and_new_cases(sys.argv[1])
        final_freq_hist(sys.argv[1])
