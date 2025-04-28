import sys
from pathlib import Path

pasta_raiz = Path(__file__).resolve().parent.parent
sys.path.append(str(pasta_raiz))


from src.services.functions import CSVLoader

loader = CSVLoader()