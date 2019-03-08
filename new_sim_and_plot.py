import csv
import matplotlib.pyplot as plt
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


def runSim(outputPrefix, vacRate=None, immRate=None, r0=None, rngSeed=None):

    try:  # FIRST DELETE DIRECTORY FILES, BEFORE ADDING VALUES
        os.remove(outputPrefix + "_" + str(vacRate) + "_" + str(immRate) + "_"
                  + str(r0) + "_" + str(rngSeed) + '/cases.csv')
    except OSError:
        pass

    # Set up simulator
    control = PyController(data_dir="data")

    # Load configuration from file
    control.loadRunConfig(os.path.join("config", "outbreak_2019_estimates.xml"))

    # Set some parameters
    control.runConfig.setParameter("output_prefix", outputPrefix + "_" +
                                   str(vacRate) + "_" + str(immRate) + "_" +
                                   str(r0) + "_" + str(rngSeed))
    control.runConfig.setParameter("seeding_rate", 0.00000334)
    control.runConfig.setParameter("output_cases", "false")
    control.runConfig.setParameter("contact_output_file", "false")

    if vacRate:
        control.runConfig.setParameter("vaccine_profile", "Random")
        control.runConfig.setParameter("vaccine_rate", vacRate / 100)
    else:
        control.runConfig.setParameter("vaccine_profile", "None")
    if immRate:
        control.runConfig.setParameter("immunity_profile", "Random")
        control.runConfig.setParameter("immunity_rate", immRate / 100)
    else:
        control.runConfig.setParameter("immunity_profile", "None")
    if r0:
        control.runConfig.setParameter("r0", r0)
    if rngSeed:
        control.runConfig.setParameter("rng_seed", rngSeed)

    control.registerCallback(trackCases, EventType.Stepped)
    # Run simulation
    control.control()


def plotImmAvg(outputPrefix, vacRate=None, immRate=None, r0=None, seeds=None):

    if seeds:

        results = []

        for seed in seeds:
            newCasesPerDay = []
            prevCumulativeCases = 0

            with open(os.path.join(outputPrefix + "_" + str(vacRate) + "_" +
                                   str(immRate) + "_" + str(r0) + "_"
                                   + str(seed), "cases.csv")) as csvfile:
                reader = csv.DictReader(csvfile)

                for row in reader:
                    # if row["cases"]=='cases' and row["timestep"]=='timestep':
                    #     continue
                    cumulativeCases = int(row["cases"])
                    newCasesPerDay.append(cumulativeCases - prevCumulativeCases)
                    prevCumulativeCases = cumulativeCases

            results.append(newCasesPerDay)

        avg = []
        days = range(len(results[0]))
        sim_count = len(seeds)
        for i in days:
            avg_elem = 0
            for list in results:
                avg_elem += list[i]
            avg_elem /= sim_count
            avg.append(avg_elem)

        plt.plot(days, avg)

        plt.xlabel("Simulation day")
        plt.ylabel("New cases per day")
        plt.title(str(immRate) + "% immune " + str(len(seeds)) + " seed average")
        # plt.savefig('immunity_levels.png')
        plt.show()


def plotImmAvgAll(outputPrefix, vacRate=None, immRates=None, r0=None,
                      seeds=None):
    if seeds and immRates:

        legend = []

        for immRate in immRates:

            results = []

            for seed in seeds:
                newCasesPerDay = []
                prevCumulativeCases = 0

                with open(os.path.join(outputPrefix + "_" + str(vacRate) + "_" +
                                       str(immRate) + "_" + str(r0) + "_"
                                       + str(seed), "cases.csv")) as csvfile:
                    reader = csv.DictReader(csvfile)

                    for row in reader:
                        cumulativeCases = int(row["cases"])
                        newCasesPerDay.append(cumulativeCases -
                                              prevCumulativeCases)
                        prevCumulativeCases = cumulativeCases

                results.append(newCasesPerDay)

            avg = []
            days = range(len(results[0]))
            sim_count = len(seeds)
            for i in days:
                avg_elem = 0
                for list in results:
                    avg_elem += list[i]
                avg_elem /= sim_count
                avg.append(avg_elem)

            legend.append(str(immRate) + "% immune")
            plt.plot(days, avg)

        plt.xlabel("Simulation day")
        plt.ylabel("New cases per day")
        plt.title(str(len(seeds)) + " seed average")
        plt.legend(legend)
        # plt.savefig('immunity_levels.png')
        plt.show()


def plotImmAvgMultiR0(outputPrefix, vacRate=None, immRate=None, r0s=None,
                      seeds=None):
    if seeds and r0s:

        legend = []

        for r0 in r0s:

            results = []

            for seed in seeds:
                newCasesPerDay = []
                prevCumulativeCases = 0

                with open(os.path.join(outputPrefix + "_" + str(vacRate) + "_" +
                                       str(immRate) + "_" + str(r0) + "_"
                                       + str(seed), "cases.csv")) as csvfile:
                    reader = csv.DictReader(csvfile)

                    for row in reader:
                        cumulativeCases = int(row["cases"])
                        newCasesPerDay.append(cumulativeCases -
                                              prevCumulativeCases)
                        prevCumulativeCases = cumulativeCases

                results.append(newCasesPerDay)

            avg = []
            days = range(len(results[0]))
            sim_count = len(seeds)
            for i in days:
                avg_elem = 0
                for list in results:
                    avg_elem += list[i]
                avg_elem /= sim_count
                avg.append(avg_elem)

            legend.append("$R_0$ = " + str(r0))
            plt.plot(days, avg)

        plt.xlabel("Simulation day")
        plt.ylabel("New cases per day")
        plt.title(
            str(immRate) + "% immune " + str(len(seeds)) + " seed average")
        plt.legend(legend)
        # plt.savefig('immunity_levels.png')
        plt.show()


if __name__ == "__main__":
    immunityLevels = [70.1, 70.2, 70.3, 70.4, 70.5, 70.6, 70.7, 70.8, 70.9]
    rng_seeds = range(1, 11)
    r0s = range(12, 19)

    # for lvl in immunityLevels:
    # for r0 in r0s:
    #     for seed in rng_seeds:
    #         runSim("AVG", immRate=lvl, rngSeed=seed)
    plotImmAvgMultiR0("AVG", immRate=70.8, r0s=r0s,  seeds=rng_seeds)
    # plotImmAvgAll("AVG", immRates=immunityLevels,  seeds=rng_seeds)