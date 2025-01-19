import pycaret.classification as pyc
import plotly.graph_objects as go
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import colors
from IPython.display import display_html
import random

def setup_model_params(target, odds, type_bet, spread = 1):
    global TARGET, ODDS, SPREAD, TYPE_BET
    TARGET = target
    ODDS = odds
    SPREAD = spread
    TYPE_BET = type_bet

def check_setup():
    if TARGET is None or ODDS is None:
        raise Exception('setup_model_params must be called before using this function.')

def calculate_profit(df):

    check_setup()

    if TYPE_BET.lower() == 'lay':
        df.loc[(df[TARGET] == 0), 'Profit'] = - ((df[ODDS] * SPREAD) - 1)
        df.loc[(df[TARGET] == 1), 'Profit'] =  1

    elif TYPE_BET.lower() == 'back':
        df.loc[(df[TARGET] == 1), 'Profit'] = ((df[ODDS] * SPREAD) - 1)
        df.loc[(df[TARGET] == 0), 'Profit'] = - 1

    return df

def setup_pycaret(data, features, seed, train_size = 0.5, normalize = True, normalize_method = 'minmax', remove_outliers = False, fix_imbalance = True, verbose = False):

    check_setup()

    cls = pyc.setup(
        data = data,
        ignore_features = [x for x in data.columns.to_list() if x not in features and x != TARGET],
        target = TARGET,
        train_size = train_size,
        normalize = normalize,
        normalize_method = normalize_method,
        session_id = seed,
        remove_outliers = remove_outliers,
        fix_imbalance = fix_imbalance,
        verbose = verbose,
        memory = False,
    )

    pyc.remove_metric('AUC')
    pyc.remove_metric('Accuracy')
    pyc.remove_metric('Recall')
    pyc.remove_metric('Kappa')
    pyc.remove_metric('MCC')

    xtrain_train = pyc.get_config('X_train')
    ytrain_train = pyc.get_config('y_train')
    xtrain_test = pyc.get_config('X_test')
    ytrain_test = pyc.get_config('y_test')

    real_train = pd.concat([xtrain_train, ytrain_train], axis=1)
    real_test = pd.concat([xtrain_test, ytrain_test],  axis=1)
    real_train.sort_index(inplace=True)
    real_test.sort_index(inplace=True)

    return real_train, real_test

def calculate_metrics(df, total, return_metrics = False):
    df['Acumulado'] = df['Profit'].cumsum()
    df['Drawdown'] = df['Acumulado'] - df['Acumulado'].cummax()
    df['Responsabilidade'] = (df[ODDS] - 1)

    plb = df['Profit'].sum()
    entradas = df.shape[0]
    wr = round((df[df[TARGET] == 1].shape[0] / entradas), 4)
    oddback = (df[ODDS].mean())
    med_gain = df[df[TARGET] == 1]['Profit'].mean()
    med_loss = df[df[TARGET] == 0]['Profit'].mean()
    roi = plb / df['Responsabilidade'].sum()
    porc_ent = entradas / total
    ev = (wr*med_gain) + ((1-wr)*med_loss)
    dd = df['Drawdown'].min()

    if return_metrics == False:
        print(f'PL: {plb:.2f} | ROI: {100*roi:.2f}% | Prec.: {wr:.4f}')
        print(f'Odd média: {oddback:.2f} ({1/oddback:.2f} WR)')
        print(f'Média Gain: {med_gain:.2f} | Média Loss: {med_loss:.2f}')
        print(f'EM: {ev:.2f}')
        print(f'Máx Drawndown: {dd:.2f}')
        print(f'{entradas} entradas em {total} jogos ({100*porc_ent:.2f}%)')
    else:
        return_metrics == True
        metrics = {
            'pl': plb,
            'wr': wr,
            'dd': dd,
            'oddback': oddback,
            'med_gain': med_gain,
            'med_loss': med_loss,
            'roi': roi,
            'porc_ent': porc_ent,
            'ev': ev,
        }
        return metrics

