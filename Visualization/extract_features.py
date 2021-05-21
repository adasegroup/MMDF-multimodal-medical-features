import pandas as pd
import numpy as np

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
