from EstrazioneDatiUsable import *
from ModelloML import *


def ottieni_dati_citta(citta):
    if citta is None:
        print("Inserita citta non valida")

    id_citta = find_id_comune_by_name(citta)
    if not id_citta:
        print("Città non trovata")
        nuova_citta = None

    else:
        latitudine, longitudine = trova_coordinate(citta)
        print("Pericolosità")
        pericolosita = calc_pericolosita(citta)

        print("Costovita")
        regione = trova_regione_da_comune(citta)
        id_regione = find_id_regione_by_name(regione)

        costo_vitarealvalue = trova_valore_per_id(id_regione, Request_Type.SPESA_MEDIA.value)
        if costo_vitarealvalue == -1:
            costo_vit = 2
        else:
            if costo_vitarealvalue < 2100:
                costo_vit = 1
            elif costo_vitarealvalue > 2700:
                costo_vit = 3
            else:
                costo_vit = 2
        print("Abitanti - Superficie")
        abitanti = trova_valore_per_id(id_citta, Request_Type.POPOLAZIONE.value)
        superficie = trova_valore_per_id(id_citta, Request_Type.SUPERFICIE.value) / 100
        print("Negozi")
        num_negozi = stima_poi_totali(citta, Poi_Type.NEGOZIO.value, superficie)
        print("Ristoranti")
        num_ristoranti = stima_poi_totali(citta, Poi_Type.RISTORANTE.value, superficie)
        print("Scuole")
        num_scuole = stima_poi_totali(citta, Poi_Type.SCUOLA.value, superficie)
        print("Fine recupero dati")

        # Creare un DataFrame con i dati inseriti dall'utente
        nuova_citta = pd.DataFrame({
            'Latitudine': [latitudine],
            'Longitudine': [longitudine],
            'Pericolosità': [pericolosita],
            'Costo Vita': [costo_vit],
            'Abitanti': [abitanti],
            'Superficie': [superficie],
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

    citta_trovate = get_citta_bbox(get_bounding_box_custom(latitudine, longitudine, "overpass", raggio), raggio)
    print(citta_trovate)
    classifica = []
    fallite = []
    for citta in citta_trovate:
        result = ottieni_dati_citta(citta)
        print("Citta analizzata")

        # Verifica che i dati della città rispettino i criteri specificati
        if (not result.empty and result['Pericolosità'].iloc[0] <= max_pericolosita and
                result['Costo Vita'].iloc[0] <= costo_vita and
                min_abitanti <= result['Abitanti'].iloc[0] <= max_abitanti and
                result['Num Negozi'].iloc[0] >= min_negozi and
                result['Num Ristoranti'].iloc[0] >= min_ristoranti and
                result['Num Scuole'].iloc[0] >= min_scuole):

            result['IdQ'] = predict(result)
            result['Nome'] = citta
            classifica.append(result)
            print("Aggiunta")

        else:
            print("La città non soddisfa i criteri specificati.")
            fallite.append(result)

    df_val = None

    if not len(classifica) == 0:
        df_val = pd.concat(classifica, ignore_index=True)  # Concatena i DataFrame nella lista
        # df_val.to_csv('valutazione.csv', index=False)
    '''
    if not len(fallite) == 0:
        df_fail = pd.concat(fallite, ignore_index=True)
        df_fail.to_csv('fallimento.csv', index=False)
    '''
    if df_val is not None:
        final_result = df_val.sort_values(by='IdQ', ignore_index=True, ascending=False)
        final_result = final_result.head(5)
    else:
        final_result = "Nessun risultato è stato trovato!"
    return final_result
