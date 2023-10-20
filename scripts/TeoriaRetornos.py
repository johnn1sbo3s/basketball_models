import pandas as pd; pd.set_option('display.max_columns', None); pd.options.mode.chained_assignment = None  # default='warn'
import numpy as np

def teoria_retornos(df, target, odds, outputs = ['1', '2']):
    # Home
    df.loc[(df['Home_Pts'] > df['Away_Pts']), target] = 1
    df.loc[(df['Home_Pts'] < df['Away_Pts']), target] = 0
    df.loc[(df[target]) == 1, 'pl1'] = (100 * df[odds[0]]) - 100
    df.loc[(df[target]) == 0, 'pl1'] = - 100
    
    # Away
    df.loc[(df[target]) == 0, 'pl2'] = (100 * df[odds[1]]) - 100
    df.loc[(df[target]) == 1, 'pl2'] = - 100


    # Identifique as datas únicas em que ocorreram jogos
    last_days = df[df['Home'] != ""]['Date'].unique()
    last_days = last_days[-101:]
    df = df[df['Date'].isin(last_days)]

    pl_home_por_dia = df.groupby('Date')['pl1'].sum().reset_index()
    pl_away_por_dia = df.groupby('Date')['pl2'].sum().reset_index()

    # df[['Date', 'Home', 'Away', 'Home_Pts', 'Away_Pts', target, odds[0], odds[1]]].to_excel('teste_TR.xlsx', index=False)

    TR = pd.DataFrame({
        'Date': pl_home_por_dia['Date'],
        'h_pl': pl_home_por_dia['pl1'],
        'a_pl': pl_away_por_dia['pl2'],
    })

    TR['Date'] = pd.to_datetime(TR['Date'], format='%Y/%m/%d')
    TR = TR.sort_values(by='Date')
    TR['Date'] = TR['Date'].dt.strftime('%d/%m/%Y')

    TR.reset_index(drop=True, inplace=True)
    TR.reset_index(inplace=True)
    TR.rename(columns={"index": "peso"}, inplace=True)
    TR['peso'] += 1

    def get_result(row):
        max_value = max(row['h_pl'], row['a_pl'])
        if row['h_pl'] == max_value:
            return outputs[0]
        else:
            return outputs[1]

    # Aplicar a função get_result para criar a nova coluna 'Result'
    TR['Result'] = TR.apply(get_result, axis=1)

    TR['h_acu'] = TR['h_pl'].cumsum()
    TR['a_acu'] = TR['a_pl'].cumsum()

    TR['numerador'] = TR['h_acu'].rolling(window=16, min_periods=16).apply(lambda x: (x * TR.loc[x.index, 'peso']).sum(), raw=False)
    TR['denominador'] = TR['peso'].rolling(window=16, min_periods=16).sum()
    TR['H16'] = TR['numerador'] / TR['denominador']
    TR.drop(columns=['numerador', 'denominador'], inplace=True)

    TR['numerador'] = TR['h_acu'].rolling(window=8, min_periods=8).apply(lambda x: (x * TR.loc[x.index, 'peso']).sum(), raw=False)
    TR['denominador'] = TR['peso'].rolling(window=8, min_periods=8).sum()
    TR['H8'] = TR['numerador'] / TR['denominador']
    TR.drop(columns=['numerador', 'denominador'], inplace=True)

    TR['HC'] = 2 * TR['H8'] - TR['H16']

    TR['numerador'] = TR['HC'].rolling(window=4, min_periods=4).apply(lambda x: (x * TR.loc[x.index, 'peso']).sum(), raw=False)
    TR['denominador'] = TR['peso'].rolling(window=4, min_periods=4).sum()
    TR['H4'] = TR['numerador'] / TR['denominador']
    TR.drop(columns=['numerador', 'denominador'], inplace=True)

    TR['numerador'] = TR['a_acu'].rolling(window=16, min_periods=16).apply(lambda x: (x * TR.loc[x.index, 'peso']).sum(), raw=False)
    TR['denominador'] = TR['peso'].rolling(window=16, min_periods=16).sum()
    TR['A16'] = TR['numerador'] / TR['denominador']
    TR.drop(columns=['numerador', 'denominador'], inplace=True)

    TR['numerador'] = TR['a_acu'].rolling(window=8, min_periods=8).apply(lambda x: (x * TR.loc[x.index, 'peso']).sum(), raw=False)
    TR['denominador'] = TR['peso'].rolling(window=8, min_periods=8).sum()
    TR['A8'] = TR['numerador'] / TR['denominador']
    TR.drop(columns=['numerador', 'denominador'], inplace=True)

    TR['AC'] = 2 * TR['A8'] - TR['A16']

    TR['numerador'] = TR['AC'].rolling(window=4, min_periods=4).apply(lambda x: (x * TR.loc[x.index, 'peso']).sum(), raw=False)
    TR['denominador'] = TR['peso'].rolling(window=4, min_periods=4).sum()
    TR['A4'] = TR['numerador'] / TR['denominador']
    TR.drop(columns=['numerador', 'denominador'], inplace=True)

    TR['H_Dist'] =  TR['h_acu'] / TR['H4']
    TR['A_Dist'] =  TR['a_acu'] / TR['A4']

    TR['HR'] = (TR['H4'] - TR['H4'].shift(1)) / (TR['H4'].shift(1).abs())
    TR['AR'] = (TR['A4'] - TR['A4'].shift(1)) / (TR['A4'].shift(1).abs())

    TR['numerador'] = TR['H4'].rolling(window=5, min_periods=5).apply(lambda x: ((x - TR.loc[x.index, 'H4'].mean()) * (TR.loc[x.index, 'peso'] - TR.loc[x.index, 'peso'].mean())).sum(), raw=False)
    TR['H_Inc'] = TR['numerador'] / 10
    TR.drop(columns=['numerador'], inplace=True)

    TR['numerador'] = TR['A4'].rolling(window=5, min_periods=5).apply(lambda x: ((x - TR.loc[x.index, 'A4'].mean()) * (TR.loc[x.index, 'peso'] - TR.loc[x.index, 'peso'].mean())).sum(), raw=False)
    TR['A_Inc'] = TR['numerador'] / 10
    TR.drop(columns=['numerador'], inplace=True)

    TR['H_DP'] = TR['h_acu'].rolling(window=10, min_periods=10).std()
    TR['A_DP'] = TR['a_acu'].rolling(window=10, min_periods=10).std()

    TR['Hamp'] = TR['h_acu'].rolling(window=10, min_periods=10).max() / TR['h_acu'].rolling(window=10, min_periods=10).min()
    TR['Aamp'] = TR['a_acu'].rolling(window=10, min_periods=10).max() / TR['a_acu'].rolling(window=10, min_periods=10).min()

    def normalize_last_5(window):
        min_val = window.min()
        max_val = window.max()
        try:
            result = (window.iloc[-1] - min_val) / (max_val - min_val)
        except:
            result = 0
        return result

    # Criar uma janela de tamanho 5 dos últimos registros e calculUR a normalização
    TR['norm_H4'] = TR['H4'].rolling(window=5, min_periods=1).apply(normalize_last_5, raw=False)
    TR['norm_A4'] = TR['A4'].rolling(window=5, min_periods=1).apply(normalize_last_5, raw=False)

    TR['norm_H_Dist'] = TR['H_Dist'].rolling(window=5, min_periods=1).apply(normalize_last_5, raw=False)
    TR['norm_A_Dist'] = TR['A_Dist'].rolling(window=5, min_periods=1).apply(normalize_last_5, raw=False)

    TR['norm_HR'] = TR['HR'].rolling(window=5, min_periods=1).apply(normalize_last_5, raw=False)
    TR['norm_AR'] = TR['AR'].rolling(window=5, min_periods=1).apply(normalize_last_5, raw=False)

    TR['norm_H_Inc'] = TR['H_Inc'].rolling(window=5, min_periods=1).apply(normalize_last_5, raw=False)
    TR['norm_A_Inc'] = TR['A_Inc'].rolling(window=5, min_periods=1).apply(normalize_last_5, raw=False)

    TR['norm_H_DP'] = TR['H_DP'].rolling(window=5, min_periods=1).apply(normalize_last_5, raw=False)
    TR['norm_A_DP'] = TR['A_DP'].rolling(window=5, min_periods=1).apply(normalize_last_5, raw=False)

    TR['norm_Hamp'] = TR['Hamp'].rolling(window=5, min_periods=1).apply(normalize_last_5, raw=False)
    TR['norm_Aamp'] = TR['Aamp'].rolling(window=5, min_periods=1).apply(normalize_last_5, raw=False)

    TR.fillna(0, inplace=True)
    TR['R'] = TR['Result'].shift(-1)
    TR = TR.iloc[27:]

    TR_norm = TR.iloc[:, -13:]

    last = TR_norm['norm_H4'].iloc[-1]
    TR_norm['dist_H4'] = TR_norm['norm_H4'].apply(lambda x: abs(last - x))
    last = TR_norm['norm_A4'].iloc[-1]
    TR_norm['dist_A4'] = TR_norm['norm_A4'].apply(lambda x: abs(last - x))

    last = TR_norm['norm_H_Dist'].iloc[-1]
    TR_norm['dist_H_Dist'] = TR_norm['norm_H_Dist'].apply(lambda x: abs(last - x))
    last = TR_norm['norm_A_Dist'].iloc[-1]
    TR_norm['dist_A_Dist'] = TR_norm['norm_A_Dist'].apply(lambda x: abs(last - x))

    last = TR_norm['norm_HR'].iloc[-1]
    TR_norm['dist_HR'] = TR_norm['norm_HR'].apply(lambda x: abs(last - x))
    last = TR_norm['norm_AR'].iloc[-1]
    TR_norm['dist_AR'] = TR_norm['norm_AR'].apply(lambda x: abs(last - x))

    last = TR_norm['norm_H_Inc'].iloc[-1]
    TR_norm['dist_H_Inc'] = TR_norm['norm_H_Inc'].apply(lambda x: abs(last - x))
    last = TR_norm['norm_A_Inc'].iloc[-1]
    TR_norm['dist_A_Inc'] = TR_norm['norm_A_Inc'].apply(lambda x: abs(last - x))

    last = TR_norm['norm_H_DP'].iloc[-1]
    TR_norm['dist_H_DP'] = TR_norm['norm_H_DP'].apply(lambda x: abs(last - x))
    last = TR_norm['norm_A_DP'].iloc[-1]
    TR_norm['dist_A_DP'] = TR_norm['norm_A_DP'].apply(lambda x: abs(last - x))

    last = TR_norm['norm_Hamp'].iloc[-1]
    TR_norm['dist_Hamp'] = TR_norm['norm_Hamp'].apply(lambda x: abs(last - x))
    last = TR_norm['norm_Aamp'].iloc[-1]
    TR_norm['dist_Aamp'] = TR_norm['norm_Aamp'].apply(lambda x: abs(last - x))

    TR_norm['Distancia'] = TR_norm['dist_H4'] + TR_norm['dist_A4'] + TR_norm['dist_H_Dist'] + TR_norm['dist_A_Dist'] + TR_norm['dist_HR'] + TR_norm['dist_AR'] + TR_norm['dist_H_Inc'] + TR_norm['dist_A_Inc'] + TR_norm['dist_H_DP'] + TR_norm['dist_A_DP'] + TR_norm['dist_Hamp'] + TR_norm['dist_Aamp']

    TR_norm.drop(['dist_H4', 'dist_A4', 'dist_H_Dist', 'dist_A_Dist', 'dist_HR', 'dist_AR', 'dist_H_Inc', 'dist_A_Inc', 'dist_H_DP', 'dist_A_DP', 'dist_Hamp', 'dist_Aamp'], axis=1, inplace=True)

    TR_norm['Rank'] = TR_norm['Distancia'].rank(ascending=True)
    TR_norm['Rank'] -= 1

    TR_norm.reset_index(drop=True, inplace=True)
    resposta = TR_norm.sort_values('Distancia').iloc[1:4, -3]
    resposta = resposta.values

    return resposta, TR