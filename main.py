import pandas as pd
import unidecode
import requests
import re
from bs4 import BeautifulSoup


def filter_text_by_regex(regex, text):
    filtered_text = re.findall(regex, text)[0]
    return filtered_text


def get_digit(text):
    return filter_text_by_regex(r'([\d,\.]+)', text)


def get_text_only(text):
    text_only = " ".join(text.split())
    return text_only


def get_text_by_css_selector(soup, css_selector):
    text = soup.select_one(css_selector).text
    return text


def city_get_info(city_link):
    page = requests.get(city_link)
    if page.status_code == 200:
        soup = BeautifulSoup(page.text, 'html.parser')
        # Informacoes Gerais
        city_info = {
            'city_link': city_link,
            'codigo_ibge':  get_digit(get_text_by_css_selector(soup, '.topo__celula-esquerda .topo__valor')),
            'gentilico': get_text_only(get_text_by_css_selector(soup, '.topo__celula-direita .topo__valor')),
            'prefeito': get_text_only(get_text_by_css_selector(soup, '.topo__celula-linha .topo__valor')),
        }
        # Populacao
        city_info['populacao'] = {
            'populacao_estimada': get_digit(get_text_by_css_selector(soup, '.lista__indicador:nth-child(2) div')),
            'populacao_ultimo_censo': get_digit(get_text_by_css_selector(soup, '.lista__indicador:nth-child(4) div')),
            'densidade_demografica':  get_digit(get_text_by_css_selector(soup, '.lista__indicador:nth-child(6) div')),
        }
        # Trabalho e Rendimento
        city_info['trabalho_e_rendimento'] = {
            'salario_medio_mensal_trabalhadores_formais':  get_digit(get_text_by_css_selector(soup, '.lista__indicador:nth-child(9) div')),
            'pessoal_ocupado': get_digit(get_text_by_css_selector(soup, '.lista__indicador:nth-child(11) div')),
            'populacao_ocupada':  get_digit(get_text_by_css_selector(soup, '.lista__indicador:nth-child(13) div')),
            'perc_pop_rend_ate_1/2_salario_minimo':  get_digit(get_text_by_css_selector(soup, '.lista__indicador:nth-child(15) div'))
        }
        # Educacao
        city_info['educacao'] = {
            'taxa_escolarizacao_6a14_anos':  get_digit(get_text_by_css_selector(soup, '.lista__indicador:nth-child(18) div')),
            'IDEB_anos_iniciais_fundamental':  get_digit(get_text_by_css_selector(soup, '.lista__indicador:nth-child(20) div')),
            'IDEB_anos_finais_fundamental':  get_digit(get_text_by_css_selector(soup, '.lista__indicador:nth-child(22) div')),
            'matriculas_ensino_fundamental': get_digit(get_text_by_css_selector(soup, '.lista__indicador:nth-child(24) div')),
            'matriculas_ensino_medio': get_digit(get_text_by_css_selector(soup, '.lista__indicador:nth-child(26) div')),
            'docentes_ensino_fundamental': get_digit(get_text_by_css_selector(soup, '.lista__indicador:nth-child(28) div')),
            'docentes_ensino_medio':  get_digit(get_text_by_css_selector(soup, '.lista__indicador:nth-child(30) div')),
            'estabelecimentos_ensino_fundamental':  get_digit(get_text_by_css_selector(soup, '.lista__indicador:nth-child(32) div')),
            'estabelecimentos_ensino_medio': get_digit(get_text_by_css_selector(soup, '.lista__indicador:nth-child(34) div'))
        }
        # Economia
        city_info['educacao'] = {
            'PIB_per_capta': get_digit(get_text_by_css_selector(soup, '.lista__indicador:nth-child(37) div')),
            'percentual_receitas_externas': get_digit(get_text_by_css_selector(soup, '.lista__indicador:nth-child(39) div')),
            'IDHM': get_digit(get_text_by_css_selector(soup, '.lista__indicador:nth-child(41) div')),
            'total_receitas_realizadas': get_digit(get_text_by_css_selector(soup, '.lista__indicador:nth-child(43) div')),
            'total_receitas_empenhadas': get_digit(get_text_by_css_selector(soup, '.lista__indicador:nth-child(45) div'))
        }
        # Saude
        city_info['saude'] = {
            'mortalidade_infantil': get_digit(get_text_by_css_selector(soup, '.lista__indicador:nth-child(48) div')),
            'internacoes_diarreia': get_digit(get_text_by_css_selector(soup, '.lista__indicador:nth-child(50) div')),
            'estabelecimentos_SUS': get_digit(get_text_by_css_selector(soup,'.lista__indicador:nth-child(52) div' ))
        }
        # Territorio e ambiente
        city_info['territorio_e_ambiente'] = {
            'area_territorial': get_digit(get_text_by_css_selector(soup, '.lista__indicador:nth-child(55) div')),
            'esgotamento_sanitario': get_digit(get_text_by_css_selector(soup, '.lista__indicador:nth-child(57) div')),
            'arborizacao_vias_publicas': get_digit(get_text_by_css_selector(soup, '.lista__indicador:nth-child(59) div')),
            'urbanizacao_vias_publicas': get_digit(get_text_by_css_selector(soup, '.lista__indicador:nth-child(61) div'))
        }
        return city_info
    else:
        print(f'City link: {city_link} not reacheble')
        return False




covid_data = pd.read_csv('./dados_municipais_covid.csv')

cities_state = covid_data[['state', 'city']]

cities_state['converted'] = cities_state.apply(lambda x: x.state.lower() + '/' + unidecode.unidecode(x.city.lower().replace(' ', '-').replace("'", "")), axis=1)

state_city_list = cities_state['converted'].to_list()

links = [f'https://cidades.ibge.gov.br/brasil/{state_city}/panorama' for state_city in state_city_list]


PAGE = requests.get(links[0])
SOUP = BeautifulSoup(PAGE.text, 'html.parser')
