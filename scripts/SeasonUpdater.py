import pandas as pd; pd.set_option('display.max_columns', None)
import time
from tqdm import tqdm
from selenium.webdriver.common.by import By
from selenium import webdriver
from  selenium.webdriver.common.keys import Keys
import re

def clean_name(name):
    name = re.sub(r'\s*-.*$', '', name.strip())  # Remover informações extras
    return name.title()  # Padronizar nome com letras maiúsculas iniciais

def find_point_five(number):
    # Converte o número em uma string
    number_str = str(number)
    # Verifica se a string termina com ".5"
    if number_str.endswith(".5"):
        return True
    else:
        return False

def atualiza_temporada(url, temp_path, n_jogos):
    # Lendo o arquivo da temporada pra verificar a existência
    try:
        temporada = pd.read_csv(temp_path)
    except:
        # Dicionário com as colunas e seus valores iniciais zerados
        data = {'Date': [], 'League': [], 'Time': [], 'Home': [], 'Away': [], 'Home_Pts': [], 'Away_Pts': [], 'Odds_H': [], 'Odds_A': [],
            'Over_Line': [],'Odds_Over': [],'Odds_Under': [], 'HA_Line': [], 'HA_Odds_H': [], 'HA_Odds_A': []
        }
        temporada = pd.DataFrame(data)
        temporada.to_csv(f'{temp_path}')

    # Instanciando o Objeto ChromeOptions
    options = webdriver.EdgeOptions()
    
    # options.add_argument('--headless')
    options.add_argument('--no-sandbox') 
    options.add_argument('--disable-dev-shm-usage')
    
    wd_Chrome = webdriver.Edge(options=options)

    # Com o WebDrive a gente consegue a pedir a página (URL)
    wd_Chrome.get(url)

    time.sleep(0.8)

    # Apertando o botão de carregar mais jogos
    if n_jogos > 100:
        try:
            loadMore = wd_Chrome.find_element(By.CSS_SELECTOR, 'a.event__more--static')
            isPresent = loadMore.is_displayed()
            cliquei = 0
        
            while isPresent:
                try:
                    cliquei = cliquei + 1
                    print(f'Cliquei Load More {cliquei} vezes')
                    wd_Chrome.find_element(By.CSS_SELECTOR, 'a.event__more--static').send_keys(Keys.ENTER)
                    time.sleep(2)
                    isPresent = loadMore.is_displayed()
                except:
                    isPresent = False
                    break
        except:
            print("LoadMore não encontrado na página.")
            pass

    # Pegando o ID dos Jogos
    id_jogos = []
    jogos = wd_Chrome.find_elements(By.CSS_SELECTOR,'div.event__match--static')

    for i in jogos:
        id_jogos.append(i.get_attribute("id"))

    # Exemplo de ID de um jogo: 'g_1_Gb7buXVt'    
    id_jogos = [i[4:] for i in id_jogos]

    # Pegando apenas os últimos n_jogos
    id_jogos = id_jogos[:n_jogos]

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
            Home_Pts = float(wd_Chrome.find_element(By.CSS_SELECTOR,'div.detailScore__wrapper').text.split('-')[0])
            Away_Pts = float(wd_Chrome.find_element(By.CSS_SELECTOR,'div.detailScore__wrapper').text.split('-')[1])

            if League.lower == 'nba - pré-temporada' :
                # Condição satisfeita, pula para a próxima iteração do loop
                continue

            Country = clean_name(Country)
            League = clean_name(League)
            League_name = Country + ' ' + League
            
            # Match Odds
            wd_Chrome.get(f'https://www.flashscore.com.br/jogo/{link}/#/comparacao-de-odds/home-away/tr-incluindo-prol')
            time.sleep(0.8)
            celulas = wd_Chrome.find_elements(By.CSS_SELECTOR,'div.ui-table__row')
            
            for celula in celulas:
                bookie = celula.find_element(By.CSS_SELECTOR,'img.prematchLogo')
                bookie = bookie.get_attribute('title')
                if ((bookie == 'bet365')):
                    Odds_H = float(celula.find_elements(By.CSS_SELECTOR,'a.oddsCell__odd')[0].text)
                    Odds_A = float(celula.find_elements(By.CSS_SELECTOR,'a.oddsCell__odd')[1].text)
                    break
                else:
                    pass


            # Over/Under
            wd_Chrome.get(f'https://www.flashscore.com.br/jogo/{link}/#/comparacao-de-odds/acima-abaixo/tr-incluindo-prol')
            time.sleep(0.8)
            celulas = wd_Chrome.find_elements(By.CLASS_NAME,'ui-table__row')

            for celula in celulas:
                bookie = celula.find_element(By.CSS_SELECTOR, 'img.prematchLogo').get_attribute('title')
                Odds_Over = float(celula.find_elements(By.TAG_NAME,'span')[1].text)
                Over_Line = float(celula.find_elements(By.TAG_NAME,'span')[0].text)
                if (((bookie == 'bet365') and (Odds_Over >= 1.80) and find_point_five(Over_Line))):
                    Odds_Under = float(celula.find_elements(By.TAG_NAME,'span')[2].text)
                    break
                else:
                    Over_Line, Odds_Over, Odds_Under = 0, 0, 0                   
                    pass


            # Handicap
            wd_Chrome.get(f'https://www.flashscore.com.br/jogo/{link}/#/comparacao-de-odds/handicap-asiatico/tr-incluindo-prol')
            time.sleep(0.8)
            celulas = wd_Chrome.find_elements(By.CLASS_NAME,'ui-table__row')

            for celula in celulas:

                HA_Line = float(celula.find_elements(By.TAG_NAME,'span')[0].text)
                HA_Odds_H = float(celula.find_elements(By.TAG_NAME,'span')[1].text)

                bookie = celula.find_element(By.CSS_SELECTOR, 'img.prematchLogo').get_attribute('title')
                if ((bookie == 'bet365' and HA_Odds_H >= 1.80) and (bookie == 'bet365' and HA_Odds_H <= 2.10) and (find_point_five(HA_Line))):
                    HA_Odds_A = float(celula.find_elements(By.TAG_NAME,'span')[2].text)
                    break
                else:
                    pass

            # print(Date, Home, Over_Line, Odds_Over, Odds_Under, HA_Line, HA_Odds_H, HA_Odds_A)
            # print()

            base_jogos.loc[base_jogos.shape[0],['Date', 'League','Time','Home','Away','Home_Pts','Away_Pts','Odds_H','Odds_A','Over_Line','Odds_Over','Odds_Under','HA_Line','HA_Odds_H','HA_Odds_A']] = [
                Date, League_name, Time, Home, Away, Home_Pts, Away_Pts, Odds_H, Odds_A, Over_Line, Odds_Over, Odds_Under, HA_Line, HA_Odds_H, HA_Odds_A
            ]
        except:
            continue

    wd_Chrome.quit()

    # Ajusta coluna de data
    base_jogos['Date'] = pd.to_datetime(base_jogos['Date'], format='%d.%m.%Y')
    base_jogos = base_jogos.sort_values(by='Date')
    base_jogos['Date'] = base_jogos['Date'].dt.date
    base_jogos.reset_index(drop=True, inplace=True)
    
    temporada = pd.read_csv(temp_path)
    n_antes = len(temporada)

    # Exclui os registros que já existem no dataset da temporada
    temporada = pd.concat([temporada, base_jogos], ignore_index=True)
    temporada = temporada.drop_duplicates(subset=['Date', 'Home', 'Away'], keep='first')
    temporada.reset_index(drop=True, inplace=True)
    n_depois = len(temporada)

    temporada.to_csv(temp_path, index=False)

    n_atualizacao = n_depois - n_antes
    liga = url.split('/')[5]
    print(f'Temporada da {liga} atualizada com {n_atualizacao} jogos')
    print()