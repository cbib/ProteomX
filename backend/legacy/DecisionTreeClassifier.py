#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Credits: Claire Lescoat, Macha Nikolski


"""
Decision tree classifier algorithm

To add:

- parameters for : balanced/unbalanced class, stratify test and train, scale data
- options : grid search, cross-validation
- plots (and metrics) : ROC curve

"""


import argparse
import pandas as pd
import re
import matplotlib.pyplot as plt
import sklearn
from sklearn.tree import export_graphviz
from sklearn.externals.six import StringIO
from IPython.display import Image
import pydotplus
import pydot
from sklearn.tree import DecisionTreeClassifier # Import Decision Tree Classifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split # Import train_test_split function

# TODO
from sklearn import metrics #Import scikit-learn metrics module for accuracy calculation
from sklearn.metrics import precision_score, recall_score, precision_recall_curve,f1_score, fbeta_score, make_scorer, confusion_matrix, accuracy_score


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_file", "-i", help='Input file (csv)')
    parser.add_argument("--output_tree_complete", "-otc", help='Output file with all metrics and values (png)')
    parser.add_argument("--output_tree_simple", "-ots", help='Output file (png)')

    args = parser.parse_args()
    return args


def prepare_df_decision_tree_classifier(file):

    df = pd.read_csv(file, header=0, index_col=None)

    # create suffix to grab features with regex
    df['Compound_ID'] = 'CP_' + df['Accession'].astype(str)

    # Coumpound ID as index
    df.set_index('Compound_ID', inplace=True, drop=True)

    # drop unwanted columns
    df.drop(["Unnamed: 0", "Description", "BIOCHEMICAL", "padj", "pvalue", "score_overlap", "ratio_samples_control", "SUPER_PATHWAY", "Accession"],
            axis=1, inplace=True, errors='ignore')

    problematic_sample = ["VAL_Control_5", "VAL_Control_8",
                          "VAL_VIH_2", "VAL_VIH_3", "VAL_VIH_6", "VAL_VIH_10", "VAL_VIH_29"]
    df.drop(problematic_sample, axis=1, inplace=True)
    # drop NA

    df = df.dropna()

    # transpose to have df in right format for variables to explain
    tdf = df.transpose()

    # create new category for labels
    tdf["Patient"] = tdf.index.values
    tdf.reset_index(drop=True, inplace=True)

    for i in tdf.index.values:
        s = tdf.loc[i]["Patient"]
        replaced = re.sub('_[\d]{1,2}', '', s)
        replaced = re.sub('VAL_', '', replaced)
        replaced = re.sub('METABO_', '', replaced)
        replaced = re.sub('PROTEO_', '', replaced)

        tdf.loc[i, "label"] = replaced

    tdf.drop(["Patient"], axis=1, inplace=True)

    return tdf


def prepare_x_y_DecisionTreeClassifier(tdf, xcols='CP_', ycol='label'):

    X = tdf.filter(regex=xcols)
    feature_cols = X.columns.values
    y = tdf[ycol]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=43, stratify=y)  # 70% training and 30% test

    #sc = StandardScaler()
    #X_train = sc.fit_transform(X_train)
    #X_test = sc.transform(X_test)

    #tdf_scaled = pd.DataFrame(sc.transform(X), columns=X.columns, index=tdf[ycol])
    #tdf_scaled.to_csv('./data/InflammaVIH/clustering/tdf_scaled.csv')
    #print(pd.DataFrame(sc.transform(X), columns=X.columns, index=tdf[ycol]))

    return X_train, X_test, y_train, y_test, feature_cols



def compute_DecisionTreeClassifier(X_train, X_test, y_train, y_test):
    clf = DecisionTreeClassifier(class_weight='balanced',
                                 random_state=11,
                                 criterion='gini',
                                 splitter='random')

    # Train Decision Tree Classifer
    clf = clf.fit(X_train, y_train)

    # Predict the response for test dataset
    y_pred = clf.predict(X_test)

    # Model scores, how often is the classifier correct?
    # TODO : pos label ?
    accuracy = clf.score(X_test, y_test).round(2)
    precision = precision_score(y_test, y_pred, pos_label="Control").round(2)
    recall = recall_score(y_test, y_pred, pos_label="Control").round(2)
    f1 = f1_score(y_test, y_pred, pos_label="Control").round(2)

    print('Accuracy :', accuracy)
    print('Precision :', precision)
    print('Recall :', recall)
    print('F1_score :', f1)

    return clf


