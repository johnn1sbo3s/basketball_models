import pandas as pd
import numpy as np

# Back e lay home
def back_home(df):
    df.loc[(df['Home_Pts'] > df['Away_Pts']), 'Back_Home'] = 1
    df.loc[(df['Home_Pts'] <= df['Away_Pts']), 'Back_Home'] = 0
    df.loc[(df['Back_Home'] == 1), 'Lay_Home'] = 0
    df.loc[(df['Back_Home'] == 0), 'Lay_Home'] = 1

    return df

# Back e lay away
def back_away(df):
    df.loc[(df['Home_Pts'] < df['Away_Pts']), 'Back_Away'] = 1
    df.loc[(df['Home_Pts'] >= df['Away_Pts']), 'Back_Away'] = 0
    df.loc[(df['Back_Away'] == 1), 'Lay_Away'] = 0
    df.loc[(df['Back_Away'] == 0), 'Lay_Away'] = 1

    return df

# Over
def back_over(df):
    df.loc[(df['Home_Pts'] + df['Away_Pts']) > df['Over_Line'], 'Back_Over'] = 1
    df.loc[(df['Home_Pts'] + df['Away_Pts']) < df['Over_Line'], 'Back_Over'] = 0

    return df

# Under
def back_under(df):
    df['Back_Under'] = 1
    df.loc[df['Back_Over'] == 1, 'Back_Under'] = 0

    return df

def cria_alvos(df):
    df = back_home(df)
    df = back_away(df)
    df = back_over(df)
    df = back_under(df)

    return df

################################################################################
# Prepara df
################################################################################

