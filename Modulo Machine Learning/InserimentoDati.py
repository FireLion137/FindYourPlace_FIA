import pandas as pd

from EstrazioneDatiUsable import *
from ModelloML import *


# Funzione per ottenere i dati della nuova città dall'utente
# si aspetta una lista con dentro i parametri
def input_parameters(parametri):
    # Estrai i valori dai parametri
    (raggio, latitudine, longitudine, costo_vita, max_pericolosita,
     min_abitanti, max_abitanti, min_negozi, min_ristoranti, min_scuole) = parametri

    # Conversione dei valori inseriti
    latitudine = float(latitudine)
    longitudine = float(longitudine)
    pericolosita = float(max_pericolosita)
    costo_vita = float(costo_vita)
    min_abitanti = int(min_abitanti)
    max_abitanti = int(max_abitanti)
    min_negozi = float(min_negozi)
    min_ristoranti = float(min_ristoranti)
    min_scuole = float(min_scuole)

    # Creazione di un DataFrame per rappresentare la città cercata con i nuovi criteri
    parametri_ricerca = pd.DataFrame({
        'Latitudine': [latitudine],
        'Longitudine': [longitudine],
        'Pericolosità': [pericolosita],
        'Costo Vita': [costo_vita],
        'Min Abitanti': [min_abitanti],
        'Max Abitanti': [max_abitanti],
        'Min Negozi': [min_negozi],
        'Min Ristoranti': [min_ristoranti],
        'Min Scuole': [min_scuole]
    })

    return parametri_ricerca


def ottieni_dati_citta(citta):
    if citta is None:
        print("Inserita citta non valida")

    id_citta = find_id_comune_by_name(citta)
    if not id:
        print("Città non trovata")
        nuova_citta = None

    else:
        latitudine, longitudine = trova_coordinate(citta)
        pericolosita = calc_pericolosita(citta)

        costo_vitarealvalue = trova_valore_per_id(id_citta, Request_Type.SPESA_MEDIA.value)
        if costo_vitarealvalue < 2100:
            costo_vit = 1
        elif costo_vitarealvalue > 2700:
            costo_vit = 3
        else:
            costo_vit = 2

        abitanti = trova_valore_per_id(id_citta, Request_Type.POPOLAZIONE.value)
        superfice = trova_valore_per_id(id_citta, Request_Type.SUPERFICIE.value)
        num_negozi = stima_poi_totali(citta, Poi_Type.NEGOZIO.value, superfice)
        num_ristoranti = stima_poi_totali(citta, Poi_Type.RISTORANTE.value, superfice)
        num_scuole = stima_poi_totali(citta, Poi_Type.SCUOLA.value, superfice)

        # Creare un DataFrame con i dati inseriti dall'utente
        nuova_citta = pd.DataFrame({
            'Latitudine': [latitudine],
            'Longitudine': [longitudine],
            'Pericolosità': [pericolosita],
            'Costo Vita': [costo_vit],
            'Abitanti': [abitanti],
            'Superficie': [superfice],
            'Num Negozi': [num_negozi],
            'Num Ristoranti': [num_ristoranti],
            'Num Scuole': [num_scuole]
        })

    return nuova_citta


def stampa_ricerca(parametri):
    # Estrai i valori dai parametri
    (raggio, latitudine, longitudine, costo_vita, max_pericolosita,
     min_abitanti, max_abitanti, min_negozi, min_ristoranti, min_scuole) = parametri

    print(parametri)

    if raggio <= 10:
        n = 10  # cerco minimo 10 citta

    else:
        n = round((raggio / 150) * 30)  # piu grande il raggio, piu citta cerco (150 mappato in 30)

    citta_trovate = get_citta_in_bbox(get_bounding_box_custom(latitudine, longitudine, "here", raggio), n)
    classifica = []
    fallite = []
    for citta in citta_trovate:
        result = ottieni_dati_citta(citta)

        # Verifica che i dati della città rispettino i criteri specificati
        if (not result.empty and result['Pericolosità'].iloc[0] <= max_pericolosita and
                min_abitanti <= result['Abitanti'].iloc[0] <= max_abitanti and
                result['Num Negozi'].iloc[0] >= min_negozi and
                result['Num Ristoranti'].iloc[0] >= min_ristoranti and
                result['Num Scuole'].iloc[0] >= min_scuole):

            result['IdQ'] = predict(result)
            classifica.append(result)

        else:
            print("La città non soddisfa i criteri specificati.")
            fallite.append(result)

    if classifica:
        df_val = pd.concat(classifica, ignore_index=True)  # Concatena i DataFrame nella lista
        df_val.to_csv('valutazione.csv', index=False)

    else:
        df_fail = pd.concat(fallite, ignore_index=True)
        df_fail.to_csv('fallimento.csv', index=False)
        print("Nessuna citta trovata in base ai requisiti")
