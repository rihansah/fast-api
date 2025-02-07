from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:rihan%40123@127.0.0.1:3306/TodoApplicationDatabase"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
sessionLocal = sessionmaker(autoflush=False, autocommit = False, bind= engine)
Base = declarative_base()