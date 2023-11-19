import pandas as pd; pd.set_option('display.max_columns', None)
import numpy as np

def calcular_mediacg(_df):
    final_df = _df.copy()

    def calcular_media(row):
        date, home, away = row['Date'], row['Home'], row['Away']

        df_cum = _df[(_df['Date'] < date) & ((_df['Home'] == home) | (_df['Away'] == home))].tail(5)
        if len(df_cum) == 5:
            df_cum.loc[(df_cum['Home'] == home), 'real_cg'] = df_cum['CustoGolHome']
            df_cum.loc[(df_cum['Away'] == home), 'real_cg'] = df_cum['CustoGolAway']
            df_cum.loc[(df_cum['Home'] == home), 'real_pontos'] = df_cum['PontosHome']
            df_cum.loc[(df_cum['Away'] == home), 'real_pontos'] = df_cum['PontosAway']
            df_cum.loc[(df_cum['Home'] == home), 'real_odds'] = df_cum['Odds_H']
            df_cum.loc[(df_cum['Away'] == home), 'real_odds'] = df_cum['Odds_A']
            df_cum.loc[(df_cum['Home'] == home), 'gols_feitos'] = df_cum['Home_Pts']
            df_cum.loc[(df_cum['Away'] == home), 'gols_feitos'] = df_cum['Away_Pts']
            df_cum.loc[(df_cum['Home'] == home), 'gols_tomados'] = df_cum['Away_Pts']
            df_cum.loc[(df_cum['Away'] == home), 'gols_tomados'] = df_cum['Home_Pts']
            last_cg = df_cum['real_cg'].iloc[-1]
            media_pts = df_cum['real_pontos'].mean()
            dp_pts = df_cum['real_pontos'].std()
            cv_pts = dp_pts / media_pts
            media_CG = df_cum['real_cg'].mean()
            dp_CG = df_cum['real_cg'].std()
            cv_CG = dp_CG / media_CG
            media_odds = df_cum['real_odds'].mean()
            dp_odds = df_cum['real_odds'].std()
            cv_odds = dp_odds / media_odds
            gols_feitos = df_cum['gols_feitos'].sum()
            gols_tomados = df_cum['gols_tomados'].sum()
            saldo_gols = gols_feitos - gols_tomados
            final_df.loc[row.name, 'Avg_CG_H'] = media_CG
            final_df.loc[row.name, 'DP_CG_H'] = dp_CG
            final_df.loc[row.name, 'CV_CG_H'] = cv_CG
            final_df.loc[row.name, 'Avg_Pontos_H'] = media_pts
            final_df.loc[row.name, 'DP_Pontos_H'] = dp_pts
            final_df.loc[row.name, 'CV_Pontos_H'] = cv_pts
            final_df.loc[row.name, 'CG_H_Last_Game'] = last_cg
            final_df.loc[row.name, 'Media_Odds_Geral_H'] = media_odds
            final_df.loc[row.name, 'DP_Odds_Geral_H'] = dp_odds
            final_df.loc[row.name, 'CV_Odds_Geral_H'] = cv_odds
            final_df.loc[row.name, 'Saldo_Gols_H'] = saldo_gols
        else:
            final_df.loc[row.name, 'Avg_CG_H'] = 0
            final_df.loc[row.name, 'DP_CG_H'] = 0
            final_df.loc[row.name, 'CV_CG_H'] = 0
            final_df.loc[row.name, 'Avg_Pontos_H'] = 0
            final_df.loc[row.name, 'DP_Pontos_H'] = 0
            final_df.loc[row.name, 'CV_Pontos_H'] = 0
            final_df.loc[row.name, 'CG_H_Last_Game'] = 0
            final_df.loc[row.name, 'Media_Odds_Geral_H'] = 0
            final_df.loc[row.name, 'DP_Odds_Geral_H'] = 0
            final_df.loc[row.name, 'CV_Odds_Geral_H'] = 0
            final_df.loc[row.name, 'Saldo_Gols_H'] = 0

        df_cum = _df[(_df['Date'] < date) & ((_df['Home'] == away) | (_df['Away'] == away))].tail(5)
        if len(df_cum) == 5:
            df_cum.loc[(df_cum['Home'] == away), 'real_cg'] = df_cum['CustoGolHome']
            df_cum.loc[(df_cum['Away'] == away), 'real_cg'] = df_cum['CustoGolAway']
            df_cum.loc[(df_cum['Home'] == away), 'real_pontos'] = df_cum['PontosHome']
            df_cum.loc[(df_cum['Away'] == away), 'real_pontos'] = df_cum['PontosAway']
            df_cum.loc[(df_cum['Home'] == away), 'real_odds'] = df_cum['Odds_H']
            df_cum.loc[(df_cum['Away'] == away), 'real_odds'] = df_cum['Odds_A']
            df_cum.loc[(df_cum['Home'] == away), 'gols_feitos'] = df_cum['Home_Pts']
            df_cum.loc[(df_cum['Away'] == away), 'gols_feitos'] = df_cum['Away_Pts']
            df_cum.loc[(df_cum['Home'] == away), 'gols_tomados'] = df_cum['Away_Pts']
            df_cum.loc[(df_cum['Away'] == away), 'gols_tomados'] = df_cum['Home_Pts']
            last_cg = df_cum['real_cg'].iloc[-1]
            media_pts = df_cum['real_pontos'].mean()
            dp_pts = df_cum['real_pontos'].std()
            cv_pts = dp_pts / media_pts
            media_CG = df_cum['real_cg'].mean()
            dp_CG = df_cum['real_cg'].std()
            cv_CG = dp_CG / media_CG
            media_odds = df_cum['real_odds'].mean()
            dp_odds = df_cum['real_odds'].std()
            cv_odds = dp_odds / media_odds
            gols_feitos = df_cum['gols_feitos'].sum()
            gols_tomados = df_cum['gols_tomados'].sum()
            saldo_gols = gols_feitos - gols_tomados
            final_df.loc[row.name, 'Avg_CG_A'] = media_CG
            final_df.loc[row.name, 'DP_CG_A'] = dp_CG
            final_df.loc[row.name, 'CV_CG_A'] = cv_CG
            final_df.loc[row.name, 'Avg_Pontos_A'] = media_pts
            final_df.loc[row.name, 'DP_Pontos_A'] = dp_pts
            final_df.loc[row.name, 'CV_Pontos_A'] = cv_pts
            final_df.loc[row.name, 'CG_A_Last_Game'] = last_cg
            final_df.loc[row.name, 'Media_Odds_Geral_A'] = media_odds
            final_df.loc[row.name, 'DP_Odds_Geral_A'] = dp_odds
            final_df.loc[row.name, 'CV_Odds_Geral_A'] = cv_odds
            final_df.loc[row.name, 'Saldo_Gols_A'] = saldo_gols
        else:
            final_df.loc[row.name, 'Avg_CG_A'] = 0
            final_df.loc[row.name, 'DP_CG_A'] = 0
            final_df.loc[row.name, 'CV_CG_A'] = 0
            final_df.loc[row.name, 'Avg_Pontos_A'] = 0
            final_df.loc[row.name, 'DP_Pontos_A'] = 0
            final_df.loc[row.name, 'CV_Pontos_A'] = 0
            final_df.loc[row.name, 'CG_A_Last_Game'] = 0
            final_df.loc[row.name, 'Media_Odds_Geral_A'] = 0
            final_df.loc[row.name, 'DP_Odds_Geral_A'] = 0
            final_df.loc[row.name, 'CV_Odds_Geral_A'] = 0
            final_df.loc[row.name, 'Saldo_Gols_A'] = 0

    _df.apply(calcular_media, axis=1)

    return final_df


