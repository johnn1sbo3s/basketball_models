import pandas as pd
import glob
import warnings
warnings.filterwarnings("ignore")
import matplotlib.pyplot as plt

def get_results(data, target, odds):
    data['Date'] = pd.to_datetime(data['Date']).dt.date
    data['Acumulado'] = data['Profit'].cumsum()
    data['Drawdown'] = data['Acumulado'] - data['Acumulado'].cummax()
    data.loc[(data[target] == 1), 'Resultado'] = 'green'
    data.loc[(data[target] == 0), 'Resultado'] = 'red'

    plb = data['Profit'].sum()
    entradas = data.shape[0]
    wr = data[data[target] == 1].shape[0] / entradas
    med_gain = data[data[target] == 1]['Profit'].mean()
    med_loss = data[data[target] == 0]['Profit'].mean()
    roi = plb / entradas
    ev = (wr*med_gain) + ((1-wr)*med_loss)
    dd = data['Drawdown'].min()
    dias = data['Date'].unique().tolist()
    dias = len(dias)
    total_dias = ((data['Date'].max() - data['Date'].min()).days) + 1

    df_odds = data[['Date', 'Home', 'Away', 'Home_Pts', 'Away_Pts', odds, 'Resultado', 'Profit', 'Acumulado']].copy()
    print(f'WR: {wr * 100:.2f}% | ROI: {roi * 100:.2f}% | Drawdown: {dd:.2f}%')
    print(f'MedGain: {med_gain:.2f} | MedLoss: {med_loss:.2f} | EV: {ev:.2f}')
    print(f'\nProfit: {plb:.2f} | Entradas: {entradas:.0f}')
    print(f'Dias: {dias:.0f} ({total_dias:.0f} totais)')


    df_by_day = data.groupby('Date').agg({'Profit': 'sum', 'Fixture ID': 'count'}).reset_index()
    df_by_day = df_by_day.rename(columns={'Profit': 'Total_Profit', 'Fixture ID': 'Qtd_Games'})
    df_by_day['Total_Profit'] = df_by_day['Total_Profit'].round(2)
    df_by_day['Acumulado'] = df_by_day['Total_Profit'].cumsum()

    # Divida a largura da figura em duas colunas
    fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(17, 5))

    # Primeiro gráfico (Acumulado por aposta)
    df_odds['Acumulado'].plot(ax=axes[0], linewidth=2)
    axes[0].set_title('Acumulado por aposta')

    # Segundo gráfico (Acumulado por dia)
    df_by_day['Acumulado'].plot(ax=axes[1], linewidth=2, marker='o')
    axes[1].set_title('Acumulado por dia')

    # Ajuste de layout para aumentar o espaço horizontal
    plt.subplots_adjust(wspace=0.15)

    # Exiba os gráficos
    plt.show()

    return df_odds, df_by_day