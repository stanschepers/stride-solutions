import csv
import time
import timeit

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import pyplot as mp
import os

from pystride.Event import Event, EventType
from pystride.PyController import PyController


def trackCases(simulator, event):
    """
        Callback function to track cumulative cases
        after each time-step.
    """
    outputPrefix = simulator.GetConfigValue("run.output_prefix")
    timestep = event.timestep
    cases = simulator.GetPopulation().GetInfectedCount()

    with open(os.path.join(outputPrefix, "cases.csv"), "a") as csvfile:
        fieldnames = ["timestep", "cases"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if timestep == 0:
            writer.writeheader()
        writer.writerow({"timestep": timestep, "cases": cases})


def plotNewCases(outputPrefix, vaccinationLevels):
    """
        Plot new cases per day for a list of vaccination levels.
    """
    legend = []
    for v in vaccinationLevels:
        legend.append(str(v) + '% immune')
        days = []
        newCasesPerDay = []
        prevCumulativeCases = 0  # Keep track of how many cases have been recorded until current time-step
        with open(os.path.join(outputPrefix + "_" + str(v), "cases.csv")) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                days.append(int(row["timestep"]))
                cumulativeCases = int(row["cases"])
                newCasesPerDay.append(cumulativeCases - prevCumulativeCases)
                prevCumulativeCases = cumulativeCases
        plt.plot(days, newCasesPerDay)
    plt.xlabel("Simulation day")
    plt.ylabel("New cases per day")
    plt.legend(legend)
    plt.savefig('immunity_levels.png')
    plt.show()


def plotPorfiling(name, levels, timings):
    """
        Plot timings from profiling
    """
    plt.plot(levels, timings)
    plt.xlabel(name)
    plt.ylabel("time in secondes")
    # plt.legend(legend)
    plt.savefig('profiling_%s.png' % name)
    plt.show()


def runSimulation(outputPrefix=None, vaccinationLevel=None, numDay=None, populationSize=None, seedingRate=None,
                  contactLogMode=None):
    # Set up simulator
    control = PyController(data_dir="data")
    # Load configuration from file
    if populationSize:
        control.loadRunConfig(os.path.join("config", "run_generate_default.xml"))
    else:
        control.loadRunConfig(os.path.join("config", "run_default.xml"))
    # Set some parameters
    if numDay:
        control.runConfig.setParameter("num_days", numDay)

    if vaccinationLevel:
        control.runConfig.setParameter("vaccine_rate", vaccinationLevel / 100)

    if populationSize:
        control.runConfig.setParameter("geopop_gen.population_size", populationSize)

    if seedingRate:
        control.runConfig.setParameter("seeding_rate", seedingRate)

    if contactLogMode:
        control.runConfig.setParameter("contact_log_level", contactLogMode)

    control.runConfig.setParameter("output_cases", "false")
    control.runConfig.setParameter("contact_output_file", "false")
    control.runConfig.setParameter("output_prefix", "output/" + outputPrefix + "_" + str(int(time.time())))
    control.registerCallback(trackCases, EventType.Stepped)
    # Run simulation
    control.control()


def wrapper(func, *args, **kwargs):
    def wrapped():
        return func(*args, **kwargs)

    return wrapped


def main():
    outputPrefix = "Demo"
    # vaccinationLevels = [60, 65, 66.1, 66.15, 66.2, 67, 70, 80]
    vaccinationLevels = [66]

    days = np.linspace(start=10, stop=1000, num=20, dtype=np.int)
    timings_days = []

    populationSize = np.linspace(1000, 10 ** 7, num=1000, dtype=np.int)
    timings_populationSize = []

    imunnityRate = np.linspace(1, 100, endpoint=False, num=9)
    timings_immunityRate = []

    seedingRate = np.linspace(.00000166, .002, num=10)
    timings_seedingRate = []

    contactLogMode = ["None", "Transmissions"]
    timings_contactLogMode = []

    # for nr in vaccinationLevels:
    try:  # FIRST DELETE DIRECTORY FILES, BEFORE ADDING VALUES
        import shutil
        shutil.rmtree("./output", ignore_errors=True)
    except OSError:
        pass

    # Run simulations
    print(len(days))
    for i, d in enumerate(days):
        print(i)
        wrapped = wrapper(runSimulation, outputPrefix=outputPrefix, numDay=d)
        timings_days.append(timeit.timeit(wrapped))

    plotPorfiling("Days", days, timings_days)

    # Post-processing
    # plotNewCases(outputPrefix, vaccinationLevels)


if __name__ == "__main__":
    main()
