from InserimentoDati import *

# Parametri per Sorrento
parametri_sorrento = [
    10,  # raggio in km
    40.6263,  # latitudine
    14.3757,  # longitudine
    2,  # costo di vita (scala ipotetica 1-3)
    10000,  # pericolosità massima (scala ipotetica 1-3)
    100,  # min abitanti
    50000,  # max abitanti
    5,  # min negozi
    10,  # min ristoranti
    5  # min scuole
]

# Parametri per Piacenza
parametri_piacenza = [
    65,  # raggio in km
    45.0526,  # latitudine
    9.6922,  # longitudine
    3,  # costo di vita
    2000,  # pericolosità massima
    100,  # min abitanti
    120000,  # max abitanti
    20,  # min negozi
    15,  # min ristoranti
    10  # min scuole
]

# Parametri per Castellammare di Stabia
parametri_castellammare_di_stabia = [
    5,  # raggio in km
    40.7155,  # latitudine
    14.4891,  # longitudine
    2,  # costo di vita
    2,  # pericolosità massima
    30000,  # min abitanti
    70000,  # max abitanti
    10,  # min negozi
    5,  # min ristoranti
    8  # min scuole
]

print(stampa_ricerca(parametri_sorrento))