def prepara_df(df, criar_alvos = True):
    df = df[(df.Odds_H != 0)]
    df = df.query('1.5 <= Odds_Over <= 3').reset_index(drop=True)

    df['p_H'] = 1 / df['Odds_H']
    df['p_A'] = 1 / df['Odds_A']

    df['H_A'] = df['Odds_H'] / df['Odds_A']
    df['A_H'] = df['Odds_A'] / df['Odds_H']
    df['H_O'] = df['Odds_H'] / df['Odds_Over']
    df['A_O'] = df['Odds_A'] / df['Odds_Over']

    df['Euc_Dist_MO'] = np.sqrt(((df['Odds_H'] - df['Odds_A'])**2) + ((df['Odds_H'] - df['Odds_A'])**2))
    df['Angle_MO'] = np.degrees(np.arctan((df['Odds_A'] - df['Odds_H']) / 2))

    df['Euc_Dist_OV'] = np.sqrt(((df['Odds_Over'] - df['Odds_Under'])**2) + ((df['Odds_Over'] - df['Odds_Under'])**2))
    df['Angle_OV'] = np.degrees(np.arctan((df['Odds_Over'] - df['Odds_Under']) / 2))

    df['DifAbs_HomeAway'] = np.abs(df['Odds_H'] - df['Odds_A'])

    df['Angle_HomeAway'] = np.degrees(np.arctan((df['Odds_A'] - df['Odds_H']) / 2))

    df['DifPer_HomeAway'] = np.abs((df['Odds_H'] - df['Odds_A'])) / df['Odds_A']

    n_per = 5

    # Média de pontos
    df['Ptos_H'] = np.where(df['Home_Pts'] >  df['Away_Pts'], 3,
               np.where(df['Home_Pts'] == df['Away_Pts'], 1, 0))

    df['Ptos_A'] = np.where(df['Home_Pts'] >  df['Away_Pts'], 0,
                np.where(df['Home_Pts'] == df['Away_Pts'], 1, 3))

    df['Media_Ptos_H'] = df.groupby('Home')['Ptos_H'].rolling(window=n_per, min_periods=n_per).mean().reset_index(0,drop=True)
    df['Media_Ptos_A'] = df.groupby('Away')['Ptos_A'].rolling(window=n_per, min_periods=n_per).mean().reset_index(0,drop=True)
    df['Media_Ptos_H'] = df.groupby('Home')['Media_Ptos_H'].shift(1)
    df['Media_Ptos_A'] = df.groupby('Away')['Media_Ptos_A'].shift(1)

    df['DesvPad_Ptos_H'] = df.groupby('Home')['Ptos_H'].rolling(window=n_per, min_periods=n_per).std().reset_index(0,drop=True)
    df['DesvPad_Ptos_A'] = df.groupby('Away')['Ptos_A'].rolling(window=n_per, min_periods=n_per).std().reset_index(0,drop=True)
    df['DesvPad_Ptos_H'] = df.groupby('Home')['DesvPad_Ptos_H'].shift(1)
    df['DesvPad_Ptos_A'] = df.groupby('Away')['DesvPad_Ptos_A'].shift(1)

    df['CV_Ptos_H'] = df['DesvPad_Ptos_H'] / df['Media_Ptos_H']
    df['CV_Ptos_A'] = df['DesvPad_Ptos_A'] / df['Media_Ptos_A']

    df['DifPtos_H'] = df['Media_Ptos_H'] - df['Media_Ptos_A']

    # Média de gols marcados
    df['Media_GM_H'] = df.groupby('Home')['Home_Pts'].rolling(window=n_per, min_periods=n_per).mean().reset_index(0,drop=True)
    df['Media_GM_A'] = df.groupby('Away')['Away_Pts'].rolling(window=n_per, min_periods=n_per).mean().reset_index(0,drop=True)
    df['Media_GM_H'] = df.groupby('Home')['Media_GM_H'].shift(1)
    df['Media_GM_A'] = df.groupby('Away')['Media_GM_A'].shift(1)

    df['DesvPad_GM_H'] = df.groupby('Home')['Home_Pts'].rolling(window=n_per, min_periods=n_per).std().reset_index(0,drop=True)
    df['DesvPad_GM_A'] = df.groupby('Away')['Away_Pts'].rolling(window=n_per, min_periods=n_per).std().reset_index(0,drop=True)
    df['DesvPad_GM_H'] = df.groupby('Home')['DesvPad_GM_H'].shift(1)
    df['DesvPad_GM_A'] = df.groupby('Away')['DesvPad_GM_A'].shift(1)

    df['CV_GM_H'] = df['DesvPad_GM_H'] / df['Media_GM_H']
    df['CV_GM_A'] = df['DesvPad_GM_A'] / df['Media_GM_A']

    df['DifGM_H'] = df['Media_GM_H'] - df['Media_GM_A']

    # Média de gols sofridos
    df['Media_GS_H'] = df.groupby('Home')['Away_Pts'].rolling(window=n_per, min_periods=n_per).mean().reset_index(0,drop=True)
    df['Media_GS_A'] = df.groupby('Away')['Home_Pts'].rolling(window=n_per, min_periods=n_per).mean().reset_index(0,drop=True)
    df['Media_GS_H'] = df.groupby('Home')['Media_GS_H'].shift(1)
    df['Media_GS_A'] = df.groupby('Away')['Media_GS_A'].shift(1)

    df['DesvPad_GS_H'] = df.groupby('Home')['Away_Pts'].rolling(window=n_per, min_periods=n_per).std().reset_index(0,drop=True)
    df['DesvPad_GS_A'] = df.groupby('Away')['Home_Pts'].rolling(window=n_per, min_periods=n_per).std().reset_index(0,drop=True)
    df['DesvPad_GS_H'] = df.groupby('Home')['DesvPad_GS_H'].shift(1)
    df['DesvPad_GS_A'] = df.groupby('Away')['DesvPad_GS_A'].shift(1)

    df['CV_GS_H'] = df['DesvPad_GS_H'] / df['Media_GS_H']
    df['CV_GS_A'] = df['DesvPad_GS_A'] / df['Media_GS_A']

    df['DifGS_H'] = df['Media_GS_H'] - df['Media_GS_A']

    # Média de saldo de gols
    df['SG_H'] = df['Home_Pts'] - df['Away_Pts']
    df['SG_A'] = df['Away_Pts'] - df['Home_Pts']

    df['Media_SG_H'] = df.groupby('Home')['SG_H'].rolling(window=n_per, min_periods=n_per).mean().reset_index(0,drop=True)
    df['Media_SG_A'] = df.groupby('Away')['SG_A'].rolling(window=n_per, min_periods=n_per).mean().reset_index(0,drop=True)
    df['Media_SG_H'] = df.groupby('Home')['Media_SG_H'].shift(1)
    df['Media_SG_A'] = df.groupby('Away')['Media_SG_A'].shift(1)

    df['DesvPad_SG_H'] = df.groupby('Home')['SG_H'].rolling(window=n_per, min_periods=n_per).std().reset_index(0,drop=True)
    df['DesvPad_SG_A'] = df.groupby('Away')['SG_A'].rolling(window=n_per, min_periods=n_per).std().reset_index(0,drop=True)
    df['DesvPad_SG_H'] = df.groupby('Home')['DesvPad_SG_H'].shift(1)
    df['DesvPad_SG_A'] = df.groupby('Away')['DesvPad_SG_A'].shift(1)

    df['CV_SG_H'] = df['DesvPad_SG_H'] / df['Media_SG_H']
    df['CV_SG_A'] = df['DesvPad_SG_A'] / df['Media_SG_A']

    df['DifSG_H'] = df['Media_SG_H'] - df['Media_SG_A']

    # Média de saldo de gols pela odd
    df['SG_H_01'] = (df['Home_Pts'] - df['Away_Pts']) / df['p_H']
    df['SG_A_01'] = (df['Away_Pts'] - df['Home_Pts']) / df['p_A']

    df['Media_SG_H_01'] = df.groupby('Home')['SG_H_01'].rolling(window=n_per, min_periods=n_per).mean().reset_index(0,drop=True)
    df['Media_SG_A_01'] = df.groupby('Away')['SG_A_01'].rolling(window=n_per, min_periods=n_per).mean().reset_index(0,drop=True)
    df['Media_SG_H_01'] = df.groupby('Home')['Media_SG_H_01'].shift(1)
    df['Media_SG_A_01'] = df.groupby('Away')['Media_SG_A_01'].shift(1)

    df['DesvPad_SG_H_01'] = df.groupby('Home')['SG_H_01'].rolling(window=n_per, min_periods=n_per).std().reset_index(0,drop=True)
    df['DesvPad_SG_A_01'] = df.groupby('Away')['SG_A_01'].rolling(window=n_per, min_periods=n_per).std().reset_index(0,drop=True)
    df['DesvPad_SG_H_01'] = df.groupby('Home')['DesvPad_SG_H_01'].shift(1)
    df['DesvPad_SG_A_01'] = df.groupby('Away')['DesvPad_SG_A_01'].shift(1)

    df['CV_SG_H_01'] = df['DesvPad_SG_H_01'] / df['Media_SG_H_01']
    df['CV_SG_A_01'] = df['DesvPad_SG_A_01'] / df['Media_SG_A_01']

    # Média de saldo de gols pela odd 2
    df['SG_H_02'] = (df['Home_Pts'] - df['Away_Pts']) / df['p_A']
    df['SG_A_02'] = (df['Away_Pts'] - df['Home_Pts']) / df['p_H']

    df['Media_SG_H_02'] = df.groupby('Home')['SG_H_02'].rolling(window=n_per, min_periods=n_per).mean().reset_index(0,drop=True)
    df['Media_SG_A_02'] = df.groupby('Away')['SG_A_02'].rolling(window=n_per, min_periods=n_per).mean().reset_index(0,drop=True)
    df['Media_SG_H_02'] = df.groupby('Home')['Media_SG_H_02'].shift(1)
    df['Media_SG_A_02'] = df.groupby('Away')['Media_SG_A_02'].shift(1)

    df['DesvPad_SG_H_02'] = df.groupby('Home')['SG_H_02'].rolling(window=n_per, min_periods=n_per).std().reset_index(0,drop=True)
    df['DesvPad_SG_A_02'] = df.groupby('Away')['SG_A_02'].rolling(window=n_per, min_periods=n_per).std().reset_index(0,drop=True)
    df['DesvPad_SG_H_02'] = df.groupby('Home')['DesvPad_SG_H_02'].shift(1)
    df['DesvPad_SG_A_02'] = df.groupby('Away')['DesvPad_SG_A_02'].shift(1)

    df['CV_SG_H_02'] = df['DesvPad_SG_H_02'] / df['Media_SG_H_02']
    df['CV_SG_A_02'] = df['DesvPad_SG_A_02'] / df['Media_SG_A_02']

    # Custo do Gol 2.0
    df['CG_H_02'] = (df['Home_Pts'] / 2) + (df['p_H'] / 2)
    df['CG_A_02'] = (df['Away_Pts'] / 2) + (df['p_A'] / 2)

    df['Media_CG_H_02'] = df.groupby('Home')['CG_H_02'].rolling(window=n_per, min_periods=n_per).mean().reset_index(0,drop=True)
    df['Media_CG_A_02'] = df.groupby('Away')['CG_A_02'].rolling(window=n_per, min_periods=n_per).mean().reset_index(0,drop=True)
    df['Media_CG_H_02'] = df.groupby('Home')['Media_CG_H_02'].shift(1)
    df['Media_CG_A_02'] = df.groupby('Away')['Media_CG_A_02'].shift(1)

    df['DesvPad_CG_H_02'] = df.groupby('Home')['CG_H_02'].rolling(window=n_per, min_periods=n_per).std().reset_index(0,drop=True)
    df['DesvPad_CG_A_02'] = df.groupby('Away')['CG_A_02'].rolling(window=n_per, min_periods=n_per).std().reset_index(0,drop=True)
    df['DesvPad_CG_H_02'] = df.groupby('Home')['DesvPad_CG_H_02'].shift(1)
    df['DesvPad_CG_A_02'] = df.groupby('Away')['DesvPad_CG_A_02'].shift(1)

    df['CV_CG_H_02'] = df['DesvPad_CG_H_02'] / df['Media_CG_H_02']
    df['CV_CG_A_02'] = df['DesvPad_CG_A_02'] / df['Media_CG_A_02']

    # Diferença Custo do Gol
    df['Dif_CG_02'] = df['Media_CG_H_02'] - df['Media_CG_A_02']

    # Média móvel das odds
    df['MediaOddsHome'] = df.groupby('Home')['Odds_H'].rolling(window=n_per).mean().reset_index(level=0, drop=True)
    df['MediaOddsAway'] = df.groupby('Away')['Odds_A'].rolling(window=n_per).mean().reset_index(level=0, drop=True)
    df['MediaOddsHome'] = df.groupby('Home')['MediaOddsHome'].shift(1)
    df['MediaOddsAway'] = df.groupby('Away')['MediaOddsAway'].shift(1)
    df['MediaOddsHome'] = df['MediaOddsHome'].replace(np.nan, 0)
    df['MediaOddsAway'] = df['MediaOddsAway'].replace(np.nan, 0)

    # Variáveis de gols
    df['Media_Goals_Home'] = df.groupby('Home')['Home_Pts'].rolling(5).mean().reset_index(0, drop=True)
    df['Media_Goals_Away'] = df.groupby('Away')['Away_Pts'].rolling(5).mean().reset_index(0, drop=True)
    df['Media_Goals_Home'] = df['Media_Goals_Home'].shift(1)
    df['Media_Goals_Away'] = df['Media_Goals_Away'].shift(1)

    df = df.drop(columns=['SG_H', 'SG_A', 'CG_H_02', 'CG_A_02', 'SG_H_02', 'SG_A_02', 'SG_H_01', 'SG_A_01', 'Ptos_H', 'Ptos_A'])

    df.reset_index(drop=True, inplace=True)

    if criar_alvos:
        df = cria_alvos(df)

    return df