import pandas as pd

from EstrazioneDatiUsable import *


# Funzione per ottenere i dati della nuova città dall'utente
def ricerca_citta():
    ricerca = []
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
    latitudine = float(latitudine) if latitudine else None
    longitudine = float(longitudine) if longitudine else None
    pericolosita = float(pericolosita) if pericolosita else None
    costo_vita = float(costo_vita) if costo_vita else None
    abitanti = int(abitanti) if abitanti else None
    abitanti_per_km2 = float(abitanti_per_km2) if abitanti_per_km2 else None
    num_negozi_km2 = float(num_negozi_km2) if num_negozi_km2 else None
    num_ristoranti_km2 = float(num_ristoranti_km2) if num_ristoranti_km2 else None
    num_scuole_km2 = float(num_scuole_km2) if num_scuole_km2 else None

    # Creare un DataFrame con i valori inseriti dall'utente
    nuova_citta = pd.DataFrame({
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
        citta = (input("Inserisci il nome del comune che ti interessa: "))

    if not find_id_comune_by_name(citta):
        print("Città non trovata, riprova")
        ottieni_dati_citta(None)

    latitudine, longitudine = trova_coordinate(citta)
    pericolosita = calc_pericolosita(citta)
    costo_vit = calc_spesa_media(trova_regione_da_comune(citta))
    abitanti = trova_popolazione(citta)
    superfice = trova_sup(citta)
    abitanti_per_km2 = abitanti / superfice
    num_negozi_km2 = trova_numero_poi_herev7(citta, Poi_Type.NEGOZIO.value) / superfice
    num_ristoranti_km2 = trova_numero_poi_herev7(citta, Poi_Type.RISTORANTE.value) / superfice
    num_scuole_km2 = trova_numero_poi_herev7(citta, Poi_Type.SCUOLA.value) / superfice

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

    df_citta = pd.DataFrame(nuova_citta)

    return df_citta


def interface():
    citta_trovate, df_citta = ricerca_citta()
    valutazione = []

    for citta in citta_trovate:
        valutazione.append(ottieni_dati_citta(citta))

    pd.DataFrame(valutazione)
    print(valutazione)

interface()


