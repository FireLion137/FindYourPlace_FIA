import numpy as np
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor, VotingRegressor, BaggingRegressor, \
    StackingRegressor
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.model_selection import cross_val_score
from sklearn.linear_model import LinearRegression, Lasso, Ridge
from sklearn.metrics import mean_squared_error, root_mean_squared_error, mean_absolute_percentage_error
import pandas as pd
from sklearn.svm import SVR
from sklearn.tree import DecisionTreeRegressor
import joblib

# Importazione DataFrame
df = pd.DataFrame(pd.read_csv('File Dati/IdQ_Com_Final.csv'))

# Non posso usare string, converto ALTO, MEDIO, BASSO in valori numerici: 1, 2, 3
costoVita_mapping = {"BASSO": 1, "MEDIO": 2, "ALTO": 3}
df["Costo Vita"] = df["Costo Vita"].map(costoVita_mapping)

# Approssimo idQ a 2 numeri dopo la virgola
df['IdQ'] = round(df['IdQ'], 2)

# Faccio a monte i calcoli necessari con la superfice (valori per km2)
df['Num Negozi Km2'] = df['Num Negozi'] / df['Superficie']
df['Num Ristoranti Km2'] = df['Num Ristoranti'] / df['Superficie']
df['Num Scuole Km2'] = df['Num Scuole'] / df['Superficie']


# Separo feature e target
X = df[['Pericolosità', 'Costo Vita', 'Abitanti per Km2',
        'Num Negozi Km2', 'Num Ristoranti Km2', 'Num Scuole Km2']]  # Features
y = df['IdQ']  # Target

# Dividere il dataset in set di addestramento e test
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

models = {
    "Linear_Regression": LinearRegression(),
    "Lasso_Regression": Lasso(),
    "Ridge_Regression": Ridge(),
    "Gradient_Boosting_Regression": GradientBoostingRegressor(random_state=72),
    "Decision_Tree": DecisionTreeRegressor(),
    "Random_Forest": RandomForestRegressor(random_state=59),
    "Support_Vector_Machine": SVR()
}


# Addestramento e valutazione dei modelli
for name, model in models.items():
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    print(f"\n{name}: Mean Squared Error - {mse}")
    rmse = root_mean_squared_error(y_test, y_pred)
    print(f"{name}: Root Mean Squared Error - {rmse}")
    mape = mean_absolute_percentage_error(y_test, y_pred)
    print(f"{name}: Mean Absolute Percentage Error - {mape}")
    print('Accuracy:', round(100*(1 - mape), 2))

    scores = cross_val_score(model, X, y, cv=5, scoring='neg_mean_squared_error')
    mse_scores = -scores
    print(f"{name}: Mean Squared Error - Mean: {mse_scores.mean()}, Standard Deviation: {mse_scores.std()}")

    joblib.dump(model, f'Trained Models/{name}.pkl')

'''
for i in range (100):
    model = RandomForestRegressor(random_state=)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    print(f"RandomForestRegressor state= {i}: Mean Squared Error - {mse}")
'''


rf_model = RandomForestRegressor(random_state=59)
gb_model = GradientBoostingRegressor(random_state=72)

# Addestramento dei Modelli Singoli
rf_model.fit(X_train, y_train)
gb_model.fit(X_train, y_train)

# Creazione di Ensemble (Voting Regressor)
ensemble_model = VotingRegressor([('rf', rf_model), ('gb', gb_model)])
# Valutazione del Modello Ensemble
ensemble_model.fit(X_train, y_train)
y_pred = ensemble_model.predict(X_test)
mse = mean_squared_error(y_test, y_pred)
print("\n\nMean Squared Error (Voting):", mse)
rmse = root_mean_squared_error(y_test, y_pred)
print("Root Mean Squared Error (Voting):", rmse)
mape = mean_absolute_percentage_error(y_test, y_pred)
print("Mean Absolute Percentage Error (Voting):", mape)
print('Accuracy (Voting):', round(100*(1 - mape), 2))

scores = cross_val_score(ensemble_model, X, y, cv=5, scoring='neg_mean_squared_error')
mse_scores = -scores
print(f"Mean Squared Error (Voting) - Mean: {mse_scores.mean()}, Standard Deviation: {mse_scores.std()}")

# Creazione di Ensemble (Bagging)
bagging_model = BaggingRegressor(estimator=RandomForestRegressor(random_state=59), n_estimators=15, random_state=73)
# Valutazione del Modello Ensemble (Bagging)
bagging_model.fit(X_train, y_train)
y_pred_bagging = bagging_model.predict(X_test)
mse_bagging = mean_squared_error(y_test, y_pred_bagging)
print("\nMean Squared Error (Bagging):", mse_bagging)
rmse = root_mean_squared_error(y_test, y_pred_bagging)
print("Root Mean Squared Error (Bagging):", rmse)
mape = mean_absolute_percentage_error(y_test, y_pred_bagging)
print("Mean Absolute Percentage Error (Bagging):", mape)
print('Accuracy (Bagging):', round(100*(1 - mape), 2))

