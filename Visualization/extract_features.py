import pandas as pd
import numpy as np

from numpy import loadtxt
from xgboost import XGBClassifier
from matplotlib import pyplot

import matplotlib.pyplot as plt

def get_feature(feature_name, df):
    pos = df[feature_name][df['fibrillation'] == 0].dropna()
    neg = table[feature_name][df['fibrillation'] == 1].dropna()
    return pos, neg

def get_feature_heart(feature_name, df):
    pos = df[feature_name][df['heart_failure'] == 0].dropna()
    neg = df[feature_name][df['heart_failure'] == 1].dropna()
    return pos, neg

def get_feature_sin_rhytm(df):
    df["sn"] = df[["sinus_rhythm", "Sin"]].max(axis=1)
    pos = df[df['fibrillation'] == 0]
    neg = df[df['fibrillation'] == 1]
    return pos['sn'], neg['sn']

from sklearn.decomposition import PCA
from sklearn.manifold import TSNE

def make_2D_objects(df, list_of_features, model_type = 'TSNE'):
    ekg_table = df[list_of_features]
    tf = ekg_table.fillna(0.0)
    groups = tf.groupby(['combined_id']).mean()
    pos_ned = groups['fibrillation'].values
    posneg = [str(elem) for elem in pos_ned]
    tf = ekg_table.fillna(0.0)
    groups = tf.groupby(['combined_id']).mean()
    
    if (model_type == 'TSNE'):
        pca = TSNE(n_components=2)
    elif (model_type == 'PCA'):
        pca = PCA(n_components=2)
    else:
        print ("Please choose TSNE or PCA model type")
        exit();
    
    word_vectors_pca = pca.fit_transform(groups)

    word_vectors_pca = (word_vectors_pca - word_vectors_pca.mean(axis=0)) / word_vectors_pca.std(axis=0)
    
    return word_vectors_pca, posneg


def feature_importance_by_xgb(table, feature_list, size_x = 30, size_y = 6):
    labels = table['fibrillation']
    labels = [1 if label == True else 0 for label in labels]
    
    table_df = table[feature_list]
    table_df = table_df.fillna(0.0)
    if ('sex' in table_df.columns):
        table_df['sex'] = [0 if elem == 'M' else 1 for elem in table_df['sex'].values]
    
    X = table_df.values
    y = labels
    # fit model no training data
    model = XGBClassifier()
    model.fit(table_df, y)
    
    loc = range(len(feature_list))
    labels = feature_list
    
    pyplot.bar(range(len(model.feature_importances_)), model.feature_importances_)
    pyplot.rcParams["figure.figsize"] = (size_x, size_y) 
    pyplot.xticks(loc, labels, rotation=40, fontsize=11)
    pyplot.show()
    
def find_outliers(table, feature):
    features = table[feature]
    
    labels = table['fibrillation']

    mean = np.mean(features.dropna().values)
    std = np.std(features.dropna().values)
    
    list_of_outliers = []
    list_of_labels = []
    list_of_positive = []
    list_of_negative = []
    for (ind, elem) in enumerate(features):
        if (abs(elem - mean) > 3*std):
            list_of_outliers.append(elem)
            list_of_labels.append(labels[ind])
            if (labels[ind] == True):
                list_of_positive.append(elem)
            elif (labels[ind] == False):
                list_of_negative.append(elem)
        
    print ("Mean: ", mean, "Std: ", std, " number_of_objects: ", len(table), " number_of_outliers: ", len(list_of_outliers))


    fig, (ax1, ax2) = plt.subplots(1, 2)
    fig.suptitle('Data vs. outliers')
    ax2.hist(list_of_outliers, bins = 50, alpha=0.7, label='Outliers')
    ax1.hist(features.dropna().values, bins =50, alpha=0.7, label='Common data')
    plt.legend()
    plt.show()
    
    return list_of_outliers, list_of_labels, list_of_positive, list_of_negative