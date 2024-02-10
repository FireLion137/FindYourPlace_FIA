# Importare le librerie necessarie
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
import pandas as pd


# Importazione DataFrame
data = pd.read_csv('File Dati/IdQ_Com_Final.csv')

df = pd.DataFrame(data)

# Non posso usare string, converto ALTO, MEDIO, BASSO in valori numerici: 1, 2, 3
costoVita_mapping = {"BASSO": 1, "MEDIO": 2, "ALTO": 3}
df["Costo Vita"] = df["Costo Vita"].map(costoVita_mapping   )

# Approssimo idQ a 2 numeri dopo la virgola
df['IdQ'] = round(df['IdQ'], 2)

# Separo feature e target
X = df[['Latitudine', 'Longitudine', 'Pericolosità', 'Costo Vita', 'Abitanti', 'Superficie', 'Abitanti per Km2', 'Num Negozi', 'Num Ristoranti', 'Num Scuole']]  # Features
y = df['IdQ']  # Target

# Dividere il dataset in set di addestramento e test
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Creare un modello di regressione lineare
model = LinearRegression()

# Addestrare il modello
model.fit(X_train, y_train)

# Effettuare previsioni sul set di test
y_pred = model.predict(X_test)

# Iterare attraverso i dati di test e stampare i valori previsti e reali
for i in range(len(y_test)):
    print(f"Previsto: {y_pred[i]}, Reale: {y_test.iloc[i]}")

# Valutare le prestazioni del modello
mse = mean_squared_error(y_test, y_pred)
print(f'Errore quadratico medio (MSE): {mse}')

# Ora puoi utilizzare il modello addestrato per stimare la qualità della vita di un comune
# fornendo i dati delle regioni e capoluoghi corrispondenti.
