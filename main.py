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
hour = tm.localtime().tm_hour

def atualizar_repo():
    origin = repo.remote(name='origin')

    # Obtém as informações mais recentes do repositório remoto
    origin.fetch()
    print("\nVerificando se o repositório tem atualizações...")

    # Verifica se há alterações no repositório local
    if repo.is_dirty():
        print("\nO repositório local tem alterações. Realizando um commit genérico antes de atualizar.")
        git_commit('Commit genérico para atualizar o repositório')
        repo.git.push('origin', 'main')
    else:
        # Verifica se há atualizações disponíveis
        if origin.refs:
            print("\nAtualizando o repositório...")
            origin.pull()
            print("Atualização concluída.")
        else:
            print("\nNão há atualizações disponíveis.")

def git_commit(commit_message):
    try:
        repo.git.add('--all')
        repo.git.commit('-m', commit_message)
    except:
        pass


atualizar_repo()

if hour < 17:
    print('Pegando últimos resultados...')
    pm.execute_notebook(
        input_path='atualiza_ultimos_jogos.ipynb',
        output_path='atualiza_ultimos_jogos.ipynb',
        parameters={'dia': ontem}
    )
    print(f'\nCommitando resultados...')
    git_commit(f'Resultados do dia {ontem}')

    print(f'Pegando jogos de hoje...')
    subprocess.run(["python", f"jogos_do_dia.py"])
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
    subprocess.run(["python", f"jogos_do_dia.py"])
    print(f'Commitando jogos do dia...')
    git_commit(f'Jogos do dia {amanha}')

print('Pushing...')
repo.git.push('origin', 'main')

print('Finalizando...')
tm.sleep(7)