# Definizione di tutti i metodi usati.

import json
import re
import requests
from enum import Enum

from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from geopy.exc import GeocoderTimedOut, GeocoderQuotaExceeded

from sklearn.neighbors import BallTree
import numpy as np
import pandas as pd
import overpass

from Disegna_box import *

with open('File Dati/CL_ITTER107.json', 'r') as _file:
    data = json.load(_file)

# Estrai la lista di codici dal file JSON
codes = data['data']['codelists'][0]['codes']

# Associazioni per nomi non corrispondenti
associazioni_comune = {
    "Bolzano": "Bolzano/Bozen",
    "Bolzano / Bozen": "Bolzano/Bozen",
    "Bolzano - Bozen": "Bolzano/Bozen",
    "Forli": "Forlì"
}


# Funzione per trovare l'id in base al nome del comune
def find_id_comune_by_name(name):
    result = []
    for code in codes:
        if code['name']['it'] == name and re.match("^\\d{6}$", code['id']):
            result.append(code['id'])

    if len(result) == 0 and name in associazioni_comune:
        name = associazioni_comune[name]
        for code in codes:
            if code['name']['it'] == name and re.match("^\\d{6}$", code['id']):
                result.append(code['id'])

    # print(name, result)
    if len(result) == 0:
        return None
    elif len(result) == 1:
        return result[0]
    return result


# Associazioni per nomi non corrispondenti
associazioni_regione_province = {
    "Provincia di Trento": "Trento",
    "Trentino-Alto Adige": "Trentino Alto Adige / Südtirol",
    "Bolzano": "Bolzano / Bozen",
    "Reggio Calabria": "Reggio di Calabria",
    "Provincia di Imperia": "Imperia"
}


# Funzione per trovare l'id in base al nome della regione o provincia
def find_id_regione_by_name(name):
    for code in codes:
        if code['name']['it'] == name and re.match("^IT.*$", code['id']):
            return code['id']

    if name in associazioni_regione_province:
        name = associazioni_regione_province[name]
        for code in codes:
            if code['name']['it'] == name and re.match("^IT.*$", code['id']):
                return code['id']
    else:
        return None
    return None


geolocator = Nominatim(user_agent="FindYourPlace")
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1, max_retries=5)
reverse = RateLimiter(geolocator.reverse, min_delay_seconds=1, max_retries=5)


# Funzione per ottenere location da un comune
def trova_location(comune):
    location = None
    try:
        structuredQuery = {
            "postalcode": '',
            "state": '',
            "country": 'Italia',
            "street": '',
            "city": {comune}
        }

        location = geocode(structuredQuery)
        if location is None:
            location = geocode(comune)
    except (GeocoderTimedOut, GeocoderQuotaExceeded, TimeoutError) as e:
        if TimeoutError or GeocoderQuotaExceeded:
            print(e)

    if location is None:
        print(f'Location for {comune} not found')
    return location


# Funzione per ottenere le coordinate di un comune
def trova_coordinate(comune):
    loc = trova_location(comune)

    if loc:
        latitudine, longitudine = loc.latitude, loc.longitude
        return latitudine, longitudine
    else:
        return None


# Funzione per ottenere il bounding box di un comune
def get_bounding_box(comune, bbox_type):
    valid = {"here", "overpass"}
    if bbox_type not in valid:
        raise ValueError("results: type must be one of %r." % valid)

    loc = trova_location(comune)

    if loc:
        bbox = loc.raw.get('boundingbox', None)
        if bbox:
            # Converti i valori del bounding box in float
            bounding_box = [float(coord) for coord in bbox]

            if bbox_type == "here":
                return bounding_box[2], bounding_box[0], bounding_box[3], bounding_box[1]

            elif bbox_type == "overpass":
                return bounding_box[0], bounding_box[2], bounding_box[1], bounding_box[3]

    return None


def get_bounding_box_custom(lat, lon, bbox_type, bbox_range_km):
    bbox_range = bbox_range_km / 111  # conversione da km a gradi, conversione aprossimativa, imprecisa verso i poli

    valid = {"here", "overpass"}
    if bbox_type not in valid:
        raise ValueError("bbox_type must be one of %r." % valid)

    if bbox_range <= 0:
        raise ValueError("bbox_range must be a positive value.")

    half_range = bbox_range / 2

    max_lat = lat + half_range
    min_lat = lat - half_range
    max_lon = lon + half_range
    min_lon = lon - half_range

    if bbox_type == "here":
        return min_lon, min_lat, max_lon, max_lat

    elif bbox_type == "overpass":
        return min_lat, min_lon, max_lat, max_lon

    else:
        return None


