from sqlalchemy import Column, Integer, String

from source.database import Base


class MetadataBase(Base):
    __tablename__ = 'cookies'

    id = Column(Integer, primary_key=True)
    cookie = Column(String)
    service = Column(String)
    parse_data = Column(String)
    path = Column(String)