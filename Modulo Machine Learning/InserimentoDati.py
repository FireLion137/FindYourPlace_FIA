from EstrazioneDatiUsable import *
from ModelloML import *


# Funzione per ottenere i dati della nuova città dall'utente
def ottieni_dati_citta():
    citta = (input("Inserisci il nome del comune che ti interessa: "))

    if not find_id_comune_by_name(citta):
        print("Città non trovata, riprova")
        ottieni_dati_citta()

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
    qualita_nuova_citta = model.predict(df_citta)
    print("Qualità stimata: ", qualita_nuova_citta)


def ottieni_dati_zona():
    # citta = (input("Inserisci il nome del comune che ti interessa: "))
    citta = "Padova"
    print("Coordinate riferimento: ", trova_coordinate(citta))
    if not find_id_comune_by_name(citta):
        print("Città non trovata, riprova")
        ottieni_dati_zona()

    lista_citta = get_citta_in_bbox(citta, "here", 10)
    print(lista_citta)