scores = cross_val_score(bagging_model, X, y, cv=5, scoring='neg_mean_squared_error')
mse_scores = -scores
print(f"Mean Squared Error (Bagging) - Mean: {mse_scores.mean()}, Standard Deviation: {mse_scores.std()}")

importance_scores = []
for estimator in bagging_model.estimators_:
    importance_scores.append(estimator.feature_importances_)
average_importance = np.mean(importance_scores, axis=0)
for feature, importance in zip(X_train.columns, average_importance):
    print(f"Feature: {feature}, Importance: {importance}")
joblib.dump(bagging_model, 'Trained Models/Bagging_Regression.pkl')


'''
for i in range (100):
    bagging_model = BaggingRegressor(estimator=RandomForestRegressor(random_state=59), n_estimators=20, random_state=i)
    # Valutazione del Modello Ensemble (Bagging)
    bagging_model.fit(X_train, y_train)
    y_pred_bagging = bagging_model.predict(X_test)
    mse_bagging = mean_squared_error(y_test, y_pred_bagging)
    print(f"BaggingRegressor state= {i}: Mean Squared Error - {mse_bagging}")
'''

# Creazione di Ensemble (Stacking)
estimators = [('rf', rf_model), ('gb', gb_model)]
stacking_model = StackingRegressor(estimators=estimators, final_estimator=LinearRegression())
# Valutazione del Modello Ensemble (Stacking)
stacking_model.fit(X_train, y_train)
y_pred_stacking = stacking_model.predict(X_test)
mse_stacking = mean_squared_error(y_test, y_pred_stacking)
print("\nMean Squared Error (Stacking):", mse_stacking)
rmse = root_mean_squared_error(y_test, y_pred_stacking)
print("Root Mean Squared Error (Stacking):", rmse)
mape = mean_absolute_percentage_error(y_test, y_pred_stacking)
print("Mean Absolute Percentage Error (Stacking):", mape)
print('Accuracy (Stacking):', round(100*(1 - mape), 2))

scores = cross_val_score(stacking_model, X, y, cv=5, scoring='neg_mean_squared_error')
mse_scores = -scores
print(f"Mean Squared Error (Stacking) - Mean: {mse_scores.mean()}, Standard Deviation: {mse_scores.std()}")

'''
for name, model in models.items():
    estimators = [('rf', rf_model), ('gb', gb_model)]
    stacking_model = StackingRegressor(estimators=estimators, final_estimator=model)
    stacking_model.fit(X_train, y_train)
    y_pred_stacking = stacking_model.predict(X_test)
    mse_stacking = mean_squared_error(y_test, y_pred_stacking)
    print(f"Mean Squared Error (Stacking) final_estimator= {name}:", mse_stacking)
'''

'''
# Tuning degli iperparametri per RandomForestRegressor
rf_param_grid = {
    'n_estimators': [100, 200, 300],
    'max_depth': [None, 5, 10],
    'min_samples_split': [2, 5, 10],
    'min_samples_leaf': [1, 2, 4]
}

rf_grid_search = GridSearchCV(RandomForestRegressor(random_state=59), rf_param_grid, scoring='neg_mean_squared_error')
rf_grid_search.fit(X_train, y_train)

rf_best_params = rf_grid_search.best_params_
print("\nMigliori iperparametri per RandomForestRegressor:", rf_best_params)

rf_best_model = RandomForestRegressor(random_state=59, **rf_best_params)
rf_best_model.fit(X_train, y_train)
y_pred_best_rf = rf_best_model.predict(X_test)
mse_best_rf = mean_squared_error(y_test, y_pred_best_rf)
print("Mean Squared Error (Best RF):", mse_best_rf)
scores = cross_val_score(rf_best_model, X, y, cv=5, scoring='neg_mean_squared_error')
mse_scores = -scores
print(f"Mean Squared Error (Best RF) - Mean: {mse_scores.mean()}, Standard Deviation: {mse_scores.std()}")

# Tuning degli iperparametri per BaggingRegressor
bagging_param_grid = {
    'n_estimators': [1, 10, 15, 20]
}

bagging_grid_search = GridSearchCV(BaggingRegressor(estimator=RandomForestRegressor(random_state=59), random_state=73), bagging_param_grid, scoring='neg_mean_squared_error')
bagging_grid_search.fit(X_train, y_train)

bagging_best_params = bagging_grid_search.best_params_
print("Migliori iperparametri per BaggingRegressor:", bagging_best_params)

bagging_best_model = BaggingRegressor(estimator=RandomForestRegressor(random_state=59), random_state=73, **bagging_best_params)
bagging_best_model.fit(X_train, y_train)
y_pred_best_bagging = bagging_best_model.predict(X_test)
mse_best_bagging = mean_squared_error(y_test, y_pred_best_bagging)
print("Mean Squared Error (Best Bagging):", mse_best_bagging)
scores = cross_val_score(bagging_best_model, X, y, cv=5, scoring='neg_mean_squared_error')
mse_scores = -scores
print(f"Mean Squared Error (Best Bagging) - Mean: {mse_scores.mean()}, Standard Deviation: {mse_scores.std()}")
'''