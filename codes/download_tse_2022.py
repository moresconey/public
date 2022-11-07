import requests
import pandas as pd
from time import sleep
import os

header = {'user-agent' :'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36'}

# Downloading base from URL, using requests
def download_file(url : str, dest_file : str):
    import requests
    req = requests.get(url)
    file = open(dest_file, 'wb')
    for chunk in req.iter_content(100000):
        file.write(chunk)
    file.close()
    return True

def get_info_files(cd_uf, cd_municipio, cd_zona, cd_secao):
    url = f'https://resultados.tse.jus.br/oficial/ele2022/arquivo-urna/407/dados/{cd_uf}/{cd_municipio}/{cd_zona}/{cd_secao}/p000407-{cd_uf}-m{cd_municipio}-z{cd_zona}-s{cd_secao}-aux.json'
    r = requests.get(url = url, headers= header)
    r = eval(r.content)
    return r

def get_log_files(cd_uf,cd_municipio, cd_zona, cd_secao, folder_path):
    hash_file = get_info_files(cd_uf=cd_uf,cd_municipio= cd_municipio, cd_zona= cd_zona, cd_secao= cd_secao)
    for hashe in hash_file['hashes']:
        cd_hash = hashe['hash']
        for nm_file in hashe['nmarq']:
            url = f'https://resultados.tse.jus.br/oficial/ele2022/arquivo-urna/407/dados/{cd_uf}/{cd_municipio}/{cd_zona}/{cd_secao}/{cd_hash}/{nm_file}'
            download_file(url, folder_path + f'{cd_uf}/{nm_file}')
    return True

# Create Structure
folder_path = 'C:/tse_analise/'
ufs = ['ac', 'al', 'ap', 'am', 'ba', 'ce', 'df', 'es', 'zz', 'go', 'ma', 'mt', 'ms', 'mg', 'pr', 'pb', 'pa', 'pe', 'pi', 'rj', 'rn', 'rs', 'ro', 'rr', 'sc', 'se', 'sp', 'to']
# Create folder
for folder in ufs:
    os.mkdir(folder_path + folder)

# Get All Zones and Section
df = pd.DataFrame()
for cd_uf in ufs:
    url = f'https://resultados.tse.jus.br/oficial/ele2022/arquivo-urna/407/config/{cd_uf}/{cd_uf}-p000407-cs.json'
    r = requests.get(url = url, headers= header)
    r = eval(r.content)

    for municipio in r['abr'][0]['mu']:
        print('UF: {} -> {}'.format(cd_uf, municipio['nm']))
        for zonas in municipio['zon']:
            for sec in zonas['sec']:
                df = pd.concat([df, pd.DataFrame([{'cd_uf' : cd_uf,'cd_municipio' : municipio['cd'], 'nm_municipio' : municipio['nm'], 'cd_zona' : zonas['cd'],'cd_secao' : sec['ns'], 'cd_secao2': sec['nsp']}])], ignore_index=True)

df['download'] = True
# Salva arquivo de Resumo
df.to_excel(folder_path + 'resumo.xlsx', index=False)

# caso queira iniciar o download de um arquivo já gravado
# df = pd.read_excel(folder_path + 'resumo.xlsx', dtype=str)

# download all log files
for idx, row in df.iterrows():
    # if row['cd_uf'] != 'pe':
    #     continue
    if row['download']:
        try:
            if get_log_files(row['cd_uf'],row['cd_municipio'], row['cd_zona'], row['cd_secao'], folder_path):
                df.loc[idx, 'download'] = False
        except:
            sleep(60*3)
            if get_log_files(row['cd_uf'],row['cd_municipio'], row['cd_zona'], row['cd_secao'], folder_path):
                df.loc[idx, 'download'] = False

df.to_excel(folder_path + 'resumo.xlsx', index=False)