def get_citta_bbox(bbox, raggio):
    # draw_bbox_on_map(bbox) # Crea mappa per visualizzare bbox

    if raggio <= 10:
        target = 5  # cerco minimo 10 citta

    else:
        target = max(round((raggio / 5)), 5)  # piu grande il raggio, piu citta cerco (150 mappato in 30)

    min_lat, min_lon, max_lat, max_lon = bbox

    api = overpass.API()
    query = f"node['place' = 'city']({min_lat},{min_lon},{max_lat},{max_lon});"
    response = api.get(query)
    citta_trovate = []

    # Estrai le informazioni desiderate, cerco prima citta,
    # poi paesi, poi villaggi, poi suburb finche non raggiungo target
    if response["features"]:
        for feature in response["features"]:
            nome_citta = feature["properties"]["name"]
            citta_trovate.append(nome_citta)

    if len(citta_trovate) < target:
        query = f"node['place' = 'town']({min_lat},{min_lon},{max_lat},{max_lon});"
        response = api.get(query)

        if response["features"]:
            for feature in response["features"]:
                nome_citta = feature["properties"]["name"]
                citta_trovate.append(nome_citta)

    if len(citta_trovate) < target:
        query = f"node['place' = 'village']({min_lat},{min_lon},{max_lat},{max_lon});"
        response = api.get(query)

        if response["features"]:
            for feature in response["features"]:
                nome_citta = feature["properties"]["name"]
                citta_trovate.append(nome_citta)

    if not citta_trovate:
        print("Nessuna citta trovata")
        return

    return citta_trovate[:target]  # tronco la lista per non eccedere target nel caso dovesse essere troppo lunga


# Funzione per ottenere le coordinate più vicine in un dataframe
def trova_coordinate_vicine(latitudine, longitudine, dataframe):
    bt = BallTree(np.deg2rad(dataframe[['LAT', 'LON']].values), metric='haversine')
    distanze, indici = bt.query(np.deg2rad(np.c_[latitudine, longitudine]))

    nearest = dataframe.iloc[indici[0]]

    return nearest[['LAT', 'LON', 'Zona Sismica']]


# Funzione per ottenere la regione dal comune
def trova_regione_da_comune(comune):
    location = trova_location(comune)

    if location:
        position = reverse((location.latitude, location.longitude), language='it')
        regione = position.raw['address']['state']
        return regione
    else:
        return None


# Funzione per ottenere la regione dal comune
def trova_provincia_da_comune(comune):
    location = trova_location(comune)

    if location:
        position = reverse((location.latitude, location.longitude), language='it')
        try:
            regione = position.raw['address']['county']
        except:
            regione = position.raw['address']['province']
        return regione
    else:
        return None


# Lettura dati scaricati istat
class Request_Type(Enum):
    INQUINAMENTO = "inq"
    CRIMINALITA = "crim"
    DENUNCE = "den"
    SUPERFICIE = "sup"
    IDROGEOLOGICO = "idro"
    POPOLAZIONE = "pop"
    SPESA_MEDIA = "spesa"


# Funzione per trovare valore in locale invece che tramite api istat
def trova_valore_per_id(id_istat, request_type):
    valid = {"inq", "crim", "den", "sup", "idro", "pop", "spesa"}
    if request_type not in valid:
        raise ValueError("Errore: request_type must be one of %r." % valid)

    if request_type == "inq":
        with open('istatData/inquinamentoRegioni.json', 'r') as file:
            jsonFile = json.load(file)
    elif request_type == "crim":
        with open('istatData/criminalitaRegioni.json', 'r') as file:
            jsonFile = json.load(file)
    elif request_type == "den":
        with open('istatData/denunceProvince.json', 'r') as file:
            jsonFile = json.load(file)
    elif request_type == "sup":
        with open('istatData/superficieComuni.json', 'r') as file:
            jsonFile = json.load(file)
    elif request_type == "idro":
        with open('istatData/rischioIdrogeologicoComuni.json', 'r') as file:
            jsonFile = json.load(file)
    elif request_type == "pop":
        with open('istatData/popolazione.json', 'r') as file:
            jsonFile = json.load(file)
    elif request_type == "spesa":
        with open('istatData/spesaMediaRegioni.json', 'r') as file:
            jsonFile = json.load(file)

    result = []
    for series in jsonFile['message:GenericData']['message:DataSet']['generic:Series']:
        series_key = series['generic:SeriesKey']['generic:Value']

        if type(id_istat) is not list:
            ref_area_dict = next(
                (i for i in series_key if i['@id'] in ['REF_AREA', 'ITTER107'] and i['@value'] == id_istat),
                None)

            if ref_area_dict:
                try:
                    result.append(float(series['generic:Obs']['generic:ObsValue']['@value']))
                except KeyError:
                    result.append(-1)
        else:
            for id_x in id_istat:
                ref_area_dict = next(
                    (i for i in series_key if i['@id'] in ['REF_AREA', 'ITTER107'] and i['@value'] == id_x), None)

                if ref_area_dict:
                    try:
                        result.append(float(series['generic:Obs']['generic:ObsValue']['@value']))
                    except KeyError:
                        result.append(-1)
                    continue

    # print(id, result)
    if len(result) == 0:
        return -1
    elif len(result) == 1:
        return result[0]
    return result


