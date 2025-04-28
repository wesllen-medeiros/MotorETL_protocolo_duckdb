import sys
from pathlib import Path

# Adiciona o diretório raiz do projeto ao sys.path
pasta_raiz = Path(__file__).resolve().parent.parent
sys.path.append(str(pasta_raiz))

from src.database.load.builder import CoffetlDBBuilder
from src.log_config import get_logger

logger = get_logger()


class Initialization:
    """Cria estrutura de inicial."""

    def __new__(cls, *args, **kwargs):
        """Garante a criação do banco de dados ao instanciar a classe."""
        instance = super(Initialization, cls).__new__(cls)
        CoffetlDBBuilder().create_database()
        return instance

    def __init__(self) -> None:
        self.__builder = CoffetlDBBuilder()

    def admin(self) -> None:
        """Cria tabelas do schema admin."""
        self.__builder.build_struct('admin')

    def protocolo(self) -> None:
        """Cria tabelas do schema protocolo."""
        self.__builder.build_struct('protocolo')
