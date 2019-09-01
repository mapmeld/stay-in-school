# predicting
# pip3 install scikit-learn numpy scipy xgboost
# (if using it) pip3 install auto-sklearn

import csv
from random import shuffle

import numpy as np
from scipy import stats
from sklearn.metrics import explained_variance_score, r2_score

# Predictive Modeling
from sklearn.linear_model import BayesianRidge, LinearRegression
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor

# from sklearn.neighbors import KNeighborsRegressor, RadiusNeighborsRegressor
# from sklearn.svm import SVR

# AutoML libraries
from autosklearn.regression import AutoSklearnRegressor
# from tpot import TPOTRegressor


grades = ['01', '02', '03', '04', '05', '06', '07', '08', '1b']

# column indexes
# these 'remove_columns' have all zeroes or some other problem
# we can safely remove them without affecting the prediction
remove_columns = [35, 37, 419, 420,421,422,423,424,428,498,499,500,501,502,504,505,506,507,508,510,511,512,513,514,516,517,518,519,520,522,523,524,525,526,527,528,529,530,531, 532, 536, 563, 564, 565, 566, 567, 568, 572, 574, 607, 614, 616, 619, 620] # all zeroes, I think
retiro_total = None
retiro_final = None

for grade in grades:
    print(grade)
    # load the school data
    # drop first column (school code)
    # last column is y-values (target, dropout rate)
    original_x = []
    original_y = []

    # retiro_shares is an experiment to store dropout numbers as a %
    # for example instead of 1 or 5 students left due to crime, it's 20% or 10%
    x_retiro_shares = []

    # open the CSV file for this grade
    with open('grad_' + grade + '.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        datarows = []
        index = 0
        for row in csv_reader:
            index = index + 1
            if (index > 1):
                # data row
                datarows.append(row)
            else:
                # header row, collect some info here
                retiro_total = row.index('retiros_2010_acelerada_total')
                retiro_final = row.index('retiros_2017_educmedia_crime')
                # if retiro_total is None or retiro_final is None:
                #     print(row)
                #     quit()

        # random sort of rows
        # this is important because training and test data is cut from this
        shuffle(datarows)

        for row in datarows:
            # if the dropout rate is calculated, we can work with this row
            if row[-1] != '':
                xrow = []
                xrow_retiro_shares = []
                latest_retiro_total = 1
                vind = -1
                last_index = -1
                for val in row[1:-1]:
                    vind = vind + 1

                    # make sure column varies between rows
                    if vind not in remove_columns:

                        if val == '':
                            # blank means 0
                            val = 0

                        # xrow adds int
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

                # store meaningful columns
                original_x.append(xrow)
                x_retiro_shares.append(xrow_retiro_shares)

                # store target value
                original_y.append(float(row[-1]))

    # convert to numpy array type
    original_x = np.array(original_x)

    # Z-Score is related to standard deviation
    # it makes it easier to compare meaningful differences (i.e. compare 1 vs. 3 on a scale 1-10, and 1 vs. 3 on a scale 1-100)
    # we have original_x and scaled_x to test out if zscore is helpful
    scaled_x = stats.zscore(np.copy(original_x), axis=0)

    x_retiro_shares = np.array(x_retiro_shares)
    scaled_retiro_shares = stats.zscore(np.copy(x_retiro_shares), axis=0)

    # print an alert if the ZScore resulted in any NaN (not-a-number) errors
    # this happens if we tried to do standard deviation on a column that was all 0s or something like that
    colindex = 0
    for col in scaled_retiro_shares[0]:
        if str(col) == 'nan':
            print(colindex)
        colindex += 1

    original_y = np.array(original_y)
    # ZScore on the target values too
    scaled_y = stats.zscore(np.copy(original_y), axis=0)

    # dividing between training and test data
    dividing_line = int(0.8 * len(original_x))

    def predict(algo, zscoreX, zscoreY, retiroPercent, urbanOnly):
        # print algo, accuracy, and r-squared
        print(algo)
        print('with zScore on X: ' + str(zscoreX) + ' and Y: ' + str(zscoreY) + ' and retiros_share ? ' + str(retiroPercent) + ' and urban only? ' + str(urbanOnly))

        # load correct x and y based on what I am testing at the moment
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

        # some algorithms have special parameters
        if algo == AutoSklearnRegressor:
            model = algo(time_left_for_this_task=600, per_run_time_limit=120)
        elif algo == RandomForestRegressor:
            model = algo(n_estimators=150)
        # elif algo == TPOTRegressor:
        #     model = algo(config_dict='TPOT light')
        else:
            model = algo()

        # this is where the model gets trained!
        model.fit(x[:dividing_line], y[:dividing_line])

        # TPOT score
        # print(model.score(x[dividing_line:], y[dividing_line:]))

        # see how well the test data works
        y_predict = model.predict(x[dividing_line:])
        print(explained_variance_score(y[dividing_line:], y_predict))
        print(r2_score(y[dividing_line:], y_predict))

    # eli5 / other explainable AI is in the explain-good-and-bad-predictions.py

    # more ideas: scale to municipio pop, urban only

    for algo in [XGBRegressor, RandomForestRegressor]:
        for zscoreX in [True, False]:
            for zscoreY in [True, False]:
                for retiroPercent in [False]: # I didn't find this to ever be helpful
                    for urbanOnly in [False]: # not implemented
                        predict(algo, zscoreX, zscoreY, retiroPercent, urbanOnly)
