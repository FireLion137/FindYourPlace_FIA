# Definizione di tutti i metodi usati. **AVVIARE PRIMA DI QUALSIASI ALTRO CODICE**

import json
import re
import time
import requests
from enum import Enum
import random

from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from geopy.exc import GeocoderTimedOut, GeocoderQuotaExceeded

from sklearn.neighbors import BallTree
import numpy as np
import pandas as pd

from Disegna_box import *

with open('File Dati/CL_ITTER107.json', 'r') as file:
    data = json.load(file)

# Estrai la lista di codici dal file JSON
codes = data['data']['codelists'][0]['codes']

# Associazioni per nomi non corrispondenti
associazioni_comune= {
    "Bolzano": "Bolzano/Bozen",
    "Bolzano / Bozen": "Bolzano/Bozen",
    "Forli": "Forlì"
}
# Funzione per trovare l'id in base al nome del comune
def find_id_comune_by_name(name):
    result= []
    for code in codes:
        if code['name']['it'] == name and re.match("^\\d{6}$", code['id']):
            result.append(code['id'])

    if len(result) == 0 and name in associazioni_comune:
      name= associazioni_comune[name]
      for code in codes:
        if code['name']['it'] == name and re.match("^\\d{6}$", code['id']):
            result.append(code['id'])

    print(name, result)
    if len(result) == 0:
        return None
    elif len(result) == 1:
        return result[0]
    return result

# Associazioni per nomi non corrispondenti
associazioni_regione_province= {
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
      name= associazioni_regione_province[name]
      for code in codes:
        if code['name']['it'] == name and re.match("^IT.*$", code['id']):
            return code['id']
    else:
      return None
    return None

# Funzione per ottenere gli abitanti di un comume
def extract_abitanti_observation(response_json):
    try:
        observation = response_json['data']['dataSets'][0]['series']['0:0:0:0:0:0']['observations']['0'][0]
        return observation
    except KeyError:
        return None

# Funzione per ottenere i problemi in una regione
def extract_problemi_observation(response_json):
    try:
        observation = response_json['data']['dataSets'][0]['series']['0:0:0:0:0:0:0:0:0:0:0:0:0:0:0']['observations']['0'][0]
        return observation
    except KeyError:
        return None

# Funzione per ottenere le denunce in una regione
def extract_denunce_observation(response_json):
    try:
        observation = response_json['data']['dataSets'][0]['series']['0:0:0:0:0:0']['observations']['0'][0]
        return observation
    except KeyError:
        return None

# Funzione per ottenere la spesa media in una regione
def extract_spesamedia_observation(response_json):
    try:
        observation = response_json['data']['dataSets'][0]['series']['0:0:0:0:0:0:0:0:0:0:0']['observations']['0'][0]
        return observation
    except KeyError:
        return None

# Funzione per ottenere la superficie di un comune
def extract_superficie_observation(response_json):
    try:
        observation = response_json['data']['dataSets'][0]['series']['0:0:0']['observations']['0'][0]
        return observation
    except KeyError:
        return None

# Funzione per ottenere le aree a rischio idrogeologico in km2
def extract_rischi_idro_observation(response_json):
    try:
        observationHIGH = response_json['data']['dataSets'][0]['series']['0:0:0']['observations']['0'][0]
        observationLOW = response_json['data']['dataSets'][0]['series']['0:0:1']['observations']['0'][0]
        observationMED = response_json['data']['dataSets'][0]['series']['0:0:2']['observations']['0'][0]
        observations= [observationLOW, observationMED, observationHIGH]
        return observations
    except KeyError:
        return None


geolocator = Nominatim(user_agent="FindYourPlace")
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1, max_retries=5)
reverse = RateLimiter(geolocator.reverse, min_delay_seconds=1, max_retries=5)