def get_last_info(_df):
    final_df = _df.copy()

    # Ordena o DataFrame pelo campo 'Date'
    final_df.sort_values(by='Date', inplace=True)
    final_df.reset_index(drop=True, inplace=True)

    # Inicializa as colunas de gols das últimas partidas e odds
    final_df['Goals_Last_H'] = 0
    final_df['Goals_Last_A'] = 0
    final_df['Last_Odd_H'] = 0
    final_df['Last_Odd_A'] = 0

    # Função para obter os gols das últimas partidas e odds
    def get_goals_and_odds(row):
        date, home, away = row['Date'], row['Home'], row['Away']

        # Filtra os jogos anteriores do time da casa
        prev_games_home = _df[((_df['Home'] == home) | (_df['Away'] == home)) & (_df['Date'] < date)]
        if not prev_games_home.empty:
            # Seleciona o último jogo
            last_game_home = prev_games_home.iloc[-1]
            if last_game_home['Home'] == home:
                final_df.loc[row.name, 'Goals_Last_H'] = last_game_home['Home_Pts']
                final_df.loc[row.name, 'Last_Odd_H'] = last_game_home['Odds_H']
            else:
                final_df.loc[row.name, 'Goals_Last_H'] = last_game_home['Away_Pts']
                final_df.loc[row.name, 'Last_Odd_H'] = last_game_home['Odds_A']

        # Filtra os jogos anteriores do time visitante
        prev_games_away = _df[((_df['Home'] == away) | (_df['Away'] == away)) & (_df['Date'] < date)]
        if not prev_games_away.empty:
            # Seleciona o último jogo
            last_game_away = prev_games_away.iloc[-1]
            if last_game_away['Home'] == away:
                final_df.loc[row.name, 'Goals_Last_A'] = last_game_away['Home_Pts']
                final_df.loc[row.name, 'Last_Odd_A'] = last_game_away['Odds_H']
            else:
                final_df.loc[row.name, 'Goals_Last_A'] = last_game_away['Away_Pts']
                final_df.loc[row.name, 'Last_Odd_A'] = last_game_away['Odds_A']

    # Aplica a função get_goals_and_odds a cada linha do DataFrame
    final_df.apply(get_goals_and_odds, axis=1)

    return final_df


