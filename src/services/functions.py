import sys
from pathlib import Path
import pandas as pd
from sqlalchemy import text
from bs4 import BeautifulSoup, MarkupResemblesLocatorWarning
import warnings
import os
import csv
from src.database.connection import CoffetlDB
from src.env import Settings
from sqlalchemy_utils import database_exists, create_database


# warnings.filterwarnings("ignore", category=MarkupResemblesLocatorWarning)

settings = Settings()

class DataProcessor:
    """
        Classe para tratamento e validação de dados.
    """

    @staticmethod
    def tratar_dados(df):
        try:
            # Limpa os nomes das colunas
            df.columns = df.columns.str.strip()

            # Remove linhas completamente vazias
            df = df.dropna(how='all')

            # Substitui 0 por valores ausentes (opcional)
            df.replace({0: pd.NA}, inplace=True)

            print("Dados tratados com sucesso.")
            return df
        except Exception as e:
            print(f"Erro ao tratar os dados: {e}")
            return None


class CSVLoader:
    """
        Classe para carregar CSV e enviar para PostgreSQL.
    """

    def __init__(self):
        # Inicializa a conexão com o banco de dados usando CoffetlDB
        self.db = CoffetlDB()
        self.engine = self.db.get_engine()
        self.file_path()
    

    def file_path(self):
        # Adiciona o diretório raiz do projeto ao sys.path
        pasta_raiz = Path(__file__).resolve().parent.parent.parent
        sys.path.append(str(pasta_raiz))

        # Caminho da pasta onde os arquivos CSV estão localizados
        pasta_csv = pasta_raiz / 'csv'

        # Verificar se pasta_csv é um diretório válido
        if pasta_csv.is_dir():
            # Iterar sobre todos os arquivos CSV na pasta csv
            for arquivo in pasta_csv.iterdir():
                if arquivo.suffix == '.csv':
                    # Chamar o método para carregar o CSV no PostgreSQL
                    CSVLoader.carregar_csv_no_postgresql(self, str(arquivo))
        else:
            print(f"Erro: {pasta_csv} não é um diretório válido.")
            # Listar os arquivos encontrados na pasta CSV
            arquivos_encontrados = [arquivo.name for arquivo in pasta_csv.iterdir() if arquivo.is_file()]
            print(f"Arquivos encontrados na pasta CSV: {arquivos_encontrados}")

    def carregar_csv_no_postgresql(self, caminho_arquivo):
        # Verifica se o banco de dados existe, caso contrário, cria
        if not hasattr(self, '_database_checked'):
            if not database_exists(settings.COFFETL_DATABASE_URI):
                create_database(settings.COFFETL_DATABASE_URI)
            print(f"Banco de dados '{settings.COFFETLDB_NAME}' criado com sucesso.")
        else:
            print(f"Banco de dados '{settings.COFFETLDB_NAME}' já existe.")
            self._database_checked = True
        try:
            # Nome da tabela baseado no nome do arquivo CSV
            nome_tabela = os.path.splitext(os.path.basename(caminho_arquivo))[0]

            # Verifica se a tabela já existe e conta os registros
            with self.engine.connect() as connection:
                query = text(f"""
                    SELECT COUNT(*) FROM information_schema.tables 
                    WHERE table_schema = 'public' AND table_name = :nome_tabela
                """)
                tabela_existe = connection.execute(query, {"nome_tabela": nome_tabela}).scalar() > 0

                if tabela_existe:
                    query_count = text(f"SELECT COUNT(*) FROM public.{nome_tabela}")
                    registros_tabela = connection.execute(query_count).scalar()

                    # Conta os registros no CSV
                    with open(caminho_arquivo, encoding='utf-8') as csv_file:
                        registros_csv = sum(1 for _ in csv_file) - 1  # Subtrai o cabeçalho

                    if registros_csv == registros_tabela:
                        print(f"Tabela 'public.{nome_tabela}' já existe com os mesmos dados ({registros_tabela} registros). Operação ignorada.")
                        return

            # Lê o CSV com Pandas
            try:
                df = pd.read_csv(
                    caminho_arquivo,
                    sep=',',
                    engine='python',
                    quoting=csv.QUOTE_MINIMAL,
                    quotechar='"',
                    on_bad_lines='skip',
                    encoding='utf-8'
                )
                print("Arquivo CSV lido com sucesso")
            except Exception as e:
                print(f"Erro ao ler com Pandas: {e}")
                return

            # Função para limpar HTML de colunas de texto
            def limpar_html(valor):
                if isinstance(valor, str):
                    return BeautifulSoup(valor, "html.parser").get_text(separator=' ', strip=True)
                return valor

            # Aplica somente nas colunas de texto (object)
            for coluna in df.select_dtypes(include='object').columns:
                df[coluna] = df[coluna].map(limpar_html)

            # Trata os dados
            processor = DataProcessor()
            df = processor.tratar_dados(df)
            if df is None:
                print("Erro no tratamento dos dados. Operação abortada.")
                return

            # Insere os dados no PostgreSQL
            df.to_sql(nome_tabela, self.engine, schema='public', index=False, if_exists='replace')
            print(f"Dados inseridos com sucesso na tabela 'public.{nome_tabela}'.")
        except Exception as e:
            print(f"Erro geral no processo de carregamento: {e}")
