from importlib import resources

import joblib
import pandas as pd



def predict(citta):
    # Estrai i valori dalla DataFrame
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
        'Pericolosità': [pericolosita],
        'Costo Vita': [costo_vita],
        'Abitanti per Km2': [abitanti_km2],
        'Num Negozi Km2': [num_negozi_km2],
        'Num Ristoranti Km2': [num_ristoranti_km2],
        'Num Scuole Km2': [num_scuole_km2]
    })

    # trained_model = joblib.load('Trained_Models/Bagging_Regression.pkl')

    # Leggi il file binario
    with resources.path("fyp_pkg.Trained_Models", "Bagging_Regression.pkl") as file_path:
        # Carica il modello utilizzando joblib
        trained_model = joblib.load(file_path)

    return round(float(trained_model.predict(nuova_citta_km2)), 2)