# Cria classes do target
def cria_alvos(_df):
    # Back Home
    _df.loc[(_df['Home_Pts'] > _df['Away_Pts']), 'Back_Home'] = 1
    _df.loc[(_df['Home_Pts'] < _df['Away_Pts']), 'Back_Home'] = 0
    
    _df.loc[(_df['Back_Home']) == 1, 'PL_Home'] = _df.Odds_H - 1
    _df.loc[(_df['Back_Home']) == 0, 'PL_Home'] = - 1
    
    # Back Away
    _df.loc[(_df['Home_Pts'] < _df['Away_Pts']), 'Back_Away'] = 1
    _df.loc[(_df['Home_Pts'] > _df['Away_Pts']), 'Back_Away'] = 0
    
    _df.loc[(_df['Back_Away']) == 1, 'PL_Away'] = _df.Odds_A - 1
    _df.loc[(_df['Back_Away']) == 0, 'PL_Away'] = - 1
    
    # Over/Under
    _df.loc[(_df['Home_Pts'] + _df['Away_Pts']) > _df['Over_Line'], 'Back_Over'] = 1
    _df.loc[(_df['Home_Pts'] + _df['Away_Pts']) < _df['Over_Line'], 'Back_Over'] = 0
    
    _df.loc[(_df['Back_Over']) == 1, 'PL_Over'] = _df.Odds_Over - 1
    _df.loc[(_df['Back_Over']) == 0, 'PL_Over'] = - 1

    _df.loc[(_df['Back_Over']) == 0, 'PL_Under'] = _df.Odds_Under - 1
    _df.loc[(_df['Back_Over']) == 1, 'PL_Under'] = - 1
    
    # HA
    _df.loc[((_df['Home_Pts'] + _df['HA_Line'])) > _df['Away_Pts'], 'Back_HA_H'] = 1
    _df.loc[((_df['Home_Pts'] + _df['HA_Line'])) < _df['Away_Pts'], 'Back_HA_H'] = 0
    _df.loc[((_df['Home_Pts'] + _df['HA_Line'])) == _df['Away_Pts'], 'Back_HA_H'] = 2
    
    _df.loc[(_df['Back_HA_H']) == 1, 'PL_HA_H'] = _df.HA_Odds_H - 1
    _df.loc[(_df['Back_HA_H']) == 0, 'PL_HA_H'] = - 1
    _df.loc[(_df['Back_HA_H']) == 2, 'PL_HA_H'] = - 0

    _df.loc[(_df['Back_HA_H']) == 0, 'PL_HA_A'] = _df.HA_Odds_A - 1
    _df.loc[(_df['Back_HA_H']) == 1, 'PL_HA_A'] = - 1
    _df.loc[(_df['Back_HA_H']) == 2, 'PL_HA_A'] = - 0

    return _df


