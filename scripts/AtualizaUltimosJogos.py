import pandas as pd
import time
import numpy as np
from tqdm import tqdm
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import re

def atualiza_ultimos_jogos(id_jogos):

    # Instanciando o Objeto ChromeOptions
    options = webdriver.EdgeOptions()
    
    options.add_argument('--headless')
    options.add_argument('--no-sandbox') 
    options.add_argument('--disable-dev-shm-usage')
    wd_Chrome = webdriver.Edge(options=options)
    
    # Com o WebDrive a gente consegue a pedir a página (URL)
    wd_Chrome.get('https://www.flashscore.com.br')

    time.sleep(1)

    base_jogos = pd.DataFrame({})

    for link in tqdm(id_jogos, total=len(id_jogos)):
        try:
            wd_Chrome.get(f'https://www.flashscore.com.br/jogo/{link}/#/resumo-de-jogo/resumo-de-jogo')

            Home_Pts, Away_Pts = np.nan, np.nan
            Status = 'Não iniciado'

            Status = wd_Chrome.find_element(By.CSS_SELECTOR,'div.detailScore__status').text
            if Status.lower() == 'encerrado' or Status.lower() or 'após pênaltis' or Status.lower() == 'após tempo extra':
                Home_Pts = float(wd_Chrome.find_element(By.CSS_SELECTOR,'div.detailScore__wrapper').text.split('-')[0])
                Away_Pts = float(wd_Chrome.find_element(By.CSS_SELECTOR,'div.detailScore__wrapper').text.split('-')[1])
                Status = Status.title()

            # Pegando as Informacoes Básicas do Jogo
            Home = wd_Chrome.find_element(By.CSS_SELECTOR,'div.duelParticipant__home')
            Home = Home.find_element(By.CSS_SELECTOR,'div.participant__participantName').text
            Away = wd_Chrome.find_element(By.CSS_SELECTOR,'div.duelParticipant__away')
            Away = Away.find_element(By.CSS_SELECTOR,'div.participant__participantName').text
            
            base_jogos.loc[base_jogos.shape[0],['Fixture ID', 'Home', 'Away' , 'Home_Pts', 'Away_Pts', 'Status']] = [
                link, Home, Away, Home_Pts, Away_Pts, Status
            ]

        except:
            continue

    wd_Chrome.quit()

    return base_jogos