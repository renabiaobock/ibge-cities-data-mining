import pandas as pd
import unidecode
import requests
import re
from bs4 import BeautifulSoup


def city_get_info(city_link):
    page = requests.get(city_link)
    if page.status_code == 200:
        soup = BeautifulSoup(page.text, 'html.parser')
        city_info = {
            'city_link': city_link,
            'codigo_ibge': re.findall(r'\d+', soup.select_one('.topo__celula-esquerda .topo__valor').text)[0],
            'gentilico': soup.select_one('.topo__celula-direita .topo__valor').text.replace(' ', '').replace('\n', ''),
            'prefeito': soup.select_one('.topo__celula-linha .topo__valor').text.replace('  ', '').replace('\n', ''),
            'populacao': {
                'populacao_estimada': re.findall(r'\d+\.\d+', soup.select_one('.lista__cabecalho+ .lista__indicador div').text)[0],
                'densidade_demografica': re.findall(r'\d+\,\d+', soup.select_one('.lista__indicador:nth-child(6) div').text)[0]
            }
        }
        return city_info
    else:
        return False


covid_data = pd.read_csv('./dados_municipais_covid.csv')

cities_state = covid_data[['state', 'city']]

cities_state['converted'] = cities_state.apply(lambda x: x.state.lower() + '/' + unidecode.unidecode(x.city.lower().replace(' ', '-').replace("'", "")), axis=1)

state_city_list = cities_state['converted'].to_list()

links = [f'https://cidades.ibge.gov.br/brasil/{state_city}/panorama' for state_city in state_city_list]