################################################################################
# Prepara o _DF
################################################################################

def prepara_df(_df):
    _df.reset_index(drop=True, inplace=True)

    _df = cria_alvos(_df)

    _df['P(H)'] = 1 / _df['Odds_H']
    _df['P(A)'] = 1 / _df['Odds_A']
    _df['P(O)'] = 1 / _df['Odds_Over']
    _df['P(U)'] = 1 / _df['Odds_Under']
    
    _df['P_Diff'] = ((1 / _df['Odds_H']) + (1 / _df['Odds_A'])) - 1

    # Pontos
    _df.loc[((_df['Home_Pts']) > (_df['Away_Pts'])), 'PontosHome'] = 3
    _df.loc[((_df['Home_Pts']) < (_df['Away_Pts'])), 'PontosHome'] = 0
    _df.loc[((_df['Home_Pts']) < (_df['Away_Pts'])), 'PontosAway'] = 3
    _df.loc[((_df['Home_Pts']) > (_df['Away_Pts'])), 'PontosAway'] = 0

    # Custo do gol
    _df['CustoGolHome'] = _df['Home_Pts'] / (1 / _df['Odds_H'])
    _df['CustoGolAway'] = _df['Away_Pts'] / (1 / _df['Odds_A'])
    _df['CustoGolHome'] = _df['CustoGolHome'].replace(np.inf, 0)
    _df['CustoGolAway'] = _df['CustoGolAway'].replace(np.inf, 0)
    _df.reset_index(drop=True, inplace=True)

    # Média, dp e cv do custo do gol
    _df = calcular_mediacg(_df)

    # Últimos gols e odds
    _df = get_last_info(_df)

    _df['MediaCustoGolHome'] = _df.groupby('Home')['CustoGolHome'].rolling(window=5).mean().reset_index(level=0, drop=True)
    _df['MediaCustoGolAway'] = _df.groupby('Away')['CustoGolAway'].rolling(window=5).mean().reset_index(level=0, drop=True)
    _df['MediaCustoGolHome']  = _df.groupby('Home')['MediaCustoGolHome'].shift(1)
    _df['MediaCustoGolAway']  = _df.groupby('Away')['MediaCustoGolAway'].shift(1)
    _df['MediaCustoGolHome'] = _df['MediaCustoGolHome'].replace(np.nan, 0)
    _df['MediaCustoGolAway'] = _df['MediaCustoGolAway'].replace(np.nan, 0)
    
    _df['CV_ML'] = (_df[['Odds_H', 'Odds_A']].std(axis=1)) / (_df[['Odds_H', 'Odds_A']].mean(axis=1))
    _df['CV_Over'] = (_df[['Odds_Over', 'Odds_Under']].std(axis=1)) / (_df[['Odds_Over', 'Odds_Under']].mean(axis=1))
    _df['CV_HA'] = (_df[['HA_Odds_H', 'HA_Odds_A']].std(axis=1)) / (_df[['HA_Odds_H', 'HA_Odds_A']].mean(axis=1))

    _df.reset_index(drop=True, inplace=True)

    # Retornos para home
    _df['Retornos_BH_Acu'] = _df.groupby('Home')['PL_Home'].rolling(5).sum().reset_index(level=0, drop=True)
    _df['Retornos_BH_Acu'] = _df.groupby('Home')['Retornos_BH_Acu'].shift(1)
    _df['Retornos_BH_Acu'] = _df['Retornos_BH_Acu'].fillna(0)
    
    _df['Avg_Retornos_BH'] = _df.groupby('Home')['PL_Home'].rolling(5).mean().reset_index(level=0, drop=True)
    _df['Avg_Retornos_BH'] = _df.groupby('Home')['Avg_Retornos_BH'].shift(1)
    _df['Avg_Retornos_BH'] = _df['Avg_Retornos_BH'].fillna(0)
    
    _df['Custo_Retorno_BH'] = (_df['Odds_H'] - 1) / _df['Avg_Retornos_BH']

    _df['Avg_Porc_BH_Bookie'] = _df.groupby('Home')['P(H)'].rolling(10).mean().reset_index(level=0, drop=True)
    _df['Avg_Porc_BH_Bookie'] = _df.groupby('Home')['Avg_Porc_BH_Bookie'].shift(1)
    _df['Avg_Porc_BH_Bookie'] = _df['Avg_Porc_BH_Bookie'].fillna(0)

    _df['Avg_Porc_BH_Real'] = _df.groupby('Home')['Back_Home'].rolling(10).mean().reset_index(level=0, drop=True)
    _df['Avg_Porc_BH_Real'] = _df.groupby('Home')['Avg_Porc_BH_Real'].shift(1)
    _df['Avg_Porc_BH_Real'] = _df['Avg_Porc_BH_Real'].fillna(0)
    _df['Dist_Porc_BH'] = _df['Avg_Porc_BH_Real'] - _df['Avg_Porc_BH_Bookie']


    # Retornos para away
    _df['Retornos_BA_Acu'] = _df.groupby('Away')['PL_Away'].rolling(5).sum().reset_index(level=0, drop=True)
    _df['Retornos_BA_Acu'] = _df.groupby('Away')['Retornos_BA_Acu'].shift(1)
    _df['Retornos_BA_Acu'] = _df['Retornos_BA_Acu'].fillna(0)

    _df['Avg_Retornos_BA'] = _df.groupby('Away')['PL_Away'].rolling(5).mean().reset_index(level=0, drop=True)
    _df['Avg_Retornos_BA'] = _df.groupby('Away')['Avg_Retornos_BA'].shift(1)
    _df['Avg_Retornos_BA'] = _df['Avg_Retornos_BA'].fillna(0)

    _df['Custo_Retorno_BA'] = (_df['Odds_A'] - 1) / _df['Avg_Retornos_BA']

    _df['Avg_Porc_BA_Bookie'] = _df.groupby('Away')['P(A)'].rolling(10).mean().reset_index(level=0, drop=True)
    _df['Avg_Porc_BA_Bookie'] = _df.groupby('Away')['Avg_Porc_BA_Bookie'].shift(1)
    _df['Avg_Porc_BA_Bookie'] = _df['Avg_Porc_BA_Bookie'].fillna(0)

    _df['Avg_Porc_BA_Real'] = _df.groupby('Away')['Back_Away'].rolling(10).mean().reset_index(level=0, drop=True)
    _df['Avg_Porc_BA_Real'] = _df.groupby('Away')['Avg_Porc_BA_Real'].shift(1)
    _df['Avg_Porc_BA_Real'] = _df['Avg_Porc_BA_Real'].fillna(0)
    _df['Dist_Porc_BA'] = _df['Avg_Porc_BA_Real'] - _df['Avg_Porc_BA_Bookie']

    _df.drop(columns=['CustoGolHome', 'CustoGolAway', 'PontosHome', 'PontosAway'], inplace=True)

    return _df