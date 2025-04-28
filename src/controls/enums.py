from enum import Enum


class StatusLoteEnum(Enum):
    AGUARDANDO_EXECUCAO = 1
    EXECUTANDO = 2
    EXECUTADO = 3
    EXECUTADO_PARCIALMENTE = 4
    ERRO = 5
    CANCELADO = 6
    AGUARDANDO_REEXECUCAO = 7


class StatusOcorrenciaEnum(Enum):
    AGUARDANDO_EXECUCAO = 1
    ERRO = 2
    SUCESSO = 3
