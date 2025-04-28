from sqlalchemy import MetaData
from sqlalchemy.orm import declarative_base

# Individualizar sistemas

BASE_ADMIN = declarative_base(metadata=MetaData(schema='admin'))
BASE_PROTOCOLO = declarative_base(metadata=MetaData(schema='protocolo'))