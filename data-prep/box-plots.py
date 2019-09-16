# scatter plots
import csv

grade = '06'
val = 'grade_pop_7'
sectors = {}

with open('../grad_' + grade + '.csv') as csvfile:
    rdr = csv.reader(csvfile, delimiter=',')
    header = True
    orig = []
    for row in rdr:
        if header:
            orig = row
            header = False
        else:
            index = 0
            nxtyr_sector = int(float(row[orig.index(val)]) / 10.0)
            if nxtyr_sector not in sectors:
                sectors[nxtyr_sector] = [float(row[-1])]
            else:
                sectors[nxtyr_sector].append(float(row[-1]))

bunches = list(sectors.keys())
bunches.sort()
# print(bunches)
wrt = csv.writer(open('bplot.csv', 'w'))
for bunch in bunches:
    vals = sectors[bunch]
    vals.sort()
    # print(vals)
    length = len(vals)
    wrt.writerow([vals[0], vals[int(length / 4.0)], vals[int(length / 2.0)], vals[int(length * 0.75)], vals[-1]])
    if bunch >= 0.8:
        print(bunch)
        print(vals)
