from sqlalchemy import (
    Column,
    String,
    Integer,
    DateTime,
    Enum,
    ForeignKey,
    func,
)
from sqlalchemy.dialects.postgresql import JSON
from src.controls.enums import (
    StatusLoteEnum,
    StatusOcorrenciaEnum,
)
from src.database.base import BASE_ADMIN


class RegistrosLotes(BASE_ADMIN):
    """Model tabela de controle de lotes."""

    __tablename__ = 'registros_lotes'
    __table_args__ = {'schema': 'admin'}

    id_lote = Column(String, primary_key=True, nullable=False)
    tipo_registro = Column(String, nullable=False)
    url_consulta = Column(String(), nullable=False)
    status = Column(
        Enum(StatusLoteEnum), default=StatusLoteEnum.AGUARDANDO_EXECUCAO
    )
    envio = Column(DateTime, default=func.now())


class RegistrosOcorrencias(BASE_ADMIN):
    """Model tabela de controle de ocorrências."""

    __tablename__ = 'registros_ocorrencias'
    __table_args__ = {'schema': 'admin'}

    sequencial = Column(Integer, primary_key=True, autoincrement=True)
    hash = Column(String, primary_key=True)
    sistema = Column(String, nullable=False)
    tipo_registro = Column(String, nullable=False)
    status = Column(
        Enum(StatusOcorrenciaEnum),
        default=StatusOcorrenciaEnum.AGUARDANDO_EXECUCAO,
    )
    id_lote = Column(
        String,
        ForeignKey(RegistrosLotes.id_lote),
        nullable=True,
    )
    mensagem_erro = Column(String, nullable=True)
    json_envio = Column(JSON, nullable=False)


class ParametrosEnvioFrotas(BASE_ADMIN):
    """Model tabela de controle de parâmetros de envio."""

    __tablename__ = 'parametros_envio_frotas'
    __table_args__ = {'schema': 'admin'}

    id_param = Column(Integer, primary_key=True, autoincrement=True)
    sistema = Column(String, primary_key=True)
    i_entidades = Column(Integer, primary_key=True)
    exercicio_inicial = Column(Integer, nullable=False)
    exercicio_final = Column(
        Integer,
        default=func.extract('year', func.current_date()),
    )
    token = Column(String, nullable=False)
    data_exec = Column(DateTime, default=func.now())
