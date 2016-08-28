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
    title = Column(UnicodeText)
    date = Column(UnicodeText)
    body = Column(UnicodeText)


Index('my_index', MyModel.id, unique=True, mysql_length=255)
