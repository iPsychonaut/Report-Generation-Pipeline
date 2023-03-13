# -*- coding: utf-8 -*-

from sklearn.linear_model import LinearRegression, Ridge, Lasso, ElasticNet, BayesianRidge
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.svm import SVR
from xgboost import XGBRegressor
from lightgbm import LGBMRegressor
from catboost import CatBoostRegressor

import pandas as pd

def feature_model_selection(ft_df):
    # Define a list of regression models to test
    models = [
        LinearRegression(),
        Ridge(),
        Lasso(),
        ElasticNet(),
        DecisionTreeRegressor(),
        RandomForestRegressor(),
        GradientBoostingRegressor(),
        KNeighborsRegressor(),
        SVR(kernel='linear'),
        SVR(kernel='poly'),
        SVR(kernel='rbf'),
        BayesianRidge(),
        XGBRegressor(),
        LGBMRegressor(),
        CatBoostRegressor(verbose=0)]
    
    # Define dictionaries to store the MSE and R-squared scores for each model
    mse_scores = {}
    r2_scores = {}
    
    # Apply one-hot encoding to the 'Sample_ID' column
    ft_df = pd.get_dummies(ft_df, columns=['Bin_ID','Flush_ID'])
    
    # Train and test each model, and store the scores in the dictionaries
    for model in models:
        model.fit(X_train, y_train)
        y_train_pred = model.predict(X_train)
        y_test_pred = model.predict(X_test)
        mse_scores[str(model)] = [mean_squared_error(y_train, y_train_pred), mean_squared_error(y_test, y_test_pred)]
        r2_scores[str(model)] = [r2_score(y_train, y_train_pred), r2_score(y_test, y_test_pred)]
    
    # Initialize lists to store the model names and scores
    models = []
    train_mse_scores = []
    test_mse_scores = []
    train_r2_scores = []
    test_r2_scores = []
    
    # Store the model names and scores in the lists
    for model, mse in mse_scores.items():
        models.append(model)
        train_mse_scores.append(mse[0])
        test_mse_scores.append(mse[1])
    
    for model, r2 in r2_scores.items():
        train_r2_scores.append(r2[0])
        test_r2_scores.append(r2[1])
    
    # Create the dataframe
    model_stats_df = pd.DataFrame({
        'Model': models,
        'Train MSE': train_mse_scores,
        'Test MSE': test_mse_scores,
        'Train R-squared': train_r2_scores,
        'Test R-squared': test_r2_scores
    })
    
    # Print the dataframe
    print(model_stats_df)
    
#feature_model_selection(ft_df)