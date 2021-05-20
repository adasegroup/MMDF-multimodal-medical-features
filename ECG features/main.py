import pandas as pd
from tqdm import tqdm
from load import load_data
from generate_features import *
from sqlite_db import * 

path = 'data\China 12-Lead ECG Challenge Database'
ecg_data, headers, lables = load_data(path)

features = []

for i in tqdm(range(len(headers))):
    ecg, header = ecg_data[i], headers[i]
    ecg_features = generate_features(ecg, header)
    age, sex = get_general_features(header)
    features.append([ecg_features, age, sex])

df = pd.DataFrame(features, columns=['ecg_features', 'age', 'sex'])
df.dropna(axis=0, inplace=True)
df.reset_index(drop=True, inplace=True)

column_names = []
for iline in header:
    if '.mat' in iline:
        name = iline.split(' 0 ')[2].strip()
        column_names.append(name)

df[column_names] = df.ecg_features.apply(pd.Series).iloc[:, :12]
df.drop('ecg_features', axis=1, inplace=True)

for name in column_names:
    expand_df = df[name].apply(pd.Series)
    expand_df = expand_df.drop(0, axis=1)
    df[name + "_" + expand_df.columns] = expand_df
    df.drop(name, axis=1, inplace=True)
    for subname in expand_df.columns:
        expand_subdf = df[name + "_" + subname].apply(pd.Series)
        expand_subdf = expand_subdf.drop(0, axis=1)
        df[name + "_" + subname + "_" + expand_subdf.columns] = expand_subdf
        df.drop(name + "_" + subname, axis=1, inplace=True)
        
save_to_sqldb(path= './data/', name = 'ecg_features', df = df)
df.to_csv('./data/ecg_features.csv', index=False)