# Calcolo spesa media da regione
def calc_spesa_media(regione):
    # Trova id tramite nome regione oppure Nord-Centro-Sud
    id_regione_found = find_id_regione_by_name(regione)

    # Costruisci l'URL con l'id trovato
    api_url = f'https://sdmx.istat.it/SDMXWS/rest/data/31_739/A.HH.99.SPESA_MEDIA..ALL..{id_regione_found}.ALL.ALL.TOT?startPeriod=2021&format=jsondata'

    # Effettua la richiesta all'API
    response = requests.get(api_url)

    # Verifica se la richiesta ha avuto successo (status code 200)
    if response.status_code == 200:
        # Estrai l'observation dalla risposta JSON
        observation = extract_spesamedia_observation(response.json())

        if observation is not None:

            costo_vita = None
            if observation < 2100:
                costo_vita = 1
            elif observation > 2700:
                costo_vita = 3
            else:
                costo_vita = 2

            return costo_vita

    else:
        print("Errore calcolo costo vita")


# Trova popolazione da comune
def trova_popolazione(comune):
    # Trova id tramite nome comune
    id_comune_found = find_id_comune_by_name(comune)

    # Costruisci l'URL con l'id trovato
    api_url = f'https://sdmx.istat.it/SDMXWS/rest/data/22_289/.TOTAL.{id_comune_found}.9.99.?startPeriod=2023&format=jsondata'

    # Effettua la richiesta all'API
    response = requests.get(api_url)

    # Verifica se la richiesta ha avuto successo (status code 200)
    if response.status_code == 200:
        # Estrai l'observation dalla risposta JSON
        observation = extract_abitanti_observation(response.json())

        if observation is not None:
            return observation
        else:
            print("Observation della popolazione non trovato nella risposta JSON.")
    else:
        print(f"Errore nella richiesta all'API. Codice di stato: {response.status_code}")

#### Superficie di un comune
def trova_sup(comune):

    id_comune_found = find_id_comune_by_name(comune)

    # Costruisci l'URL con l'id trovato
    api_url = f'https://sdmx.istat.it/SDMXWS/rest/data/729_1050/A.{id_comune_found}.TOTAREA?startPeriod=2023&format=jsondata'

    # Effettua la richiesta all'API
    response = requests.get(api_url)

    superficie = None
    # Verifica se la richiesta ha avuto successo (status code 200)
    if response.status_code == 200:
        # Estrai l'observation dalla risposta JSON
        observation = extract_superficie_observation(response.json())

        if observation is not None:
            return observation
            superficie = observation / 100
        else:
            print(f"Observation della superficie non trovato nella risposta JSON.")

    else:
        print(f"Errore nella richiesta all'API. Codice di stato: {response.status_code}")


# Funzione per ottenere location da un comune
def trova_location(comune):
    try:
      structuredQuery = {
        "postalcode" : '',
        "state" : '',
        "country" : 'Italia',
        "street" : '',
        "city" : {comune}
      }

      location = geocode(structuredQuery)
      if location is None:
        location = geocode(comune)
    except (GeocoderTimedOut, GeocoderQuotaExceeded, TimeoutError) as e:
      if (TimeoutError, GeocoderQuotaExceeded):
            print(e)
      else:
            print(f'Location not found: {e}')
            return None

    if location is None:
        print(f'Location for {comune} not found')
    return location

# Funzione per ottenere le coordinate di un comune
def trova_coordinate(comune):
    loc= trova_location(comune)

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

            if bbox_type=="here":
              return bounding_box[2], bounding_box[0], bounding_box[3], bounding_box[1]
            elif bbox_type=="overpass":
              return bounding_box[0], bounding_box[2], bounding_box[1], bounding_box[3]

    return None


def get_citta_from_bbox(bbox, num_citta):

    # Generazione casuale di coordinate geografiche nel bounding box
    citta_generate = []
    for _ in range(num_citta):
        lat = (random.uniform(float(bbox[0]), float(bbox[1])))
        lon = (random.uniform(float(bbox[2]), float(bbox[3])))
        citta_generate.append((lat, lon))

    # Restituisci le città generate
    return citta_generate


