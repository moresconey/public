# SCRIPT TO DOWNLOAD AND LOAD FEDERAL REVENUE CNPJ
# Create by: Ney Moresco
# Date: 2021-09-21
# Update: 2022-10-10

import io
import os
import time
import zipfile
import requests
import pandas as pd
from sqlalchemy import create_engine
from pySmartDL import SmartDL

class DB_CNPJ:
    # Function download files
    def download_file(self, url: str, dest_file: str):
        _ = SmartDL(url, dest_file).start()

    def __init__(self, user, password, ip_postgres, schema):
        # Set Variables
        self.url_base = 'http://200.152.38.155/CNPJ/'
        self.user = user
        self.password = password
        self.serverip = ip_postgres
        self.schema = schema
        self.files = []
        self.uploaded = []
        self.engine = None
        HTML = requests.get(self.url_base)
        df = pd.read_html(HTML.content.decode('utf8'))[0]
        df = df.drop(columns=['Unnamed: 0', 'Description'])
        df = df[df['Name'].str.find('.zip') > 0]
        self.df = df

    def download_files(self, files = []):
        # Create an array with filenames and start download
        # url_base = 'http://200.152.38.155/CNPJ/'
        # self.urls = [f'http://{i}.zip' for i in re.findall('http://(.*?).zip', self.HTML.text)][:-2]
        # self.files = [x.split('/')[-1] for x in self.urls]

        if files == []:
            files = self.df.Name.values

        for _ , row in self.df.iterrows():
            if row.Name in files:
                self.download_file(self.url_base + row.Name, os.getcwd() + '\\' + row.Name)

    def psql_insert_copy(table, conn, keys, data_iter):
        import csv
        """
        Execute SQL statement inserting data

        Parameters
        ----------
        table : pandas.io.sql.SQLTable
        conn : sqlalchemy.engine.Engine or sqlalchemy.engine.Connection
        keys : list of str
            Column names
        data_iter : Iterable that iterates the values to be inserted
        """
        # gets a DBAPI connection that can provide a cursor
        dbapi_conn = conn.connection
        with dbapi_conn.cursor() as cur:
            s_buf = io.StringIO()
            writer = csv.writer(s_buf)
            writer.writerows(data_iter)
            s_buf.seek(0)

            columns = ', '.join(['"{}"'.format(k) for k in keys])
            if table.schema:
                table_name = '{}.{}'.format(table.schema, table.name)
            else:
                table_name = table.name

            sql = 'COPY {} ({}) FROM STDIN WITH CSV'.format(
                table_name, columns)
            cur.copy_expert(sql=sql, file=s_buf)

    def upload_to_postgresql(self, first_upload_truncate = False):
        # Set layout, in order to facilitate the reading of the base a pattern was created in the first two digits, being:
        # st = string
        # cd = code
        # dt = date

        if self.engine is None:
            # Create postgresql engine 
            self.engine = create_engine(f'postgresql://{self.user}:{self.password}@{self.serverip}/postgres?options=-csearch_path%3D{self.schema}')

        self.layout_files = {'EMPRESAS': {'columns':
                                {'st_cnpj_base': [], 'st_razao_social': [], 'cd_natureza_juridica': [], 'cd_qualificacao': [],
                                    'vl_capital_social': [], 'cd_porte_empresa': [], 'st_ente_federativo': []},
                                'table_name_db': 'tb_empresa'},
                        'ESTABELECIMENTOS': {'columns':
                                    {'st_cnpj_base': [], 'st_cnpj_ordem': [], 'st_cnpj_dv': [], 'cd_matriz_filial': [], 'st_nome_fantasia': [], 'cd_situacao_cadastral': [],
                                    'dt_situacao_cadastral': [], 'cd_motivo_situacao_cadastral': [], 'st_cidade_exterior': [], 'cd_pais': [], 'dt_inicio_atividade': [],
                                    'cd_cnae_principal': [], 'cd_cnae_secundario': [], 'st_tipo_logradouro': [], 'st_logradouro': [], 'st_numero': [], 'st_complemento': [],
                                    'st_bairro': [], 'st_cep': [], 'st_uf': [], 'cd_municipio': [], 'st_ddd1': [], 'st_telefone1': [], 'st_ddd2': [], 'st_telefone2': [],
                                    'st_ddd_fax': [], 'st_fax': [], 'st_email': [], 'st_situacao_especial': [], 'dt_situacao_especial': []
                                    }, 'table_name_db': 'tb_estabelecimento'},
                        'SIMPLES': {'columns':
                                    {'st_cnpj_base': [], 'st_opcao_simples': [], 'dt_opcao_simples': [], 'dt_exclusao_simples': [],
                                    'st_opcao_mei': [], 'dt_opcao_mei': [], 'dt_exclusao_mei': []
                                    }, 'table_name_db': 'tb_dados_simples'},
                        'SOCIOS': {'columns':
                                {'st_cnpj_base': [], 'cd_tipo': [], 'st_nome': [], 'st_cpf_cnpj': [], 'cd_qualificacao': [], 'dt_entrada': [],
                                    'cd_pais': [], 'st_representante': [], 'st_nome_representante': [], 'cd_qualificacao_representante': [], 'cd_faixa_etaria': []},
                                'table_name_db': 'tb_socio'},
                        'PAISES': {'columns': {'cd_pais': [], 'st_pais': []}, 'table_name_db': 'tb_pais'},
                        'MUNICIPIOS': {'columns': {'cd_municipio': [], 'st_municipio': []}, 'table_name_db': 'tb_municipios'},
                        'QUALIFICACOES': {'columns': {'cd_qualificacao': [], 'st_qualificacao': []}, 'table_name_db': 'tb_qualificacao_socio'},
                        'NATUREZAS': {'columns': {'cd_natureza_juridica': [], 'st_natureza_juridica': []}, 'table_name_db': 'tb_natureza_juridica'},
                        'MOTIVOS': {'columns': {'cd_motivo_situacao_cadastral': [], 'st_motivo_situacao_cadastral': []}, 'table_name_db': 'tb_motivo_situacao_cadastral'},
                        'CNAES': {'columns': {'cd_cnae': [], 'st_cnae': []}, 'table_name_db': 'tb_cnae'}
                        }

        for _ , row in self.df.iterrows():
            # Check loaded files
            if row.Name in self.uploaded:
                continue

            if first_upload_truncate:
                r = self.create_table(row.Name)
                if r != 'Exists':
                    print('Base {} Created!'.format(r))

            temp_file = io.BytesIO()
            # Select layout from filename
            model = ''.join(letter for letter in row.Name.split('.')[0] if letter.isalpha()).upper()
            # Unzip file into memory
            with zipfile.ZipFile(row.Name, 'r') as zip_ref:
                temp_file.write(zip_ref.read(zip_ref.namelist()[0]))

            # Indicator back to zero
            temp_file.seek(0)

            # Read csv's
            for chunk in pd.read_csv(temp_file, delimiter=';', header=None, chunksize=65000, names=list(self.layout_files[model]['columns'].keys()), iterator=True, dtype=str, encoding="ISO-8859-1"):
                # Format date columns
                for i in chunk.columns[chunk.columns.str.contains('dt_')]:
                    chunk.loc[chunk[i] == '00000000', i] = None
                    chunk.loc[chunk[i] == '0', i] = None
                    chunk[i] = pd.to_datetime(chunk[i], format='%Y%m%d', errors='coerce')

                chunk.fillna('', inplace = True)

                # Using Try for connection attempts, if the connection is lost, wait 60 seconds to retry
                try:
                    chunk.to_sql(self.layout_files[model]['table_name_db'], self.engine, if_exists="append", index=False, method= DB_CNPJ.psql_insert_copy)
                except:
                    time.sleep(60)
                    chunk.to_sql(self.layout_files[model]['table_name_db'], self.engine, if_exists="append", index=False, method= DB_CNPJ.psql_insert_copy)

            # Store processed filenames
            print(f'File {row.Name} uploaded!')
            self.uploaded.append(row.Name)

    def create_table(self, file):
        file = file.split('.')[0]
        file = ''.join(letter for letter in file if letter.isalpha()).upper()

        for i in self.uploaded:
            if i.upper().find(file) >= 0:
                return 'Exists'

        df = pd.DataFrame(self.layout_files[file]['columns'], dtype=str)
        df.to_sql(self.layout_files[file]['table_name_db'], self.engine, if_exists="replace", index=False)
        return self.layout_files[file]['table_name_db']

    def index_db(self):
        # Create index to improve performance
        indexes = ['CREATE INDEX ix_estab_cnpj_base ON cnpj.tb_estabelecimento USING hash(st_cnpj_base);',
        'CREATE INDEX ix_estab_nome_fantasia ON cnpj.tb_estabelecimento USING hash(st_nome_fantasia);',
        'CREATE INDEX ix_estab_uf ON cnpj.tb_estabelecimento USING hash(st_uf);',
        'CREATE INDEX ix_estab_municipio ON cnpj.tb_estabelecimento USING hash(cd_municipio)',
        'CREATE INDEX ix_muni_cod_municipio ON cnpj.tb_municipios USING hash(cd_municipio);',
        'CREATE INDEX ix_muni_municipio ON cnpj.tb_municipios USING hash(st_municipio);',
        'CREATE INDEX ix_simples_cnpj_base ON cnpj.tb_dados_simples USING hash(st_cnpj_base);',
        'CREATE INDEX ix_empresa_cnpj_base ON cnpj.tb_empresa USING hash(st_cnpj_base);',
        'CREATE INDEX ix_socio_cnpj_base ON cnpj.tb_socio USING hash(st_cnpj_base);',
        'CREATE INDEX ix_empresa_razao_social ON cnpj.tb_empresa USING hash(st_razao_social);'
        ]

        for sql in indexes:
            self.engine.execute(sql)

    def show_files(self):
        print(self.df)


if __name__ == '__main__':
    # Set Global Variables
    USER = 'username'
    PASSWORD = 'password'
    SERVER_IP = 'server_ip:server_port' # Server IP + Port
    SCHEMA = 'cnpj'
    obj = DB_CNPJ(USER, PASSWORD, SERVER_IP, SCHEMA)

    obj.show_files()

    # For a single update file per file
    # Type the name of the file you want to download
    # obj.download_files(['Municipios.zip'])

    obj.uploaded = []
    obj.upload_to_postgresql(first_upload_truncate=True)

    obj.index_db()
