import pytest
from src.database.connection import CoffetlDB

def test_engine_creation():
    db = CoffetlDB()
    engine = db.get_engine()
    assert engine is not None, "A engine não foi criada corretamente."