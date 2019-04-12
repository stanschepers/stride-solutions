import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import sys


def plot_cumulative_and_new_cases(file):
    data = pd.read_csv(file)

    data_cumulative = []
    data_difference = []
    data_difference_boxplot = []

    boxplot_measure_interval = 10
    boxplot_diffrence_interval = 10

    for col in data:
        data_cumulative.append(data[col].copy())
        data_difference.append(data[col].copy())

    for _ in range(len(data_difference[0])):
        data_difference_boxplot.append([])

    for j in range(len(data_difference)):
        data_array = data_difference[j]
        length = len(data_array)
        result = []
        for i in range(length):
            if i == 0:
                result.append(data_array[i])
                # if max(data_array) > 100:
                #     data_difference_boxplot[i].append(data_array[i])

            else:
                result.append(data_array[i] - data_array[i - 1])
                if i%boxplot_measure_interval == 0:
                    if max(data_array) > 100:
                        data_difference_boxplot[i].append((data_array[i] - data_array[i - boxplot_diffrence_interval])/boxplot_diffrence_interval)
        data_difference[j] = pd.Series(result, copy=True)

    # Plot cumulative
    outbreaks = 0
    for data_points in data_cumulative:
        if max(data_points) >= 100:
            outbreaks += 1
        data_points.plot(kind='line')
    print("amount of outbreaks:", outbreaks)

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

    # Box plot
    boxplot_data = []
    for i in range(len(data_difference[0])):
        if i%boxplot_measure_interval == 0 and i != 0:
            boxplot_data.append(data_difference_boxplot[i])

    plt.boxplot(boxplot_data)
    if boxplot_measure_interval == 1:
        plt.xlabel('Number of days in simulation')
        plt.ylabel('Number of new infected cases')
    else:
        plt.xlabel('Number of ' + str(boxplot_measure_interval) + ' days in simulation')
        plt.ylabel('Avg number of new infected cases')

    plt.show()
    plt.close()  # clf


def final_freq_hist(file):
    data = pd.read_csv(file)

    final_frequencies = data.iloc[[-1]].squeeze().tolist()

    plt.hist(final_frequencies)
    plt.xlabel("Final size after {} days".format(500))
    plt.ylabel("Frequency")
    plt.show()
    plt.close()


def final_freq_bar(file, sorted=False):
    data = pd.read_csv(file)

    final_frequencies = data.iloc[[-1]].squeeze()
    if sorted:
        final_frequencies = final_frequencies.sort_values()

    for i in range(100):
        print(final_frequencies[i])

    x = np.arange(len(final_frequencies))

    plt.bar(x, height=final_frequencies)

    plt.xlabel('Different simulations')
    plt.ylabel('Final number of infected cases')

    plt.xticks([])

    # plt.hist(final_frequencies)
    plt.xlabel("Simulations")
    plt.ylabel("Final size after {} days".format(500))

    plt.show()
    plt.close()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Please supply (only) the name of the file containing stochastic "
              "analysis results.")
    else:
        plot_cumulative_and_new_cases(sys.argv[1])
        #final_freq_hist(sys.argv[1])
        #final_freq_bar(sys.argv[1])
        #final_freq_bar(sys.argv[1], sorted=True)
