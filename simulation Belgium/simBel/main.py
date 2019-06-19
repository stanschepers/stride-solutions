import csv

if __name__ == '__main__':

    with open('../smallflanders/stan_infected.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            # if line_count == 0:
            #     print(f'Column names are {", ".join(row)}')
            #     line_count += 1
            # else:
            lastrow = row

        threshold = 600
        nonOutbreaks = 0
        outbreaks = 0

        for i in range(len(row)):
            if int(row[i]) < threshold:
                nonOutbreaks += 1
            else:
                outbreaks += 1

        print("Outbreaks: ", outbreaks, "\nNon-outbreaks: ", nonOutbreaks)