def plot_chart(df, line_limit=None):
    df.sort_index(inplace=True)
    df.reset_index(drop=True, inplace=True)

    df['hbacu'] = df['Profit'].cumsum()

    fig = go.Figure()

    fig.add_trace(go.Scatter
        (
            x = df.index,
            y = df['hbacu'],
            mode = 'lines',
            name = 'Profit',
        )
    )

    if line_limit:
        fig.add_vline(x=line_limit, line_width=2, line_dash="dash", line_color="#5BDED3")

    fig.update_layout(
        title = 'Acumulado por aposta',
        xaxis_title = 'Jogos',
        yaxis_title = 'Acumulado',
        legend_title = 'Legenda',
        hovermode = 'x unified',
        margin = dict(l=20, r=30, t=60, b=20),
        width = 700,
        height = 300,
    )

    fig.show()

def plot_mini_chart(df):
    df.sort_index(inplace=True)
    df.reset_index(drop=True, inplace=True)

    df['hbacu'] = df['Profit'].cumsum()
    df['hbacu'].plot.line(figsize=(3.5, 1))
    plt.xlabel('Index')
    plt.ylabel('Acumulado')
    plt.title('Acumulado por jogo')
    plt.show()

def info_model(model, data, filter_func, filter = 0, show_info = True):
    total = data.shape[0]

    df = pyc.predict_model(model, data, verbose = False)
    df.sort_index(inplace=True)

    df = filter_func(df, filter)

    df = calculate_profit(df)

    if show_info:
        calculate_metrics(df, total)
        plot_chart(df)

    return df

def export_val(df):

    check_setup()

    data = df.copy()
    data.rename(columns={'Profit': 'Profit', ODDS: 'Odds'}, inplace=True)
    data.loc[(data['Profit'] > 0), 'Resultado'] = 'green'
    data.loc[(data['Profit'] < 0), 'Resultado'] = 'red'
    data = data[['Date', 'Home', 'Away', 'FTHG', 'FTAG', 'Odds', 'Resultado', 'Profit']]

    file_name = TARGET.lower()
    data.to_csv(f'{file_name}.csv', index=False)

def resuls_by_period(data, periodo = '1M'):
    dataframe = data.copy()

    dataframe['Date'] = pd.to_datetime(dataframe['Date'])
    df_agrupado = dataframe.groupby(pd.Grouper(key='Date', freq=periodo)).agg({'Profit': 'sum', 'Home': 'count', 'Responsabilidade': 'sum'}).reset_index()
    df_agrupado['Profit'] = df_agrupado['Profit'].astype(float)
    df_agrupado['Profit'] = df_agrupado['Profit'].round(2)
    df_agrupado['ROI'] = df_agrupado['Profit'] / df_agrupado['Responsabilidade']
    df_agrupado['ROI'] = df_agrupado['ROI'].round(2)
    df_agrupado.drop(columns='Responsabilidade', inplace=True)
    media_pl = df_agrupado['Profit'].mean()
    std_pl = df_agrupado['Profit'].std()
    media_roi = df_agrupado['ROI'].mean()
    std_roi = df_agrupado['ROI'].std()
    print(f'Media Profit: {media_pl:.2f}  |   Média ROI: {media_roi:.2f}')
    print(f'Std Profit: {std_pl:.2f}    |   Std ROI: {std_roi:.2f}')

    return df_agrupado

def create_batches(df, size = 1000):
    num_dfs_menores = len(df) // size + 1

    dfs_menores = []

    for i in range(num_dfs_menores):
        inicio = i * size
        fim = (i + 1) * size

        df_menor = df.iloc[inicio:fim]
        dfs_menores.append(df_menor)

    return dfs_menores

def simplify_ranges(lista_intervalos):
    lista_intervalos.sort(key=lambda intervalo: intervalo.left)

    intervalos_simplificados = [lista_intervalos[0]]

    for intervalo in lista_intervalos[1:]:
        if intervalo.left <= intervalos_simplificados[-1].right:
            # Os intervalos se sobrepoõem ou são adjacentes, então os unimos
            intervalos_simplificados[-1] = pd.Interval(intervalos_simplificados[-1].left, max(intervalo.right, intervalos_simplificados[-1].right), closed='right')
        else:
            # Os intervalos não se sobrepoõem, então adicionamos o intervalo à lista
            intervalos_simplificados.append(intervalo)

    return intervalos_simplificados

