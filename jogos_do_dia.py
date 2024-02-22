import warnings
warnings.filterwarnings('ignore')
import pandas as pd; pd.set_option('display.max_columns', None)
import time
from datetime import date, timedelta
from tqdm import tqdm
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import re
import os
import warnings
warnings.filterwarnings('ignore')

root = os.getcwd()

hour = time.localtime().tm_hour
if hour < 17:
    dia = 'hoje'
else:
    dia = 'amanha'

def clean_name(name):
    name = re.sub(r'\s*-.*$', '', name.strip())  # Remover informações extras
    return name.title()  # Caso contrário, padronizar nome com letras maiúsculas iniciais
def find_point_five(number):
    # Converte o número em uma string
    number_str = str(number)
    # Verifica se a string termina com ".5"
    if number_str.endswith(".5"):
        return True
    else:
        return False
hoje = date.today()
amanha = hoje + timedelta(days=1)

BOOKIE_1 = 'Bet365'
BOOKIE_2 = '1xBet'
BOOKIE_3 = 'Betano'

try:
    if dia != 'amanha':
        existentes = pd.read_csv(f'jogos_do_dia/{hoje}.csv')
    else:
        existentes = pd.read_csv(f'jogos_do_dia/{amanha}.csv')
        
    existentes = existentes['Fixture ID'].unique().tolist()
except:
    existentes = []
# Instanciando o Objeto ChromeOptions
options = webdriver.EdgeOptions()

# Passando algumas opções para esse ChromeOptions
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--log-level=3')

# Criação do WebDriver do Chrome
wd_Chrome = webdriver.Edge(options=options)

# Com o WebDrive a gente consegue a pedir a página (URL)
wd_Chrome.get("https://www.flashscore.com.br/basquete/")
time.sleep(2)

# Para jogos do dia seguinte
if dia == "amanha":
    wd_Chrome.find_element(By.XPATH,'//*[@id="live-table"]/div[1]/div[2]/div/button[3]').send_keys(Keys.ENTER)
    time.sleep(2)

# Pegando o ID dos Jogos
id_jogos = []
jogos = wd_Chrome.find_elements(By.CSS_SELECTOR,'div.event__match--scheduled')

for i in jogos:
    id_jogos.append(i.get_attribute("id"))

# Exemplo de ID de um jogo: 'g_1_Gb7buXVt'    
id_jogos = [i[4:] for i in id_jogos]

# Separando apenas os IDs de jogos que eu não peguei ainda
if len(existentes) > 0:
    id_jogos = [id for id in id_jogos if id not in existentes]

base_jogos = pd.DataFrame({})

