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
        legend.append(str(v)+ '% immune')
        days = []
        newCasesPerDay = []
        prevCumulativeCases = 0 # Keep track of how many cases have been recorded until current time-step
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

def runSimulation(outputPrefix, vaccinationLevel):
    # Set up simulator
    control = PyController(data_dir="data")
    # Load configuration from file
    control.loadRunConfig(os.path.join("config", "outbreak_2019_estimates.xml"))
    # Set some parameters
    control.runConfig.setParameter("vaccine_rate", vaccinationLevel / 100)
    control.runConfig.setParameter("output_cases", "false")
    control.runConfig.setParameter("contact_output_file", "false")
    control.runConfig.setParameter("output_prefix", outputPrefix + "_" + str(vaccinationLevel))
    control.runConfig.setParameter("seeding_rate", 0.00000334) # Seed 2 infected persons in population of 600 000
    control.registerCallback(trackCases, EventType.Stepped)
    # Run simulation
    control.control()

def main():
    outputPrefix = "Demo"
    # vaccinationLevels = [60, 65, 66.1, 66.15, 66.2, 67, 70, 80]
    vaccinationLevels = [61, 70, 78, 80]

    for nr in vaccinationLevels:
        try: # FIRST DELETE DIRECTORY FILES, BEFORE ADDING VALUES
            os.remove(outputPrefix+'_'+str(nr)+'/cases.csv')
        except OSError:
            pass

    # Run simulations
    for v in vaccinationLevels:
        runSimulation(outputPrefix, v)
    # Post-processing
    plotNewCases(outputPrefix, vaccinationLevels)

if __name__=="__main__":
    main()