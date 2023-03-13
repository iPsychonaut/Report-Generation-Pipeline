# -*- coding: utf-8 -*-
"""
Created on Mon Mar 13 13:02:58 2023

@author: theda
"""
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from catboost import CatBoostRegressor
import pandas as pd

def cat_boost_regressor(ft_df):
    # CatBoostRegressor Training/Testing Process
    # Prepare data for training
    X = ft_df.drop('Fruit_PCB+PCN_mg', axis=1)
    y = ft_df['Fruit_PCB+PCN_mg']
    
    # Split the data into training and testing datasets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.5, random_state=42)
    
    # Train a CatBoostRegressor model
    model = CatBoostRegressor(verbose=0)
    model.fit(X, y)
    
    # Get the feature importance scores
    importances = model.feature_importances_
    
    # Get the column names of X_train
    features = X_train.columns
    
    # Create a pandas dataframe to store the feature importance scores
    df_importances = pd.DataFrame({'Analysis Feature': features, '▲-Contribution %': [round(importance, 2) for importance in importances]})
    df_importances = df_importances.sort_values(by='▲-Contribution %', ascending=False)
    
    # Print the top 10 features with the highest importance scores
    print(df_importances.head(10))
    return(df_importances)