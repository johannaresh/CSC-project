import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.feature_selection import mutual_info_regression
from tickerdataframe import relative_info_train, relative_info_test

mi_traindf = relative_info_train.copy()
mi_Xtraining = mi_traindf[['SMA20', 'EMA20', 'RSI14', 'ATR14', 'OBV','Boll_%B20']]
mi_Ytraining = mi_traindf[['Adj Close']]

mi_testdf = relative_info_test.copy()
mi_Xtest = mi_testdf[['SMA20', 'EMA20', 'RSI14', 'ATR14', 'OBV','Boll_%B20']]
mi_Ytest = mi_testdf[['Adj Close']]

def make_mi_scores(X, y, discrete_features):
    mi_scores = mutual_info_regression(X, y, discrete_features=discrete_features)
    mi_scores = pd.Series(mi_scores, name="MI Scores", index=X.columns)
    mi_scores = mi_scores.sort_values(ascending=False)
    return mi_scores

mitraining_scores = make_mi_scores(mi_Xtraining, mi_Ytraining, discrete_features=False)
mitesting_scores = make_mi_scores(mi_Xtest, mi_Ytest, discrete_features=False)

def plot_mi_scores(scores):
    scores = scores.sort_values(ascending=True)
    width = np.arange(len(scores))
    ticks = list(scores.index)
    plt.figure(dpi=100, figsize=(8, 5))
    plt.barh(width, scores)
    plt.yticks(width, ticks)
    plt.title("Mutual Information Scores")
    return plt.show()

print(mitraining_scores)
print(mitesting_scores)