def find_top_range(var, treino, teste, validacao, bins, n_ranges, target = 'target'):
    nome = f'Cat_{var}'
    var_dict = {}

    # Cut para definir os grupos
    treino[nome]  = pd.cut(treino[var], bins = bins, duplicates='drop')

    pivot_table = pd.pivot_table(treino,
                                values=target,
                                index=[nome],
                                aggfunc=['mean', 'count']
                                )

    pivot_table.sort_values(('mean', target), ascending=False, inplace=True)
    ranges = pivot_table.index.tolist()

    ranges = ranges[:n_ranges]
    ranges = sorted(ranges, key=lambda x: x.left)
    ranges = simplify_ranges(ranges)

    # Máscara booleana para filtrar o DataFrame
    mascara_treino = treino[var].apply(lambda x: any(x in range for range in ranges))
    mascara_teste = teste[var].apply(lambda x: any(x in range for range in ranges))
    mascara_val = validacao[var].apply(lambda x: any(x in range for range in ranges))

    # Aplicar a máscara para obter o DataFrame filtrado
    teste_filtrado = teste[mascara_teste]
    treino_filtrado = treino[mascara_treino]
    val_filtrado = validacao[mascara_val]

    metric_validacao = {}

    metric_tr_base = calculate_metrics(treino, total=len(treino), return_metrics=True)
    metric_te_base = calculate_metrics(teste, total=len(teste), return_metrics=True)
    metric_val_base = calculate_metrics(validacao, total=len(validacao), return_metrics=True)
    metric_treino = calculate_metrics(treino_filtrado, total=len(treino), return_metrics=True)
    metric_teste = calculate_metrics(teste_filtrado, total=len(teste), return_metrics=True)
    metric_validacao = calculate_metrics(val_filtrado, total=len(validacao), return_metrics=True)

    var_dict['range'] = ranges
    var_dict['metric_tr_base'] = metric_tr_base
    var_dict['metric_te_base'] = metric_te_base
    var_dict['metric_val_base'] = metric_val_base
    var_dict['metric_treino'] = metric_treino
    var_dict['metric_teste'] = metric_teste
    var_dict['metric_val'] = metric_validacao
    var_dict['df_treino'] = treino_filtrado
    var_dict['df_teste'] = teste_filtrado
    var_dict['df_val'] = val_filtrado

    return var_dict

def test_bins(train_data, test_data, val_data, features, bins, n_ranges, metric, limit, min_entries=0.02):
    print(f'Bins = {bins} | Range = {n_ranges}', '-' * 150)
    variaveis = features.copy()
    ranges_dict = {}

    for var in variaveis:
        try:
            new_dict = find_top_range(var, n_ranges = n_ranges, treino = train_data, teste = test_data, validacao = val_data, bins = bins, target = 'Profit')
            ranges_dict[var] = new_dict
        except:
            pass

    ordenado = {chave: valor for chave, valor in sorted(ranges_dict.items(), key=lambda item: item[1]['metric_val'][metric[0]], reverse=True)}
    for var in ordenado:
        diff_treino = ordenado[var]["metric_treino"][metric[0]] - ordenado[var]["metric_tr_base"][metric[0]]
        diff_teste = ordenado[var]["metric_teste"][metric[0]] - ordenado[var]["metric_te_base"][metric[0]]
        diff_val = ordenado[var]["metric_val"][metric[0]] - ordenado[var]["metric_val_base"][metric[0]]
        entradas = ordenado[var]["metric_val"]["porc_ent"]
        if ((diff_treino > 0) & (diff_teste > 0) & (diff_val > 0) & (entradas > min_entries) & (abs(ordenado[var]["metric_val"][metric[0]] - ordenado[var]["metric_teste"][metric[0]]) < limit)):
            print(f'{var} | {bins} bins | {n_ranges} ranges')
            print(f'treino: {ordenado[var]["metric_treino"][metric[0]]:.4f} ({ordenado[var]["metric_treino"][metric[0]] - ordenado[var]["metric_tr_base"][metric[0]]:.2f})   |   {ordenado[var]["metric_treino"][metric[1]]:.2f} ({ordenado[var]["metric_treino"][metric[1]] - ordenado[var]["metric_tr_base"][metric[1]]:.2f})')
            print(f'teste: {ordenado[var]["metric_teste"][metric[0]]:.4f} ({ordenado[var]["metric_teste"][metric[0]] - ordenado[var]["metric_te_base"][metric[0]]:.2f})   |   {ordenado[var]["metric_teste"][metric[1]]:.2f} ({ordenado[var]["metric_teste"][metric[1]] - ordenado[var]["metric_te_base"][metric[1]]:.2f})')
            print(f'val: {ordenado[var]["metric_val"][metric[0]]:.4f} ({ordenado[var]["metric_val"][metric[0]] - ordenado[var]["metric_val_base"][metric[0]]:.2f})   |   {ordenado[var]["metric_val"][metric[1]]:.2f} ({ordenado[var]["metric_val"][metric[1]] - ordenado[var]["metric_val_base"][metric[1]]:.2f})')
            print(f'% Ent: {ordenado[var]["metric_val"]["porc_ent"]:.2f}')
            print()
            # exibe_metricas(ranges_dict[var]['df_treino'], total=len(real_treino), return_metrics=False)
            plot_mini_chart(ranges_dict[var]['df_treino'])
            # exibe_metricas(ranges_dict[var]['df_teste'], total=len(real_teste), return_metrics=False)
            plot_mini_chart(ranges_dict[var]['df_teste'])
            plot_mini_chart(ranges_dict[var]['df_val'])
            print()

    return ranges_dict

