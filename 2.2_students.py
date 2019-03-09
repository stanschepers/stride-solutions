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

def vaccinateStudents(simulator, event):
    """
        Callback function to track cumulative cases
        after 7 days.
    """
    outputPrefix = simulator.GetConfigValue("run.output_prefix")
    timestep = event.timestep
    cases = simulator.GetPopulation().GetInfectedCount()

    if (timestep == 6): #dag0 is ook een dag
        pop = simulator.GetPopulation()
        for pIndex in range(pop.size()):
            if pop[pIndex].GetHealth().IsSusceptible():
                if 18 <= pop[pIndex].GetAge() <= 26:
                    pop[pIndex].GetHealth().SetImmune()


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
        legend.append("Students vaccinated after 7 days: "+str(v))
        days = []
        newCasesPerDay = []
        prevCumulativeCases = 0 # Keep track of how many cases have been recorded until current time-step
        name = str(v).lower()
        with open(os.path.join(outputPrefix+ "_" + name, "cases.csv")) as csvfile:
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

def runSimulation(outputPrefix, vaccinated):
    # Set up simulator
    control = PyController(data_dir="data")
    # Load configuration from file
    control.loadRunConfig(os.path.join("config", "2.2.xml"))


    # Set some parameters
    control.runConfig.setParameter("output_cases", "false")
    control.runConfig.setParameter("contact_output_file", "false")
    control.runConfig.setParameter("output_prefix", outputPrefix)
    control.runConfig.setParameter("seeding_rate", 0.00000334) # Seed 2 infected persons in population of 600 000

    if(vaccinated):
        control.runConfig.setParameter("vaccine_profile", "None")
        control.registerCallback(vaccinateStudents, EventType.Stepped)
    else:
        control.runConfig.setParameter("vaccine_profile", "None")
        control.registerCallback(trackCases, EventType.Stepped)

    # Run simulation
    control.control()

def main():
    prefix = "2.2_vaccinated"
    statusses = [False, True]

    for status in statusses:
        try:  # FIRST DELETE DIRECTORY FILES, BEFORE ADDING VALUES
            name = "_"+str(status).lower()
            os.remove(prefix + name + '/cases.csv')
        except OSError:
            pass

        # Run simulations
        runSimulation(prefix + name, status)

    # Post-processing
    plotNewCases(prefix, statusses)

if __name__=="__main__":
    main()