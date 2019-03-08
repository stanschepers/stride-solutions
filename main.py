import csv
import time
import timeit

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import pyplot as mp
import os

from memory_profiler import profile
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


def plotProfiling(name, levels, timings, bar=False):
    """
        Plot timings from profiling
    """
    if bar:
        plt.bar(levels, timings)
    else:
        plt.plot(levels, timings)
    plt.xlabel(name)
    plt.ylabel("Time (in seconds)")
    plt.title("Time Profiling %s" % name)
    # plt.suptitle("Default config")
    plt.savefig('profiling_%s.png' % name.replace(" ", "_"))
    plt.show()


# @profile
def runSimulation(outputPrefix=None, immunityRate=None, numDay=None, populationSize=None, seedingRate=None,
                  contactLogMode=None):
    # Set up simulator
    control = PyController(data_dir="data")
    # Load configuration from file
    if populationSize is not None:
        control.loadRunConfig(os.path.join("config", "run_generate_default.xml"))
    else:
        control.loadRunConfig(os.path.join("config", "run_default.xml"))
    # Set some parameters
    if numDay is not None:
        control.runConfig.setParameter("num_days", numDay)

    if immunityRate is not None:
        print(immunityRate)
        control.runConfig.setParameter("immunity_rate", immunityRate)

    if populationSize is not None:
        pass
        control.runConfig._etree.find("geopop_gen").find("population_size").text = str(populationSize)

    if seedingRate is not None:
        control.runConfig.setParameter("seeding_rate", seedingRate)

    if contactLogMode is not None:
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

    populationSize = np.linspace(1000, 10 ** 7, num=20, dtype=int)
    timings_populationSize = []

    imunnityRate = np.linspace(0, 1, endpoint=False, num=100)
    timings_immunityRate = []

    seedingRate = np.linspace(.00000001, 1, num=20)
    timings_seedingRate = []

    contactLogMode = ["None", "Transmissions", "All", "Susceptibles"]
    timings_contactLogMode = []

    # for nr in vaccinationLevels:
    try:  # FIRST DELETE DIRECTORY FILES, BEFORE ADDING VALUES
        import shutil
        shutil.rmtree("./output", ignore_errors=True)
    except OSError:
        pass

    # Run simulations
    # print(len(days))
    # for i, d in enumerate(days):
    #     print("Number %d/%d" % (i + 1, len(days)))
    #     start = time.time()
    #     runSimulation(outputPrefix, numDay=d)
    #     timings_days.append(time.time() - start)
    # plotProfiling("Days", days, timings_days)

    for i, p in enumerate(populationSize):
        print("Number %d/%d" % (i, len(populationSize)))
        start = time.time()
        runSimulation(outputPrefix, populationSize=p)
        timings_populationSize.append(time.time() - start)

    plotProfiling("Population Size", populationSize, timings_populationSize)

    # for i, r in enumerate(imunnityRate):
    #     print("Number %d/%d" % (i, len(imunnityRate)))
    #     start = time.time()
    #     runSimulation(outputPrefix, immunityRate=r)
    #     timings_immunityRate.append(time.time() - start)
    #
    # plotProfiling("Immunity Rate", imunnityRate, timings_immunityRate)

    # for i, r in enumerate(seedingRate):
    #     print("Number %d/%d" % (i, len(seedingRate)))
    #     start = time.time()
    #     runSimulation(outputPrefix)
    #     timings_seedingRate.append(time.time() - start)
    #
    # plotProfiling("Seeding Rate", seedingRate, timings_seedingRate)

    #
    # for i, r in enumerate(contactLogMode):
    #     print("Number %d/%d" % (i + 1, len(contactLogMode)))
    #     start = time.time()
    #     runSimulation(outputPrefix, contactLogMode=r)
    #     timings_contactLogMode.append(time.time() - start)
    #
    # plotProfiling("Contact Log", [i for i in contactLogMode], timings_contactLogMode, bar=True)

    # Post-processing
    # plotNewCases(outputPrefix, vaccinationLevels)


if __name__ == "__main__":
    main()