for link in tqdm(id_jogos, total=len(id_jogos)):
    wd_Chrome.get(f'https://www.flashscore.com.br/jogo/{link}/#/resumo-de-jogo/resumo-de-jogo')
    
    Odds_H = 0
    Odds_A = 0
    Over_Line = 0
    Odds_Over = 0
    Odds_Under = 0
    HA_Line = 0
    HA_Odds_H = 0
    HA_Odds_A = 0
    
    # Pegando as Informacoes Básicas do Jogo
    try:
        Date = wd_Chrome.find_element(By.CSS_SELECTOR,'div.duelParticipant__startTime').text.split(' ')[0]
        Time = wd_Chrome.find_element(By.CSS_SELECTOR,'div.duelParticipant__startTime').text.split(' ')[1]
        Country = wd_Chrome.find_element(By.CSS_SELECTOR,'span.tournamentHeader__country').text.split(':')[0]
        League = wd_Chrome.find_element(By.CSS_SELECTOR,'span.tournamentHeader__country')
        League = League.find_element(By.CSS_SELECTOR,'a').text
        Home = wd_Chrome.find_element(By.CSS_SELECTOR,'div.duelParticipant__home')
        Home = Home.find_element(By.CSS_SELECTOR,'div.participant__participantName').text
        Away = wd_Chrome.find_element(By.CSS_SELECTOR,'div.duelParticipant__away')
        Away = Away.find_element(By.CSS_SELECTOR,'div.participant__participantName').text

        Country = clean_name(Country)
        League = clean_name(League)
        League_name = Country + ' ' + League

        # if League_name not in lista_ligas:
        #     # Condição satisfeita, pula para a próxima iteração do loop
        #     continue

        # Match Odds
        wd_Chrome.get(f'https://www.flashscore.com.br/jogo/{link}/#/comparacao-de-odds/home-away/tr-incluindo-prol')
        time.sleep(1)
        celulas = wd_Chrome.find_elements(By.CSS_SELECTOR,'div.ui-table__row')
        
        for celula in celulas:
            bookie = celula.find_element(By.CSS_SELECTOR,'img.prematchLogo')
            bookie = bookie.get_attribute('title')
            if ((bookie == BOOKIE_1)):
                Odds_H = float(celula.find_elements(By.CSS_SELECTOR,'a.oddsCell__odd')[0].text)
                Odds_A = float(celula.find_elements(By.CSS_SELECTOR,'a.oddsCell__odd')[1].text)
                break
            elif ((bookie == BOOKIE_2)):
                Odds_H = float(celula.find_elements(By.CSS_SELECTOR,'a.oddsCell__odd')[0].text)
                Odds_A = float(celula.find_elements(By.CSS_SELECTOR,'a.oddsCell__odd')[1].text)
                break
            else:
                pass

        if Odds_H == 0:
            continue

        # Over/Under
        wd_Chrome.get(f'https://www.flashscore.com.br/jogo/{link}/#/comparacao-de-odds/acima-abaixo/tr-incluindo-prol')
        time.sleep(1)
        celulas = wd_Chrome.find_elements(By.CLASS_NAME,'ui-table__row')

        for celula in celulas:
            bookie = celula.find_element(By.CSS_SELECTOR, 'img.prematchLogo').get_attribute('title')
            Odds_Over = float(celula.find_elements(By.TAG_NAME,'span')[1].text)
            Over_Line = float(celula.find_elements(By.TAG_NAME,'span')[0].text)
            if (((bookie == BOOKIE_1) and (Odds_Over >= 1.80) and find_point_five(Over_Line))):
                Odds_Under = float(celula.find_elements(By.TAG_NAME,'span')[2].text)
                break
            elif (((bookie == BOOKIE_2) and (Odds_Over >= 1.80) and find_point_five(Over_Line))):
                Odds_Under = float(celula.find_elements(By.TAG_NAME,'span')[2].text)
                break
            else:
                Over_Line, Odds_Over, Odds_Under = 0, 0, 0                   
                pass


        # Handicap
        wd_Chrome.get(f'https://www.flashscore.com.br/jogo/{link}/#/comparacao-de-odds/handicap-asiatico/tr-incluindo-prol')
        time.sleep(1)
        celulas = wd_Chrome.find_elements(By.CLASS_NAME,'ui-table__row')

        for celula in celulas:
            
            HA_Line = float(celula.find_elements(By.TAG_NAME,'span')[0].text)
            HA_Odds_H = celula.find_elements(By.TAG_NAME,'span')[1].text
            HA_Odds_A = celula.find_elements(By.TAG_NAME,'span')[2].text

            if (HA_Odds_H == '-') or (HA_Odds_A == '-'):
                HA_Odds_H, HA_Odds_A = 0, 0
            else:
                HA_Odds_H, HA_Odds_A = float(HA_Odds_H), float(HA_Odds_A)

            bookie = celula.find_element(By.CSS_SELECTOR, 'img.prematchLogo').get_attribute('title')
            if ((bookie == BOOKIE_1 and HA_Odds_H >= 1.80) and (bookie == BOOKIE_1 and HA_Odds_H <= 2.10) and (find_point_five(HA_Line))):
                break
            elif ((bookie == BOOKIE_2 and HA_Odds_H >= 1.80) and (bookie == BOOKIE_2 and HA_Odds_H <= 2.10) and (find_point_five(HA_Line))):
                break
            elif ((bookie == BOOKIE_3 and HA_Odds_H >= 1.80) and (bookie == BOOKIE_2 and HA_Odds_H <= 2.10) and (find_point_five(HA_Line))):
                break
            else:
                pass

        # print(Date, Home, Over_Line, Odds_Over, Odds_Under, HA_Line, HA_Odds_H, HA_Odds_A)
        # print()

        base_jogos.loc[base_jogos.shape[0],['Fixture ID', 'Date','League','Time','Home','Away','Odds_H','Odds_A','Over_Line','Odds_Over','Odds_Under','HA_Line','HA_Odds_H','HA_Odds_A']] = [
            link, Date, League_name, Time, Home, Away, Odds_H, Odds_A, Over_Line, Odds_Over, Odds_Under, HA_Line, HA_Odds_H, HA_Odds_A
        ]
    except:
        continue

wd_Chrome.quit()
backup = base_jogos.copy()

# Remove jogos sem odds
if len(base_jogos) > 0:
    base_jogos = base_jogos[base_jogos['Odds_H'] != 0]
    base_jogos.reset_index(drop=True, inplace=True)

    # Ajusta coluna de data
    base_jogos['Date'] = pd.to_datetime(base_jogos['Date'], format='%d.%m.%Y')
    base_jogos['Date'] = pd.to_datetime(base_jogos['Date']).dt.date

    dia_jogos = base_jogos['Date'].iloc[0]

    try:
        existente = pd.read_csv(f'jogos_do_dia/{dia_jogos}.csv')
        n_jogos_antes = existente.shape[0]
        existente = pd.concat([existente, base_jogos])
        existente = existente.drop_duplicates(subset=['Home', 'Away'], keep='first')
        existente.reset_index(drop=True, inplace=True)
        n_jogos_depois = existente.shape[0]
        existente.to_csv(f'jogos_do_dia/{dia_jogos}.csv', index=False)
        print(f'{n_jogos_depois - n_jogos_antes} jogos adicionados aos jogos do dia.')
    except:
        base_jogos.to_csv(f'jogos_do_dia/{dia_jogos}.csv', index=False)
        print(f'{len(base_jogos)} jogos')