def get_citta_in_bbox(comune, bbox_type, n):
    # Ottenere il bounding box
    bbox = get_bounding_box(comune, bbox_type)
    if bbox:
        # Generare città casuali nel bounding box
        citta_generate = get_citta_from_bbox(bbox, n)

        # Ottenere nomi delle città basandosi sulle coordinate
        geolocator = Nominatim(user_agent="my_geocoder")
        lista_citta = []

        for lat, lon in citta_generate:
            location = geolocator.reverse((lat, lon), language='it')
            if location and location.address:
                lista_citta.append(location.address)

        return lista_citta

    return None


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


### Lettura dati scaricati istat
class Request_Type(Enum):
    INQUINAMENTO = "inq"
    CRIMINALITA = "crim"
    DENUNCE = "den"
    SUPERFICIE= "sup"
    IDROGEOLOGICO= "idro"
    POPOLAZIONE= "pop"
    SPESA_MEDIA= "spesa"

# Funzione per trovare valore in locale invece che tramite api istat
def trova_valore_per_id(id, request_type):
  valid = {"inq", "crim", "den", "sup", "idro", "pop", "spesa"}
  if request_type not in valid:
      raise ValueError("Errore: request_type must be one of %r." % valid)

  if(request_type == "inq"):
    with open('istatData/inquinamentoRegioni.json', 'r') as file:
        jsonFile = json.load(file)
  elif(request_type == "crim"):
    with open('istatData/criminalitaRegioni.json', 'r') as file:
        jsonFile = json.load(file)
  elif(request_type == "den"):
    with open('istatData/denunceProvince.json', 'r') as file:
        jsonFile = json.load(file)
  elif(request_type == "sup"):
    with open('istatData/superficieComuni.json', 'r') as file:
        jsonFile = json.load(file)
  elif(request_type == "idro"):
    with open('istatData/rischioIdrogeologicoComuni.json', 'r') as file:
        jsonFile = json.load(file)
  elif(request_type == "pop"):
    with open('istatData/popolazione.json', 'r') as file:
        jsonFile = json.load(file)
  elif(request_type == "spesa"):
    with open('istatData/spesaMediaRegioni.json', 'r') as file:
        jsonFile = json.load(file)

  result= []
  for series in jsonFile['message:GenericData']['message:DataSet']['generic:Series']:
      series_key = series['generic:SeriesKey']['generic:Value']

      if type(id) is not list:
        ref_area_dict = next((i for i in series_key if i['@id'] in ['REF_AREA', 'ITTER107'] and i['@value'] == id), None)

        if ref_area_dict:
          try:
            result.append(float(series['generic:Obs']['generic:ObsValue']['@value']))
          except KeyError:
            result.append(-1)
      else:
        for id_x in id:
          ref_area_dict = next((i for i in series_key if i['@id'] in ['REF_AREA', 'ITTER107'] and i['@value'] == id_x), None)

          if ref_area_dict:
            try:
              result.append(float(series['generic:Obs']['generic:ObsValue']['@value']))
            except KeyError:
              result.append(-1)
            continue

  #print(id, result)
  if len(result) == 0:
    return -1
  elif len(result) == 1:
    return result[0]
  return result

listaIdRegioni= ['ITC1', 'ITC2', 'ITC3', 'ITC4',
                 'ITD1', 'ITD2', 'ITD3', 'ITD4', 'ITD5', 'ITDA',
                 'ITE1', 'ITE2', 'ITE3', 'ITE4',
                 'ITF1', 'ITF2', 'ITF3', 'ITF4', 'ITF5', 'ITF6',
                 'ITG1', 'ITG2']