def apply_gradient(df, column):
    # Normaliza os valores da coluna para estar entre 0 e 1
    norm = colors.Normalize(vmin=df[column].min(), vmax=df[column].max())
    cmap = colors.LinearSegmentedColormap.from_list("", ["red", "orange", "green"])
    colors_series = pd.Series([colors.rgb2hex(cmap(norm(value))) for value in df[column]])

    return colors_series

def best_values(pivot_table1, pivot_table2, pivot_table3, limiar=0.03):
    # Transforma as pivot_tables em dataframes
    df1 = pivot_table1.reset_index()
    df2 = pivot_table2.reset_index()
    df3 = pivot_table3.reset_index()
    n_rows = len(df1)

    # Obtém os índices das linhas que têm bons resultados em ambos os dataframes
    indices_bons_resultados = []

    for i in range(n_rows):
        mean_pvtb1 = df1.iloc[i]['mean'].item()
        mean_pvtb2 = df2.iloc[i]['mean'].item()
        mean_pvtb3 = df3.iloc[i]['mean'].item()
        diff = abs(mean_pvtb1 - mean_pvtb2)
        diff2 = abs(mean_pvtb1 - mean_pvtb3)
        if (diff < limiar) and (diff2 < limiar):
            indices_bons_resultados.append(i)

    # Filtra os dataframes originais usando os índices com bons resultados em ambos
    df1_filtered = df1[df1.index.isin(indices_bons_resultados)]
    df2_filtered = df2[df2.index.isin(indices_bons_resultados)]
    df3_filtered = df3[df3.index.isin(indices_bons_resultados)]

    return df1_filtered, df2_filtered, df3_filtered

