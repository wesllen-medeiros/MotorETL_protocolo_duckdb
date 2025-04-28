from sqlalchemy import Connection, create_engine, text
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.orm import sessionmaker
from src.env import Settings

settings = Settings()


class CoffetlDB:
    """
    Classe para gerenciar a conexão com o banco de dados
    """

    def __init__(self) -> None:
        """Inicializa a configuração da conexão."""
        self.__uri = str(settings.COFFETL_DATABASE_URI)
        self.__ensure_database_exists()
        self.__engine = self.__create_database_engine()

    def __ensure_database_exists(self) -> None:
        """Garante que o banco de dados exista, criando-o se necessário."""
        if not database_exists(self.__uri):
            create_database(self.__uri)
            print(f"Banco de dados '{settings.COFFETLDB_NAME}' criado com sucesso.")
        else:
            print(f"Banco de dados '{settings.COFFETLDB_NAME}' já existe.")

    def __create_database_engine(self) -> Connection:
        """Cria a engine de conexão."""
        return create_engine(self.__uri)

    def get_engine(self) -> Connection:
        """Retorna a engine de conexão"""
        return self.__engine

    def __enter__(self):
        """Método de entrada do context manager. Estabelece conexão."""
        session_make = sessionmaker(bind=self.__engine)
        self.session = session_make()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Método de saída context manager. Fecha conexão."""
        self.session.close()
