import pandas as pd


def ricerca_simile(df_citta):
    # Importa il DataFrame con i dati delle città
    df = pd.DataFrame(pd.read_csv('File Dati/IdQ_Com_Final.csv'))

    # Calcola la distanza tra i dati inseriti dall'utente e quelli del DataFrame
    df['Distanza'] = ((df['Latitudine'] - df_citta['Latitudine'].values[0]) ** 2 +
                      (df['Longitudine'] - df_citta['Longitudine'].values[0]) ** 2 +
                      (df['Pericolosità'] - df_citta['Pericolosità'].values[0]) ** 2 +
                      (df['Costo Vita'] - df_citta['Costo Vita'].values[0]) ** 2 +
                      (df['Abitanti'] - df_citta['Abitanti'].values[0]) ** 2 +
                      (df['Abitanti per Km2'] - df_citta['Abitanti per Km2'].values[0]) ** 2 +
                      (df['Num Negozi Km2'] - df_citta['Num Negozi Km2'].values[0]) ** 2 +
                      (df['Num Ristoranti Km2'] - df_citta['Num Ristoranti Km2'].values[0]) ** 2 +
                      (df['Num Scuole Km2'] - df_citta['Num Scuole Km2'].values[0]) ** 2) ** 0.5

    # Ordina il DataFrame in base alla distanza
    df_sorted = df.sort_values(by=['Distanza'])

    # Restituisci le prime 5 città più simili
    result_df = df_sorted.head(5)

    return result_df

# Esegui la ricerca
risultato_ricerca = ricerca_citta()
print("Città simili:")
print(risultato_ricerca)