listaProvince = [
    "Agrigento","Alessandria","Ancona","Arezzo","Ascoli Piceno","Asti","Avellino","Bari","Barletta-Andria-Trani",
    "Belluno","Benevento","Bergamo","Biella","Bologna","Bolzano / Bozen","Brescia","Brindisi","Cagliari","Caltanissetta",
    "Campobasso","Caserta","Catania","Catanzaro","Chieti","Como","Cosenza","Cremona","Crotone","Cuneo",
    "Enna","Fermo","Ferrara","Firenze","Foggia","Forlì-Cesena","Frosinone","Genova","Gorizia","Grosseto","Imperia","Isernia",
    "La Spezia","L'Aquila","Latina","Lecce","Lecco","Livorno","Lodi","Lucca","Macerata","Mantova","Massa-Carrara","Matera",
    "Messina","Milano","Modena","Monza e della Brianza","Napoli","Novara","Nuoro","Oristano","Padova","Palermo","Parma","Pavia",
    "Perugia","Pesaro e Urbino","Pescara","Piacenza","Pisa","Pistoia","Pordenone","Potenza","Prato","Ragusa","Ravenna",
    "Reggio di Calabria","Reggio nell'Emilia","Rieti","Rimini","Roma","Rovigo","Salerno","Sassari","Savona",
    "Siena","Siracusa","Sondrio","Sud Sardegna","Taranto","Teramo","Terni","Torino","Trapani","Trento","Treviso","Trieste","Udine",
    "Varese","Venezia","Verbano-Cusio-Ossola","Vercelli","Verona","Vibo Valentia","Vicenza","Viterbo"
]


min_denunce_per_ab = float('inf')
max_denunce_per_ab = float('-inf')
for provincia in listaProvince:
  id_provincia= find_id_regione_by_name(provincia)
  denunce= int(trova_valore_per_id(id_provincia, Request_Type.DENUNCE.value))
  popolazione= int(trova_valore_per_id(id_provincia, Request_Type.POPOLAZIONE.value))

  if(denunce == -1 or popolazione == -1):
    continue

  denunce_per_ab= denunce/popolazione*100000
  if denunce_per_ab < min_denunce_per_ab:
      min_denunce_per_ab = denunce_per_ab
  if denunce_per_ab > max_denunce_per_ab:
      max_denunce_per_ab = denunce_per_ab

# print("Valore minimo delle denunce ogni 100.000 abitanti: ", min_denunce_per_ab)
# print("Valore massimo delle denunce ogni 100.000 abitanti: ", max_denunce_per_ab)

