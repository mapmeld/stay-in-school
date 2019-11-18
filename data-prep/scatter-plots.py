# scatter plots
import csv

grade = '08'
graphs = [
    ['hurtos_1000', 'hurtos_2000', 'hurtos_3000'],
    ['robos_1000', 'robos_2000', 'robos_3000'],
    ['homicidios_1000', 'homicidios_2000', 'homicidios_3000'],
]
# SELECT "CODIGÓ C.E." FROM "Sol_MINED_2019_024_coordenadas" WHERE "DPTO" = 6;
school_codes = open('sansalvador.csv', 'r').read().split("\n")
points = []

with open('./grad_' + grade + '.csv') as csvfile:
    rdr = csv.reader(csvfile, delimiter=',')
    header = True
    orig = []
    for row in rdr:
        if header:
            orig = row
            header = False
            for graph in graphs:
                points.append([])
        else:
            index = 0

            # skip if special school_code is needed
            school_code = row[0]
            if (len(school_codes) > 0) and (school_code not in school_codes):
                continue
            # add other variables
            for graph in graphs:
                # get graduation rate (last column)
                oprow = [row[-1]]

                for col in graph:
                    oprow.append(float(row[orig.index(col)])) #/ float(row[orig.index('near_schools_pop')]))
                points[index].append(oprow)
                index += 1

# output CSV
index = 0
for graph in points:
    wrt = csv.writer(open('csv_' + str(index) + '.csv', 'w'))
    for row in graph:
        # row = [graduation, ...vars...]
        wrt.writerow(row)
    index += 1