min_denunce_per_ab = 1700
max_denunce_per_ab = 7000
zone_sismiche = pd.read_csv('File Dati/Zone Sismiche.csv')


def calc_pericolosita(comune):
    id_comune = find_id_comune_by_name(comune)
    # print(f'ID Comune {comune} ISTAT: {id_comune}')

    provincia = trova_provincia_da_comune(comune)
    id_provincia = find_id_regione_by_name(provincia)
    # print(f'ID Provincia {provincia} ISTAT: {id_provincia}')

    regione = trova_regione_da_comune(comune)
    id_regione = find_id_regione_by_name(regione)
    # print(f'ID Regione {regione} ISTAT: {id_regione}')

    coordinate = trova_coordinate(comune)
    # print(f'Coordinate Comune: {coordinate}\n')

    # Inquinamento Regione
    inquinamento = trova_valore_per_id(id_regione, Request_Type.INQUINAMENTO.value)
    # print(f'Inquinamento {regione} con id {id_regione}: {inquinamento}')

    # Criminalità Regione
    criminalita = trova_valore_per_id(id_regione, Request_Type.CRIMINALITA.value)
    # print(f'Criminalità {regione} con id {id_regione}: {criminalità}')

    # Denunce per 100000 Abitanti Provincia
    popolazione = int(trova_valore_per_id(id_provincia, Request_Type.POPOLAZIONE.value))
    denunce = int(trova_valore_per_id(id_provincia, Request_Type.DENUNCE.value))
    if denunce != -1:
        denunce_per_ab = denunce / popolazione * 100000
    else:
        denunce_per_ab = min_denunce_per_ab
    # print(f'Denunce ogni 100.000 abitanti in {provincia} con id {id_provincia}: {denunce_per_ab}')

    # Rischio idrogeologico Comune
    if id_comune is not None:
        idrogeologicoValues = trova_valore_per_id(id_comune, Request_Type.IDROGEOLOGICO.value)
    else:
        idrogeologicoValues = trova_valore_per_id(id_regione, Request_Type.IDROGEOLOGICO.value)

    if idrogeologicoValues != -1:
        # L'ordine è HIGH - LOW - MED, in Low è incluso Med, in cui a sua volta è incluso High
        idrogeologicoLow = idrogeologicoValues[1] - idrogeologicoValues[2]  # Rimuovo il Med (in cui vi è anche l'high)
        idrogeologicoMed = idrogeologicoValues[2] - idrogeologicoValues[0]  # Rimuovo l' High
        idrogeologicoHigh = idrogeologicoValues[0]
        # Trovo superficie comune e calcolo il rischio ponderato
        superficie = trova_valore_per_id(id_comune, Request_Type.SUPERFICIE.value) / 100
        rischio_ponderato = idrogeologicoLow * 0.5 + idrogeologicoMed * 1 + idrogeologicoHigh * 1.5
        rischio_idro_perc = rischio_ponderato / max(superficie, rischio_ponderato) * 100
    else:
        rischio_idro_perc = 0
    # print(f'Rischio idrogeologico {comune} con id {id_comune}: {rischio_idro_perc}')

    # Zona Sismica Coordinate
    near_coords = trova_coordinate_vicine(coordinate[0], coordinate[1], zone_sismiche)
    zona_sismica = int(near_coords.iloc[0]['Zona Sismica'])
    # print(f'Zona Sismica {comune} con id {id_comune}: {zona_sismica}\n')

    # Calcolo indice di pericolosità
    # Normalizzo le denunce
    if (max_denunce_per_ab - min_denunce_per_ab) <= 0:
        den_normal = 0.0
    else:
        den_normal = (denunce_per_ab - min_denunce_per_ab) / (max_denunce_per_ab - min_denunce_per_ab) * 100
    # Normalizzo la zona sismica
    sismi_normal = (1 - (zona_sismica - 1) / 3) * 100

    # Pesi per il calcolo ponderato
    peso_inquinamento = 0.15
    peso_criminalita = 0.2
    peso_denunce = 0.3
    peso_rischio_idrogeologico = 0.1
    peso_zona_sismica = 0.25
    return (
            peso_inquinamento * (inquinamento if inquinamento != -1 else 0) +
            peso_criminalita * (criminalita if criminalita != -1 else 0) +
            peso_denunce * den_normal +
            peso_rischio_idrogeologico * rischio_idro_perc +
            peso_zona_sismica * sismi_normal
    )


