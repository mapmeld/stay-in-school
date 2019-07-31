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

# load the school data
# drop first column (school code)
# last column is y-values
original_x = []
original_y = []

with open('grad_1b.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    datarows = []
    index = 0
    for row in csv_reader:
        index = index + 1
        if (index > 1):
            datarows.append(row)
    shuffle(datarows)

    for row in datarows:
        xrow = []
        vind = -1
        for val in row[1:-1]:
            vind = vind + 1
            # avoid these always-zero columns
            if vind not in [35, 37]:
                xrow.append(int(val))

        original_x.append(xrow)
        original_y.append(float(row[-1]))

original_x = np.array(original_x)
scaled_x = stats.zscore(np.copy(original_x), axis=0)

original_y = np.array(original_y)
scaled_y = stats.zscore(np.copy(original_y), axis=0)

dividing_line = int(0.8 * len(original_x))

def predict(algo, zscoreX, zscoreY, urbanOnly):
    # print algo, accuracy, r-squared?
    print(algo)
    print('with zScore on X: ' + str(zscoreX) + ' and Y: ' + str(zscoreY) + ' : urban only? ' + str(urbanOnly))

    if zscoreX:
        x = np.copy(scaled_x)
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
# include class size / school size

for algo in [RandomForestRegressor, SGDRegressor, BayesianRidge, LinearRegression, KNeighborsRegressor, SVR, XGBRegressor, AdaBoostRegressor]:
    for zscoreX in [True, False]:
        for zscoreY in [True, False]:
            for urbanOnly in [False]: # True, False
                predict(algo, zscoreX, zscoreY, urbanOnly)