"""Calcolo pericolosità in percentuale di un comune"""
def calc_pericolosita(comune):
  id_comune = find_id_comune_by_name(comune)
  #print(f'ID Comune {comune} ISTAT: {id_comune}')

  provincia= trova_provincia_da_comune(comune)
  id_provincia = find_id_regione_by_name(provincia)
  #print(f'ID Provincia {provincia} ISTAT: {id_provincia}')

  regione= trova_regione_da_comune(comune)
  id_regione = find_id_regione_by_name(regione)
  #print(f'ID Regione {regione} ISTAT: {id_regione}')

  coordinate= trova_coordinate(comune)
  #print(f'Coordinate Comune: {coordinate}\n')

  #### Inquinamento Regione
  inquinamento= trova_valore_per_id(id_regione, Request_Type.INQUINAMENTO.value)
  #print(f'Inquinamento {regione} con id {id_regione}: {inquinamento}')

  #### Criminalità Regione
  criminalità= trova_valore_per_id(id_regione, Request_Type.CRIMINALITA.value)
  #print(f'Criminalità {regione} con id {id_regione}: {criminalità}')

  #### Denunce per 100000 Abitanti Provincia
  popolazione= int(trova_valore_per_id(id_provincia, Request_Type.POPOLAZIONE.value))
  denunce= int(trova_valore_per_id(id_provincia, Request_Type.DENUNCE.value))
  if (denunce != -1):
    denunce_per_ab= denunce/popolazione*100000
  else:
    denunce_per_ab= min_denunce_per_ab
  #print(f'Denunce ogni 100.000 abitanti in {provincia} con id {id_provincia}: {denunce_per_ab}')

  #### Rischio idrogeologico Comune
  if id_comune is not None:
    idrogeologicoValues= trova_valore_per_id(id_comune, Request_Type.IDROGEOLOGICO.value)
  else:
    idrogeologicoValues= trova_valore_per_id(id_regione, Request_Type.IDROGEOLOGICO.value)

  if (idrogeologicoValues != -1):
    ## L'ordine è HIGH - LOW - MED, in Low è incluso Med, in cui a sua volta è incluso High
    idrogeologicoLow= idrogeologicoValues[1]-idrogeologicoValues[2] # Rimuovo il Med (in cui vi è anche l'high)
    idrogeologicoMed= idrogeologicoValues[2]-idrogeologicoValues[0] # Rimuovo l' High
    idrogeologicoHigh= idrogeologicoValues[0]
    ## Trovo superficie comune e calcolo il rischio ponderato
    superficie= trova_valore_per_id(id_comune, Request_Type.SUPERFICIE.value)/100
    rischio_ponderato= idrogeologicoLow*0.5+idrogeologicoMed*1+idrogeologicoHigh*1.5
    rischio_idro_perc= rischio_ponderato/max(superficie, rischio_ponderato)*100
  else:
    rischio_idro_perc= 0
  #print(f'Rischio idrogeologico {comune} con id {id_comune}: {rischio_idro_perc}')

  #### Zona Sismica Coordinate
  near_coords = trova_coordinate_vicine(coordinate[0], coordinate[1], pd.read_csv('File Dati/Zone Sismiche.csv'))
  zona_sismica = int(near_coords.iloc[0]['Zona Sismica'])
  #print(f'Zona Sismica {comune} con id {id_comune}: {zona_sismica}\n')

  #### Calcolo indice di pericolosità
  ## Normalizzo le denunce --- Avviare il codice per calcolare min e max prima!
  if (max_denunce_per_ab - min_denunce_per_ab) <= 0:
      den_normal= 0.0
  else:
      den_normal= (denunce_per_ab - min_denunce_per_ab)/(max_denunce_per_ab - min_denunce_per_ab)*100
  ## Normalizzo la zona sismica
  sismi_normal= (1-(zona_sismica - 1)/3)*100

  ## Pesi per il calcolo ponderato
  peso_inquinamento = 0.15
  peso_criminalita = 0.2
  peso_denunce = 0.3
  peso_rischio_idrogeologico = 0.1
  peso_zona_sismica = 0.25
  return (
          peso_inquinamento * (inquinamento if inquinamento != -1 else 0) +
          peso_criminalita * (criminalità if criminalità != -1 else 0) +
          peso_denunce * den_normal +
          peso_rischio_idrogeologico * rischio_idro_perc +
          peso_zona_sismica * sismi_normal
      )

#print(f'La pericolosità è: {calc_pericolosita("Trento")}')

"""Trova Bounding Box di un comune e ricerca numero negozi, ristoranti e scuole<br>
Purtroppo il limite di pois trovabili è 100, per cui mi limito a cercare in un raggio di X metri solo determinate categorie.
"""


class Poi_Type(Enum):
    NEGOZIO = "neg"
    RISTORANTE = "rist"
    SCUOLA = "scuola"

