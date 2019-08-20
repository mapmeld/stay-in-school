# better prediction attempts
# focus on Grade 1b->2b
# pip3 install scikit-learn numpy scipy xgboost

import csv, json
from random import shuffle

import numpy as np
from scipy import stats
from sklearn import preprocessing, utils
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import BayesianRidge, LinearRegression
from sklearn.neighbors import KNeighborsRegressor
from xgboost import XGBRegressor

from sklearn.metrics import explained_variance_score, r2_score

#from alibi.explainers import AnchorTabular
from eli5 import show_prediction, show_weights


# 06
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

    def predict(algo, zscoreX, zscoreY):
        # print algo, accuracy, r-squared?
        print(algo)
        print('with zScore on X: ' + str(zscoreX) + ' and Y: ' + str(zscoreY))

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


        # try this with Alibi and ELI5
        # ELI5 might have better/faster XGBoost integration?
        #explainer = AnchorTabular(model.predict, feature_names, categorical_names={})
        #explainer.fit(x[:dividing_line], disc_perc=[25, 50, 75])

        #print(str(len(order_of_schools)) + ' and ' + str(len(y_predict)) + ' should equal')
        swdoc = open('swdoc.html', 'w')
        swdoc.write(show_weights(model).data)
        swdoc.close()
        spdoc = open('spdoc.html', 'w')

        myi = 0
        for school in y_predict:
            schools_to_predict[ order_of_schools[myi] ] = int(1000 * float(school))
            myi += 1

            if myi % 60 == 0:
                # 1/10th chance
                spdoc.write(show_prediction(model, x[dividing_line+myi], show_feature_values=True).data)
                #explainer.explain(, threshold=0.95)
        spdoc.close()

        print(explained_variance_score(y[dividing_line:], y_predict))
        print(r2_score(y[dividing_line:], y_predict))

        quit()

    # eli5 and other libraries better than alibi for explaining?

    # scale to municipio pop

    def run_algos():
        for algo in [XGBRegressor]: # BayesianRidge,
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
                headers = row
                feature_names = []
                for vind in remove_columns:
                    headers[vind] = None
                for header in headers[1:-1]:
                    if header is not None:
                        feature_names.append(header)
                # print(feature_names[195])
                # print(feature_names[492])
                # print(feature_names[234])
                # print(feature_names[229])
                # print(feature_names[231])
                # print(feature_names[151])
                # print(feature_names[160])
                # print(feature_names[379])
                # print(feature_names[315])
                # print(feature_names[236])
                # print(feature_names[575])
                retiro_total = row.index('retiros_2010_acelerada_total')
                retiro_final = row.index('retiros_2017_educmedia_crime')
                # if retiro_total is None or retiro_final is None:
                #     print(row)
                #     quit()

        shuffle(orig_datarows)

        datarows = []
        schools_to_predict = {}

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
                        # if len(xrow) == last_index:
                        #     print(str(vind) + ' stored as col # ' + str(len(xrow)))
                        # last_index = len(xrow)

                        if vind not in remove_columns:
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
        export_school_predictions = open('./remembered_predicted_' + str(grade) + '.json', 'w')
        export_school_predictions.write(json.dumps(schools_to_predict))
        export_school_predictions.close()