def compute_DecisionTreeClassifier_gridcv(X_train, X_test, y_train, y_test):
    #clf = DecisionTreeClassifier(class_weight='balanced',
    #                             random_state=2)
    clf = DecisionTreeClassifier(random_state=2)

    parameter_grid = {'criterion': ['gini', 'entropy'],
                      'splitter': ['best', 'random'],
                      'max_depth': [1, 2, 3, 4, 5],
                      'max_features': [1, 2, 3, 4, 5]}

    cross_validation = sklearn.model_selection.StratifiedKFold(n_splits=6)

    grid_search = sklearn.model_selection.GridSearchCV(clf, param_grid=parameter_grid, cv=cross_validation)

    grid_search.fit(X_train, y_train)
    print('Best score: {}'.format(grid_search.best_score_))
    print('Best parameters: {}'.format(grid_search.best_params_))

    dtc = grid_search.best_estimator_
    y_pred = dtc.predict(X_test)

    accuracy = dtc.score(X_test, y_test).round(2)
    precision = precision_score(y_test, y_pred, pos_label="Control").round(2)
    recall = recall_score(y_test, y_pred, pos_label="Control").round(2)
    f1 = f1_score(y_test, y_pred, pos_label="Control").round(2)

    print('Accuracy :', accuracy)
    print('Precision :', precision)
    print('Recall :', recall)
    print('F1_score :', f1)


    sklearn.tree.plot_tree(dtc, precision=0,
                           class_names=['Control', 'VIH'],
                           proportion=True)
    plt.show()
    return dtc


def compute_DecisionTreeClassifier_gridcv_overfitting(tdf, xcols='CP_', ycol='label'):
    X = tdf.filter(regex=xcols)
    feature_cols = X.columns.values
    print("feature cols : ", feature_cols)
    y = tdf[ycol]
    print(X.shape)
    print(y.shape)

    clf = DecisionTreeClassifier(class_weight='balanced',
                                 random_state=2)

    parameter_grid = {'criterion': ['gini', 'entropy'],
                      'splitter': ['best', 'random'],
                      'max_depth': [1, 2, 3, 4, 5],
                      'max_features': [1, 2, 3, 4, 5]}

    cross_validation = sklearn.model_selection.StratifiedKFold(n_splits=5)

    grid_search = sklearn.model_selection.GridSearchCV(clf, param_grid=parameter_grid, cv=cross_validation)

    grid_search.fit(X, y)
    print('Best score: {}'.format(grid_search.best_score_))
    print('Best parameters: {}'.format(grid_search.best_params_))

    dtc = grid_search.best_estimator_


    #sklearn.plot_tree(dtc, precision=0)
    #plt.show()
    return dtc, feature_cols


def plot_tree(clf, feature_cols, output_file):
    dot_data = StringIO()

    export_graphviz(clf, out_file=dot_data,
                    filled=True,
                    rounded=True,
                    impurity=False,
                    special_characters=True,
                    feature_names=feature_cols,
                    class_names=['Control', 'VIH'],
                    precision=2,
                    proportion=False,
                    label='all')

    graph = pydotplus.graph_from_dot_data(dot_data.getvalue())
    graph.write_png(output_file)
    Image(graph.create_png())
    return


def plot_simple_tree(clf, output_simple_tree):

    class_names = ['Control', 'VIH']
    dot_data = StringIO()

    export_graphviz(clf,
                    out_file=dot_data,
                    feature_names=feature_cols,
                    filled=True,
                    rounded=True,
                    impurity=False,
                    class_names=class_names,
                    precision=4)

    #PATH = '/home/clescoat/Documents/ProteomX/treett.dot'
    f = pydotplus.graph_from_dot_file(dot_data).to_string()

    print(f)

    # suppress samples / value in all nodes
    f = re.sub("samples = \d{1,2}", '', f)
    f = re.sub("value = \[[0-9]{0,2}\.?[0-9]{0,4}, [0-9]{0,2}\.?[0-9]{0,4}\]", '', f)
    f = re.sub("\\\\n", '', f)
    f = re.sub("\dclass", '\nclass', f)

    # suppress "class" in decision nodes
    f = re.sub("\d\nclass = [a-zA-Z]*", '', f)

    with open('tree_modifiedtt.dot', 'w') as file:
        file.write(f)

    (graph,) = pydot.graph_from_dot_file("tree_modifiedtt.dot")
    graph.write_png('tree_finaltt.png')



def plot_confusion_matrix(clf, X_test, y_test, output_cm):
    cm = sklearn.metrics.plot_confusion_matrix(clf, X_test, y_test)
    plt.savefig(output_cm)
    return cm


if __name__ == "__main__":
    args = get_args()

    tdf = prepare_df_decision_tree_classifier(args.input_file)

    X_train, X_test, y_train, y_test, feature_cols = prepare_x_y_DecisionTreeClassifier(tdf)

    # model
    #clf, feature_cols = compute_DecisionTreeClassifier_gridcv_overfitting(tdf)
    clf = compute_DecisionTreeClassifier_gridcv(X_train, X_test, y_train, y_test)

    # plots
    plot_tree(clf, feature_cols, args.output_tree_complete)

    plot_simple_tree(clf, args.output_tree_simple)

    plot_confusion_matrix(clf, X_test, y_test, args.output_cm)







