import duckdb
from datetime import datetime

from src.log_config import get_logger
from src.env import Settings

logger = get_logger()
settings = Settings()


class DuckDB:
    """
    Client para gerenciar a conexão com o DuckDB e configurar a integração com PostgreSQL.
    """

    _instance = None
    _connection = None

    def __new__(cls, *args, **kwargs) -> 'DuckDB':
        """Verifica se a instância já existe."""
        if not cls._instance:
            cls._instance = super(DuckDB, cls).__new__(
                cls, *args, **kwargs
            )
        return cls._instance

    def __init__(self) -> None:
        """Inicializa a conexão com o DuckDB."""
        if not hasattr(self, '__engine'):
            self.__path = settings.DUCKDB_PATH
            self.__secret_string = settings.DUCKDB_SECRET_STRING
            self.__engine = self.__create_database_engine()

        if not hasattr(self, '__postgres_attached'):
            self._set_postgres_config()
            self.__postgres_attached = True

    def __create_database_engine(self) -> duckdb.DuckDBPyConnection:
        """Cria a engine de conexão."""
        if not DuckDB._connection:
            DuckDB._connection = duckdb.connect(self.__path)
        return DuckDB._connection

    def get_engine(self) -> duckdb.DuckDBPyConnection:
        """Retorna a engine de conexão"""
        return self.__engine

    def close(self) -> None:
        """Fecha a conexão com o DuckDB."""
        if DuckDB._connection:
            DuckDB._connection.close()
            DuckDB._connection = None

    def _set_postgres_config(self) -> None:
        """Configura o DuckDB para conexão com o PostgreSQL."""
        try:
            self.__engine.execute('INSTALL postgres;')
            self.__engine.execute('LOAD postgres;')

            if not self._has_secret():
                self._secret = self._generate_duckdb_secret()
            else:
                self._secret = settings.DUCKDB_SECRET_NAME

            self.__engine.execute(
                f"ATTACH '' AS coffetl_pg (TYPE POSTGRES, SECRET {self._secret});"
            )
            logger.trace(
                'Extensão postgres configurada com sucesso no DuckDB.'
            )
        except Exception as e:
            logger.error(
                f'Erro ao configurar a extensão postgres no DuckDB: {e}'
            )
            raise

    def _generate_duckdb_secret(self) -> str:
        """Gera um persistent secret para o DuckDB."""
        try:
            self.__engine.execute(
                f'CREATE PERSISTENT SECRET coffetl_pg_secret ({self.__secret_string});'
            )
            logger.info('Secret gerado com sucesso.')
            return settings.DUCKDB_SECRET_NAME
        except Exception as e:
            logger.error(f'Erro ao gerar secret do DuckDB: {e}')
            raise

    def _has_secret(self) -> bool:
        """Verifica se o secret já existe no DuckDB."""
        try:
            result = self.__engine.execute('FROM duckdb_secrets()').fetchone()
            return result is not None
        except Exception as e:
            logger.error(f'Erro ao verificar segredo do DuckDB: {e}')
            raise

    def fetch_view(self, schema: str, view: str) -> duckdb.DuckDBPyRelation:
        """Retorna a view de uma tabela."""
        try:
            return self.__engine.sql(
                f'SELECT * FROM coffetl_pg.{schema}.vw_{view}'
            )
        except Exception as e:
            logger.warning(
                f'Não foram encontrados dados de "{view}" transformados: {e}'
            )

    def add_ocurrences(self, data: list[dict]) -> None:
        """Insere registros adicionados na fila de envio à tabela de controle."""
        try:
            sql = """
                INSERT INTO coffetl_pg.admin.registros_ocorrencias (
                        hash, sistema, tipo_registro, status, json_envio
                ) VALUES (
                    $hash, $sistema, $tipo_registro, $status, $json_envio
                )
            """

            self.__engine.executemany(sql, data)

        except Exception as e:
            logger.error(f'Não foi possível adicionar ocorrência: {e}')

    def add_batchs(self, batch_id: str, url: str) -> None:
        """Insere lotes enviados na tabela de controle."""
        try:
            sql = """
                INSERT INTO coffetl_pg.admin.registros_lotes (
                        id_lote, tipo_registro, url_consulta, status, envio
                ) VALUES (
                    $id_lote, $tipo_registro, $url_consulta, $status, $envio
                )
            """

            self.__engine.execute(
                sql,
                {
                    'id_lote': batch_id,
                    'tipo_registro': url.split('/')[-1],
                    'url_consulta': url,
                    'status': 'AGUARDANDO_EXECUCAO',
                    'envio': datetime.now(),
                },
            )

        except Exception as e:
            logger.error(f'Não foi possível adicionar ocorrência: {e}')

    def fetch_pendent_batchs(self, endpoint: str) -> duckdb.DuckDBPyRelation:
        """Retorna listagem de lotes pendentes."""
        try:
            return self.__engine.sql(
                f"""SELECT * 
                FROM coffetl_pg.admin.registros_lotes 
                WHERE 
                    tipo_registro = '{endpoint}'
                    AND status IN (
                        'AGUARDANDO_EXECUCAO', 
                        'EXECUTANDO', 
                        'AGUARDANDO_REEXECUCAO'
                    )
                """
            )
        except Exception as e:
            logger.error(
                f'Problema ao realizar consulta de lotes pendentes: {e}'
            )

    def update_ocurrences(self, data: list[dict]) -> None:
        """Insere registros adicionados na fila de envio à tabela de controle."""
        try:
            sql = """
                UPDATE coffetl_pg.admin.registros_ocorrencias SET
                    status = $status,
                    id_lote = $id_lote,
                    mensagem_erro = $mensagem_erro
                WHERE 
                    hash= $hash
                    AND status IN ('AGUARDANDO_EXECUCAO')
            """

            self.__engine.executemany(sql, data)

        except Exception as e:
            logger.error(f'Não foi possível atualizar ocorrência: {e}')

    def update_ctrl_ids(
        self, schema: str, table: str, data: list[dict]
    ) -> None:
        """Insere registros adicionados na fila de envio à tabela de controle."""
        try:
            sql = f"""
                UPDATE coffetl_pg.{schema}.ctrl_{table} SET
                    id_gerado = $id_gerado
                WHERE 
                    hash= $hash
            """

            self.__engine.executemany(sql, data)

        except Exception as e:
            logger.error(f"Erro atualizar id's na tabela de controle: {e}")

    def update_batch_status(self, data: list[dict]) -> None:
        """Insere registros adicionados na fila de envio à tabela de controle."""
        try:
            sql = """
                UPDATE coffetl_pg.admin.registros_lotes SET
                    status = $status
                WHERE 
                    id_lote= $id_lote
            """

            self.__engine.executemany(sql, data)

        except Exception as e:
            logger.error(f'Erro atualizar status de lotes: {e}')

    def __enter__(self) -> 'DuckDB':
        self.get_engine()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()
