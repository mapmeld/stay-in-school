# this does the predictions AND some cool explainable AI stuff
# pip3 install scikit-learn numpy scipy xgboost eli5

import csv, json
from random import shuffle

import numpy as np
from scipy import stats
from sklearn.metrics import explained_variance_score, r2_score
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import BayesianRidge, LinearRegression
from xgboost import XGBRegressor

#from alibi.explainers import AnchorTabular
from eli5 import show_prediction, show_weights

grades = ['06', '1b']

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

    def predict(algo, zscoreX, zscoreY):
        # print algo, accuracy, r-squared
        print(algo)
        print('with zScore on X: ' + str(zscoreX) + ' and Y: ' + str(zscoreY))

        # different ZScore options
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


        # Alibi Explainable AI, only has Classifier support
        # we are going to use ELI5
        # ELI5 is typically used in a notebook, but we can export it as HTML

        swdoc = open('swdoc.html', 'w')
        swdoc.write(show_weights(model).data)
        swdoc.close()
        spdoc = open('spdoc.html', 'w')

        # we are remembering our prediction for every school, while it is in the test data
        myi = 0
        for school in y_predict:
            schools_to_predict[ order_of_schools[myi] ] = int(1000 * float(school))
            myi += 1

            if myi % 60 == 0:
                # 1/10th chance of an individual prediction
                spdoc.write(show_prediction(model, x[dividing_line+myi], show_feature_values=True).data)
        spdoc.close()

        # evaluation of test data
        print(explained_variance_score(y[dividing_line:], y_predict))
        print(r2_score(y[dividing_line:], y_predict))

        # only doing one grade for now
        quit()

    def run_algos():
        for algo in [XGBRegressor, BayesianRidge]:
            # I'm currently not running all ZScore options
            for zscoreX in [False]:
                for zscoreY in [True]:
                    predict(algo, zscoreX, zscoreY)

    with open('grad_' + grade + '.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        orig_datarows = []
        index = 0
        for row in csv_reader:
            index = index + 1
            if (index > 1):
                orig_datarows.append(row)
            else:
                # header info
                # remove the same columns from headers which I would remove from the data
                headers = row
                feature_names = []
                for vind in remove_columns:
                    headers[vind] = None
                for header in headers[1:-1]:
                    if header is not None:
                        feature_names.append(header)
                # tell me the meaning of columns which come out of ELI5 importances
                # print(feature_names[195])

                retiro_total = row.index('retiros_2010_acelerada_total')
                retiro_final = row.index('retiros_2017_educmedia_crime')
                # if retiro_total is None or retiro_final is None:
                #     print(row)
                #     quit()

        # random sort of training and test data
        shuffle(orig_datarows)

        datarows = []
        schools_to_predict = {}

        # we do 90% training 10% test data
        # we shift where that 10% comes from, until every school has a predicted value
        for cutout in range(0, 10):
            original_x = []
            original_y = []
            order_of_schools = []

            cutout_start = int(float(cutout) / 10.0 * len(orig_datarows))
            cutout_end = int(float(cutout + 1) / 10.0 * len(orig_datarows))
            print('rows from ' + str(cutout_start) + ' to ' + str(cutout_end))
            pre_cutout = orig_datarows[0:cutout_start]
            cutout_rows = orig_datarows[cutout_start:cutout_end]
            post_cutout = orig_datarows[cutout_end:]
            datarows = pre_cutout + post_cutout + cutout_rows

            rowcount = 0
            for row in datarows:
                if row[-1] != '':
                    if rowcount >= int(0.9 * len(datarows)):
                        order_of_schools.append(row[0])
                    rowcount += 1

                    xrow = []
                    latest_retiro_total = 1
                    vind = -1
                    last_index = -1
                    for val in row[1:-1]:
                        vind = vind + 1

                        # avoid these always-zero columns
                        if vind not in remove_columns:
                            # blank means zero
                            if val == '':
                                val = 0

                            # xrow stores original value
                            xrow.append(int(val))

                    original_x.append(xrow)
                    original_y.append(float(row[-1]))

            original_x = np.array(original_x)
            scaled_x = stats.zscore(np.copy(original_x), axis=0)
            colindex = 0

            original_y = np.array(original_y)
            scaled_y = stats.zscore(np.copy(original_y), axis=0)

            dividing_line = int(0.9 * len(original_x))
            run_algos()

        # export all of the predictions for schools when they were in the test data
        # if we had different ZScore settings, we would keep overwriting it because there's only one file per grade
        # you could change the file name to show any other different settings
        export_school_predictions = open('./remembered_predicted_' + str(grade) + '.json', 'w')
        export_school_predictions.write(json.dumps(schools_to_predict))
        export_school_predictions.close()
