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


def plotNewCases(outputPrefix, vaccinationLevels):
    """
        Plot new cases per day for a list of vaccination levels.
    """
    legend = []
    for v in vaccinationLevels:
        legend.append(str(v) + '% commuting to work')
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
    plt.savefig('commutingLevels.png')
    plt.show()


def runSimulation(outputPrefix, commutingLevel):
    # Set up simulator
    control = PyController(data_dir="data")
    # Load configuration from file
    control.loadRunConfig(os.path.join("config", "2.3.xml"))
    # Set some parameters
    control.runConfig.setParameter("output_cases", "false")
    control.runConfig.setParameter("contact_output_file", "false")
    control.runConfig.setParameter("output_prefix", outputPrefix + "_" + str(commutingLevel))
    control.runConfig.setParameter("seeding_rate", 0.00000334)  # Seed 2 infected persons in population of 600 000
    control.registerCallback(trackCases, EventType.Stepped)
    # control.runConfig._etree.
    control.runConfig.setParameter("geopop_gen.fraction_workplace_commuters", commutingLevel)
    # Run simulation
    control.control()


def main():
    outputPrefix = "commuting"

    # De commuting levels 0.01 tot en met 0.07 laten Stride crashen
    # GEEN IDEE WAAROM

    commutingLevels = [0.0]
    for perc in range(1, 11, 1):
        getal = round(float(perc)*0.1, 2)
        commutingLevels.append(getal)

    # comment onderstaande lijn code uit en kies uw commuting levels!
    # commutingLevels = [0.0, 0.25, 0.5, 0.75, 1.0]

    print(commutingLevels)


    for nr in commutingLevels:
        try:  # FIRST DELETE DIRECTORY FILES, BEFORE ADDING VALUES
            os.remove(outputPrefix + '_' + str(nr) + '/cases.csv')
        except OSError:
            pass

    # Run simulations
    for v in commutingLevels:
        runSimulation(outputPrefix, v)
    # Post-processing
    plotNewCases(outputPrefix, commutingLevels)


if __name__ == "__main__":
    main()
