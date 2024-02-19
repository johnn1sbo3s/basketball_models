import papermill as pm
import subprocess
import os
from datetime import datetime, timedelta
import time as tm
import git

REPO_PATH = os.getcwd()
repo = git.Repo(REPO_PATH)
data_var = datetime.now().strftime('%Y-%m-%d')
amanha = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
ontem = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

def git_commit(commit_message):
    try:
        repo.git.add('--all')
        repo.git.commit('-m', commit_message)
    except:
        pass

# get hour
hour = tm.localtime().tm_hour

if hour < 17:
    print('Pegando últimos resultados...')
    pm.execute_notebook(
        input_path='update_last_games.ipynb',
        output_path='update_last_games.ipynb',
        parameters={'data_var': ontem}
    )
    print(f'\nCommitando resultados...')
    git_commit(f'Resultados do dia {ontem}')

    print(f'Pegando jogos de hoje...')
    pm.execute_notebook(
        input_path='jogos_do_dia.ipynb',
        output_path='jogos_do_dia.ipynb',
        parameters={'dia': 'hoje'}
    )
    print(f'Commitando jogos do dia...')
    git_commit(f'Jogos do dia {data_var}')

    print('Gerando apostas...')
    pm.execute_notebook(
        input_path='apostas_do_dia_v1.ipynb',
        output_path='apostas_do_dia_v1.ipynb',
        parameters={'data_var': data_var}
    )
    pm.execute_notebook(
        input_path='apostas_do_dia_v2.ipynb',
        output_path='apostas_do_dia_v2.ipynb',
        parameters={'data_var': data_var}
    )
    print(f'Commitando apostas do dia...')
    git_commit(f'Apostas do dia {data_var}')
else:
    print(f'Pegando jogos de amanhã...')
    pm.execute_notebook(
        input_path='jogos_do_dia.ipynb',
        output_path='jogos_do_dia.ipynb',
        parameters={'dia': 'amanha'}
    )

print('Pushing...')
repo.git.push('origin', 'main')

print('Finalizando...')
tm.sleep(7)