class Poi_Type(Enum):
    NEGOZIO = "neg"
    RISTORANTE = "rist"
    SCUOLA = "scuola"


# trova numero poi di un comune in un certo raggio (MAX 100)
def trova_numero_poi_herev7(comune, poi_type, raggio=None):
    valid = {"neg", "rist", "scuola"}
    if poi_type not in valid:
        raise ValueError("Errore: poi_type must be one of %r." % valid)
    if raggio is None:
        if poi_type == 'neg':
            raggio = 1000
        elif poi_type == 'rist':
            raggio = 200
        elif poi_type == 'scuola':
            raggio = 1000

    bounding_box = get_bounding_box(comune, "here")
    coords = trova_coordinate(comune)

    if not bounding_box:
        print(f"Bounding box non trovato per {comune}")

    API_KEY = "oY1k3tXVkAI8O68lu62eXTEkuOc7TQb6Pwn2S_ZCXKo"

    # Trova Negozi
    if poi_type == 'neg':
        api_url = (f'https://geocode.search.hereapi.com/v1/browse?'
                   f'at={coords[0]},{coords[1]}'
                   f'&in=circle:{coords[0]},{coords[1]};r={raggio}'
                   f'&categories=600-6000,600-6100,600-6200,600-6600-0000,600-6700-0000'
                   f'&limit=100&apiKey={API_KEY}')

        response = requests.get(api_url)
        num = None
        if response.status_code == 200:
            num = len(response.json()["items"])
        else:
            print(f"Errore nella richiesta all'API. Codice di stato: {response.status_code}")
        return num

    # Trova Ristoranti
    elif poi_type == 'rist':
        api_url = (f'https://geocode.search.hereapi.com/v1/browse?'
                   f'at={coords[0]},{coords[1]}'
                   f'&in=circle:{coords[0]},{coords[1]};r={raggio}'
                   f'&categories=100-1000-0000'
                   f'&limit=100&apiKey={API_KEY}')

        response = requests.get(api_url)
        num = None
        if response.status_code == 200:
            num = len(response.json()["items"])
        else:
            print(f"Errore nella richiesta all'API. Codice di stato: {response.status_code}")
        return num

    # Trova Scuole
    elif poi_type == 'scuola':
        api_url = (f'https://geocode.search.hereapi.com/v1/browse?'
                   f'at={coords[0]},{coords[1]}'
                   f'&in=circle:{coords[0]},{coords[1]};r={raggio}'
                   f'&categories=800-8200-0000'
                   f'&limit=100&apiKey={API_KEY}')

        response = requests.get(api_url)
        num = None
        if response.status_code == 200:
            num = len(response.json()["items"])
        else:
            print(f"Errore nella richiesta all'API. Codice di stato: {response.status_code}")
        return num


def stima_poi_totali(comune, poi_type, superficie, raggio=None):
    valid = {"neg", "rist", "scuola"}
    if poi_type not in valid:
        raise ValueError("Errore: poi_type must be one of %r." % valid)
    if raggio is None:
        if poi_type == 'neg':
            raggio = 1000
        elif poi_type == 'rist':
            raggio = 200
        elif poi_type == 'scuola':
            raggio = 1000

    num_poi = trova_numero_poi_herev7(comune, poi_type, raggio)
    if num_poi is None or num_poi == 0:
        num_poi = 1
    area_ricerca = (np.pi * raggio * raggio) / (10 ** 6)
    stima = int(superficie / area_ricerca * num_poi)
    # print(comune, poi_type, num_poi, stima)
    return stima
