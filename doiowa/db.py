from sqlalchemy import Column, create_engine, JSON, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from doiowa.config import DB_CONN

engine = create_engine(DB_CONN)
Session = sessionmaker(bind=engine)
Base = declarative_base()


class DoiJson(Base):
    __tablename__ = "doi_json"
    doi = Column(String(50), primary_key=True)
    json = Column(JSON)


def create_db(engine):
    Base.metadata.create_all(engine)