def find_best_range(treino, teste, val, var, tipo, bins = 10, limiar = 0.03):
    nome = f'Cat_{var}'

    # Usa qcut para definir os grupos
    treino[nome]  = pd.qcut(treino[var], q = bins, duplicates='drop')
    teste[nome]  = pd.qcut(teste[var], q = bins, duplicates='drop')
    val[nome]  = pd.qcut(val[var], q = bins, duplicates='drop')

    pivot_table = pd.pivot_table(treino,
                                values=tipo,
                                index=[nome],
                                aggfunc=['mean', 'count', 'sum']
                                )
    pivot_table2 = pd.pivot_table(teste,
                                values=tipo,
                                index=[nome],
                                aggfunc=['mean', 'count', 'sum']
                                )
    pivot_table3 = pd.pivot_table(val,
                                values=tipo,
                                index=[nome],
                                aggfunc=['mean', 'count', 'sum']
                                )

    dfzim1, dfzim2, dfzim3 = best_values(pivot_table, pivot_table2, pivot_table3, limiar=limiar)

    aux_treino = dfzim1[dfzim1[('count', tipo)] > 0]
    aux_teste = dfzim2[dfzim2[('count', tipo)] > 0]
    aux_val = dfzim3[dfzim3[('count', tipo)] > 0]

    aux_treino.reset_index(inplace=True)
    aux_teste.reset_index(inplace=True)
    aux_val.reset_index(inplace=True)

    print(var)

    # Aplique o degradê à coluna 'mean' e exiba o DataFrame estilizado
    aux_treino_color = aux_treino.style.apply(lambda x: ['color: black; background-color: {}'.format(cor) for cor in apply_gradient(aux_treino, ('mean', tipo))], axis=0)
    aux_teste_color = aux_teste.style.apply(lambda x: ['color: black; background-color: {}'.format(cor) for cor in apply_gradient(aux_teste, ('mean', tipo))], axis=0)
    # aux_val_color = aux_val.style.apply(lambda x: ['color: black; background-color: {}'.format(cor) for cor in apply_gradient(aux_val, ('mean', target))], axis=0)

    html_str = """
    <div style="display: flex; justify-content:;">
        <div style="margin-right: 30px;">
            <p>Treino</p>
            {0}
        </div>
        <div style="margin-right: 30px;">
            <p>Teste</p>
            {1}
        </div>
        <div>
            <p>Validação</p>
            {2}
        </div>
    </div>
    """

    html_output = html_str.format(aux_treino_color.to_html(), aux_teste_color.to_html(), aux_val.to_html())
    display_html(html_output, raw=True)

    print()
    print('\n')
    print('-' * 130)
    print('\n')


################################################
# SELEÇÃO DE VARIÁVEIS
################################################

def random_variables(var_list, min_vars, max_vars):
    num_vars = random.randint(min_vars, max_vars)
    num_vars = min(num_vars, len(var_list))
    random_vars = random.sample(var_list, num_vars)

    return random_vars

def create_model_sample(data, fts, seed, model_algorithm, fix_imbalance=True):
    sample_real_train, sample_real_test = setup_pycaret(data = data, features = fts, seed = seed, fix_imbalance=fix_imbalance)

    model = pyc.create_model(model_algorithm, verbose = False, fold = 10)

    tab = pyc.pull()
    prec_model = (tab.loc['Mean', 'Prec.'])
    std_model = (tab.loc['Std', 'Prec.'])

    previsoes = pyc.predict_model(model, verbose = False)

    total = previsoes.shape[0]

    previsoes = previsoes[previsoes['prediction_label'] == 1]

    previsoes = calculate_profit(previsoes)
    if TYPE_BET.lower() == 'lay':
        previsoes.loc[(previsoes[TARGET] == 0), 'Profit'] = - ((previsoes[ODDS] * SPREAD) - 1)
        previsoes.loc[(previsoes[TARGET] == 1), 'Profit'] =  0.94
    elif TYPE_BET.lower() == 'back':
        previsoes.loc[(previsoes[TARGET] == 1), 'Profit'] = ((previsoes[ODDS] * SPREAD) - 1) * 0.94
        previsoes.loc[(previsoes[TARGET] == 0), 'Profit'] =  - 1

    pl = previsoes['Profit'].sum()
    entradas = previsoes.shape[0]
    wr = round((previsoes[previsoes[TARGET] == 1].shape[0] / entradas), 2)
    oddback = previsoes[previsoes['prediction_label'] == 1][ODDS].mean()
    med_gain = previsoes[previsoes[TARGET] == 1]['Profit'].mean()
    med_loss = previsoes[previsoes[TARGET] == 0]['Profit'].mean()
    previsoes['Responsabilidade'] = (previsoes[ODDS] - 1)
    roi = pl / previsoes['Responsabilidade'].sum()
    porc_ent = entradas / total
    ev = (wr*med_gain) + ((1-wr)*med_loss)

    metrics = {
        'dataframe': previsoes,
        'prec_model': prec_model,
        'pl': pl,
        'wr': wr,
        'oddback': oddback,
        'med_gain': med_gain,
        'med_loss': med_loss,
        'roi': roi,
        'porc_ent': porc_ent,
        'ev': ev,
        'std_model': std_model,
    }

    return metrics
