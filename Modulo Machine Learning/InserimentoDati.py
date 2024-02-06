import pandas as pd

from EstrazioneDatiUsable import *


# Funzione per ottenere i dati della nuova città dall'utente
def ricerca_citta():
    # Range del bbox da creare (rettangolare)
    dim = float(input("Inserisci il range della ricerca: "))
    # Numero di citta inserite nell'algoritmo di ricerca
    n = int(input("Inserisci il numero di alternative che vuoi considerare: "))

    # Chiedi all'utente di inserire i valori dei parametri o lasciare vuoti
    latitudine = input("Inserisci la latitudine (Premi Invio per saltare): ")
    longitudine = input("Inserisci la longitudine (Premi Invio per saltare): ")

    # Nome del comune cercato
    stato = True
    citta = None
    while stato:
        citta = (input("Inserisci il nome del comune che ti interessa: "))

        if not find_id_comune_by_name(citta):
            print("Città non trovata, riprova")

        else:
            stato = False

    if citta is not None:
        latitudine, longitudine = trova_coordinate(citta)

    pericolosita = input("Inserisci la pericolosità (Premi Invio per saltare): ")
    costo_vita = input("Inserisci il costo della vita (Premi Invio per saltare): ")
    abitanti = input("Inserisci il numero di abitanti (Premi Invio per saltare): ")
    abitanti_per_km2 = input("Inserisci il numero di abitanti per km2 (Premi Invio per saltare): ")
    num_negozi_km2 = input("Inserisci il numero di negozi per km2 (Premi Invio per saltare): ")
    num_ristoranti_km2 = input("Inserisci il numero di ristoranti per km2 (Premi Invio per saltare): ")
    num_scuole_km2 = input("Inserisci il numero di scuole per km2 (Premi Invio per saltare): ")

    # Converte i valori inseriti in float o li lascia vuoti se l'utente ha premuto Invio
    latitudine = float(latitudine) if latitudine else 0
    longitudine = float(longitudine) if longitudine else 0
    pericolosita = float(pericolosita) if pericolosita else 0
    costo_vita = float(costo_vita) if costo_vita else 0
    abitanti = int(abitanti) if abitanti else 0
    abitanti_per_km2 = float(abitanti_per_km2) if abitanti_per_km2 else 0
    num_negozi_km2 = float(num_negozi_km2) if num_negozi_km2 else 0
    num_ristoranti_km2 = float(num_ristoranti_km2) if num_ristoranti_km2 else 0
    num_scuole_km2 = float(num_scuole_km2) if num_scuole_km2 else 0

    # Creare un DataFrame con i valori inseriti dall'utente
    nuova_citta = pd.DataFrame({
        'Nome': [citta],
        'Latitudine': [latitudine],
        'Longitudine': [longitudine],
        'Pericolosità': [pericolosita],
        'Costo Vita': [costo_vita],
        'Abitanti': [abitanti],
        'Abitanti per Km2': [abitanti_per_km2],
        'Num Negozi Km2': [num_negozi_km2],
        'Num Ristoranti Km2': [num_ristoranti_km2],
        'Num Scuole Km2': [num_scuole_km2]
    })

    citta_trovate = get_citta_in_bbox(get_bounding_box_custom(latitudine, longitudine, "here", dim), n)
    return citta_trovate, nuova_citta


def ottieni_dati_citta(citta):
    if citta is None:
        print("Inserita citta non valida")

    id_citta = find_id_comune_by_name(citta)
    if not id:
        print("Città non trovata")
        nuova_citta = None

    else:
        latitudine, longitudine = trova_coordinate(citta)
        print("Passo 1")
        pericolosita = calc_pericolosita(citta)
        print("Passo 2")
        costo_vit = calc_spesa_media(trova_regione_da_comune(citta))
        print("Passo 3")
        abitanti = trova_popolazione(id_citta)
        print("Passo 4")
        superfice = trova_sup(id_citta)
        print("Passo 5")
        abitanti_per_km2 = abitanti / superfice
        print("Passo 6")
        num_negozi_km2 = trova_numero_poi_herev7(citta, Poi_Type.NEGOZIO.value) / superfice
        print("Passo 7")
        num_ristoranti_km2 = trova_numero_poi_herev7(citta, Poi_Type.RISTORANTE.value) / superfice
        print("Passo 8")
        num_scuole_km2 = trova_numero_poi_herev7(citta, Poi_Type.SCUOLA.value) / superfice
        print("Passo 9")
        # Creare un DataFrame con i dati inseriti dall'utente
        nuova_citta = pd.DataFrame({
            'Latitudine': [latitudine],
            'Longitudine': [longitudine],
            'Pericolosità': [pericolosita],
            'Costo Vita': [costo_vit],
            'Abitanti': [abitanti],
            'Abitanti per Km2': [abitanti_per_km2],
            'Num Negozi Km2': [num_negozi_km2],
            'Num Ristoranti Km2': [num_ristoranti_km2],
            'Num Scuole Km2': [num_scuole_km2]
        })

    return nuova_citta


def ricerca_simile(df_val, df_citta):

    # Calcola la distanza tra i dati della città e quelli del DataFrame di input
    df_val['Distanza'] = np.sqrt(
        (df_val['Latitudine'] - df_citta['Latitudine'].values[0]) ** 2 +
        (df_val['Longitudine'] - df_citta['Longitudine'].values[0]) ** 2 +
        (df_val['Pericolosità'] - df_citta['Pericolosità'].values[0]) ** 2 +
        (df_val['Costo Vita'] - df_citta['Costo Vita'].values[0]) ** 2 +
        (df_val['Abitanti'] - df_citta['Abitanti'].values[0]) ** 2 +
        (df_val['Abitanti per Km2'] - df_citta['Abitanti per Km2'].values[0]) ** 2 +
        (df_val['Num Negozi Km2'] - df_citta['Num Negozi Km2'].values[0]) ** 2 +
        (df_val['Num Ristoranti Km2'] - df_citta['Num Ristoranti Km2'].values[0]) ** 2 +
        (df_val['Num Scuole Km2'] - df_citta['Num Scuole Km2'].values[0]) ** 2
    )

    # Ordina il DataFrame in base alla distanza
    df_sorted = df_val.sort_values(by=['Distanza'])

    # Restituisci le prime 5 città più simili
    result_df = df_sorted.head(5)

    return result_df


def interface():
    citta_trovate, df_target = ricerca_citta()
    valutazione = []

    for citta in citta_trovate:
        dati_citta = ottieni_dati_citta(citta)
        if dati_citta is not None:
            valutazione.append(dati_citta)

    df_val = pd.concat(valutazione, ignore_index=True)  # Concatena i DataFrame nella lista

    df_val.to_csv('valutazione.csv', index=False)
    df_target.to_csv('target.csv', index=False)

    df_candidates = ricerca_simile(df_val, df_target)
    print(df_candidates)


interface()