### trova numero poi di un comune in un certo raggio (MAX 100)
def trova_numero_poi_herev7(comune, poi_type, raggio= None):
  valid = {"neg", "rist", "scuola"}
  if poi_type not in valid:
      raise ValueError("Errore: poi_type must be one of %r." % valid)
  if raggio is None:
    if (poi_type == 'neg'): raggio= 1000
    elif (poi_type == 'rist'): raggio= 200
    elif (poi_type == 'scuola'): raggio= 1000

  bounding_box = get_bounding_box(comune,"here")
  draw_bbox_on_map(bounding_box)
  coords= trova_coordinate(comune)

  if not bounding_box:
      print(f"Bounding box non trovato per {comune}")

  API_KEY= "oY1k3tXVkAI8O68lu62eXTEkuOc7TQb6Pwn2S_ZCXKo"

  ### Trova Negozi
  if (poi_type == 'neg'):
    api_url = (f'https://geocode.search.hereapi.com/v1/browse?'
    f'at={coords[0]},{coords[1]}'
    #f'&in=bbox:{bounding_box[0]},{bounding_box[1]},{bounding_box[2]},{bounding_box[3]}'
    f'&in=circle:{coords[0]},{coords[1]};r={raggio}'
    #https://www.here.com/docs/bundle/places-search-api-developer-guide/page/topics/place_categories/category-600-shopping.html
    f'&categories=600-6000,600-6100,600-6200,600-6600-0000,600-6700-0000'
    f'&limit=100&apiKey={API_KEY}')

    response = requests.get(api_url)
    num= None
    if response.status_code == 200:
        num = len(response.json()["items"])
    else:
        print(f"Errore nella richiesta all'API. Codice di stato: {response.status_code}")
    return num

  ### Trova Ristoranti
  elif (poi_type == 'rist'):
    api_url = (f'https://geocode.search.hereapi.com/v1/browse?'
    f'at={coords[0]},{coords[1]}'
    #f'&in=bbox:{bounding_box[0]},{bounding_box[1]},{bounding_box[2]},{bounding_box[3]}'
    f'&in=circle:{coords[0]},{coords[1]};r={raggio}'
    #https://www.here.com/docs/bundle/places-search-api-developer-guide/page/topics/place_categories/category-600-shopping.html
    f'&categories=100-1000-0000'
    f'&limit=100&apiKey={API_KEY}')

    response = requests.get(api_url)
    num= None
    if response.status_code == 200:
        num = len(response.json()["items"])
    else:
        print(f"Errore nella richiesta all'API. Codice di stato: {response.status_code}")
    return num

  ### Trova Scuole
  elif (poi_type == 'scuola'):
    api_url = (f'https://geocode.search.hereapi.com/v1/browse?'
    f'at={coords[0]},{coords[1]}'
    #f'&in=bbox:{bounding_box[0]},{bounding_box[1]},{bounding_box[2]},{bounding_box[3]}'
    f'&in=circle:{coords[0]},{coords[1]};r={raggio}'
    #https://www.here.com/docs/bundle/places-search-api-developer-guide/page/topics/place_categories/category-600-shopping.html
    f'&categories=800-8200-0000'
    f'&limit=100&apiKey={API_KEY}')

    response = requests.get(api_url)
    num= None
    if response.status_code == 200:
        num = len(response.json()["items"])
    else:
        print(f"Errore nella richiesta all'API. Codice di stato: {response.status_code}")
    return num


"""In questo codice invece provo ad usare overpass, ma in caso di comuni con pochi dati, questo risulterà inaffidabile.<br>
Infatti spesso il codice soprastante anche usando solo un certo raggio e certe categorie, riesce a trovare più negozi in un certo paese.
"""

def trova_numero_negozi_overpass(comune):
    bbox = get_bounding_box(comune,"overpass")
    bbox_query = f"{bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]}"

    overpass_endpoint = "https://overpass-api.de/api/interpreter"

    # Definisci la query Overpass
    query = f"""
    [out:json];
    (
        node["building"="school"]({bbox_query});
        way["building"="school"]({bbox_query});
        relation["building"="school"]({bbox_query});
    );
    out count;
    """

    # Parametri della richiesta
    params = {
        'data': query
    }

    # Effettua la richiesta
    response = requests.get(overpass_endpoint, params=params)

    # Estrai il numero di negozi dal risultato
    result = response.json()
    numero_negozi = result['elements'][0]['tags']['total']

    return numero_negozi

# Trova il numero di negozi del comune
# numero_negozi_trovati = trova_numero_negozi_overpass('Milano')
# print(f"Numero nel bbox specificato: {numero_negozi_trovati}")
