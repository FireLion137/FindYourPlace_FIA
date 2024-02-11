from InserimentoDati import *

parametri_milano = [
    1,  # raggio in km
    45.4641943,  # latitudine
    9.1896346,  # longitudine
    3,  # costo di vita (scala ipotetica 1-3)
    100,  # pericolosità massima (scala ipotetica 1-3)
    100,  # min abitanti
    10000000,  # max abitanti
    5,  # min negozi
    10,  # min ristoranti
    5  # min scuole
]

parametri_napoli = [
    2,  # raggio in km
    40.8358846,  # latitudine
    14.2487679,  # longitudine
    3,  # costo di vita
    100,  # pericolosità massima
    100,  # min abitanti
    3000000,  # max abitanti
    20,  # min negozi
    15,  # min ristoranti
    10  # min scuole
]

parametri_bologna = [
    20,  # raggio in km
    44.4938203,  # latitudine
    11.3426327,  # longitudine
    3,  # costo di vita
    100,  # pericolosità massima
    100,  # min abitanti
    3000000,  # max abitanti
    20,  # min negozi
    15,  # min ristoranti
    10  # min scuole
]

parametri_alessandria = [
    2,  # raggio in km
    44.9130438,  # latitudine
    8.6154872,  # longitudine
    3,  # costo di vita
    100,  # pericolosità massima
    100,  # min abitanti
    3000000,  # max abitanti
    20,  # min negozi
    15,  # min ristoranti
    10  # min scuole
]

parametri_firenze = [
    2,  # raggio in km
    43.7698712,  # latitudine
    11.2555757,  # longitudine
    3,  # costo di vita
    100,  # pericolosità massima
    100,  # min abitanti
    3000000,  # max abitanti
    20,  # min negozi
    15,  # min ristoranti
    10  # min scuole
]

result = stampa_ricerca(parametri_bologna)
print(result)
