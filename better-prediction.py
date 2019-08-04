# better prediction attempts
# focus on Grade 1b->2b
# pip3 install scikit-learn numpy scipy xgboost

import csv
from random import shuffle

import numpy as np
from scipy import stats
from sklearn import preprocessing, utils
from sklearn.ensemble import RandomForestRegressor, AdaBoostRegressor
from sklearn.linear_model import SGDRegressor, BayesianRidge, LinearRegression #, LogisticRegression
from sklearn.neighbors import KNeighborsRegressor #, RadiusNeighborsRegressor
from sklearn.svm import SVR
from xgboost import XGBRegressor

from sklearn.metrics import explained_variance_score, r2_score

#'01','02','03','04','05','06','07','08'
grades = ['1b']

# column indexes
remove_columns = [35, 37, 419, 420,421,422,423,424,428,498,499,500,501,502,504,505,506,507,508,510,511,512,513,514,516,517,518,519,520,522,523,524,525,526,527,528,529,530,531, 532, 536, 563, 564, 565, 566, 567, 568, 572, 574, 607, 614, 616, 619, 620] # all zeroes, I think
retiro_total = None
retiro_final = None

for grade in grades:
    print(grade)
    # load the school data
    # drop first column (school code)
    # last column is y-values
    original_x = []
    x_retiro_shares = []
    original_y = []

    with open('grad_' + grade + '.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        datarows = []
        index = 0
        for row in csv_reader:
            index = index + 1
            if (index > 1):
                datarows.append(row)
            else:
                # header info
                retiro_total = row.index('retiros_2010_acelerada_total')
                retiro_final = row.index('retiros_2017_educmedia_crime')
                # if retiro_total is None or retiro_final is None:
                #     print(row)
                #     quit()

        shuffle(datarows)

        for row in datarows:
            if row[-1] != '':
                xrow = []
                xrow_retiro_shares = []
                latest_retiro_total = 1
                vind = -1
                last_index = -1
                for val in row[1:-1]:
                    vind = vind + 1
                    # avoid these always-zero columns
                    # if len(xrow) == last_index:
                    #     print(str(vind) + ' stored as col # ' + str(len(xrow)))
                    # last_index = len(xrow)

                    if vind not in remove_columns:
                        if val == '':
                            val = 0

                        # xrow stores original value
                        xrow.append(int(val))

                        # retiros shares %ages of students who left for various reasons
                        if vind >= retiro_total and vind <= retiro_final:
                            if ((vind - retiro_total) % 6) == 0:
                                # this is a total for this year/grade level
                                val = int(val)
                                latest_retiro_total = float(val) or 1.0
                            else:
                                # this is a number of people who left for a particular reason
                                # which we represent in retiro_shares as a percentage float
                                val = float(val) / latest_retiro_total
                            xrow_retiro_shares.append(val)
                        else:
                            xrow_retiro_shares.append(int(val))

                original_x.append(xrow)
                x_retiro_shares.append(xrow_retiro_shares)
                original_y.append(float(row[-1]))

    original_x = np.array(original_x)
    scaled_x = stats.zscore(np.copy(original_x), axis=0)

    x_retiro_shares = np.array(x_retiro_shares)
    scaled_retiro_shares = stats.zscore(np.copy(x_retiro_shares), axis=0)
    colindex = 0
    for col in scaled_retiro_shares[0]:
        if str(col) == 'nan':
            print(colindex)
        colindex += 1

    original_y = np.array(original_y)
    scaled_y = stats.zscore(np.copy(original_y), axis=0)

    dividing_line = int(0.8 * len(original_x))

    def predict(algo, zscoreX, zscoreY, retiroPercent, urbanOnly):
        # print algo, accuracy, r-squared?
        print(algo)
        print('with zScore on X: ' + str(zscoreX) + ' and Y: ' + str(zscoreY) + ' and retiros_share ? ' + str(retiroPercent) + ' and urban only? ' + str(urbanOnly))

        if zscoreX:
            if retiroPercent:
                x = np.copy(scaled_retiro_shares)
            else:
                x = np.copy(scaled_x)
        else:
            if retiroPercent:
                x = np.copy(x_retiro_shares)
            else:
                x = np.copy(original_x)

        if zscoreY:
            y = np.copy(scaled_y)
        else:
            y = np.copy(original_y)

        model = algo()
        model.fit(x[:dividing_line], y[:dividing_line])
        y_predict = model.predict(x[dividing_line:])

        print(explained_variance_score(y[dividing_line:], y_predict))
        print(r2_score(y[dividing_line:], y_predict))

    # eli5 and other libraries better than alibi for explaining?

    # scale to municipio pop
    # urban only

# RandomForestRegressor, SGDRegressor, KNeighborsRegressor, AdaBoostRegressor
    for algo in [BayesianRidge, LinearRegression, SVR, XGBRegressor]:
        for zscoreX in [False]: # True, False
            for zscoreY in [True, False]:
                for retiroPercent in [True, False]:
                    for urbanOnly in [False]: # True, False
                        predict(algo, zscoreX, zscoreY, retiroPercent, urbanOnly)
