from sqlalchemy.schema import CreateSchema, Sequence
from sqlalchemy.sql import text
from sqlalchemy_utils import database_exists, create_database
from src.database.connection import CoffetlDB, settings
from src.log_config import get_logger

logger = get_logger()


class CoffetlDBBuilder:
    """Gerencia a criação da estrutura do banco de dados."""

    def __init__(self) -> None:
        """Inicializa a configuração da conexão."""
        self._db = CoffetlDB()

    @classmethod
    def create_database(self) -> None:
        """Cria um banco de dados caso não exista."""
        try:
            if not database_exists(settings.COFFETL_DATABASE_URI):
                create_database(settings.COFFETL_DATABASE_URI)
                logger.info(
                    f'Banco de dados "{settings.COFFETLDB_NAME}" criado com sucesso.'
                )
            else:
                logger.info(
                    f'Banco de dados "{settings.COFFETLDB_NAME}" já existe.'
                )
        except Exception as e:
            logger.error(f'Erro ao criar banco de dados: {e}')

    def create_schema(self, schema_name: str) -> bool:
        """Realiza a criação de um schema."""
        if not self.__has_schema(schema_name):
            try:
                with self._db as conn:
                    conn.session.execute(CreateSchema(schema_name))
                    conn.session.commit()
            except Exception as e:
                logger.error(f'Erro ao criar schema "{schema_name}": {e}')
                return False
        logger.info(f'Schema "{schema_name}" criado com sucesso.')
        return True

    def __has_schema(self, schema_name: str) -> bool:
        """Realiza a verificação da existencia de um schema."""
        with self._db as conn:
            if conn.get_engine().dialect.has_schema(
                conn.session, schema_name
            ):
                return True
        return False

    def build_struct(self, schema_name: str) -> None:
        """Criação da estrutura de banco de dados frotas."""
        base = self._match_system_base(schema_name)

        if not self.create_schema(schema_name):
            logger.error(f'O schema "{schema_name}" não existe.')
            return

        try:
            with self._db as conn:
                base.metadata.create_all(
                    conn.get_engine(),
                    checkfirst=True,
                )
        except Exception as e:
            logger.error(
                f'Erro ao criar tabelas do schema "{schema_name}": {e}'
            )
            return

    def _match_system_base(self, schema_name: str) -> None:
        """Realiza mapeamento dos bases de acordo com o schema."""
        match schema_name:
            case 'admin':
                from src.database.base import BASE_ADMIN
                from src.controls import models

                return BASE_ADMIN

            case 'frotas':
                from src.database.base import BASE_FROTAS
                # from src.backend.core.apps.frotas import models

                return BASE_FROTAS
