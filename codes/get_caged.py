import pandas as pd

class CAGED:
    def get_uf_base(dtCut = None):
        if dtCut is None:
            dtCut = pd.Timestamp.now() -  pd.DateOffset(months=1)
            dtCut = dtCut.strftime('%b%Y').capitalize()

        URL = f'http://pdet.mte.gov.br/images/Novo_CAGED/{dtCut}/3-tabelas.xlsx'
        df = pd.read_excel(URL, sheet_name = 'Tabela 3')
        df = df.iloc[6:, 1:8]
        df.columns = ['UF', 'CodigoMunicipio' ,'Municipio', 'Admissoes', 'Demissoes', 'Saldo', 'Variacao']
        df.dropna(inplace=True)

        df.Admissoes = pd.to_numeric(df.Admissoes)
        df.Demissoes = pd.to_numeric(df.Demissoes)
        df.Saldo = pd.to_numeric(df.Saldo)

        df.Municipio = df.Municipio.apply(lambda x: x[3:])
        df.sort_values("Saldo", inplace = True, ascending = False)
        df.reset_index(inplace = True, drop = True)
        df['RankNacional'] = range(1,df.shape[0]+1)
        df['RankEstadual'] = df.groupby(by = 'UF')['Saldo'].rank(ascending = False)
        df['RankEstadual'] = df['RankEstadual'].astype('int16')

        return df

    def get_average_wages(dtCut = None):
        if dtCut is None:
            dtCut = pd.Timestamp.now() -  pd.DateOffset(months=1)
            dtCut = dtCut.strftime('%b%Y').capitalize()

        URL = f'http://pdet.mte.gov.br/images/Novo_CAGED/{dtCut}/3-tabelas.xlsx'
        df = pd.read_excel(URL, sheet_name = 'Tabela 9')
        df = df.iloc[4:, 1:]
        df.columns = ['Mes', 'SalarioMedioAdmissao', 'SalarioMedioDesligamento']
        df.dropna(inplace=True)
        df.reset_index(inplace=True, drop=True)
        return df

    def get_cnae_section(dtCut = None):
        if dtCut is None:
            dtCut = pd.Timestamp.now() -  pd.DateOffset(months=1)
            dtCut = dtCut.strftime('%b%Y').capitalize()

        URL = f'http://pdet.mte.gov.br/images/Novo_CAGED/{dtCut}/3-tabelas.xlsx'
        df = pd.read_excel(URL, sheet_name = 'Tabela 1')
        df = df.iloc[6:, 1:6]
        df.columns = ['Secao', 'Admissoes', 'Desligamentos', 'Saldo', 'Variacao']
        df.dropna(inplace=True)
        df.reset_index(inplace=True, drop=True)

        return df

if __name__ == '__main__':
    # Type Month and Year if you want, for automatic not fill dtCut
    dtCut = 'Jul2022'

    dfUF = CAGED.get_uf_base(dtCut)
    dfSection = CAGED.get_cnae_section(dtCut)
    dfSalary = CAGED.get_average_wages(dtCut)