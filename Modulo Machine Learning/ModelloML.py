# Importare le librerie necessarie
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
import pandas as pd

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
X = df[['Latitudine', 'Longitudine', 'Pericolosità', 'Costo Vita', 'Abitanti',
        'Num Negozi Km2', 'Num Ristoranti Km2', 'Num Scuole Km2']]  # Features
y = df['IdQ']  # Target

# Dividere il dataset in set di addestramento e test
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Creare un modello di regressione lineare
model = LinearRegression()

# Addestrare il modello
model.fit(X_train, y_train)

# Effettuare previsioni sul set di test
y_pred = model.predict(X_test)

mse = mean_squared_error(y_test, y_pred)
print(mse)


def predict(citta):
    # Estrai i valori dalla DataFrame
    latitudine = citta['Latitudine'].iloc[0]
    longitudine = citta['Longitudine'].iloc[0]
    pericolosita = citta['Pericolosità'].iloc[0]
    costo_vita = citta['Costo Vita'].iloc[0]
    abitanti = citta['Abitanti'].iloc[0]
    superficie = citta['Superficie'].iloc[0]
    num_negozi = citta['Num Negozi'].iloc[0]
    num_ristoranti = citta['Num Ristoranti'].iloc[0]
    num_scuole = citta['Num Scuole'].iloc[0]

    # Calcola i valori per km2
    abitanti_km2 = abitanti / superficie
    num_negozi_km2 = num_negozi / superficie
    num_ristoranti_km2 = num_ristoranti / superficie
    num_scuole_km2 = num_scuole / superficie

    # Crea un nuovo DataFrame con i valori per km2
    nuova_citta_km2 = pd.DataFrame({
        'Latitudine': [latitudine],
        'Longitudine': [longitudine],
        'Pericolosità': [pericolosita],
        'Costo Vita': [costo_vita],
        'Abitanti': [abitanti],
        'Num Negozi Km2': [num_negozi_km2],
        'Num Ristoranti Km2': [num_ristoranti_km2],
        'Num Scuole Km2': [num_scuole_km2]
    })

    return round(float(model.predict(nuova_citta_km2)), 2)
