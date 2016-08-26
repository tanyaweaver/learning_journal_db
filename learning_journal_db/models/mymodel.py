from sqlalchemy import (
    Column,
    Index,
    Integer,
    UnicodeText,
)

from .meta import Base


class MyModel(Base):
    __tablename__ = 'models'
    id = Column(Integer, primary_key=True)
    name = Column(UnicodeText)
    value = Column(Integer)


Index('my_index', MyModel.name, unique=True, mysql_length=255)
